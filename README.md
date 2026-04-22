# 🔥 Habit Tracker

A beautiful and minimal **habit tracking web app** built with Python Flask and SQLite. Track your daily habits, build streaks, and visualize your progress — all in one place.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3+-black?style=flat-square&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-green?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📸 Features

- ✅ **Add / Delete Habits** — with custom name, description & color
- 🔥 **Streak Tracking** — consecutive days auto-calculated
- 📊 **30-Day Completion Rate** — see your consistency in %
- 📅 **Weekly Dots** — visual last 7 days status (clickable)
- 📈 **30-Day Bar Chart** — interactive progress chart via Chart.js
- 🗄️ **SQLite Database** — all data saved locally, no signup needed
- 🌙 **Dark UI** — clean, modern dark theme

---

## 🗂️ Project Structure

```
habit-tracker/
│
├── app.py              # Main Flask app (routes)
├── database.py         # DB setup, queries & logic
├── requirements.txt    # Python dependencies
│
├── templates/
│   └── index.html      # Frontend (HTML + CSS + JS)
│
└── habits.db           # SQLite DB (auto-created on first run)
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/habit-tracker.git
cd habit-tracker
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
python app.py
```

### 4. Open in Browser
```
http://127.0.0.1:5000
```

> **Note:** `habits.db` will be created automatically on first run.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite (via Python's built-in `sqlite3`) |
| Frontend | HTML, CSS, JavaScript |
| Charts | Chart.js (CDN) |
| Fonts | Google Fonts (Syne + DM Sans) |

---

## 📋 How to Use

1. Click **"+ Add Habit"** to create a new habit
2. Choose a name, description, and color
3. Every day, click **"Mark Done"** to log your habit
4. Watch your 🔥 streak grow!
5. Click **"Show 30-day progress"** to see your bar chart
6. Click any weekly dot to toggle past days

---

## 🚀 Future Improvements

- [ ] User authentication (login/signup)
- [ ] Email/notification reminders
- [ ] Export data as CSV
- [ ] Mobile app (React Native)
- [ ] Dark/Light theme toggle

---

## 👨‍💻 Author

Made with ❤️ by Nikita

---


