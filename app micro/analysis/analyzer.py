"""
analysis/analyzer.py
WeatherAnalyzer class implementing meteorological statistical analysis.
Matches Figure 3 Class Diagram and satisfies Course Outcome (ii) & Page 9 requirements:
- map(), filter(), reduce(), lambda
- sorted(), zip(), enumerate(), list/dict comprehensions
"""

from functools import reduce
from typing import List, Tuple, Dict, Any, Optional
from models.weather_data import ForecastDay


class WeatherAnalyzer:
    """
    Meteorological analysis engine for 5-day weather forecasts.
    Analyzes temperature distributions, identifies trends, and filters conditions.
    Matches Figure 3 Class Diagram.
    """

    def __init__(self, forecasts: Optional[List[ForecastDay]] = None):
        # Attribute matching Figure 3: - forecasts: List
        self._forecasts: List[ForecastDay] = forecasts or []

    @property
    def forecasts(self) -> List[ForecastDay]:
        return self._forecasts

    @forecasts.setter
    def forecasts(self, value: List[ForecastDay]) -> None:
        self._forecasts = value or []

    def average_temp(self) -> float:
        """
        Calculates the mean temperature across the 5 forecast days.
        Matches Figure 3: + average_temp(): float
        Demonstrates: map(), reduce(), and lambda.
        """
        if not self._forecasts:
            return 0.0

        # Functional: extract mean daily temps using map and lambda
        daily_temps: List[float] = list(map(lambda f: (f.temp_min + f.temp_max) / 2.0, self._forecasts))

        # Functional: calculate total sum using reduce and lambda
        total_sum: float = reduce(lambda acc, t: acc + t, daily_temps, 0.0)

        return round(total_sum / len(daily_temps), 1)

    def max_min_temp(self) -> Tuple[float, float]:
        """
        Finds the highest maximum and lowest minimum temperatures in the forecast.
        Matches Figure 3: + max_min_temp(): tuple -> (highest_max, lowest_min)
        Demonstrates: map(), lambda, and sorted().
        """
        if not self._forecasts:
            return (0.0, 0.0)

        # Functional map to get all maximums and all minimums
        max_temps: List[float] = list(map(lambda f: f.temp_max, self._forecasts))
        min_temps: List[float] = list(map(lambda f: f.temp_min, self._forecasts))

        # Functional sorted() to retrieve extremes
        highest_max = sorted(max_temps, reverse=True)[0]
        lowest_min = sorted(min_temps)[0]

        return (round(highest_max, 1), round(lowest_min, 1))

    def trend(self) -> str:
        """
        Identifies whether the 5-day forecast exhibits a Warming, Cooling, or Stable trend.
        Matches Figure 3: + trend(): String
        Demonstrates: enumerate(), zip(), and functional comprehension.
        """
        if len(self._forecasts) < 2:
            return "Insufficient forecast data to determine trend."

        # Extract daily mid-temperatures
        temps = [(f.temp_min + f.temp_max) / 2.0 for f in self._forecasts]

        # Calculate daily day-over-day temperature differences using zip
        # zip() pairs consecutive days: (Day1, Day2), (Day2, Day3), ...
        consecutive_pairs = zip(temps[:-1], temps[1:])
        deltas = [day_next - day_curr for day_curr, day_next in consecutive_pairs]

        # Calculate net difference and average daily shift
        net_shift = temps[-1] - temps[0]

        # Use enumerate() to analyze consistency of directional steps
        positive_shifts = 0
        negative_shifts = 0
        for i, delta in enumerate(deltas):
            if delta > 0.4:
                positive_shifts += 1
            elif delta < -0.4:
                negative_shifts += 1

        if net_shift >= 1.5 and positive_shifts >= 2:
            return f"Warming Trend (Expected to rise by +{round(net_shift, 1)}°C)"
        elif net_shift <= -1.5 and negative_shifts >= 2:
            return f"Cooling Trend (Expected to drop by {round(net_shift, 1)}°C)"
        else:
            return "Stable Weather (Temperatures remain relatively steady)"

    def filter_rainy_days(self) -> List[ForecastDay]:
        """
        Filters forecast days with rain or precipitation.
        Demonstrates: filter() and lambda.
        """
        return list(
            filter(
                lambda f: "rain" in f.description.lower() or f.pop >= 30.0 or "drizzle" in f.description.lower(),
                self._forecasts,
            )
        )

    def filter_by_temperature_threshold(self, min_temp_threshold: float) -> List[ForecastDay]:
        """
        Filters forecast days whose maximum temperature meets or exceeds a threshold.
        Demonstrates: filter() with lambda.
        """
        return list(filter(lambda f: f.temp_max >= min_temp_threshold, self._forecasts))

    def get_comprehensive_summary(self, is_fahrenheit: bool = False) -> Dict[str, Any]:
        """
        Aggregates statistical analysis into a dictionary for UI presentation.
        Demonstrates list comprehensions and dictionary comprehensions.
        """
        avg_c = self.average_temp()
        highest_c, lowest_c = self.max_min_temp()
        weather_trend = self.trend()
        rainy_days = self.filter_rainy_days()

        def c_to_f(c_val: float) -> float:
            return round((c_val * 9 / 5) + 32, 1)

        # Dictionary comprehension of day summaries
        date_summary_map = {f.date: f.description for f in self._forecasts}

        return {
            "average_temp": c_to_f(avg_c) if is_fahrenheit else avg_c,
            "highest_temp": c_to_f(highest_c) if is_fahrenheit else highest_c,
            "lowest_temp": c_to_f(lowest_c) if is_fahrenheit else lowest_c,
            "trend": weather_trend,
            "rainy_day_count": len(rainy_days),
            "rainy_dates": [f.date for f in rainy_days],
            "dates": [f.date for f in self._forecasts],
            "day_summaries": date_summary_map,
            "unit": "°F" if is_fahrenheit else "°C",
        }
