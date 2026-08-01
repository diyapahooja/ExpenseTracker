"""
frames/transactions_frame.py
Full transaction list with search-by-category, date filters
(Today / This Week / This Month / Custom), delete, and CSV export.
"""

import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv

import database as db
import constants as c


class TransactionsFrame(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.date_from = None
        self.date_to = None

        ctk.CTkLabel(self, text="Transactions", font=ctk.CTkFont(size=26, weight="bold")
                     ).pack(anchor="w", pady=(0, 15))

        # ---- controls row ----
        controls = ctk.CTkFrame(self, fg_color=c.COLOR_CARD, corner_radius=12)
        controls.pack(fill="x", pady=(0, 15))

        row1 = ctk.CTkFrame(controls, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=(15, 5))

        self.search_entry = ctk.CTkEntry(row1, placeholder_text="🔍 Search category (e.g. Food)", width=260)
        self.search_entry.pack(side="left", padx=(0, 10))
        self.search_entry.bind("<Return>", lambda e: self.refresh())

        ctk.CTkButton(row1, text="Search", width=90, command=self.refresh).pack(side="left", padx=5)
        ctk.CTkButton(row1, text="Clear", width=90, fg_color="transparent", border_width=1,
                      command=self._clear_search).pack(side="left", padx=5)

        self.type_filter = ctk.CTkOptionMenu(row1, values=["All", "Income", "Expense"], width=110,
                                              command=lambda _: self.refresh())
        self.type_filter.pack(side="left", padx=(20, 5))

        ctk.CTkButton(row1, text="⬇ Export CSV", width=130, fg_color=c.COLOR_GREEN,
                      command=self._export_csv).pack(side="right")

        row2 = ctk.CTkFrame(controls, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=(5, 15))

        ctk.CTkLabel(row2, text="Filter:").pack(side="left", padx=(0, 10))
        for label, key in [("Today", "today"), ("This Week", "week"),
                            ("This Month", "month"), ("All Time", "all")]:
            ctk.CTkButton(row2, text=label, width=100, fg_color=c.COLOR_ACCENT,
                          command=lambda k=key: self._apply_quick_filter(k)).pack(side="left", padx=4)

        ctk.CTkLabel(row2, text="  Custom:").pack(side="left", padx=(15, 5))
        self.from_entry = ctk.CTkEntry(row2, width=110, placeholder_text="YYYY-MM-DD")
        self.from_entry.pack(side="left", padx=3)
        ctk.CTkLabel(row2, text="to").pack(side="left")
        self.to_entry = ctk.CTkEntry(row2, width=110, placeholder_text="YYYY-MM-DD")
        self.to_entry.pack(side="left", padx=3)
        ctk.CTkButton(row2, text="Apply", width=70, command=self._apply_custom_filter).pack(side="left", padx=5)

        # ---- table ----
        table_frame = ctk.CTkFrame(self, fg_color=c.COLOR_CARD, corner_radius=12)
        table_frame.pack(fill="both", expand=True)

        cols = ("id", "type", "category", "amount", "date", "note")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        headings = {"id": "ID", "type": "Type", "category": "Category",
                    "amount": "Amount (Rs.)", "date": "Date", "note": "Note"}
        widths = {"id": 40, "type": 80, "category": 120, "amount": 110, "date": 100, "note": 250}
        for col in cols:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")
        self.tree.pack(fill="both", expand=True, side="left", padx=(15, 0), pady=15)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", pady=15, padx=(0, 15))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", pady=(10, 0))
        ctk.CTkButton(btn_row, text="🗑 Delete Selected", fg_color=c.COLOR_RED,
                      command=self._delete_selected).pack(side="left")

    def _clear_search(self):
        self.search_entry.delete(0, "end")
        self.refresh()

    def _apply_quick_filter(self, key):
        today = datetime.now().date()
        if key == "today":
            self.date_from = self.date_to = today.strftime("%Y-%m-%d")
        elif key == "week":
            start = today - timedelta(days=today.weekday())
            self.date_from, self.date_to = start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        elif key == "month":
            start = today.replace(day=1)
            self.date_from, self.date_to = start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        else:  # all
            self.date_from = self.date_to = None
        self.from_entry.delete(0, "end")
        self.to_entry.delete(0, "end")
        self.refresh()

    def _apply_custom_filter(self):
        f, t = self.from_entry.get().strip(), self.to_entry.get().strip()
        try:
            if f:
                datetime.strptime(f, "%Y-%m-%d")
            if t:
                datetime.strptime(t, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date", "Use YYYY-MM-DD format.")
            return
        self.date_from = f or None
        self.date_to = t or None
        self.refresh()

    def _current_rows(self):
        category = self.search_entry.get().strip() or None
        ttype = self.type_filter.get().lower()
        ttype = None if ttype == "all" else ttype
        return db.get_transactions(self.app.user["id"], category=category,
                                    date_from=self.date_from, date_to=self.date_to, ttype=ttype)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for txn_id, ttype, category, amount, date, note in self._current_rows():
            sign = "+" if ttype == "income" else "-"
            self.tree.insert("", "end", values=(txn_id, ttype.title(), category,
                                                  f"{sign}{amount:,.0f}", date, note or ""))

    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a transaction to delete first.")
            return
        if not messagebox.askyesno("Confirm delete", f"Delete {len(selected)} transaction(s)?"):
            return
        for item in selected:
            txn_id = self.tree.item(item)["values"][0]
            db.delete_transaction(txn_id, self.app.user["id"])
        self.refresh()
        self.app.frames["dashboard"].refresh()

    def _export_csv(self):
        rows = self._current_rows()
        if not rows:
            messagebox.showinfo("Nothing to export", "No transactions match the current filters.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile="expenses.csv",
                                             filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Type", "Category", "Amount", "Date", "Note"])
            for txn_id, ttype, category, amount, date, note in rows:
                writer.writerow([txn_id, ttype, category, amount, date, note or ""])
        messagebox.showinfo("Exported", f"Saved to {path}")
