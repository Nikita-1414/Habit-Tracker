import sqlite3
import os
from datetime import date, timedelta

# Use /tmp for Render, fallback to local for development
DB_DIR = os.environ.get("DB_DIR", os.path.dirname(__file__))
DB_NAME = os.path.join(DB_DIR, "habits.db")

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at DATE DEFAULT (date('now'))
        )
    """)

    # Habits table with user_id
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            color TEXT DEFAULT '#6366f1',
            created_at DATE DEFAULT (date('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            log_date DATE NOT NULL,
            completed INTEGER DEFAULT 0,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
            UNIQUE(habit_id, log_date)
        )
    """)

    conn.commit()
    conn.close()

# ─── USER FUNCTIONS ───────────────────────────────────────────

def create_user(username, email, password):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

# ─── HABIT FUNCTIONS ──────────────────────────────────────────

def add_habit(user_id, name, description, color):
    conn = get_connection()
    conn.execute(
        "INSERT INTO habits (user_id, name, description, color) VALUES (?, ?, ?, ?)",
        (user_id, name, description, color)
    )
    conn.commit()
    conn.close()

def delete_habit(habit_id, user_id):
    conn = get_connection()
    conn.execute("DELETE FROM habits WHERE id = ? AND user_id = ?", (habit_id, user_id))
    conn.commit()
    conn.close()

def get_all_habits(user_id):
    conn = get_connection()
    habits = conn.execute(
        "SELECT * FROM habits WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return habits

def toggle_log(habit_id, log_date):
    conn = get_connection()
    existing = conn.execute(
        "SELECT * FROM logs WHERE habit_id = ? AND log_date = ?",
        (habit_id, log_date)
    ).fetchone()

    if existing:
        new_status = 1 if existing["completed"] == 0 else 0
        conn.execute(
            "UPDATE logs SET completed = ? WHERE habit_id = ? AND log_date = ?",
            (new_status, habit_id, log_date)
        )
    else:
        conn.execute(
            "INSERT INTO logs (habit_id, log_date, completed) VALUES (?, ?, 1)",
            (habit_id, log_date)
        )
    conn.commit()
    conn.close()

def get_streak(habit_id):
    conn = get_connection()
    logs = conn.execute(
        "SELECT log_date FROM logs WHERE habit_id = ? AND completed = 1 ORDER BY log_date DESC",
        (habit_id,)
    ).fetchall()
    conn.close()

    if not logs:
        return 0

    dates = [date.fromisoformat(row["log_date"]) for row in logs]
    streak = 0
    check_date = date.today()

    for d in dates:
        if d == check_date or d == check_date - timedelta(days=1):
            streak += 1
            check_date = d - timedelta(days=1)
        else:
            break

    return streak

def get_completion_rate(habit_id, days=30):
    conn = get_connection()
    start_date = date.today() - timedelta(days=days - 1)
    completed = conn.execute(
        "SELECT COUNT(*) as count FROM logs WHERE habit_id = ? AND completed = 1 AND log_date >= ?",
        (habit_id, start_date)
    ).fetchone()["count"]
    conn.close()
    return round((completed / days) * 100)

def get_last_7_days_status(habit_id):
    conn = get_connection()
    result = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        row = conn.execute(
            "SELECT completed FROM logs WHERE habit_id = ? AND log_date = ?",
            (habit_id, d)
        ).fetchone()
        result.append({
            "date": d.strftime("%a"),
            "full_date": str(d),
            "completed": row["completed"] if row else 0
        })
    conn.close()
    return result

def get_monthly_data(habit_id):
    conn = get_connection()
    result = []
    for i in range(29, -1, -1):
        d = date.today() - timedelta(days=i)
        row = conn.execute(
            "SELECT completed FROM logs WHERE habit_id = ? AND log_date = ?",
            (habit_id, d)
        ).fetchone()
        result.append({
            "date": str(d),
            "completed": row["completed"] if row else 0
        })
    conn.close()
    return result

def is_completed_today(habit_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT completed FROM logs WHERE habit_id = ? AND log_date = ?",
        (habit_id, date.today())
    ).fetchone()
    conn.close()
    return row and row["completed"] == 1
