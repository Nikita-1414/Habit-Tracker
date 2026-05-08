import streamlit as st
import sqlite3
from datetime import datetime, date, timedelta
import bcrypt
from database import (
    init_db, add_habit, delete_habit, get_all_habits, toggle_log,
    get_streak, get_completion_rate, get_last_7_days_status,
    get_monthly_data, is_completed_today,
    create_user, get_user_by_email, get_user_by_id
)

# ─────────────────────────────────────────────────────────────
# STREAMLIT PAGE CONFIGURATION
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Habit Tracker",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize database
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization error: {e}")

# ─────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# ─────────────────────────────────────────────────────────────
# AUTHENTICATION FUNCTIONS
# ─────────────────────────────────────────────────────────────
def register_user(username, email, password, confirm_password):
    """Register a new user"""
    if not username or not email or not password:
        st.error("All fields are required.")
        return False
    
    if password != confirm_password:
        st.error("Passwords do not match.")
        return False
    
    if len(password) < 6:
        st.error("Password must be at least 6 characters.")
        return False
    
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    success = create_user(username, email.lower(), hashed)
    
    if success:
        st.success("Account created! Please login.")
        st.session_state.page = "login"
        return True
    else:
        st.error("Email or username already exists.")
        return False

def login_user(email, password):
    """Login a user"""
    user = get_user_by_email(email.lower())
    
    if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
        st.session_state.user_id = user["id"]
        st.session_state.username = user["username"]
        st.session_state.page = "dashboard"
        return True
    else:
        st.error("Invalid email or password.")
        return False

def logout_user():
    """Logout the user"""
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.page = "login"

# ─────────────────────────────────────────────────────────────
# PAGE: REGISTER
# ─────────────────────────────────────────────────────────────
def show_register_page():
    st.title("📝 Register")
    st.write("Create a new account to get started!")
    
    with st.form("register_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="At least 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Create Account", use_container_width=True):
                if register_user(username, email, password, confirm_password):
                    st.rerun()
        
        with col2:
            if st.form_submit_button("Back to Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()

# ─────────────────────────────────────────────────────────────
# PAGE: LOGIN
# ─────────────────────────────────────────────────────────────
def show_login_page():
    st.title("🎯 Habit Tracker")
    st.write("Welcome back! Please login to your account.")
    
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Login", use_container_width=True):
                if login_user(email, password):
                    st.rerun()
        
        with col2:
            if st.form_submit_button("Create Account", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

# ─────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────────
def show_dashboard_page():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎯 Habit Tracker")
        st.caption(f"📅 {date.today().strftime('%B %d, %Y')}")
    
    with col2:
        st.write(f"👋 **{st.session_state.username}**")
        if st.button("Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    st.divider()
    
    # Get user's habits
    user_id = st.session_state.user_id
    habits = get_all_habits(user_id)
    
    # Stats Bar
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Habits", len(habits))
    
    with col2:
        done_today = sum(1 for h in habits if is_completed_today(h["id"]))
        st.metric("Done Today", done_today)
    
    with col3:
        avg_streak = sum(get_streak(h["id"]) for h in habits) / len(habits) if habits else 0
        st.metric("Avg Streak 🔥", f"{avg_streak:.1f}")
    
    with col4:
        avg_rate = sum(get_completion_rate(h["id"]) for h in habits) / len(habits) if habits else 0
        st.metric("Avg Rate", f"{avg_rate:.0f}%")
    
    st.divider()
    
    # Add Habit Section
    st.subheader("➕ Add New Habit")
    with st.form("add_habit_form", clear_on_submit=True):
        habit_name = st.text_input("Habit Name", placeholder="e.g., Morning Exercise")
        habit_desc = st.text_area("Description (optional)", placeholder="Add any notes about this habit", height=80)
        habit_color = st.color_picker("Pick a Color", "#a78bfa")
        
        if st.form_submit_button("Add Habit", use_container_width=True):
            if habit_name.strip():
                add_habit(user_id, habit_name, habit_desc, habit_color)
                st.success("✅ Habit added successfully!")
                st.rerun()
            else:
                st.error("Please enter a habit name.")
    
    st.divider()
    
    # Display Habits
    if habits:
        st.subheader("📋 Your Habits")
        
        for habit in habits:
            habit_id = habit["id"]
            streak = get_streak(habit_id)
            rate = get_completion_rate(habit_id)
            week_status = get_last_7_days_status(habit_id)
            done_today = is_completed_today(habit_id)
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
                
                with col1:
                    st.subheader(f"{habit['name']}")
                    if habit['description']:
                        st.caption(habit['description'])
                
                with col2:
                    st.metric("Streak", f"🔥 {streak}")
                
                with col3:
                    st.metric("Rate", f"{rate:.0f}%")
                
                with col4:
                    status_emoji = "✅" if done_today else "⬜"
                    col_toggle, col_delete = st.columns(2)
                    with col_toggle:
                        if st.button("✓ Done", key=f"toggle_{habit_id}", use_container_width=True):
                            toggle_log(habit_id, date.today())
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️ Delete", key=f"delete_{habit_id}", use_container_width=True):
                            delete_habit(habit_id, user_id)
                            st.success("Habit deleted!")
                            st.rerun()
                
                # Display week status
                week_text = " ".join([("✅" if status else "⬜") for status in week_status])
                st.caption(f"Last 7 days: {week_text}")
                st.divider()
    else:
        st.info("📌 No habits yet! Create one to get started.")

# ─────────────────────────────────────────────────────────────
# MAIN APP LOGIC
# ─────────────────────────────────────────────────────────────
def main():
    if st.session_state.user_id is None:
        if st.session_state.page == "register":
            show_register_page()
        else:
            show_login_page()
    else:
        show_dashboard_page()

if __name__ == "__main__":
    main()
