"""
frames/budgets_frame.py
Extra feature: let the user set a monthly spending limit per category.
The dashboard shows an alert banner when a category nears/exceeds its limit.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

import database as db
import constants as c


class BudgetsFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="Budgets", font=ctk.CTkFont(size=26, weight="bold")
                     ).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self, text="Set a monthly limit per category. Dashboard will warn you as you approach it.",
                     text_color=c.COLOR_TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        card = ctk.CTkFrame(self, fg_color=c.COLOR_CARD, corner_radius=14)
        card.pack(fill="x")

        self.entries = {}
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(padx=30, pady=25, fill="x")
        form.grid_columnconfigure(1, weight=1)

        for i, category in enumerate(c.CATEGORIES_EXPENSE):
            ctk.CTkLabel(form, text=category, width=110, anchor="w").grid(row=i, column=0, sticky="w", pady=6)
            entry = ctk.CTkEntry(form, width=180, placeholder_text="Rs. limit")
            entry.grid(row=i, column=1, sticky="w", padx=15, pady=6)
            self.entries[category] = entry

        ctk.CTkButton(card, text="💾 Save Budgets", height=42, width=200, fg_color=c.COLOR_ACCENT,
                      command=self._save).pack(pady=(0, 25))

        # progress overview
        self.progress_frame = ctk.CTkFrame(self, fg_color=c.COLOR_CARD, corner_radius=14)
        self.progress_frame.pack(fill="both", expand=True, pady=(20, 0))
        ctk.CTkLabel(self.progress_frame, text="This Month's Progress",
                     font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=20, pady=(15, 10))
        self.progress_bars_holder = ctk.CTkFrame(self.progress_frame, fg_color="transparent")
        self.progress_bars_holder.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    def _save(self):
        user_id = self.app.user["id"]
        saved_any = False
        for category, entry in self.entries.items():
            val = entry.get().strip()
            if val:
                try:
                    limit = float(val)
                    if limit > 0:
                        db.set_budget(user_id, category, limit)
                        saved_any = True
                except ValueError:
                    messagebox.showerror("Invalid input", f"Limit for {category} must be a number.")
                    return
        if saved_any:
            messagebox.showinfo("Saved", "Budgets updated.")
        self.refresh()

    def refresh(self):
        user_id = self.app.user["id"]
        budgets = db.get_budgets(user_id)
        for category, limit in budgets.items():
            if category in self.entries:
                self.entries[category].delete(0, "end")
                self.entries[category].insert(0, str(int(limit)))

        for widget in self.progress_bars_holder.winfo_children():
            widget.destroy()

        if not budgets:
            ctk.CTkLabel(self.progress_bars_holder, text="No budgets set yet.",
                         text_color=c.COLOR_TEXT_MUTED).pack(anchor="w")
            return

        now = datetime.now()
        breakdown = dict(db.get_category_breakdown(user_id, now.month, now.year))
        for category, limit in budgets.items():
            spent = breakdown.get(category, 0)
            pct = min(spent / limit, 1.0) if limit else 0
            color = c.COLOR_RED if pct >= 1 else (c.COLOR_YELLOW if pct >= c.BUDGET_ALERT_THRESHOLD else c.COLOR_GREEN)

            row = ctk.CTkFrame(self.progress_bars_holder, fg_color="transparent")
            row.pack(fill="x", pady=6)
            ctk.CTkLabel(row, text=f"{category}", width=100, anchor="w").pack(side="left")
            bar = ctk.CTkProgressBar(row, progress_color=color)
            bar.set(pct)
            bar.pack(side="left", fill="x", expand=True, padx=10)
            ctk.CTkLabel(row, text=f"Rs.{spent:,.0f} / {limit:,.0f}", width=140, anchor="e"
                         ).pack(side="left")
