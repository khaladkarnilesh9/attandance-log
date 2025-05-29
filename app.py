import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import pytz
import plotly.express as px

# --- Matplotlib Configuration ---
import matplotlib
matplotlib.use('Agg') # Use Agg backend for Streamlit compatibility (non-interactive)
import matplotlib.pyplot as plt
import numpy as np

# --- Pillow for placeholder image generation ---
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False
    st.warning("Pillow library not found. Placeholder images will not be generated.")

# --- Global Configuration & Constants ---
TARGET_TIMEZONE = "Asia/Kolkata"
try:
    tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'. Please check your timezone string.")
    st.stop()

# --- File Paths ---
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"
GOALS_FILE = "goals.csv"
PAYMENT_GOALS_FILE = "payment_goals.csv"
ACTIVITY_LOG_FILE = "activity_log.csv"
ACTIVITY_PHOTOS_DIR = "activity_photos"

# Ensure directories exist
if not os.path.exists(ACTIVITY_PHOTOS_DIR):
    try: os.makedirs(ACTIVITY_PHOTOS_DIR)
    except OSError as e: st.warning(f"Could not create directory {ACTIVITY_PHOTOS_DIR}: {e}")

# --- DATA LOADING & UTILITY FUNCTIONS ---
def get_current_time_in_tz():
    return datetime.now(timezone.utc).astimezone(tz)

def get_quarter_str_for_year(year): # Renamed for clarity if used for generic quarter
    current_time = get_current_time_in_tz()
    month = current_time.month
    if 1 <= month <= 3: return f"{year}-Q1"
    elif 4 <= month <= 6: return f"{year}-Q2"
    elif 7 <= month <= 9: return f"{year}-Q3"
    else: return f"{year}-Q4"

def load_data(path, columns):
    # Check if file exists and is not empty
    if os.path.exists(path) and os.path.getsize(path) > 0:
        try:
            df = pd.read_csv(path)
            # Ensure all expected columns exist, add if missing
            for col in columns:
                if col not in df.columns:
                    df[col] = pd.NA
            # Convert specific columns to numeric, coercing errors
            num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude"]
            for nc in num_cols:
                if nc in df.columns:
                    df[nc] = pd.to_numeric(df[nc], errors='coerce') # Coerce errors to NaN
            return df
        except pd.errors.EmptyDataError: # Handles files that exist but are empty after header
            st.warning(f"File {path} is empty. Initializing with columns: {', '.join(columns)}")
            return pd.DataFrame(columns=columns)
        except Exception as e:
            st.error(f"Error loading {path}: {e}. Initializing with columns: {', '.join(columns)}")
            return pd.DataFrame(columns=columns)
    else: # File does not exist or is empty (size 0)
        if not os.path.exists(path):
            st.info(f"File {path} not found. Creating it with headers: {', '.join(columns)}")
        elif os.path.exists(path) and os.path.getsize(path) == 0:
             st.info(f"File {path} exists but is empty. Initializing with headers: {', '.join(columns)}")

        df = pd.DataFrame(columns=columns)
        try:
            df.to_csv(path, index=False) # Create file with headers
        except Exception as e:
            st.warning(f"Could not create or write headers to {path}: {e}")
        return df

# Define column sets
ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]

# Load dataframes
attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
activity_log_df = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS)


# --- USER AUTHENTICATION & INFO ---
USERS = {
    "Geetali": {"password": "Geetali123", "role": "employee", "position": "Software Engineer", "profile_photo": "images/geetali.png"},
    "Nilesh": {"password": "Nilesh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "Vishal": {"password": "Vishal123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/vishal.png"},
    "Santosh": {"password": "Santosh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/santosh.png"},
    "Deepak": {"password": "Deepak123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/deepak.png"},
    "Rahul": {"password": "Rahul123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/rahul.png"},
    "admin": {"password": "admin123", "role": "admin", "position": "System Administrator", "profile_photo": "images/admin.png"}
}

# Create dummy images folder and placeholder images
if not os.path.exists("images"):
    try: os.makedirs("images")
    except OSError: pass

if PILLOW_INSTALLED:
    for user_key, user_data in USERS.items():
        img_path = user_data.get("profile_photo")
        if img_path and not os.path.exists(img_path):
            try:
                img = Image.new('RGB', (120, 120), color = (200, 220, 240))
                draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", 40)
                except IOError: font = ImageFont.load_default()
                text_content = user_key[:2].upper()
                # Use textbbox for accurate text centering if available
                if hasattr(draw, 'textbbox'):
                    # Get bounding box: left, top, right, bottom
                    bbox = draw.textbbox((0, 0), text_content, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    # Calculate position to center the text accounting for the bbox's top offset
                    pos_x = (120 - text_width) / 2
                    pos_y = (120 - text_height) / 2 - bbox[1] # Subtract the top of the bbox
                elif hasattr(draw, 'textsize'): # Fallback for older Pillow
                    text_width, text_height = draw.textsize(text_content, font=font)
                    pos_x = (120 - text_width) / 2
                    pos_y = (120 - text_height) / 2
                else: # Basic fallback
                    pos_x, pos_y = 30, 30
                draw.text((pos_x, pos_y), text_content, fill=(28,78,128), font=font)
                img.save(img_path)
            except Exception: pass # Silently ignore placeholder creation errors

# --- CSS STYLING ---
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    /* --- FONT IMPORTS & GENERAL DEFINITIONS --- */
    body, .stButton button, .stTextInput input, .stTextArea textarea, .stSelectbox select, p, div, span {
        font-family: 'Roboto', sans-serif !important;
    }
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined' !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: 22px !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        display: inline-block !important;
        white-space: nowrap !important;
        word-wrap: normal !important;
        direction: ltr !important;
        -webkit-font-smoothing: antialiased !important;
        text-rendering: optimizeLegibility !important;
        -moz-osx-font-smoothing: grayscale !important;
        font-feature-settings: 'liga' !important;
        vertical-align: middle !important;
    }

    /* --- SIDEBAR STYLING --- */
    section[data-testid="stSidebar"] > div:first-child {
        padding: 0px !important;
        margin: 0px !important;
        background-color: #1e1f22 !important;
    }
    .sidebar-content-wrapper {
        background-color: #1e1f22 !important;
        color: #e8eaed !important;
        height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        padding: 0.75rem !important;
        box-sizing: border-box !important;
    }
    .nav-item-row {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        padding: 0.6rem 0.8rem !important;
        margin-bottom: 3px !important;
        border-radius: 8px !important;
        transition: background-color 0.15s ease-in-out, color 0.15s ease-in-out !important;
        color: #dadce0 !important;
        cursor: default !important;
    }
    .nav-item-row:hover {
        background-color: #282a2d !important;
        color: #ffffff !important;
    }
    .nav-item-row.active {
        background-color: rgba(138, 180, 248, 0.2) !important;
        color: #8ab4f8 !important;
        font-weight: 500 !important;
    }
    .nav-item-row [data-testid="stHorizontalBlock"] > div:nth-child(1) { /* Icon Column */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex: 0 0 35px !important; /* Fixed width for icon area */
        margin-right: 5px !important;
    }
    .nav-item-row .nav-icon { /* Class for the icon span */
        color: #9aa0a6 !important;
        font-size: 22px !important;
    }
    .nav-item-row:hover .nav-icon {
        color: #ffffff !important;
    }
    .nav-item-row.active .nav-icon {
        color: #8ab4f8 !important;
    }
    .nav-item-row [data-testid="stHorizontalBlock"] > div:nth-child(2) { /* Text/Button Column */
        padding-left: 0 !important;
        flex-grow: 1 !important;
        display: flex !important;
        align-items: center !important;
    }
    .nav-item-row .stButton button {
        text-align: left !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
        background-color: transparent !important;
        color: inherit !important;
        font-weight: inherit !important;
        font-size: 0.875rem !important;
        line-height: 1.4 !important;
        width: 100% !important;
        display: block !important;
        box-shadow: none !important;
        outline: none !important;
        cursor: pointer !important;
    }
    .nav-item-row .stButton button:hover,
    .nav-item-row .stButton button:focus,
    .nav-item-row .stButton button:active {
        background-color: transparent !important;
        color: inherit !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* --- User Info and Other Sidebar Elements --- */
    .welcome-text-sidebar { font-size: 1rem !important; font-weight: 500 !important; color: #e8eaed !important; margin-bottom: 0.75rem !important; padding: 0.25rem 0.5rem !important; }
    .user-profile-img-container { text-align: center !important; margin-bottom: 0.5rem !important; }
    .user-profile-img-container img { border-radius: 50% !important; width: 60px !important; height: 60px !important; object-fit: cover !important; border: 2px solid #5f6368 !important; }
    .user-position-text { text-align: center !important; font-size: 0.75rem !important; color: #bdc1c6 !important; margin-bottom: 1rem !important; }
    .sidebar-content-wrapper hr { margin: 1rem 0 !important; border: none !important; border-top: 1px solid rgba(255, 255, 255, 0.1) !important; }
    .logout-button-container { margin-top: auto !important; padding-top: 1rem !important; }
    .nav-item-row.logout-row-styling { background-color: transparent !important; color: #e8eaed !important; border: 1px solid #5f6368 !important; }
    .nav-item-row.logout-row-styling:hover { background-color: #c53929 !important; color: #ffffff !important; border-color: #c53929 !important; }
    .nav-item-row.logout-row-styling .nav-icon { color: #e8eaed !important; }
    .nav-item-row.logout-row-styling:hover .nav-icon { color: #ffffff !important; }

    /* --- Global Message Notifications & Main Content Cards --- */
    .custom-notification { padding: 1rem; border-radius: 6px; margin-bottom: 1rem; border: 1px solid transparent; font-size: 0.9rem; }
    .custom-notification.success { color: #155724; background-color: #d4edda; border-color: #c3e6cb; }
    .custom-notification.error { color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; }
    .custom-notification.info { color: #0c5460; background-color: #d1ecf1; border-color: #bee5eb; }
    .custom-notification.warning { color: #856404; background-color: #fff3cd; border-color: #ffeeba; }
    div[data-testid="stAppViewContainer"] > .main { background-color: #f0f2f5 !important; }
    .card { background-color: #ffffff; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border: 1px solid #d1d5da; box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 2px 4px rgba(0,0,0,0.04); }
    .button-column-container .stButton button { width: 100%; }
    .employee-progress-item h6 { margin-bottom: 0.25rem; font-size: 1rem; color: #202124; }
    .employee-progress-item p { font-size: 0.85rem; color: #5f6368; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}

NAV_OPTIONS_WITH_ICONS = [
    {"label": "Attendance", "icon": "schedule"},
    {"label": "Upload Activity Photo", "icon": "add_a_photo"},
    {"label": "Allowance", "icon": "payments"},
    {"label": "Goal Tracker", "icon": "emoji_events"},
    {"label": "Payment Collection Tracker", "icon": "receipt_long"},
    {"label": "View Logs", "icon": "wysiwyg"},
    {"label": "Create Order", "icon": "add_shopping_cart"}
]
if "active_page" not in st.session_state:
    st.session_state.active_page = NAV_OPTIONS_WITH_ICONS[0]["label"]


# --- PLOTTING FUNCTIONS ---
# (Keep your plotting functions as they were: render_goal_chart, create_donut_chart, create_team_progress_bar_chart)
def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty:
        st.warning("No data available to plot.")
        return
    df_chart = df.copy()
    df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear",
                              value_vars=["TargetAmount", "AchievedAmount"],
                              var_name="Metric",
                              value_name="Amount")
    if df_melted.empty:
        st.warning(f"No data to plot for {chart_title} after processing.")
        return
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group",
                 labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"},
                 title=chart_title,
                 color_discrete_map={'TargetAmount': '#4285F4', 'AchievedAmount': '#34A853'}) # Google themed colors
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric',
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)') # Transparent bg for plots
    st.plotly_chart(fig, use_container_width=True)

def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#8ab4f8', remaining_color='rgba(255,255,255,0.1)', center_text_color=None): # AI Studio theme colors
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=100) # Increased DPI for clarity
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    progress_percentage = max(0.0, min(float(progress_percentage), 100.0))
    remaining_percentage = 100.0 - progress_percentage

    if progress_percentage <= 0.01: sizes = [100.0]; slice_colors = [remaining_color]; actual_progress_display = 0.0
    elif progress_percentage >= 99.99: sizes = [100.0]; slice_colors = [achieved_color]; actual_progress_display = 100.0
    else: sizes = [progress_percentage, remaining_percentage]; slice_colors = [achieved_color, remaining_color]; actual_progress_display = progress_percentage

    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.35, edgecolor='#1e1f22')) # Dark edge for contrast
    centre_circle = plt.Circle((0,0),0.65,fc='#1e1f22'); fig.gca().add_artist(centre_circle) # Dark center to match sidebar

    text_color_to_use = center_text_color if center_text_color else (achieved_color if actual_progress_display > 0 else '#dadce0') # Light text
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=11, fontweight='bold', color=text_color_to_use) # Smaller font
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig

def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee"):
    if summary_df.empty: return None
    labels = summary_df[user_col].tolist()
    target_amounts = summary_df[target_col].fillna(0).tolist()
    achieved_amounts = summary_df[achieved_col].fillna(0).tolist()

    x = np.arange(len(labels)); width = 0.35
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.8), 5), dpi=100, facecolor='rgba(0,0,0,0)') # Transparent bg
    ax.set_facecolor('rgba(0,0,0,0)')

    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color='rgba(138, 180, 248, 0.7)', alpha=0.9) # Google Blue, slightly transparent
    rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color='rgba(52, 168, 83, 0.7)', alpha=0.9) # Google Green, slightly transparent

    ax.set_ylabel('Amount (INR)', fontsize=10, color='#dadce0') # Light text
    ax.set_title(title, fontsize=12, fontweight='bold', pad=15, color='#e8eaed') # Light text
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9, color='#dadce0')
    legend = ax.legend(fontsize=9, facecolor='#282a2d', edgecolor='#5f6368') # Dark legend bg
    for text in legend.get_texts(): text.set_color('#e8eaed') # Light legend text

    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#5f6368'); ax.spines['left'].set_color('#5f6368') # Lighter spines
    ax.tick_params(axis='x', colors='#dadce0'); ax.tick_params(axis='y', colors='#dadce0') # Light ticks
    ax.yaxis.grid(True, linestyle='--', alpha=0.2, color='#5f6368') # Dimmer grid

    def autolabel(rects_group, bar_color):
        for rect_item in rects_group:
            height_item = rect_item.get_height()
            if height_item > 0:
                ax.annotate(f'{height_item:,.0f}', xy=(rect_item.get_x() + rect_item.get_width() / 2, height_item),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontsize=7, color=bar_color, alpha=0.9) # Match bar color
    autolabel(rects1, '#8ab4f8'); autolabel(rects2, '#34A853')
    fig.tight_layout(pad=1.5)
    return fig


# --- LOGIN PAGE ---
if not st.session_state.auth["logged_in"]:
    # st.set_page_config(layout="centered") # Can be set for login page
    st.title("TrackSphere Login")
    message_placeholder_login = st.empty()
    if st.session_state.user_message:
        message_placeholder_login.markdown(
            f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>",
            unsafe_allow_html=True
        )
        st.session_state.user_message = None
        st.session_state.message_type = None

    # Centered login form using a card style from CSS
    st.markdown("<div class='card' style='max-width: 400px; margin: 2rem auto;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #202124;'>🔐 Login</h3>", unsafe_allow_html=True) # Dark text for card
    uname = st.text_input("Username", key="login_uname_main_key")
    pwd = st.text_input("Password", type="password", key="login_pwd_main_key")
    if st.button("Login", key="login_button_main_key", type="primary", use_container_width=True):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = "Login successful!"
            st.session_state.message_type = "success"
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- MAIN APPLICATION AFTER LOGIN ---
# st.set_page_config(layout="wide") # Set for main app pages
current_user_auth_info = st.session_state.auth

message_placeholder_main = st.empty()
if st.session_state.user_message:
    message_placeholder_main.markdown(
        f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>",
        unsafe_allow_html=True
    )
    st.session_state.user_message = None
    st.session_state.message_type = None

# --- SIDEBAR IMPLEMENTATION ---
with st.sidebar:
    st.markdown('<div class="sidebar-content-wrapper">', unsafe_allow_html=True)
    current_username = current_user_auth_info['username']
    user_details = USERS.get(current_username, {})

    st.markdown(f"<div class='welcome-text-sidebar'>Welcome, {current_username}!</div>", unsafe_allow_html=True)
    if user_details.get("profile_photo") and os.path.exists(user_details["profile_photo"]):
        st.markdown("<div class='user-profile-img-container'>", unsafe_allow_html=True)
        st.image(user_details["profile_photo"])
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='user-position-text'>{user_details.get('position', 'N/A')}</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    def set_active_page_callback(page_name):
        st.session_state.active_page = page_name

    for item in NAV_OPTIONS_WITH_ICONS:
        option_label = item["label"]
        option_icon = item["icon"]
        button_key = f"nav_btn_{option_label.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
        is_active = (st.session_state.active_page == option_label)
        row_class = "nav-item-row active" if is_active else "nav-item-row"
        
        st.markdown(f"<div class='{row_class}'>", unsafe_allow_html=True)
        col_icon, col_button_text = st.columns([0.15, 0.85], gap="small")
        with col_icon:
            st.markdown(f'<span class="material-symbols-outlined nav-icon">{option_icon}</span>', unsafe_allow_html=True)
        with col_button_text:
            if st.button(option_label, key=button_key, on_click=set_active_page_callback, args=(option_label,), use_container_width=True):
                pass
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="logout-button-container">', unsafe_allow_html=True)
    st.markdown("<div class='nav-item-row logout-row-styling'>", unsafe_allow_html=True)
    logout_col_icon, logout_col_button = st.columns([0.15, 0.85], gap="small")
    with logout_col_icon:
        st.markdown('<span class="material-symbols-outlined nav-icon">logout</span>', unsafe_allow_html=True)
    with logout_col_button:
        if st.button("Logout", key="logout_button_sidebar_actual_key", use_container_width=True):
            st.session_state.auth = {"logged_in": False, "username": None, "role": None}
            st.session_state.user_message = "Logged out successfully."
            st.session_state.message_type = "info"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# --- MAIN CONTENT PAGE ROUTING ---
# (The rest of your page logic from the previous full code block: Attendance, Upload Activity, Allowance, Goal Tracker, etc.)
# ... (Ensure all page content is wrapped in `<div class="card">...</div>` if desired)
active_page = st.session_state.active_page
current_username_for_pages = current_user_auth_info['username']

if active_page == "Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled for attendance. Photos for specific activities can be uploaded from the 'Upload Activity Photo' section.", icon="ℹ️")
    st.markdown("---")
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1_att, col2_att = st.columns(2)
    common_data_att = {"Username": current_username_for_pages, "Latitude": pd.NA, "Longitude": pd.NA}

    def process_general_attendance(attendance_type):
        global attendance_df
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_data = {"Type": attendance_type, "Timestamp": now_str_display, **common_data_att}
        for col_name in ATTENDANCE_COLUMNS:
            if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
        new_entry = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
        attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        try:
            attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."
            st.session_state.message_type = "success"; st.rerun()
        except Exception as e:
            st.session_state.user_message = f"Error saving attendance: {e}"
            st.session_state.message_type = "error"; st.rerun()

    with col1_att:
        if st.button("✅ Check In", key="check_in_btn_main_page", use_container_width=True, type="primary"):
            process_general_attendance("Check-In")
    with col2_att:
        if st.button("🚪 Check Out", key="check_out_btn_main_page", use_container_width=True, type="primary"):
            process_general_attendance("Check-Out")
    st.markdown('</div></div>', unsafe_allow_html=True)

elif active_page == "Upload Activity Photo":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat_activity, current_lon_activity = pd.NA, pd.NA
    with st.form(key="activity_photo_form_main"):
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description:", key="activity_desc_page")
        img_file_buffer_activity = st.camera_input("Take a picture:", key="activity_camera_page")
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo & Log")
    if submit_activity_photo:
        if img_file_buffer_activity is None: st.warning("Please take a picture.")
        elif not activity_description.strip(): st.warning("Please provide a description.")
        else:
            # ... (rest of upload logic - same as before) ...
            now_for_filename = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S")
            now_for_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            image_filename_activity = f"{current_username_for_pages}_activity_{now_for_filename}.jpg"
            image_path_activity = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_activity)
            try:
                with open(image_path_activity, "wb") as f: f.write(img_file_buffer_activity.getbuffer())
                new_activity_data = {"Username": current_username_for_pages, "Timestamp": now_for_display, 
                                     "Description": activity_description, "ImageFile": image_filename_activity, 
                                     "Latitude": current_lat_activity, "Longitude": current_lon_activity}
                for col_name in ACTIVITY_LOG_COLUMNS:
                    if col_name not in new_activity_data: new_activity_data[col_name] = pd.NA
                new_activity_entry = pd.DataFrame([new_activity_data], columns=ACTIVITY_LOG_COLUMNS)
                activity_log_df = pd.concat([activity_log_df, new_activity_entry], ignore_index=True)
                activity_log_df.to_csv(ACTIVITY_LOG_FILE, index=False)
                st.session_state.user_message = "Activity photo and log uploaded!"; st.session_state.message_type = "success"; st.rerun()
            except Exception as e: st.session_state.user_message = f"Error saving activity: {e}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif active_page == "Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    allowance_type = st.radio("Type:", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allowance_type_page", horizontal=True)
    allowance_amount = st.number_input("Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_page")
    allowance_reason = st.text_area("Reason:", key="allowance_reason_page", placeholder="Justification...")
    if st.button("Submit Request", key="submit_allowance_page", use_container_width=True, type="primary"):
        if allowance_type and allowance_amount > 0 and allowance_reason.strip():
            # ... (rest of allowance submission - same as before) ...
            allowance_date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_allowance_data = {"Username": current_username_for_pages, "Type": allowance_type, 
                                  "Amount": allowance_amount, "Reason": allowance_reason, "Date": allowance_date_str}
            new_allowance_entry = pd.DataFrame([new_allowance_data], columns=ALLOWANCE_COLUMNS)
            allowance_df = pd.concat([allowance_df, new_allowance_entry], ignore_index=True)
            try:
                allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                st.session_state.user_message = f"Allowance for ₹{allowance_amount:.2f} submitted."; st.session_state.message_type = "success"; st.rerun()
            except Exception as e: st.session_state.user_message = f"Error submitting allowance: {e}"; st.session_state.message_type = "error"; st.rerun()
        else: st.warning("Please complete all fields.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Goal Tracker Page (Simplified for brevity, expand as needed) ---
elif active_page == "Goal Tracker":
    # (Your existing Goal Tracker page logic - it's quite long, so ensure it's correctly placed here)
    # Make sure to use current_username_for_pages for filtering employee data
    # And current_user_auth_info["role"] for admin/employee views
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    # ... (Full Goal Tracker logic from your previous correct version) ...
    # Example placeholder for the logic structure:
    TARGET_GOAL_YEAR_GT = 2025
    current_quarter_gt = get_quarter_str_for_year(TARGET_GOAL_YEAR_GT) # Use specific year
    if current_user_auth_info["role"] == "admin":
        st.write(f"Admin view for Sales Goals - Quarter: {current_quarter_gt}")
        # Admin specific UI for goals
    else:
        st.write(f"Employee view for Sales Goals ({current_username_for_pages}) - Quarter: {current_quarter_gt}")
        # Employee specific UI for goals
    st.markdown("</div>", unsafe_allow_html=True)


# --- Payment Collection Tracker Page (Simplified) ---
elif active_page == "Payment Collection Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    # ... (Full Payment Tracker logic from your previous correct version) ...
    TARGET_PAYMENT_YEAR_PCT = 2025
    current_quarter_pct = get_quarter_str_for_year(TARGET_PAYMENT_YEAR_PCT)
    if current_user_auth_info["role"] == "admin":
        st.write(f"Admin view for Payment Collection - Quarter: {current_quarter_pct}")
    else:
        st.write(f"Employee view for Payment Collection ({current_username_for_pages}) - Quarter: {current_quarter_pct}")
    st.markdown("</div>", unsafe_allow_html=True)

# --- View Logs Page (Simplified) ---
elif active_page == "View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 View Logs</h3>", unsafe_allow_html=True)
    # ... (Full View Logs logic from your previous correct version) ...
    if current_user_auth_info["role"] == "admin":
        st.write("Admin view for Logs")
    else:
        st.write(f"Employee view for Logs ({current_username_for_pages})")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Create Order Page (Simplified) ---
elif active_page == "Create Order":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🛒 Create New Order</h3>", unsafe_allow_html=True)
    # ... (Full Create Order logic from your previous correct version) ...
    try:
        stores_df_co = pd.read_csv("agri_stores.csv")
        products_df_co = pd.read_csv("symplanta_products_with_images.csv")
        st.write(f"Create Order page for {current_username_for_pages}")
        # UI for selecting store, product, size, quantity
    except FileNotFoundError:
        st.error("Order data files (agri_stores.csv, symplanta_products_with_images.csv) not found.")
    st.markdown("</div>", unsafe_allow_html=True)
