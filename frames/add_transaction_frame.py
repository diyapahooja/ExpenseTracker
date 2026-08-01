"""
frames/add_transaction_frame.py
Form to add a new income or expense transaction.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

import database as db
import constants as c


class AddTransactionFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="Add Transaction", font=ctk.CTkFont(size=26, weight="bold")
                     ).pack(anchor="w", pady=(0, 20))

        card = ctk.CTkFrame(self, fg_color=c.COLOR_CARD, corner_radius=14)
        card.pack(fill="x", pady=5)

        # Type toggle: income / expense
        self.type_var = ctk.StringVar(value="expense")
        toggle_frame = ctk.CTkFrame(card, fg_color="transparent")
        toggle_frame.pack(pady=(25, 10))
        ctk.CTkRadioButton(toggle_frame, text="Expense", variable=self.type_var, value="expense",
                            command=self._update_categories, fg_color=c.COLOR_RED
                            ).pack(side="left", padx=15)
        ctk.CTkRadioButton(toggle_frame, text="Income", variable=self.type_var, value="income",
                            command=self._update_categories, fg_color=c.COLOR_GREEN
                            ).pack(side="left", padx=15)

        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(pady=10, padx=40, fill="x")
        form.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form, text="Category").grid(row=0, column=0, sticky="w", pady=10)
        self.category_menu = ctk.CTkOptionMenu(form, values=c.CATEGORIES_EXPENSE, width=250)
        self.category_menu.grid(row=0, column=1, sticky="w", pady=10, padx=(15, 0))

        ctk.CTkLabel(form, text="Amount (Rs.)").grid(row=1, column=0, sticky="w", pady=10)
        self.amount_entry = ctk.CTkEntry(form, width=250, placeholder_text="e.g. 500")
        self.amount_entry.grid(row=1, column=1, sticky="w", pady=10, padx=(15, 0))

        ctk.CTkLabel(form, text="Date (YYYY-MM-DD)").grid(row=2, column=0, sticky="w", pady=10)
        self.date_entry = ctk.CTkEntry(form, width=250)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=2, column=1, sticky="w", pady=10, padx=(15, 0))

        ctk.CTkLabel(form, text="Note (optional)").grid(row=3, column=0, sticky="w", pady=10)
        self.note_entry = ctk.CTkEntry(form, width=250, placeholder_text="e.g. Lunch with friends")
        self.note_entry.grid(row=3, column=1, sticky="w", pady=10, padx=(15, 0))

        self.status_label = ctk.CTkLabel(card, text="", text_color=c.COLOR_RED)
        self.status_label.pack(pady=(5, 0))

        ctk.CTkButton(card, text="↓  Save Transaction", height=44, width=250,
                      fg_color=c.COLOR_ACCENT, font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._save).pack(pady=25)

    def _update_categories(self):
        cats = c.CATEGORIES_INCOME if self.type_var.get() == "income" else c.CATEGORIES_EXPENSE
        self.category_menu.configure(values=cats)
        self.category_menu.set(cats[0])

    def _save(self):
        amount_str = self.amount_entry.get().strip()
        date_str = self.date_entry.get().strip()
        category = self.category_menu.get()
        ttype = self.type_var.get()
        note = self.note_entry.get().strip()

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            self.status_label.configure(text="Enter a valid positive amount.")
            return

        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            self.status_label.configure(text="Date must be in YYYY-MM-DD format.")
            return

        db.add_transaction(self.app.user["id"], ttype, category, amount, date_str, note)
        self.status_label.configure(text="", text_color=c.COLOR_RED)
        messagebox.showinfo("Saved", f"{ttype.title()} of Rs. {amount:,.0f} added successfully!")

        self.amount_entry.delete(0, "end")
        self.note_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.app.frames["dashboard"].refresh()

    def refresh(self):
        self._update_categories()
