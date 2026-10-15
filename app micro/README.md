# Weather Forecast Dashboard using REST API and Tkinter GUI

**Alliance University — Alliance School of Advanced Computing**  
**Course Micro-Project Proposal & Implementation**

---

## 👥 Student Team Members

| Sl. No. | Student Name | Registration Number |
| :---: | :--- | :--- |
| 1 | **AARAV PANDEY** | **2411021060227** |
| 2 | **NIKHIL SHIVHARE** | **2411021060262** |
| 3 | **NRIPENDRA SINGH** | **2411021060229** |
| 4 | **TARUN PORWAL** | **2411021060153** |
| 5 | **YUVRAJ KUMAR** | **2411021060208** |

---

## 📌 Project Overview

The **Weather Forecast Dashboard** is an Object-Oriented Software Application developed in **Python** featuring an interactive **Tkinter GUI**, communication with online weather services via a **REST API (OpenWeatherMap)**, and multi-tier persistence via an **SQLite database** and **JSON files**.

### Key Highlights
- **100% Ad-Free & Lightweight Desktop Experience**: Eliminates web bloat and slow multi-step browser interfaces.
- **Background Multithreading**: Prevents UI freeze by executing network requests on asynchronous worker threads with a thread-safe message queue.
- **Embedded Visualizations**: Matplotlib temperature trend charts with diurnal highs/lows and shaded ranges directly inside the Tkinter window.
- **Meteorological Analytics**: Computes 5-day averages, detects warming/cooling trends, and flags precipitation likelihood.
- **Dual Mode Support**: Seamlessly runs with a live OpenWeatherMap API key or an automatic offline simulation engine for instant demonstrations without setup errors.
- **Full Persistence**: Tracks search history, favourite cities, user preferences (Celsius/Fahrenheit), and meteorological records.

---

## 🎯 Course Outcomes Addressed

| Outcome | Description | Code Implementation |
| :--- | :--- | :--- |
| **i. Modular OOP Constructs** | Design modular and reusable Python applications using classes, objects, and packages. | Modular package layout: `models/`, `services/`, `analysis/`, `storage/`, `gui/`. |
| **ii. Functional Programming** | Implement efficient and expressive code using `map()`, `filter()`, `reduce()`, and `lambda`. | Implemented in `analysis/analyzer.py` (`average_temp`, `filter_rainy_days`, etc.). |
| **iii. Multithreading & Concurrency** | High-performance asynchronous execution for responsive GUIs. | Non-blocking background worker threads in `gui/app.py` via `threading.Thread` and `queue.Queue`. |
| **iv. Data Visualization** | Process and present statistical data effectively using charts. | Embedded `FigureCanvasTkAgg` plotting high/low curves in `analysis/chart_plotter.py`. |
| **v. Full-Fledged Application Integration** | Integrate REST APIs, SQLite databases, JSON files, and GUI. | `WeatherAPIClient`, `StorageManager` (SQLite + JSON), and `WeatherApp` (Tkinter). |

---

## 🏛️ OOP Architecture & Design Patterns

### 1. Abstraction
- Defined `BaseWeatherEntity` (`models/weather_data.py`) as an **Abstract Base Class (ABC)** enforcing `get_summary()` and `to_fahrenheit()` interfaces.

### 2. Encapsulation
- All data models (`WeatherData`, `ForecastDay`) encapsulate state using private attributes (`_city`, `_temperature`, etc.) with validated getters, setters, and properties.

### 3. Inheritance
- `ForecastDay` directly extends `WeatherData`:
  ```python
  class ForecastDay(WeatherData):
      # Inherits city, temperature, humidity, wind, and description
      # Extends with date_str, temp_min, temp_max, pop
  ```

### 4. Polymorphism
- The polymorphic method `get_summary()` is defined on the abstract base and overridden in `ForecastDay` to format forecast day specifics differently from current conditions.

### 5. Exception Handling Hierarchy
- Custom domain exceptions derived from `WeatherAppException`:
  - `InvalidInputError` (422)
  - `CityNotFoundError` (404)
  - `APIKeyError` (401)
  - `NetworkConnectionError` (503)
  - `StorageError` (500)

### 6. Functional Programming Paradigms
- Located in `analysis/analyzer.py`:
  - `reduce()` + `lambda`: Computes mean forecast temperature.
  - `map()` + `lambda`: Extracts daily maximum and minimum temperatures.
  - `filter()` + `lambda`: Filters rainy days and threshold temperature events.
  - `sorted()`: Determines meteorological extremes.
  - `zip()`: Pairs consecutive days to evaluate day-over-day temperature deltas.
  - `enumerate()`: Tracks consecutive trend changes (warming/cooling).
  - List & Dictionary comprehensions: Aggregates daily summaries.

---

## 🗄️ Database Design (Figure 4 Schema)

The SQLite database (`weather_dashboard.db`) is managed through `StorageManager` and implements all 6 entities from Figure 4:

```mermaid
erDiagram
    CITY ||--o{ SEARCH_HISTORY : has
    CITY ||--o{ FAVOURITE_CITY : has
    CITY ||--o{ WEATHER_RECORD : logs
    CITY ||--o{ FORECAST_DAY : forecasts

    CITY {
        int city_id PK
        string city_name UQ
        string country_code
        real latitude
        real longitude
    }
    SEARCH_HISTORY {
        int history_id PK
        int city_id FK
        datetime searched_at
    }
    FAVOURITE_CITY {
        int fav_id PK
        int city_id FK
        datetime added_at
    }
    WEATHER_RECORD {
        int record_id PK
        int city_id FK
        real temperature
        real feels_like
        int humidity
        int pressure
        real wind_speed
        string condition
        datetime fetched_at
    }
    USER_SETTINGS {
        int setting_id PK
        string temp_unit
        int refresh_minutes
    }
    FORECAST_DAY {
        int forecast_id PK
        int city_id FK
        date forecast_date
        real temp_min
        real temp_max
        string condition
    }
```

*Note: In addition to the SQLite database, data is automatically synchronized to `history.json` and `favourites.json` as specified in the project requirements.*

---

## 📂 Project Directory Structure

```text
app micro/
├── main.py                     # Primary Application Entry Point
├── run.bat                     # Windows One-Click Batch Launcher
├── config.json                 # User Configuration (API key, theme, unit)
├── history.json                # JSON Search History
├── favourites.json             # JSON Saved Favourites
├── weather_dashboard.db        # SQLite Database (auto-generated)
├── requirements.txt            # Python Dependencies
├── README.md                   # Complete Documentation
├── models/
│   ├── __init__.py
│   ├── exceptions.py           # Custom Exception Hierarchy
│   └── weather_data.py         # WeatherData & ForecastDay (OOP Models)
├── services/
│   ├── __init__.py
│   ├── validator.py            # InputValidator (Sanitization & Rules)
│   ├── api_client.py           # WeatherAPIClient (REST API & Demo engine)
│   └── data_parser.py          # DataParser (JSON to Domain Models)
├── analysis/
│   ├── __init__.py
│   ├── analyzer.py             # WeatherAnalyzer (Functional Programming)
│   └── chart_plotter.py        # ChartPlotter (Matplotlib Visualizations)
├── storage/
│   ├── __init__.py
│   └── storage_manager.py      # StorageManager (SQLite CRUD & JSON sync)
├── gui/
│   ├── __init__.py
│   ├── app.py                  # WeatherApp Main GUI Controller
│   ├── components.py           # Presentation Panels & Widgets
│   ├── theme.py                # Modern Design System (Dark/Light)
│   └── icon_generator.py       # Antialiased Weather Icon Renderer
└── tests/
    ├── __init__.py
    └── test_weather.py         # Automated Test Suite (15 Test Cases)
```

---

## 🚀 How to Run the Application

### Option A: One-Click Windows Launcher
Double-click `run.bat` in the project root.

### Option B: From Terminal / Command Prompt
```bash
python main.py
```

### Option C: Running the Automated Test Suite
```bash
python -m unittest discover tests
```

---

## 🔑 OpenWeatherMap API Key Configuration

1. You can use the app **immediately without an API key**; it will operate in **Demo / Simulator Mode** with realistic weather and 5-day forecasts for any city worldwide.
2. To use live OpenWeatherMap data:
   - Click the **⚙ Settings** button in the dashboard toolbar.
   - Paste your free OpenWeatherMap API key (from [openweathermap.org](https://openweathermap.org/api)).
   - Click **Save Settings**.
   - The status bar will switch to **● Mode: Live OpenWeatherMap API**.
#   w e a t h e r - d a s h b o a r d  
 #   w e a t h e r - d a s h b o a r d  
 #   w e a t h e r - d a s h b o a r d  
 