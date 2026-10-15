"""
main.py
Main entry point for the Weather Forecast Dashboard application.
Alliance University - Alliance School of Advanced Computing
Micro-Project: Weather Forecast Dashboard using REST API and Tkinter GUI
"""

import sys
import os
import tkinter as tk

# Ensure current directory is in Python path for clean imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from gui.app import WeatherApp


def enable_windows_high_dpi():
    """Enables crisp high-DPI font rendering on Windows operating systems."""
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def main():
    enable_windows_high_dpi()

    root = tk.Tk()
    
    # Configure root window icon & styling
    root.title("Weather Forecast Dashboard - REST API & Tkinter")
    
    app = WeatherApp(root)

    # Clean exit handling
    def on_closing():
        if app.storage and app.settings:
            app.storage.save_settings(app.settings)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
