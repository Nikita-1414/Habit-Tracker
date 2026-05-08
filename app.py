import streamlit as st
import sqlite3
from datetime import datetime, date, timedelta
import bcrypt
import calendar
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
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize database
try:
    init_db()
except Exception as e:
    st.error(f"Database initialization error: {e}")

# ─────────────────────────────────────────────────────────────
# CUSTOM STYLING - EXACT DESIGN MATCH
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    :root {
        --bg: #0a0a0f;
        --surface: #13131a;
        --surface2: #1c1c27;
        --border: rgba(255,255,255,0.07);
        --text: #f0f0f5;
        --muted: #6b6b80;
        --accent: #a78bfa;
        --success: #34d399;
        --danger: #f87171;
    }
    
    body, .main {
        background: var(--bg) !important;
        color: var(--text) !important;
    }
    
    /* Header */
    .header-box {
        text-align: center;
        margin-bottom: 32px;
        padding: 0 20px;
    }
    
    .header-box h1 {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0 0 8px 0;
    }
    
    .header-title {
        color: var(--text);
    }
    
    .header-title-accent {
        color: var(--accent);
    }
    
    .header-date {
        color: var(--muted);
        font-size: 0.9rem;
    }
    
    /* Add Habit Button Container */
    .add-btn-container {
        text-align: right;
        margin-bottom: 24px;
        padding: 0 20px;
    }
    
    /* Stats container */
    .stats-container {
        display: flex;
        gap: 16px;
        margin-bottom: 40px;
        justify-content: center;
        padding: 0 20px;
        flex-wrap: wrap;
    }
    
    .stat-box {
        background: rgba(30, 30, 45, 0.8);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 24px 32px;
        text-align: center;
        flex: 1;
        min-width: 200px;
    }
    
    .stat-number {
        font-size: 2.4rem;
        font-weight: 800;
        color: var(--accent);
        margin-bottom: 8px;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Habit card */
    .habit-card {
        background: rgba(30, 30, 45, 0.6);
        border-left: 5px solid;
        border-radius: 12px;
        padding: 24px;
        margin: 0 20px 16px 20px;
        border: 1px solid rgba(255,255,255,0.05);
    }
    
    .habit-header-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }
    
    .habit-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: var(--text);
        margin-bottom: 4px;
    }
    
    .habit-desc {
        font-size: 0.85rem;
        color: var(--muted);
    }
    
    .habit-meta {
        display: flex;
        gap: 16px;
        margin-bottom: 16px;
        font-size: 0.9rem;
    }
    
    .meta-item {
        display: flex;
        align-items: center;
        gap: 6px;
        color: var(--muted);
    }
    
    .meta-value {
        color: var(--text);
        font-weight: 600;
    }
    
    /* Day labels */
    .day-labels {
        display: flex;
        justify-content: space-around;
        gap: 8px;
        margin-bottom: 8px;
        font-size: 0.65rem;
        color: var(--muted);
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    /* Week circles */
    .week-circles {
        display: flex;
        justify-content: space-around;
        gap: 8px;
        margin-bottom: 16px;
        padding-bottom: 12px;
    }
    
    .day-circle {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: rgba(255,255,255,0.07);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--muted);
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid transparent;
    }
    
    .day-circle.completed {
        border: none;
        color: white;
        font-weight: bold;
    }
    
    /* Progress section */
    .progress-section {
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    
    .progress-toggle {
        font-size: 0.85rem;
        color: var(--muted);
        cursor: pointer;
        margin-bottom: 12px;
    }
    
    .progress-bar-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
    }
    
    .progress-bar-bg {
        flex: 1;
        height: 18px;
        background: rgba(255,255,255,0.03);
        border-radius: 3px;
        overflow: hidden;
    }
    
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--accent), var(--success));
        transition: width 0.3s ease;
    }
    
    .progress-percent {
        font-size: 0.85rem;
        color: var(--accent);
        font-weight: 700;
        min-width: 45px;
        text-align: right;
    }
    
    /* Buttons */
    .habit-buttons {
        display: flex;
        gap: 12px;
        margin-top: 16px;
    }
    
    .btn-done {
        flex: 1;
        padding: 10px 16px;
        background: var(--accent);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s;
    }
    
    .btn-done:hover {
        opacity: 0.9;
    }
    
    .btn-close {
        background: transparent;
        border: none;
        color: var(--muted);
        cursor: pointer;
        font-size: 1.4rem;
        padding: 0 4px;
        transition: color 0.2s;
    }
    
    .btn-close:hover {
        color: var(--text);
    }
    
    /* Styed color picker buttons */
    .stButton > button {
        background-color: var(--accent) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.2s !important;
    }
    
    .stButton > button:hover {
        opacity: 0.9 !important;
    }
    
    /* Text inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: rgba(255,255,255,0.05) !important;
        color: var(--text) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        font-size: 0.9rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent) !important;
        background-color: rgba(167,139,250,0.1) !important;
    }
    
    /* Color picker */
    .stColorPicker {
        margin: 12px 0;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .header-box h1 {
            font-size: 2rem;
        }
        
        .stat-box {
            min-width: 100%;
            padding: 16px;
        }
        
        .stats-container {
            flex-direction: column;
        }
        
        .day-circle {
            width: 28px;
            height: 28px;
            font-size: 0.65rem;
        }
        
        .habit-card {
            margin: 0 16px 16px 16px;
            padding: 16px;
        }
        
        .habit-meta {
            gap: 12px;
            font-size: 0.85rem;
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
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────
def get_7_day_status(habit_id):
    """Get last 7 days status for a habit"""
    conn = sqlite3.connect("habits.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    
    status = []
    for i in range(6, -1, -1):
        check_date = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        result = cursor.execute(
            "SELECT completed FROM logs WHERE habit_id = ? AND log_date = ?",
            (habit_id, check_date)
        ).fetchone()
        status.append(bool(result["completed"]) if result else False)
    
    conn.close()
    return status

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
    st.markdown("<h1 style='text-align: center;'>📝 Register</h1>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        username = st.text_input("Username", placeholder="Enter your username")
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="At least 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Create Account", use_container_width=True):
                if register_user(username, email, password, confirm_password):
                    st.rerun()
        
        with col_btn2:
            if st.button("Back to Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()

# ─────────────────────────────────────────────────────────────
# PAGE: LOGIN
# ─────────────────────────────────────────────────────────────
def show_login_page():
    st.markdown("<h1 style='text-align: center;'>🎯 Habit Tracker</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b6b80;'>Welcome back</p>", unsafe_allow_html=True)
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        email = st.text_input("Email", placeholder="Enter your email")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Login", use_container_width=True):
                if login_user(email, password):
                    st.rerun()
        
        with col_btn2:
            if st.button("Create Account", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

# ─────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────────
def show_dashboard_page():
    # Header
    st.markdown("""
    <div class='header-box'>
        <h1><span class='header-title'>Habit</span> <span class='header-title-accent'>Tracker</span></h1>
        <div class='header-date'>📅 """ + date.today().strftime("%B %d, %Y") + """</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Top right button
    col1, col2, col3 = st.columns([1, 1, 0.3])
    with col3:
        logout_col1, logout_col2 = st.columns([1, 1])
        with logout_col2:
            if st.button("🚪", key="logout_btn", help="Logout"):
                logout_user()
                st.rerun()
    
    # Get user's habits
    user_id = st.session_state.user_id
    habits = get_all_habits(user_id)
    
    # Stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='stat-box'>
            <div class='stat-number'>""" + str(len(habits)) + """</div>
            <div class='stat-label'>Total Habits</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        done_today = sum(1 for h in habits if is_completed_today(h["id"]))
        st.markdown("""
        <div class='stat-box'>
            <div class='stat-number'>""" + str(done_today) + """</div>
            <div class='stat-label'>Done Today</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_streak = sum(get_streak(h["id"]) for h in habits) / len(habits) if habits else 0
        st.markdown("""
        <div class='stat-box'>
            <div class='stat-number'>""" + f"{avg_streak:.1f}" + """</div>
            <div class='stat-label'>Avg Streak 🔥</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    # Add Habit Button
    col1, col2, col3 = st.columns([1, 1, 0.2])
    with col3:
        if st.button("➕ Add Habit", use_container_width=False):
            st.session_state.show_add_habit = True
            st.rerun()
    
    # Add Habit Modal
    if st.session_state.show_add_habit:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<h3 style='text-align: center; margin-bottom: 24px;'>✨ New Habit</h3>", unsafe_allow_html=True)
            
            with st.form("add_habit_form", clear_on_submit=False):
                habit_name = st.text_input("Habit Name", placeholder="e.g., Morning Run")
                habit_desc = st.text_area("Description", placeholder="e.g., Run 5km every morning", height=80)
                
                st.markdown("<p style='color: #6b6b80; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; margin: 16px 0 8px 0; font-weight: 600;'>PICK A COLOR</p>", unsafe_allow_html=True)
                
                # Preset colors
                colors = ["#a78bfa", "#34d399", "#60a5fa", "#f97316", "#ec4899", "#fbbf24"]
                color_names = ["Purple", "Green", "Blue", "Orange", "Pink", "Yellow"]
                
                selected_color = st.session_state.get("selected_habit_color", colors[0])
                
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                color_cols = [col1, col2, col3, col4, col5, col6]
                
                for i, (color, name) in enumerate(zip(colors, color_names)):
                    with color_cols[i]:
                        if st.button("●", key=f"color_{color}", help=name):
                            st.session_state.selected_habit_color = color
                            selected_color = color
                
                st.write("")
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.form_submit_button("Cancel", use_container_width=True):
                        st.session_state.show_add_habit = False
                        st.rerun()
                
                with col_btn2:
                    if st.form_submit_button("✓ Add Habit", use_container_width=True):
                        if habit_name.strip():
                            add_habit(user_id, habit_name, habit_desc, selected_color)
                            st.session_state.show_add_habit = False
                            st.success("Habit added!")
                            st.rerun()
                        else:
                            st.error("Please enter a habit name.")
    
    st.write("")
    st.write("")
    
    # Display Habits
    if habits:
        for habit in habits:
            habit_id = habit["id"]
            streak = get_streak(habit_id)
            rate = get_completion_rate(habit_id)
            done_today = is_completed_today(habit_id)
            week_status = get_7_day_status(habit_id)
            
            # Habit Card
            habit_html = f"""
            <div class='habit-card' style='border-left-color: {habit["color"]};'>
                <div class='habit-header-top'>
                    <div>
                        <div class='habit-title'>{habit['name']}</div>
                        <div class='habit-desc'>{habit['description'] if habit['description'] else ''}</div>
                    </div>
                </div>
                
                <div class='habit-meta'>
                    <div class='meta-item'>🔥 <span class='meta-value'>{streak}</span> day streak</div>
                    <div class='meta-item'>📊 <span class='meta-value'>{rate:.0f}%</span> 30-day rate</div>
                </div>
                
                <div class='day-labels'>
                    <div>SAT</div>
                    <div>SUN</div>
                    <div>MON</div>
                    <div>TUE</div>
                    <div>WED</div>
                    <div>THU</div>
                    <div>FRI</div>
                </div>
                
                <div class='week-circles'>
            """
            
            # Add day circles
            day_names_short = ['SAT', 'SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI']
            for i, (status, day_name) in enumerate(zip(week_status, day_names_short)):
                completed_class = "completed" if status else ""
                completed_style = f"background-color: {habit['color']};" if status else ""
                symbol = "✓" if status else ""
                habit_html += f"""
                    <div class='day-circle {completed_class}' style='{completed_style}'>{symbol}</div>
                """
            
            habit_html += """
                </div>
                
                <div class='progress-section'>
                    <div class='progress-toggle' onclick="toggleProgressChart('{habit_id}')">
                        ▸ Show 30-day progress
                    </div>
                    <div class='progress-bar-container'>
                        <div class='progress-bar-bg'>
                            <div class='progress-bar-fill' style='width: {rate:.0f}%; background-color: {color};'></div>
                        </div>
                        <div class='progress-percent'>{rate:.0f}%</div>
                    </div>
                </div>
                
                <div class='habit-buttons'>
                    <button class='btn-done' style='background-color: {color};'>✓ Done</button>
                    <button class='btn-close'>✕</button>
                </div>
            </div>
            """.format(
                habit_id=habit_id,
                rate=rate,
                color=habit["color"]
            )
            
            st.markdown(habit_html, unsafe_allow_html=True)
            
            # Action buttons below card
            col1, col2, col3 = st.columns([1, 1, 0.5])
            with col1:
                if st.button("✓ Mark Done", key=f"done_{habit_id}", use_container_width=True):
                    toggle_log(habit_id, date.today())
                    st.rerun()
            
            with col2:
                if st.button("Mark Not Done", key=f"undo_{habit_id}", use_container_width=True):
                    toggle_log(habit_id, date.today())
                    st.rerun()
            
            with col3:
                if st.button("🗑", key=f"delete_{habit_id}", use_container_width=True):
                    delete_habit(habit_id, user_id)
                    st.rerun()
            
            st.write("")
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
