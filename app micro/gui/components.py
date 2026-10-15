"""
gui/components.py
Reusable GUI widgets and composite panels for the Weather Forecast Dashboard.
Implements the Presentation Layer panels defined in Figure 1 of the Proposal:
- City Search & Action Toolbar
- Current Weather Panel
- Weather Analytics Banner (from WeatherAnalyzer)
- 5-Day Forecast Panel (using ForecastDay objects)
- Temperature Chart Frame (integrated with ChartPlotter)
- Status Bar
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List, Optional, Dict, Any

from gui.theme import Theme
from gui.icon_generator import WeatherIconGenerator
from models.weather_data import WeatherData, ForecastDay


class SearchToolbar(tk.Frame):
    """
    Search toolbar with input entry, search button, favourites list,
    unit toggle (°C/°F), theme toggle, and settings button.
    """

    def __init__(
        self,
        parent,
        on_search: Callable[[str], None],
        on_unit_toggle: Callable[[], None],
        on_theme_toggle: Callable[[], None],
        on_toggle_favourite: Callable[[], None],
        on_open_settings: Callable[[], None],
        theme: Dict[str, Any],
        **kwargs,
    ):
        super().__init__(parent, bg=theme["bg_card"], bd=0, highlightthickness=1, **kwargs)
        self.config(highlightbackground=theme["border_color"])

        self._on_search = on_search
        self._on_unit_toggle = on_unit_toggle
        self._on_theme_toggle = on_theme_toggle
        self._on_toggle_favourite = on_toggle_favourite
        self._on_open_settings = on_open_settings
        self._theme = theme

        self._build_widgets()

    def _build_widgets(self):
        t = self._theme

        # Brand / Logo icon label
        brand_frame = tk.Frame(self, bg=t["bg_card"])
        brand_frame.pack(side=tk.LEFT, padx=(14, 10), pady=8)

        brand_lbl = tk.Label(
            brand_frame,
            text="🌦 SkyCast",
            font=("Segoe UI", 13, "bold"),
            fg=t["accent_light"],
            bg=t["bg_card"],
        )
        brand_lbl.pack(side=tk.LEFT)

        # Search Entry Container
        search_container = tk.Frame(self, bg=t["bg_main"], bd=0, highlightthickness=1)
        search_container.config(highlightbackground=t["border_color"])
        search_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=8)

        search_icon = tk.Label(
            search_container,
            text="🔍",
            font=("Segoe UI", 10),
            fg=t["text_muted"],
            bg=t["bg_main"],
        )
        search_icon.pack(side=tk.LEFT, padx=(8, 4))

        POPULAR_CITIES = [
            "Bengaluru",
            "Mumbai",
            "Delhi",
            "Hyderabad",
            "Chennai",
            "Kolkata",
            "London",
            "New York",
            "Tokyo",
            "Paris",
            "Dubai",
            "Singapore",
            "Sydney",
            "Toronto",
            "Berlin",
            "San Francisco",
        ]
        self.city_entry = ttk.Combobox(
            search_container,
            values=POPULAR_CITIES,
            font=Theme.FONTS["body"],
        )
        self.city_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(2, 6), ipady=3)
        self.city_entry.bind("<Return>", lambda e: self._submit_search())
        self.city_entry.bind("<<ComboboxSelected>>", lambda e: self._submit_search())

        # Search Button
        self.btn_search = tk.Button(
            self,
            text="Search",
            font=Theme.FONTS["body_bold"],
            fg="#ffffff",
            bg=t["accent_primary"],
            activebackground=t["accent_hover"],
            activeforeground="#ffffff",
            bd=0,
            padx=16,
            pady=4,
            cursor="hand2",
            command=self._submit_search,
        )
        self.btn_search.pack(side=tk.LEFT, padx=6, pady=8)

        # Favourite Toggle Button (Star)
        self.btn_fav = tk.Button(
            self,
            text="★ Fav",
            font=Theme.FONTS["body_bold"],
            fg=t["accent_gold"],
            bg=t["bg_card_hover"],
            activebackground=t["bg_card_hover"],
            activeforeground=t["accent_gold"],
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._on_toggle_favourite,
        )
        self.btn_fav.pack(side=tk.LEFT, padx=4, pady=8)

        # Unit Toggle Button (°C / °F)
        self.btn_unit = tk.Button(
            self,
            text="°C / °F",
            font=Theme.FONTS["body_bold"],
            fg=t["text_primary"],
            bg=t["bg_card_hover"],
            activebackground=t["bg_card_hover"],
            activeforeground=t["accent_light"],
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self._on_unit_toggle,
        )
        self.btn_unit.pack(side=tk.LEFT, padx=4, pady=8)

        # Theme Toggle (Dark/Light)
        self.btn_theme = tk.Button(
            self,
            text="🌙" if t["name"] == "dark" else "☀️",
            font=("Segoe UI", 11),
            fg=t["text_primary"],
            bg=t["bg_card_hover"],
            activebackground=t["bg_card_hover"],
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._on_theme_toggle,
        )
        self.btn_theme.pack(side=tk.LEFT, padx=4, pady=8)

        # Settings Button (Gear)
        self.btn_settings = tk.Button(
            self,
            text="⚙ Settings",
            font=Theme.FONTS["caption"],
            fg=t["text_secondary"],
            bg=t["bg_card_hover"],
            activebackground=t["bg_card_hover"],
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=self._on_open_settings,
        )
        self.btn_settings.pack(side=tk.LEFT, padx=(4, 12), pady=8)

    def _submit_search(self):
        city = self.city_entry.get().strip()
        if city:
            self._on_search(city)

    def set_city_text(self, text: str):
        self.city_entry.set(text)

    def update_fav_status(self, is_fav: bool):
        t = self._theme
        if is_fav:
            self.btn_fav.config(text="★ Saved", fg=t["accent_gold"])
        else:
            self.btn_fav.config(text="☆ Add Fav", fg=t["text_secondary"])

    def update_unit_label(self, unit: str):
        self.btn_unit.config(text=f"Switch to °{'F' if unit == 'C' else 'C'}")


class QuickCityBar(tk.Frame):
    """
    Horizontal interactive strip of pre-selected popular cities.
    Allows 1-click immediate weather lookup according to selected city.
    """
    DEFAULT_CITIES = [
        "Bengaluru", "Mumbai", "Delhi", "Hyderabad",
        "London", "New York", "Tokyo", "Paris", "Dubai"
    ]

    def __init__(
        self,
        parent,
        on_city_select: Callable[[str], None],
        theme: Dict[str, Any],
        cities: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(parent, bg=theme["bg_main"], **kwargs)
        self._on_city_select = on_city_select
        self._theme = theme
        self._cities = cities or self.DEFAULT_CITIES
        self._active_city = ""
        self._buttons: Dict[str, tk.Button] = {}
        self._build_widgets()

    def _build_widgets(self):
        t = self._theme
        lbl = tk.Label(
            self,
            text="📍 Quick Cities:",
            font=Theme.FONTS["caption"],
            fg=t["text_secondary"],
            bg=t["bg_main"],
        )
        lbl.pack(side=tk.LEFT, padx=(4, 6))

        for city in self._cities:
            btn = tk.Button(
                self,
                text=city,
                font=Theme.FONTS["caption"],
                fg=t["text_primary"],
                bg=t["bg_card"],
                activebackground=t["accent_primary"],
                activeforeground="#ffffff",
                relief=tk.FLAT,
                bd=0,
                padx=9,
                pady=2,
                cursor="hand2",
                command=lambda c=city: self._on_click(c),
            )
            btn.pack(side=tk.LEFT, padx=3)
            self._buttons[city] = btn

    def _on_click(self, city: str):
        self.set_active_city(city)
        self._on_city_select(city)

    def set_active_city(self, city: str):
        self._active_city = city
        t = self._theme
        for c, btn in self._buttons.items():
            if c.lower() == city.lower():
                btn.config(bg=t["accent_primary"], fg="#ffffff")
            else:
                btn.config(bg=t["bg_card"], fg=t["text_primary"])


class CurrentWeatherPanel(tk.Frame):
    """
    Displays current conditions: City, Country, Current Temp,
    Weather Icon, Condition Badge, Feels-Like, Humidity, Pressure, Wind.
    Matches Figure 1: Current Weather Panel.
    """

    def __init__(self, parent, theme: Dict[str, Any], **kwargs):
        super().__init__(parent, bg=theme["bg_card"], bd=0, highlightthickness=1, **kwargs)
        self.config(highlightbackground=theme["border_color"])
        self._theme = theme

        self._build_widgets()

    def _build_widgets(self):
        t = self._theme

        # Top row: Location & Observation Timestamp
        top_row = tk.Frame(self, bg=t["bg_card"])
        top_row.pack(fill=tk.X, padx=18, pady=(14, 4))

        self.lbl_city = tk.Label(
            top_row,
            text="Search a city to view weather",
            font=Theme.FONTS["title"],
            fg=t["text_primary"],
            bg=t["bg_card"],
        )
        self.lbl_city.pack(side=tk.LEFT)

        self.lbl_country_badge = tk.Label(
            top_row,
            text="",
            font=Theme.FONTS["badge"],
            fg=t["accent_light"],
            bg=t["bg_card_hover"],
            padx=8,
            pady=2,
        )
        self.lbl_country_badge.pack(side=tk.LEFT, padx=10)

        self.lbl_time = tk.Label(
            top_row,
            text="",
            font=Theme.FONTS["caption"],
            fg=t["text_muted"],
            bg=t["bg_card"],
        )
        self.lbl_time.pack(side=tk.RIGHT)

        # Middle Hero Section: Icon + Big Temperature + Condition
        hero_frame = tk.Frame(self, bg=t["bg_card"])
        hero_frame.pack(fill=tk.X, padx=18, pady=8)

        self.lbl_icon = tk.Label(hero_frame, bg=t["bg_card"])
        self.lbl_icon.pack(side=tk.LEFT, padx=(0, 16))

        temp_col = tk.Frame(hero_frame, bg=t["bg_card"])
        temp_col.pack(side=tk.LEFT)

        self.lbl_temp = tk.Label(
            temp_col,
            text="--",
            font=Theme.FONTS["hero_temp"],
            fg=t["text_primary"],
            bg=t["bg_card"],
        )
        self.lbl_temp.pack(anchor=tk.W)

        self.lbl_condition = tk.Label(
            temp_col,
            text="Ready",
            font=Theme.FONTS["subtitle"],
            fg=t["accent_light"],
            bg=t["bg_card"],
        )
        self.lbl_condition.pack(anchor=tk.W)

        # Right Hero Info: Feels Like & Today Min/Max
        sub_info_col = tk.Frame(hero_frame, bg=t["bg_card"])
        sub_info_col.pack(side=tk.RIGHT, padx=10)

        self.lbl_feels_like = tk.Label(
            sub_info_col,
            text="Feels like: --",
            font=Theme.FONTS["body_bold"],
            fg=t["text_secondary"],
            bg=t["bg_card"],
        )
        self.lbl_feels_like.pack(anchor=tk.E, pady=2)

        self.lbl_min_max = tk.Label(
            sub_info_col,
            text="H: --  L: --",
            font=Theme.FONTS["body"],
            fg=t["text_muted"],
            bg=t["bg_card"],
        )
        self.lbl_min_max.pack(anchor=tk.E, pady=2)

        # Divider
        divider = tk.Frame(self, bg=t["border_color"], height=1)
        divider.pack(fill=tk.X, padx=18, pady=(4, 10))

        # Bottom Metric Chips: Humidity, Pressure, Wind Speed
        metrics_frame = tk.Frame(self, bg=t["bg_card"])
        metrics_frame.pack(fill=tk.X, padx=18, pady=(0, 14))

        self.chip_humidity = self._create_metric_chip(metrics_frame, "💧 Humidity", "-- %")
        self.chip_humidity.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.chip_pressure = self._create_metric_chip(metrics_frame, "🧭 Pressure", "-- hPa")
        self.chip_pressure.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

        self.chip_wind = self._create_metric_chip(metrics_frame, "💨 Wind Speed", "-- m/s")
        self.chip_wind.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))

    def _create_metric_chip(self, parent, title: str, default_val: str) -> tk.Frame:
        t = self._theme
        chip = tk.Frame(parent, bg=t["bg_card_hover"], padx=10, pady=8)
        lbl_t = tk.Label(chip, text=title, font=Theme.FONTS["small"], fg=t["text_muted"], bg=t["bg_card_hover"])
        lbl_t.pack(anchor=tk.W)
        lbl_v = tk.Label(chip, text=default_val, font=Theme.FONTS["body_bold"], fg=t["text_primary"], bg=t["bg_card_hover"])
        lbl_v.pack(anchor=tk.W, pady=(2, 0))
        chip.val_label = lbl_v  # keep ref
        return chip

    def update_weather(self, weather: WeatherData, unit: str = "C", is_dark: bool = True):
        t = self._theme
        loc_str = weather.city
        self.lbl_city.config(text=loc_str)
        if weather.country:
            self.lbl_country_badge.config(text=f"📍 {weather.country}")
            self.lbl_country_badge.pack(side=tk.LEFT, padx=10)
        else:
            self.lbl_country_badge.pack_forget()

        self.lbl_time.config(text=f"Observed: {weather.timestamp.strftime('%I:%M %p')}")

        unit_symbol = "°C" if unit == "C" else "°F"
        temp_val = weather.to_celsius() if unit == "C" else weather.to_fahrenheit()
        feels_val = weather.feels_like if unit == "C" else weather.feels_like_fahrenheit()

        self.lbl_temp.config(text=f"{temp_val:.1f}{unit_symbol}")
        self.lbl_condition.config(text=weather.description)
        self.lbl_feels_like.config(text=f"Feels like: {feels_val:.1f}{unit_symbol}")

        min_val = weather.temp_min if unit == "C" else round((weather.temp_min * 9/5) + 32, 1)
        max_val = weather.temp_max if unit == "C" else round((weather.temp_max * 9/5) + 32, 1)
        self.lbl_min_max.config(text=f"High: {max_val:.1f}{unit_symbol}   Low: {min_val:.1f}{unit_symbol}")

        # Metrics chips
        self.chip_humidity.val_label.config(text=f"{weather.humidity}%")
        self.chip_pressure.val_label.config(text=f"{weather.pressure} hPa")
        self.chip_wind.val_label.config(text=f"{weather.wind_speed} m/s")

        # Weather Icon
        photo = WeatherIconGenerator.get_icon(weather.icon or weather.description, size=64, is_dark=is_dark)
        self.lbl_icon.config(image=photo)
        self.lbl_icon.image = photo


class WeatherAnalyticsBanner(tk.Frame):
    """
    Displays calculated statistics from WeatherAnalyzer:
    - 5-day Average temperature
    - Highest forecast temp
    - Lowest forecast temp
    - Trend analysis (Warming / Cooling / Stable)
    """

    def __init__(self, parent, theme: Dict[str, Any], **kwargs):
        super().__init__(parent, bg=theme["bg_card"], bd=0, highlightthickness=1, **kwargs)
        self.config(highlightbackground=theme["border_color"])
        self._theme = theme

        self._build_widgets()

    def _build_widgets(self):
        t = self._theme

        title_row = tk.Frame(self, bg=t["bg_card"])
        title_row.pack(fill=tk.X, padx=16, pady=(10, 6))

        title_lbl = tk.Label(
            title_row,
            text="📊 5-Day Meteorological Analysis",
            font=Theme.FONTS["body_bold"],
            fg=t["text_primary"],
            bg=t["bg_card"],
        )
        title_lbl.pack(side=tk.LEFT)

        self.trend_badge = tk.Label(
            title_row,
            text="Trend: Calculating...",
            font=Theme.FONTS["badge"],
            fg=t["accent_warm"],
            bg=t["bg_card_hover"],
            padx=8,
            pady=2,
        )
        self.trend_badge.pack(side=tk.RIGHT)

        stats_row = tk.Frame(self, bg=t["bg_card"])
        stats_row.pack(fill=tk.X, padx=16, pady=(0, 10))

        self.lbl_avg = tk.Label(
            stats_row,
            text="Avg Temp: --",
            font=Theme.FONTS["body"],
            fg=t["text_secondary"],
            bg=t["bg_card"],
        )
        self.lbl_avg.pack(side=tk.LEFT, padx=(0, 20))

        self.lbl_high = tk.Label(
            stats_row,
            text="Peak High: --",
            font=Theme.FONTS["body"],
            fg=t["accent_warm"],
            bg=t["bg_card"],
        )
        self.lbl_high.pack(side=tk.LEFT, padx=(0, 20))

        self.lbl_low = tk.Label(
            stats_row,
            text="Lowest Low: --",
            font=Theme.FONTS["body"],
            fg=t["accent_light"],
            bg=t["bg_card"],
        )
        self.lbl_low.pack(side=tk.LEFT, padx=(0, 20))

        self.lbl_rain = tk.Label(
            stats_row,
            text="Precipitation: None expected",
            font=Theme.FONTS["body"],
            fg=t["accent_success"],
            bg=t["bg_card"],
        )
        self.lbl_rain.pack(side=tk.LEFT)

    def update_analysis(self, summary: Dict[str, Any]):
        u = summary.get("unit", "°C")
        self.lbl_avg.config(text=f"Avg Temp: {summary.get('average_temp', 0):.1f}{u}")
        self.lbl_high.config(text=f"Peak High: {summary.get('highest_temp', 0):.1f}{u}")
        self.lbl_low.config(text=f"Lowest Low: {summary.get('lowest_temp', 0):.1f}{u}")
        self.trend_badge.config(text=summary.get("trend", "Stable"))

        rain_count = summary.get("rainy_day_count", 0)
        if rain_count > 0:
            self.lbl_rain.config(
                text=f"⚠️ Rain expected on {rain_count} day(s)",
                fg=self._theme["accent_warm"],
            )
        else:
            self.lbl_rain.config(
                text="✓ No rain anticipated",
                fg=self._theme["accent_success"],
            )


class FiveDayForecastPanel(tk.Frame):
    """
    Displays 5 day-wise cards for the upcoming forecast.
    Matches Figure 1: 5-Day Forecast Panel.
    """

    def __init__(self, parent, theme: Dict[str, Any], **kwargs):
        super().__init__(parent, bg=theme["bg_main"], bd=0, **kwargs)
        self._theme = theme
        self._cards: List[tk.Frame] = []

        self._build_widgets()

    def _build_widgets(self):
        t = self._theme

        title_lbl = tk.Label(
            self,
            text="📅 5-Day Extended Weather Outlook",
            font=Theme.FONTS["body_bold"],
            fg=t["text_primary"],
            bg=t["bg_main"],
        )
        title_lbl.pack(anchor=tk.W, pady=(4, 6))

        self.cards_container = tk.Frame(self, bg=t["bg_main"])
        self.cards_container.pack(fill=tk.X, expand=True)

    def update_forecast(self, forecasts: List[ForecastDay], unit: str = "C", is_dark: bool = True):
        # Clear previous cards
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        self._cards.clear()

        t = self._theme
        unit_sym = "°C" if unit == "C" else "°F"

        for f in forecasts:
            card = tk.Frame(
                self.cards_container,
                bg=t["bg_card"],
                bd=0,
                highlightthickness=1,
                padx=10,
                pady=10,
            )
            card.config(highlightbackground=t["border_color"])
            card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

            # Date Label
            lbl_date = tk.Label(
                card,
                text=f.date,
                font=Theme.FONTS["body_bold"],
                fg=t["text_primary"],
                bg=t["bg_card"],
            )
            lbl_date.pack(anchor=tk.CENTER)

            # Weather Icon
            icon_photo = WeatherIconGenerator.get_icon(f.icon or f.description, size=42, is_dark=is_dark)
            lbl_ic = tk.Label(card, image=icon_photo, bg=t["bg_card"])
            lbl_ic.image = icon_photo
            lbl_ic.pack(anchor=tk.CENTER, pady=4)

            # Condition short description
            cond_text = f.description[:14] + "..." if len(f.description) > 14 else f.description
            lbl_cond = tk.Label(
                card,
                text=cond_text,
                font=Theme.FONTS["caption"],
                fg=t["text_secondary"],
                bg=t["bg_card"],
            )
            lbl_cond.pack(anchor=tk.CENTER)

            # Temperatures (Max / Min)
            max_val = f.temp_max if unit == "C" else f.temp_max_fahrenheit()
            min_val = f.temp_min if unit == "C" else f.temp_min_fahrenheit()

            temp_box = tk.Frame(card, bg=t["bg_card"])
            temp_box.pack(anchor=tk.CENTER, pady=(6, 2))

            lbl_h = tk.Label(
                temp_box,
                text=f"{max_val:.0f}{unit_sym}",
                font=Theme.FONTS["body_bold"],
                fg=t["accent_warm"],
                bg=t["bg_card"],
            )
            lbl_h.pack(side=tk.LEFT, padx=3)

            lbl_sep = tk.Label(temp_box, text="/", font=Theme.FONTS["caption"], fg=t["text_muted"], bg=t["bg_card"])
            lbl_sep.pack(side=tk.LEFT)

            lbl_l = tk.Label(
                temp_box,
                text=f"{min_val:.0f}{unit_sym}",
                font=Theme.FONTS["body"],
                fg=t["accent_light"],
                bg=t["bg_card"],
            )
            lbl_l.pack(side=tk.LEFT, padx=3)

            # Rain probability badge
            pop_fg = t["accent_light"] if f.pop > 10 else t["text_muted"]
            lbl_pop = tk.Label(
                card,
                text=f"💧 {f.pop:.0f}%" if f.pop > 0 else "💧 0%",
                font=Theme.FONTS["small"],
                fg=pop_fg,
                bg=t["bg_card"],
            )
            lbl_pop.pack(anchor=tk.CENTER, pady=(2, 0))

            self._cards.append(card)


class HistoryDrawer(tk.Frame):
    """
    Drawer/Sidebar showing recent search history and saved favourites.
    Provides one-click weather querying.
    """

    def __init__(
        self,
        parent,
        on_city_click: Callable[[str], None],
        on_remove_fav: Callable[[str], None],
        theme: Dict[str, Any],
        **kwargs,
    ):
        super().__init__(parent, bg=theme["bg_card"], bd=0, highlightthickness=1, **kwargs)
        self.config(highlightbackground=theme["border_color"])
        self._on_city_click = on_city_click
        self._on_remove_fav = on_remove_fav
        self._theme = theme

        self._build_widgets()

    def _build_widgets(self):
        t = self._theme

        header = tk.Label(
            self,
            text="⭐ Saved Favourites",
            font=Theme.FONTS["body_bold"],
            fg=t["text_primary"],
            bg=t["bg_card"],
        )
        header.pack(anchor=tk.W, padx=12, pady=(10, 4))

        self.fav_container = tk.Frame(self, bg=t["bg_card"])
        self.fav_container.pack(fill=tk.X, padx=10, pady=(0, 10))

        div = tk.Frame(self, bg=t["border_color"], height=1)
        div.pack(fill=tk.X, padx=10, pady=4)

        hist_header = tk.Label(
            self,
            text="🕒 Recent Searches",
            font=Theme.FONTS["body_bold"],
            fg=t["text_primary"],
            bg=t["bg_card"],
        )
        hist_header.pack(anchor=tk.W, padx=12, pady=(8, 4))

        self.hist_container = tk.Frame(self, bg=t["bg_card"])
        self.hist_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def update_lists(self, favourites: List[str], history: List[str]):
        t = self._theme

        # Update Favourites
        for w in self.fav_container.winfo_children():
            w.destroy()

        if not favourites:
            empty_lbl = tk.Label(
                self.fav_container,
                text="No favourites saved",
                font=Theme.FONTS["caption"],
                fg=t["text_muted"],
                bg=t["bg_card"],
            )
            empty_lbl.pack(anchor=tk.W, padx=4, pady=2)
        else:
            for city in favourites[:6]:
                row = tk.Frame(self.fav_container, bg=t["bg_card_hover"], pady=2, padx=6)
                row.pack(fill=tk.X, pady=2)

                btn = tk.Button(
                    row,
                    text=f"★ {city}",
                    font=Theme.FONTS["caption"],
                    fg=t["text_primary"],
                    bg=t["bg_card_hover"],
                    activebackground=t["accent_primary"],
                    activeforeground="#ffffff",
                    bd=0,
                    anchor=tk.W,
                    cursor="hand2",
                    command=lambda c=city: self._on_city_click(c),
                )
                btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

                del_btn = tk.Button(
                    row,
                    text="✕",
                    font=("Segoe UI", 8),
                    fg=t["text_muted"],
                    bg=t["bg_card_hover"],
                    activeforeground=t["accent_danger"],
                    bd=0,
                    cursor="hand2",
                    command=lambda c=city: self._on_remove_fav(c),
                )
                del_btn.pack(side=tk.RIGHT)

        # Update History
        for w in self.hist_container.winfo_children():
            w.destroy()

        if not history:
            empty_h = tk.Label(
                self.hist_container,
                text="No recent searches",
                font=Theme.FONTS["caption"],
                fg=t["text_muted"],
                bg=t["bg_card"],
            )
            empty_h.pack(anchor=tk.W, padx=4, pady=2)
        else:
            for city in history[:8]:
                btn = tk.Button(
                    self.hist_container,
                    text=f"• {city}",
                    font=Theme.FONTS["caption"],
                    fg=t["text_secondary"],
                    bg=t["bg_card"],
                    activebackground=t["bg_card_hover"],
                    activeforeground=t["accent_light"],
                    bd=0,
                    anchor=tk.W,
                    cursor="hand2",
                    command=lambda c=city: self._on_city_click(c),
                )
                btn.pack(fill=tk.X, pady=1)


class StatusBar(tk.Frame):
    """
    Bottom Status bar showing API connection state, auto-refresh status, and university microproject info.
    """

    def __init__(self, parent, theme: Dict[str, Any], **kwargs):
        super().__init__(parent, bg=theme["bg_card"], bd=0, highlightthickness=1, **kwargs)
        self.config(highlightbackground=theme["border_color"])
        self._theme = theme

        self._build_widgets()

    def _build_widgets(self):
        t = self._theme

        self.lbl_status = tk.Label(
            self,
            text="Ready",
            font=Theme.FONTS["small"],
            fg=t["text_secondary"],
            bg=t["bg_card"],
        )
        self.lbl_status.pack(side=tk.LEFT, padx=12, pady=4)

        self.lbl_team = tk.Label(
            self,
            text="Alliance University | OOP Micro-Project",
            font=Theme.FONTS["small"],
            fg=t["text_muted"],
            bg=t["bg_card"],
        )
        self.lbl_team.pack(side=tk.RIGHT, padx=12, pady=4)

        self.lbl_mode = tk.Label(
            self,
            text="Mode: Live API",
            font=Theme.FONTS["small"],
            fg=t["accent_success"],
            bg=t["bg_card"],
        )
        self.lbl_mode.pack(side=tk.RIGHT, padx=16, pady=4)

    def set_status(self, text: str, is_error: bool = False):
        fg = self._theme["accent_danger"] if is_error else self._theme["text_secondary"]
        self.lbl_status.config(text=text, fg=fg)

    def set_mode(self, is_live: bool):
        if is_live:
            self.lbl_mode.config(text="● Mode: Live OpenWeatherMap API", fg=self._theme["accent_success"])
        else:
            self.lbl_mode.config(text="○ Mode: Demo / Simulated Fallback", fg=self._theme["accent_gold"])
