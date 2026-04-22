import sqlite3
from datetime import date, timedelta

DB_NAME = "habits.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            color TEXT DEFAULT '#6366f1',
            created_at DATE DEFAULT (date('now'))
        )
    """)

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

def add_habit(name, description, color):
    conn = get_connection()
    conn.execute(
        "INSERT INTO habits (name, description, color) VALUES (?, ?, ?)",
        (name, description, color)
    )
    conn.commit()
    conn.close()

def delete_habit(habit_id):
    conn = get_connection()
    conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()
    conn.close()

def get_all_habits():
    conn = get_connection()
    habits = conn.execute("SELECT * FROM habits ORDER BY created_at DESC").fetchall()
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
