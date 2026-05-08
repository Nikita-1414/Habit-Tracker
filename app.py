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
# CUSTOM STYLING (Minimal, Stable CSS)
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .habit-card {
        border-left: 6px solid #a78bfa;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
        background-color: rgba(30, 30, 45, 0.6);
    }
    
    .day-indicator {
        display: inline-block;
        width: 28px;
        height: 28px;
        margin: 3px;
        border-radius: 4px;
        text-align: center;
        line-height: 28px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .day-completed {
        background-color: #a78bfa;
        color: white;
    }
    
    .day-missed {
        background-color: #3a3a50;
        color: #8a8a9e;
    }
    
    .stat-box {
        background-color: rgba(30, 30, 45, 0.8);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "show_add_habit" not in st.session_state:
    st.session_state.show_add_habit = False

# ─────────────────────────────────────────────────────────────
# HELPER FUNCTIONS FOR 30-DAY TRACKING
# ─────────────────────────────────────────────────────────────
def get_30_day_status(habit_id):
    """Get last 30 days status for a habit"""
    conn = sqlite3.connect("habits.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    status = []
    for i in range(29, -1, -1):
        check_date = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        result = cursor.execute(
            "SELECT completed FROM logs WHERE habit_id = ? AND log_date = ?",
            (habit_id, check_date)
        ).fetchone()
        status.append(bool(result["completed"]) if result else False)
    
    conn.close()
    return status

def render_30_day_grid(habit_id, habit_color):
    """Render 30-day calendar grid"""
    days_status = get_30_day_status(habit_id)
    
    # Create grid layout (6 rows x 5 columns for 30 days)
    html = '<div style="display: flex; flex-wrap: wrap; gap: 5px; margin: 10px 0;">'
    
    for i, status in enumerate(days_status):
        if status:
            html += f'<div class="day-indicator day-completed" style="background-color: {habit_color};">✓</div>'
        else:
            html += f'<div class="day-indicator day-missed">·</div>'
    
    html += '</div>'
    return html

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
    st.session_state.show_add_habit = False

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
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown("# 🎯 Habit Tracker")
        st.caption(f"📅 {date.today().strftime('%B %d, %Y')}")
    
    with col2:
        pass
    
    with col3:
        st.write(f"👋 **{st.session_state.username}**")
        if st.button("🚪 Logout", use_container_width=True, key="logout_main"):
            logout_user()
            st.rerun()
    
    # Get user's habits
    user_id = st.session_state.user_id
    habits = get_all_habits(user_id)
    
    # Stats Bar
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown('<div class="stat-box"><h3>📊</h3><p><strong>{}</strong></p><p style="font-size: 0.8rem; color: #8a8a9e;">Total Habits</p></div>'.format(len(habits)), unsafe_allow_html=True)
    
    with col2:
        done_today = sum(1 for h in habits if is_completed_today(h["id"]))
        st.markdown('<div class="stat-box"><h3>✅</h3><p><strong>{}</strong></p><p style="font-size: 0.8rem; color: #8a8a9e;">Done Today</p></div>'.format(done_today), unsafe_allow_html=True)
    
    with col3:
        avg_streak = sum(get_streak(h["id"]) for h in habits) / len(habits) if habits else 0
        st.markdown('<div class="stat-box"><h3>🔥</h3><p><strong>{:.1f}</strong></p><p style="font-size: 0.8rem; color: #8a8a9e;">Avg Streak</p></div>'.format(avg_streak), unsafe_allow_html=True)
    
    with col4:
        avg_rate = sum(get_completion_rate(h["id"]) for h in habits) / len(habits) if habits else 0
        st.markdown('<div class="stat-box"><h3>📈</h3><p><strong>{:.0f}%</strong></p><p style="font-size: 0.8rem; color: #8a8a9e;">Avg Rate</p></div>'.format(avg_rate), unsafe_allow_html=True)
    
    with col5:
        if st.button("➕ Add Habit", use_container_width=True, key="add_habit_btn"):
            st.session_state.show_add_habit = True
            st.rerun()
    
    st.divider()
    
    # Add Habit Modal
    if st.session_state.show_add_habit:
        st.markdown("## ✨ New Habit")
        with st.form("add_habit_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            
            with col1:
                habit_name = st.text_input("Habit Name", placeholder="e.g., Morning Run", key="habit_name_input")
            
            with col2:
                habit_color = st.color_picker("Pick a Color", "#a78bfa", key="habit_color_input")
            
            habit_desc = st.text_area("Description", placeholder="e.g., Run 5km every morning", height=60, key="habit_desc_input")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✅ Add Habit", use_container_width=True):
                    if habit_name.strip():
                        add_habit(user_id, habit_name, habit_desc, habit_color)
                        st.session_state.show_add_habit = False
                        st.success("Habit added successfully!")
                        st.rerun()
                    else:
                        st.error("Please enter a habit name.")
            
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.show_add_habit = False
                    st.rerun()
        
        st.divider()
    
    # Display Habits with Beautiful Cards
    if habits:
        st.markdown("## 📋 Your Habits")
        
        for habit in habits:
            habit_id = habit["id"]
            streak = get_streak(habit_id)
            rate = get_completion_rate(habit_id)
            done_today = is_completed_today(habit_id)
            
            # Habit Card
            with st.container():
                # Card Header
                col1, col2, col3, col4 = st.columns([2, 0.8, 0.8, 0.4])
                
                with col1:
                    st.markdown(f"<div style='margin-bottom: 5px;'><strong style='font-size: 1.1rem;'>{habit['name']}</strong></div>", unsafe_allow_html=True)
                    if habit['description']:
                        st.caption(habit['description'])
                
                with col2:
                    st.markdown(f"<div style='text-align: center;'><div style='font-size: 0.7rem; color: #8a8a9e;'>STREAK</div><div style='font-size: 1.2rem; font-weight: bold; color: #a78bfa;'>🔥 {streak}</div></div>", unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"<div style='text-align: center;'><div style='font-size: 0.7rem; color: #8a8a9e;'>RATE</div><div style='font-size: 1.2rem; font-weight: bold; color: #a78bfa;'>{rate:.0f}%</div></div>", unsafe_allow_html=True)
                
                with col4:
                    status_emoji = "✅" if done_today else "⬜"
                    st.markdown(f"<div style='text-align: center; margin-top: 10px;'>{status_emoji}</div>", unsafe_allow_html=True)
                
                # 30-Day Progress Grid
                st.markdown("#### Last 30 Days")
                st.markdown(render_30_day_grid(habit_id, habit['color']), unsafe_allow_html=True)
                
                # Action Buttons
                col1, col2, col3 = st.columns([1.5, 1.5, 1])
                
                with col1:
                    if st.button("✓ Mark Done", key=f"done_{habit_id}", use_container_width=True):
                        toggle_log(habit_id, date.today())
                        st.success("Great job! 🎉")
                        st.rerun()
                
                with col2:
                    if st.button("Mark Not Done", key=f"undo_{habit_id}", use_container_width=True):
                        toggle_log(habit_id, date.today())
                        st.info("Updated!")
                        st.rerun()
                
                with col3:
                    if st.button("❌", key=f"delete_{habit_id}", use_container_width=True):
                        delete_habit(habit_id, user_id)
                        st.success("Habit deleted!")
                        st.rerun()
                
                st.markdown("---")
    else:
        st.info("📌 No habits yet! Click '➕ Add Habit' to get started.")

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
