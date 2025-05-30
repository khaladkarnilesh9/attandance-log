import streamlit as st
import pandas as pd
from datetime import datetime, timezone
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

# --- Bootstrap and Material Icons CDN & Custom CSS ---
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* Apply Roboto to the whole app, and Material Symbols Outlined for icons */
    body, .stButton button, .stTextInput input, .stTextArea textarea, .stSelectbox select, .stRadio div label {
        font-family: 'Roboto', sans-serif;
    }
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined';
        font-weight: normal;
        font-style: normal;
        font-size: 22px;  /* Base size for icons */
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
        vertical-align: middle;  /* Align icons nicely with text */
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
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        padding: 0.5rem 0.75rem !important;
        margin-bottom: 0.125rem !important;
        border-radius: 0.375rem !important;
        text-decoration: none !important;
        color: #212529 !important;
        transition: background-color 0.15s ease-in-out, color 0.15s ease-in-out;
    }
    .sidebar-nav-item:hover {
        background-color: #e9ecef !important;
        color: #000 !important;
    }
    
    /* Icon container within the nav item (first column) */
    .sidebar-nav-item .icon-container {
        display: flex;
        align-items: center;
        justify-content: center;
        /* margin-right: 8px; */ /* Handled by column gap now */
    }
    .sidebar-nav-item .icon-container .material-symbols-outlined {
        font-size: 20px !important;
        color: inherit;
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
        background-color: transparent !important;
        color: inherit !important;
        box-shadow: none !important;
        outline: none !important;
        cursor: pointer;
    }
    /* Hover/focus for the button itself - should be minimal as .sidebar-nav-item handles visual hover */
    .sidebar-nav-item .stButton button:hover,
    .sidebar-nav-item .stButton button:focus,
    .sidebar-nav-item .stButton button:active {
        background-color: transparent !important;
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
    /* Icon and button text color for active item */
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
        padding-left: 0.5rem;
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
        border: 2px solid #dee2e6;
    }
    .user-position-text {
        text-align: center;
        font-size: 0.875em;
        color: #6c757d;
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
        background-color: #dc3545 !important; /* Bootstrap danger color for logout */
        color: white !important;
        border: none !important;
        width: 100% !important;
        font-weight: 500 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0.375rem;
    }
    .logout-button-container .stButton button:hover {
        background-color: #c82333 !important; /* Darker danger on hover */
        color: white !important;
    }
    .logout-button-container .stButton button .material-symbols-outlined {
        margin-right: 8px;
        font-size: 20px;
        color: white; /* Ensure icon is white */
    }
    
    /* General Card Styling for Main Content */
    .card {
        background-color: #fff;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .card h3, .card h4, .card h5 {
        color: #343a40;
        margin-bottom: 1rem;
    }
    .stAlert {
        border-radius: 0.375rem;
    }
    .stRadio > label { /* Target the actual label of st.radio for font family */
        font-family: 'Roboto', sans-serif;
    }
    
    /* Global message notification styling (kept as is) */
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
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"
GOALS_FILE = "goals.csv"
PAYMENT_GOALS_FILE = "payment_goals.csv"
ACTIVITY_LOG_FILE = "activity_log.csv"
ACTIVITY_PHOTOS_DIR = "activity_photos"
ATTENDANCE_PHOTOS_DIR = "attendance_photos" # Not used in current logic, but kept for completeness

for dir_path in [ACTIVITY_PHOTOS_DIR, ATTENDANCE_PHOTOS_DIR]:
    if not os.path.exists(dir_path):
        try: os.makedirs(dir_path)
        except OSError: pass

TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'. Please use a valid IANA timezone.")
    st.stop()

def get_current_time_in_tz():
    return datetime.now(timezone.utc).astimezone(tz)

def get_quarter_str_for_year(year):
    now_month = get_current_time_in_tz().month
    if 1 <= now_month <= 3: return f"{year}-Q1"
    elif 4 <= now_month <= 6: return f"{year}-Q2"
    elif 7 <= now_month <= 9: return f"{year}-Q3"
    else: return f"{year}-Q4"

# --- Load or create data ---
# This function now returns the dataframe and is responsible for initial load
# It will be called once to populate session state
def load_dataframe_from_csv(path, columns):
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
        except Exception as e:
            st.error(f"Error loading {path}: {e}. Returning empty DataFrame.");
            return pd.DataFrame(columns=columns)
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

# --- Session State Initialization ---
# Initialize session state variables for authentication and page navigation
if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}
if "active_page" not in st.session_state: st.session_state.active_page = "Attendance" # Default page

# Load dataframes into session state only once
if "attendance_df" not in st.session_state:
    st.session_state.attendance_df = load_dataframe_from_csv(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
if "allowance_df" not in st.session_state:
    st.session_state.allowance_df = load_dataframe_from_csv(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
if "goals_df" not in st.session_state:
    st.session_state.goals_df = load_dataframe_from_csv(GOALS_FILE, GOALS_COLUMNS)
if "payment_goals_df" not in st.session_state:
    st.session_state.payment_goals_df = load_dataframe_from_csv(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
if "activity_log_df" not in st.session_state:
    st.session_state.activity_log_df = load_dataframe_from_csv(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS)


# --- Charting Functions ---
def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty:
        st.warning("No data available to plot."); return
    df_chart = df.copy()
    df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear", value_vars=["TargetAmount", "AchievedAmount"], var_name="Metric", value_name="Amount")
    if df_melted.empty:
        st.warning(f"No data to plot for {chart_title} after processing."); return
    
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group",
                    labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"},
                    title=chart_title, color_discrete_map={'TargetAmount': '#3498db', 'AchievedAmount': '#2ecc71'})
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric')
    fig.update_xaxes(type='category')
    st.plotly_chart(fig, use_container_width=True)

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

# --- Global Message Display Function ---
def display_message():
    if st.session_state.user_message:
        message_type = st.session_state.get("message_type", "info")
        st.markdown(
            f"<div class='custom-notification {message_type}'>{st.session_state.user_message}</div>",
            unsafe_allow_html=True
        )
        st.session_state.user_message = None
        st.session_state.message_type = None

# --- Page Functions ---

def attendance_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled for attendance. Photos for specific activities can be uploaded from the 'Upload Activity Photo' section.", icon="ℹ️")
    
    st.markdown("---")
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    common_data = {"Username": st.session_state.auth["username"], "Latitude": pd.NA, "Longitude": pd.NA}

    def process_general_attendance(attendance_type):
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_data = {"Type": attendance_type, "Timestamp": now_str_display, **common_data}
        for col_name in ATTENDANCE_COLUMNS:
            if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
        new_entry_df = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
        
        # Concat and save directly to session state dataframe
        st.session_state.attendance_df = pd.concat([st.session_state.attendance_df, new_entry_df], ignore_index=True)
        try:
            st.session_state.attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."
            st.session_state.message_type = "success"
        except Exception as e:
            st.session_state.user_message = f"Error saving attendance: {e}"
            st.session_state.message_type = "error"
        st.rerun() # Rerun to display message and update state

    with col1:
        if st.button("✅ Check In", key="check_in_btn_main_no_photo", use_container_width=True, type="primary"):
            process_general_attendance("Check-In")
    with col2:
        if st.button("🚪 Check Out", key="check_out_btn_main_no_photo", use_container_width=True, type="primary"):
            process_general_attendance("Check-Out")
    st.markdown('</div></div>', unsafe_allow_html=True)

def upload_activity_photo_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat, current_lon = pd.NA, pd.NA # Placeholder, actual location capture not implemented
    
    with st.form(key="activity_photo_form", clear_on_submit=True):
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description of activity/visit:", key="activity_desc_input")
        img_file_buffer_activity = st.camera_input("Take a picture of your activity/visit", key="activity_camera_input")
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo and Log Activity")
    
    if submit_activity_photo:
        if img_file_buffer_activity is None:
            st.session_state.user_message = "Please take a picture before submitting."
            st.session_state.message_type = "warning"
        elif not activity_description.strip():
            st.session_state.user_message = "Please provide a description for the activity."
            st.session_state.message_type = "warning"
        else:
            now_for_filename = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S")
            now_for_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            image_filename_activity = f"{st.session_state.auth['username']}_activity_{now_for_filename}.jpg"
            image_path_activity = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_activity)
            try:
                with open(image_path_activity, "wb") as f:
                    f.write(img_file_buffer_activity.getbuffer())
                
                new_activity_data = {
                    "Username": st.session_state.auth["username"],
                    "Timestamp": now_for_display,
                    "Description": activity_description,
                    "ImageFile": image_filename_activity,
                    "Latitude": current_lat,
                    "Longitude": current_lon
                }
                new_activity_entry_df = pd.DataFrame([new_activity_data], columns=ACTIVITY_LOG_COLUMNS)
                
                st.session_state.activity_log_df = pd.concat([st.session_state.activity_log_df, new_activity_entry_df], ignore_index=True)
                st.session_state.activity_log_df.to_csv(ACTIVITY_LOG_FILE, index=False)

                st.session_state.user_message = "Activity photo and log uploaded!"
                st.session_state.message_type = "success"
            except Exception as e:
                st.session_state.user_message = f"Error saving activity: {e}"
                st.session_state.message_type = "error"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def allowance_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    
    a_type = st.radio("Allowance Type", ["Travel", "Dinner", "Medical", "Internet", "Other"],
                      key="allowance_type_radio_main", horizontal=True)
    amount = st.number_input("Enter Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_main")
    reason = st.text_area("Reason for Allowance:", key="allowance_reason_main", placeholder="Please provide a clear justification...")
    
    if st.button("Submit Allowance Request", key="submit_allowance_btn_main", use_container_width=True, type="primary"):
        if a_type and amount > 0 and reason.strip():
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry_data = {
                "Username": st.session_state.auth["username"], "Type": a_type,
                "Amount": amount, "Reason": reason, "Date": date_str
            }
            new_entry_df = pd.DataFrame([new_entry_data], columns=ALLOWANCE_COLUMNS)
            
            st.session_state.allowance_df = pd.concat([st.session_state.allowance_df, new_entry_df], ignore_index=True)
            try:
                st.session_state.allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                st.session_state.user_message = f"Allowance for ₹{amount:.2f} submitted."
                st.session_state.message_type = "success"
            except Exception as e:
                st.session_state.user_message = f"Error submitting allowance: {e}"
                st.session_state.message_type = "error"
            st.rerun()
        else:
            st.session_state.user_message = "Please complete all fields with valid values."
            st.session_state.message_type = "warning"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def goal_tracker_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_GOAL_YEAR = 2025
    current_quarter_for_display = get_quarter_str_for_year(TARGET_GOAL_YEAR)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    
    if st.session_state.auth["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR}"],
                                key="admin_goal_action_radio_2025_q", horizontal=True)
        
        if admin_action == "View Team Progress":
            st.markdown(f"<h5>Team Goal Progress for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            quarterly_goals_df = st.session_state.goals_df[st.session_state.goals_df["MonthYear"] == current_quarter_for_display]
            
            if not quarterly_goals_df.empty:
                # Group by Username and sum TargetAmount and AchievedAmount
                team_summary = quarterly_goals_df.groupby("Username").agg(
                    Target=('TargetAmount', 'sum'),
                    Achieved=('AchievedAmount', 'sum')
                ).reset_index()
                
                # Calculate overall progress for each user
                team_summary['Progress'] = team_summary.apply(
                    lambda row: (row['Achieved'] / row['Target'] * 100) if row['Target'] > 0 else 0, axis=1
                )
                
                st.markdown("<h6>Individual Quarterly Progress:</h6>", unsafe_allow_html=True)
                for index, row in team_summary.iterrows():
                    col1, col2 = st.columns([0.6, 0.4])
                    with col1:
                        st.markdown(f"**{row['Username']}**")
                        st.progress(min(row['Progress'] / 100, 1.0), text=f"Target: ₹{row['Target']:,.0f} | Achieved: ₹{row['Achieved']:,.0f}")
                    with col2:
                        fig = create_donut_chart(row['Progress'], chart_title="", center_text_color="#0d6efd")
                        st.pyplot(fig)
                
                st.markdown("---")
                st.markdown("<h6>Team Performance Summary (Bar Chart):</h6>", unsafe_allow_html=True)
                bar_fig = create_team_progress_bar_chart(team_summary, title=f"Team Goals for {current_quarter_for_display}")
                if bar_fig:
                    st.pyplot(bar_fig)
            else:
                st.info(f"No goals set for the team for {current_quarter_for_display} yet.")
        
        elif admin_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set/Edit Goals for Employees ({TARGET_GOAL_YEAR})</h5>", unsafe_allow_html=True)
            selected_employee = st.selectbox("Select Employee", list(USERS.keys()), key="goal_employee_select")
            selected_quarter = st.selectbox("Select Quarter", [f"{TARGET_GOAL_YEAR}-Q1", f"{TARGET_GOAL_YEAR}-Q2", f"{TARGET_GOAL_YEAR}-Q3", f"{TARGET_GOAL_YEAR}-Q4"], key="goal_quarter_select")

            current_goal_for_employee_quarter = st.session_state.goals_df[
                (st.session_state.goals_df["Username"] == selected_employee) &
                (st.session_state.goals_df["MonthYear"] == selected_quarter)
            ]
            
            # Pre-fill form if a goal exists
            default_description = ""
            default_target = 0.0
            default_achieved = 0.0
            default_status = "Not Started"

            if not current_goal_for_employee_quarter.empty:
                first_goal = current_goal_for_employee_quarter.iloc[0]
                default_description = first_goal["GoalDescription"] if pd.notna(first_goal["GoalDescription"]) else ""
                default_target = first_goal["TargetAmount"] if pd.notna(first_goal["TargetAmount"]) else 0.0
                default_achieved = first_goal["AchievedAmount"] if pd.notna(first_goal["AchievedAmount"]) else 0.0
                default_status = first_goal["Status"] if pd.notna(first_goal["Status"]) else "Not Started"

            with st.form(key="set_goal_form", clear_on_submit=False):
                goal_description = st.text_area("Goal Description:", value=default_description, key="admin_goal_desc")
                target_amount = st.number_input("Target Amount (INR):", min_value=0.0, value=float(default_target), step=1000.0, format="%.2f", key="admin_target_amount")
                achieved_amount = st.number_input("Achieved Amount (INR):", min_value=0.0, value=float(default_achieved), step=100.0, format="%.2f", key="admin_achieved_amount")
                goal_status = st.selectbox("Status:", status_options, index=status_options.index(default_status) if default_status in status_options else 0, key="admin_goal_status")
                
                submit_goal = st.form_submit_button("Save Goal")
            
            if submit_goal:
                if not goal_description.strip() or target_amount <= 0:
                    st.session_state.user_message = "Please provide a description and a positive target amount."
                    st.session_state.message_type = "warning"
                else:
                    new_goal_data = {
                        "Username": selected_employee,
                        "MonthYear": selected_quarter,
                        "GoalDescription": goal_description,
                        "TargetAmount": target_amount,
                        "AchievedAmount": achieved_amount,
                        "Status": goal_status
                    }
                    
                    if not current_goal_for_employee_quarter.empty:
                        # Update existing entry
                        idx = current_goal_for_employee_quarter.index[0]
                        for col, val in new_goal_data.items():
                            st.session_state.goals_df.loc[idx, col] = val
                        st.session_state.user_message = f"Goal for {selected_employee} in {selected_quarter} updated."
                    else:
                        # Add new entry
                        new_goal_df = pd.DataFrame([new_goal_data], columns=GOALS_COLUMNS)
                        st.session_state.goals_df = pd.concat([st.session_state.goals_df, new_goal_df], ignore_index=True)
                        st.session_state.user_message = f"New goal set for {selected_employee} in {selected_quarter}."
                    
                    try:
                        st.session_state.goals_df.to_csv(GOALS_FILE, index=False)
                        st.session_state.message_type = "success"
                    except Exception as e:
                        st.session_state.user_message = f"Error saving goal: {e}"
                        st.session_state.message_type = "error"
                st.rerun()

    else: # Employee View
        st.markdown("<h4>My Sales Goals</h4>", unsafe_allow_html=True)
        user_goals = st.session_state.goals_df[st.session_state.goals_df["Username"] == st.session_state.auth["username"]].copy()
        
        if not user_goals.empty:
            # Ensure numeric types
            user_goals["TargetAmount"] = pd.to_numeric(user_goals["TargetAmount"], errors='coerce').fillna(0)
            user_goals["AchievedAmount"] = pd.to_numeric(user_goals["AchievedAmount"], errors='coerce').fillna(0)
            
            st.markdown(f"<h5>Goals for {st.session_state.auth['username']} for {TARGET_GOAL_YEAR}:</h5>", unsafe_allow_html=True)
            for index, row in user_goals.sort_values(by="MonthYear").iterrows():
                progress_percentage = (row['AchievedAmount'] / row['TargetAmount'] * 100) if row['TargetAmount'] > 0 else 0
                
                expander = st.expander(f"**{row['MonthYear']}** - {row['GoalDescription']}")
                with expander:
                    st.write(f"**Status:** {row['Status']}")
                    st.write(f"**Target:** ₹{row['TargetAmount']:,.2f}")
                    st.write(f"**Achieved:** ₹{row['AchievedAmount']:,.2f}")
                    
                    col_prog, col_donut = st.columns([2,1])
                    with col_prog:
                        st.progress(min(progress_percentage / 100, 1.0), text=f"Progress: {progress_percentage:.0f}%")
                    with col_donut:
                        donut_fig = create_donut_chart(progress_percentage)
                        st.pyplot(donut_fig)
                    
                    # Option for employee to update achieved amount (optional, depending on flow)
                    if row["Status"] != "Achieved" and row["Status"] != "Cancelled":
                        with st.form(key=f"update_achieved_form_{row['MonthYear']}", clear_on_submit=True):
                            new_achieved = st.number_input("Update Achieved Amount (INR):", min_value=float(row['AchievedAmount']), step=100.0, format="%.2f", key=f"new_achieved_{row['MonthYear']}")
                            update_status = st.selectbox("Update Status:", status_options, index=status_options.index(row['Status']) if row['Status'] in status_options else 0, key=f"update_status_{row['MonthYear']}")
                            update_button = st.form_submit_button("Update Goal Progress")
                            if update_button:
                                try:
                                    idx_to_update = st.session_state.goals_df[(st.session_state.goals_df["Username"] == row["Username"]) & (st.session_state.goals_df["MonthYear"] == row["MonthYear"])].index[0]
                                    st.session_state.goals_df.loc[idx_to_update, "AchievedAmount"] = new_achieved
                                    st.session_state.goals_df.loc[idx_to_update, "Status"] = update_status
                                    st.session_state.goals_df.to_csv(GOALS_FILE, index=False)
                                    st.session_state.user_message = "Goal progress updated successfully!"
                                    st.session_state.message_type = "success"
                                except Exception as e:
                                    st.session_state.user_message = f"Error updating goal: {e}"
                                    st.session_state.message_type = "error"
                                st.rerun()

            st.markdown("---")
            render_goal_chart(user_goals, f"My Quarterly Sales Goals for {TARGET_GOAL_YEAR}")
        else:
            st.info("No sales goals have been set for you yet.")
    st.markdown('</div>', unsafe_allow_html=True)

def payment_collection_tracker_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_COLLECTION_YEAR = 2025
    current_quarter_for_display = get_quarter_str_for_year(TARGET_COLLECTION_YEAR)
    status_options = ["Pending", "In Progress", "Collected", "Overdue"]

    if st.session_state.auth["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Payment Collections</h4>", unsafe_allow_html=True)
        admin_action_payment = st.radio("Action:", ["View Team Collection Progress", f"Set/Edit Collection Goal for {TARGET_COLLECTION_YEAR}"],
                                        key="admin_payment_action_radio", horizontal=True)

        if admin_action_payment == "View Team Collection Progress":
            st.markdown(f"<h5>Team Collection Progress for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            quarterly_payment_goals_df = st.session_state.payment_goals_df[st.session_state.payment_goals_df["MonthYear"] == current_quarter_for_display]

            if not quarterly_payment_goals_df.empty:
                team_payment_summary = quarterly_payment_goals_df.groupby("Username").agg(
                    Target=('TargetAmount', 'sum'),
                    Achieved=('AchievedAmount', 'sum')
                ).reset_index()
                
                team_payment_summary['Progress'] = team_payment_summary.apply(
                    lambda row: (row['Achieved'] / row['Target'] * 100) if row['Target'] > 0 else 0, axis=1
                )

                st.markdown("<h6>Individual Quarterly Collection Progress:</h6>", unsafe_allow_html=True)
                for index, row in team_payment_summary.iterrows():
                    col1, col2 = st.columns([0.6, 0.4])
                    with col1:
                        st.markdown(f"**{row['Username']}**")
                        st.progress(min(row['Progress'] / 100, 1.0), text=f"Target: ₹{row['Target']:,.0f} | Collected: ₹{row['Achieved']:,.0f}")
                    with col2:
                        fig = create_donut_chart(row['Progress'], chart_title="", center_text_color="#0d6efd")
                        st.pyplot(fig)
                
                st.markdown("---")
                st.markdown("<h6>Team Collection Performance Summary (Bar Chart):</h6>", unsafe_allow_html=True)
                bar_fig = create_team_progress_bar_chart(team_payment_summary, title=f"Team Collection Goals for {current_quarter_for_display}", achieved_col="Achieved")
                if bar_fig:
                    st.pyplot(bar_fig)
            else:
                st.info(f"No payment collection goals set for the team for {current_quarter_for_display} yet.")

        elif admin_action_payment == f"Set/Edit Collection Goal for {TARGET_COLLECTION_YEAR}":
            st.markdown(f"<h5>Set/Edit Collection Goals for Employees ({TARGET_COLLECTION_YEAR})</h5>", unsafe_allow_html=True)
            selected_employee = st.selectbox("Select Employee", list(USERS.keys()), key="payment_goal_employee_select")
            selected_quarter = st.selectbox("Select Quarter", [f"{TARGET_COLLECTION_YEAR}-Q1", f"{TARGET_COLLECTION_YEAR}-Q2", f"{TARGET_COLLECTION_YEAR}-Q3", f"{TARGET_COLLECTION_YEAR}-Q4"], key="payment_goal_quarter_select")

            current_payment_goal_for_employee_quarter = st.session_state.payment_goals_df[
                (st.session_state.payment_goals_df["Username"] == selected_employee) &
                (st.session_state.payment_goals_df["MonthYear"] == selected_quarter)
            ]
            
            default_description = ""
            default_target = 0.0
            default_achieved = 0.0
            default_status = "Pending"

            if not current_payment_goal_for_employee_quarter.empty:
                first_goal = current_payment_goal_for_employee_quarter.iloc[0]
                default_description = first_goal["GoalDescription"] if pd.notna(first_goal["GoalDescription"]) else ""
                default_target = first_goal["TargetAmount"] if pd.notna(first_goal["TargetAmount"]) else 0.0
                default_achieved = first_goal["AchievedAmount"] if pd.notna(first_goal["AchievedAmount"]) else 0.0
                default_status = first_goal["Status"] if pd.notna(first_goal["Status"]) else "Pending"

            with st.form(key="set_payment_goal_form", clear_on_submit=False):
                goal_description = st.text_area("Collection Goal Description:", value=default_description, key="admin_payment_goal_desc")
                target_amount = st.number_input("Target Collection Amount (INR):", min_value=0.0, value=float(default_target), step=1000.0, format="%.2f", key="admin_payment_target_amount")
                achieved_amount = st.number_input("Achieved Collection Amount (INR):", min_value=0.0, value=float(default_achieved), step=100.0, format="%.2f", key="admin_payment_achieved_amount")
                goal_status = st.selectbox("Status:", status_options, index=status_options.index(default_status) if default_status in status_options else 0, key="admin_payment_goal_status")
                
                submit_payment_goal = st.form_submit_button("Save Collection Goal")
            
            if submit_payment_goal:
                if not goal_description.strip() or target_amount <= 0:
                    st.session_state.user_message = "Please provide a description and a positive target amount."
                    st.session_state.message_type = "warning"
                else:
                    new_payment_goal_data = {
                        "Username": selected_employee,
                        "MonthYear": selected_quarter,
                        "GoalDescription": goal_description,
                        "TargetAmount": target_amount,
                        "AchievedAmount": achieved_amount,
                        "Status": goal_status
                    }
                    
                    if not current_payment_goal_for_employee_quarter.empty:
                        idx = current_payment_goal_for_employee_quarter.index[0]
                        for col, val in new_payment_goal_data.items():
                            st.session_state.payment_goals_df.loc[idx, col] = val
                        st.session_state.user_message = f"Collection goal for {selected_employee} in {selected_quarter} updated."
                    else:
                        new_payment_goal_df = pd.DataFrame([new_payment_goal_data], columns=PAYMENT_GOALS_COLUMNS)
                        st.session_state.payment_goals_df = pd.concat([st.session_state.payment_goals_df, new_payment_goal_df], ignore_index=True)
                        st.session_state.user_message = f"New collection goal set for {selected_employee} in {selected_quarter}."
                    
                    try:
                        st.session_state.payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                        st.session_state.message_type = "success"
                    except Exception as e:
                        st.session_state.user_message = f"Error saving collection goal: {e}"
                        st.session_state.message_type = "error"
                st.rerun()

    else: # Employee View
        st.markdown("<h4>My Payment Collection Goals</h4>", unsafe_allow_html=True)
        user_payment_goals = st.session_state.payment_goals_df[st.session_state.payment_goals_df["Username"] == st.session_state.auth["username"]].copy()
        
        if not user_payment_goals.empty:
            user_payment_goals["TargetAmount"] = pd.to_numeric(user_payment_goals["TargetAmount"], errors='coerce').fillna(0)
            user_payment_goals["AchievedAmount"] = pd.to_numeric(user_payment_goals["AchievedAmount"], errors='coerce').fillna(0)

            st.markdown(f"<h5>Collection Goals for {st.session_state.auth['username']} for {TARGET_COLLECTION_YEAR}:</h5>", unsafe_allow_html=True)
            for index, row in user_payment_goals.sort_values(by="MonthYear").iterrows():
                progress_percentage = (row['AchievedAmount'] / row['TargetAmount'] * 100) if row['TargetAmount'] > 0 else 0
                
                expander = st.expander(f"**{row['MonthYear']}** - {row['GoalDescription']}")
                with expander:
                    st.write(f"**Status:** {row['Status']}")
                    st.write(f"**Target:** ₹{row['TargetAmount']:,.2f}")
                    st.write(f"**Collected:** ₹{row['AchievedAmount']:,.2f}")
                    
                    col_prog, col_donut = st.columns([2,1])
                    with col_prog:
                        st.progress(min(progress_percentage / 100, 1.0), text=f"Progress: {progress_percentage:.0f}%")
                    with col_donut:
                        donut_fig = create_donut_chart(progress_percentage)
                        st.pyplot(donut_fig)
                    
                    if row["Status"] != "Collected":
                        with st.form(key=f"update_collected_form_{row['MonthYear']}", clear_on_submit=True):
                            new_achieved = st.number_input("Update Collected Amount (INR):", min_value=float(row['AchievedAmount']), step=100.0, format="%.2f", key=f"new_collected_{row['MonthYear']}")
                            update_status = st.selectbox("Update Status:", status_options, index=status_options.index(row['Status']) if row['Status'] in status_options else 0, key=f"update_payment_status_{row['MonthYear']}")
                            update_button = st.form_submit_button("Update Collection Progress")
                            if update_button:
                                try:
                                    idx_to_update = st.session_state.payment_goals_df[(st.session_state.payment_goals_df["Username"] == row["Username"]) & (st.session_state.payment_goals_df["MonthYear"] == row["MonthYear"])].index[0]
                                    st.session_state.payment_goals_df.loc[idx_to_update, "AchievedAmount"] = new_achieved
                                    st.session_state.payment_goals_df.loc[idx_to_update, "Status"] = update_status
                                    st.session_state.payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                                    st.session_state.user_message = "Collection goal progress updated successfully!"
                                    st.session_state.message_type = "success"
                                except Exception as e:
                                    st.session_state.user_message = f"Error updating collection goal: {e}"
                                    st.session_state.message_type = "error"
                                st.rerun()
            st.markdown("---")
            render_goal_chart(user_payment_goals, f"My Quarterly Payment Collections for {TARGET_COLLECTION_YEAR}")
        else:
            st.info("No payment collection goals have been set for you yet.")
    st.markdown('</div>', unsafe_allow_html=True)

def view_logs_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📋 View All Logs</h3>", unsafe_allow_html=True)

    log_type = st.radio("Select Log Type:", ["Attendance Logs", "Activity Logs", "Allowance Logs", "Sales Goals", "Payment Goals"], horizontal=True, key="log_type_radio")

    df_to_display = pd.DataFrame()
    log_title = ""
    if log_type == "Attendance Logs":
        df_to_display = st.session_state.attendance_df.copy()
        log_title = "Recent Attendance Entries"
    elif log_type == "Activity Logs":
        df_to_display = st.session_state.activity_log_df.copy()
        log_title = "Recent Activity Entries"
    elif log_type == "Allowance Logs":
        df_to_display = st.session_state.allowance_df.copy()
        log_title = "Recent Allowance Requests"
    elif log_type == "Sales Goals":
        df_to_display = st.session_state.goals_df.copy()
        log_title = "Sales Goals"
    elif log_type == "Payment Goals":
        df_to_display = st.session_state.payment_goals_df.copy()
        log_title = "Payment Collection Goals"
    
    # Filter by current user if not admin
    if st.session_state.auth["role"] != "admin":
        df_to_display = df_to_display[df_to_display["Username"] == st.session_state.auth["username"]]

    st.markdown(f"<h4>{log_title}</h4>", unsafe_allow_html=True)
    if not df_to_display.empty:
        st.dataframe(df_to_display, use_container_width=True)
        # If activity logs, show images
        if log_type == "Activity Logs":
            st.markdown("<h5>Activity Photos:</h5>", unsafe_allow_html=True)
            for index, row in df_to_display.iterrows():
                if pd.notna(row["ImageFile"]):
                    img_path = os.path.join(ACTIVITY_PHOTOS_DIR, row["ImageFile"])
                    if os.path.exists(img_path):
                        st.image(img_path, caption=f"{row['Timestamp']} - {row['Description']}", width=200)
                    else:
                        st.warning(f"Image not found: {row['ImageFile']}")
    else:
        st.info("No logs to display for this category or user.")
    st.markdown('</div>', unsafe_allow_html=True)

def create_order_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🛒 Create New Order</h3>", unsafe_allow_html=True)
    st.warning("This feature is under construction. Please check back later!", icon="🚧")
    # You can add a simple form here for order details if needed
    st.markdown('</div>', unsafe_allow_html=True)


# --- Login Logic ---
if not st.session_state.auth["logged_in"]:
    st.title("TrackSphere Login")
    display_message() # Display any pending messages for login
    
    st.markdown("<h3>🔐 Login</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname")
    pwd = st.text_input("Password", type="password", key="login_pwd")
    if st.button("Login", key="login_button", type="primary"):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = "Login successful!"; st.session_state.message_type = "success"
            st.rerun() # Rerun to show main app and clear login form
        else:
            st.session_state.user_message = "Invalid username or password."
            st.session_state.message_type = "error"
            st.rerun() # Rerun to display error message using the global message system
    st.stop() # Stop execution here if not logged in

# --- Main Application (Post-Login) ---
current_user = st.session_state.auth # User is authenticated at this point

# Global Message Display for Main Application
display_message()

# --- Sidebar Navigation ---
nav_options_with_icons = [
    {"label": "Attendance", "icon": "schedule", "function": attendance_page},
    {"label": "Upload Activity Photo", "icon": "add_a_photo", "function": upload_activity_photo_page},
    {"label": "Allowance", "icon": "payments", "function": allowance_page},
    {"label": "Goal Tracker", "icon": "emoji_events", "function": goal_tracker_page},
    {"label": "Payment Collection Tracker", "icon": "receipt_long", "function": payment_collection_tracker_page},
    {"label": "View Logs", "icon": "wysiwyg", "function": view_logs_page},
    {"label": "Create Order", "icon": "add_shopping_cart", "function": create_order_page}
]

def set_active_page_callback(page_name):
    st.session_state.active_page = page_name

with st.sidebar:
    st.markdown('<div class="sidebar-content-wrapper">', unsafe_allow_html=True)

    # User Info
    st.markdown(f"<div class='welcome-text-sidebar'>Welcome, **{current_user['username']}**!</div>", unsafe_allow_html=True)
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
        button_key = f"nav_btn_{i}"
        is_active = (st.session_state.active_page == option_label)
        active_class = "active-nav-item" if is_active else ""

        # Using st.columns for better structural control within the HTML div
        nav_item_cols = st.columns([1, 4], gap="small")
        with nav_item_cols[0]: # Icon column
            # Open the sidebar-nav-item div here, it will be closed by the next st.markdown below
            st.markdown(f'<div class="sidebar-nav-item {active_class}"><div class="icon-container"><span class="material-symbols-outlined">{option_icon}</span></div>', unsafe_allow_html=True)
        with nav_item_cols[1]: # Button/Text column
            st.button(
                label=option_label,
                key=button_key,
                on_click=set_active_page_callback,
                args=(option_label,),
                use_container_width=True
            )
            # Close the sidebar-nav-item div that was opened in the first column
            # This is crucial for correctly nesting HTML and preventing the TypeError
            st.markdown('</div>', unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True) # Close .sidebar-nav

    # Logout Button
    st.markdown('<div class="logout-button-container">', unsafe_allow_html=True)
    if st.button(label="<span class='material-symbols-outlined'>logout</span> Logout", key="logout_button_sidebar", use_container_width=True, unsafe_allow_html=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."
        st.session_state.message_type = "info"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True) # Close .logout-button-container
    
    st.markdown('</div>', unsafe_allow_html=True) # Close .sidebar-content-wrapper

# --- Render Active Page ---
for item in nav_options_with_icons:
    if st.session_state.active_page == item["label"]:
        item["function"]()
        break
