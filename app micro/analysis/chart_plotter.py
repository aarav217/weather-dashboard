"""
analysis/chart_plotter.py
ChartPlotter class for data visualization using Matplotlib.
Matches Figure 3 Class Diagram:
- figure: Figure
- plot_temperature(list): void
Integrates seamlessly with Tkinter via FigureCanvasTkAgg.
"""

from typing import List, Optional
import matplotlib
matplotlib.use("TkAgg")  # Ensure TkAgg backend is used
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

from models.weather_data import ForecastDay


class ChartPlotter:
    """
    Visualizes temperature trends across the 5-day forecast period.
    Matches Figure 3 Class Diagram specifications.
    """

    def __init__(self, figsize=(6.6, 2.5), dpi=100):
        # Attribute matching Figure 3: - figure: Figure
        self._figure: Figure = Figure(figsize=figsize, dpi=dpi)
        self._ax = self._figure.add_subplot(111)
        self._figure.patch.set_facecolor("#1e293b")
        self._ax.set_facecolor("#0f172a")

    @property
    def figure(self) -> Figure:
        return self._figure

    def plot_temperature(
        self,
        forecast_list: List[ForecastDay],
        unit: str = "°C",
        is_dark: bool = True,
    ) -> None:
        """
        Plots the 5-day temperature trend with high/low curves and filled range.
        Matches Figure 3: + plot_temperature(list): void
        """
        self._ax.clear()

        if not forecast_list:
            self._ax.text(
                0.5,
                0.5,
                "No forecast data available",
                ha="center",
                va="center",
                color="#94a3b8" if is_dark else "#64748b",
                fontsize=11,
            )
            self._figure.tight_layout()
            return

        # Theme color palettes
        if is_dark:
            bg_fig = "#1e293b"      # Slate 800
            bg_ax = "#0f172a"       # Slate 900
            text_color = "#f1f5f9"  # Slate 100
            subtext_color = "#94a3b8"
            grid_color = "#334155"  # Slate 700
            high_color = "#f97316"  # Orange 500
            low_color = "#38bdf8"   # Sky 400
            fill_color = "#f97316"
        else:
            bg_fig = "#ffffff"
            bg_ax = "#f8fafc"
            text_color = "#0f172a"
            subtext_color = "#64748b"
            grid_color = "#e2e8f0"
            high_color = "#ea580c"
            low_color = "#0284c7"
            fill_color = "#fb923c"

        self._figure.patch.set_facecolor(bg_fig)
        self._ax.set_facecolor(bg_ax)

        # Extract data points
        dates = [f.date for f in forecast_list]
        x_indices = list(range(len(dates)))

        if unit == "°F":
            highs = [f.temp_max_fahrenheit() for f in forecast_list]
            lows = [f.temp_min_fahrenheit() for f in forecast_list]
        else:
            highs = [f.temp_max for f in forecast_list]
            lows = [f.temp_min for f in forecast_list]

        # Plot curves
        self._ax.plot(
            x_indices,
            highs,
            color=high_color,
            marker="o",
            markersize=6,
            linewidth=2.2,
            label=f"Max Temp ({unit})",
            zorder=4,
        )
        self._ax.plot(
            x_indices,
            lows,
            color=low_color,
            marker="s",
            markersize=5,
            linewidth=2.0,
            linestyle="--",
            label=f"Min Temp ({unit})",
            zorder=4,
        )

        # Fill range between highs and lows
        self._ax.fill_between(x_indices, lows, highs, color=fill_color, alpha=0.15, zorder=3)

        # Annotate points with temperature values
        for i, (h, l) in enumerate(zip(highs, lows)):
            self._ax.annotate(
                f"{h:.0f}{unit}",
                (i, h),
                textcoords="offset points",
                xytext=(0, 7),
                ha="center",
                fontsize=8.5,
                fontweight="bold",
                color=high_color,
            )
            self._ax.annotate(
                f"{l:.0f}{unit}",
                (i, l),
                textcoords="offset points",
                xytext=(0, -14),
                ha="center",
                fontsize=8.5,
                fontweight="bold",
                color=low_color,
            )

        # Axis styling
        self._ax.set_xticks(x_indices)
        self._ax.set_xticklabels(dates, fontsize=8.5, color=text_color, fontweight="normal")
        self._ax.tick_params(colors=subtext_color, labelsize=8)

        # Y-limits padding for label headroom
        all_vals = highs + lows
        y_min = min(all_vals) - 3.5
        y_max = max(all_vals) + 4.0
        self._ax.set_ylim(y_min, y_max)

        # Spines styling
        for spine in self._ax.spines.values():
            spine.set_color(grid_color)
            spine.set_linewidth(0.8)

        # Grid lines
        self._ax.grid(True, linestyle=":", alpha=0.6, color=grid_color)
        self._ax.set_axisbelow(True)

        # Legend
        legend = self._ax.legend(
            loc="upper right",
            frameon=True,
            facecolor=bg_ax,
            edgecolor=grid_color,
            fontsize=8,
            labelcolor=text_color,
        )
        legend.get_frame().set_alpha(0.85)

        self._ax.set_title(
            f"5-Day Temperature Trend & Diurnal Range ({unit})",
            fontsize=9.5,
            fontweight="bold",
            color=text_color,
            pad=8,
        )

        self._figure.tight_layout(pad=1.2)
