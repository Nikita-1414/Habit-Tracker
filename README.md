# 🔥 Habit Tracker

A simple yet powerful web application to build and track your daily habits. Set goals, monitor your progress, and maintain streaks to stay motivated.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3+-green?style=flat-square&logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## ✨ Features

- ✅ **User Authentication** — Secure registration and login with bcrypt password hashing
- ✅ **Habit Management** — Create, view, and delete habits with custom descriptions and colors
- 🔥 **Streak Tracking** — Current streak counter for each habit
- 📊 **Completion Rate** — Track percentage of completed days
- 📅 **7-Day Activity View** — Visual overview of last week's progress
- 📈 **Monthly Analytics** — Track habit data across the month
- 🗄️ **Multi-User Support** — SQLite database with relational schema for multiple users
- 🎨 **Responsive Design** — Clean, user-friendly interface for desktop and mobile

---

## 🗂️ Project Structure

```
habit-tracker/
├── app.py                 # Main Flask application with routes
├── database.py            # Database initialization and operations
├── requirements.txt       # Python dependencies
├── render.yaml           # Render deployment configuration
├── habits.db             # SQLite database (created automatically)
└── templates/
    ├── index.html        # Dashboard/main page
    ├── login.html        # Login page
    └── register.html     # Registration page
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/habit-tracker.git
cd habit-tracker
```

### 2. Create a Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional for Production)
```bash
# Windows
set SECRET_KEY=your-secret-key-here

# macOS/Linux
export SECRET_KEY=your-secret-key-here
```

### 5. Run the Application
```bash
python app.py
```

### 6. Open in Browser
Navigate to `http://localhost:5000` to access the app.

> **Note:** `habits.db` will be created automatically on first run.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | Flask (Python) |
| Database | SQLite with relational schema |
| Authentication | Bcrypt password hashing |
| Frontend | HTML/CSS/JavaScript |
| Deployment | Render.com (configured via render.yaml) |
| Server | Gunicorn (production WSGI server) |

---

## 📋 How to Use

1. **Register** — Create a new account with username, email, and password (minimum 6 characters)
2. **Login** — Sign in with your credentials
3. **Create Habits** — Click "Add Habit" to create new habits
4. **Choose Details** — Set name, description, and custom color for each habit
5. **Log Daily** — Click to mark habits as completed each day
6. **Monitor Progress** — 
   - View your current streak
   - Check completion rate percentage
   - See last 7 days activity
   - Review monthly trends
7. **Logout** — Sign out when done

---

## 🗄️ Database Schema

### Users Table
```sql
id (PRIMARY KEY)
username (UNIQUE)
email (UNIQUE)
password (hashed)
created_at
```

### Habits Table
```sql
id (PRIMARY KEY)
user_id (FOREIGN KEY)
name
description
color (default: #6366f1)
created_at
```

### Logs Table
```sql
id (PRIMARY KEY)
habit_id (FOREIGN KEY)
log_date
completed (0/1)
UNIQUE(habit_id, log_date)
```

---

## 🚀 Deployment on Render

The application is pre-configured for deployment on [Render](https://render.com):

### Steps:
1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click **"New +"** and select **"Web Service"**
4. Connect your GitHub repository
5. Render will automatically detect `render.yaml` and configure your deployment
6. Your app will be live at your Render URL

### Environment Variables:
Set the following in Render dashboard under **Environment**:
- `SECRET_KEY` — Use a strong secret key (don't use the default dev key)

---

## 🔐 Security Notes

- Passwords are hashed using bcrypt with salt
- SQLite has PRAGMA foreign_keys enabled for data integrity
- Set `SECRET_KEY` environment variable in production
- Enable HTTPS in production environments
- Input validation on all user forms

---

## 🚀 Future Enhancements

- [ ] Email notifications and reminders
- [ ] Export habit data as CSV
- [ ] Social features (share streaks, friend lists)
- [ ] Mobile app version
- [ ] Advanced statistics and graphs
- [ ] Dark mode theme
- [ ] Habit categories and tags

---

## 🤝 Contributing

Contributions are welcome! Please feel free to:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the MIT License. See the LICENSE file for more details.

---

## 🆘 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions

---

**Happy Habit Tracking!** 🎯


