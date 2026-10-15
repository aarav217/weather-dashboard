"""
run_tests_gui.py
Graphical Test Runner and Rubric Verification Dashboard for Weather App.
Alliance University - Alliance School of Advanced Computing
Visualizes all 15 unit tests across OOP, Functional Programming, Service, and Storage layers.
"""

import sys
import os
import time
import queue
import threading
import unittest
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gui.theme import Theme
import tests.test_weather as test_module


def enable_windows_high_dpi():
    """Enables crisp high-DPI font rendering on Windows operating systems."""
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


RUBRIC_MAP = {
    "test_abstraction": {
        "category": "OOP Principles",
        "title": "Abstraction & Abstract Base Class",
        "desc": "Verifies BaseWeatherEntity enforces @abstractmethod get_summary() and to_fahrenheit(), raising TypeError on instantiation.",
        "outcome": "CO1: Object-Oriented Abstraction & Polymorphism",
    },
    "test_encapsulation": {
        "category": "OOP Principles",
        "title": "Encapsulation & Property Accessors",
        "desc": "Verifies private attributes (_city, _temperature, etc.), property getters, and unit conversion methods.",
        "outcome": "CO1: Encapsulated Data Models",
    },
    "test_inheritance": {
        "category": "OOP Principles",
        "title": "Inheritance (ForecastDay extends WeatherData)",
        "desc": "Verifies class hierarchy, issubclass checks, and proper super().__init__() attribute inheritance.",
        "outcome": "CO1: Inheritance Hierarchy",
    },
    "test_polymorphism": {
        "category": "OOP Principles",
        "title": "Polymorphism (Dynamic Method Dispatch)",
        "desc": "Verifies polymorphic override of get_summary() across heterogeneous BaseWeatherEntity collections.",
        "outcome": "CO1: Polymorphism & Interface Uniformity",
    },
    "test_exception_handling": {
        "category": "OOP Principles",
        "title": "Custom Exception Hierarchy",
        "desc": "Verifies custom WeatherAppException taxonomy (InvalidInputError, CityNotFoundError, APIKeyError, NetworkConnectionError).",
        "outcome": "CO1 & CO4: Robust Error Handling",
    },
    "test_average_temp_reduce_map_lambda": {
        "category": "Functional Programming",
        "title": "Higher-Order reduce(), map(), and lambda",
        "desc": "Computes average forecast temperature using functional constructs without imperative accumulator loops.",
        "outcome": "CO2: Functional Transformations",
    },
    "test_filter_rainy_days": {
        "category": "Functional Programming",
        "title": "Higher-Order filter() and lambda",
        "desc": "Extracts precipitation-prone forecast days using filter() and predicate lambda functions.",
        "outcome": "CO2: Functional Predicate Filtering",
    },
    "test_max_min_temp_sorted_map": {
        "category": "Functional Programming",
        "title": "Functional sorted() and map()",
        "desc": "Identifies extreme temperature bounds across forecast periods using functional sorting pipelines.",
        "outcome": "CO2: Functional Ordering & Projections",
    },
    "test_trend_zip_enumerate": {
        "category": "Functional Programming",
        "title": "Functional zip() and enumerate()",
        "desc": "Analyzes day-to-day temperature differences and trends using pairwise zip() and enumerate().",
        "outcome": "CO2: Itertool & Stream Transformations",
    },
    "test_input_validator": {
        "category": "Services & Parser",
        "title": "InputValidator Sanitization & Regex",
        "desc": "Validates city name strings, length constraints, illegal symbols, and coordinate ranges.",
        "outcome": "CO3: Service Layer & Input Validation",
    },
    "test_api_client_simulation": {
        "category": "Services & Parser",
        "title": "REST API Client & Resilience",
        "desc": "Validates API endpoint URL generation, error code mapping (401, 404, 500), and request simulation.",
        "outcome": "CO3: REST API Integration",
    },
    "test_data_parser": {
        "category": "Services & Parser",
        "title": "JSON DataParser & Object Marshalling",
        "desc": "Transforms raw OpenWeatherMap REST payload into concrete WeatherData and ForecastDay instances.",
        "outcome": "CO3: Data Serialization & Parsing",
    },
    "test_sqlite_tables_created": {
        "category": "Storage Layer",
        "title": "SQLite Schema & Table Initialization",
        "desc": "Verifies DDL table generation for search_history and favorites according to database schema.",
        "outcome": "CO4: Relational Database Storage",
    },
    "test_history_persistence": {
        "category": "Storage Layer",
        "title": "Search History CRUD & Persistence",
        "desc": "Verifies inserting, querying, and updating recent city search queries with timestamps.",
        "outcome": "CO4: Data Persistence & Retrieval",
    },
    "test_favourites_persistence": {
        "category": "Storage Layer",
        "title": "Favorites Management (Add / Remove)",
        "desc": "Verifies bookmarking cities, querying favorites, duplicate avoidance, and persistence across sessions.",
        "outcome": "CO4: Relational CRUD Operations",
    },
}


class CustomTestResult(unittest.TestResult):
    """Custom TestResult that streams real-time updates through a thread-safe Queue."""

    def __init__(self, update_queue: queue.Queue):
        super().__init__()
        self.update_queue = update_queue
        self.start_times = {}

    def startTest(self, test):
        super().startTest(test)
        test_id = test._testMethodName
        self.start_times[test_id] = time.perf_counter()
        self.update_queue.put(("START", test_id, None))

    def addSuccess(self, test):
        super().addSuccess(test)
        test_id = test._testMethodName
        duration = time.perf_counter() - self.start_times.get(test_id, time.perf_counter())
        self.update_queue.put(("SUCCESS", test_id, {"duration": duration}))

    def addFailure(self, test, err):
        super().addFailure(test, err)
        test_id = test._testMethodName
        duration = time.perf_counter() - self.start_times.get(test_id, time.perf_counter())
        msg = self._exc_info_to_string(err, test)
        self.update_queue.put(("FAILURE", test_id, {"duration": duration, "error": msg}))

    def addError(self, test, err):
        super().addError(test, err)
        test_id = test._testMethodName
        duration = time.perf_counter() - self.start_times.get(test_id, time.perf_counter())
        msg = self._exc_info_to_string(err, test)
        self.update_queue.put(("ERROR", test_id, {"duration": duration, "error": msg}))


class TestRunnerGUI:
    """Modern Tkinter Graphical Test Suite Runner."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Weather App - Automated Test Suite & Rubric Verifier")
        self.root.geometry("1100x720")
        self.root.minsize(950, 600)

        self.theme = Theme.DARK
        self.root.configure(bg=self.theme["bg_main"])

        self.update_queue = queue.Queue()
        self.is_running = False
        self.test_data = {}
        self.selected_category = "All Tests"

        self._configure_styles()
        self._build_ui()
        self._load_test_definitions()

        # Start poll queue
        self.root.after(50, self._process_queue)

        # Automatically run all tests 300ms after window loads
        self.root.after(300, self.run_all_tests)

    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Treeview styling
        style.configure(
            "Treeview",
            background=self.theme["bg_card"],
            foreground=self.theme["text_primary"],
            fieldbackground=self.theme["bg_card"],
            rowheight=34,
            font=("Segoe UI", 10),
            borderwidth=0,
        )
        style.map(
            "Treeview",
            background=[("selected", self.theme["accent_primary"])],
            foreground=[("selected", "#ffffff")],
        )
        style.configure(
            "Treeview.Heading",
            background=self.theme["bg_card_hover"],
            foreground=self.theme["text_primary"],
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padding=(8, 6),
        )
        style.map(
            "Treeview.Heading",
            background=[("active", self.theme["border_focus"])],
        )

        # Progress bar
        style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor=self.theme["bg_card"],
            background=self.theme["accent_success"],
            thickness=8,
            relief="flat",
        )

    def _build_ui(self):
        # 1. Top Header
        header_frame = tk.Frame(self.root, bg=self.theme["bg_card"], pady=12, padx=20)
        header_frame.pack(fill="x", side="top")

        title_lbl = tk.Label(
            header_frame,
            text="🧪 Weather App — Rubric & Unit Test Dashboard",
            font=("Segoe UI", 15, "bold"),
            bg=self.theme["bg_card"],
            fg=self.theme["text_primary"],
        )
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(
            header_frame,
            text="Alliance School of Advanced Computing • Micro-Project Automated Verification Suite (15 Tests)",
            font=("Segoe UI", 9),
            bg=self.theme["bg_card"],
            fg=self.theme["text_secondary"],
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # 2. Metric KPI Cards Row
        kpi_frame = tk.Frame(self.root, bg=self.theme["bg_main"], pady=10, padx=20)
        kpi_frame.pack(fill="x")

        self.kpi_total = self._create_kpi_card(kpi_frame, "TOTAL TESTS", "15", self.theme["accent_light"])
        self.kpi_passed = self._create_kpi_card(kpi_frame, "PASSED", "0", self.theme["accent_success"])
        self.kpi_failed = self._create_kpi_card(kpi_frame, "FAILED", "0", self.theme["accent_danger"])
        self.kpi_time = self._create_kpi_card(kpi_frame, "TOTAL DURATION", "0.00s", self.theme["accent_warm"])
        self.kpi_rubric = self._create_kpi_card(kpi_frame, "RUBRIC COVERAGE", "100%", self.theme["accent_gold"])

        # 3. Control & Filter Toolbar
        ctrl_frame = tk.Frame(self.root, bg=self.theme["bg_main"], padx=20, pady=5)
        ctrl_frame.pack(fill="x")

        self.btn_run_all = tk.Button(
            ctrl_frame,
            text="▶ Run All Tests",
            font=("Segoe UI", 10, "bold"),
            bg=self.theme["accent_primary"],
            fg="#ffffff",
            activebackground=self.theme["accent_hover"],
            activeforeground="#ffffff",
            relief="flat",
            padx=16,
            pady=6,
            cursor="hand2",
            command=self.run_all_tests,
        )
        self.btn_run_all.pack(side="left", padx=(0, 10))

        self.btn_run_selected = tk.Button(
            ctrl_frame,
            text="▶ Run Selected",
            font=("Segoe UI", 9),
            bg=self.theme["bg_card"],
            fg=self.theme["text_primary"],
            activebackground=self.theme["bg_card_hover"],
            activeforeground=self.theme["text_primary"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.run_selected_test,
        )
        self.btn_run_selected.pack(side="left", padx=(0, 15))

        # Category Filter Tabs
        filter_lbl = tk.Label(
            ctrl_frame,
            text="Filter Category:",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_main"],
            fg=self.theme["text_secondary"],
        )
        filter_lbl.pack(side="left", padx=(10, 6))

        categories = [
            "All Tests",
            "OOP Principles",
            "Functional Programming",
            "Services & Parser",
            "Storage Layer",
        ]
        self.category_var = tk.StringVar(value="All Tests")
        for cat in categories:
            btn = tk.Radiobutton(
                ctrl_frame,
                text=cat,
                variable=self.category_var,
                value=cat,
                command=self._apply_filter,
                bg=self.theme["bg_main"],
                fg=self.theme["text_primary"],
                selectcolor=self.theme["bg_card"],
                activebackground=self.theme["bg_main"],
                activeforeground=self.theme["accent_light"],
                font=("Segoe UI", 9),
            )
            btn.pack(side="left", padx=4)

        # Progress bar
        self.prog_bar = ttk.Progressbar(
            self.root,
            style="Green.Horizontal.TProgressbar",
            mode="determinate",
            maximum=15,
        )
        self.prog_bar.pack(fill="x", padx=20, pady=(6, 8))

        # 4. Main Body: Split View (Treeview on left, Details on right)
        body_frame = tk.Frame(self.root, bg=self.theme["bg_main"], padx=20, pady=4)
        body_frame.pack(fill="both", expand=True)

        # Left: Treeview
        tree_container = tk.Frame(body_frame, bg=self.theme["bg_card"], bd=1, relief="solid")
        tree_container.pack(side="left", fill="both", expand=True, padx=(0, 10))

        columns = ("status", "name", "category", "duration")
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("status", text="Status", anchor="center")
        self.tree.heading("name", text="Test Method & Concept", anchor="w")
        self.tree.heading("category", text="Rubric Module", anchor="w")
        self.tree.heading("duration", text="Duration", anchor="e")

        self.tree.column("status", width=70, anchor="center")
        self.tree.column("name", width=270, anchor="w")
        self.tree.column("category", width=160, anchor="w")
        self.tree.column("duration", width=80, anchor="e")

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Right: Details Card
        self.detail_frame = tk.Frame(body_frame, bg=self.theme["bg_card"], width=380, padx=16, pady=16)
        self.detail_frame.pack(side="right", fill="both", expand=False)
        self.detail_frame.pack_propagate(False)

        self._build_detail_card()

        # 5. Bottom Status Bar
        status_frame = tk.Frame(self.root, bg=self.theme["bg_card"], padx=20, pady=6)
        status_frame.pack(fill="x", side="bottom")

        self.lbl_status = tk.Label(
            status_frame,
            text="Ready to execute automated test suite.",
            font=("Segoe UI", 9),
            bg=self.theme["bg_card"],
            fg=self.theme["text_secondary"],
        )
        self.lbl_status.pack(side="left")

        self.lbl_timestamp = tk.Label(
            status_frame,
            text="",
            font=("Segoe UI", 9),
            bg=self.theme["bg_card"],
            fg=self.theme["text_muted"],
        )
        self.lbl_timestamp.pack(side="right")

    def _create_kpi_card(self, parent, label: str, val: str, color: str):
        card = tk.Frame(parent, bg=self.theme["bg_card"], padx=14, pady=8, bd=1, relief="solid")
        card.pack(side="left", expand=True, fill="x", padx=4)

        lbl = tk.Label(
            card,
            text=label,
            font=("Segoe UI", 8, "bold"),
            bg=self.theme["bg_card"],
            fg=self.theme["text_muted"],
        )
        lbl.pack(anchor="w")

        val_lbl = tk.Label(
            card,
            text=val,
            font=("Segoe UI", 16, "bold"),
            bg=self.theme["bg_card"],
            fg=color,
        )
        val_lbl.pack(anchor="w")
        return val_lbl

    def _build_detail_card(self):
        title = tk.Label(
            self.detail_frame,
            text="Rubric & Test Inspection",
            font=("Segoe UI", 12, "bold"),
            bg=self.theme["bg_card"],
            fg=self.theme["text_primary"],
        )
        title.pack(anchor="w", pady=(0, 10))

        # Test name badge
        self.det_test_name = tk.Label(
            self.detail_frame,
            text="Select a test to view details",
            font=("Segoe UI", 11, "bold"),
            bg=self.theme["bg_card"],
            fg=self.theme["accent_light"],
            wraplength=340,
            justify="left",
        )
        self.det_test_name.pack(anchor="w")

        # Status badge
        self.det_status = tk.Label(
            self.detail_frame,
            text="STATUS: PENDING",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_card_hover"],
            fg=self.theme["text_secondary"],
            padx=8,
            pady=3,
        )
        self.det_status.pack(anchor="w", pady=(8, 12))

        # Outcome header
        self.det_outcome = tk.Label(
            self.detail_frame,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_card"],
            fg=self.theme["accent_warm"],
            wraplength=340,
            justify="left",
        )
        self.det_outcome.pack(anchor="w", pady=(0, 6))

        # Description
        self.det_desc = tk.Label(
            self.detail_frame,
            text="",
            font=("Segoe UI", 9),
            bg=self.theme["bg_card"],
            fg=self.theme["text_secondary"],
            wraplength=340,
            justify="left",
        )
        self.det_desc.pack(anchor="w", pady=(0, 12))

        # Output / Log box
        log_title = tk.Label(
            self.detail_frame,
            text="Verification Output / Assertion Log:",
            font=("Segoe UI", 9, "bold"),
            bg=self.theme["bg_card"],
            fg=self.theme["text_muted"],
        )
        log_title.pack(anchor="w", pady=(0, 4))

        self.det_log = tk.Text(
            self.detail_frame,
            bg=self.theme["bg_main"],
            fg=self.theme["text_primary"],
            font=("Consolas", 9),
            relief="flat",
            wrap="word",
            height=12,
        )
        self.det_log.pack(fill="both", expand=True)

    def _load_test_definitions(self):
        """Populates the initial test items into the treeview."""
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)

        for test_case in suite:
            for test in test_case:
                m_name = test._testMethodName
                info = RUBRIC_MAP.get(m_name, {
                    "category": "General",
                    "title": m_name,
                    "desc": test.shortDescription() or "Automated test method",
                    "outcome": "Verification Criteria",
                })
                self.test_data[m_name] = {
                    "name": m_name,
                    "category": info["category"],
                    "title": info["title"],
                    "desc": info["desc"],
                    "outcome": info["outcome"],
                    "status": "PENDING",
                    "duration": 0.0,
                    "error": None,
                }

        self._render_tree()

    def _render_tree(self):
        self.tree.delete(*self.tree.get_children())
        selected_cat = self.category_var.get()

        for name, data in self.test_data.items():
            if selected_cat != "All Tests" and data["category"] != selected_cat:
                continue

            status_icon = "⏳"
            if data["status"] == "PASSED":
                status_icon = "✔"
            elif data["status"] in ("FAILED", "ERROR"):
                status_icon = "✖"

            dur_str = f"{data['duration'] * 1000:.1f}ms" if data["duration"] > 0 else "-"
            self.tree.insert(
                "",
                "end",
                iid=name,
                values=(status_icon, name, data["category"], dur_str),
            )

    def _apply_filter(self):
        self._render_tree()

    def run_all_tests(self):
        if self.is_running:
            return

        self.is_running = True
        self.btn_run_all.configure(state="disabled", text="⏳ Running Tests...")
        self.btn_run_selected.configure(state="disabled")
        self.prog_bar["value"] = 0
        self.lbl_status.config(text="Executing automated test suite in background thread...")

        # Reset statuses
        for k in self.test_data:
            self.test_data[k]["status"] = "PENDING"
            self.test_data[k]["duration"] = 0.0
            self.test_data[k]["error"] = None
        self._render_tree()

        threading.Thread(target=self._run_tests_worker, daemon=True).start()

    def run_selected_test(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Selection Required", "Please select a test from the list to run.")
            return

        test_name = selected[0]
        if self.is_running:
            return

        self.is_running = True
        self.btn_run_all.configure(state="disabled")
        self.btn_run_selected.configure(state="disabled", text="⏳ Running...")
        self.lbl_status.config(text=f"Executing single test: {test_name}...")

        self.test_data[test_name]["status"] = "PENDING"
        self._render_tree()

        threading.Thread(target=self._run_single_test_worker, args=(test_name,), daemon=True).start()

    def _run_tests_worker(self):
        start_time = time.perf_counter()
        suite = unittest.TestLoader().loadTestsFromModule(test_module)
        result = CustomTestResult(self.update_queue)
        suite.run(result)
        total_time = time.perf_counter() - start_time
        self.update_queue.put(("ALL_DONE", None, {"total_time": total_time, "result": result}))

    def _run_single_test_worker(self, test_name: str):
        start_time = time.perf_counter()
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        full_suite = loader.loadTestsFromModule(test_module)

        for case in full_suite:
            for test in case:
                if test._testMethodName == test_name:
                    suite.addTest(test)
                    break

        result = CustomTestResult(self.update_queue)
        suite.run(result)
        total_time = time.perf_counter() - start_time
        self.update_queue.put(("SINGLE_DONE", test_name, {"total_time": total_time, "result": result}))

    def _process_queue(self):
        try:
            while True:
                msg_type, test_id, payload = self.update_queue.get_nowait()

                if msg_type == "START":
                    if test_id in self.test_data:
                        self.test_data[test_id]["status"] = "RUNNING"
                        self.lbl_status.config(text=f"Testing: {test_id}...")

                elif msg_type == "SUCCESS":
                    if test_id in self.test_data:
                        self.test_data[test_id]["status"] = "PASSED"
                        self.test_data[test_id]["duration"] = payload["duration"]
                    self.prog_bar.step(1)

                elif msg_type in ("FAILURE", "ERROR"):
                    if test_id in self.test_data:
                        self.test_data[test_id]["status"] = "FAILED"
                        self.test_data[test_id]["duration"] = payload["duration"]
                        self.test_data[test_id]["error"] = payload["error"]
                    self.prog_bar.step(1)

                elif msg_type == "ALL_DONE":
                    self.is_running = False
                    self.btn_run_all.configure(state="normal", text="▶ Run All Tests")
                    self.btn_run_selected.configure(state="normal", text="▶ Run Selected")
                    self.prog_bar["value"] = 15

                    total_time = payload["total_time"]
                    res = payload["result"]
                    passed = res.testsRun - len(res.failures) - len(res.errors)

                    self.kpi_total.config(text=str(res.testsRun))
                    self.kpi_passed.config(text=str(passed))
                    self.kpi_failed.config(text=str(len(res.failures) + len(res.errors)))
                    self.kpi_time.config(text=f"{total_time:.2f}s")

                    self.lbl_status.config(
                        text=f"✔ Test execution complete: {passed}/{res.testsRun} passed in {total_time:.2f}s."
                    )
                    self.lbl_timestamp.config(text=f"Last run: {datetime.now().strftime('%H:%M:%S')}")
                    self._render_tree()

                    # Auto select test_abstraction or first item
                    target = "test_abstraction" if "test_abstraction" in self.test_data else list(self.test_data.keys())[0]
                    self.tree.selection_set(target)
                    self.tree.focus(target)
                    self._show_test_detail(target)

                elif msg_type == "SINGLE_DONE":
                    self.is_running = False
                    self.btn_run_all.configure(state="normal", text="▶ Run All Tests")
                    self.btn_run_selected.configure(state="normal", text="▶ Run Selected")
                    self.lbl_status.config(text=f"Finished running {test_id}.")
                    self._render_tree()
                    self.tree.selection_set(test_id)
                    self._show_test_detail(test_id)

        except queue.Empty:
            pass
        finally:
            self.root.after(50, self._process_queue)

    def _on_tree_select(self, event):
        selected = self.tree.selection()
        if selected:
            self._show_test_detail(selected[0])

    def _show_test_detail(self, test_name: str):
        data = self.test_data.get(test_name)
        if not data:
            return

        self.det_test_name.config(text=f"{data['title']} ({test_name})")
        self.det_outcome.config(text=f"🎯 {data['outcome']}")
        self.det_desc.config(text=data['desc'])

        if data["status"] == "PASSED":
            dur = f"{data['duration'] * 1000:.1f}ms"
            self.det_status.config(
                text=f"✔ PASSED ({dur})",
                bg=self.theme["accent_success"],
                fg="#ffffff",
            )
            self.det_log.delete("1.0", "end")
            self.det_log.insert(
                "1.0",
                f"=== TEST RESULT: PASSED ===\n"
                f"Test Method: {test_name}\n"
                f"Execution Duration: {dur}\n"
                f"Status: Success\n\n"
                f"Course Outcome: {data['outcome']}\n"
                f"Verification: All assertions passed with 0 errors or unexpected exceptions."
            )
        elif data["status"] == "FAILED":
            self.det_status.config(
                text="✖ FAILED",
                bg=self.theme["accent_danger"],
                fg="#ffffff",
            )
            self.det_log.delete("1.0", "end")
            self.det_log.insert(
                "1.0",
                f"=== TEST RESULT: FAILED ===\n"
                f"Test Method: {test_name}\n\n"
                f"Traceback:\n{data.get('error', 'Assertion failed.')}"
            )
        else:
            self.det_status.config(
                text="⏳ PENDING",
                bg=self.theme["bg_card_hover"],
                fg=self.theme["text_secondary"],
            )
            self.det_log.delete("1.0", "end")
            self.det_log.insert("1.0", "Test has not been executed yet.")


def main():
    enable_windows_high_dpi()
    root = tk.Tk()
    app = TestRunnerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
