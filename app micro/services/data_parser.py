"""
services/data_parser.py
Data Parser module: parses OpenWeatherMap JSON responses into WeatherData and ForecastDay OOP objects.
Corresponds to 'Data Parser (JSON to objects)' in Figure 1 & Step 6 of Proposal Workflow.
"""

from datetime import datetime
from typing import Dict, Any, List, Tuple
from collections import defaultdict

from models.weather_data import WeatherData, ForecastDay
from models.exceptions import WeatherAppException


class DataParser:
    """
    Parses raw REST JSON payloads into strongly-typed OOP domain models.
    """

    @classmethod
    def parse_current_weather(cls, data: Dict[str, Any]) -> WeatherData:
        """
        Parses current weather JSON into a WeatherData object.
        """
        try:
            city_name = data.get("name", "Unknown City")
            country = data.get("sys", {}).get("country", "")
            main = data.get("main", {})
            wind = data.get("wind", {})
            weather_list = data.get("weather", [])
            primary_weather = weather_list[0] if weather_list else {}

            temp = main.get("temp", 0.0)
            feels_like = main.get("feels_like", temp)
            temp_min = main.get("temp_min", temp)
            temp_max = main.get("temp_max", temp)
            humidity = main.get("humidity", 0)
            pressure = main.get("pressure", 1013)
            wind_speed = wind.get("speed", 0.0)
            description = primary_weather.get("description", "Clear")
            icon = primary_weather.get("icon", "01d")

            dt_timestamp = data.get("dt")
            dt_obj = datetime.fromtimestamp(dt_timestamp) if dt_timestamp else datetime.now()

            return WeatherData(
                city=city_name,
                temperature=float(temp),
                feels_like=float(feels_like),
                humidity=int(humidity),
                pressure=int(pressure),
                wind_speed=float(wind_speed),
                description=str(description),
                icon=str(icon),
                country=country,
                timestamp=dt_obj,
                temp_min=float(temp_min),
                temp_max=float(temp_max),
            )
        except Exception as e:
            raise WeatherAppException(f"Failed to parse current weather data: {str(e)}")

    @classmethod
    def parse_forecast(cls, data: Dict[str, Any]) -> List[ForecastDay]:
        """
        Parses 5-day / 3-hour forecast JSON into a list of 5 distinct ForecastDay objects.
        Groups 3-hour periods by calendar date, computes true daily min/max,
        and determines the most prevalent weather condition and rain probability.
        """
        try:
            city_info = data.get("city", {})
            city_name = city_info.get("name", "Unknown City")
            country = city_info.get("country", "")
            forecast_list = data.get("list", [])

            # Group entries by day date string (YYYY-MM-DD)
            grouped_by_day = defaultdict(list)
            for item in forecast_list:
                dt_txt = item.get("dt_txt")  # e.g. "2026-10-15 12:00:00"
                if dt_txt:
                    day_key = dt_txt.split(" ")[0]
                else:
                    ts = item.get("dt", 0)
                    day_key = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
                grouped_by_day[day_key].append(item)

            forecast_days: List[ForecastDay] = []

            # We process up to 5 consecutive forecast days
            for day_key, items in sorted(grouped_by_day.items())[:5]:
                # Extract all temperatures for the day
                temps = [entry["main"]["temp"] for entry in items if "main" in entry]
                temp_min = min(temps) if temps else 20.0
                temp_max = max(temps) if temps else 25.0

                # Calculate average humidity and wind
                humidities = [entry["main"].get("humidity", 50) for entry in items if "main" in entry]
                avg_humidity = sum(humidities) // len(humidities) if humidities else 50

                winds = [entry["wind"].get("speed", 2.0) for entry in items if "wind" in entry]
                avg_wind = round(sum(winds) / len(winds), 1) if winds else 2.5

                # Max probability of precipitation
                pops = [entry.get("pop", 0.0) for entry in items]
                max_pop = max(pops) if pops else 0.0

                # Representative condition (pick midday ~12:00 or majority condition)
                midday_entry = None
                for entry in items:
                    if "12:00:00" in entry.get("dt_txt", ""):
                        midday_entry = entry
                        break
                if not midday_entry:
                    midday_entry = items[len(items) // 2]

                weather_entry = midday_entry.get("weather", [{}])[0]
                condition = weather_entry.get("description", "Clear")
                icon = weather_entry.get("icon", "01d")

                # Format user-friendly date: e.g. "Thu, Oct 15"
                date_dt = datetime.strptime(day_key, "%Y-%m-%d")
                friendly_date = date_dt.strftime("%a, %b %d")

                day_obj = ForecastDay(
                    city=city_name,
                    date_str=friendly_date,
                    temp_min=float(temp_min),
                    temp_max=float(temp_max),
                    condition=str(condition),
                    humidity=int(avg_humidity),
                    pressure=1013,
                    wind_speed=float(avg_wind),
                    icon=str(icon),
                    country=country,
                    pop=float(max_pop),
                )
                forecast_days.append(day_obj)

            return forecast_days
        except Exception as e:
            raise WeatherAppException(f"Failed to parse forecast data: {str(e)}")
