"""
models/weather_data.py
OOP Data Models for the Weather Forecast Dashboard.
Demonstrates:
- Abstraction: BaseWeatherEntity (Abstract Base Class)
- Encapsulation: Private/protected attributes with getters, setters, and validation
- Inheritance: ForecastDay inherits from WeatherData
- Polymorphism: Overridden methods (get_summary, display_card)
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional


class BaseWeatherEntity(ABC):
    """
    Abstract Base Class representing any weather observation or forecast entity.
    Demonstrates Abstraction.
    """

    @abstractmethod
    def get_summary(self) -> str:
        """Polymorphic method to return a formatted summary of the weather entity."""
        pass

    @abstractmethod
    def to_fahrenheit(self) -> float:
        """Convert primary temperature to Fahrenheit."""
        pass


class WeatherData(BaseWeatherEntity):
    """
    Class representing Current Weather Information for a specific city.
    Demonstrates Encapsulation and Data Modeling.
    """

    def __init__(
        self,
        city: str,
        temperature: float,
        feels_like: float,
        humidity: int,
        pressure: int,
        wind_speed: float,
        description: str,
        icon: str = "01d",
        country: str = "",
        timestamp: Optional[datetime] = None,
        temp_min: Optional[float] = None,
        temp_max: Optional[float] = None,
    ):
        # Encapsulated private attributes
        self._city = city.strip().title()
        self._temperature = round(float(temperature), 1)
        self._feels_like = round(float(feels_like), 1)
        self._humidity = max(0, min(100, int(humidity)))
        self._pressure = int(pressure)
        self._wind_speed = round(float(wind_speed), 1)
        self._description = description.strip().capitalize()
        self._icon = icon
        self._country = country.upper()
        self._timestamp = timestamp or datetime.now()
        self._temp_min = round(float(temp_min), 1) if temp_min is not None else self._temperature
        self._temp_max = round(float(temp_max), 1) if temp_max is not None else self._temperature

    # Encapsulated Getters
    @property
    def city(self) -> str:
        return self._city

    @property
    def temperature(self) -> float:
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        self._temperature = round(float(value), 1)

    @property
    def feels_like(self) -> float:
        return self._feels_like

    @property
    def humidity(self) -> int:
        return self._humidity

    @property
    def pressure(self) -> int:
        return self._pressure

    @property
    def wind_speed(self) -> float:
        return self._wind_speed

    @property
    def description(self) -> str:
        return self._description

    @property
    def icon(self) -> str:
        return self._icon

    @property
    def country(self) -> str:
        return self._country

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def temp_min(self) -> float:
        return self._temp_min

    @property
    def temp_max(self) -> float:
        return self._temp_max

    def to_fahrenheit(self) -> float:
        """Convert Celsius temperature to Fahrenheit."""
        return round((self._temperature * 9 / 5) + 32, 1)

    def feels_like_fahrenheit(self) -> float:
        """Convert feels_like Celsius temperature to Fahrenheit."""
        return round((self._feels_like * 9 / 5) + 32, 1)

    def to_celsius(self) -> float:
        """Return Celsius temperature."""
        return self._temperature

    def get_summary(self) -> str:
        """
        Polymorphic method returning a concise summary of current conditions.
        """
        loc = f"{self._city}, {self._country}" if self._country else self._city
        return (
            f"Current Weather in {loc}: {self._temperature}°C ({self.to_fahrenheit()}°F), "
            f"{self._description}. Humidity: {self._humidity}%, Wind: {self._wind_speed} m/s."
        )

    def __repr__(self) -> str:
        return f"<WeatherData city='{self.city}' temp={self.temperature}°C desc='{self.description}'>"


class ForecastDay(WeatherData):
    """
    Class representing a single day in a 5-day Weather Forecast.
    Demonstrates Inheritance (extends WeatherData) and Polymorphism (overrides get_summary).
    """

    def __init__(
        self,
        city: str,
        date_str: str,
        temp_min: float,
        temp_max: float,
        condition: str,
        humidity: int = 50,
        pressure: int = 1013,
        wind_speed: float = 3.0,
        icon: str = "01d",
        country: str = "",
        pop: float = 0.0,
    ):
        # Calculate daily representative temperature as average of min and max
        avg_temp = round((temp_min + temp_max) / 2.0, 1)

        # Call parent constructor
        super().__init__(
            city=city,
            temperature=avg_temp,
            feels_like=avg_temp,
            humidity=humidity,
            pressure=pressure,
            wind_speed=wind_speed,
            description=condition,
            icon=icon,
            country=country,
            temp_min=temp_min,
            temp_max=temp_max,
        )

        self._date_str = date_str  # E.g. "Mon, Oct 19" or "2026-10-19"
        self._pop = round(float(pop) * 100, 1) if float(pop) <= 1.0 else round(float(pop), 1)

    @property
    def date(self) -> str:
        return self._date_str

    @property
    def pop(self) -> float:
        """Probability of Precipitation percentage (0 - 100%)."""
        return self._pop

    def temp_min_fahrenheit(self) -> float:
        return round((self._temp_min * 9 / 5) + 32, 1)

    def temp_max_fahrenheit(self) -> float:
        return round((self._temp_max * 9 / 5) + 32, 1)

    # Polymorphic Override
    def get_summary(self) -> str:
        """
        Polymorphic override of BaseWeatherEntity.get_summary() specifically for forecast days.
        """
        return (
            f"Forecast for {self._date_str}: {self._description}. "
            f"Min: {self._temp_min}°C ({self.temp_min_fahrenheit()}°F) / "
            f"Max: {self._temp_max}°C ({self.temp_max_fahrenheit()}°F), "
            f"Rain Chance: {self._pop}%."
        )

    def __repr__(self) -> str:
        return (
            f"<ForecastDay date='{self.date}' min={self.temp_min}°C "
            f"max={self.temp_max}°C cond='{self.description}'>"
        )
