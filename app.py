from flask import Flask, render_template, request, redirect, url_for, jsonify
from database import init_db, add_habit, delete_habit, get_all_habits, toggle_log, get_streak, get_completion_rate, get_last_7_days_status, get_monthly_data, is_completed_today
from datetime import date

app = Flask(__name__)

@app.route("/")
def index():
    habits = get_all_habits()
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
    return render_template("index.html", habits=habits_data, today=today)

@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    color = request.form.get("color", "#6366f1")
    if name:
        add_habit(name, description, color)
    return redirect(url_for("index"))

@app.route("/delete/<int:habit_id>", methods=["POST"])
def delete(habit_id):
    delete_habit(habit_id)
    return redirect(url_for("index"))

@app.route("/toggle/<int:habit_id>", methods=["POST"])
def toggle(habit_id):
    log_date = request.form.get("date", str(date.today()))
    toggle_log(habit_id, log_date)
    return redirect(url_for("index"))

@app.route("/api/monthly/<int:habit_id>")
def monthly(habit_id):
    data = get_monthly_data(habit_id)
    return jsonify(data)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
