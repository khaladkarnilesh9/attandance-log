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

# --- Bootstrap and Material Icons CDN ---
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
""", unsafe_allow_html=True)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Apply Roboto to the whole app, and Material Symbols Outlined for icons */
    body, .stButton button, .stTextInput input, .stTextArea textarea, .stSelectbox select {
        font-family: 'Roboto', sans-serif;
    }
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        font-size: 22px; 
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
        vertical-align: middle; 
    }

    /* Streamlit's default sidebar container */
    section[data-testid="stSidebar"] > div:first-child {
        padding: 0 !important; /* Remove Streamlit's default padding */
    }

    .sidebar-content-wrapper {
        background-color: #f8f9fa !important; /* Bootstrap 'bg-light' equivalent */
        height: 100%; 
        display: flex;
        flex-direction: column;
        padding: 1rem; /* Overall padding for sidebar content */
    }

    /* Styling for each navigation item's container div */
    .sidebar-nav-item {
        display: flex !important;         /* Use flex to layout icon col and button col */
        align-items: center !important;   /* Vertically center content of columns */
        width: 100% !important;
        padding: 0.5rem 0.75rem !important; /* Padding for the whole item (row) */
        margin-bottom: 0.125rem !important;
        border-radius: 0.375rem !important; /* Bootstrap standard border-radius */
        text-decoration: none !important;
        color: #212529 !important;        /* Default text/icon color */
        transition: background-color 0.15s ease-in-out, color 0.15s ease-in-out;
    }
    .sidebar-nav-item:hover { /* Hover for the whole item container */
        background-color: #e9ecef !important; /* Light gray hover */
        color: #000 !important; /* Darker text/icon on hover */
    }
    
    /* Icon container within the nav item (first column) */
    .sidebar-nav-item .icon-container {
        display: flex;
        align-items: center;
        justify-content: center; /* Center icon in its column */
        /* margin-right: 8px; /* Space between icon and button column if not using column gap */
    }
    .sidebar-nav-item .icon-container .material-symbols-outlined {
        font-size: 20px !important;
        color: inherit; /* Inherit color from .sidebar-nav-item parent */
    }

    /* Styling for st.button (text part) to be transparent and fit in */
    .sidebar-nav-item .stButton button {
        display: block !important;
        width: 100% !important;
        text-align: left !important;
        border: none !important;
        padding: 0 !important; 
        margin: 0 !important; 
        font-weight: 400 !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        background-color: transparent !important; /* Make button background transparent */
        color: inherit !important; /* Inherit text color from .sidebar-nav-item */
        box-shadow: none !important;
        outline: none !important;
        cursor: pointer; 
    }
    /* Hover/focus for the button itself - should be minimal as .sidebar-nav-item handles visual hover */
     .sidebar-nav-item .stButton button:hover,
     .sidebar-nav-item .stButton button:focus,
     .sidebar-nav-item .stButton button:active {
        background-color: transparent !important; /* Keep transparent */
        /* color: inherit !important; */ /* Color is already inherited */
        box-shadow: none !important;
        outline: none !important;
    }

    /* Active navigation item styling (applied to the container div .sidebar-nav-item) */
    .sidebar-nav-item.active-nav-item {
        color: #fff !important; /* This will be inherited by icon and button text */
        background-color: #0d6efd !important; /* Bootstrap primary color */
    }
    .sidebar-nav-item.active-nav-item:hover { 
        color: #fff !important;
        background-color: #0b5ed7 !important; /* Darker primary on hover for active item */
    }
    /* Icon and button text color for active item (already inherited, but can be explicit) */
    .sidebar-nav-item.active-nav-item .icon-container .material-symbols-outlined {
        color: #fff !important; 
    }
    .sidebar-nav-item.active-nav-item .stButton button {
         color: #fff !important; 
         font-weight: 500 !important; /* Bolder text for active button */
    }

    /* Welcome text and user info */
    .welcome-text-sidebar {
        font-size: 1.1rem;
        font-weight: 500;
        color: #212529;
        margin-bottom: 0.5rem;
        padding-left: 0.5rem; /* Optional: align with nav item padding */
    }
    .user-profile-img-container {
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .user-profile-img-container img {
        border-radius: 50%;
        width: 80px;
        height: 80px;
        object-fit: cover;
        border: 2px solid #dee2e6; /* Bootstrap light border */
    }
    .user-position-text {
        text-align: center;
        font-size: 0.875em;
        color: #6c757d; /* Bootstrap muted text color */
        margin-bottom: 1rem;
    }
    .sidebar-content-wrapper hr {
        margin: 1rem 0;
        opacity: 0.25;
    }

    /* Logout Button Styling */
    .logout-button-container {
        margin-top: auto; /* Pushes logout to the bottom */
        padding-top: 1rem; /* Space above logout */
    }
    .logout-button-container .stButton button {
        background-color: #6c757d !important; /* Bootstrap secondary/gray */
        color: white !important;
        border: none !important;
        width: 100% !important;
        font-weight: 500 !important;
        display: flex !important; 
        align-items: center !important;
        justify-content: center !important; /* Center if only text or icon+text */
        padding: 0.5rem 1rem !important;
    }
    .logout-button-container .stButton button:hover {
        background-color: #5a6268 !important; /* Darker gray on hover */
        color: white !important;
    }
    /* For an icon in logout button if using emoji/text prefix in label */
    /* .logout-button-container .stButton button .material-symbols-outlined {
        margin-right: 8px; 
        font-size: 20px;
    } */

    /* Global message notification styling */
    .custom-notification {
        padding: 10px; border-radius: 5px; margin-bottom: 15px; border: 1px solid transparent;
    }
    .custom-notification.success {
        color: #0f5132; background-color: #d1e7dd; border-color: #badbcc;
    }
    .custom-notification.error {
        color: #842029; background-color: #f8d7da; border-color: #f5c2c7;
    }
    .custom-notification.info {
        color: #055160; background-color: #cff4fc; border-color: #b6effb;
    }
    .custom-notification.warning {
        color: #664d03; background-color: #fff3cd; border-color: #ffecb5;
    }
</style>
""", unsafe_allow_html=True)

# --- Credentials & User Info ---
USERS = {
    "Geetali": {"password": "Geetali123", "role": "employee", "position": "Software Engineer", "profile_photo": "images/geetali.png"},
    "Nilesh": {"password": "Nilesh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "Vishal": {"password": "Vishal123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/vishal.png"},
    "Santosh": {"password": "Santosh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/santosh.png"},
    "Deepak": {"password": "Deepak123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/deepak.png"},
    "Rahul": {"password": "Rahul123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/rahul.png"},
    "admin": {"password": "admin123", "role": "admin", "position": "System Administrator", "profile_photo": "images/admin.png"}
}

# --- Create dummy images folder and placeholder images ---
if not os.path.exists("images"):
    try: os.makedirs("images")
    except OSError: pass # Folder already exists or other OS error
if PILLOW_INSTALLED:
    for user_key, user_data in USERS.items():
        img_path = user_data.get("profile_photo")
        if img_path and not os.path.exists(img_path):
            try:
                img = Image.new('RGB', (120, 120), color = (200, 220, 240)); draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", 40)
                except IOError: font = ImageFont.load_default()
                text = user_key[:2].upper()
                # PIL text drawing methods changed over versions
                if hasattr(draw, 'textbbox'): # More modern PIL
                    bbox = draw.textbbox((0,0), text, font=font); text_width, text_height = bbox[2]-bbox[0], bbox[3]-bbox[1]
                    text_x, text_y = (120-text_width)/2, (120-text_height)/2 - bbox[1] # Adjust y based on bbox[1] for better centering
                elif hasattr(draw, 'textsize'): # Older PIL
                    text_width, text_height = draw.textsize(text, font=font); text_x, text_y = (120-text_width)/2, (120-text_height)/2
                else: # Fallback if textsize and textbbox not available
                    text_x, text_y = 30,30 # Approximate center
                draw.text((text_x, text_y), text, fill=(28,78,128), font=font); img.save(img_path)
            except Exception: pass # Ignore if placeholder creation fails

# --- File Paths & Timezone & Directories ---
ATTENDANCE_FILE = "attendance.csv"; ALLOWANCE_FILE = "allowances.csv"; GOALS_FILE = "goals.csv"; PAYMENT_GOALS_FILE = "payment_goals.csv"
ACTIVITY_LOG_FILE = "activity_log.csv"
ACTIVITY_PHOTOS_DIR = "activity_photos"
ATTENDANCE_PHOTOS_DIR = "attendance_photos"

for dir_path in [ACTIVITY_PHOTOS_DIR, ATTENDANCE_PHOTOS_DIR]:
    if not os.path.exists(dir_path):
        try: os.makedirs(dir_path)
        except OSError: pass

TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError: st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'. Please use a valid IANA timezone."); st.stop()

def get_current_time_in_tz(): return datetime.now(timezone.utc).astimezone(tz)

def get_quarter_str_for_year(year, for_current_display=False):
    now_month = get_current_time_in_tz().month
    if 1 <= now_month <= 3: return f"{year}-Q1"
    elif 4 <= now_month <= 6: return f"{year}-Q2"
    elif 7 <= now_month <= 9: return f"{year}-Q3"
    else: return f"{year}-Q4"

# --- Load or create data ---
def load_data(path, columns):
    if os.path.exists(path):
        try:
            if os.path.getsize(path) > 0:
                df = pd.read_csv(path)
                for col in columns: # Ensure all expected columns exist
                    if col not in df.columns: df[col] = pd.NA
                num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude"]
                for nc in num_cols:
                    if nc in df.columns: df[nc] = pd.to_numeric(df[nc], errors='coerce')
                return df
            else: return pd.DataFrame(columns=columns)
        except pd.errors.EmptyDataError: return pd.DataFrame(columns=columns)
        except Exception as e: st.error(f"Error loading {path}: {e}."); return pd.DataFrame(columns=columns)
    else: # File does not exist, create it with headers
        df = pd.DataFrame(columns=columns);
        try: df.to_csv(path, index=False)
        except Exception as e: st.warning(f"Could not create {path}: {e}")
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

# --- Charting Functions ---
def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty: st.warning("No data available to plot."); return
    df_chart = df.copy()
    df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear", value_vars=["TargetAmount", "AchievedAmount"], var_name="Metric", value_name="Amount")
    if df_melted.empty: st.warning(f"No data to plot for {chart_title} after processing."); return
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group",
                 labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"},
                 title=chart_title, color_discrete_map={'TargetAmount': '#3498db', 'AchievedAmount': '#2ecc71'})
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric')
    fig.update_xaxes(type='category'); st.plotly_chart(fig, use_container_width=True)

def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#2ecc71', remaining_color='#f0f0f0', center_text_color=None):
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=90); fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    progress_percentage = max(0.0, min(float(progress_percentage), 100.0))
    remaining_percentage = 100.0 - progress_percentage
    if progress_percentage <= 0.01: sizes, slice_colors, actual_progress_display = [100.0], [remaining_color], 0.0
    elif progress_percentage >= 99.99: sizes, slice_colors, actual_progress_display = [100.0], [achieved_color], 100.0
    else: sizes, slice_colors, actual_progress_display = [progress_percentage, remaining_percentage], [achieved_color, remaining_color], progress_percentage
    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.4, edgecolor='white'))
    centre_circle = plt.Circle((0,0),0.60,fc='white'); fig.gca().add_artist(centre_circle)
    text_color_to_use = center_text_color if center_text_color else (achieved_color if actual_progress_display > 0 else '#4A4A4A')
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=12, fontweight='bold', color=text_color_to_use)
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0); return fig

def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee"):
    if summary_df.empty: return None
    labels = summary_df[user_col].tolist(); target_amounts = summary_df[target_col].fillna(0).tolist(); achieved_amounts = summary_df[achieved_col].fillna(0).tolist()
    x = np.arange(len(labels)); width = 0.35
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.8), 5), dpi=100)
    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color='#3498db', alpha=0.8)
    rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color='#2ecc71', alpha=0.8)
    ax.set_ylabel('Amount (INR)', fontsize=10); ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9); ax.legend(fontsize=9)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0: ax.annotate(f'{height:,.0f}', xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=7, color='#333')
    autolabel(rects1); autolabel(rects2); fig.tight_layout(pad=1.5); return fig

# --- Session State Initialization ---
if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}

# --- Login Logic ---
if not st.session_state.auth["logged_in"]:
    st.title("TrackSphere Login")
    message_placeholder_login = st.empty()
    if st.session_state.user_message: # Display pending messages from previous actions
        message_placeholder_login.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
        st.session_state.user_message = None; st.session_state.message_type = None # Clear after display
    
    st.markdown("<h3>🔐 Login</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname")
    pwd = st.text_input("Password", type="password", key="login_pwd")
    if st.button("Login", key="login_button", type="primary"): 
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = "Login successful!"; st.session_state.message_type = "success"
            st.rerun() # Rerun to show main app and clear login form
        else: st.error("Invalid username or password.") # This error shows directly
    st.stop() # Stop execution here if not logged in

# --- Main Application (Post-Login) ---
current_user = st.session_state.auth # User is authenticated at this point

# Global Message Display for Main Application
message_placeholder_main = st.empty()
if "user_message" in st.session_state and st.session_state.user_message:
    message_type_main = st.session_state.get("message_type", "info")
    message_placeholder_main.markdown(
        f"<div class='custom-notification {message_type_main}'>{st.session_state.user_message}</div>",
        unsafe_allow_html=True
    )
    st.session_state.user_message = None # Clear message after displaying it
    st.session_state.message_type = None

# --- Sidebar Navigation ---
nav_options_with_icons = [
    {"label": "Attendance", "icon": "schedule"},
    {"label": "Upload Activity Photo", "icon": "add_a_photo"},
    {"label": "Allowance", "icon": "payments"},
    {"label": "Goal Tracker", "icon": "emoji_events"},
    {"label": "Payment Collection Tracker", "icon": "receipt_long"},
    {"label": "View Logs", "icon": "wysiwyg"},
    {"label": "Create Order", "icon": "add_shopping_cart"}
]

if "active_page" not in st.session_state: # Initialize default page
    st.session_state.active_page = nav_options_with_icons[0]["label"]

def set_active_page_callback(page_name):
    st.session_state.active_page = page_name

with st.sidebar:
    st.markdown('<div class="sidebar-content-wrapper">', unsafe_allow_html=True)

    # User Info
    st.markdown(f"<div class='welcome-text-sidebar'>Welcome, {current_user['username']}!</div>", unsafe_allow_html=True)
    user_sidebar_info = USERS.get(current_user["username"], {})
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]):
        st.markdown("<div class='user-profile-img-container'>", unsafe_allow_html=True)
        st.image(user_sidebar_info["profile_photo"])
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='user-position-text'>{user_sidebar_info.get('position', 'N/A')}</div>",
        unsafe_allow_html=True
    )
    st.markdown("<hr>", unsafe_allow_html=True)

    # Navigation Items
    st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True) 
    for i, item in enumerate(nav_options_with_icons):
        option_label = item["label"]
        option_icon = item["icon"]
        button_key = f"nav_btn_{i}" # Simple, unique key
        is_active = (st.session_state.active_page == option_label)
        active_class = "active-nav-item" if is_active else ""

        st.markdown(f'<div class="sidebar-nav-item {active_class}">', unsafe_allow_html=True)
        icon_col, text_col = st.columns([1, 4], gap="small") # [icon_weight, text_weight]
        with icon_col:
            st.markdown(f'<div class="icon-container"><span class="material-symbols-outlined">{option_icon}</span></div>', unsafe_allow_html=True)
        with text_col:
            st.button( # This button does not use unsafe_allow_html
                label=option_label,
                key=button_key,
                on_click=set_active_page_callback,
                args=(option_label,),
                use_container_width=True
            )
        st.markdown('</div>', unsafe_allow_html=True) # Close .sidebar-nav-item
    st.markdown('</div>', unsafe_allow_html=True) # Close .sidebar-nav

    # Logout Button
    st.markdown('<div class="logout-button-container">', unsafe_allow_html=True)
    if st.button(label="➡️ Logout", key="logout_button_sidebar", use_container_width=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."
        st.session_state.message_type = "info"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True) # Close .logout-button-container
    
    st.markdown('</div>', unsafe_allow_html=True) # Close .sidebar-content-wrapper

# --- Main Content Area Based on Active Page ---
if st.session_state.active_page == "Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True) 
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled for attendance. Photos for specific activities can be uploaded from the 'Upload Activity Photo' section.", icon="ℹ️")
    st.markdown("---"); st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2); common_data = {"Username": current_user["username"], "Latitude": pd.NA, "Longitude": pd.NA}

    def process_general_attendance(attendance_type):
        global attendance_df # Ensure modification of global df
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_data = {"Type": attendance_type, "Timestamp": now_str_display, **common_data}
        for col_name in ATTENDANCE_COLUMNS: # Ensure all columns are present
            if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
        new_entry_df = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
        
        # It's safer to reload data after modification if multiple users/sessions could modify it
        # For single user session, direct concat and save is okay.
        current_attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS) # Load fresh data
        updated_attendance_df = pd.concat([current_attendance_df, new_entry_df], ignore_index=True)
        try:
            updated_attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            attendance_df = updated_attendance_df # Update global df variable
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."
            st.session_state.message_type = "success"
            st.rerun()
        except Exception as e:
            st.session_state.user_message = f"Error saving attendance: {e}"
            st.session_state.message_type = "error"
            st.rerun()

    with col1:
        if st.button("✅ Check In", key="check_in_btn_main_no_photo", use_container_width=True, type="primary"):
            process_general_attendance("Check-In")
    with col2:
        if st.button("🚪 Check Out", key="check_out_btn_main_no_photo", use_container_width=True, type="primary"):
            process_general_attendance("Check-Out")
    st.markdown('</div></div>', unsafe_allow_html=True)

elif st.session_state.active_page == "Upload Activity Photo":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat, current_lon = pd.NA, pd.NA # Placeholder, actual location capture not implemented
    with st.form(key="activity_photo_form"):
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description of activity/visit:", key="activity_desc")
        img_file_buffer_activity = st.camera_input("Take a picture of your activity/visit", key="activity_camera_input")
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo and Log Activity")
    
    if submit_activity_photo:
        if img_file_buffer_activity is None: st.warning("Please take a picture before submitting.")
        elif not activity_description.strip(): st.warning("Please provide a description for the activity.")
        else:
            now_for_filename = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S")
            now_for_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            image_filename_activity = f"{current_user['username']}_activity_{now_for_filename}.jpg"
            image_path_activity = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_activity)
            try:
                with open(image_path_activity, "wb") as f: f.write(img_file_buffer_activity.getbuffer())
                
                new_activity_data = {
                    "Username": current_user["username"], 
                    "Timestamp": now_for_display, 
                    "Description": activity_description, 
                    "ImageFile": image_filename_activity, 
                    "Latitude": current_lat, 
                    "Longitude": current_lon
                }
                for col_name in ACTIVITY_LOG_COLUMNS: # Ensure all columns are present
                    if col_name not in new_activity_data: new_activity_data[col_name] = pd.NA
                new_activity_entry_df = pd.DataFrame([new_activity_data], columns=ACTIVITY_LOG_COLUMNS)
                
                current_activity_log_df = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS)
                updated_activity_log_df = pd.concat([current_activity_log_df, new_activity_entry_df], ignore_index=True)
                updated_activity_log_df.to_csv(ACTIVITY_LOG_FILE, index=False)
                activity_log_df = updated_activity_log_df # Update global df

                st.session_state.user_message = "Activity photo and log uploaded!"
                st.session_state.message_type = "success"; st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error saving activity: {e}"
                st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.active_page == "Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    st.markdown("<h6>Select Allowance Type:</h6>", unsafe_allow_html=True) # Removed div for simplicity
    a_type = st.radio("Allowance Type", ["Travel", "Dinner", "Medical", "Internet", "Other"], 
                      key="allowance_type_radio_main", horizontal=True, label_visibility='collapsed') # Use label
    amount = st.number_input("Enter Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_main")
    reason = st.text_area("Reason for Allowance:", key="allowance_reason_main", placeholder="Please provide a clear justification...")
    
    if st.button("Submit Allowance Request", key="submit_allowance_btn_main", use_container_width=True, type="primary"):
        if a_type and amount > 0 and reason.strip():
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry_data = {
                "Username": current_user["username"], "Type": a_type, 
                "Amount": amount, "Reason": reason, "Date": date_str
            }
            new_entry_df = pd.DataFrame([new_entry_data], columns=ALLOWANCE_COLUMNS)
            
            current_allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
            updated_allowance_df = pd.concat([current_allowance_df, new_entry_df], ignore_index=True)
            try:
                updated_allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                allowance_df = updated_allowance_df # Update global df
                st.session_state.user_message = f"Allowance for ₹{amount:.2f} submitted."
                st.session_state.message_type = "success"; st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error submitting allowance: {e}"
                st.session_state.message_type = "error"; st.rerun()
        else: st.warning("Please complete all fields with valid values.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.active_page == "Goal Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_GOAL_YEAR = 2025; current_quarter_for_display = get_quarter_str_for_year(TARGET_GOAL_YEAR)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    
    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR}"], 
                                key="admin_goal_action_radio_2025_q", horizontal=True)
        if admin_action == "View Team Progress":
            st.markdown(f"<h5>Team Goal Progress for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            employee_users = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users: st.info("No employees found.")
            else:
                # Load fresh goals_df for admin view
                current_goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
                summary_list_sales = []
                for emp_name in employee_users:
                    emp_current_goal = current_goals_df[
                        (current_goals_df["Username"].astype(str) == str(emp_name)) & 
                        (current_goals_df["MonthYear"].astype(str) == str(current_quarter_for_display))
                    ]
                    target, achieved, status_val = 0.0, 0.0, "Not Set"
                    if not emp_current_goal.empty:
                        g_data = emp_current_goal.iloc[0]
                        target = float(pd.to_numeric(g_data.get("TargetAmount"), errors='coerce') or 0.0)
                        achieved = float(pd.to_numeric(g_data.get("AchievedAmount", 0.0), errors='coerce') or 0.0)
                        status_val = g_data.get("Status", "N/A")
                    summary_list_sales.append({"Employee": emp_name, "Target": target, "Achieved": achieved, "Status": status_val})
                
                summary_df_sales = pd.DataFrame(summary_list_sales)
                if not summary_df_sales.empty:
                    st.markdown("<h6>Individual Sales Progress:</h6>", unsafe_allow_html=True)
                    num_cols_sales = min(3, len(summary_df_sales)) # Adjust num cols if few employees
                    if num_cols_sales > 0:
                        cols_sales = st.columns(num_cols_sales)
                        col_idx_sales = 0
                        for index, row in summary_df_sales.iterrows():
                            progress_percent = (row['Achieved'] / row['Target'] * 100) if row['Target'] > 0 else 0
                            donut_fig = create_donut_chart(progress_percent, achieved_color='#28a745')
                            current_col_sales = cols_sales[col_idx_sales % num_cols_sales]
                            with current_col_sales:
                                st.markdown(f"<div class='employee-progress-item'><h6>{row['Employee']}</h6><p>Target: ₹{row['Target']:,.0f}<br>Achieved: ₹{row['Achieved']:,.0f}</p></div>", unsafe_allow_html=True)
                                st.pyplot(donut_fig, use_container_width=True)
                                st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                            col_idx_sales += 1
                    
                    st.markdown("<hr style='margin-top: 10px; margin-bottom:25px;'>", unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Sales Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_sales = create_team_progress_bar_chart(summary_df_sales, title="Team Sales Target vs. Achieved", target_col="Target", achieved_col="Achieved")
                    if team_bar_fig_sales: st.pyplot(team_bar_fig_sales, use_container_width=True)
                    else: st.info("No sales data to plot for the team bar chart.")
                else: st.info(f"No sales goals data found for {current_quarter_for_display} to display team progress.")

        elif admin_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set or Update Employee Goal ({TARGET_GOAL_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employee_options: st.warning("No employees available.")
            else:
                selected_emp = st.radio("Select Employee:", employee_options, key="goal_emp_radio_admin_set", horizontal=True)
                quarter_options = [f"{TARGET_GOAL_YEAR}-Q{i}" for i in range(1,5)]
                selected_period = st.radio("Goal Period:", quarter_options, key="goal_period_radio_admin_set", horizontal=True)
                
                editable_goals_df = load_data(GOALS_FILE, GOALS_COLUMNS).copy() # Load fresh for editing
                existing_g_series = editable_goals_df[
                    (editable_goals_df["Username"].astype(str) == str(selected_emp)) & 
                    (editable_goals_df["MonthYear"].astype(str) == str(selected_period))
                ]
                g_desc, g_target, g_achieved, g_status = "", 0.0, 0.0, "Not Started"
                
                if not existing_g_series.empty:
                    g_data = existing_g_series.iloc[0]
                    g_desc = g_data.get("GoalDescription","")
                    g_target = float(pd.to_numeric(g_data.get("TargetAmount",0.0),errors='coerce') or 0.0)
                    g_achieved = float(pd.to_numeric(g_data.get("AchievedAmount",0.0),errors='coerce') or 0.0)
                    g_status = g_data.get("Status","Not Started")
                    st.info(f"Editing goal for {selected_emp} - {selected_period}")

                with st.form(key=f"set_goal_form_{selected_emp}_{selected_period}_admin"):
                    new_desc = st.text_area("Goal Description", value=g_desc, key=f"desc_{selected_emp}_{selected_period}_g_admin")
                    new_target = st.number_input("Target Sales (INR)", value=g_target, min_value=0.0, step=1000.0, format="%.2f", key=f"target_{selected_emp}_{selected_period}_g_admin")
                    new_achieved = st.number_input("Achieved Sales (INR)", value=g_achieved, min_value=0.0, step=100.0, format="%.2f", key=f"achieved_{selected_emp}_{selected_period}_g_admin")
                    new_status = st.radio("Status:", status_options, index=status_options.index(g_status) if g_status in status_options else 0, 
                                          horizontal=True, key=f"status_{selected_emp}_{selected_period}_g_admin")
                    submitted = st.form_submit_button("Save Goal")

                if submitted:
                    if not new_desc.strip(): st.warning("Description is required.")
                    elif new_target <= 0 and new_status not in ["Cancelled","On Hold","Not Started"]: st.warning("Target > 0 required unless status is Cancelled, On Hold or Not Started.")
                    else:
                        existing_g_indices = editable_goals_df[
                            (editable_goals_df["Username"].astype(str) == str(selected_emp)) &
                            (editable_goals_df["MonthYear"].astype(str) == str(selected_period))
                        ].index

                        if not existing_g_indices.empty: # Update existing
                            idx_to_update = existing_g_indices[0]
                            editable_goals_df.loc[idx_to_update, "GoalDescription"] = new_desc
                            editable_goals_df.loc[idx_to_update, "TargetAmount"] = new_target
                            editable_goals_df.loc[idx_to_update, "AchievedAmount"] = new_achieved
                            editable_goals_df.loc[idx_to_update, "Status"] = new_status
                            msg_verb="updated"
                        else: # Add new
                            new_row_data = {
                                "Username":selected_emp, "MonthYear":selected_period, 
                                "GoalDescription":new_desc, "TargetAmount":new_target, 
                                "AchievedAmount":new_achieved, "Status":new_status
                            }
                            for col_name in GOALS_COLUMNS: # Ensure all columns are present
                                if col_name not in new_row_data: new_row_data[col_name] = pd.NA
                            new_row_df = pd.DataFrame([new_row_data], columns=GOALS_COLUMNS)
                            editable_goals_df = pd.concat([editable_goals_df, new_row_df], ignore_index=True)
                            msg_verb="set"
                        
                        try:
                            editable_goals_df.to_csv(GOALS_FILE,index=False)
                            goals_df = editable_goals_df # Update global df
                            st.session_state.user_message=f"Goal for {selected_emp} ({selected_period}) {msg_verb}!"
                            st.session_state.message_type="success"; st.rerun()
                        except Exception as e:
                            st.session_state.user_message=f"Error saving goal: {e}"
                            st.session_state.message_type="error"; st.rerun()
    else: # Employee View
        st.markdown("<h4>My Sales Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        # Load fresh goals_df for employee view
        my_goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
        my_goals = my_goals_df[my_goals_df["Username"].astype(str) == str(current_user["username"])].copy()
        
        for col in ["TargetAmount", "AchievedAmount"]: 
            my_goals[col] = pd.to_numeric(my_goals[col], errors="coerce").fillna(0.0)
        
        current_g_df = my_goals[my_goals["MonthYear"] == current_quarter_for_display] 
        st.markdown(f"<h5>Current Goal Period: {current_quarter_for_display}</h5>", unsafe_allow_html=True)
        
        if not current_g_df.empty:
            g = current_g_df.iloc[0]
            target_amt = g["TargetAmount"]
            achieved_amt = g["AchievedAmount"]
            st.markdown(f"**Description:** {g.get('GoalDescription', 'N/A')}")
            
            col_metrics_sales, col_chart_sales = st.columns([0.63,0.37]) # Ratio for metrics vs chart
            with col_metrics_sales:
                sub_col1,sub_col2=st.columns(2)
                sub_col1.metric("Target",f"₹{target_amt:,.0f}")
                sub_col2.metric("Achieved",f"₹{achieved_amt:,.0f}")
                st.metric("Status",g.get("Status","In Progress"),label_visibility="labeled")
            with col_chart_sales:
                progress_percent_sales=(achieved_amt/target_amt*100) if target_amt > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:-15px;'>Sales Progress</h6>",unsafe_allow_html=True)
                donut_fig_sales=create_donut_chart(progress_percent_sales,"Sales Progress",achieved_color='#28a745')
                st.pyplot(donut_fig_sales,use_container_width=True)
            
            st.markdown("---")
            with st.form(key=f"update_achievement_{current_user['username']}_{current_quarter_for_display}"):
                new_val = st.number_input("Update Achieved Amount (INR):",value=achieved_amt,min_value=0.0,step=100.0,format="%.2f")
                submitted_ach = st.form_submit_button("Update Achievement")
            
            if submitted_ach:
                # Load fresh for update, then save
                editable_goals_df_update = load_data(GOALS_FILE, GOALS_COLUMNS).copy()
                idx_series = editable_goals_df_update[
                    (editable_goals_df_update["Username"] == current_user["username"]) &
                    (editable_goals_df_update["MonthYear"] == current_quarter_for_display)
                ].index
                
                if not idx_series.empty:
                    idx_to_update = idx_series[0]
                    editable_goals_df_update.loc[idx_to_update,"AchievedAmount"] = new_val
                    # Determine new status based on updated achievement
                    current_target_amt = editable_goals_df_update.loc[idx_to_update, "TargetAmount"]
                    new_status = "Achieved" if new_val >= current_target_amt and current_target_amt > 0 else "In Progress"
                    editable_goals_df_update.loc[idx_to_update,"Status"] = new_status
                    
                    try:
                        editable_goals_df_update.to_csv(GOALS_FILE,index=False)
                        goals_df = editable_goals_df_update # Update global df
                        st.session_state.user_message = "Achievement updated!"
                        st.session_state.message_type = "success"; st.rerun()
                    except Exception as e:
                        st.session_state.user_message = f"Error updating achievement: {e}"
                        st.session_state.message_type = "error"; st.rerun()
                else:
                    st.session_state.user_message = "Could not find your current goal to update."
                    st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No goal set for {current_quarter_for_display}. Contact admin.")
        
        st.markdown("---"); st.markdown("<h5>My Past Goals (2025)</h5>", unsafe_allow_html=True)
        past_goals = my_goals[
            (my_goals["MonthYear"].astype(str).str.startswith(str(TARGET_GOAL_YEAR))) & 
            (my_goals["MonthYear"].astype(str) != current_quarter_for_display)
        ]
        if not past_goals.empty: render_goal_chart(past_goals, "Past Sales Goal Performance")
        else: st.info(f"No past goal records for {TARGET_GOAL_YEAR}.")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.active_page == "Payment Collection Tracker":
    # Similar structure to Goal Tracker, ensure to load_data before modification/view
    # and update global df after saving. I'll omit repetitive parts for brevity here,
    # but apply the same load/save pattern as in Goal Tracker.
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_YEAR_PAYMENT = 2025; current_quarter_display_payment = get_quarter_str_for_year(TARGET_YEAR_PAYMENT)
    status_options_payment = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Set & Track Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action_payment = st.radio("Action:", ["View Team Progress", f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}"], 
                                        key="admin_payment_action_admin_set", horizontal=True)
        if admin_action_payment == "View Team Progress":
            st.markdown(f"<h5>Team Payment Collection Progress for {current_quarter_display_payment}</h5>", unsafe_allow_html=True)
            employees_payment_list = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employees_payment_list: st.info("No employees found.")
            else:
                current_payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
                summary_list_payment = []
                for emp_pay_name in employees_payment_list:
                    record_payment = current_payment_goals_df[
                        (current_payment_goals_df["Username"]==emp_pay_name) &
                        (current_payment_goals_df["MonthYear"]==current_quarter_display_payment)
                    ]
                    target_p, achieved_p, status_p = 0.0, 0.0, "Not Set"
                    if not record_payment.empty:
                        rec_payment = record_payment.iloc[0]
                        target_p = float(pd.to_numeric(rec_payment["TargetAmount"],errors='coerce') or 0.0)
                        achieved_p = float(pd.to_numeric(rec_payment["AchievedAmount"],errors='coerce') or 0.0)
                        status_p = rec_payment.get("Status","N/A")
                    summary_list_payment.append({"Employee":emp_pay_name,"Target":target_p,"Achieved":achieved_p,"Status":status_p})
                
                summary_df_payment = pd.DataFrame(summary_list_payment)
                if not summary_df_payment.empty:
                    st.markdown("<h6>Individual Collection Progress:</h6>", unsafe_allow_html=True)
                    num_cols_payment = min(3, len(summary_df_payment))
                    if num_cols_payment > 0:
                        cols_payment = st.columns(num_cols_payment)
                        col_idx_payment = 0
                        for index,row in summary_df_payment.iterrows():
                            progress_percent_p=(row['Achieved']/row['Target']*100) if row['Target'] > 0 else 0
                            donut_fig_p=create_donut_chart(progress_percent_p,achieved_color='#2070c0') # Specific color
                            current_col_p=cols_payment[col_idx_payment%num_cols_payment]
                            with current_col_p:
                                st.markdown(f"<div class='employee-progress-item'><h6>{row['Employee']}</h6><p>Target: ₹{row['Target']:,.0f}<br>Collected: ₹{row['Achieved']:,.0f}</p></div>",unsafe_allow_html=True)
                                st.pyplot(donut_fig_p,use_container_width=True)
                                st.markdown("<div style='margin-bottom:15px;'></div>",unsafe_allow_html=True)
                            col_idx_payment+=1
                    
                    st.markdown("<hr style='margin-top:10px;margin-bottom:25px;'>",unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Collection Performance:</h6>",unsafe_allow_html=True)
                    team_bar_fig_payment = create_team_progress_bar_chart(summary_df_payment,title="Team Collection Target vs. Achieved",target_col="Target",achieved_col="Achieved")
                    if team_bar_fig_payment:
                        # Custom color for achieved bars in payment chart
                        for bar_group_idx, bar_group in enumerate(team_bar_fig_payment.axes[0].containers):
                            if bar_group.get_label() == 'Achieved': # Check label set in create_team_progress_bar_chart
                                for bar in bar_group: bar.set_color('#2070c0') # Payment achieved color
                        st.pyplot(team_bar_fig_payment,use_container_width=True)
                    else: st.info("No collection data to plot for team bar chart.")
                else: st.info(f"No payment collection data for {current_quarter_display_payment}.")

        elif admin_action_payment == f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}":
            st.markdown(f"<h5>Set or Update Collection Goal ({TARGET_YEAR_PAYMENT} - Quarterly)</h5>", unsafe_allow_html=True)
            employees_for_payment_goal = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employees_for_payment_goal: st.warning("No employees available.")
            else:
                selected_emp_payment=st.radio("Select Employee:",employees_for_payment_goal,key="payment_emp_radio_admin_set",horizontal=True)
                quarters_payment=[f"{TARGET_YEAR_PAYMENT}-Q{i}" for i in range(1,5)]
                selected_period_payment=st.radio("Quarter:",quarters_payment,key="payment_period_radio_admin_set",horizontal=True)
                
                editable_payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS).copy()
                existing_payment_goal_series = editable_payment_goals_df[
                    (editable_payment_goals_df["Username"]==selected_emp_payment) &
                    (editable_payment_goals_df["MonthYear"]==selected_period_payment)
                ]
                desc_payment, tgt_payment_val, ach_payment_val, stat_payment = "",0.0,0.0,"Not Started"
                if not existing_payment_goal_series.empty:
                    g_payment=existing_payment_goal_series.iloc[0]
                    desc_payment=g_payment.get("GoalDescription","")
                    tgt_payment_val=float(pd.to_numeric(g_payment.get("TargetAmount",0.0),errors='coerce') or 0.0)
                    ach_payment_val=float(pd.to_numeric(g_payment.get("AchievedAmount",0.0),errors='coerce') or 0.0)
                    stat_payment=g_payment.get("Status","Not Started")
                    st.info(f"Editing payment goal for {selected_emp_payment} - {selected_period_payment}")

                with st.form(f"form_payment_{selected_emp_payment}_{selected_period_payment}_admin"):
                    new_desc_payment=st.text_input("Collection Goal Description",value=desc_payment,key=f"desc_pay_{selected_emp_payment}_{selected_period_payment}_p_admin")
                    new_tgt_payment=st.number_input("Target Collection (INR)",value=tgt_payment_val,min_value=0.0,step=1000.0,format="%.2f",key=f"target_pay_{selected_emp_payment}_{selected_period_payment}_p_admin")
                    new_ach_payment=st.number_input("Collected Amount (INR)",value=ach_payment_val,min_value=0.0,step=500.0,format="%.2f",key=f"achieved_pay_{selected_emp_payment}_{selected_period_payment}_p_admin")
                    new_status_payment=st.selectbox("Status",status_options_payment,index=status_options_payment.index(stat_payment) if stat_payment in status_options_payment else 0,
                                                    key=f"status_pay_{selected_emp_payment}_{selected_period_payment}_p_admin")
                    submitted_payment=st.form_submit_button("Save Goal")
                
                if submitted_payment:
                    if not new_desc_payment.strip(): st.warning("Description required.")
                    elif new_tgt_payment <= 0 and new_status_payment not in ["Cancelled","Not Started", "On Hold"]: st.warning("Target > 0 required unless status is Cancelled, Not Started or On Hold.")
                    else:
                        existing_pg_indices = editable_payment_goals_df[
                            (editable_payment_goals_df["Username"]==selected_emp_payment) &
                            (editable_payment_goals_df["MonthYear"]==selected_period_payment)
                        ].index
                        if not existing_pg_indices.empty:
                            idx_to_update_pg = existing_pg_indices[0]
                            editable_payment_goals_df.loc[idx_to_update_pg, "GoalDescription"] = new_desc_payment
                            editable_payment_goals_df.loc[idx_to_update_pg, "TargetAmount"] = new_tgt_payment
                            editable_payment_goals_df.loc[idx_to_update_pg, "AchievedAmount"] = new_ach_payment
                            editable_payment_goals_df.loc[idx_to_update_pg, "Status"] = new_status_payment
                            msg_payment="updated"
                        else:
                            new_row_data_p={"Username":selected_emp_payment,"MonthYear":selected_period_payment,
                                            "GoalDescription":new_desc_payment,"TargetAmount":new_tgt_payment,
                                            "AchievedAmount":new_ach_payment,"Status":new_status_payment}
                            for col_name in PAYMENT_GOALS_COLUMNS:
                                if col_name not in new_row_data_p: new_row_data_p[col_name]=pd.NA
                            new_row_df_p = pd.DataFrame([new_row_data_p], columns=PAYMENT_GOALS_COLUMNS)
                            editable_payment_goals_df=pd.concat([editable_payment_goals_df,new_row_df_p],ignore_index=True)
                            msg_payment="set"
                        try:
                            editable_payment_goals_df.to_csv(PAYMENT_GOALS_FILE,index=False)
                            payment_goals_df = editable_payment_goals_df # Update global df
                            st.session_state.user_message=f"Payment goal {msg_payment} for {selected_emp_payment} ({selected_period_payment})"
                            st.session_state.message_type="success"; st.rerun()
                        except Exception as e:
                            st.session_state.user_message=f"Error saving payment goal: {e}"
                            st.session_state.message_type="error"; st.rerun()
    else: # Employee View for Payment Collection
        st.markdown("<h4>My Payment Collection Goals (2025)</h4>", unsafe_allow_html=True)
        my_payment_goals_main_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
        user_goals_payment = my_payment_goals_main_df[my_payment_goals_main_df["Username"]==current_user["username"]].copy()
        user_goals_payment[["TargetAmount","AchievedAmount"]] = user_goals_payment[["TargetAmount","AchievedAmount"]].apply(pd.to_numeric,errors="coerce").fillna(0.0)
        
        current_payment_goal_period_df = user_goals_payment[user_goals_payment["MonthYear"]==current_quarter_display_payment]
        st.markdown(f"<h5>Current Quarter: {current_quarter_display_payment}</h5>", unsafe_allow_html=True)
        
        if not current_payment_goal_period_df.empty:
            g_pay=current_payment_goal_period_df.iloc[0]; tgt_pay=g_pay["TargetAmount"]; ach_pay=g_pay["AchievedAmount"]
            st.markdown(f"**Goal:** {g_pay.get('GoalDescription','')}")
            col_metrics_pay,col_chart_pay=st.columns([0.63,0.37])
            with col_metrics_pay:
                sub_col1_pay,sub_col2_pay=st.columns(2)
                sub_col1_pay.metric("Target",f"₹{tgt_pay:,.0f}")
                sub_col2_pay.metric("Collected",f"₹{ach_pay:,.0f}")
                st.metric("Status",g_pay.get("Status","In Progress"),label_visibility="labeled")
            with col_chart_pay:
                progress_percent_pay=(ach_pay/tgt_pay*100) if tgt_pay > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:-15px;'>Collection Progress</h6>",unsafe_allow_html=True)
                donut_fig_payment=create_donut_chart(progress_percent_pay,"Collection Progress",achieved_color='#2070c0')
                st.pyplot(donut_fig_payment,use_container_width=True)
            
            st.markdown("---")
            with st.form(key=f"update_collection_{current_user['username']}_{current_quarter_display_payment}"):
                new_ach_val_payment=st.number_input("Update Collected Amount (INR):",value=ach_pay,min_value=0.0,step=500.0, format="%.2f")
                submit_collection_update=st.form_submit_button("Update Collection")
            
            if submit_collection_update:
                editable_payment_goals_df_update = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS).copy()
                idx_pay_series=editable_payment_goals_df_update[
                    (editable_payment_goals_df_update["Username"]==current_user["username"]) &
                    (editable_payment_goals_df_update["MonthYear"]==current_quarter_display_payment)
                ].index
                if not idx_pay_series.empty:
                    idx_pay_to_update = idx_pay_series[0]
                    editable_payment_goals_df_update.loc[idx_pay_to_update,"AchievedAmount"]=new_ach_val_payment
                    current_target_pay = editable_payment_goals_df_update.loc[idx_pay_to_update, "TargetAmount"]
                    editable_payment_goals_df_update.loc[idx_pay_to_update,"Status"] = "Achieved" if new_ach_val_payment >= current_target_pay and current_target_pay > 0 else "In Progress"
                    try:
                        editable_payment_goals_df_update.to_csv(PAYMENT_GOALS_FILE,index=False)
                        payment_goals_df = editable_payment_goals_df_update # Update global
                        st.session_state.user_message = "Collection updated."
                        st.session_state.message_type = "success"; st.rerun()
                    except Exception as e:
                        st.session_state.user_message = f"Error updating collection: {e}"
                        st.session_state.message_type = "error"; st.rerun()
                else:
                    st.session_state.user_message = "Could not find your current payment goal to update."
                    st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No collection goal for {current_quarter_display_payment}.")
        
        st.markdown("<h5>Past Quarters</h5>", unsafe_allow_html=True)
        past_payment_goals = user_goals_payment[user_goals_payment["MonthYear"]!=current_quarter_display_payment]
        if not past_payment_goals.empty: render_goal_chart(past_payment_goals,"Past Collection Performance")
        else: st.info("No past collection goals.")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.active_page == "View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 View Logs</h3>", unsafe_allow_html=True)
    
    # Load fresh data for viewing
    current_activity_log_df_view = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS)
    current_attendance_df_view = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
    current_allowance_df_view = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
    current_goals_df_view = load_data(GOALS_FILE, GOALS_COLUMNS)
    current_payment_goals_df_view = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)

    def display_activity_logs_with_photos(df_logs, user_name_for_header):
        if df_logs.empty: st.info(f"No activity logs for {user_name_for_header}."); return
        df_logs_sorted = df_logs.sort_values(by="Timestamp", ascending=False).copy()
        st.markdown(f"<h5>Field Activity Logs for: {user_name_for_header}</h5>", unsafe_allow_html=True)
        for index, row in df_logs_sorted.iterrows():
            st.markdown("---"); col_details, col_photo = st.columns([0.7, 0.3])
            with col_details:
                st.markdown(f"**Timestamp:** {row['Timestamp']}<br>**Description:** {row.get('Description', 'N/A')}<br>**Location:** {'Not Recorded' if pd.isna(row.get('Latitude')) else f"Lat: {row.get('Latitude'):.4f}, Lon: {row.get('Longitude'):.4f}"}", unsafe_allow_html=True)
                if pd.notna(row['ImageFile']) and row['ImageFile'] != "": st.caption(f"Photo ID: {row['ImageFile']}")
                else: st.caption("No photo for this activity.")
            with col_photo:
                if pd.notna(row['ImageFile']) and row['ImageFile'] != "":
                    image_path_to_display = os.path.join(ACTIVITY_PHOTOS_DIR, str(row['ImageFile']))
                    if os.path.exists(image_path_to_display):
                        try: st.image(image_path_to_display, width=150)
                        except Exception as img_e: st.warning(f"Image error: {img_e}")
                    else: st.caption(f"Image missing")
    
    def display_attendance_logs(df_logs, user_name_for_header):
        if df_logs.empty: st.warning(f"No general attendance records for {user_name_for_header}."); return
        df_logs_sorted = df_logs.sort_values(by="Timestamp", ascending=False).copy()
        st.markdown(f"<h5>General Attendance Records for: {user_name_for_header}</h5>", unsafe_allow_html=True)
        columns_to_show = ["Type", "Timestamp"]
        if 'Latitude' in df_logs_sorted.columns and 'Longitude' in df_logs_sorted.columns:
            df_logs_sorted['Location'] = df_logs_sorted.apply(
                lambda r: f"Lat: {r['Latitude']:.4f}, Lon: {r['Longitude']:.4f}"
                if pd.notna(r['Latitude']) and pd.notna(r['Longitude']) else "Not Recorded", axis=1
            )
            columns_to_show.append('Location')
        st.dataframe(df_logs_sorted[columns_to_show], use_container_width=True, hide_index=True)

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: View Employee Records</h4>", unsafe_allow_html=True)
        employee_name_list = [name for name in USERS.keys() if name != "admin"]
        selected_employee_log = st.selectbox("Select Employee:", employee_name_list, key="log_employee_select_admin_activity")

        if selected_employee_log: 
            emp_activity_log = current_activity_log_df_view[current_activity_log_df_view["Username"] == selected_employee_log]
            display_activity_logs_with_photos(emp_activity_log, selected_employee_log)
            st.markdown("<br><hr><br>", unsafe_allow_html=True)
            
            emp_attendance_log = current_attendance_df_view[current_attendance_df_view["Username"] == selected_employee_log]
            display_attendance_logs(emp_attendance_log, selected_employee_log)
            
            st.markdown("---"); st.markdown(f"<h5>Allowances for {selected_employee_log}</h5>", unsafe_allow_html=True)
            emp_allowance_log = current_allowance_df_view[current_allowance_df_view["Username"] == selected_employee_log]
            if not emp_allowance_log.empty: st.dataframe(emp_allowance_log.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
            else: st.warning("No allowance records found")
            
            st.markdown(f"<h5>Sales Goals for {selected_employee_log}</h5>", unsafe_allow_html=True)
            emp_goals_log = current_goals_df_view[current_goals_df_view["Username"] == selected_employee_log]
            if not emp_goals_log.empty: st.dataframe(emp_goals_log.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
            else: st.warning("No sales goals records found")
            
            st.markdown(f"<h5>Payment Collection Goals for {selected_employee_log}</h5>", unsafe_allow_html=True)
            emp_payment_goals_log = current_payment_goals_df_view[current_payment_goals_df_view["Username"] == selected_employee_log]
            if not emp_payment_goals_log.empty: st.dataframe(emp_payment_goals_log.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
            else: st.warning("No payment collection goals records found")
        else: st.info("Please select an employee to view their logs.")
    else: # Employee view
        st.markdown("<h4>My Records</h4>", unsafe_allow_html=True)
        my_activity_log = current_activity_log_df_view[current_activity_log_df_view["Username"] == current_user["username"]]
        display_activity_logs_with_photos(my_activity_log, current_user["username"])
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        
        my_attendance_log = current_attendance_df_view[current_attendance_df_view["Username"] == current_user["username"]]
        display_attendance_logs(my_attendance_log, current_user["username"])
        
        st.markdown("---"); st.markdown("<h5>My Allowances</h5>", unsafe_allow_html=True)
        my_allowance_log = current_allowance_df_view[current_allowance_df_view["Username"] == current_user["username"]]
        if not my_allowance_log.empty: st.dataframe(my_allowance_log.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
        else: st.warning("No allowance records found for you")
        
        st.markdown("<h5>My Sales Goals</h5>", unsafe_allow_html=True)
        my_goals_log = current_goals_df_view[current_goals_df_view["Username"] == current_user["username"]]
        if not my_goals_log.empty: st.dataframe(my_goals_log.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
        else: st.warning("No sales goals records found for you")
        
        st.markdown("<h5>My Payment Collection Goals</h5>", unsafe_allow_html=True)
        my_payment_goals_log = current_payment_goals_df_view[current_payment_goals_df_view["Username"] == current_user["username"]]
        if not my_payment_goals_log.empty: st.dataframe(my_payment_goals_log.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
        else: st.warning("No payment collection goals records found for you")
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.active_page == "Create Order":
    st.title("Create New Order") 
    try:
        # These files need to exist in the same directory as app.py or provide full path
        stores_df = pd.read_csv("agri_stores.csv")
        products_df = pd.read_csv("symplanta_products_with_images.csv")
    except FileNotFoundError as e:
        st.error(f"Error: Required CSV file not found. Please check file names and paths. Missing: {e.filename}")
        st.stop()

    store_name = st.selectbox("Select Store", sorted(stores_df["StoreName"].dropna().astype(str).unique()))
    product_name = st.selectbox(
        "Select Product",
        sorted(products_df["Product Name"].dropna().astype(str).unique())
    )
    product_sizes = products_df[products_df["Product Name"] == product_name]
    size = st.selectbox(
        "Select Size",
        sorted(product_sizes["Size"].dropna().astype(str).unique())
    )
    quantity = st.number_input("Enter Quantity", min_value=1, value=1)

    if st.button("Add to Order", type="primary"):
        if "order_items" not in st.session_state: st.session_state["order_items"] = []
        
        selected_product_df = product_sizes[product_sizes["Size"] == size]
        if not selected_product_df.empty:
            selected_product = selected_product_df.iloc[0]
            item = {
                "Store": store_name, "Product": product_name, "Size": size,
                "Quantity": quantity, "Unit Price": selected_product["Price"],
                "Total": selected_product["Price"] * quantity
            }
            st.session_state["order_items"].append(item)
            st.success("Item added to order!")
        else: st.warning("Selected product size details not found.")

    if "order_items" in st.session_state and st.session_state["order_items"]:
        st.subheader("🧾 Order Summary")
        order_df = pd.DataFrame(st.session_state["order_items"])
        order_df["Unit Price"] = pd.to_numeric(order_df["Unit Price"], errors='coerce').fillna(0)
        order_df["Total"] = pd.to_numeric(order_df["Total"], errors='coerce').fillna(0)
        
        order_df_display = order_df.copy() # For display formatting
        order_df_display["Unit Price"] = order_df_display["Unit Price"].apply(lambda x: f"₹{x:,.2f}")
        order_df_display["Total"] = order_df_display["Total"].apply(lambda x: f"₹{x:,.2f}")
        
        st.dataframe(order_df_display[["Store", "Product", "Size", "Quantity", "Unit Price", "Total"]], use_container_width=True) # Explicit column order
        st.markdown(f"**Grand Total: ₹{order_df['Total'].sum():,.2f}**")
