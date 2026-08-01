# 💰 Expense Tracker (Python + CustomTkinter + SQLite)

A desktop expense/income tracker with a modern dark-mode GUI, per-user login,
SQLite storage, search/filter, CSV export, and matplotlib charts —
built to be a solid, demo-ready resume project.

## Features

- 🔐 **Multi-user login/signup** — passwords stored as SHA-256 hashes, not plain text
- ➕ **Add income/expense** — category dropdown, amount, date, optional note
- 📋 **Transactions list** — search by category, filter by Today / This Week /
  This Month / custom date range, delete entries
- 📤 **Export to CSV** — one click, opens a native "Save As" dialog
- 📊 **Dashboard** — current month income / expense / savings cards + recent
  transactions table
- 📈 **Reports & Charts**
  - Pie chart — expense breakdown by category (any month/year)
  - Bar chart — income vs expense trend across the whole year
- 🎯 **Budgets (bonus feature)** — set a monthly limit per category; the
  dashboard shows a warning banner when you're close to or over budget, and
  the Budgets tab shows live progress bars
- 🌙 Clean dark theme throughout

## Project structure

```
expense_tracker/
├── main.py                     # entry point — run this
├── auth_window.py               # login / signup screen
├── main_app.py                  # main window shell + sidebar navigation
├── database.py                  # all SQLite logic (schema, auth, CRUD, queries)
├── constants.py                 # categories, colors, theme constants
├── requirements.txt
└── frames/
    ├── dashboard_frame.py
    ├── add_transaction_frame.py
    ├── transactions_frame.py
    ├── reports_frame.py
    └── budgets_frame.py
```

## Setup

1. Make sure Python 3.9+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   (On Linux, if you get a tkinter error, also run: `sudo apt install python3-tk`)
3. Run the app:
   ```bash
   python main.py
   ```

The app will create `expense_tracker.db` automatically in the project folder
the first time you run it — no manual database setup needed.

## Database schema

**users**
| column   | type    |
|----------|---------|
| id       | INTEGER PK |
| username | TEXT UNIQUE |
| password | TEXT (SHA-256 hash) |

**transactions**
| column   | type |
|----------|------|
| id       | INTEGER PK |
| user_id  | INTEGER (FK → users) |
| type     | TEXT ('income' / 'expense') |
| category | TEXT |
| amount   | REAL |
| date     | TEXT (YYYY-MM-DD) |
| note     | TEXT |

**budgets** *(bonus feature)*
| column        | type |
|---------------|------|
| id            | INTEGER PK |
| user_id       | INTEGER (FK → users) |
| category      | TEXT |
| monthly_limit | REAL |

## Ideas to extend further

- Recurring transactions (e.g. auto-add monthly rent)
- Multi-currency support
- Dark/light theme toggle
- Export report as PDF instead of just CSV
- Cloud sync using a hosted database

## Tested

The database layer and full GUI flow (login → dashboard → add transaction →
search/filter → charts → budgets) were tested end-to-end before delivery,
including a headless Xvfb run of the actual Tkinter/CustomTkinter window.
