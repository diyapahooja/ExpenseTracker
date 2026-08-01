"""
main.py — Entry point for the Expense Tracker app.
Run with:  python main.py
"""

import database as db
from auth_window import AuthWindow

if __name__ == "__main__":
    db.init_db()
    app = AuthWindow()
    app.mainloop()
