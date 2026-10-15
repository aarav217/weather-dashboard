"""
storage/storage_manager.py
StorageManager class implementing SQLite database persistence and JSON file sync.
Accurately implements Figure 3 (Class Diagram) and Figure 4 (Database Design).
"""

import os
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import List, Dict, Any, Optional, Generator

from models.weather_data import WeatherData, ForecastDay
from models.exceptions import StorageError


class StorageManager:
    """
    Manages data persistence via SQLite relational database and JSON files.
    Matches Figure 3 and Figure 4 specifications.
    """

    def __init__(
        self,
        base_dir: Optional[str] = None,
        db_name: str = "weather_dashboard.db",
        history_file: str = "history.json",
        favourites_file: str = "favourites.json",
        config_file: str = "config.json",
    ):
        self._base_dir = base_dir or os.getcwd()
        self._db_path = os.path.join(self._base_dir, db_name)
        self._history_path = os.path.join(self._base_dir, history_file)
        self._favourites_path = os.path.join(self._base_dir, favourites_file)
        self._config_path = os.path.join(self._base_dir, config_file)

        # In-memory caches matching Figure 3 attributes
        self._history: List[str] = []
        self._favourites: List[str] = []

        # Initialize schema and load persisted caches
        self._init_sqlite_db()
        self.load_history()
        self.load_favourites()

    @property
    def file_path(self) -> str:
        """Matches Figure 3 attribute: - file_path: String"""
        return self._history_path

    @property
    def history(self) -> List[str]:
        """Matches Figure 3 attribute: - history: List"""
        return self._history

    @property
    def favourites(self) -> List[str]:
        """Matches Figure 3 attribute: - favourites: List"""
        return self._favourites

    def _get_connection(self) -> sqlite3.Connection:
        """Creates a connection to SQLite with foreign keys enabled."""
        conn = sqlite3.connect(self._db_path, timeout=5.0)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Thread-safe context manager guaranteeing proper commit, rollback, and connection closure."""
        conn = self._get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_sqlite_db(self) -> None:
        """
        Initializes SQLite database tables strictly according to Figure 4 Database Design:
        - CITY
        - SEARCH_HISTORY
        - FAVOURITE_CITY
        - WEATHER_RECORD
        - USER_SETTINGS
        - FORECAST_DAY
        """
        try:
            with self._connection() as conn:
                cursor = conn.cursor()

                # 1. CITY Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS CITY (
                    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT UNIQUE NOT NULL,
                    country_code TEXT,
                    latitude REAL,
                    longitude REAL
                );
                """)

                # 2. SEARCH_HISTORY Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS SEARCH_HISTORY (
                    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_id INTEGER NOT NULL,
                    searched_at DATETIME NOT NULL,
                    FOREIGN KEY (city_id) REFERENCES CITY (city_id) ON DELETE CASCADE
                );
                """)

                # 3. FAVOURITE_CITY Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS FAVOURITE_CITY (
                    fav_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_id INTEGER UNIQUE NOT NULL,
                    added_at DATETIME NOT NULL,
                    FOREIGN KEY (city_id) REFERENCES CITY (city_id) ON DELETE CASCADE
                );
                """)

                # 4. WEATHER_RECORD Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS WEATHER_RECORD (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_id INTEGER NOT NULL,
                    temperature REAL NOT NULL,
                    feels_like REAL,
                    humidity INTEGER,
                    pressure INTEGER,
                    wind_speed REAL,
                    condition TEXT,
                    fetched_at DATETIME NOT NULL,
                    FOREIGN KEY (city_id) REFERENCES CITY (city_id) ON DELETE CASCADE
                );
                """)

                # 5. USER_SETTINGS Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS USER_SETTINGS (
                    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    temp_unit TEXT DEFAULT 'C',
                    refresh_minutes INTEGER DEFAULT 30
                );
                """)

                # 6. FORECAST_DAY Table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS FORECAST_DAY (
                    forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_id INTEGER NOT NULL,
                    forecast_date DATE NOT NULL,
                    temp_min REAL NOT NULL,
                    temp_max REAL NOT NULL,
                    condition TEXT,
                    FOREIGN KEY (city_id) REFERENCES CITY (city_id) ON DELETE CASCADE
                );
                """)

                # Seed default user settings if absent
                cursor.execute("SELECT COUNT(*) FROM USER_SETTINGS")
                if cursor.fetchone()[0] == 0:
                    cursor.execute(
                        "INSERT INTO USER_SETTINGS (temp_unit, refresh_minutes) VALUES (?, ?)",
                        ("C", 30),
                    )
        except sqlite3.Error as e:
            raise StorageError(f"Database initialization failed: {str(e)}")

    def _get_or_create_city(self, city_name: str, country_code: str = "") -> int:
        """Helper to get city_id or insert if new."""
        clean_name = city_name.strip().title()
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city_id FROM CITY WHERE LOWER(city_name) = LOWER(?)", (clean_name,))
            row = cursor.fetchone()
            if row:
                return row["city_id"]

            cursor.execute(
                "INSERT INTO CITY (city_name, country_code, latitude, longitude) VALUES (?, ?, ?, ?)",
                (clean_name, country_code.upper(), 0.0, 0.0),
            )
            return cursor.lastrowid

    # -------------------------------------------------------------------------
    # History Operations (Figure 3: + save_history(city), + load_history())
    # -------------------------------------------------------------------------
    def save_history(self, city: str) -> None:
        """
        Saves searched city into SQLite SEARCH_HISTORY and history.json.
        Matches Figure 3: + save_history(city): void
        """
        clean_city = city.strip().title()
        if not clean_city:
            return

        try:
            city_id = self._get_or_create_city(clean_city)
            now_iso = datetime.now().isoformat()

            with self._connection() as conn:
                conn.execute(
                    "INSERT INTO SEARCH_HISTORY (city_id, searched_at) VALUES (?, ?)",
                    (city_id, now_iso),
                )

            # Update memory cache (most recent first, unique)
            if clean_city in self._history:
                self._history.remove(clean_city)
            self._history.insert(0, clean_city)
            self._history = self._history[:20]  # retain last 20

            # Sync to JSON file
            self._sync_history_json()
        except Exception:
            # Fallback to JSON-only persistence
            if clean_city not in self._history:
                self._history.insert(0, clean_city)
            self._sync_history_json()

    def load_history(self) -> List[str]:
        """
        Loads search history from SQLite or JSON file.
        Matches Figure 3: + load_history(): List
        """
        results: List[str] = []
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT c.city_name, MAX(sh.searched_at) as last_seen
                FROM SEARCH_HISTORY sh
                JOIN CITY c ON sh.city_id = c.city_id
                GROUP BY c.city_name
                ORDER BY last_seen DESC
                LIMIT 20;
                """)
                rows = cursor.fetchall()
                results = [r["city_name"] for r in rows]
        except Exception:
            pass

        # If SQLite had no rows or failed, read from JSON file
        if not results and os.path.exists(self._history_path):
            try:
                with open(self._history_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        results = [c.title() for c in data if isinstance(c, str)]
            except Exception:
                pass

        # Defaults if completely fresh
        if not results:
            results = ["Bengaluru", "Mumbai", "Delhi", "London", "New York"]

        self._history = results
        return self._history

    def _sync_history_json(self) -> None:
        """Writes current history list to history.json."""
        try:
            with open(self._history_path, "w", encoding="utf-8") as f:
                json.dump(self._history, f, indent=2)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Favourite Operations (Figure 3: + add_favourite(city), load_favourites)
    # -------------------------------------------------------------------------
    def add_favourite(self, city: str) -> None:
        """
        Adds city to favourites in SQLite and favourites.json.
        Matches Figure 3: + add_favourite(city): void
        """
        clean_city = city.strip().title()
        if not clean_city or clean_city in self._favourites:
            return

        try:
            city_id = self._get_or_create_city(clean_city)
            now_iso = datetime.now().isoformat()
            with self._connection() as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO FAVOURITE_CITY (city_id, added_at) VALUES (?, ?)",
                    (city_id, now_iso),
                )

            self._favourites.append(clean_city)
            self._sync_favourites_json()
        except Exception:
            if clean_city not in self._favourites:
                self._favourites.append(clean_city)
            self._sync_favourites_json()

    def remove_favourite(self, city: str) -> None:
        """
        Removes city from favourites in SQLite and favourites.json.
        Matches Figure 3: + remove_favourite(city): void
        """
        clean_city = city.strip().title()
        if clean_city in self._favourites:
            self._favourites.remove(clean_city)

        try:
            city_id = self._get_or_create_city(clean_city)
            with self._connection() as conn:
                conn.execute("DELETE FROM FAVOURITE_CITY WHERE city_id = ?", (city_id,))
            self._sync_favourites_json()
        except Exception:
            self._sync_favourites_json()

    def load_favourites(self) -> List[str]:
        """
        Loads favourites list from SQLite or JSON file.
        Matches Figure 3: + load_favourites(): List
        """
        results: List[str] = []
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                SELECT c.city_name
                FROM FAVOURITE_CITY fc
                JOIN CITY c ON fc.city_id = c.city_id
                ORDER BY fc.added_at DESC;
                """)
                rows = cursor.fetchall()
                results = [r["city_name"] for r in rows]
        except Exception:
            pass

        if not results and os.path.exists(self._favourites_path):
            try:
                with open(self._favourites_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        results = [c.title() for c in data if isinstance(c, str)]
            except Exception:
                pass

        if not results:
            results = ["Bengaluru", "London", "Tokyo"]

        self._favourites = results
        return self._favourites

    def _sync_favourites_json(self) -> None:
        """Writes favourites to favourites.json."""
        try:
            with open(self._favourites_path, "w", encoding="utf-8") as f:
                json.dump(self._favourites, f, indent=2)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Weather Record & Forecast Persistence (Figure 4 Schema)
    # -------------------------------------------------------------------------
    def record_weather_observation(self, weather: WeatherData, forecasts: Optional[List[ForecastDay]] = None) -> None:
        """Stores a snapshot in WEATHER_RECORD and FORECAST_DAY."""
        try:
            city_id = self._get_or_create_city(weather.city, weather.country)
            now_iso = datetime.now().isoformat()

            with self._connection() as conn:
                conn.execute(
                    """
                    INSERT INTO WEATHER_RECORD (
                        city_id, temperature, feels_like, humidity, pressure, wind_speed, condition, fetched_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        city_id,
                        weather.temperature,
                        weather.feels_like,
                        weather.humidity,
                        weather.pressure,
                        weather.wind_speed,
                        weather.description,
                        now_iso,
                    ),
                )

                if forecasts:
                    for f in forecasts:
                        conn.execute(
                            """
                            INSERT INTO FORECAST_DAY (
                                city_id, forecast_date, temp_min, temp_max, condition
                            ) VALUES (?, ?, ?, ?, ?)
                            """,
                            (city_id, f.date, f.temp_min, f.temp_max, f.description),
                        )
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # User Settings & Config (config.json + USER_SETTINGS table)
    # -------------------------------------------------------------------------
    def load_settings(self) -> Dict[str, Any]:
        """Loads user settings (unit, theme, refresh interval, api_key)."""
        defaults = {
            "api_key": "",
            "temp_unit": "C",
            "refresh_minutes": 30,
            "theme": "dark",
            "auto_refresh_enabled": False,
            "last_city": "Bengaluru",
        }

        # Check config.json
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    defaults.update(saved)
            except Exception:
                pass

        # Check SQLite USER_SETTINGS
        try:
            with self._connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT temp_unit, refresh_minutes FROM USER_SETTINGS ORDER BY setting_id DESC LIMIT 1")
                row = cursor.fetchone()
                if row:
                    defaults["temp_unit"] = row["temp_unit"]
                    defaults["refresh_minutes"] = row["refresh_minutes"]
        except Exception:
            pass

        return defaults

    def save_settings(self, settings: Dict[str, Any]) -> None:
        """Saves user settings to config.json and SQLite USER_SETTINGS."""
        try:
            with open(self._config_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)

            with self._connection() as conn:
                conn.execute(
                    "UPDATE USER_SETTINGS SET temp_unit = ?, refresh_minutes = ? WHERE setting_id = (SELECT MAX(setting_id) FROM USER_SETTINGS)",
                    (settings.get("temp_unit", "C"), settings.get("refresh_minutes", 30)),
                )
        except Exception:
            pass
