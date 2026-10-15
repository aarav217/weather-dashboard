"""
gui/app.py
WeatherApp class: Central GUI controller for the Weather Forecast Dashboard.
Matches Figure 1 (System Architecture), Figure 2 (Flow Diagram), and Figure 3 (Class Diagram).
Demonstrates Multithreading, MVC pattern, responsive Tkinter design, and robust exception handling.
"""

import sys
import os
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional, List, Dict, Any

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from gui.theme import Theme
from gui.components import (
    SearchToolbar,
    QuickCityBar,
    CurrentWeatherPanel,
    WeatherAnalyticsBanner,
    FiveDayForecastPanel,
    HistoryDrawer,
    StatusBar,
)
from services.validator import InputValidator
from services.api_client import WeatherAPIClient
from services.data_parser import DataParser
from analysis.analyzer import WeatherAnalyzer
from analysis.chart_plotter import ChartPlotter
from storage.storage_manager import StorageManager
from models.weather_data import WeatherData, ForecastDay
from models.exceptions import WeatherAppException, InvalidInputError, CityNotFoundError


class WeatherApp:
    """
    Main Controller and Presentation Layer for the Weather Forecast Dashboard.
    Strictly implements Figure 3 Class Diagram attributes and methods:
    - root: Tk
    - city_entry: Entry
    - unit: String ('C' or 'F')
    + build_ui(): void
    + on_search(): void
    + update_display(): void
    + show_error(msg): void
    """

    def __init__(self, root: tk.Tk):
        # Attributes matching Figure 3
        self.root: tk.Tk = root
        self.city_entry: Optional[tk.Entry] = None
        self.unit: str = "C"  # "C" or "F"

        # App Configuration & Architecture Layers
        self.storage: StorageManager = StorageManager()
        self.settings: Dict[str, Any] = self.storage.load_settings()
        self.unit = self.settings.get("temp_unit", "C")
        self.current_theme_name: str = self.settings.get("theme", "dark")
        self.theme: Dict[str, Any] = Theme.DARK if self.current_theme_name == "dark" else Theme.LIGHT

        # Service & Analysis layers
        api_key = self.settings.get("api_key", "")
        self.api_client: WeatherAPIClient = WeatherAPIClient(api_key=api_key)
        self.analyzer: WeatherAnalyzer = WeatherAnalyzer()
        self.plotter: ChartPlotter = ChartPlotter()

        # State tracking
        self.current_weather: Optional[WeatherData] = None
        self.forecast_list: List[ForecastDay] = []
        self._is_fetching: bool = False
        self._refresh_timer_id: Optional[str] = None
        self._canvas_tk: Optional[FigureCanvasTkAgg] = None
        self._task_queue: queue.Queue = queue.Queue()

        # Build GUI
        self.build_ui()

        # Start checking thread queue on main Tkinter loop
        self._check_queue()

        # Initial load: search last city or default
        initial_city = self.settings.get("last_city", "Bengaluru")
        self.toolbar.set_city_text(initial_city)
        self.root.after(200, lambda: self._execute_search_threaded(initial_city))

        # Schedule auto-refresh if enabled
        self._schedule_auto_refresh()

        # Ensure window is visible and focused
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(350, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

    def _check_queue(self) -> None:
        """Processes background thread messages safely on the Tkinter main event thread."""
        try:
            while True:
                task_type, payload = self._task_queue.get_nowait()
                if task_type == "SUCCESS":
                    weather_obj, forecast_objs = payload
                    self._on_fetch_success(weather_obj, forecast_objs)
                elif task_type == "FAILURE":
                    self._on_fetch_failure(payload)
        except queue.Empty:
            pass
        finally:
            self.root.after(60, self._check_queue)

    def build_ui(self) -> None:
        """
        Constructs the graphical user interface.
        Matches Figure 3: + build_ui(): void
        """
        self.root.title("Weather Forecast Dashboard | Alliance University Micro-Project")
        self.root.geometry("1100x820")
        self.root.minsize(980, 720)
        self.root.configure(bg=self.theme["bg_main"])

        # Top level container
        main_container = tk.Frame(self.root, bg=self.theme["bg_main"])
        main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Search Toolbar (Top) with Combobox City Selector
        self.toolbar = SearchToolbar(
            main_container,
            on_search=self.on_search,
            on_unit_toggle=self._toggle_unit,
            on_theme_toggle=self._toggle_theme,
            on_toggle_favourite=self._toggle_favourite,
            on_open_settings=self._open_settings_dialog,
            theme=self.theme,
        )
        self.toolbar.pack(fill=tk.X, padx=14, pady=(12, 4))
        self.city_entry = self.toolbar.city_entry
        self.toolbar.update_unit_label(self.unit)

        # 1b. Quick City Pills (1-click weather for selected cities)
        self.quick_cities_bar = QuickCityBar(
            main_container,
            on_city_select=self.on_search,
            theme=self.theme,
        )
        self.quick_cities_bar.pack(fill=tk.X, padx=14, pady=(0, 8))

        # Body area: Left content area + Right history sidebar
        body_frame = tk.Frame(main_container, bg=self.theme["bg_main"])
        body_frame.pack(fill=tk.BOTH, expand=True, padx=14, pady=0)

        # Left Column (Main Dashboard Content)
        left_col = tk.Frame(body_frame, bg=self.theme["bg_main"])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # 2. Current Weather Hero Panel (Figure 1)
        self.current_panel = CurrentWeatherPanel(left_col, theme=self.theme)
        self.current_panel.pack(fill=tk.X, pady=(0, 8))

        # 3. Weather Analytics Banner (Calculated by WeatherAnalyzer)
        self.analytics_banner = WeatherAnalyticsBanner(left_col, theme=self.theme)
        self.analytics_banner.pack(fill=tk.X, pady=(0, 8))

        # 4. 5-Day Forecast Panel (Figure 1)
        self.forecast_panel = FiveDayForecastPanel(left_col, theme=self.theme)
        self.forecast_panel.pack(fill=tk.X, pady=(0, 8))

        # 5. Temperature Trend Chart Container (Figure 1)
        chart_card = tk.Frame(left_col, bg=self.theme["bg_card"], bd=0, highlightthickness=1)
        chart_card.config(highlightbackground=self.theme["border_color"])
        chart_card.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        # Embed Matplotlib canvas into Tkinter
        self._canvas_tk = FigureCanvasTkAgg(self.plotter.figure, master=chart_card)
        self._canvas_tk.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # Right Column (Search History & Saved Favourites Drawer)
        self.drawer = HistoryDrawer(
            body_frame,
            on_city_click=self._on_history_city_clicked,
            on_remove_fav=self._on_remove_favourite,
            theme=self.theme,
            width=240,
        )
        self.drawer.pack(side=tk.RIGHT, fill=tk.Y, pady=(0, 6))
        self.drawer.update_lists(self.storage.favourites, self.storage.history)

        # 6. Status Bar (Bottom)
        self.status_bar = StatusBar(self.root, theme=self.theme)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.set_mode(self.api_client.is_live_configured())

    def on_search(self, city_name: Optional[str] = None) -> None:
        """
        Triggered when user clicks Search or presses Enter in city_entry.
        Matches Figure 3: + on_search(): void
        Follows Figure 2 Flowchart:
        - Input validation
        - Threaded REST API call
        - Safe UI dispatch
        """
        if self._is_fetching:
            return

        raw_city = city_name if city_name else (self.city_entry.get() if self.city_entry else "")

        try:
            # Figure 2: Step 3 Input Validation
            validated_city = InputValidator.validate_city(raw_city)
        except InvalidInputError as err:
            self.show_error(str(err.message))
            return

        # Start non-blocking multithreaded request
        self._execute_search_threaded(validated_city)

    def _execute_search_threaded(self, city: str) -> None:
        """
        Executes REST API requests on a background thread to prevent GUI freezing.
        Matches Proposal Section 4.0: "Network calls run in background threads".
        """
        self._is_fetching = True
        self.status_bar.set_status(f"Fetching meteorological data for '{city}'...", is_error=False)
        self.toolbar.btn_search.config(state=tk.DISABLED, text="Loading...")

        def thread_target():
            try:
                # Figure 2: Step 4 REST API Request
                current_raw = self.api_client.fetch_current(city)
                forecast_raw = self.api_client.fetch_forecast(city)

                # Figure 2: Step 6 JSON Parsing
                weather_obj = DataParser.parse_current_weather(current_raw)
                forecast_objs = DataParser.parse_forecast(forecast_raw)

                # Safe dispatch to main loop queue
                self._task_queue.put(("SUCCESS", (weather_obj, forecast_objs)))

            except WeatherAppException as e:
                self._task_queue.put(("FAILURE", str(e.message)))
            except Exception as e:
                self._task_queue.put(("FAILURE", f"Unexpected error: {str(e)}"))

        thread = threading.Thread(target=thread_target, daemon=True)
        thread.start()

    def _on_fetch_success(self, weather: WeatherData, forecasts: List[ForecastDay]) -> None:
        """Callback on main thread when weather fetch completes successfully."""
        self._is_fetching = False
        self.toolbar.btn_search.config(state=tk.NORMAL, text="Search")
        self.current_weather = weather
        self.forecast_list = forecasts

        # Figure 2: Step 8 Plot temperature chart and save city to search history
        self.storage.save_history(weather.city)
        self.storage.record_weather_observation(weather, forecasts)

        # Update last city in settings
        self.settings["last_city"] = weather.city
        self.storage.save_settings(self.settings)

        # Figure 2: Step 7 & 8 Update Display
        self.update_display()

        # Update favourite button status
        is_fav = weather.city in self.storage.favourites
        self.toolbar.update_fav_status(is_fav)

        # Update drawer history list
        self.drawer.update_lists(self.storage.favourites, self.storage.history)

        # Sync Quick City pill and Combobox text
        if hasattr(self, "quick_cities_bar"):
            self.quick_cities_bar.set_active_city(weather.city)
        if hasattr(self, "toolbar"):
            self.toolbar.set_city_text(weather.city)

        self.status_bar.set_status(f"✓ Weather data updated for {weather.city} at {weather.timestamp.strftime('%I:%M:%S %p')}")
        self.status_bar.set_mode(self.api_client.is_live_configured())

    def _on_fetch_failure(self, error_message: str) -> None:
        """Callback on main thread when fetch fails."""
        self._is_fetching = False
        self.toolbar.btn_search.config(state=tk.NORMAL, text="Search")
        self.status_bar.set_status(f"Error: {error_message}", is_error=True)
        self.show_error(error_message)

    def update_display(self) -> None:
        """
        Updates all dashboard display panels with current model data.
        Matches Figure 3: + update_display(): void
        """
        if not self.current_weather:
            return

        is_dark = self.theme["name"] == "dark"

        # 1. Update Current Weather Panel
        self.current_panel.update_weather(self.current_weather, unit=self.unit, is_dark=is_dark)

        # 2. Update 5-Day Forecast Panel
        self.forecast_panel.update_forecast(self.forecast_list, unit=self.unit, is_dark=is_dark)

        # 3. Update Weather Analytics Banner (Calculated by WeatherAnalyzer)
        self.analyzer.forecasts = self.forecast_list
        summary = self.analyzer.get_comprehensive_summary(is_fahrenheit=(self.unit == "F"))
        self.analytics_banner.update_analysis(summary)

        # 4. Update Matplotlib Chart (ChartPlotter)
        unit_str = "°F" if self.unit == "F" else "°C"
        self.plotter.plot_temperature(self.forecast_list, unit=unit_str, is_dark=is_dark)
        if self._canvas_tk:
            self._canvas_tk.draw()

    def show_error(self, msg: str) -> None:
        """
        Displays an error dialog to the user.
        Matches Figure 3: + show_error(msg): void
        """
        messagebox.showerror("Weather Dashboard Notice", msg, parent=self.root)

    # -------------------------------------------------------------------------
    # Unit, Favourite, Theme, and Drawer Actions
    # -------------------------------------------------------------------------
    def _toggle_unit(self) -> None:
        """Toggles temperature unit between Celsius and Fahrenheit."""
        self.unit = "F" if self.unit == "C" else "C"
        self.settings["temp_unit"] = self.unit
        self.storage.save_settings(self.settings)
        self.toolbar.update_unit_label(self.unit)
        self.update_display()
        self.status_bar.set_status(f"Temperature units toggled to °{self.unit}")

    def _toggle_favourite(self) -> None:
        """Adds or removes the currently viewed city from favourites."""
        if not self.current_weather:
            return

        city = self.current_weather.city
        if city in self.storage.favourites:
            self.storage.remove_favourite(city)
            self.toolbar.update_fav_status(False)
            self.status_bar.set_status(f"Removed '{city}' from favourites.")
        else:
            self.storage.add_favourite(city)
            self.toolbar.update_fav_status(True)
            self.status_bar.set_status(f"Added '{city}' to favourites.")

        self.drawer.update_lists(self.storage.favourites, self.storage.history)

    def _on_remove_favourite(self, city: str) -> None:
        """Removes a favourite city clicked from the drawer."""
        self.storage.remove_favourite(city)
        if self.current_weather and self.current_weather.city == city:
            self.toolbar.update_fav_status(False)
        self.drawer.update_lists(self.storage.favourites, self.storage.history)
        self.status_bar.set_status(f"Removed '{city}' from favourites.")

    def _on_history_city_clicked(self, city: str) -> None:
        """Queries weather when a city is clicked from history or favourites."""
        self.toolbar.set_city_text(city)
        self.on_search(city)

    def _toggle_theme(self) -> None:
        """Toggles between Dark and Light theme."""
        new_theme = "light" if self.current_theme_name == "dark" else "dark"
        self.current_theme_name = new_theme
        self.theme = Theme.LIGHT if new_theme == "light" else Theme.DARK
        self.settings["theme"] = new_theme
        self.storage.save_settings(self.settings)

        # Rebuild UI with the new theme
        for widget in self.root.winfo_children():
            widget.destroy()

        self.build_ui()
        self.update_display()

    # -------------------------------------------------------------------------
    # Auto-Refresh & Background Periodic Polling
    # -------------------------------------------------------------------------
    def _schedule_auto_refresh(self) -> None:
        """Schedules recurring auto-refresh in milliseconds based on user settings."""
        if self._refresh_timer_id:
            self.root.after_cancel(self._refresh_timer_id)
            self._refresh_timer_id = None

        if self.settings.get("auto_refresh_enabled", False):
            minutes = self.settings.get("refresh_minutes", 30)
            ms = max(60, minutes * 60) * 1000  # at least 1 minute

            def auto_tick():
                if self.current_weather and not self._is_fetching:
                    self.status_bar.set_status("Auto-refreshing weather data...")
                    self._execute_search_threaded(self.current_weather.city)
                self._schedule_auto_refresh()

            self._refresh_timer_id = self.root.after(ms, auto_tick)

    # -------------------------------------------------------------------------
    # Settings & Configuration Modal
    # -------------------------------------------------------------------------
    def _open_settings_dialog(self) -> None:
        """Opens modal dialog for API Key, Auto-refresh, and Team Info."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Dashboard Settings & API Configuration")
        dialog.geometry("540x560")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        t = self.theme
        dialog.configure(bg=t["bg_card"])

        padding = 16

        # Title
        tk.Label(
            dialog,
            text="⚙ Dashboard Configuration",
            font=Theme.FONTS["subtitle"],
            fg=t["text_primary"],
            bg=t["bg_card"],
        ).pack(anchor=tk.W, padx=padding, pady=(16, 6))

        tk.Label(
            dialog,
            text="Configure your OpenWeatherMap REST API key, polling interval, and view project metadata.",
            font=Theme.FONTS["caption"],
            fg=t["text_secondary"],
            bg=t["bg_card"],
            wraplength=500,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, padx=padding, pady=(0, 12))

        # API Key Section
        api_box = tk.LabelFrame(
            dialog,
            text=" OpenWeatherMap REST API Key ",
            font=Theme.FONTS["body_bold"],
            fg=t["text_primary"],
            bg=t["bg_card"],
            padx=12,
            pady=10,
        )
        api_box.pack(fill=tk.X, padx=padding, pady=6)

        entry_key = tk.Entry(
            api_box,
            font=Theme.FONTS["body"],
            fg=t["text_primary"],
            bg=t["bg_main"],
            insertbackground=t["accent_light"],
            bd=1,
            relief=tk.SOLID,
        )
        entry_key.insert(0, self.api_client.api_key)
        entry_key.pack(fill=tk.X, pady=(2, 6))

        tk.Label(
            api_box,
            text="Tip: Leave blank or 'DEMO' to run the offline simulator with realistic data for any city.",
            font=Theme.FONTS["small"],
            fg=t["text_muted"],
            bg=t["bg_card"],
        ).pack(anchor=tk.W)

        # Auto-Refresh Section
        refresh_box = tk.LabelFrame(
            dialog,
            text=" Auto-Refresh Preferences ",
            font=Theme.FONTS["body_bold"],
            fg=t["text_primary"],
            bg=t["bg_card"],
            padx=12,
            pady=10,
        )
        refresh_box.pack(fill=tk.X, padx=padding, pady=6)

        auto_ref_var = tk.BooleanVar(value=self.settings.get("auto_refresh_enabled", False))
        chk_ref = tk.Checkbutton(
            refresh_box,
            text="Enable Periodic Auto-Refresh",
            variable=auto_ref_var,
            font=Theme.FONTS["body"],
            fg=t["text_primary"],
            bg=t["bg_card"],
            activebackground=t["bg_card"],
            selectcolor=t["bg_main"],
        )
        chk_ref.pack(anchor=tk.W)

        interval_row = tk.Frame(refresh_box, bg=t["bg_card"])
        interval_row.pack(fill=tk.X, pady=(6, 0))

        tk.Label(
            interval_row,
            text="Refresh Interval (Minutes):",
            font=Theme.FONTS["body"],
            fg=t["text_secondary"],
            bg=t["bg_card"],
        ).pack(side=tk.LEFT)

        spin_min = tk.Spinbox(
            interval_row,
            from_=5,
            to=120,
            increment=5,
            width=6,
            font=Theme.FONTS["body"],
            bg=t["bg_main"],
            fg=t["text_primary"],
        )
        spin_min.delete(0, tk.END)
        spin_min.insert(0, str(self.settings.get("refresh_minutes", 30)))
        spin_min.pack(side=tk.LEFT, padx=10)

        # University Project Details Box
        univ_box = tk.LabelFrame(
            dialog,
            text=" Alliance University Micro-Project Details ",
            font=Theme.FONTS["body_bold"],
            fg=t["text_primary"],
            bg=t["bg_card"],
            padx=12,
            pady=8,
        )
        univ_box.pack(fill=tk.X, padx=padding, pady=6)

        info_text = (
            "Alliance School of Advanced Computing\n"
            "Project: Weather Forecast Dashboard using REST API and Tkinter GUI\n"
            "Team: Aarav Pandey, Nikhil Shivhare, Nripendra Singh, Tarun Porwal, Yuvraj Kumar"
        )
        tk.Label(
            univ_box,
            text=info_text,
            font=Theme.FONTS["small"],
            fg=t["text_secondary"],
            bg=t["bg_card"],
            justify=tk.LEFT,
        ).pack(anchor=tk.W)

        # Save Button & Actions
        btn_row = tk.Frame(dialog, bg=t["bg_card"])
        btn_row.pack(fill=tk.X, padx=padding, pady=(16, 12))

        def save_and_close():
            new_key = entry_key.get().strip()
            self.api_client.api_key = new_key
            self.settings["api_key"] = new_key
            self.settings["auto_refresh_enabled"] = auto_ref_var.get()
            try:
                self.settings["refresh_minutes"] = int(spin_min.get())
            except ValueError:
                self.settings["refresh_minutes"] = 30

            self.storage.save_settings(self.settings)
            self.status_bar.set_mode(self.api_client.is_live_configured())
            self._schedule_auto_refresh()
            dialog.destroy()
            messagebox.showinfo("Settings Saved", "Preferences updated successfully!", parent=self.root)

        btn_save = tk.Button(
            btn_row,
            text="Save Settings",
            font=Theme.FONTS["body_bold"],
            fg="#ffffff",
            bg=t["accent_primary"],
            activebackground=t["accent_hover"],
            activeforeground="#ffffff",
            bd=0,
            padx=18,
            pady=6,
            cursor="hand2",
            command=save_and_close,
        )
        btn_save.pack(side=tk.RIGHT, padx=(8, 0))

        btn_cancel = tk.Button(
            btn_row,
            text="Cancel",
            font=Theme.FONTS["body"],
            fg=t["text_secondary"],
            bg=t["bg_card_hover"],
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=dialog.destroy,
        )
        btn_cancel.pack(side=tk.RIGHT)
