"""
frames/dashboard_frame.py
Home screen: current-month income / expense / savings cards + a
"recent transactions" table, plus a quick budget-alert banner.
"""

import customtkinter as ctk
from tkinter import ttk
from datetime import datetime

import database as db
import constants as c


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.header = ctk.CTkLabel(self, text="Dashboard", font=ctk.CTkFont(size=26, weight="bold"))
        self.header.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))

        # summary cards
        self.income_card = self._make_card(1, "Income", c.COLOR_GREEN)
        self.expense_card = self._make_card(2, "Expense", c.COLOR_RED)
        self.savings_card = self._make_card(3, "Savings", c.COLOR_BLUE)

        self.alert_label = ctk.CTkLabel(self, text="", text_color=c.COLOR_YELLOW,
                                         font=ctk.CTkFont(size=13, weight="bold"))
        self.alert_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=(90, 5))

        # recent transactions table
        table_frame = ctk.CTkFrame(self, fg_color=c.COLOR_CARD, corner_radius=12)
        table_frame.grid(row=2, column=0, columnspan=3, sticky="nsew", pady=(20, 0))
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(table_frame, text="Recent Transactions", font=ctk.CTkFont(size=16, weight="bold")
                     ).pack(anchor="w", padx=15, pady=(15, 5))

        cols = ("type", "category", "amount", "date", "note")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", height=9)
        headings = {"type": "Type", "category": "Category", "amount": "Amount (Rs.)",
                    "date": "Date", "note": "Note"}
        widths = {"type": 80, "category": 120, "amount": 110, "date": 100, "note": 220}
        for col in cols:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")
        self.tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def _make_card(self, col, title, color):
        card = ctk.CTkFrame(self, fg_color=c.COLOR_CARD, corner_radius=14, height=90)
        card.grid(row=1, column=col - 1, sticky="ew", padx=(0 if col == 1 else 8, 0))
        card.grid_propagate(False)
        ctk.CTkLabel(card, text=title, text_color=c.COLOR_TEXT_MUTED,
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=18, pady=(15, 0))
        value_label = ctk.CTkLabel(card, text="Rs. 0", font=ctk.CTkFont(size=22, weight="bold"),
                                    text_color=color)
        value_label.pack(anchor="w", padx=18)
        card.value_label = value_label
        return card

    def refresh(self):
        now = datetime.now()
        income, expense, savings = db.get_summary(self.app.user["id"], now.month, now.year)
        self.income_card.value_label.configure(text=f"Rs. {income:,.0f}")
        self.expense_card.value_label.configure(text=f"Rs. {expense:,.0f}")
        self.savings_card.value_label.configure(text=f"Rs. {savings:,.0f}")

        # extra feature: warn if any budgeted category is close to / over its limit
        budgets = db.get_budgets(self.app.user["id"])
        warnings = []
        if budgets:
            breakdown = dict(db.get_category_breakdown(self.app.user["id"], now.month, now.year))
            for cat, limit in budgets.items():
                spent = breakdown.get(cat, 0)
                if limit > 0 and spent >= limit:
                    warnings.append(f"⚠ {cat} over budget (Rs.{spent:,.0f}/{limit:,.0f})")
                elif limit > 0 and spent >= c.BUDGET_ALERT_THRESHOLD * limit:
                    warnings.append(f"⚠ {cat} nearing budget (Rs.{spent:,.0f}/{limit:,.0f})")
        self.alert_label.configure(text="   ".join(warnings) if warnings else "")

        for row in self.tree.get_children():
            self.tree.delete(row)
        for txn_id, ttype, category, amount, date, note in db.get_recent_transactions(self.app.user["id"]):
            sign = "+" if ttype == "income" else "-"
            self.tree.insert("", "end", values=(ttype.title(), category, f"{sign}{amount:,.0f}",
                                                  date, note or ""))
