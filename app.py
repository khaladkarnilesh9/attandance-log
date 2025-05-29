import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from streamlit_option_menu import option_menu
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
    # st.warning("Pillow library not found. Placeholder images will not be generated.") # Optional warning

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
    try: os.makedirs(ACTIVITY_PHOTOS_DIR, exist_ok=True) # exist_ok=True prevents error if dir exists
    except OSError as e: st.warning(f"Could not create directory {ACTIVITY_PHOTOS_DIR}: {e}")


# --- DATA LOADING & UTILITY FUNCTIONS ---
def get_current_time_in_tz():
    return datetime.now(timezone.utc).astimezone(tz)

def get_quarter_str_for_year(year):
    current_time = get_current_time_in_tz()
    month = current_time.month
    if 1 <= month <= 3: return f"{year}-Q1"
    elif 4 <= month <= 6: return f"{year}-Q2"
    elif 7 <= month <= 9: return f"{year}-Q3"
    else: return f"{year}-Q4"

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
        except pd.errors.EmptyDataError:
            # st.warning(f"File {path} is empty. Initializing with columns.") # Optional
            return pd.DataFrame(columns=columns)
        except Exception as e:
            # st.error(f"Error loading {path}: {e}. Initializing with columns.") # Optional
            return pd.DataFrame(columns=columns)
    else:
        # if not os.path.exists(path): st.info(f"File {path} not found. Creating it.") # Optional
        # elif os.path.exists(path) and os.path.getsize(path) == 0: st.info(f"File {path} empty. Initializing.") # Optional
        df = pd.DataFrame(columns=columns)
        try: df.to_csv(path, index=False)
        except Exception as e: st.warning(f"Could not create or write to {path}: {e}")
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

if not os.path.exists("images"): os.makedirs("images", exist_ok=True)
if PILLOW_INSTALLED:
    for user_key, user_data in USERS.items():
        img_path = user_data.get("profile_photo")
        if img_path and not os.path.exists(img_path):
            try:
                img = Image.new('RGB', (60, 60), color = (220, 220, 220))
                draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", 20)
                except IOError: font = ImageFont.load_default()
                text_content = user_key[:1].upper()
                if hasattr(draw, 'textbbox'):
                    bbox = draw.textbbox((0,0), text_content, font=font); w,h = bbox[2]-bbox[0], bbox[3]-bbox[1]
                    x,y = (60-w)/2 - bbox[0], (60-h)/2 - bbox[1]
                else: x,y = 20,15
                draw.text((x, y), text_content, fill=(100,100,100), font=font)
                img.save(img_path)
            except Exception: pass


# --- SESSION STATE INITIALIZATION ---
if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}
if "order_items" not in st.session_state: st.session_state.order_items = [] # For Create Order page

# --- CSS STYLING (Google AI Studio Inspired) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    /* --- BASE & FONT --- */
    body, .stButton button, .stTextInput input, .stTextArea textarea, .stSelectbox select, p, div, span {
        font-family: 'Roboto', sans-serif !important;
    }
    /* Ensure Material Icons font is available for option_menu if it uses it (Bootstrap Icons are default) */
    .material-icons { /* This class is used by streamlit-option-menu if you use Material Icons names */
        font-family: 'Material Icons' !important;
    }
    .material-symbols-outlined { /* If you use these elsewhere via span e.g. for logout */
        font-family: 'Material Symbols Outlined' !important; /* If you have this font linked separately */
        vertical-align: middle !important;
        font-size: 18px !important;
        margin-right: 8px;
    }

    /* --- SIDEBAR --- */
    section[data-testid="stSidebar"] > div:first-child {
        padding: 0px !important;
        background-color: #131314 !important; /* AI Studio very dark gray */
        height: 100vh; /* Ensure sidebar takes full height */
        display: flex; /* Added */
        flex-direction: column; /* Added */
    }
    /* This class is intended for a div you'd wrap around all sidebar content if needed */
    /* For now, section[data-testid="stSidebar"] > div:first-child handles the main container */

    .sidebar-header {
        padding: 20px 16px 16px 16px; /* More top padding */
        border-bottom: 1px solid rgba(255, 255, 255, 0.08); /* Softer border */
        margin-bottom: 10px;
    }
    .sidebar-header h2 {
        color: #8ab4f8; /* Google Blue accent */
        font-size: 1.3rem; /* Slightly smaller */
        margin: 0; font-weight: 500;
    }
    .sidebar-header p {
        color: #9aa0a6; /* Subdued text */
        font-size: 0.8rem; margin: 2px 0 0 0;
    }

    .sidebar-user-info {
        padding: 8px 16px 12px 16px; /* Padding around user info */
        display: flex;
        align-items: center;
        gap: 10px; /* Space between image and text block */
    }
    .user-profile-img-sidebar {
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        object-fit: cover !important;
        border: 1px solid #5f6368 !important;
    }
    .user-details-sidebar div:nth-child(1) { /* Username */
        color: #e8eaed !important;
        font-size: 0.9rem;
        font-weight: 500;
        line-height: 1.2;
    }
    .user-details-sidebar div:nth-child(2) { /* Position */
        color: #9aa0a6 !important;
        font-size: 0.75rem;
        line-height: 1.2;
    }
    section[data-testid="stSidebar"] hr { /* Targeting hr within sidebar */
        margin: 10px 16px !important; /* Consistent L/R margin */
        border-color: rgba(255, 255, 255, 0.08) !important;
    }

    /* streamlit-option-menu specific styling is done via its `styles` parameter */
    /* This is just a container for the logout button */
    .logout-button-container-sidebar {
        margin-top: auto; /* Pushes logout to the bottom */
        padding: 16px;
    }
    .logout-button-container-sidebar .stButton button {
        background-color: transparent !important;
        color: #bdc1c6 !important; /* Lighter gray for logout text */
        border: 1px solid #5f6368 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 0.875rem !important;
        border-radius: 6px !important;
    }
    .logout-button-container-sidebar .stButton button:hover {
        background-color: rgba(236, 66, 47, 0.15) !important; /* Reddish hover */
        border-color: rgba(236, 66, 47, 0.4) !important;
        color: #f28b82 !important; /* Lighter red text on hover */
    }
    .logout-button-container-sidebar .stButton button .material-symbols-outlined {
        color: inherit !important; /* Icon inherits color */
    }

    /* --- Main Content & Notifications --- */
    div[data-testid="stAppViewContainer"] > .main { background-color: #f8f9fa !important; color: #202124; } /* Light gray main bg */
    .card { background-color: #ffffff; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; border: 1px solid #dee2e6; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .custom-notification { padding: 1rem; border-radius: 6px; margin-bottom: 1rem; border: 1px solid transparent; font-size: 0.9rem; }
    .custom-notification.success { color: #0f5132; background-color: #d1e7dd; border-color: #badbcc; }
    .custom-notification.error { color: #842029; background-color: #f8d7da; border-color: #f5c2c7; }
    .custom-notification.info { color: #055160; background-color: #cff4fc; border-color: #b6effb; }
    .custom-notification.warning { color: #664d03; background-color: #fff3cd; border-color: #ffecb5; }
    .button-column-container .stButton button { width: 100%; }
    .employee-progress-item h6 { margin-bottom: 0.25rem; font-size: 1rem; color: #202124; }
    .employee-progress-item p { font-size: 0.85rem; color: #5f6368; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)


# --- LOGIN PAGE ---
if not st.session_state.auth["logged_in"]:
    st.title("TrackSphere Login")
    message_placeholder_login = st.empty()
    if st.session_state.user_message:
        message_placeholder_login.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
        st.session_state.user_message = None; st.session_state.message_type = None

    st.markdown("<div class='card' style='max-width: 400px; margin: 2rem auto;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #202124;'>🔐 Login</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname_main_key")
    pwd = st.text_input("Password", type="password", key="login_pwd_main_key")
    if st.button("Login", key="login_button_main_key", type="primary", use_container_width=True):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = "Login successful!"; st.session_state.message_type = "success"; st.rerun()
        else: st.error("Invalid username or password.")
    st.markdown("</div>", unsafe_allow_html=True); st.stop()

# --- MAIN APPLICATION AFTER LOGIN ---
current_user = st.session_state.auth

message_placeholder_main = st.empty()
if st.session_state.user_message:
    message_placeholder_main.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
    st.session_state.user_message = None; st.session_state.message_type = None

# --- SIDEBAR IMPLEMENTATION WITH streamlit_option_menu ---
with st.sidebar:
    # Header
    st.markdown("""
    <div class="sidebar-header">
        <h2>TrackSphere</h2>
        <p>Field Activity Tracker</p>
    </div>
    """, unsafe_allow_html=True)

    # User Info
    current_username = current_user.get('username', 'Guest')
    user_details = USERS.get(current_username, {})
    profile_photo_path = user_details.get("profile_photo", "")

    st.markdown('<div class="sidebar-user-info">', unsafe_allow_html=True)
    if profile_photo_path and os.path.exists(profile_photo_path) and PILLOW_INSTALLED:
        st.image(profile_photo_path, width=32, output_format='auto', use_column_width='never',
                 # The class is applied to the img tag by Streamlit if possible,
                 # but better to style container if needed. Here, fixed width is set.
                )
    else: # Fallback icon if no image or Pillow not installed
        st.markdown(f"""<span class="material-icons" style="font-size: 32px; color: #5f6368; margin-right:12px; vertical-align:middle;">account_circle</span>""", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="user-details-sidebar">
            <div>{current_username}</div>
            <div>{user_details.get('position', 'N/A')}</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True) # Use Streamlit's hr for simplicity, styled by CSS

    # Navigation Menu
    # Using Bootstrap Icons for streamlit-option-menu
    # Find names at: https://icons.getbootstrap.com/
    # For Material Icons, you'd list names like "schedule", "add_a_photo" and set menu_icon_family="material-icons"
    # in option_menu, and ensure Material Icons font is loaded.
    
    # For this example, sticking to Bootstrap Icons as they are default for option_menu
    menu_options = ["Home", "Attendance", "Upload Activity Photo", "Allowance", "Goal Tracker", "Payment Collection Tracker", "View Logs", "Create Order"]
    menu_icons = ['house-door', 'calendar2-check', 'camera', 'wallet', 'graph-up', 'collection', 'journals', 'cart-plus']
    
    # Check if current st.session_state.active_page is valid, otherwise default to "Home"
    if st.session_state.get('active_page') not in menu_options:
        st.session_state.active_page = "Home"
    
    default_menu_index = menu_options.index(st.session_state.active_page)


    selected = option_menu(
        menu_title=None,
        options=menu_options,
        icons=menu_icons,
        # menu_icon="grid-3x3-gap-fill", # Example main menu icon
        default_index=default_menu_index,
        orientation="vertical",
        on_change=lambda key: st.session_state.update(active_page=key), # Update active_page on change
        styles={
            "container": {"padding": "0px 8px !important", "background-color": "#131314"}, # Match sidebar, add some L/R padding
            "icon": {"color": "#9aa0a6", "font-size": "18px", "margin-right":"12px"},
            "nav-link": {
                "font-size": "0.875rem",
                "text-align": "left",
                "margin": "3px 0px", # Top/bottom margin for items
                "padding": "10px 12px", # Padding inside items
                "color": "#e0e0e0",
                "border-radius": "6px",
                "--hover-color": "rgba(255, 255, 255, 0.08)"
            },
            "nav-link-selected": {
                "background-color": "rgba(138, 180, 248, 0.16)", # AI Studio active bg
                "color": "#8ab4f8",
                "font-weight": "500",
            },
             # This targets the icon span directly if option_menu creates it with this class
            "nav-link-selected > i.icon": { # Targeting Bootstrap icons (typically <i> or <span> with class)
                 "color": "#8ab4f8 !important",
             }
        }
    )
    
    # Logout Button
    st.markdown('<div class="logout-button-container-sidebar">', unsafe_allow_html=True)
    # Using material-symbols-outlined for logout button for consistency with other potential icons
    logout_label_html = """<span class="material-symbols-outlined">logout</span> Logout"""
    if st.button(logout_label_html, key="logout_sidebar_btn_unique", use_container_width=True, unsafe_allow_html=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."
        st.session_state.message_type = "info"
        st.session_state.active_page = "Home" # Reset to home on logout
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# --- MAIN CONTENT PAGE ROUTING ---
# (Plotting functions remain the same as your last full code)
def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty: st.warning("No data available to plot."); return
    df_chart = df.copy(); df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear", value_vars=["TargetAmount", "AchievedAmount"], var_name="Metric", value_name="Amount")
    if df_melted.empty: st.warning(f"No data to plot for {chart_title} after processing."); return
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group", labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"}, title=chart_title, color_discrete_map={'TargetAmount': '#8ab4f8', 'AchievedAmount': '#34A853'}) # Google Blue/Green
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#202124') # Main content text color
    fig.update_xaxes(showgrid=False, zeroline=False, color='#5f6368'); fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.1)', zeroline=False, color='#5f6368') # Lighter grid for light bg
    st.plotly_chart(fig, use_container_width=True)

def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#8ab4f8', remaining_color='#e0e0e0', center_text_color='#202124'): # Light theme for cards
    fig, ax = plt.subplots(figsize=(2.2, 2.2), dpi=110); fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    progress_percentage = max(0.0, min(float(progress_percentage), 100.0)); remaining_percentage = 100.0 - progress_percentage
    if progress_percentage <= 0.01: sizes = [100.0]; slice_colors = [remaining_color]; actual_progress_display = 0.0
    elif progress_percentage >= 99.99: sizes = [100.0]; slice_colors = [achieved_color]; actual_progress_display = 100.0
    else: sizes = [progress_percentage, remaining_percentage]; slice_colors = [achieved_color, remaining_color]; actual_progress_display = progress_percentage
    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.35, edgecolor='#ffffff')) # White edge for card
    centre_circle = plt.Circle((0,0),0.65,fc='#ffffff'); fig.gca().add_artist(centre_circle) # White center for card
    text_color_to_use = center_text_color if actual_progress_display > 0 else '#5f6368'
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=10, fontweight='bold', color=text_color_to_use)
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0); return fig

def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee"):
    if summary_df.empty: return None
    labels = summary_df[user_col].tolist(); target_amounts = summary_df[target_col].fillna(0).tolist(); achieved_amounts = summary_df[achieved_col].fillna(0).tolist()
    x = np.arange(len(labels)); width = 0.35
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.7), 4.5), dpi=110, facecolor='rgba(0,0,0,0)'); ax.set_facecolor('rgba(0,0,0,0)')
    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color='rgba(138, 180, 248, 0.8)'); rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color='rgba(52, 168, 83, 0.8)')
    ax.set_ylabel('Amount (INR)', fontsize=9, color='#5f6368'); ax.set_title(title, fontsize=11, fontweight='bold', pad=12, color='#202124')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8, color='#5f6368')
    legend = ax.legend(fontsize=8, facecolor='rgba(255,255,255,0.8)', edgecolor='#e0e0e0');
    for text in legend.get_texts(): text.set_color('#202124')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.spines['bottom'].set_color('#d1d5da'); ax.spines['left'].set_color('#d1d5da')
    ax.tick_params(axis='x', colors='#5f6368'); ax.tick_params(axis='y', colors='#5f6368')
    ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#d1d5da') # Lighter grid
    def autolabel(rects_group, bar_color_text):
        for rect_item in rects_group:
            height_item = rect_item.get_height()
            if height_item > 0: ax.annotate(f'{height_item:,.0f}', xy=(rect_item.get_x() + rect_item.get_width() / 2, height_item), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=6, color=bar_color_text)
    autolabel(rects1, '#1a73e8'); autolabel(rects2, '#188038'); fig.tight_layout(pad=1.2); return fig


# Page routing using 'selected' from option_menu
if selected == "Home":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(f"🏠 Welcome Home, {current_user['username']}!")
    st.write("This is your main dashboard. Select an option from the sidebar to get started.")
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled for attendance. Photos for specific activities can be uploaded from the 'Upload Activity Photo' section.", icon="ℹ️")
    st.markdown("---")
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1_att, col2_att = st.columns(2)
    common_data_att = {"Username": current_user["username"], "Latitude": pd.NA, "Longitude": pd.NA} # Use current_user

    def process_general_attendance(attendance_type): # Function defined inside for scope if not needed elsewhere
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
        if st.button("✅ Check In", key="check_in_btn_page", use_container_width=True, type="primary"):
            process_general_attendance("Check-In")
    with col2_att:
        if st.button("🚪 Check Out", key="check_out_btn_page", use_container_width=True, type="primary"):
            process_general_attendance("Check-Out")
    st.markdown('</div></div>', unsafe_allow_html=True)


elif selected == "Upload Activity Photo":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat_activity, current_lon_activity = pd.NA, pd.NA
    with st.form(key="activity_photo_form_main_page"):
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description:", key="activity_desc_main_page")
        img_file_buffer_activity = st.camera_input("Take a picture:", key="activity_camera_main_page")
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo & Log")
    if submit_activity_photo:
        if img_file_buffer_activity is None: st.warning("Please take a picture.")
        elif not activity_description.strip(): st.warning("Please provide a description.")
        else:
            now_for_filename = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S")
            now_for_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            image_filename_activity = f"{current_user['username']}_activity_{now_for_filename}.jpg" # Use current_user
            image_path_activity = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_activity)
            try:
                with open(image_path_activity, "wb") as f: f.write(img_file_buffer_activity.getbuffer())
                new_activity_data = {"Username": current_user['username'], "Timestamp": now_for_display,
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

# ... (Continue for Allowance, Goal Tracker, Payment Collection Tracker, View Logs, Create Order)
# Remember to replace 'nav' with 'selected' and ensure current_user['username'] is used.

# Example for Allowance:
elif selected == "Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    # ... (Your full Allowance page logic from the previous complete code) ...
    # Make sure to use current_user['username'] for submitting allowance
    st.markdown('</div>', unsafe_allow_html=True)

# You would continue this pattern for all your other pages.
# For brevity, I'm not repeating all the detailed logic for Goal Tracker, Payment Tracker, etc.
# You should copy that from your previous complete version, just ensuring that the
# page condition is `elif selected == "Page Name":` and user-specific data uses `current_user['username']`.

# --- Placeholder for other pages ---
elif selected in ["Goal Tracker", "Payment Collection Tracker", "View Logs", "Create Order"]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(f"🚧 {selected}")
    st.write(f"Content for {selected} page to be implemented fully based on previous logic.")
    st.write(f"Data operations should use: {current_user['username']}")
    st.markdown('</div>', unsafe_allow_html=True)
