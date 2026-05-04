from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from database import (init_db, add_habit, delete_habit, get_all_habits, toggle_log,
                      get_streak, get_completion_rate, get_last_7_days_status,
                      get_monthly_data, is_completed_today,
                      create_user, get_user_by_email, get_user_by_id)
from datetime import date
import bcrypt
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# ─── AUTH DECORATOR ───────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# ─── AUTH ROUTES ──────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return render_template("register.html")
        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return render_template("register.html")

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        success = create_user(username, email, hashed)

        if success:
            flash("Account created! Please login.", "success")
            return redirect(url_for("login"))
        else:
            flash("Email or username already exists.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_user_by_email(email)

        if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ─── MAIN ROUTES ──────────────────────────────────────────────

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    habits = get_all_habits(user_id)
    habits_data = []
    for h in habits:
        habits_data.append({
            "id": h["id"],
            "name": h["name"],
            "description": h["description"],
            "color": h["color"],
            "streak": get_streak(h["id"]),
            "rate": get_completion_rate(h["id"]),
            "week": get_last_7_days_status(h["id"]),
            "done_today": is_completed_today(h["id"])
        })
    today = date.today().strftime("%B %d, %Y")
    return render_template("index.html", habits=habits_data, today=today, username=session["username"])

@app.route("/add", methods=["POST"])
@login_required
def add():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    color = request.form.get("color", "#6366f1")
    if name:
        add_habit(session["user_id"], name, description, color)
    return redirect(url_for("index"))

@app.route("/delete/<int:habit_id>", methods=["POST"])
@login_required
def delete(habit_id):
    delete_habit(habit_id, session["user_id"])
    return redirect(url_for("index"))

@app.route("/toggle/<int:habit_id>", methods=["POST"])
@login_required
def toggle(habit_id):
    log_date = request.form.get("date", str(date.today()))
    toggle_log(habit_id, log_date)
    return redirect(url_for("index"))

@app.route("/api/monthly/<int:habit_id>")
@login_required
def monthly(habit_id):
    data = get_monthly_data(habit_id)
    return jsonify(data)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
