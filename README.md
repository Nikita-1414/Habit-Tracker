# 🔥 Habit Tracker

A beautiful and minimal **habit tracking app** built with Python Streamlit and SQLite. Track your daily habits, build streaks, and visualize your progress — all in one place.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?style=flat-square&logo=streamlit)
![SQLite](https://img.shields.io/badge/SQLite-Database-green?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📸 Features

- ✅ **User Authentication** — secure login & registration with hashed passwords
- ✅ **Add / Delete Habits** — with custom name, description & color
- 🔥 **Streak Tracking** — consecutive days auto-calculated
- 📊 **30-Day Completion Rate** — see your consistency in %
- 📅 **Weekly Dots** — visual last 7 days status (clickable)
- 📈 **30-Day Bar Chart** — interactive progress chart via Chart.js
- 🗄️ **SQLite Database** — all data persisted locally with multi-user support
- 🌙 **Dark UI** — clean, modern dark theme with responsive design

---

## 🗂️ Project Structure

```
habit-tracker/
│
├── app.py              # Main Streamlit app
├── database.py         # DB setup, queries & logic
├── requirements.txt    # Python dependencies
│
├── .streamlit/
│   └── config.toml     # Streamlit configuration
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
streamlit run app.py
```

### 4. Open in Browser
Streamlit will automatically open your app in the browser (typically at `http://localhost:8501`). If not, check the terminal for the URL.

> **Note:** `habits.db` will be created automatically on first run.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite (via Python's built-in `sqlite3`) |
| Frontend/Backend | Python, Streamlit |
| Database | SQLite (via Python's built-in `sqlite3`) |
| Security | bcrypt (password hashing) |
| UI/Theme | Streamlit Components + Custom CSS |
| Fonts | Streamlit Default

## 📋 How to Use

1. **Register** — Create a new account with email & password
2. **Login** — Sign in with your credentials
3. Click **"+ Add Habit"** to create a new habit
4. Choose a name, description, and color
5. Every day, click **"Mark Done"** to log your habit
6. Watch your 🔥 streak grow!
7. Click **"Show 30-day progress"** to see your bar chart
8. Click any weekly dot to toggle past days
9. Click **"Logout"** when done

---

## 🌐 Deployment on Streamlit Cloud

### 1. Push to GitHub
```bash
git add .
git commit -m "Deploy to Streamlit"
git push origin main
```

### 2. Deploy on Streamlit Cloud
- Go to [Streamlit Cloud](https://streamlit.io/cloud)
- Click **"New app"**
- Select your GitHub repository, branch, and `app.py`
- Click **"Deploy!"**

### 3. Configure Environment Variables (if needed)
In Streamlit Cloud dashboard, go to **App settings** → **Secrets** and add any environment variables.

### Database Persistence
SQLite database is stored locally in the Streamlit container. For persistent storage across deployments, consider using cloud databases (PostgreSQL, MongoDB, etc.).

---

## 🚀 Future Improvements

- [ ] Email/notification reminders
- [ ] Export data as CSV
- [ ] Mobile app (React Native)
- [ ] Dark/Light theme toggle
- [ ] Social features (share streaks, friend challenges)
- [ ] Advanced analytics & insightsenders


---

## 👨‍💻 Author

Made with ❤️ by Nikita

---


