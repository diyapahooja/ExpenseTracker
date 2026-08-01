"""
auth_window.py
Login / Sign up screen. On successful login it destroys itself and
launches the main dashboard app (main_app.MainApp).
"""

import customtkinter as ctk
from tkinter import messagebox
import database as db
import constants as c


class AuthWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker — Login")
        self.geometry("420x520")
        self.resizable(False, False)
        self.configure(fg_color=c.COLOR_BG)
        self.mode = "login"  # or "signup"

        self._build_ui()

    def _build_ui(self):
        for widget in self.winfo_children():
            widget.destroy()

        card = ctk.CTkFrame(self, fg_color=c.COLOR_CARD, corner_radius=16)
        card.pack(expand=True, fill="both", padx=30, pady=30)

        ctk.CTkLabel(card, text="💰", font=ctk.CTkFont(size=42)).pack(pady=(35, 0))
        ctk.CTkLabel(card, text="Expense Tracker",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(5, 0))

        subtitle = "Login to continue" if self.mode == "login" else "Create a new account"
        ctk.CTkLabel(card, text=subtitle, text_color=c.COLOR_TEXT_MUTED).pack(pady=(0, 25))

        self.username_entry = ctk.CTkEntry(card, placeholder_text="Username", width=260, height=40)
        self.username_entry.pack(pady=8)

        self.password_entry = ctk.CTkEntry(card, placeholder_text="Password", show="•", width=260, height=40)
        self.password_entry.pack(pady=8)
        self.password_entry.bind("<Return>", lambda e: self._submit())

        if self.mode == "signup":
            self.confirm_entry = ctk.CTkEntry(card, placeholder_text="Confirm password", show="•",
                                               width=260, height=40)
            self.confirm_entry.pack(pady=8)
            self.confirm_entry.bind("<Return>", lambda e: self._submit())

        self.error_label = ctk.CTkLabel(card, text="", text_color=c.COLOR_RED)
        self.error_label.pack(pady=(5, 0))

        btn_text = "Login" if self.mode == "login" else "Sign Up"
        ctk.CTkButton(card, text=btn_text, width=260, height=42, command=self._submit,
                      fg_color=c.COLOR_ACCENT, font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))

        toggle_text = "Don't have an account? Sign up" if self.mode == "login" else "Already have an account? Login"
        ctk.CTkButton(card, text=toggle_text, fg_color="transparent", hover_color=c.COLOR_SIDEBAR,
                      text_color=c.COLOR_BLUE, command=self._toggle_mode).pack(pady=(5, 20))

    def _toggle_mode(self):
        self.mode = "signup" if self.mode == "login" else "login"
        self._build_ui()

    def _submit(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if self.mode == "login":
            user = db.verify_user(username, password)
            if user:
                self.destroy()
                from main_app import MainApp
                app = MainApp(user)
                app.mainloop()
            else:
                self.error_label.configure(text="Invalid username or password.")
        else:
            confirm = self.confirm_entry.get()
            if password != confirm:
                self.error_label.configure(text="Passwords do not match.")
                return
            ok, msg = db.create_user(username, password)
            if ok:
                messagebox.showinfo("Success", msg)
                self.mode = "login"
                self._build_ui()
            else:
                self.error_label.configure(text=msg)
