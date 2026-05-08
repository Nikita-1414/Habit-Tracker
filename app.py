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
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        background-color: #0a0a0f;
    }
    
    .main {
        background-color: #0a0a0f;
    }
    
    .habit-card {
        background-color: #1a1a2e;
        border-left: 5px solid #a78bfa;
        border-radius: 8px;
        padding: 20px;
        margin: 15px 0;
    }
    
    .day-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0;
    }
    
    .day-number {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: bold;
        background-color: #2a2a3e;
        color: #6b6b80;
    }
    
    .day-number.completed {
        background-color: #a78bfa;
        color: white;
    }
    
    .progress-bar {
        width: 100%;
        height: 6px;
        background-color: #2a2a3e;
        border-radius: 3px;
        overflow: hidden;
        margin: 8px 0;
    }
    
    .progress-fill {
        height: 100%;
        border-radius: 3px;
    }
    
    .stat-box {
        background-color: #1a1a2e;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        margin: 5px;
    }
    
    .sidebar-card {
        background-color: #1a1a2e;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2a2a3e;
    }
    
    @media (max-width: 768px) {
        .habit-card {
            padding: 15px;
        }
        .day-number {
            width: 28px;
            height: 28px;
            font-size: 9px;
        }
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
    """Render 30-day numbered calendar grid"""
    days_status = get_30_day_status(habit_id)
    
    html = '<div class="day-grid">'
    
    for day_num, is_completed in enumerate(days_status, 1):
        if is_completed:
            html += f'<div class="day-number completed" style="background-color: {habit_color}; border: 2px solid {habit_color};">{day_num}</div>'
        else:
            html += f'<div class="day-number">{day_num}</div>'
    
    html += '</div>'
    return html

def render_progress_bar(habit_id, habit_color):
    """Render progress bar for 30-day completion"""
    days_status = get_30_day_status(habit_id)
    completed = sum(days_status)
    percentage = (completed / len(days_status) * 100) if days_status else 0
    
    html = f'''
    <div class="progress-bar">
        <div class="progress-fill" style="width: {percentage}%; background-color: {habit_color};"></div>
    </div>
    <div style="text-align: right; font-size: 0.85rem; color: {habit_color}; font-weight: bold;">{percentage:.0f}%</div>
    '''
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
    
    with col3:
        st.write(f"👋 **{st.session_state.username}**")
        if st.button("🚪 Logout", use_container_width=True, key="logout_main"):
            logout_user()
            st.rerun()
    
    # Get user's habits
    user_id = st.session_state.user_id
    habits = get_all_habits(user_id)
    
    # Stats Bar
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f'''
        <div class="stat-box">
            <div style="font-size: 1.8rem; font-weight: bold; color: #a78bfa;">📊</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: white;">{len(habits)}</div>
            <div style="font-size: 0.7rem; color: #8a8a9e; text-transform: uppercase; letter-spacing: 1px;">Total Habits</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        done_today = sum(1 for h in habits if is_completed_today(h["id"]))
        st.markdown(f'''
        <div class="stat-box">
            <div style="font-size: 1.8rem; font-weight: bold; color: #34d399;">✅</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: white;">{done_today}</div>
            <div style="font-size: 0.7rem; color: #8a8a9e; text-transform: uppercase; letter-spacing: 1px;">Done Today</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        avg_streak = sum(get_streak(h["id"]) for h in habits) / len(habits) if habits else 0
        st.markdown(f'''
        <div class="stat-box">
            <div style="font-size: 1.8rem; font-weight: bold; color: #f87171;">🔥</div>
            <div style="font-size: 1.5rem; font-weight: bold; color: white;">{avg_streak:.1f}</div>
            <div style="font-size: 0.7rem; color: #8a8a9e; text-transform: uppercase; letter-spacing: 1px;">Avg Streak</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        if st.button("➕ Add Habit", use_container_width=True, key="add_habit_btn"):
            st.session_state.show_add_habit = not st.session_state.show_add_habit
            st.rerun()
    
    st.markdown("---")
    
    # Main Content Area - Sidebar + Habits
    main_col1, main_col2 = st.columns([1, 2.5], gap="medium")
    
    # LEFT SIDEBAR - Add Habit Form
    with main_col1:
        if st.session_state.show_add_habit:
            st.markdown("## ✨ New Habit")
            
            habit_name = st.text_input("HABIT NAME", placeholder="e.g., Morning Run", key="habit_name_input", label_visibility="collapsed")
            habit_desc = st.text_area("DESCRIPTION (OPTIONAL)", placeholder="e.g., Run 5km every morning", height=60, key="habit_desc_input", label_visibility="collapsed")
            
            st.markdown("**PICK A COLOR**")
            
            # Preset color buttons
            color_cols = st.columns(6)
            preset_colors = ["#a78bfa", "#34d399", "#60a5fa", "#f97316", "#ec4899", "#eab308"]
            selected_color = "#a78bfa"
            
            for idx, col in enumerate(color_cols):
                with col:
                    if st.button("", key=f"color_{idx}", use_container_width=True):
                        selected_color = preset_colors[idx]
            
            # Custom color picker
            habit_color = st.color_picker("Pick Custom Color", "#a78bfa", key="habit_color_input", label_visibility="collapsed")
            
            # Hex display
            st.markdown(f'<div style="text-align: center; padding: 10px; background-color: #0a0a0f; border: 1px solid #2a2a3e; border-radius: 6px; font-family: monospace; color: #a78bfa; font-weight: bold;">{habit_color.upper()}</div>', unsafe_allow_html=True)
            st.caption("HEX")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Cancel", use_container_width=True, key="cancel_habit"):
                    st.session_state.show_add_habit = False
                    st.rerun()
            
            with col2:
                if st.button("Add Habit ✓", use_container_width=True, key="submit_habit"):
                    if habit_name.strip():
                        add_habit(user_id, habit_name, habit_desc, habit_color)
                        st.session_state.show_add_habit = False
                        st.success("Habit added!")
                        st.rerun()
                    else:
                        st.error("Please enter a habit name.")
    
    # RIGHT SIDE - Habit Cards
    with main_col2:
        if habits:
            st.markdown("## 📋 Your Habits")
            
            for idx, habit in enumerate(habits):
                habit_id = habit["id"]
                streak = get_streak(habit_id)
                rate = get_completion_rate(habit_id)
                done_today = is_completed_today(habit_id)
                
                # Habit Card
                st.markdown(f'''
                <div class="habit-card" style="border-left-color: {habit['color']};">
                ''', unsafe_allow_html=True)
                
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### {habit['name']}")
                    if habit['description']:
                        st.caption(habit['description'])
                
                with col2:
                    if st.button("✓ Done", key=f"done_{habit_id}", use_container_width=True):
                        toggle_log(habit_id, date.today())
                        st.rerun()
                    
                    if st.button("✕", key=f"close_{habit_id}", use_container_width=True):
                        if st.button("Confirm Delete", key=f"confirm_delete_{habit_id}"):
                            delete_habit(habit_id, user_id)
                            st.rerun()
                
                # Streak and Rate info
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"🔥 **{streak}** day streak")
                with col2:
                    st.markdown(f"📊 **{rate:.0f}%** 30-day rate")
                
                # 30-day grid with numbers
                st.markdown("#### Last 30 Days")
                st.markdown(render_30_day_grid(habit_id, habit['color']), unsafe_allow_html=True)
                
                # Progress bar
                st.markdown("#### 30-day progress")
                st.markdown(render_progress_bar(habit_id, habit['color']), unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("")
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
