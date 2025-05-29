import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import pytz
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# --- Global Configuration & Constants ---
TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError: st.error(f"Invalid TZ: {TARGET_TIMEZONE}"); st.stop()

ATTENDANCE_FILE = "attendance.csv"; ALLOWANCE_FILE = "allowances.csv"; GOALS_FILE = "goals.csv";
PAYMENT_GOALS_FILE = "payment_goals.csv"; ACTIVITY_LOG_FILE = "activity_log.csv";
ACTIVITY_PHOTOS_DIR = "activity_photos"
if not os.path.exists(ACTIVITY_PHOTOS_DIR): os.makedirs(ACTIVITY_PHOTOS_DIR, exist_ok=True)

def get_current_time_in_tz(): return datetime.now(timezone.utc).astimezone(tz)
def get_quarter_str_for_year(year):
    m = get_current_time_in_tz().month
    if 1<=m<=3: return f"{year}-Q1"; elif 4<=m<=6: return f"{year}-Q2";
    elif 7<=m<=9: return f"{year}-Q3"; else: return f"{year}-Q4"

def load_data(path, columns):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        try:
            df = pd.read_csv(path)
            for col in columns:
                if col not in df.columns: df[col] = pd.NA
            num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude"]
            for nc in num_cols:
                if nc in df.columns: df[nc] = pd.to_numeric(df[nc], errors='coerce')
            return df
        except Exception: return pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
        try: df.to_csv(path, index=False)
        except Exception: pass
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]

attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
activity_log_df = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS)

USERS = { "admin": {"password": "admin123", "role": "admin", "position": "System Administrator", "profile_photo": "images/admin.png"},
    # Add other users here if they have profile photos or specific positions needed before login
    "Geetali": {"password": "Geetali123", "role": "employee", "position": "Software Engineer", "profile_photo": "images/geetali.png"},
    "Nilesh": {"password": "Nilesh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"}
}
if not os.path.exists("images"): os.makedirs("images", exist_ok=True)
if PILLOW_INSTALLED:
    for user_key, user_data in USERS.items():
        img_path = user_data.get("profile_photo")
        if img_path and not os.path.exists(img_path):
            try: # Simplified placeholder
                img = Image.new('RGB', (60, 60), color = (200, 200, 200)); img.save(img_path)
            except: pass


# --- NEW CSS FOR GOOGLE AI STUDIO LOOK (SIMPLIFIED HTML APPROACH) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    /* --- BASE & FONT --- */
    body, .stButton button, .stTextInput input, .stTextArea textarea, .stSelectbox select, p, div, span {
        font-family: 'Roboto', sans-serif !important;
    }
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined' !important;
        font-weight: normal !important; font-style: normal !important;
        font-size: 20px !important; /* Icon size */
        line-height: 1 !important; letter-spacing: normal !important;
        text-transform: none !important; display: inline-block !important;
        white-space: nowrap !important; word-wrap: normal !important;
        direction: ltr !important; -webkit-font-smoothing: antialiased !important;
        text-rendering: optimizeLegibility !important; -moz-osx-font-smoothing: grayscale !important;
        font-feature-settings: 'liga' !important;
        vertical-align: -0.1em !important; /* Fine-tune alignment */
        margin-right: 12px !important; /* Space after icon */
    }

    /* --- SIDEBAR --- */
    section[data-testid="stSidebar"] > div:first-child {
        padding: 0px !important;
        background-color: #131314 !important; /* AI Studio very dark gray */
    }
    .sidebar-content-wrapper {
        background-color: #131314 !important;
        color: #e8eaed !important;
        height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        padding: 12px !important; /* Overall sidebar padding */
        box-sizing: border-box !important;
    }

    /* User Info Area in Sidebar */
    .sidebar-user-info {
        padding: 8px;
        margin-bottom: 12px; /* Space after user info block */
    }
    .welcome-text-sidebar {
        font-size: 0.9rem !important; /* Smaller welcome */
        font-weight: 400 !important;
        color: #bdc1c6 !important; /* Lighter gray */
        margin-bottom: 8px !important;
        padding-left: 4px; /* Align with nav items a bit */
    }
    .user-profile-img-container {
        text-align: left !important; /* Align image to left */
        margin-bottom: 4px !important;
        padding-left: 4px;
    }
    .user-profile-img-container img {
        border-radius: 50% !important;
        width: 32px !important; /* Smaller profile image */
        height: 32px !important;
        object-fit: cover !important;
        border: 1px solid #5f6368 !important; /* Subtle border */
        vertical-align: middle;
    }
    .user-position-text {
        font-size: 0.75rem !important;
        color: #9aa0a6 !important; /* Subdued position text */
        padding-left: 4px;
        margin-top: -2px; /* Pull up slightly */
    }
    .sidebar-content-wrapper hr {
        margin: 12px 0px !important; /* Reduced margin for HR */
        border: none !important;
        border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Navigation Buttons (st.button directly) */
    .stButton > button { /* General button reset for sidebar nav */
        display: flex !important;
        align-items: center !important;
        text-align: left !important;
        width: 100% !important;
        padding: 8px 10px !important; /* Nav item padding */
        margin-bottom: 4px !important; /* Space between items */
        border: none !important;
        border-radius: 6px !important;
        background-color: transparent !important;
        color: #e0e0e0 !important; /* Default nav text color (light gray) */
        font-weight: 400 !important;
        font-size: 0.875rem !important; /* Nav text size */
        line-height: 1.5 !important;
        transition: background-color 0.15s ease-in-out, color 0.15s ease-in-out !important;
        box-shadow: none !important;
        outline: none !important;
        cursor: pointer !important;
    }
    /* Specific styling for icons inside these buttons */
    .stButton > button .material-symbols-outlined {
        color: #9aa0a6 !important; /* Default icon color */
        font-size: 18px !important; /* Slightly smaller icon */
    }

    .stButton > button:hover {
        background-color: rgba(255, 255, 255, 0.08) !important; /* Subtle whiteish hover */
        color: #ffffff !important; /* Brighter text on hover */
    }
    .stButton > button:hover .material-symbols-outlined {
        color: #ffffff !important;
    }

    /* Active Navigation Button Styling */
    /* We need a way to identify the active button's wrapper if st.button is used directly */
    /* This assumes a div with class 'active-nav-item' wraps the active st.button */
    div.active-nav-item > .stButton > button {
        background-color: rgba(138, 180, 248, 0.16) !important; /* Google Blue accent with low opacity */
        color: #8ab4f8 !important; /* Active item text color */
        font-weight: 500 !important;
    }
    div.active-nav-item > .stButton > button .material-symbols-outlined {
        color: #8ab4f8 !important; /* Active icon color */
    }

    /* Logout Button specific styling (if different from regular nav) */
    .logout-button-container .stButton > button {
        margin-top: auto; /* Pushes to bottom if container is flex */
        /* Add any specific logout styles here, e.g., border or different hover */
    }
     .logout-button-container {
        margin-top: auto;
        padding-top: 1rem;
    }


    /* --- Main Content & Notifications --- */
    div[data-testid="stAppViewContainer"] > .main { background-color: #ffffff !important; color: #202124; } /* White main bg */
    .card { background-color: #ffffff; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border: 1px solid #e0e0e0; box-shadow: 0 1px 2px rgba(0,0,0,0.07); }
    .custom-notification { padding: 1rem; border-radius: 6px; margin-bottom: 1rem; border: 1px solid transparent; font-size: 0.9rem; }
    .custom-notification.success { color: #155724; background-color: #d4edda; border-color: #c3e6cb; }
    .custom-notification.error { color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; }
    .custom-notification.info { color: #0c5460; background-color: #d1ecf1; border-color: #bee5eb; }
    .custom-notification.warning { color: #856404; background-color: #fff3cd; border-color: #ffeeba; }
    .button-column-container .stButton button { width: 100%; }
    .employee-progress-item h6 { margin-bottom: 0.25rem; font-size: 1rem; color: #202124; }
    .employee-progress-item p { font-size: 0.85rem; color: #5f6368; margin-bottom: 0.5rem; }

</style>
""", unsafe_allow_html=True)


# --- SESSION STATE & NAVIGATION ---
if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}

NAV_OPTIONS_WITH_ICONS = [
    {"label": "Attendance", "icon": "schedule", "key": "nav_attendance"},
    {"label": "Upload Activity Photo", "icon": "add_a_photo", "key": "nav_upload"},
    {"label": "Allowance", "icon": "payments", "key": "nav_allowance"},
    {"label": "Goal Tracker", "icon": "emoji_events", "key": "nav_goal"},
    {"label": "Payment Collection Tracker", "icon": "receipt_long", "key": "nav_payment"},
    {"label": "View Logs", "icon": "wysiwyg", "key": "nav_logs"},
    {"label": "Create Order", "icon": "add_shopping_cart", "key": "nav_order"}
]
if "active_page" not in st.session_state:
    st.session_state.active_page = NAV_OPTIONS_WITH_ICONS[0]["label"]


# --- PLOTTING FUNCTIONS (Keep as they were or theme them too) ---
# (Your plotting functions: render_goal_chart, create_donut_chart, create_team_progress_bar_chart)
# ... (plotting functions from your previous full code) ...
def render_goal_chart(df: pd.DataFrame, chart_title: str): # Defined earlier, keep as is
    if df.empty: st.warning("No data available to plot."); return
    df_chart = df.copy(); df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear", value_vars=["TargetAmount", "AchievedAmount"], var_name="Metric", value_name="Amount")
    if df_melted.empty: st.warning(f"No data to plot for {chart_title} after processing."); return
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group", labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"}, title=chart_title, color_discrete_map={'TargetAmount': '#8ab4f8', 'AchievedAmount': '#34A853'}) # Google Blue/Green
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#e0e0e0')
    fig.update_xaxes(showgrid=False, zeroline=False, color='#9aa0a6'); fig.update_yaxes(showgrid=True, gridcolor='rgba(255,255,255,0.1)', zeroline=False, color='#9aa0a6')
    st.plotly_chart(fig, use_container_width=True)

def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#8ab4f8', remaining_color='rgba(255,255,255,0.05)', center_text_color='#e8eaed'):
    fig, ax = plt.subplots(figsize=(2.2, 2.2), dpi=110); fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    progress_percentage = max(0.0, min(float(progress_percentage), 100.0)); remaining_percentage = 100.0 - progress_percentage
    if progress_percentage <= 0.01: sizes = [100.0]; slice_colors = [remaining_color]; actual_progress_display = 0.0
    elif progress_percentage >= 99.99: sizes = [100.0]; slice_colors = [achieved_color]; actual_progress_display = 100.0
    else: sizes = [progress_percentage, remaining_percentage]; slice_colors = [achieved_color, remaining_color]; actual_progress_display = progress_percentage
    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.35, edgecolor='#131314'))
    centre_circle = plt.Circle((0,0),0.65,fc='#131314'); fig.gca().add_artist(centre_circle)
    text_color_to_use = center_text_color if actual_progress_display > 0 else '#9aa0a6'
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=10, fontweight='bold', color=text_color_to_use)
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0); return fig

def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee"):
    if summary_df.empty: return None
    labels = summary_df[user_col].tolist(); target_amounts = summary_df[target_col].fillna(0).tolist(); achieved_amounts = summary_df[achieved_col].fillna(0).tolist()
    x = np.arange(len(labels)); width = 0.35
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.7), 4.5), dpi=110, facecolor='rgba(0,0,0,0)'); ax.set_facecolor('rgba(0,0,0,0)')
    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color='rgba(138, 180, 248, 0.7)'); rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color='rgba(52, 168, 83, 0.7)')
    ax.set_ylabel('Amount (INR)', fontsize=9, color='#dadce0'); ax.set_title(title, fontsize=11, fontweight='bold', pad=12, color='#e8eaed')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8, color='#dadce0')
    legend = ax.legend(fontsize=8, facecolor='rgba(40,42,45,0.8)', edgecolor='rgba(95,99,104,0.5)');
    for text in legend.get_texts(): text.set_color('#e8eaed')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.spines['bottom'].set_color('#5f6368'); ax.spines['left'].set_color('#5f6368')
    ax.tick_params(axis='x', colors='#dadce0'); ax.tick_params(axis='y', colors='#dadce0')
    ax.yaxis.grid(True, linestyle='--', alpha=0.2, color='#5f6368')
    def autolabel(rects_group, bar_color_text):
        for rect_item in rects_group:
            height_item = rect_item.get_height()
            if height_item > 0: ax.annotate(f'{height_item:,.0f}', xy=(rect_item.get_x() + rect_item.get_width() / 2, height_item), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=6, color=bar_color_text)
    autolabel(rects1, '#8ab4f8'); autolabel(rects2, '#34A853'); fig.tight_layout(pad=1.2); return fig

# --- LOGIN PAGE ---
if not st.session_state.auth["logged_in"]:
    st.title("TrackSphere Login")
    # ... (Login page logic from previous full code - ensure keys are unique) ...
    message_placeholder_login = st.empty()
    if st.session_state.user_message:
        message_placeholder_login.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
        st.session_state.user_message = None; st.session_state.message_type = None
    st.markdown("<div class='card' style='max-width: 400px; margin: 2rem auto;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #202124;'>🔐 Login</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname_unique")
    pwd = st.text_input("Password", type="password", key="login_pwd_unique")
    if st.button("Login", key="login_button_unique", type="primary", use_container_width=True):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = "Login successful!"; st.session_state.message_type = "success"; st.rerun()
        else: st.error("Invalid username or password.")
    st.markdown("</div>", unsafe_allow_html=True); st.stop()


# --- MAIN APPLICATION AFTER LOGIN ---
current_user_auth_info = st.session_state.auth
message_placeholder_main = st.empty()
if st.session_state.user_message:
    message_placeholder_main.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
    st.session_state.user_message = None; st.session_state.message_type = None

# --- REVISED SIDEBAR IMPLEMENTATION ---
with st.sidebar:
    st.markdown('<div class="sidebar-content-wrapper">', unsafe_allow_html=True)
    current_username = current_user_auth_info['username']
    user_details = USERS.get(current_username, {})

    # User Info Block
    st.markdown('<div class="sidebar-user-info">', unsafe_allow_html=True)
    col_img, col_info = st.columns([0.25, 0.75], gap="small")
    with col_img:
        if user_details.get("profile_photo") and os.path.exists(user_details["profile_photo"]):
            st.markdown("<div class='user-profile-img-container'>", unsafe_allow_html=True)
            st.image(user_details["profile_photo"])
            st.markdown("</div>", unsafe_allow_html=True)
        else: # Fallback if no image
            st.markdown(f"<div class='user-profile-img-container'><span class='material-symbols-outlined' style='font-size: 32px; color: #5f6368;'>account_circle</span></div>", unsafe_allow_html=True)

    with col_info:
        st.markdown(f"<div class='welcome-text-sidebar' style='margin-bottom: -2px; padding-left:0;'>{current_username}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='user-position-text' style='padding-left:0;'>{user_details.get('position', 'N/A')}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) # Close sidebar-user-info

    st.markdown("<hr>", unsafe_allow_html=True)

    def set_active_page_callback(page_name):
        st.session_state.active_page = page_name

    for item in NAV_OPTIONS_WITH_ICONS:
        label_with_icon_html = f"""
            <span class='material-symbols-outlined'>{item["icon"]}</span>
            <span style='margin-left: 0px;'>{item["label"]}</span>
        """
        # To apply active class, we need to wrap the button
        # This part is tricky because st.button doesn't take a class directly for its outer div
        is_active = (st.session_state.active_page == item["label"])
        
        if is_active:
            # For the active item, we wrap it in a div that has the 'active-nav-item' class
            st.markdown("<div class='active-nav-item'>", unsafe_allow_html=True)
            st.button(
                label_with_icon_html,
                key=item["key"],
                on_click=set_active_page_callback,
                args=(item["label"],),
                use_container_width=True,
                unsafe_allow_html=True # This is CRITICAL for rendering HTML in button
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.button(
                label_with_icon_html,
                key=item["key"],
                on_click=set_active_page_callback,
                args=(item["label"],),
                use_container_width=True,
                unsafe_allow_html=True # This is CRITICAL
            )

    # Logout Button
    st.markdown('<div class="logout-button-container">', unsafe_allow_html=True)
    logout_label_html = "<span class='material-symbols-outlined'>logout</span>Logout"
    if st.button(logout_label_html, key="nav_logout", use_container_width=True, unsafe_allow_html=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."
        st.session_state.message_type = "info"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True) # Close sidebar-content-wrapper

# --- MAIN CONTENT PAGE ROUTING (Your existing page logic goes here) ---
# ... (Place your if/elif active_page == "..." blocks here, same as the previous full code) ...
# ... Ensure all page content is wrapped in `<div class="card">...</div>` if desired ...
# (Content for Attendance, Upload Activity, Allowance, Goal Tracker, Payment Tracker, View Logs, Create Order)
# For brevity, I'll put placeholders. You should use your full page logic.

active_page = st.session_state.active_page
current_username_for_pages = current_user_auth_info['username']

if active_page == "Attendance":
    # ... (Your full Attendance page logic) ...
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("🕒 Attendance")
    st.write("Attendance form will be here.")
    st.markdown('</div>', unsafe_allow_html=True)
elif active_page == "Upload Activity Photo":
    # ... (Your full Upload Activity Photo page logic) ...
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header("📸 Upload Activity Photo")
    st.write("Upload form will be here.")
    st.markdown('</div>', unsafe_allow_html=True)
# ... Add all other elif blocks for your pages ...
elif active_page == "Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True); st.header("💼 Allowance"); st.markdown('</div>', unsafe_allow_html=True)
elif active_page == "Goal Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True); st.header("🎯 Goal Tracker"); st.markdown('</div>', unsafe_allow_html=True)
elif active_page == "Payment Collection Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True); st.header("💰 Payment Collection"); st.markdown('</div>', unsafe_allow_html=True)
elif active_page == "View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True); st.header("📊 View Logs"); st.markdown('</div>', unsafe_allow_html=True)
elif active_page == "Create Order":
    st.markdown('<div class="card">', unsafe_allow_html=True); st.header("🛒 Create Order"); st.markdown('</div>', unsafe_allow_html=True)
