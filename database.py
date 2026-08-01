"""
database.py
All SQLite database logic for the Expense Tracker:
- schema creation (users, transactions, budgets)
- user signup / login (passwords stored as SHA-256 hashes)
- transaction CRUD
- aggregate queries used for the dashboard / reports / charts
"""

import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expense_tracker.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,          -- 'income' or 'expense'
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            date TEXT NOT NULL,          -- YYYY-MM-DD
            note TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    # Extra feature: per-user, per-category monthly budgets
    cur.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            monthly_limit REAL NOT NULL,
            UNIQUE(user_id, category),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ---------------- Auth ----------------

def create_user(username: str, password: str):
    username = username.strip()
    if not username or not password.strip():
        return False, "Username and password cannot be empty."
    if len(password) < 4:
        return False, "Password must be at least 4 characters."
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password)),
        )
        conn.commit()
        return True, "Account created successfully. Please log in."
    except sqlite3.IntegrityError:
        return False, "That username is already taken."
    finally:
        conn.close()


def verify_user(username: str, password: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username FROM users WHERE username = ? AND password = ?",
        (username.strip(), hash_password(password)),
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1]}
    return None


# ---------------- Transactions ----------------

def add_transaction(user_id, ttype, category, amount, date, note=""):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO transactions (user_id, type, category, amount, date, note) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, ttype, category, amount, date, note),
    )
    conn.commit()
    conn.close()


def delete_transaction(txn_id, user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (txn_id, user_id))
    conn.commit()
    conn.close()


def get_transactions(user_id, category=None, date_from=None, date_to=None, ttype=None):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT id, type, category, amount, date, note FROM transactions WHERE user_id = ?"
    params = [user_id]
    if category:
        query += " AND category LIKE ?"
        params.append(f"%{category}%")
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND date <= ?"
        params.append(date_to)
    if ttype:
        query += " AND type = ?"
        params.append(ttype)
    query += " ORDER BY date DESC, id DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_recent_transactions(user_id, limit=8):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, type, category, amount, date, note FROM transactions "
        "WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_summary(user_id, month=None, year=None):
    """Returns (income, expense, savings) for the given month/year, or all-time if None."""
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT type, SUM(amount) FROM transactions WHERE user_id = ?"
    params = [user_id]
    if month and year:
        query += " AND strftime('%m', date) = ? AND strftime('%Y', date) = ?"
        params.extend([f"{month:02d}", str(year)])
    query += " GROUP BY type"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    income, expense = 0.0, 0.0
    for t, total in rows:
        if t == "income":
            income = total or 0.0
        elif t == "expense":
            expense = total or 0.0
    return income, expense, income - expense


def get_category_breakdown(user_id, month=None, year=None, ttype="expense"):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT category, SUM(amount) FROM transactions WHERE user_id = ? AND type = ?"
    params = [user_id, ttype]
    if month and year:
        query += " AND strftime('%m', date) = ? AND strftime('%Y', date) = ?"
        params.extend([f"{month:02d}", str(year)])
    query += " GROUP BY category ORDER BY SUM(amount) DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_monthly_trend(user_id, year):
    """Returns dict keyed '01'..'12' -> {'income': x, 'expense': y} for the given year."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT strftime('%m', date) as month, type, SUM(amount)
        FROM transactions
        WHERE user_id = ? AND strftime('%Y', date) = ?
        GROUP BY month, type
    """, (user_id, str(year)))
    rows = cur.fetchall()
    conn.close()
    data = {f"{i:02d}": {"income": 0.0, "expense": 0.0} for i in range(1, 13)}
    for month, ttype, total in rows:
        if month in data and ttype in ("income", "expense"):
            data[month][ttype] = total or 0.0
    return data


def get_available_years(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT strftime('%Y', date) FROM transactions WHERE user_id = ? ORDER BY 1 DESC",
                (user_id,))
    rows = [r[0] for r in cur.fetchall() if r[0]]
    conn.close()
    return rows


# ---------------- Budgets (extra feature) ----------------

def set_budget(user_id, category, monthly_limit):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO budgets (user_id, category, monthly_limit) VALUES (?, ?, ?)
        ON CONFLICT(user_id, category) DO UPDATE SET monthly_limit = excluded.monthly_limit
    """, (user_id, category, monthly_limit))
    conn.commit()
    conn.close()


def get_budgets(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT category, monthly_limit FROM budgets WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return {cat: limit for cat, limit in rows}
