"""
gui/theme.py
Design System and Theme Palette for the Weather Forecast Dashboard.
Supports sleek Dark Mode and modern Light Mode.
"""

class Theme:
    DARK = {
        "name": "dark",
        "bg_main": "#0f172a",          # Slate 900
        "bg_card": "#1e293b",          # Slate 800
        "bg_card_hover": "#334155",    # Slate 700
        "bg_input": "#1e293b",
        "border_color": "#334155",
        "border_focus": "#38bdf8",
        
        "text_primary": "#f8fafc",     # Slate 50
        "text_secondary": "#94a3b8",   # Slate 400
        "text_muted": "#64748b",       # Slate 500
        
        "accent_primary": "#0284c7",   # Sky 600
        "accent_hover": "#0369a1",     # Sky 700
        "accent_light": "#38bdf8",     # Sky 400
        
        "accent_warm": "#f97316",      # Orange 500
        "accent_success": "#10b981",   # Emerald 500
        "accent_danger": "#ef4444",    # Red 500
        "accent_gold": "#eab308",      # Yellow 500
        
        "chart_bg": "#1e293b",
        "chart_plot_bg": "#0f172a",
        "chart_grid": "#334155",
    }

    LIGHT = {
        "name": "light",
        "bg_main": "#f1f5f9",          # Slate 100
        "bg_card": "#ffffff",          # White
        "bg_card_hover": "#f8fafc",    # Slate 50
        "bg_input": "#ffffff",
        "border_color": "#cbd5e1",     # Slate 300
        "border_focus": "#0284c7",
        
        "text_primary": "#0f172a",     # Slate 900
        "text_secondary": "#475569",   # Slate 600
        "text_muted": "#94a3b8",       # Slate 400
        
        "accent_primary": "#0284c7",   # Sky 600
        "accent_hover": "#0369a1",     # Sky 700
        "accent_light": "#0ea5e9",     # Sky 500
        
        "accent_warm": "#ea580c",      # Orange 600
        "accent_success": "#059669",   # Emerald 600
        "accent_danger": "#dc2626",    # Red 600
        "accent_gold": "#ca8a04",      # Yellow 600
        
        "chart_bg": "#ffffff",
        "chart_plot_bg": "#f8fafc",
        "chart_grid": "#e2e8f0",
    }

    FONTS = {
        "title": ("Segoe UI", 18, "bold"),
        "hero_temp": ("Segoe UI", 38, "bold"),
        "subtitle": ("Segoe UI", 12, "bold"),
        "body": ("Segoe UI", 10),
        "body_bold": ("Segoe UI", 10, "bold"),
        "caption": ("Segoe UI", 9),
        "small": ("Segoe UI", 8),
        "badge": ("Segoe UI", 9, "bold"),
    }
