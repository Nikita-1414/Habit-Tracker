import streamlit as st
import sqlite3
from datetime import date, timedelta
import bcrypt
from database import (
    init_db, add_habit, delete_habit, get_all_habits, toggle_log,
    get_streak, get_completion_rate, get_last_7_days_status,
    is_completed_today, create_user, get_user_by_email
)

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Habit Tracker",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

init_db()

# ─────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #0a0a0f; color: #f0f0f5; }
    .main { background: #0a0a0f; }
    
    .header-section {
        text-align: center;
        margin-bottom: 40px;
        padding: 20px;
    }
    
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 8px;
    }
    
    .header-title .accent {
        color: #a78bfa;
    }
    
    .header-date {
        color: #6b6b80;
        font-size: 0.95rem;
    }
    
    .stats-row {
        display: flex;
        gap: 20px;
        justify-content: center;
        margin-bottom: 40px;
        flex-wrap: wrap;
    }
    
    .stat-box {
        background: #1a1a27;
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 12px;
        padding: 20px 30px;
        min-width: 120px;
        text-align: center;
    }
    
    .stat-number {
        font-size: 2.2rem;
        font-weight: 800;
        color: #a78bfa;
        margin-bottom: 4px;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #6b6b80;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    .habits-container {
        max-width: 1100px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    .habit-card {
        background: #1a1a27;
        border-left: 5px solid #a78bfa;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
    }
    
    .habit-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
    }
    
    .habit-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #f0f0f5;
        margin-bottom: 4px;
    }
    
    .habit-desc {
        font-size: 0.85rem;
        color: #6b6b80;
    }
    
    .habit-meta {
        display: flex;
        gap: 20px;
        margin-bottom: 16px;
        font-size: 0.9rem;
    }
    
    .meta-value {
        font-weight: 700;
        color: #a78bfa;
    }
    
    .days-row {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        margin-bottom: 8px;
    }
    
    .day-label {
        flex: 1;
        text-align: center;
        font-size: 0.75rem;
        color: #6b6b80;
        font-weight: 600;
    }
    
    .week-circles {
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
    }
    
    .day-circle {
        flex: 1;
        aspect-ratio: 1;
        border-radius: 50%;
        background: #2a2a3a;
        border: 2px solid #3a3a4a;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        color: #6b6b80;
        font-size: 0.8rem;
    }
    
    .day-circle.completed {
        color: white;
        border: none;
    }
    
    .progress-section {
        border-top: 1px solid rgba(255,255,255,0.05);
        padding-top: 12px;
        margin-top: 12px;
    }
    
    .progress-text {
        font-size: 0.8rem;
        color: #6b6b80;
        margin-bottom: 8px;
        cursor: pointer;
    }
    
    .progress-bar {
        display: flex;
        gap: 8px;
        align-items: center;
    }
    
    .progress-fill {
        flex: 1;
        height: 6px;
        background: #2a2a3a;
        border-radius: 3px;
        overflow: hidden;
    }
    
    .progress-percent {
        font-size: 0.85rem;
        font-weight: 700;
        min-width: 40px;
        text-align: right;
    }
    
    .done-btn {
        position: absolute;
        top: 20px;
        right: 20px;
        background: #a78bfa;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        font-size: 0.9rem;
    }
    
    .close-btn {
        position: absolute;
        top: 20px;
        right: 80px;
        background: transparent;
        color: #6b6b80;
        border: none;
        font-size: 1.2rem;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SESSION STATE
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
def get_30_day_status(habit_id):
    """Get 30-day completion status"""
    conn = sqlite3.connect("habits.db")
    conn.row_factory = sqlite3.Row
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
# AUTH FUNCTIONS
# ─────────────────────────────────────────────────────────────
def register_user(username, email, password, confirm_password):
    if not username or not email or not password:
        st.error("All fields required")
        return False
    if password != confirm_password:
        st.error("Passwords don't match")
        return False
    if len(password) < 6:
        st.error("Password must be 6+ characters")
        return False
    
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    if create_user(username, email.lower(), hashed):
        st.success("Account created! Login now.")
        st.session_state.page = "login"
        return True
    else:
        st.error("Email/username already exists")
        return False

def login_user(email, password):
    user = get_user_by_email(email.lower())
    if user and bcrypt.checkpw(password.encode(), user["password"].encode()):
        st.session_state.user_id = user["id"]
        st.session_state.username = user["username"]
        st.session_state.page = "dashboard"
        return True
    else:
        st.error("Invalid email or password")
        return False

def logout_user():
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.page = "login"

# ─────────────────────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────────────────────
def show_login_page():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.title("🎯 Habit Tracker")
        st.write("Welcome back!")
        
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Login", use_container_width=True):
                    if login_user(email, password):
                        st.rerun()
            with col2:
                if st.form_submit_button("Register", use_container_width=True):
                    st.session_state.page = "register"
                    st.rerun()

def show_register_page():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.title("📝 Register")
        st.write("Create a new account")
        
        with st.form("register_form"):
            username = st.text_input("Username")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Register", use_container_width=True):
                    if register_user(username, email, password, confirm):
                        st.rerun()
            with col2:
                if st.form_submit_button("Back", use_container_width=True):
                    st.session_state.page = "login"
                    st.rerun()

def show_dashboard_page():
    user_id = st.session_state.user_id
    habits = get_all_habits(user_id)
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 0.2])
    with col1:
        if st.button("👤", help="Logout"):
            logout_user()
            st.rerun()
    with col2:
        st.markdown(f"""
        <div class='header-section'>
            <div class='header-title'>Habit <span class='accent'>Tracker</span></div>
            <div class='header-date'>📅 {date.today().strftime('%B %d, %Y')}</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        if st.button("➕", help="Add Habit"):
            st.session_state.show_add_habit = not st.session_state.show_add_habit
            st.rerun()
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-number'>{len(habits)}</div>
            <div class='stat-label'>Total Habits</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        done = sum(1 for h in habits if is_completed_today(h["id"]))
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-number'>{done}</div>
            <div class='stat-label'>Done Today</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg = sum(get_streak(h["id"]) for h in habits) / len(habits) if habits else 0
        st.markdown(f"""
        <div class='stat-box'>
            <div class='stat-number'>{avg:.1f}</div>
            <div class='stat-label'>Avg Streak 🔥</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("")
    
    # Add Habit Modal
    if st.session_state.show_add_habit:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### ✨ New Habit")
            with st.form("add_habit_form"):
                habit_name = st.text_input("Habit Name", placeholder="e.g., Morning Run")
                habit_desc = st.text_area("Description", placeholder="e.g., Run 5km every morning", height=60)
                
                st.markdown("**PICK A COLOR**")
                colors = ["#a78bfa", "#34d399", "#60a5fa", "#f97316", "#ec4899", "#fbbf24"]
                color_cols = st.columns(6)
                selected_color = colors[0]
                
                for i, (col, color) in enumerate(zip(color_cols, colors)):
                    with col:
                        if st.button("●", key=f"color_{i}"):
                            st.session_state.selected_color = color
                
                selected_color = st.session_state.get("selected_color", colors[0])
                
                col1, col2 = st.columns(2)
                with col1:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)
                with col2:
                    submit = st.form_submit_button("✓ Add Habit", use_container_width=True)
                
                if cancel:
                    st.session_state.show_add_habit = False
                    st.rerun()
                
                if submit:
                    if habit_name.strip():
                        add_habit(user_id, habit_name, habit_desc, selected_color)
                        st.session_state.show_add_habit = False
                        st.success("Habit added!")
                        st.rerun()
                    else:
                        st.error("Enter habit name")
    
    st.write("")
    
    # Habits List
    if habits:
        st.markdown("<div class='habits-container'>", unsafe_allow_html=True)
        
        for habit in habits:
            hid = habit["id"]
            streak = get_streak(hid)
            rate = get_completion_rate(hid)
            done_today = is_completed_today(hid)
            week = get_last_7_days_status(hid)
            
            col1, col2 = st.columns([0.8, 0.2])
            
            with col1:
                # Day labels
                day_labels = ["SAT", "SUN", "MON", "TUE", "WED", "THU", "FRI"]
                days_html = '<div class="days-row">'
                for label in day_labels:
                    days_html += f'<div class="day-label">{label}</div>'
                days_html += '</div>'
                
                # Day circles
                week_html = '<div class="week-circles">'
                for status, label in zip(week, day_labels):
                    completed = "completed" if status else ""
                    style = f"background-color: {habit['color']};" if status else ""
                    symbol = "✓" if status else ""
                    week_html += f'<div class="day-circle {completed}" style="{style}">{symbol}</div>'
                week_html += '</div>'
                
                # Progress
                progress_html = f"""
                <div class="progress-bar">
                    <div class="progress-fill">
                        <div style="width: {rate:.0f}%; height: 100%; background-color: {habit['color']};"></div>
                    </div>
                    <div class="progress-percent" style="color: {habit['color']};">{rate:.0f}%</div>
                </div>
                """
                
                card_html = f"""
                <div class="habit-card" style="border-left-color: {habit['color']};">
                    <div class="done-btn" style="background-color: {habit['color']};">✓ Done</div>
                    <button class="close-btn">✕</button>
                    
                    <div class="habit-header">
                        <div>
                            <div class="habit-title">{habit['name']}</div>
                            <div class="habit-desc">{habit['description']}</div>
                        </div>
                    </div>
                    
                    <div class="habit-meta">
                        <div>🔥 <span class="meta-value">{streak}</span> day streak</div>
                        <div>📊 <span class="meta-value">{rate:.0f}%</span> 30-day rate</div>
                    </div>
                    
                    {days_html}
                    {week_html}
                    
                    <div class="progress-section">
                        <div class="progress-text">▸ Show 30-day progress</div>
                        {progress_html}
                    </div>
                </div>
                """
                
                st.markdown(card_html, unsafe_allow_html=True)
            
            with col2:
                if st.button("✓", key=f"done_{hid}", help="Mark Done"):
                    toggle_log(hid, date.today())
                    st.rerun()
                if st.button("✕", key=f"delete_{hid}", help="Delete"):
                    delete_habit(hid, user_id)
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("📌 No habits yet! Click ➕ to add one.")

# ─────────────────────────────────────────────────────────────
# MAIN
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
