"""
main_app.py
The main application window shown after login. Has a sidebar for
navigation and swaps out content frames:
  Dashboard | Add Transaction | Transactions | Reports | Budgets
"""

import customtkinter as ctk
from tkinter import ttk
from datetime import datetime

import database as db
import constants as c
from frames.dashboard_frame import DashboardFrame
from frames.add_transaction_frame import AddTransactionFrame
from frames.transactions_frame import TransactionsFrame
from frames.reports_frame import ReportsFrame
from frames.budgets_frame import BudgetsFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainApp(ctk.CTk):
    def __init__(self, user):
        super().__init__()
        self.user = user  # {"id": ..., "username": ...}

        self.title(f"Expense Tracker — {user['username']}")
        self.geometry("1200x720")
        self.minsize(1000, 620)
        self.configure(fg_color=c.COLOR_BG)

        self._setup_treeview_style()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()

        # container that holds whichever frame is currently active
        self.container = ctk.CTkFrame(self, fg_color=c.COLOR_BG)
        self.container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for FrameClass, name in [
            (DashboardFrame, "dashboard"),
            (AddTransactionFrame, "add"),
            (TransactionsFrame, "transactions"),
            (ReportsFrame, "reports"),
            (BudgetsFrame, "budgets"),
        ]:
            frame = FrameClass(self.container, self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("dashboard")

    def _setup_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                         background="#20233c",
                         foreground="white",
                         fieldbackground="#20233c",
                         rowheight=30,
                         borderwidth=0,
                         font=("Segoe UI", 11))
        style.map("Treeview", background=[("selected", c.COLOR_ACCENT)])
        style.configure("Treeview.Heading",
                         background=c.COLOR_SIDEBAR,
                         foreground="white",
                         font=("Segoe UI", 11, "bold"),
                         borderwidth=0)
        style.map("Treeview.Heading", background=[("active", c.COLOR_ACCENT)])

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=230, fg_color=c.COLOR_SIDEBAR, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="💰 ExpenseTracker",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(30, 5), padx=20)
        ctk.CTkLabel(sidebar, text=f"👤 {self.user['username']}",
                     text_color=c.COLOR_TEXT_MUTED).pack(pady=(0, 25))

        nav_items = [
            ("📊  Dashboard", "dashboard"),
            ("➕  Add Transaction", "add"),
            ("📋  Transactions", "transactions"),
            ("📈  Reports & Charts", "reports"),
            ("🎯  Budgets", "budgets"),
        ]
        self.nav_buttons = {}
        for label, key in nav_items:
            btn = ctk.CTkButton(sidebar, text=label, anchor="w", height=42,
                                 fg_color="transparent", hover_color=c.COLOR_ACCENT,
                                 font=ctk.CTkFont(size=13),
                                 command=lambda k=key: self.show_frame(k))
            btn.pack(fill="x", padx=15, pady=3)
            self.nav_buttons[key] = btn

        ctk.CTkFrame(sidebar, fg_color=c.COLOR_TEXT_MUTED, height=1).pack(fill="x", padx=20, pady=20)

        ctk.CTkButton(sidebar, text="🚪  Logout", anchor="w", height=42,
                      fg_color="transparent", hover_color=c.COLOR_RED,
                      command=self._logout).pack(fill="x", padx=15, pady=3, side="bottom")

    def show_frame(self, name):
        for key, btn in self.nav_buttons.items():
            btn.configure(fg_color=c.COLOR_ACCENT if key == name else "transparent")
        frame = self.frames[name]
        if hasattr(frame, "refresh"):
            frame.refresh()
        frame.tkraise()

    def _logout(self):
        self.destroy()
        from auth_window import AuthWindow
        app = AuthWindow()
        app.mainloop()


if __name__ == "__main__":
    # Allows testing main_app directly with a dummy user (dev convenience)
    db.init_db()
    dummy_user = {"id": 1, "username": "demo"}
    app = MainApp(dummy_user)
    app.mainloop()
