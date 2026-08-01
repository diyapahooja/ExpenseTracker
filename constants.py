"""
Constants used across the Expense Tracker app:
categories, month names, and theme colors.
"""

CATEGORIES_EXPENSE = ["Food", "Shopping", "Travel", "Bills", "Education",
                       "Entertainment", "Health", "Rent", "Other"]

CATEGORIES_INCOME = ["Salary", "Freelance", "Business", "Investment", "Gift", "Other"]

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

# ---- Theme ----
COLOR_BG = "#1a1a2e"
COLOR_SIDEBAR = "#16213e"
COLOR_CARD = "#0f3460"
COLOR_ACCENT = "#4361ee"
COLOR_GREEN = "#2ecc71"
COLOR_RED = "#e74c3c"
COLOR_BLUE = "#3498db"
COLOR_YELLOW = "#f1c40f"
COLOR_TEXT_MUTED = "#8e8ea0"

CHART_COLORS = ["#e74c3c", "#3498db", "#2ecc71", "#f1c40f", "#9b59b6",
                "#1abc9c", "#e67e22", "#34495e", "#ff6b6b", "#48dbfb"]

# Simple monthly budget alert threshold (percentage of income spent) — extra feature
BUDGET_ALERT_THRESHOLD = 0.8
