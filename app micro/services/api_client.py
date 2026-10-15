"""
services/api_client.py
Service layer client communicating with OpenWeatherMap REST API.
Implements the exact interface from Figure 3 (Class Diagram) of the proposal.
Includes intelligent fallback / Demo mode for immediate testing without API key errors.
"""

import time
import math
import random
import requests
from typing import Dict, Any, Optional

from models.exceptions import (
    APIKeyError,
    CityNotFoundError,
    NetworkConnectionError,
    WeatherAppException,
)


class WeatherAPIClient:
    """
    REST API Client responsible for communicating with OpenWeatherMap.
    Matches Figure 3 Class Diagram specifications.
    """

    DEFAULT_BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: str = "", base_url: str = DEFAULT_BASE_URL):
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._session = requests.Session()
        self._timeout = 8.0  # seconds

    @property
    def api_key(self) -> str:
        return self._api_key

    @api_key.setter
    def api_key(self, value: str) -> None:
        self._api_key = value.strip()

    @property
    def base_url(self) -> str:
        return self._base_url

    def is_live_configured(self) -> bool:
        """Checks if a valid-looking live OpenWeatherMap API key is provided."""
        return bool(self._api_key and len(self._api_key) >= 24 and self._api_key.upper() != "DEMO")

    def check_response(self, response: requests.Response) -> bool:
        """
        Validates HTTP response status code and raises appropriate custom exceptions.
        Matches Figure 3: + check_response(): bool
        """
        if response.status_code == 200:
            return True

        if response.status_code == 401:
            raise APIKeyError(
                "Invalid or unauthorized OpenWeatherMap API key. "
                "Please configure a valid API key in Settings or switch to Demo Mode."
            )
        elif response.status_code == 404:
            raise CityNotFoundError(response.url)
        elif response.status_code == 429:
            raise WeatherAppException("OpenWeatherMap API rate limit exceeded. Please try again shortly.", 429)
        else:
            raise WeatherAppException(
                f"Weather API returned error HTTP {response.status_code}: {response.text}",
                status_code=response.status_code,
            )

    def fetch_current(self, city: str) -> Dict[str, Any]:
        """
        Fetches current weather for the specified city.
        Matches Figure 3: + fetch_current(city): dict
        """
        if not self.is_live_configured():
            # Run offline / demo simulator
            return self._generate_simulated_current(city)

        url = f"{self._base_url}/weather"
        params = {
            "q": city,
            "appid": self._api_key,
            "units": "metric",  # Fetch in Celsius by default
        }

        try:
            response = self._session.get(url, params=params, timeout=self._timeout)
            if self.check_response(response):
                return response.json()
        except requests.exceptions.Timeout:
            raise NetworkConnectionError("Connection timed out while contacting OpenWeatherMap servers.")
        except requests.exceptions.ConnectionError:
            raise NetworkConnectionError("Network unreachable. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            if not isinstance(e, WeatherAppException):
                raise NetworkConnectionError(f"Network error occurred: {str(e)}")
            raise

    def fetch_forecast(self, city: str) -> Dict[str, Any]:
        """
        Fetches 5-day / 3-hour forecast for the specified city.
        Matches Figure 3: + fetch_forecast(city): dict
        """
        if not self.is_live_configured():
            # Run offline / demo simulator
            return self._generate_simulated_forecast(city)

        url = f"{self._base_url}/forecast"
        params = {
            "q": city,
            "appid": self._api_key,
            "units": "metric",
        }

        try:
            response = self._session.get(url, params=params, timeout=self._timeout)
            if self.check_response(response):
                return response.json()
        except requests.exceptions.Timeout:
            raise NetworkConnectionError("Connection timed out while contacting forecast service.")
        except requests.exceptions.ConnectionError:
            raise NetworkConnectionError("Network unreachable. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            if not isinstance(e, WeatherAppException):
                raise NetworkConnectionError(f"Network error occurred: {str(e)}")
            raise

    # -------------------------------------------------------------------------
    # Intelligent Demo / Offline Simulation Engine
    # Generates deterministic, realistic OpenWeatherMap-format JSON responses
    # -------------------------------------------------------------------------
    def _generate_simulated_current(self, city: str) -> Dict[str, Any]:
        """Generates realistic current weather JSON response matching OpenWeatherMap schema."""
        city_seed = sum(ord(c) for c in city.lower())
        rng = random.Random(city_seed)

        # Baseline temps based on city name hashing
        base_temp = 12.0 + (city_seed % 22) + rng.uniform(-2.0, 2.0)
        feels_like = base_temp + rng.uniform(-2.5, 2.5)
        humidity = 40 + (city_seed % 50)
        pressure = 1008 + (city_seed % 18)
        wind_speed = round(rng.uniform(1.8, 8.5), 1)

        weather_types = [
            {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"},
            {"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"},
            {"id": 803, "main": "Clouds", "description": "scattered clouds", "icon": "03d"},
            {"id": 804, "main": "Clouds", "description": "overcast clouds", "icon": "04d"},
            {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"},
            {"id": 502, "main": "Rain", "description": "moderate rain", "icon": "10d"},
            {"id": 211, "main": "Thunderstorm", "description": "thunderstorm with rain", "icon": "11d"},
        ]
        condition = weather_types[city_seed % len(weather_types)]

        clean_city = city.split(",")[0].strip().title()
        country_code = city.split(",")[1].strip().upper() if "," in city else "IN"

        return {
            "coord": {"lon": 77.5946, "lat": 12.9716},
            "weather": [condition],
            "base": "stations",
            "main": {
                "temp": round(base_temp, 1),
                "feels_like": round(feels_like, 1),
                "temp_min": round(base_temp - rng.uniform(1.0, 3.5), 1),
                "temp_max": round(base_temp + rng.uniform(1.0, 3.5), 1),
                "pressure": pressure,
                "humidity": humidity,
            },
            "visibility": 10000,
            "wind": {"speed": wind_speed, "deg": (city_seed * 37) % 360},
            "clouds": {"all": (city_seed * 17) % 100},
            "dt": int(time.time()),
            "sys": {
                "country": country_code,
                "sunrise": int(time.time()) - 21600,
                "sunset": int(time.time()) + 21600,
            },
            "name": clean_city,
            "cod": 200,
            "_simulated": True,
        }

    def _generate_simulated_forecast(self, city: str) -> Dict[str, Any]:
        """Generates realistic 5-day / 3-hour forecast JSON matching OpenWeatherMap schema."""
        city_seed = sum(ord(c) for c in city.lower())
        rng = random.Random(city_seed + 101)

        base_temp = 12.0 + (city_seed % 22)
        weather_pool = [
            {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"},
            {"id": 801, "main": "Clouds", "description": "partly cloudy", "icon": "02d"},
            {"id": 804, "main": "Clouds", "description": "overcast clouds", "icon": "04d"},
            {"id": 500, "main": "Rain", "description": "light showers", "icon": "10d"},
            {"id": 800, "main": "Clear", "description": "sunny", "icon": "01d"},
        ]

        forecast_list = []
        now_ts = int(time.time())
        day_seconds = 86400

        # Generate entries for 5 upcoming days (8 periods per day = 40 periods)
        for day_idx in range(5):
            day_variation = math.sin((day_idx / 5.0) * math.pi) * 4.0 + rng.uniform(-1.5, 1.5)
            cond = weather_pool[(city_seed + day_idx) % len(weather_pool)]

            for hour_step in range(8):
                hour_offset = hour_step * 3 * 3600
                entry_ts = now_ts + (day_idx * day_seconds) + hour_offset

                # Diurnal temperature cycle (peaks around early afternoon)
                diurnal = math.sin((hour_step / 8.0) * 2 * math.pi - math.pi / 2) * 3.5
                temp = base_temp + day_variation + diurnal + rng.uniform(-0.5, 0.5)

                entry = {
                    "dt": entry_ts,
                    "main": {
                        "temp": round(temp, 1),
                        "feels_like": round(temp + rng.uniform(-1.0, 1.0), 1),
                        "temp_min": round(temp - 1.5, 1),
                        "temp_max": round(temp + 1.5, 1),
                        "pressure": 1012 + int(rng.uniform(-4, 4)),
                        "humidity": int(min(95, max(30, 60 + diurnal * -5))),
                    },
                    "weather": [cond],
                    "wind": {"speed": round(rng.uniform(2.0, 6.5), 1)},
                    "pop": round(rng.uniform(0.0, 0.6) if "Rain" in cond["main"] else rng.uniform(0.0, 0.15), 2),
                    "dt_txt": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(entry_ts)),
                }
                forecast_list.append(entry)

        clean_city = city.split(",")[0].strip().title()
        country_code = city.split(",")[1].strip().upper() if "," in city else "IN"

        return {
            "cod": "200",
            "message": 0,
            "cnt": len(forecast_list),
            "list": forecast_list,
            "city": {
                "id": 1277333,
                "name": clean_city,
                "country": country_code,
                "coord": {"lat": 12.9716, "lon": 77.5946},
            },
            "_simulated": True,
        }
