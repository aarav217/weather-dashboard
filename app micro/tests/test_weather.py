"""
tests/test_weather.py
Comprehensive automated test suite verifying all Course Outcomes and OOP rubric criteria:
- Object-Oriented Design (Classes, Encapsulation, Inheritance, Polymorphism, Abstraction)
- Functional Programming (map, filter, reduce, lambda, sorted, zip, enumerate)
- Service Layer & Validation (InputValidator, DataParser, WeatherAPIClient)
- Storage Layer & SQLite Database Schema (Figure 4)
"""

import os
import unittest
import tempfile
from datetime import datetime

from models.exceptions import (
    WeatherAppException,
    InvalidInputError,
    CityNotFoundError,
    APIKeyError,
    NetworkConnectionError,
)
from models.weather_data import BaseWeatherEntity, WeatherData, ForecastDay
from services.validator import InputValidator
from services.api_client import WeatherAPIClient
from services.data_parser import DataParser
from analysis.analyzer import WeatherAnalyzer
from storage.storage_manager import StorageManager


class TestWeatherAppOOP(unittest.TestCase):
    """Verifies OOP Principles and design constructs."""

    def test_abstraction(self):
        """Verify that BaseWeatherEntity is abstract and enforces method implementation."""
        # Verify that BaseWeatherEntity explicitly registers abstract methods
        self.assertEqual(
            BaseWeatherEntity.__abstractmethods__,
            frozenset({"get_summary", "to_fahrenheit"}),
        )
        # Verify that attempting to instantiate the abstract class directly raises TypeError
        with self.assertRaises(TypeError):
            BaseWeatherEntity()  # pyright: ignore[reportAbstractUsage]

    def test_encapsulation(self):
        """Verify encapsulated properties and unit conversion methods."""
        w = WeatherData(
            city="Bengaluru",
            temperature=25.0,
            feels_like=26.0,
            humidity=65,
            pressure=1013,
            wind_speed=3.5,
            description="Clear sky",
            country="IN",
        )
        self.assertEqual(w.city, "Bengaluru")
        self.assertEqual(w.temperature, 25.0)
        self.assertEqual(w.to_fahrenheit(), 77.0)
        self.assertEqual(w.humidity, 65)

    def test_inheritance(self):
        """Verify that ForecastDay inherits from WeatherData."""
        self.assertTrue(issubclass(ForecastDay, WeatherData))
        self.assertTrue(issubclass(ForecastDay, BaseWeatherEntity))

        f = ForecastDay(
            city="Bengaluru",
            date_str="Wed, Oct 14",
            temp_min=20.0,
            temp_max=30.0,
            condition="Scattered clouds",
            pop=0.25,
        )
        self.assertEqual(f.city, "Bengaluru")
        self.assertEqual(f.date, "Wed, Oct 14")
        self.assertEqual(f.temp_min, 20.0)
        self.assertEqual(f.temp_max, 30.0)
        self.assertEqual(f.temperature, 25.0)  # average of min/max
        self.assertEqual(f.pop, 25.0)

    def test_polymorphism(self):
        """Verify polymorphic behavior of get_summary()."""
        w = WeatherData(
            city="Delhi",
            temperature=30.0,
            feels_like=32.0,
            humidity=40,
            pressure=1010,
            wind_speed=4.0,
            description="Sunny",
        )
        f = ForecastDay(
            city="Delhi",
            date_str="Thu, Oct 15",
            temp_min=22.0,
            temp_max=34.0,
            condition="Sunny",
        )

        entities: list[BaseWeatherEntity] = [w, f]
        summaries = [e.get_summary() for e in entities]

        self.assertIn("Current Weather in Delhi", summaries[0])
        self.assertIn("Forecast for Thu, Oct 15", summaries[1])

    def test_exception_handling(self):
        """Verify custom exception hierarchy."""
        self.assertTrue(issubclass(InvalidInputError, WeatherAppException))
        self.assertTrue(issubclass(CityNotFoundError, WeatherAppException))
        self.assertTrue(issubclass(APIKeyError, WeatherAppException))
        self.assertTrue(issubclass(NetworkConnectionError, WeatherAppException))

        err = CityNotFoundError("Atlantis")
        self.assertEqual(err.status_code, 404)
        self.assertIn("Atlantis", str(err))


class TestFunctionalProgramming(unittest.TestCase):
    """Verifies functional programming constructs in WeatherAnalyzer."""

    def setUp(self):
        self.forecasts = [
            ForecastDay("Paris", "Day 1", temp_min=10.0, temp_max=20.0, condition="Clear sky", pop=0.0),
            ForecastDay("Paris", "Day 2", temp_min=12.0, temp_max=22.0, condition="Light rain", pop=0.6),
            ForecastDay("Paris", "Day 3", temp_min=14.0, temp_max=24.0, condition="Heavy rain", pop=0.8),
            ForecastDay("Paris", "Day 4", temp_min=15.0, temp_max=26.0, condition="Cloudy", pop=0.1),
            ForecastDay("Paris", "Day 5", temp_min=16.0, temp_max=28.0, condition="Sunny", pop=0.0),
        ]
        self.analyzer = WeatherAnalyzer(self.forecasts)

    def test_average_temp_reduce_map_lambda(self):
        """Test average_temp() which utilizes map(), reduce(), and lambda."""
        # Day avgs: 15.0, 17.0, 19.0, 20.5, 22.0 -> Mean = 93.5 / 5 = 18.7
        avg = self.analyzer.average_temp()
        self.assertAlmostEqual(avg, 18.7, places=1)

    def test_max_min_temp_sorted_map(self):
        """Test max_min_temp() which uses map() and sorted()."""
        high, low = self.analyzer.max_min_temp()
        self.assertEqual(high, 28.0)
        self.assertEqual(low, 10.0)

    def test_trend_zip_enumerate(self):
        """Test trend() which uses zip() and enumerate()."""
        trend_res = self.analyzer.trend()
        self.assertIn("Warming Trend", trend_res)

    def test_filter_rainy_days(self):
        """Test filter_rainy_days() using filter() and lambda."""
        rainy = self.analyzer.filter_rainy_days()
        self.assertEqual(len(rainy), 2)
        dates = [r.date for r in rainy]
        self.assertIn("Day 2", dates)
        self.assertIn("Day 3", dates)


class TestServicesAndParser(unittest.TestCase):
    """Verifies InputValidator, DataParser, and WeatherAPIClient."""

    def test_input_validator(self):
        self.assertEqual(InputValidator.validate_city("  bengaluru  "), "Bengaluru")
        self.assertEqual(InputValidator.validate_city("new york, us"), "New York, US")

        with self.assertRaises(InvalidInputError):
            InputValidator.validate_city("")

        with self.assertRaises(InvalidInputError):
            InputValidator.validate_city("City123$$$")

    def test_api_client_simulation(self):
        client = WeatherAPIClient(api_key="DEMO")
        self.assertFalse(client.is_live_configured())

        curr = client.fetch_current("Tokyo")
        self.assertEqual(curr["cod"], 200)
        self.assertEqual(curr["name"], "Tokyo")

        fore = client.fetch_forecast("Tokyo")
        self.assertEqual(fore["cod"], "200")
        self.assertTrue(len(fore["list"]) > 0)

    def test_data_parser(self):
        client = WeatherAPIClient(api_key="DEMO")
        raw_curr = client.fetch_current("London")
        weather = DataParser.parse_current_weather(raw_curr)
        self.assertEqual(weather.city, "London")
        self.assertIsInstance(weather.temperature, float)

        raw_fore = client.fetch_forecast("London")
        forecasts = DataParser.parse_forecast(raw_fore)
        self.assertEqual(len(forecasts), 5)
        self.assertEqual(forecasts[0].city, "London")


class TestStorageManager(unittest.TestCase):
    """Verifies SQLite database operations and JSON file synchronization."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = StorageManager(base_dir=self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_history_persistence(self):
        self.storage.save_history("Mumbai")
        self.storage.save_history("Bengaluru")
        hist = self.storage.load_history()
        self.assertIn("Mumbai", hist)
        self.assertIn("Bengaluru", hist)
        self.assertEqual(hist[0], "Bengaluru")

    def test_favourites_persistence(self):
        self.storage.add_favourite("San Francisco")
        favs = self.storage.load_favourites()
        self.assertIn("San Francisco", favs)

        self.storage.remove_favourite("San Francisco")
        favs_after = self.storage.load_favourites()
        self.assertNotIn("San Francisco", favs_after)

    def test_sqlite_tables_created(self):
        with self.storage._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            for expected in ["CITY", "SEARCH_HISTORY", "FAVOURITE_CITY", "WEATHER_RECORD", "USER_SETTINGS", "FORECAST_DAY"]:
                self.assertIn(expected, tables)


if __name__ == "__main__":
    unittest.main()
