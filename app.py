import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from streamlit_option_menu import option_menu # Import for the new sidebar
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
    st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'.")
    st.stop()

# --- File Paths ---
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"
GOALS_FILE = "goals.csv"
PAYMENT_GOALS_FILE = "payment_goals.csv"
ACTIVITY_LOG_FILE = "activity_log.csv"
ACTIVITY_PHOTOS_DIR = "activity_photos"

if not os.path.exists(ACTIVITY_PHOTOS_DIR):
    os.makedirs(ACTIVITY_PHOTOS_DIR, exist_ok=True)

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
                img = Image.new('RGB', (120, 120), color=(220, 220, 220))
                draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", 40)
                except IOError: font = ImageFont.load_default()
                text_content = user_key[:2].upper()
                if hasattr(draw, 'textbbox'):
                    bbox = draw.textbbox((0,0), text_content, font=font); w,h = bbox[2]-bbox[0], bbox[3]-bbox[1]
                    x,y = (120-w)/2 - bbox[0], (120-h)/2 - bbox[1]
                else: x,y = 30,30
                draw.text((x, y), text_content, fill=(100,100,100), font=font)
                img.save(img_path)
            except: pass

# --- SESSION STATE INITIALIZATION ---
if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}
if "order_items" not in st.session_state: st.session_state.order_items = []


# --- CSS STYLING (Adapted from your Kaggle example, with some theming) ---
st.markdown("""
<style>
    /* Main styling - Using your Kaggle-like theme */
    :root {
        --kaggle-blue: #20BEFF; /* Main accent color */
        --kaggle-dark-text: #333333; /* For text on light backgrounds */
        --kaggle-light-bg: #FFFFFF; /* Sidebar background */
        --kaggle-content-bg: #F5F5F5; /* Main content area background */
        --kaggle-gray-border: #E0E0E0; /* Borders and dividers */
        --kaggle-hover-bg: #f0f8ff; /* Light blue hover for items */
        --kaggle-selected-bg: #E6F7FF; /* Background for selected item */
        --kaggle-selected-text: var(--kaggle-blue); /* Text color for selected item */
        --kaggle-icon-color: #555555; /* Default icon color */
        --kaggle-icon-selected-color: var(--kaggle-blue); /* Icon color for selected item */
    }
    
    /* Base body for main content area */
    div[data-testid="stAppViewContainer"] > .main {
        background-color: var(--kaggle-content-bg) !important;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] > div:first-child { /* Target the direct child for background */
        background-color: var(--kaggle-light-bg) !important;
        border-right: 1px solid var(--kaggle-gray-border) !important;
        padding: 0 !important; /* Remove default padding if option_menu handles it */
        height: 100vh;
        display: flex;
        flex-direction: column;
    }
    
    /* Sidebar Header (App Name & Subtitle) */
    .sidebar-header {
        padding: 20px 16px 16px 16px;
        border-bottom: 1px solid var(--kaggle-gray-border);
    }
    .sidebar-header h2 {
        color: var(--kaggle-blue);
        font-size: 1.5rem; /* App name size */
        margin: 0; font-weight: 600; /* Bold app name */
    }
    .sidebar-header p {
        color: #666;
        font-size: 0.85rem; margin: 4px 0 0 0;
    }

    /* User Info Block Styling */
    .sidebar-user-info {
        padding: 12px 16px;
        display: flex;
        align-items: center;
        gap: 12px; /* Space between image and text */
        border-bottom: 1px solid var(--kaggle-gray-border);
    }
    .user-profile-img-sidebar {
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        object-fit: cover !important;
        border: 1px solid var(--kaggle-gray-border) !important;
    }
    .user-details-sidebar div:nth-child(1) { /* Username */
        color: var(--kaggle-dark-text) !important;
        font-size: 0.95rem;
        font-weight: 500;
    }
    .user-details-sidebar div:nth-child(2) { /* Position */
        color: #777 !important;
        font-size: 0.8rem;
    }
    
    /* Logout Button Container in Sidebar */
    .logout-button-container-sidebar {
        margin-top: auto; /* Pushes to bottom */
        padding: 16px; /* Padding around logout */
    }
    .logout-button-container-sidebar .stButton button {
        background-color: transparent !important;
        color: #d32f2f !important; /* Reddish color for logout */
        border: 1px solid #ef9a9a !important; /* Light red border */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 0.9rem !important;
        border-radius: 6px !important;
        width: 100% !important;
    }
    .logout-button-container-sidebar .stButton button:hover {
        background-color: rgba(211, 47, 47, 0.1) !important; /* Light red hover */
        border-color: #d32f2f !important;
    }
    .logout-button-container-sidebar .stButton button .material-symbols-outlined { /* If using material icon for logout */
        font-size: 18px !important; margin-right: 8px; color: inherit;
    }


    /* Main content card styling */
    .card { /* This class is applied via st.markdown in your page logic */
        border: 1px solid var(--kaggle-gray-border);
        border-radius: 8px;
        padding: 24px; /* More padding for cards */
        margin-bottom: 20px; /* Space between cards */
        background-color: var(--kaggle-light-bg); /* White cards */
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Example of styling elements within a card */
    .card h3 {
        color: var(--kaggle-blue);
        font-size: 1.2rem;
        margin-top: 0;
    }
    
    /* Custom notification styling */
    .custom-notification { padding: 1rem; border-radius: 6px; margin-bottom: 1rem; border: 1px solid transparent; font-size: 0.9rem; }
    .custom-notification.success { color: #155724; background-color: #d4edda; border-color: #c3e6cb; }
    .custom-notification.error { color: #721c24; background-color: #f8d7da; border-color: #f5c6cb; }
    /* ... (other .custom-notification types if needed) ... */
</style>
""", unsafe_allow_html=True)


# --- LOGIN PAGE ---
if not st.session_state.auth["logged_in"]:
    st.title("TrackSphere Login")
    message_placeholder_login = st.empty()
    if st.session_state.user_message:
        message_placeholder_login.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
        st.session_state.user_message = None; st.session_state.message_type = None

    st.markdown("<div class='card' style='max-width: 400px; margin: 3rem auto; padding: 2rem;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: var(--kaggle-blue);'>🔐 Login to TrackSphere</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname_app")
    pwd = st.text_input("Password", type="password", key="login_pwd_app")
    if st.button("Login", key="login_button_app", type="primary", use_container_width=True): # Streamlit primary button
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


# --- SIDEBAR IMPLEMENTATION WITH streamlit_option_menu (Kaggle-like) ---
with st.sidebar:
    # App Header in Sidebar
    st.markdown("""
    <div class="sidebar-header">
        <h2>TrackSphere</h2>
        <p>Field Activity Tracker</p>
    </div>
    """, unsafe_allow_html=True)

    # User Info
    current_username_display = current_user.get('username', 'Guest')
    user_details_display = USERS.get(current_username_display, {})
    profile_photo_path_display = user_details_display.get("profile_photo", "")

    st.markdown('<div class="sidebar-user-info">', unsafe_allow_html=True)
    if profile_photo_path_display and os.path.exists(profile_photo_path_display) and PILLOW_INSTALLED:
        st.image(profile_photo_path_display, width=40, output_format='auto', use_column_width='never',
                 # Apply class via markdown wrapper if st.image doesn't support class_name
                 # The CSS can target `img` within `.sidebar-user-info`
                )
    else: # Fallback icon
        st.markdown(f"""<span class="material-icons" style="font-size: 40px; color: var(--kaggle-icon-color); margin-right:12px; vertical-align:middle;">account_circle</span>""", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="user-details-sidebar">
            <div>{current_username_display}</div>
            <div>{user_details_display.get('position', 'N/A')}</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation Menu
    # Using Bootstrap Icons by default for streamlit-option-menu
    app_menu_options = ["Attendance", "Upload Activity Photo", "Allowance", "Goal Tracker", "Payment Collection Tracker", "View Logs", "Create Order"]
    app_menu_icons = ['calendar2-check', 'camera', 'wallet2', 'graph-up-arrow', 'cash-coin', 'journal-text', 'cart-plus-fill']
    
    # Default to "Attendance" if current active page is not in options (e.g., after logout/login)
    if st.session_state.get('active_page') not in app_menu_options:
        st.session_state.active_page = "Attendance" # Or your preferred default
    
    default_app_menu_index = app_menu_options.index(st.session_state.active_page)

    selected = option_menu(
        menu_title=None,
        options=app_menu_options,
        icons=app_menu_icons,
        default_index=default_app_menu_index,
        orientation="vertical",
        on_change=lambda key: st.session_state.update(active_page=key),
        styles={
            "container": {"padding": "0px 8px !important", "background-color": "var(--kaggle-light-bg)"},
            "icon": {"color": "var(--kaggle-icon-color)", "font-size": "18px", "margin-right":"10px"},
            "nav-link": {
                "font-size": "0.9rem", # Slightly larger nav text
                "text-align": "left",
                "margin": "4px 0px",
                "padding": "10px 16px",
                "color": "var(--kaggle-dark-text)", # Darker text for light bg
                "border-radius": "6px",
                "--hover-color": "var(--kaggle-hover-bg)" # Use CSS var for hover
            },
            "nav-link-selected": {
                "background-color": "var(--kaggle-selected-bg)",
                "color": "var(--kaggle-selected-text)",
                "font-weight": "500",
            },
            "nav-link-selected > i.icon": { # Target icon within selected link for Bootstrap Icons
                 "color": "var(--kaggle-icon-selected-color) !important",
             }
        }
    )
    
    # Logout Button
    st.markdown('<div class="logout-button-container-sidebar">', unsafe_allow_html=True)
    # You can use a Bootstrap icon here too if preferred, e.g. <i class="bi bi-box-arrow-right"></i>
    logout_label_html_app = """<span class="material-symbols-outlined">logout</span> Logout"""
    if st.button(logout_label_html_app, key="logout_sidebar_app_btn", use_container_width=True, unsafe_allow_html=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."
        st.session_state.message_type = "info"
        st.session_state.active_page = app_menu_options[0] # Reset to first page on logout
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# --- MAIN CONTENT PAGE ROUTING (using `selected` from option_menu) ---
# (Plotting functions: render_goal_chart, create_donut_chart, create_team_progress_bar_chart - keep as before)
# ... (plotting functions definitions from your previous full code) ...
def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty: st.warning("No data to plot."); return
    df_chart = df.copy(); df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear", value_vars=["TargetAmount", "AchievedAmount"], var_name="Metric", value_name="Amount")
    if df_melted.empty: st.warning(f"No data to plot for {chart_title}."); return
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group", labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"}, title=chart_title, color_discrete_map={'TargetAmount': '#20BEFF', 'AchievedAmount': '#34A853'}) # Kaggle blue, Green
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#333333')
    fig.update_xaxes(showgrid=False, zeroline=False, color='#555555'); fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False, color='#555555')
    st.plotly_chart(fig, use_container_width=True)

def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#20BEFF', remaining_color='#E0E0E0', center_text_color='#333333'):
    fig, ax = plt.subplots(figsize=(2.2, 2.2), dpi=110); fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    progress_percentage = max(0.0, min(float(progress_percentage), 100.0)); remaining_percentage = 100.0 - progress_percentage
    if progress_percentage <= 0.01: sizes = [100.0]; slice_colors = [remaining_color]; actual_progress_display = 0.0
    elif progress_percentage >= 99.99: sizes = [100.0]; slice_colors = [achieved_color]; actual_progress_display = 100.0
    else: sizes = [progress_percentage, remaining_percentage]; slice_colors = [achieved_color, remaining_color]; actual_progress_display = progress_percentage
    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.35, edgecolor='#FFFFFF'))
    centre_circle = plt.Circle((0,0),0.65,fc='#FFFFFF'); fig.gca().add_artist(centre_circle)
    text_color_to_use = center_text_color if actual_progress_display > 0 else '#777777'
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=10, fontweight='bold', color=text_color_to_use)
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0); return fig

def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee"):
    if summary_df.empty: return None
    labels = summary_df[user_col].tolist(); target_amounts = summary_df[target_col].fillna(0).tolist(); achieved_amounts = summary_df[achieved_col].fillna(0).tolist()
    x = np.arange(len(labels)); width = 0.35
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.7), 4.5), dpi=110, facecolor='rgba(0,0,0,0)'); ax.set_facecolor('rgba(0,0,0,0)')
    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color='rgba(32, 190, 255, 0.8)'); rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color='rgba(52, 168, 83, 0.8)')
    ax.set_ylabel('Amount (INR)', fontsize=9, color='#555555'); ax.set_title(title, fontsize=11, fontweight='bold', pad=12, color='#333333')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8, color='#555555')
    legend = ax.legend(fontsize=8, facecolor='rgba(255,255,255,0.8)', edgecolor='#E0E0E0');
    for text in legend.get_texts(): text.set_color('#333333')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.spines['bottom'].set_color('#E0E0E0'); ax.spines['left'].set_color('#E0E0E0')
    ax.tick_params(axis='x', colors='#555555'); ax.tick_params(axis='y', colors='#555555')
    ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#E0E0E0')
    def autolabel(rects_group, bar_color_text):
        for rect_item in rects_group:
            height_item = rect_item.get_height()
            if height_item > 0: ax.annotate(f'{height_item:,.0f}', xy=(rect_item.get_x() + rect_item.get_width() / 2, height_item), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=6, color=bar_color_text)
    autolabel(rects1, '#007bff'); autolabel(rects2, '#188038'); fig.tight_layout(pad=1.2); return fig


# The rest of your page logic (Attendance, Upload Photo, etc.) goes here,
# using `if selected == "Page Name":` for routing.
# Ensure you copy the full logic for each page from your previous complete code.

if selected == "Attendance":
    # ... (Your full Attendance page logic from the previous complete code) ...
    # Example:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    # ... your attendance implementation ...
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Upload Activity Photo":
    # ... (Your full Upload Activity Photo page logic) ...
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    # ... your upload photo implementation ...
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Allowance":
    # ... (Your full Allowance page logic) ...
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Goal Tracker":
    # ... (Your full Goal Tracker page logic) ...
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Payment Collection Tracker":
    # ... (Your full Payment Collection Tracker page logic) ...
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "View Logs":
    # ... (Your full View Logs page logic) ...
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 View Logs</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Create Order":
    # ... (Your full Create Order page logic) ...
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🛒 Create New Order</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Default to "Home" or your first actual page if 'selected' somehow becomes None
# Though option_menu should always return a valid option or the default.
elif selected == "Home" or selected is None: # Added a Home option
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(f"🏠 Welcome Home, {current_user['username']}!") # Use current_user here
    st.write("Select an option from the sidebar to manage your activities.")
    st.markdown('</div>', unsafe_allow_html=True)
