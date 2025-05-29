import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import pytz
import plotly.express as px

# --- Matplotlib Configuration ---
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# --- Pillow for placeholder image generation ---
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

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
# ATTENDANCE_PHOTOS_DIR = "attendance_photos" # Not actively used if photos are only with activities

# Ensure directories exist
if not os.path.exists(ACTIVITY_PHOTOS_DIR):
    try: os.makedirs(ACTIVITY_PHOTOS_DIR)
    except OSError as e: st.warning(f"Could not create directory {ACTIVITY_PHOTOS_DIR}: {e}")


# --- DATA LOADING & UTILITY FUNCTIONS ---
def get_current_time_in_tz():
    return datetime.now(timezone.utc).astimezone(tz)

def get_quarter_str_for_year(year):
    now_month = get_current_time_in_tz().month
    if 1 <= now_month <= 3: return f"{year}-Q1"
    elif 4 <= now_month <= 6: return f"{year}-Q2"
    elif 7 <= now_month <= 9: return f"{year}-Q3"
    else: return f"{year}-Q4"

def load_data(path, columns):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        try:
            df = pd.read_csv(path)
            # Ensure all expected columns exist, add if missing
            for col in columns:
                if col not in df.columns:
                    df[col] = pd.NA  # Use pd.NA for missing values, suitable for various dtypes
            # Convert specific columns to numeric, coercing errors
            num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude"]
            for nc in num_cols:
                if nc in df.columns:
                    df[nc] = pd.to_numeric(df[nc], errors='coerce')
            return df
        except pd.errors.EmptyDataError:
            st.warning(f"File {path} is empty. Initializing with columns.")
            return pd.DataFrame(columns=columns)
        except Exception as e:
            st.error(f"Error loading {path}: {e}. Initializing with columns.")
            return pd.DataFrame(columns=columns)
    else:
        if not os.path.exists(path):
            st.info(f"File {path} not found. Creating it with headers.")
        elif os.path.exists(path) and os.path.getsize(path) == 0:
             st.info(f"File {path} exists but is empty. Initializing with headers.")

        df = pd.DataFrame(columns=columns)
        try:
            df.to_csv(path, index=False)
        except Exception as e:
            st.warning(f"Could not create or write headers to {path}: {e}")
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
    except OSError: pass # Fail silently if images dir already exists or cannot be made

if PILLOW_INSTALLED:
    for user_key, user_data in USERS.items():
        img_path = user_data.get("profile_photo")
        if img_path and not os.path.exists(img_path):
            try:
                img = Image.new('RGB', (120, 120), color = (200, 220, 240))
                draw = ImageDraw.Draw(img)
                try:
                    # Attempt to load a common system font; adjust path if needed or use default
                    font = ImageFont.truetype("arial.ttf", 40)
                except IOError:
                    font = ImageFont.load_default() # Fallback to default PIL font

                text = user_key[:2].upper()

                # Modern PIL text bounding box calculation
                if hasattr(draw, 'textbbox'):
                    bbox = draw.textbbox((0,0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    # Adjust y based on bbox[1] which is the top of the text, not necessarily 0
                    text_x = (120 - text_width) / 2
                    text_y = (120 - text_height) / 2 - bbox[1]
                # Older PIL textsize calculation
                elif hasattr(draw, 'textsize'):
                    text_width, text_height = draw.textsize(text, font=font)
                    text_x = (120 - text_width) / 2
                    text_y = (120 - text_height) / 2
                # Fallback if text measurement not available
                else:
                    text_x, text_y = 30, 30

                draw.text((text_x, text_y), text, fill=(28,78,128), font=font)
                img.save(img_path)
            except Exception as e:
                # st.warning(f"Could not create placeholder image for {user_key}: {e}") # Optional warning
                pass # Fail silently for placeholder creation

# --- CSS STYLING ---
# This is the CSS block for the Google AI Studio dark theme.
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    /* --- FONT IMPORTS & GENERAL DEFINITIONS --- */
    body, .stButton button, .stTextInput input, .stTextArea textarea, .stSelectbox select, p, div, span {
        font-family: 'Roboto', sans-serif;
    }
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        font-size: 20px;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-smoothing: antialiased;
        text-rendering: optimizeLegibility;
        -moz-osx-font-smoothing: grayscale;
        font-feature-settings: 'liga';
        vertical-align: -0.15em;
    }

    /* --- SIDEBAR STYLING --- */
    section[data-testid="stSidebar"] > div:first-child {
        padding: 0px !important;
    }
    .sidebar-content-wrapper {
        background-color: #1e1f22 !important;
        color: #e8eaed !important;
        height: 100%;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        padding: 1rem 0.75rem;
        box-sizing: border-box;
    }
    .nav-item-row {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        padding: 0.6rem 0.8rem !important;
        margin-bottom: 2px !important;
        border-radius: 6px !important;
        transition: background-color 0.15s ease-in-out, color 0.15s ease-in-out;
        color: #dadce0 !important;
        cursor: default;
    }
    .nav-item-row:hover {
        background-color: #282a2d !important;
        color: #ffffff !important;
    }
    .nav-item-row.active {
        background-color: rgba(138, 180, 248, 0.16) !important;
        color: #8ab4f8 !important;
        font-weight: 500 !important;
    }
    .nav-item-row .nav-icon {
        color: #9aa0a6 !important;
        margin-right: 14px !important;
        font-size: 20px !important;
        line-height: 1 !important;
    }
    .nav-item-row:hover .nav-icon {
        color: #ffffff !important;
    }
    .nav-item-row.active .nav-icon {
        color: #8ab4f8 !important;
    }
    .nav-item-row [data-testid="stHorizontalBlock"] > div:nth-child(1) { /* Icon column */
        display: flex;
        align-items: center;
        justify-content: flex-start;
        flex-grow: 0 !important;
        flex-shrink: 0 !important;
    }
    .nav-item-row [data-testid="stHorizontalBlock"] > div:nth-child(2) { /* Text/Button column */
        padding-left: 0 !important;
        flex-grow: 1;
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
        line-height: 1.5 !important;
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
    .welcome-text-sidebar {
        font-size: 1rem;
        font-weight: 500;
        color: #e8eaed !important;
        margin-bottom: 0.75rem;
        padding: 0.25rem 0.5rem;
    }
    .user-profile-img-container {
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .user-profile-img-container img {
        border-radius: 50%;
        width: 60px;
        height: 60px;
        object-fit: cover;
        border: 2px solid #5f6368;
    }
    .user-position-text {
        text-align: center;
        font-size: 0.75rem;
        color: #bdc1c6 !important;
        margin-bottom: 1rem;
    }
    .sidebar-content-wrapper hr {
        margin: 1rem 0;
        border: none !important;
        border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    .logout-button-container {
        margin-top: auto;
        padding-top: 1rem;
    }
    .nav-item-row.logout-row-styling {
        background-color: transparent !important;
        color: #e8eaed !important;
        border: 1px solid #5f6368;
    }
    .nav-item-row.logout-row-styling:hover {
        background-color: #c53929 !important;
        color: #ffffff !important;
        border-color: #c53929 !important;
    }
    .nav-item-row.logout-row-styling .nav-icon {
        color: #e8eaed !important;
    }
    .nav-item-row.logout-row-styling:hover .nav-icon {
        color: #ffffff !important;
    }

    /* --- Global Message Notifications --- */
    .custom-notification {
        padding: 1rem;
        border-radius: 6px;
        margin-bottom: 1rem;
        border: 1px solid transparent;
        font-size: 0.9rem;
    }
    .custom-notification.success { color: #155724; background-color: #d4edda; border-color: #c3e6cb; }
    .custom-notification.error { color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; }
    .custom-notification.info { color: #0c5460; background-color: #d1ecf1; border-color: #bee5eb; }
    .custom-notification.warning { color: #856404; background-color: #fff3cd; border-color: #ffeeba; }

    /* --- Main Content Card Styling --- */
    div[data-testid="stAppViewContainer"] > .main {
        background-color: #f0f2f5; /* Light gray main background */
    }
    .card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border: 1px solid #d1d5da;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04), 0 2px 4px rgba(0,0,0,0.04);
    }
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
                 color_discrete_map={'TargetAmount': '#3498db', 'AchievedAmount': '#2ecc71'}) # Consider theming these colors too
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric')
    fig.update_xaxes(type='category')
    st.plotly_chart(fig, use_container_width=True)

def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#2ecc71', remaining_color='#f0f0f0', center_text_color=None): # Theming colors could be applied here
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=90)
    fig.patch.set_alpha(0); ax.patch.set_alpha(0) # Transparent background
    progress_percentage = max(0.0, min(float(progress_percentage), 100.0))
    remaining_percentage = 100.0 - progress_percentage

    if progress_percentage <= 0.01:
        sizes = [100.0]; slice_colors = [remaining_color]; actual_progress_display = 0.0
    elif progress_percentage >= 99.99:
        sizes = [100.0]; slice_colors = [achieved_color]; actual_progress_display = 100.0
    else:
        sizes = [progress_percentage, remaining_percentage]; slice_colors = [achieved_color, remaining_color]; actual_progress_display = progress_percentage

    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.4, edgecolor='white')) # White edgecolor for separation
    centre_circle = plt.Circle((0,0),0.60,fc='white'); fig.gca().add_artist(centre_circle) # White center

    text_color_to_use = center_text_color if center_text_color else (achieved_color if actual_progress_display > 0 else '#4A4A4A')
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=12, fontweight='bold', color=text_color_to_use)
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig

def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee"): # Theming colors
    if summary_df.empty: return None
    labels = summary_df[user_col].tolist()
    target_amounts = summary_df[target_col].fillna(0).tolist()
    achieved_amounts = summary_df[achieved_col].fillna(0).tolist()

    x = np.arange(len(labels)); width = 0.35
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.8), 5), dpi=100)
    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color='#3498db', alpha=0.8) # Theming
    rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color='#2ecc71', alpha=0.8) # Theming

    ax.set_ylabel('Amount (INR)', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.legend(fontsize=9)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                ax.annotate(f'{height:,.0f}', xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha='center', va='bottom', fontsize=7, color='#333')
    autolabel(rects1); autolabel(rects2)
    fig.tight_layout(pad=1.5)
    return fig


# --- LOGIN PAGE ---
if not st.session_state.auth["logged_in"]:
    st.title("TrackSphere Login")
    message_placeholder_login = st.empty()
    if st.session_state.user_message:
        message_placeholder_login.markdown(
            f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>",
            unsafe_allow_html=True
        )
        st.session_state.user_message = None
        st.session_state.message_type = None

    st.markdown("<div class='card' style='max-width: 400px; margin: auto; margin-top: 50px;'>", unsafe_allow_html=True) # Center login card
    st.markdown("<h3 style='text-align: center;'>🔐 Login</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname_main") # Changed key to avoid conflict if used elsewhere
    pwd = st.text_input("Password", type="password", key="login_pwd_main")
    if st.button("Login", key="login_button_main", type="primary", use_container_width=True):
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
current_user_auth_info = st.session_state.auth

# Display global messages if any
message_placeholder_main = st.empty()
if st.session_state.user_message:
    message_placeholder_main.markdown(
        f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>",
        unsafe_allow_html=True
    )
    st.session_state.user_message = None
    st.session_state.message_type = None

# --- SIDEBAR IMPLEMENTATION ---
# with st.sidebar:
#     st.markdown('<div class="sidebar-content-wrapper">', unsafe_allow_html=True)

#     current_username = current_user_auth_info['username']
#     user_details = USERS.get(current_username, {})

#     st.markdown(f"<div class='welcome-text-sidebar'>Welcome, {current_username}!</div>", unsafe_allow_html=True)

#     if user_details.get("profile_photo") and os.path.exists(user_details["profile_photo"]):
#         st.markdown("<div class='user-profile-img-container'>", unsafe_allow_html=True)
#         st.image(user_details["profile_photo"]) # Width controlled by CSS
#         st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f"<div class='user-position-text'>{user_details.get('position', 'N/A')}</div>",
        unsafe_allow_html=True
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    def set_active_page_callback(page_name): # Define callback here or globally
        st.session_state.active_page = page_name

    for item in NAV_OPTIONS_WITH_ICONS:
        option_label = item["label"]
        option_icon = item["icon"]
        button_key = f"nav_btn_{option_label.lower().replace(' ', '_').replace('(', '').replace(')', '')}"
        is_active = (st.session_state.active_page == option_label)
        
        row_class = "nav-item-row active" if is_active else "nav-item-row"
        
        st.markdown(f"<div class='{row_class}'>", unsafe_allow_html=True)
        
        # Use a fixed width for the icon column for consistent alignment
        col_icon, col_button_text = st.columns([0.15, 0.85], gap="small") # e.g. 15% for icon, 85% for text

        with col_icon:
            st.markdown(f'<span class="material-symbols-outlined nav-icon">{option_icon}</span>', unsafe_allow_html=True)
        
        with col_button_text:
            # This button is now correctly styled by the CSS targeting its parent .nav-item-row
            # and its own transparent styling.
            if st.button(option_label, key=button_key, on_click=set_active_page_callback, args=(option_label,), use_container_width=True):
                pass # Callback handles navigation change

        st.markdown("</div>", unsafe_allow_html=True) # Close the nav-item-row div

    # Logout Button
    st.markdown('<div class="logout-button-container">', unsafe_allow_html=True)
    st.markdown("<div class='nav-item-row logout-row-styling'>", unsafe_allow_html=True)
    logout_col_icon, logout_col_button = st.columns([0.15, 0.85], gap="small")
    with logout_col_icon:
        st.markdown('<span class="material-symbols-outlined nav-icon">logout</span>', unsafe_allow_html=True)
    with logout_col_button:
        if st.button("Logout", key="logout_button_sidebar_actual", use_container_width=True):
            st.session_state.auth = {"logged_in": False, "username": None, "role": None}
            st.session_state.user_message = "Logged out successfully."
            st.session_state.message_type = "info"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


# --- MAIN CONTENT PAGE ROUTING ---
active_page = st.session_state.active_page
current_username_for_pages = current_user_auth_info['username'] # Use this for data filtering

if active_page == "Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled for attendance. Photos for specific activities can be uploaded from the 'Upload Activity Photo' section.", icon="ℹ️")
    st.markdown("---")
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1_att, col2_att = st.columns(2)
    common_data_att = {"Username": current_username_for_pages, "Latitude": pd.NA, "Longitude": pd.NA}

    def process_general_attendance(attendance_type):
        global attendance_df # Ensure modification of global df
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_data = {"Type": attendance_type, "Timestamp": now_str_display, **common_data_att}
        # Ensure all columns from ATTENDANCE_COLUMNS are present
        for col_name in ATTENDANCE_COLUMNS:
            if col_name not in new_entry_data:
                new_entry_data[col_name] = pd.NA
        
        new_entry = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
        
        # Use pd.concat to append new entry
        attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        try:
            attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."
            st.session_state.message_type = "success"
            st.rerun()
        except Exception as e:
            st.session_state.user_message = f"Error saving attendance: {e}"
            st.session_state.message_type = "error"
            st.rerun()

    with col1_att:
        if st.button("✅ Check In", key="check_in_btn_main", use_container_width=True, type="primary"):
            process_general_attendance("Check-In")
    with col2_att:
        if st.button("🚪 Check Out", key="check_out_btn_main", use_container_width=True, type="primary"): # Changed type to primary for consistency
            process_general_attendance("Check-Out")
    st.markdown('</div>', unsafe_allow_html=True) # Close button-column-container
    st.markdown('</div>', unsafe_allow_html=True) # Close card

elif active_page == "Upload Activity Photo":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat_activity = pd.NA # Placeholder, actual location capture not implemented
    current_lon_activity = pd.NA

    with st.form(key="activity_photo_form"):
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description of activity/visit:", key="activity_desc_input")
        img_file_buffer_activity = st.camera_input("Take a picture of your activity/visit", key="activity_camera_main")
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo and Log Activity")

    if submit_activity_photo:
        if img_file_buffer_activity is None:
            st.warning("Please take a picture before submitting.")
        elif not activity_description.strip():
            st.warning("Please provide a description for the activity.")
        else:
            now_for_filename = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S")
            now_for_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            image_filename_activity = f"{current_username_for_pages}_activity_{now_for_filename}.jpg"
            image_path_activity = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_activity)
            try:
                with open(image_path_activity, "wb") as f:
                    f.write(img_file_buffer_activity.getbuffer())

                new_activity_data = {
                    "Username": current_username_for_pages,
                    "Timestamp": now_for_display,
                    "Description": activity_description,
                    "ImageFile": image_filename_activity,
                    "Latitude": current_lat_activity,
                    "Longitude": current_lon_activity
                }
                for col_name in ACTIVITY_LOG_COLUMNS:
                    if col_name not in new_activity_data:
                        new_activity_data[col_name] = pd.NA
                
                new_activity_entry = pd.DataFrame([new_activity_data], columns=ACTIVITY_LOG_COLUMNS)
                activity_log_df = pd.concat([activity_log_df, new_activity_entry], ignore_index=True)
                activity_log_df.to_csv(ACTIVITY_LOG_FILE, index=False)

                st.session_state.user_message = "Activity photo and log uploaded!"
                st.session_state.message_type = "success"
                st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error saving activity: {e}"
                st.session_state.message_type = "error"
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif active_page == "Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    st.markdown("<div class='form-field-label'><h6>Select Allowance Type:</h6></div>", unsafe_allow_html=True) # Consider styling this class
    allowance_type = st.radio(
        "", # No label for the radio group itself
        ["Travel", "Dinner", "Medical", "Internet", "Other"],
        key="allowance_type_selector",
        horizontal=True,
        label_visibility='collapsed'
    )
    allowance_amount = st.number_input("Enter Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_input")
    allowance_reason = st.text_area("Reason for Allowance:", key="allowance_reason_input", placeholder="Please provide a clear justification...")

    if st.button("Submit Allowance Request", key="submit_allowance_main", use_container_width=True, type="primary"):
        if allowance_type and allowance_amount > 0 and allowance_reason.strip():
            allowance_date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_allowance_data = {
                "Username": current_username_for_pages,
                "Type": allowance_type,
                "Amount": allowance_amount,
                "Reason": allowance_reason,
                "Date": allowance_date_str
            }
            new_allowance_entry = pd.DataFrame([new_allowance_data], columns=ALLOWANCE_COLUMNS)
            allowance_df = pd.concat([allowance_df, new_allowance_entry], ignore_index=True)
            try:
                allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                st.session_state.user_message = f"Allowance for ₹{allowance_amount:.2f} submitted."
                st.session_state.message_type = "success"
                st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error submitting allowance: {e}"
                st.session_state.message_type = "error"
                st.rerun()
        else:
            st.warning("Please complete all fields with valid values.")
    st.markdown('</div>', unsafe_allow_html=True)

elif active_page == "Goal Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_GOAL_YEAR = 2025
    current_quarter_for_goals = get_quarter_str_for_year(TARGET_GOAL_YEAR)
    status_options_goals = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    if current_user_auth_info["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True)
        admin_goal_action = st.radio(
            "Action:",
            ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR}"],
            key="admin_goal_action_selector",
            horizontal=True
        )
        if admin_goal_action == "View Team Progress":
            st.markdown(f"<h5>Team Goal Progress for {current_quarter_for_goals}</h5>", unsafe_allow_html=True)
            employee_usernames = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_usernames:
                st.info("No employees found.")
            else:
                sales_summary_list = []
                for emp_user in employee_usernames:
                    emp_goal_df = goals_df[
                        (goals_df["Username"].astype(str) == str(emp_user)) &
                        (goals_df["MonthYear"].astype(str) == str(current_quarter_for_goals))
                    ]
                    target_val, achieved_val, status_val_goal = 0.0, 0.0, "Not Set"
                    if not emp_goal_df.empty:
                        goal_data_row = emp_goal_df.iloc[0]
                        target_val = float(pd.to_numeric(goal_data_row.get("TargetAmount"), errors='coerce') or 0.0)
                        achieved_val = float(pd.to_numeric(goal_data_row.get("AchievedAmount", 0.0), errors='coerce') or 0.0)
                        status_val_goal = goal_data_row.get("Status", "N/A")
                    sales_summary_list.append({"Employee": emp_user, "Target": target_val, "Achieved": achieved_val, "Status": status_val_goal})
                
                sales_summary_df = pd.DataFrame(sales_summary_list)
                if not sales_summary_df.empty:
                    st.markdown("<h6>Individual Sales Progress:</h6>", unsafe_allow_html=True)
                    num_cols_display_sales = min(3, len(sales_summary_df)) # Max 3 cols, or fewer if less data
                    if num_cols_display_sales > 0:
                        cols_display_sales = st.columns(num_cols_display_sales)
                        for idx_sale, (index_sale, row_sale) in enumerate(sales_summary_df.iterrows()):
                            progress_percent_sale = (row_sale['Achieved'] / row_sale['Target'] * 100) if row_sale['Target'] > 0 else 0
                            donut_fig_sale = create_donut_chart(progress_percent_sale, achieved_color='#28a745') # Green for sales
                            
                            current_col_sale = cols_display_sales[idx_sale % num_cols_display_sales]
                            with current_col_sale:
                                st.markdown(f"<div class='employee-progress-item'><h6>{row_sale['Employee']}</h6><p>Target: ₹{row_sale['Target']:,.0f}<br>Achieved: ₹{row_sale['Achieved']:,.0f}</p></div>", unsafe_allow_html=True)
                                st.pyplot(donut_fig_sale, use_container_width=True)
                                st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True) # Spacer
                    
                    st.markdown("<hr style='margin-top: 10px; margin-bottom:25px;'>", unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Sales Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_sales_plot = create_team_progress_bar_chart(sales_summary_df, title="Team Sales Target vs. Achieved", target_col="Target", achieved_col="Achieved")
                    if team_bar_fig_sales_plot:
                        st.pyplot(team_bar_fig_sales_plot, use_container_width=True)
                    else:
                        st.info("No sales data to plot for the team bar chart.")
                else:
                    st.info(f"No sales goals data found for {current_quarter_for_goals} to display team progress.")

        elif admin_goal_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set or Update Employee Goal ({TARGET_GOAL_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options_admin = [u for u, d in USERS.items() if d["role"] == "employee"]
            if not employee_options_admin:
                st.warning("No employees available.")
            else:
                selected_emp_admin = st.radio("Select Employee:", employee_options_admin, key="goal_emp_selector_admin", horizontal=True)
                quarter_options_admin = [f"{TARGET_GOAL_YEAR}-Q{i}" for i in range(1, 5)]
                selected_period_admin = st.radio("Goal Period:", quarter_options_admin, key="goal_period_selector_admin", horizontal=True)
                
                # Load existing goal data if any
                existing_goal_admin_df = goals_df[
                    (goals_df["Username"].astype(str) == str(selected_emp_admin)) &
                    (goals_df["MonthYear"].astype(str) == str(selected_period_admin))
                ]
                g_desc_admin, g_target_admin, g_achieved_admin, g_status_admin = "", 0.0, 0.0, "Not Started"
                if not existing_goal_admin_df.empty:
                    g_data_admin = existing_goal_admin_df.iloc[0]
                    g_desc_admin = g_data_admin.get("GoalDescription", "")
                    g_target_admin = float(pd.to_numeric(g_data_admin.get("TargetAmount", 0.0), errors='coerce') or 0.0)
                    g_achieved_admin = float(pd.to_numeric(g_data_admin.get("AchievedAmount", 0.0), errors='coerce') or 0.0)
                    g_status_admin = g_data_admin.get("Status", "Not Started")
                    st.info(f"Editing existing goal for {selected_emp_admin} - {selected_period_admin}")

                with st.form(key=f"set_goal_form_admin_{selected_emp_admin}_{selected_period_admin}"):
                    new_desc_admin = st.text_area("Goal Description", value=g_desc_admin, key=f"desc_admin_goal_input")
                    new_target_admin = st.number_input("Target Sales (INR)", value=g_target_admin, min_value=0.0, step=1000.0, format="%.2f", key=f"target_admin_goal_input")
                    new_achieved_admin = st.number_input("Achieved Sales (INR)", value=g_achieved_admin, min_value=0.0, step=100.0, format="%.2f", key=f"achieved_admin_goal_input")
                    new_status_admin_idx = status_options_goals.index(g_status_admin) if g_status_admin in status_options_goals else 0
                    new_status_admin = st.radio("Status:", status_options_goals, index=new_status_admin_idx, horizontal=True, key=f"status_admin_goal_selector")
                    submitted_goal_admin = st.form_submit_button("Save Goal")

                if submitted_goal_admin:
                    if not new_desc_admin.strip():
                        st.warning("Goal Description is required.")
                    elif new_target_admin <= 0 and new_status_admin not in ["Cancelled", "On Hold", "Not Started"]:
                        st.warning("Target amount must be greater than 0 unless the status is Cancelled, On Hold, or Not Started.")
                    else:
                        # Logic to update or add goal
                        goals_df_copy = goals_df.copy() # Work on a copy
                        existing_indices = goals_df_copy[
                            (goals_df_copy["Username"] == selected_emp_admin) &
                            (goals_df_copy["MonthYear"] == selected_period_admin)
                        ].index

                        if not existing_indices.empty: # Update existing
                            goals_df_copy.loc[existing_indices[0], ["GoalDescription", "TargetAmount", "AchievedAmount", "Status"]] = \
                                [new_desc_admin, new_target_admin, new_achieved_admin, new_status_admin]
                            msg_verb_admin = "updated"
                        else: # Add new
                            new_goal_row_admin = pd.DataFrame([{
                                "Username": selected_emp_admin, "MonthYear": selected_period_admin,
                                "GoalDescription": new_desc_admin, "TargetAmount": new_target_admin,
                                "AchievedAmount": new_achieved_admin, "Status": new_status_admin
                            }], columns=GOALS_COLUMNS)
                            goals_df_copy = pd.concat([goals_df_copy, new_goal_row_admin], ignore_index=True)
                            msg_verb_admin = "set"
                        
                        try:
                            goals_df_copy.to_csv(GOALS_FILE, index=False)
                            goals_df = goals_df_copy # Update global DataFrame
                            st.session_state.user_message = f"Goal for {selected_emp_admin} ({selected_period_admin}) {msg_verb_admin}!"
                            st.session_state.message_type = "success"
                            st.rerun()
                        except Exception as e_admin_goal:
                            st.session_state.user_message = f"Error saving goal: {e_admin_goal}"
                            st.session_state.message_type = "error"
                            st.rerun()
    else:  # Employee View for Goal Tracker
        st.markdown(f"<h4>My Sales Goals ({TARGET_GOAL_YEAR} - Quarterly)</h4>", unsafe_allow_html=True)
        my_goals_df = goals_df[goals_df["Username"].astype(str) == str(current_username_for_pages)].copy()
        # Ensure numeric types for calculations
        for col_num_goal in ["TargetAmount", "AchievedAmount"]:
            my_goals_df[col_num_goal] = pd.to_numeric(my_goals_df[col_num_goal], errors="coerce").fillna(0.0)

        current_emp_goal_df = my_goals_df[my_goals_df["MonthYear"] == current_quarter_for_goals]
        st.markdown(f"<h5>Current Goal Period: {current_quarter_for_goals}</h5>", unsafe_allow_html=True)

        if not current_emp_goal_df.empty:
            current_goal_emp = current_emp_goal_df.iloc[0]
            target_amt_emp = current_goal_emp["TargetAmount"]
            achieved_amt_emp = current_goal_emp["AchievedAmount"]
            st.markdown(f"**Description:** {current_goal_emp.get('GoalDescription', 'N/A')}")

            col_metrics_emp_goal, col_chart_emp_goal = st.columns([0.63, 0.37]) # Ratio for metrics and chart
            with col_metrics_emp_goal:
                sub_col1_emp, sub_col2_emp = st.columns(2)
                sub_col1_emp.metric("Target", f"₹{target_amt_emp:,.0f}")
                sub_col2_emp.metric("Achieved", f"₹{achieved_amt_emp:,.0f}")
                st.metric("Status", current_goal_emp.get("Status", "In Progress"), label_visibility="labeled")
            with col_chart_emp_goal:
                progress_percent_emp_goal = (achieved_amt_emp / target_amt_emp * 100) if target_amt_emp > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:-5px;'>Sales Progress</h6>", unsafe_allow_html=True) # Adjusted margin
                donut_fig_emp_goal = create_donut_chart(progress_percent_emp_goal, "Sales Progress", achieved_color='#28a745')
                st.pyplot(donut_fig_emp_goal, use_container_width=True)
            
            st.markdown("---")
            with st.form(key=f"update_achievement_form_{current_username_for_pages}_{current_quarter_for_goals}"):
                new_achieved_val_emp = st.number_input("Update Achieved Amount (INR):", value=achieved_amt_emp, min_value=0.0, step=100.0, format="%.2f")
                submitted_ach_emp = st.form_submit_button("Update Achievement")

            if submitted_ach_emp:
                goals_df_emp_copy = goals_df.copy()
                idx_emp_goal = goals_df_emp_copy[
                    (goals_df_emp_copy["Username"] == current_username_for_pages) &
                    (goals_df_emp_copy["MonthYear"] == current_quarter_for_goals)
                ].index
                if not idx_emp_goal.empty:
                    goals_df_emp_copy.loc[idx_emp_goal[0], "AchievedAmount"] = new_achieved_val_emp
                    new_status_emp_goal = "Achieved" if new_achieved_val_emp >= target_amt_emp and target_amt_emp > 0 else "In Progress"
                    goals_df_emp_copy.loc[idx_emp_goal[0], "Status"] = new_status_emp_goal
                    try:
                        goals_df_emp_copy.to_csv(GOALS_FILE, index=False)
                        goals_df = goals_df_emp_copy # Update global
                        st.session_state.user_message = "Achievement updated!"
                        st.session_state.message_type = "success"
                        st.rerun()
                    except Exception as e_emp_ach:
                        st.session_state.user_message = f"Error updating achievement: {e_emp_ach}"
                        st.session_state.message_type = "error"
                        st.rerun()
                else:
                    st.session_state.user_message = "Could not find your current goal to update."
                    st.session_state.message_type = "error"
                    st.rerun()
        else:
            st.info(f"No sales goal set for {current_quarter_for_goals}. Please contact your administrator.")

        st.markdown("---")
        st.markdown(f"<h5>My Past Sales Goals ({TARGET_GOAL_YEAR})</h5>", unsafe_allow_html=True)
        past_goals_emp = my_goals_df[
            (my_goals_df["MonthYear"].astype(str).str.startswith(str(TARGET_GOAL_YEAR))) &
            (my_goals_df["MonthYear"].astype(str) != current_quarter_for_goals)
        ]
        if not past_goals_emp.empty:
            render_goal_chart(past_goals_emp, "Past Sales Goal Performance")
        else:
            st.info(f"No past sales goal records found for {TARGET_GOAL_YEAR}.")
    st.markdown("</div>", unsafe_allow_html=True) # Close card

# --- Payment Collection Tracker Page (Structure similar to Goal Tracker) ---
elif active_page == "Payment Collection Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_YEAR_PAYMENT = 2025
    current_quarter_payment = get_quarter_str_for_year(TARGET_YEAR_PAYMENT)
    status_options_payment = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    if current_user_auth_info["role"] == "admin":
        st.markdown("<h4>Admin: Set & Track Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_payment_action = st.radio(
            "Action:",
            ["View Team Progress", f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}"],
            key="admin_payment_action_selector", horizontal=True
        )
        if admin_payment_action == "View Team Progress":
            st.markdown(f"<h5>Team Payment Collection Progress for {current_quarter_payment}</h5>", unsafe_allow_html=True)
            employee_usernames_payment = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_usernames_payment:
                st.info("No employees found.")
            else:
                payment_summary_list = []
                for emp_pay_user in employee_usernames_payment:
                    emp_payment_goal_df = payment_goals_df[
                        (payment_goals_df["Username"] == emp_pay_user) &
                        (payment_goals_df["MonthYear"] == current_quarter_payment)
                    ]
                    target_p_val, achieved_p_val, status_p_val = 0.0, 0.0, "Not Set"
                    if not emp_payment_goal_df.empty:
                        payment_data_row = emp_payment_goal_df.iloc[0]
                        target_p_val = float(pd.to_numeric(payment_data_row.get("TargetAmount"), errors='coerce') or 0.0)
                        achieved_p_val = float(pd.to_numeric(payment_data_row.get("AchievedAmount", 0.0), errors='coerce') or 0.0)
                        status_p_val = payment_data_row.get("Status", "N/A")
                    payment_summary_list.append({"Employee": emp_pay_user, "Target": target_p_val, "Achieved": achieved_p_val, "Status": status_p_val})

                payment_summary_df = pd.DataFrame(payment_summary_list)
                if not payment_summary_df.empty:
                    st.markdown("<h6>Individual Collection Progress:</h6>", unsafe_allow_html=True)
                    num_cols_display_payment = min(3, len(payment_summary_df))
                    if num_cols_display_payment > 0:
                        cols_display_payment = st.columns(num_cols_display_payment)
                        for idx_pay, (index_pay, row_pay) in enumerate(payment_summary_df.iterrows()):
                            progress_percent_pay = (row_pay['Achieved'] / row_pay['Target'] * 100) if row_pay['Target'] > 0 else 0
                            donut_fig_pay = create_donut_chart(progress_percent_pay, achieved_color='#2070c0') # Blue for payment
                            current_col_pay = cols_display_payment[idx_pay % num_cols_display_payment]
                            with current_col_pay:
                                st.markdown(f"<div class='employee-progress-item'><h6>{row_pay['Employee']}</h6><p>Target: ₹{row_pay['Target']:,.0f}<br>Collected: ₹{row_pay['Achieved']:,.0f}</p></div>", unsafe_allow_html=True)
                                st.pyplot(donut_fig_pay, use_container_width=True)
                                st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                    
                    st.markdown("<hr style='margin-top: 10px; margin-bottom:25px;'>", unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Collection Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_payment_plot = create_team_progress_bar_chart(payment_summary_df, title="Team Collection Target vs. Achieved", target_col="Target", achieved_col="Achieved")
                    if team_bar_fig_payment_plot:
                        # Customize 'Achieved' bar color for payment chart
                        for bar_group in team_bar_fig_payment_plot.axes[0].containers:
                            if bar_group.get_label() == 'Achieved':
                                for bar in bar_group:
                                    bar.set_color('#2070c0') # Blue for payment achieved
                        st.pyplot(team_bar_fig_payment_plot, use_container_width=True)
                    else:
                        st.info("No collection data to plot for team bar chart.")
                else:
                    st.info(f"No payment collection data found for {current_quarter_payment}.")

        elif admin_payment_action == f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}":
            # ... (Admin form for setting/editing payment goals - similar to sales goals) ...
            st.info("Admin form for setting/editing payment goals - To be implemented fully.")
    else: # Employee View for Payment Collection Tracker
        # ... (Employee view for payment goals - similar to sales goals) ...
        st.info("Employee view for payment collection goals - To be implemented fully.")
    st.markdown("</div>", unsafe_allow_html=True) # Close card

# --- View Logs Page ---
elif active_page == "View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 View Logs</h3>", unsafe_allow_html=True)

    def display_activity_logs_with_photos(df_logs, user_name_for_header):
        if df_logs.empty:
            st.info(f"No field activity logs found for {user_name_for_header}.")
            return
        df_logs_sorted = df_logs.sort_values(by="Timestamp", ascending=False).copy()
        st.markdown(f"<h5>Field Activity Logs for: {user_name_for_header}</h5>", unsafe_allow_html=True)
        for index_log, row_log in df_logs_sorted.iterrows():
            st.markdown("---")
            col_details_log, col_photo_log = st.columns([0.7, 0.3])
            with col_details_log:
                location_str = "Not Recorded"
                if pd.notna(row_log.get('Latitude')) and pd.notna(row_log.get('Longitude')):
                    location_str = f"Lat: {row_log.get('Latitude'):.4f}, Lon: {row_log.get('Longitude'):.4f}"
                st.markdown(f"**Timestamp:** {row_log['Timestamp']}<br>"
                            f"**Description:** {row_log.get('Description', 'N/A')}<br>"
                            f"**Location:** {location_str}", unsafe_allow_html=True)
                if pd.notna(row_log.get('ImageFile')) and row_log['ImageFile'] != "":
                    st.caption(f"Photo ID: {row_log['ImageFile']}")
                else:
                    st.caption("No photo associated with this activity.")
            with col_photo_log:
                if pd.notna(row_log.get('ImageFile')) and row_log['ImageFile'] != "":
                    image_path_display = os.path.join(ACTIVITY_PHOTOS_DIR, str(row_log['ImageFile']))
                    if os.path.exists(image_path_display):
                        try:
                            st.image(image_path_display, width=150)
                        except Exception as img_e_log:
                            st.warning(f"Could not display image {row_log['ImageFile']}: {img_e_log}")
                    else:
                        st.caption(f"Image file missing: {row_log['ImageFile']}")
        st.markdown("---") # Final divider

    def display_general_attendance_logs(df_att_logs, user_name_att_header):
        if df_att_logs.empty:
            st.warning(f"No general attendance records found for {user_name_att_header}.")
            return
        df_att_logs_sorted = df_att_logs.sort_values(by="Timestamp", ascending=False).copy()
        st.markdown(f"<h5>General Attendance Records for: {user_name_att_header}</h5>", unsafe_allow_html=True)
        
        cols_to_show_att = ["Type", "Timestamp"]
        if 'Latitude' in df_att_logs_sorted.columns and 'Longitude' in df_att_logs_sorted.columns:
            df_att_logs_sorted['Location'] = df_att_logs_sorted.apply(
                lambda r: f"Lat: {r['Latitude']:.4f}, Lon: {r['Longitude']:.4f}"
                if pd.notna(r['Latitude']) and pd.notna(r['Longitude']) else "Not Recorded", axis=1
            )
            cols_to_show_att.append('Location')
        
        st.dataframe(df_att_logs_sorted[cols_to_show_att], use_container_width=True, hide_index=True)

    if current_user_auth_info["role"] == "admin":
        st.markdown("<h4>Admin: View Employee Records</h4>", unsafe_allow_html=True)
        employee_names_logs_admin = [uname for uname in USERS.keys() if USERS[uname]["role"] == "employee"]
        if not employee_names_logs_admin:
            st.info("No employees found to display logs for.")
        else:
            selected_employee_for_logs = st.selectbox(
                "Select Employee:",
                employee_names_logs_admin,
                key="log_employee_selector_admin"
            )
            if selected_employee_for_logs:
                # Activity Logs
                emp_activity_logs_df = activity_log_df[activity_log_df["Username"] == selected_employee_for_logs]
                display_activity_logs_with_photos(emp_activity_logs_df, selected_employee_for_logs)
                st.markdown("<br><hr><br>", unsafe_allow_html=True) # Spacer and divider

                # General Attendance
                emp_attendance_logs_df = attendance_df[attendance_df["Username"] == selected_employee_for_logs]
                display_general_attendance_logs(emp_attendance_logs_df, selected_employee_for_logs)
                st.markdown("---")

                # Allowances
                st.markdown(f"<h5>Allowances for {selected_employee_for_logs}</h5>", unsafe_allow_html=True)
                emp_allowance_logs_df = allowance_df[allowance_df["Username"] == selected_employee_for_logs]
                if not emp_allowance_logs_df.empty:
                    st.dataframe(emp_allowance_logs_df.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
                else:
                    st.info("No allowance records found.")
                st.markdown("---")
                
                # Sales Goals
                st.markdown(f"<h5>Sales Goals for {selected_employee_for_logs}</h5>", unsafe_allow_html=True)
                emp_sales_goals_log_df = goals_df[goals_df["Username"] == selected_employee_for_logs]
                if not emp_sales_goals_log_df.empty:
                    st.dataframe(emp_sales_goals_log_df.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
                else:
                    st.info("No sales goals records found.")
                st.markdown("---")

                # Payment Collection Goals
                st.markdown(f"<h5>Payment Collection Goals for {selected_employee_for_logs}</h5>", unsafe_allow_html=True)
                emp_payment_goals_log_df = payment_goals_df[payment_goals_df["Username"] == selected_employee_for_logs]
                if not emp_payment_goals_log_df.empty:
                    st.dataframe(emp_payment_goals_log_df.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
                else:
                    st.info("No payment collection goals found.")
    else: # Employee view of logs
        st.markdown("<h4>My Records</h4>", unsafe_allow_html=True)
        # Activity Logs
        my_activity_logs_df = activity_log_df[activity_log_df["Username"] == current_username_for_pages]
        display_activity_logs_with_photos(my_activity_logs_df, current_username_for_pages)
        st.markdown("<br><hr><br>", unsafe_allow_html=True)

        # General Attendance
        my_attendance_logs_df = attendance_df[attendance_df["Username"] == current_username_for_pages]
        display_general_attendance_logs(my_attendance_logs_df, current_username_for_pages)
        st.markdown("---")

        # Allowances
        st.markdown("<h5>My Allowances</h5>", unsafe_allow_html=True)
        my_allowance_logs_df = allowance_df[allowance_df["Username"] == current_username_for_pages]
        if not my_allowance_logs_df.empty:
            st.dataframe(my_allowance_logs_df.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
        else:
            st.info("You have no allowance records.")
        st.markdown("---")

        # Sales Goals
        st.markdown("<h5>My Sales Goals</h5>", unsafe_allow_html=True)
        my_sales_goals_log_df = goals_df[goals_df["Username"] == current_username_for_pages]
        if not my_sales_goals_log_df.empty:
            st.dataframe(my_sales_goals_log_df.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
        else:
            st.info("You have no sales goals records.")
        st.markdown("---")

        # Payment Collection Goals
        st.markdown("<h5>My Payment Collection Goals</h5>", unsafe_allow_html=True)
        my_payment_goals_log_df = payment_goals_df[payment_goals_df["Username"] == current_username_for_pages]
        if not my_payment_goals_log_df.empty:
            st.dataframe(my_payment_goals_log_df.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
        else:
            st.info("You have no payment collection goals records.")
    st.markdown('</div>', unsafe_allow_html=True) # Close card

# --- Create Order Page ---
elif active_page == "Create Order":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🛒 Create New Order</h3>", unsafe_allow_html=True) # Added icon to title

    try:
        stores_df = pd.read_csv("agri_stores.csv")
        products_df = pd.read_csv("symplanta_products_with_images.csv")
    except FileNotFoundError as e_order_csv:
        st.error(f"Error: Required CSV file not found for 'Create Order' page. Please ensure 'agri_stores.csv' and 'symplanta_products_with_images.csv' are present. Details: {e_order_csv}")
        st.stop()
    except Exception as e_order_load:
        st.error(f"An error occurred while loading data for 'Create Order' page: {e_order_load}")
        st.stop()

    store_name_order = st.selectbox("Select Store", sorted(stores_df["StoreName"].dropna().astype(str).unique()), key="order_store_selector")
    
    product_name_order = st.selectbox(
        "Select Product",
        sorted(products_df["Product Name"].dropna().astype(str).unique()),
        key="order_product_selector"
    )
    
    product_sizes_options_df = products_df[products_df["Product Name"] == product_name_order]
    
    selected_size_order = None
    if not product_sizes_options_df.empty:
        size_options = sorted(product_sizes_options_df["Size"].dropna().astype(str).unique())
        if size_options:
            selected_size_order = st.selectbox(
                "Select Size",
                size_options,
                key="order_size_selector"
            )
        else:
            st.info(f"No sizes available for product: {product_name_order}")
    else:
        st.info(f"No product details found for: {product_name_order}")

    quantity_order = st.number_input("Enter Quantity", min_value=1, value=1, key="order_quantity_input")

    if selected_size_order and st.button("Add to Order", type="primary", key="order_add_button", use_container_width=True):
        if "order_items" not in st.session_state:
            st.session_state.order_items = []

        selected_product_details_df = product_sizes_options_df[product_sizes_options_df["Size"] == selected_size_order]
        
        if not selected_product_details_df.empty:
            product_to_add = selected_product_details_df.iloc[0]
            unit_price_order = pd.to_numeric(product_to_add.get("Price"), errors='coerce')

            if pd.notna(unit_price_order):
                order_item = {
                    "Store": store_name_order,
                    "Product": product_name_order,
                    "Size": selected_size_order,
                    "Quantity": quantity_order,
                    "Unit Price": unit_price_order,
                    "Total": unit_price_order * quantity_order
                }
                st.session_state.order_items.append(order_item)
                st.success(f"{quantity_order} x {product_name_order} ({selected_size_order}) added to order!")
            else:
                st.warning(f"Price information is missing or invalid for {product_name_order} ({selected_size_order}). Cannot add to order.")
        else:
            st.warning(f"Details for {product_name_order} ({selected_size_order}) not found. Please recheck selection.")

    if "order_items" in st.session_state and st.session_state.order_items:
        st.subheader("🧾 Order Summary")
        current_order_df = pd.DataFrame(st.session_state.order_items)
        # Ensure numeric types for display formatting
        current_order_df["Unit Price"] = pd.to_numeric(current_order_df["Unit Price"], errors='coerce').fillna(0)
        current_order_df["Total"] = pd.to_numeric(current_order_df["Total"], errors='coerce').fillna(0)
        
        display_order_df = current_order_df.copy()
        display_order_df["Unit Price"] = display_order_df["Unit Price"].apply(lambda x_price: f"₹{x_price:,.2f}")
        display_order_df["Total"] = display_order_df["Total"].apply(lambda x_total: f"₹{x_total:,.2f}")
        
        st.dataframe(display_order_df[["Store", "Product", "Size", "Quantity", "Unit Price", "Total"]], use_container_width=True, hide_index=True)
        grand_total_order = current_order_df['Total'].sum()
        st.markdown(f"<h4 style='text-align: right; margin-top: 1rem;'>Grand Total: ₹{grand_total_order:,.2f}</h4>", unsafe_allow_html=True)
        
        # Option to clear order
        if st.button("Clear Order", key="clear_order_button"):
            st.session_state.order_items = []
            st.info("Order cleared.")
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True) # Close card

# Fallback for any undefined page (should not happen with current setup)
# else:
#     st.error("Page not found.")
