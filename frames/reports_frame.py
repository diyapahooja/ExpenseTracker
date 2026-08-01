"""
frames/reports_frame.py
Monthly report with income / expense / savings summary, a category-wise
pie chart, and a month-by-month income vs expense bar chart, all
rendered with matplotlib embedded inside the CTk window.
"""

import customtkinter as ctk
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # backend set explicitly; FigureCanvasTkAgg overrides drawing target
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import database as db
import constants as c


class ReportsFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x")
        ctk.CTkLabel(header_row, text="Reports & Charts", font=ctk.CTkFont(size=26, weight="bold")
                     ).pack(side="left")

        now = datetime.now()
        self.month_var = ctk.StringVar(value=c.MONTH_NAMES[now.month - 1])
        self.year_var = ctk.StringVar(value=str(now.year))

        ctk.CTkOptionMenu(header_row, values=c.MONTH_NAMES, variable=self.month_var,
                          width=140, command=lambda _: self.refresh()).pack(side="right", padx=(0, 10))
        years = [str(y) for y in range(now.year - 4, now.year + 1)]
        ctk.CTkOptionMenu(header_row, values=years, variable=self.year_var,
                          width=90, command=lambda _: self.refresh()).pack(side="right", padx=(0, 10))

        # summary cards
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.pack(fill="x", pady=15)
        self.summary_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self.income_lbl = self._summary_card(self.summary_frame, 0, "Income", c.COLOR_GREEN)
        self.expense_lbl = self._summary_card(self.summary_frame, 1, "Expense", c.COLOR_RED)
        self.savings_lbl = self._summary_card(self.summary_frame, 2, "Savings", c.COLOR_BLUE)

        # charts area
        charts_row = ctk.CTkFrame(self, fg_color="transparent")
        charts_row.pack(fill="both", expand=True)
        charts_row.grid_columnconfigure((0, 1), weight=1)
        charts_row.grid_rowconfigure(0, weight=1)

        self.pie_card = ctk.CTkFrame(charts_row, fg_color=c.COLOR_CARD, corner_radius=14)
        self.pie_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ctk.CTkLabel(self.pie_card, text="Expense by Category", font=ctk.CTkFont(size=15, weight="bold")
                     ).pack(anchor="w", padx=15, pady=(15, 0))
        self.pie_canvas_holder = ctk.CTkFrame(self.pie_card, fg_color="transparent")
        self.pie_canvas_holder.pack(fill="both", expand=True, padx=10, pady=10)

        self.bar_card = ctk.CTkFrame(charts_row, fg_color=c.COLOR_CARD, corner_radius=14)
        self.bar_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ctk.CTkLabel(self.bar_card, text=f"Monthly Trend ({self.year_var.get()})",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(15, 0))
        self.bar_canvas_holder = ctk.CTkFrame(self.bar_card, fg_color="transparent")
        self.bar_canvas_holder.pack(fill="both", expand=True, padx=10, pady=10)

        self._pie_canvas = None
        self._bar_canvas = None

    def _summary_card(self, parent, col, title, color):
        card = ctk.CTkFrame(parent, fg_color=c.COLOR_CARD, corner_radius=14, height=85)
        card.grid(row=0, column=col, sticky="ew", padx=6)
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, text_color=c.COLOR_TEXT_MUTED).pack(anchor="w", padx=18, pady=(14, 0))
        lbl = ctk.CTkLabel(card, text="Rs. 0", font=ctk.CTkFont(size=20, weight="bold"), text_color=color)
        lbl.pack(anchor="w", padx=18)
        return lbl

    def refresh(self):
        month = c.MONTH_NAMES.index(self.month_var.get()) + 1
        year = int(self.year_var.get())
        user_id = self.app.user["id"]

        income, expense, savings = db.get_summary(user_id, month, year)
        self.income_lbl.configure(text=f"Rs. {income:,.0f}")
        self.expense_lbl.configure(text=f"Rs. {expense:,.0f}")
        self.savings_lbl.configure(text=f"Rs. {savings:,.0f}")

        self._draw_pie_chart(user_id, month, year)
        self._draw_bar_chart(user_id, year)

    def _themed_figure(self, figsize):
        fig = Figure(figsize=figsize, dpi=100)
        fig.patch.set_facecolor(c.COLOR_CARD)
        return fig

    def _draw_pie_chart(self, user_id, month, year):
        if self._pie_canvas:
            self._pie_canvas.get_tk_widget().destroy()

        data = db.get_category_breakdown(user_id, month, year, ttype="expense")
        fig = self._themed_figure((4.2, 3.6))
        ax = fig.add_subplot(111)
        ax.set_facecolor(c.COLOR_CARD)

        if data:
            labels = [d[0] for d in data]
            values = [d[1] for d in data]
            ax.pie(values, labels=labels, autopct="%1.0f%%", colors=c.CHART_COLORS,
                   textprops={"color": "white", "fontsize": 8}, startangle=90)
        else:
            ax.text(0.5, 0.5, "No expenses this month", ha="center", va="center",
                    color=c.COLOR_TEXT_MUTED, transform=ax.transAxes)
            ax.axis("off")

        fig.tight_layout()
        self._pie_canvas = FigureCanvasTkAgg(fig, master=self.pie_canvas_holder)
        self._pie_canvas.draw()
        self._pie_canvas.get_tk_widget().pack(fill="both", expand=True)

    def _draw_bar_chart(self, user_id, year):
        if self._bar_canvas:
            self._bar_canvas.get_tk_widget().destroy()

        trend = db.get_monthly_trend(user_id, year)
        months = sorted(trend.keys())
        incomes = [trend[m]["income"] for m in months]
        expenses = [trend[m]["expense"] for m in months]
        labels = [c.MONTH_NAMES[int(m) - 1][:3] for m in months]

        fig = self._themed_figure((5.2, 3.6))
        ax = fig.add_subplot(111)
        ax.set_facecolor(c.COLOR_CARD)

        x = range(len(labels))
        width = 0.35
        ax.bar([i - width / 2 for i in x], incomes, width, label="Income", color=c.COLOR_GREEN)
        ax.bar([i + width / 2 for i in x], expenses, width, label="Expense", color=c.COLOR_RED)

        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, color="white", fontsize=8, rotation=45)
        ax.tick_params(colors="white")
        for spine in ax.spines.values():
            spine.set_color(c.COLOR_TEXT_MUTED)
        ax.legend(facecolor=c.COLOR_CARD, labelcolor="white", fontsize=8)

        fig.tight_layout()
        self._bar_canvas = FigureCanvasTkAgg(fig, master=self.bar_canvas_holder)
        self._bar_canvas.draw()
        self._bar_canvas.get_tk_widget().pack(fill="both", expand=True)
