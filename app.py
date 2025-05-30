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

# --- Page Configuration (MUST be the first Streamlit command) ---
st.set_page_config(
    page_title="Employee Portal",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded" # Keep sidebar expanded by default
)

# --- Bootstrap and Material Icons CDN & Custom CSS ---
# These CDN links are loaded before your custom CSS for correct layering
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* Global Styles & Resets */
    html, body {
        height: 100%;
        margin: 0;
        padding: 0;
        font-family: 'Roboto', sans-serif; /* Apply Roboto font globally */
        color: #333333; /* Default text color */
    }

    [data-testid="stAppViewContainer"] {
        background-color: #f0f2f6; /* Light gray background for the entire app */
    }

    /* Hide Streamlit's default header, footer, and toolbar */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    div[data-testid="stToolbar"] {
        visibility: hidden;
        height: 0%;
        position: fixed; /* Completely hide it */
    }

    /* Input Fields (Text, Number, Text Area, Selectbox) - Enhanced Styling */
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    div[data-baseweb="select"] input { /* Target selectbox input */
        background-color: white;
        color: #335677; /* Darker text for input values */
        border: 1px solid #ced4da; /* A slightly darker border color */
        border-radius: 8px; /* Slightly more rounded corners */
        padding: 10px 15px; /* More padding */
        font-size: 1rem; /* Standard font size */
        transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        box-shadow: none; /* Remove any default shadow */
    }

    /* Placeholder color */
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    .stNumberInput input::placeholder {
        color: #6c757d !important; /* Slightly darker grey for placeholder */
        opacity: 1; /* Ensure full visibility */
    }

    /* Focus styles for inputs */
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {
        border-color: #007bff; /* Primary blue on focus */
        box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25); /* Subtle glow */
        outline: none; /* Remove default outline */
    }
    /* Selectbox focus (it's a bit different because of BaseWeb) */
    div[data-baseweb="select"] div[role="button"]:focus-within {
        border-color: #007bff;
        box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
        outline: none;
    }

    /* Sidebar Styling (Navigation Bar Look & Feel) */
    [data-testid="stSidebar"] {
        background-color: #2c3e50; /* Darker blue-grey for sidebar background */
        padding-top: 1rem;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2); /* More prominent shadow */
    }
    [data-testid="stSidebarContent"] {
        display: flex;
        flex-direction: column;
        height: 100%; /* Make sidebar content fill height */
        padding: 0; /* Remove default sidebar padding */
    }

    /* User Profile Section in Sidebar */
    .user-profile-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1.5rem 1rem;
        margin-bottom: 1.5rem;
        text-align: center;
        background-color: #34495e; /* Slightly lighter than sidebar background */
        border-radius: 10px; /* Rounded corners for the profile box */
        margin: 1rem;
    }
    .user-profile-img {
        width: 90px; /* Slightly larger image */
        height: 90px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 0.75rem;
        border: 3px solid #f39c12; /* Accent border color */
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .welcome-text {
        font-weight: 600;
        color: white; /* White text for welcome */
        margin-bottom: 0.25rem;
        font-size: 1.2rem;
    }
    .user-position {
        font-size: 0.9rem;
        color: #bdc3c7; /* Lighter grey for position */
    }
    .divider {
        border-top: 1px solid #4a627a; /* Lighter divider for contrast */
        margin: 0.5rem 0 1.5rem 0;
    }

    /* Navigation Items (Sidebar Buttons) - Enhanced Styles */
    .sidebar-nav-item {
        display: flex;
        align-items: center;
        padding: 0.85rem 1.2rem; /* More padding for a bolder look */
        margin: 0.25rem 0.75rem; /* Space between items */
        border-radius: 8px;
        color: #ecf0f1; /* Light text color for inactive items */
        font-size: 1.05rem; /* Slightly larger font */
        font-weight: 500;
        transition: background-color 0.2s, color 0.2s, transform 0.1s;
        position: relative;
        overflow: hidden;
    }
    .sidebar-nav-item:hover {
        background-color: #3498db; /* Primary blue on hover */
        color: white;
        transform: translateX(5px); /* Slight slide effect on hover */
    }
    .sidebar-nav-item.active-nav-item {
        background-color: #007bff; /* Primary blue for active */
        color: white;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3); /* More pronounced shadow */
        transform: translateX(0); /* Ensure no slide for active */
    }
    .sidebar-nav-item .material-symbols-outlined {
        margin-right: 0.8rem; /* More space for icon */
        font-size: 1.6rem; /* Slightly larger icon */
        width: 28px; height: 28px; /* Fixed size for icons */
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #ecf0f1; /* Icon color for inactive */
    }
    .sidebar-nav-item.active-nav-item .material-symbols-outlined {
        color: white; /* Icon color for active */
    }

    /* Invisible button overlay for navigation (more robust selector) */
    .sidebar-nav-item + [data-testid="stVerticalBlock"] > [data-testid="stButton"] > button {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        opacity: 0; /* Make it invisible */
        z-index: 10; /* Ensure it's on top */
        cursor: pointer;
    }
    /* Specific override for the Streamlit button's internal structure that might be rendered */
    .sidebar-nav-item + [data-testid="stVerticalBlock"] > [data-testid="stButton"] > button > div[data-testid="baseButton-children"] {
        opacity: 0; /* Hide the default button text/icon */
    }


    /* Logout button specific styling (push to bottom) */
    .logout-container {
        margin-top: auto; /* Pushes logout button to the very bottom of the sidebar */
        padding: 1rem;
        border-top: 1px solid #4a627a; /* Divider line */
        background-color: #2c3e50; /* Match sidebar background */
    }
    .logout-container .stButton > button {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #e74c3c; /* Red for logout */
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: background-color 0.2s, transform 0.1s;
        width: 100%; /* Make button full width */
    }
    .logout-container .stButton > button:hover {
        background-color: #c0392b; /* Darker red on hover */
        transform: translateY(-2px);
    }
    .logout-container .stButton > button:active {
        background-color: #a53026;
        transform: translateY(0);
    }
    .logout-container .stButton > button .material-symbols-outlined {
        margin-right: 0.5rem;
        font-size: 1.5rem;
    }

    /* Main Content Area Styling */
    .main-content-area {
        padding: 1.5rem 2rem;
        gap: 1.5rem; /* Space between content blocks */
    }
    /* Ensure Streamlit's main block takes up correct padding */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        padding: 0; /* Remove default padding from inner vertical blocks */
    }

    .card {
        background-color: white;
        border-radius: 12px;
        padding: 2.5rem; /* More padding inside cards */
        box-shadow: 0 6px 20px rgba(0,0,0,0.1); /* Stronger, softer shadow */
        margin-bottom: 1.5rem;
    }
    .card h3, .card h4, .card h5 {
        color: #2c3e50; /* Darker color for headings */
        margin-bottom: 1.5rem;
        font-weight: 700; /* Bolder headings */
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600; /* Bolder button text */
        padding: 0.8rem 1.5rem; /* More padding for buttons */
        min-height: 45px; /* Ensure minimum height */
        transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.1s ease;
    }
    .stButton > button.primary {
        background-color: #007bff;
        color: white;
        border: none;
    }
    .stButton > button.primary:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
    }
    .stButton > button[data-testid="baseButton-secondary"] {
        background-color: #e9ecef; /* Lighter background for secondary */
        color: #4a4a4a;
        border: 1px solid #ced4da;
    }
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        background-color: #d8dee2;
        transform: translateY(-2px);
    }

    .custom-notification {
        padding: 1rem 1.25rem; /* More padding */
        border-radius: 8px; /* Consistent border radius */
        margin-bottom: 1.5rem; /* More space below notification */
        border: 1px solid transparent;
        font-size: 1rem; /* Clearer font size */
        font-weight: 500;
    }
    .custom-notification.success {
        color: #0f5132; background-color: #d1e7dd; border-color: #badbcc;
    }
    .custom-notification.error {
        color: #842029; background-color: #f8d7da; border-color: #f5c2c7;
    }
    .custom-notification.warning {
        color: #664d03; background-color: #fff3cd; border-color: #ffecb5;
    }
    .custom-notification.info {
        color: #055160; background-color: #cff4fc; border-color: #b6effb;
    }

    .button-column-container {
        display: flex;
        gap: 1rem; /* Space between the check-in/out buttons */
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stColumn {
        display: flex;
        flex-direction: column;
        flex-grow: 1; /* Make columns grow evenly */
    }
    .stColumn > .stButton {
        flex-grow: 1; /* Make buttons fill available column width */
        width: 100%; /* Ensure button takes full width within its column */
    }
    .stDateInput, .stNumberInput, .stTextInput, .stTextArea, .stSelectbox, .stRadio {
        margin-bottom: 1.25rem; /* Consistent spacing for form elements */
    }
    .stForm > div > div {
        gap: 1.25rem; /* Adjust gap for form elements */
    }

    /* Adjust progress bar colors */
    .stProgress > div > div {
        background-color: #e9ecef; /* Lighter background for empty progress bar */
        border-radius: 5px;
    }
    .stProgress > div > div > div {
        background-color: #28a745; /* Green for progress fill */
        border-radius: 5px;
    }

    /* Style for Plotly charts */
    .stPlotlyChart {
        border-radius: 12px;
        overflow: hidden; /* Ensure chart elements respect border-radius */
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); /* Consistent shadow */
    }

    /* Streamlit labels */
    .st-emotion-cache-nahz7x p { /* This targets the common p tag Streamlit uses for labels */
        font-weight: 500;
        color: #555555;
        margin-bottom: 0.5rem;
    }
    /* Specific targeting for radio/checkbox labels if needed */
    .stRadio > label, .stCheckbox > label {
        font-weight: 500;
        color: #555555;
    }
    
    /* Small adjustments for layout */
    div[data-testid="stVerticalBlock"] > div:not(:last-child) {
        margin-bottom: 1.5rem; /* Add space between vertical blocks for better readability */
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
                # Changed background color to white (255, 255, 255)
                img = Image.new('RGB', (120, 120), color = (255, 255, 255)); draw = ImageDraw.Draw(img)
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
#-------------------------------------------------------------------------------------------------

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
                    if nc in df.columns: df[nc] = pd.to_numeric(df[nc], errors='coerce') # Coerce non-numeric to NaN
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
        # Clear the message after displaying
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
    current_username = st.session_state.auth.get("username")
    
    # Ensure current_username is not None before proceeding
    if current_username is None:
        st.error("User not logged in. Please log in to record attendance.")
        st.markdown('</div></div>', unsafe_allow_html=True)
        return

    common_data = {"Username": current_username, "Latitude": pd.NA, "Longitude": pd.NA}

    def process_general_attendance(attendance_type):
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a dictionary for the new entry, ensuring all ATTENDANCE_COLUMNS are present
        new_entry_data = {col: pd.NA for col in ATTENDANCE_COLUMNS}
        new_entry_data.update({
            "Type": attendance_type,
            "Timestamp": now_str_display,
            "Username": current_username,
            "Latitude": common_data["Latitude"],
            "Longitude": common_data["Longitude"]
        })

        new_entry_df = pd.DataFrame([new_entry_data])
        
        # Concatenate and save directly to session state dataframe
        # Use .copy() to prevent SettingWithCopyWarning if further modifications were made
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
    
    current_username = st.session_state.auth.get("username")
    if current_username is None:
        st.error("User not logged in. Please log in to upload activity photos.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
        
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
            image_filename_activity = f"{current_username}_activity_{now_for_filename}.jpg"
            image_path_activity = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_activity)
            try:
                with open(image_path_activity, "wb") as f:
                    f.write(img_file_buffer_activity.getbuffer())
                
                # Create a dictionary for the new entry, ensuring all ACTIVITY_LOG_COLUMNS are present
                new_activity_data = {col: pd.NA for col in ACTIVITY_LOG_COLUMNS}
                new_activity_data.update({
                    "Username": current_username,
                    "Timestamp": now_for_display,
                    "Description": activity_description,
                    "ImageFile": image_filename_activity,
                    "Latitude": current_lat,
                    "Longitude": current_lon
                })
                new_activity_entry_df = pd.DataFrame([new_activity_data])
                
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
    
    current_username = st.session_state.auth.get("username")
    if current_username is None:
        st.error("User not logged in. Please log in to claim allowances.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    a_type = st.radio("Allowance Type", ["Travel", "Dinner", "Medical", "Internet", "Other"],
                      key="allowance_type_radio_main", horizontal=True)
    amount = st.number_input("Enter Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_main")
    reason = st.text_area("Reason for Allowance:", key="allowance_reason_main", placeholder="Please provide a clear justification...")
    
    if st.button("Submit Allowance Request", key="submit_allowance_btn_main", use_container_width=True, type="primary"):
        if a_type and amount > 0 and reason.strip():
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            
            # Create a dictionary for the new entry, ensuring all ALLOWANCE_COLUMNS are present
            new_entry_data = {col: pd.NA for col in ALLOWANCE_COLUMNS}
            new_entry_data.update({
                "Username": current_username, "Type": a_type,
                "Amount": amount, "Reason": reason, "Date": date_str
            })
            new_entry_df = pd.DataFrame([new_entry_data])
            
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
    
    current_role = st.session_state.auth.get("role")
    current_username = st.session_state.auth.get("username")

    if current_role == "admin":
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
                        st.progress(min(row['Progress'] / 100, 1.0))
                        st.write(f"Target: ₹{row['Target']:,.0f} | Achieved: ₹{row['Achieved']:,.0f}")
                    with col2:
                        # Donut chart for individual progress
                        fig = create_donut_chart(row['Progress'], chart_title=f"{row['Username']} Progress")
                        st.pyplot(fig)
                
                # Team-wide progress chart
                st.markdown("---")
                st.markdown("<h5>Overall Team Performance Chart:</h5>", unsafe_allow_html=True)
                team_bar_chart_df = team_summary[["Username", "Target", "Achieved"]]
                fig_bar = create_team_progress_bar_chart(team_bar_chart_df, title=f"Team Sales Performance {current_quarter_for_display}", user_col="Username")
                if fig_bar:
                    st.pyplot(fig_bar)
                else:
                    st.info("No team data to display bar chart.")

                st.markdown("---")
                st.markdown("<h5>Detailed Quarterly Goals:</h5>", unsafe_allow_html=True)
                # Display all goals for the current quarter for admin
                display_df = quarterly_goals_df.copy()
                display_df['TargetAmount'] = display_df['TargetAmount'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                display_df['AchievedAmount'] = display_df['AchievedAmount'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                st.dataframe(display_df.style.set_properties(**{'font-size': '14px', 'text-align': 'left'}), use_container_width=True, hide_index=True)

            else:
                st.info(f"No sales goals set for {current_quarter_for_display} yet.")

        elif admin_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set or Update Quarterly Sales Goals for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            
            with st.form(key="set_goal_form"):
                target_user = st.selectbox("Select Employee:", [u for u in USERS.keys() if USERS[u]["role"] == "employee"], key="target_user_goal")
                goal_description = st.text_area("Goal Description:", placeholder="e.g., Achieve X sales, Y client meetings", key="goal_desc")
                target_amount = st.number_input("Target Amount (INR):", min_value=0.0, step=1000.0, format="%.2f", key="target_amt")
                achieved_amount = st.number_input("Achieved Amount (INR):", min_value=0.0, step=100.0, format="%.2f", key="achieved_amt")
                status = st.selectbox("Status:", status_options, key="goal_status")

                submit_goal = st.form_submit_button("💾 Save Sales Goal")

                if submit_goal:
                    if target_user and goal_description and target_amount >= 0 and achieved_amount >= 0 and status:
                        current_quarter = current_quarter_for_display # Already in correct format
                        
                        # Check if a similar goal exists for the user in this quarter
                        existing_goal_index = st.session_state.goals_df[
                            (st.session_state.goals_df["Username"] == target_user) &
                            (st.session_state.goals_df["MonthYear"] == current_quarter) &
                            (st.session_state.goals_df["GoalDescription"] == goal_description)
                        ].index
                        
                        new_goal_data = {
                            "Username": target_user,
                            "MonthYear": current_quarter,
                            "GoalDescription": goal_description,
                            "TargetAmount": target_amount,
                            "AchievedAmount": achieved_amount,
                            "Status": status
                        }
                        
                        if not existing_goal_index.empty:
                            # Update existing goal
                            st.session_state.goals_df.loc[existing_goal_index, new_goal_data.keys()] = list(new_goal_data.values())
                            st.session_state.user_message = f"Sales goal for {target_user} updated for {current_quarter}."
                            st.session_state.message_type = "info"
                        else:
                            # Add new goal
                            st.session_state.goals_df = pd.concat([st.session_state.goals_df, pd.DataFrame([new_goal_data])], ignore_index=True)
                            st.session_state.user_message = f"New sales goal added for {target_user} for {current_quarter}."
                            st.session_state.message_type = "success"
                        
                        try:
                            st.session_state.goals_df.to_csv(GOALS_FILE, index=False)
                        except Exception as e:
                            st.session_state.user_message = f"Error saving goals: {e}"
                            st.session_state.message_type = "error"
                        st.rerun()
                    else:
                        st.session_state.user_message = "Please fill all goal fields."
                        st.session_state.message_type = "warning"
                        st.rerun()

    else: # Employee view
        st.markdown(f"<h4>My Sales Goals for {TARGET_GOAL_YEAR}</h4>", unsafe_allow_html=True)
        my_goals_df = st.session_state.goals_df[st.session_state.goals_df["Username"] == current_username]
        
        if not my_goals_df.empty:
            # Display overall progress
            total_target = my_goals_df["TargetAmount"].sum()
            total_achieved = my_goals_df["AchievedAmount"].sum()
            overall_progress = (total_achieved / total_target * 100) if total_target > 0 else 0
            
            st.markdown(f"<h5>Overall Progress:</h5>", unsafe_allow_html=True)
            col_prog_val, col_prog_chart = st.columns([0.7, 0.3])
            with col_prog_val:
                st.progress(min(overall_progress / 100, 1.0))
                st.metric(label="Total Sales Goal Progress", value=f"{overall_progress:.1f}%")
                st.markdown(f"**Target:** ₹{total_target:,.0f} | **Achieved:** ₹{total_achieved:,.0f}", unsafe_allow_html=True)
            with col_prog_chart:
                fig = create_donut_chart(overall_progress, chart_title="My Sales Progress")
                st.pyplot(fig)
            
            st.markdown("---")
            st.markdown(f"<h5>My Quarterly Goals for {current_quarter_for_display}:</h5>", unsafe_allow_html=True)
            quarterly_my_goals_df = my_goals_df[my_goals_df["MonthYear"] == current_quarter_for_display]
            
            if not quarterly_my_goals_df.empty:
                # Display table of goals
                display_df = quarterly_my_goals_df.copy()
                display_df['TargetAmount'] = display_df['TargetAmount'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                display_df['AchievedAmount'] = display_df['AchievedAmount'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                
                st.dataframe(display_df[['GoalDescription', 'TargetAmount', 'AchievedAmount', 'Status']].style.set_properties(**{'font-size': '14px', 'text-align': 'left'}), use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown("<h5>Update Goal Progress:</h5>", unsafe_allow_html=True)
                with st.form(key="update_my_goal_form"):
                    goals_list = quarterly_my_goals_df["GoalDescription"].tolist()
                    selected_goal_desc = st.selectbox("Select Goal to Update:", goals_list, key="selected_goal_to_update")
                    
                    if selected_goal_desc:
                        current_goal_data = quarterly_my_goals_df[quarterly_my_goals_df["GoalDescription"] == selected_goal_desc].iloc[0]
                        updated_achieved_amount = st.number_input("New Achieved Amount (INR):", min_value=0.0, step=100.0, format="%.2f", 
                                                                  value=float(current_goal_data["AchievedAmount"]) if pd.notna(current_goal_data["AchievedAmount"]) else 0.0,
                                                                  key="updated_achieved_amt")
                        updated_status = st.selectbox("New Status:", status_options, index=status_options.index(current_goal_data["Status"]), key="updated_goal_status")
                        
                        update_goal_btn = st.form_submit_button("🔄 Update My Sales Goal")

                        if update_goal_btn:
                            goal_index = st.session_state.goals_df[
                                (st.session_state.goals_df["Username"] == current_username) &
                                (st.session_state.goals_df["MonthYear"] == current_quarter_for_display) &
                                (st.session_state.goals_df["GoalDescription"] == selected_goal_desc)
                            ].index
                            
                            if not goal_index.empty:
                                st.session_state.goals_df.loc[goal_index, "AchievedAmount"] = updated_achieved_amount
                                st.session_state.goals_df.loc[goal_index, "Status"] = updated_status
                                try:
                                    st.session_state.goals_df.to_csv(GOALS_FILE, index=False)
                                    st.session_state.user_message = f"Goal '{selected_goal_desc}' updated successfully."
                                    st.session_state.message_type = "success"
                                except Exception as e:
                                    st.session_state.user_message = f"Error saving goal update: {e}"
                                    st.session_state.message_type = "error"
                                st.rerun()
                            else:
                                st.session_state.user_message = "Selected goal not found for update."
                                st.session_state.message_type = "error"
                                st.rerun()
                    else:
                         st.info("Select a goal to update its progress.")
            else:
                st.info(f"No sales goals assigned to you for {current_quarter_for_display} yet.")
        else:
            st.info("You currently have no sales goals assigned.")
    st.markdown('</div>', unsafe_allow_html=True)


def payment_goals_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_PAYMENT_YEAR = 2025
    current_quarter_for_display = get_quarter_str_for_year(TARGET_PAYMENT_YEAR)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    
    current_role = st.session_state.auth.get("role")
    current_username = st.session_state.auth.get("username")

    if current_role == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Payment Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio("Action:", ["View Team Payment Progress", f"Set/Edit Payment Goal for {TARGET_PAYMENT_YEAR}"],
                                 key="admin_payment_action_radio_2025_q", horizontal=True)
        
        if admin_action == "View Team Payment Progress":
            st.markdown(f"<h5>Team Payment Goal Progress for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            quarterly_payment_goals_df = st.session_state.payment_goals_df[st.session_state.payment_goals_df["MonthYear"] == current_quarter_for_display]
            
            if not quarterly_payment_goals_df.empty:
                team_summary = quarterly_payment_goals_df.groupby("Username").agg(
                    Target=('TargetAmount', 'sum'),
                    Achieved=('AchievedAmount', 'sum')
                ).reset_index()
                
                team_summary['Progress'] = team_summary.apply(
                    lambda row: (row['Achieved'] / row['Target'] * 100) if row['Target'] > 0 else 0, axis=1
                )
                
                st.markdown("<h6>Individual Quarterly Payment Progress:</h6>", unsafe_allow_html=True)
                for index, row in team_summary.iterrows():
                    col1, col2 = st.columns([0.6, 0.4])
                    with col1:
                        st.markdown(f"**{row['Username']}**")
                        st.progress(min(row['Progress'] / 100, 1.0))
                        st.write(f"Target: ₹{row['Target']:,.0f} | Achieved: ₹{row['Achieved']:,.0f}")
                    with col2:
                        fig = create_donut_chart(row['Progress'], chart_title=f"{row['Username']} Progress")
                        st.pyplot(fig)
                
                st.markdown("---")
                st.markdown("<h5>Overall Team Payment Performance Chart:</h5>", unsafe_allow_html=True)
                team_bar_chart_df = team_summary[["Username", "Target", "Achieved"]]
                fig_bar = create_team_progress_bar_chart(team_bar_chart_df, title=f"Team Payment Performance {current_quarter_for_display}", user_col="Username")
                if fig_bar:
                    st.pyplot(fig_bar)
                else:
                    st.info("No team payment data to display bar chart.")

                st.markdown("---")
                st.markdown("<h5>Detailed Quarterly Payment Goals:</h5>", unsafe_allow_html=True)
                display_df = quarterly_payment_goals_df.copy()
                display_df['TargetAmount'] = display_df['TargetAmount'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                display_df['AchievedAmount'] = display_df['AchievedAmount'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                st.dataframe(display_df.style.set_properties(**{'font-size': '14px', 'text-align': 'left'}), use_container_width=True, hide_index=True)
            else:
                st.info(f"No payment goals set for {current_quarter_for_display} yet.")

        elif admin_action == f"Set/Edit Payment Goal for {TARGET_PAYMENT_YEAR}":
            st.markdown(f"<h5>Set or Update Quarterly Payment Goals for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            
            with st.form(key="set_payment_goal_form"):
                target_user = st.selectbox("Select Employee:", [u for u in USERS.keys() if USERS[u]["role"] == "employee"], key="target_user_payment_goal")
                goal_description = st.text_area("Goal Description:", placeholder="e.g., Collect X payments, Reduce Y outstanding", key="payment_goal_desc")
                target_amount = st.number_input("Target Amount (INR):", min_value=0.0, step=1000.0, format="%.2f", key="payment_target_amt")
                achieved_amount = st.number_input("Achieved Amount (INR):", min_value=0.0, step=100.0, format="%.2f", key="payment_achieved_amt")
                status = st.selectbox("Status:", status_options, key="payment_goal_status")

                submit_goal = st.form_submit_button("💾 Save Payment Goal")

                if submit_goal:
                    if target_user and goal_description and target_amount >= 0 and achieved_amount >= 0 and status:
                        current_quarter = current_quarter_for_display # Already in correct format
                        
                        existing_goal_index = st.session_state.payment_goals_df[
                            (st.session_state.payment_goals_df["Username"] == target_user) &
                            (st.session_state.payment_goals_df["MonthYear"] == current_quarter) &
                            (st.session_state.payment_goals_df["GoalDescription"] == goal_description)
                        ].index
                        
                        new_goal_data = {
                            "Username": target_user,
                            "MonthYear": current_quarter,
                            "GoalDescription": goal_description,
                            "TargetAmount": target_amount,
                            "AchievedAmount": achieved_amount,
                            "Status": status
                        }
                        
                        if not existing_goal_index.empty:
                            st.session_state.payment_goals_df.loc[existing_goal_index, new_goal_data.keys()] = list(new_goal_data.values())
                            st.session_state.user_message = f"Payment goal for {target_user} updated for {current_quarter}."
                            st.session_state.message_type = "info"
                        else:
                            st.session_state.payment_goals_df = pd.concat([st.session_state.payment_goals_df, pd.DataFrame([new_goal_data])], ignore_index=True)
                            st.session_state.user_message = f"New payment goal added for {target_user} for {current_quarter}."
                            st.session_state.message_type = "success"
                        
                        try:
                            st.session_state.payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                        except Exception as e:
                            st.session_state.user_message = f"Error saving payment goals: {e}"
                            st.session_state.message_type = "error"
                        st.rerun()
                    else:
                        st.session_state.user_message = "Please fill all payment goal fields."
                        st.session_state.message_type = "warning"
                        st.rerun()
    else: # Employee view
        st.markdown(f"<h4>My Payment Goals for {TARGET_PAYMENT_YEAR}</h4>", unsafe_allow_html=True)
        my_payment_goals_df = st.session_state.payment_goals_df[st.session_state.payment_goals_df["Username"] == current_username]
        
        if not my_payment_goals_df.empty:
            total_target = my_payment_goals_df["TargetAmount"].sum()
            total_achieved = my_payment_goals_df["AchievedAmount"].sum()
            overall_progress = (total_achieved / total_target * 100) if total_target > 0 else 0
            
            st.markdown(f"<h5>Overall Progress:</h5>", unsafe_allow_html=True)
            col_prog_val, col_prog_chart = st.columns([0.7, 0.3])
            with col_prog_val:
                st.progress(min(overall_progress / 100, 1.0))
                st.metric(label="Total Payment Goal Progress", value=f"{overall_progress:.1f}%")
                st.markdown(f"**Target:** ₹{total_target:,.0f} | **Achieved:** ₹{total_achieved:,.0f}", unsafe_allow_html=True)
            with col_prog_chart:
                fig = create_donut_chart(overall_progress, chart_title="My Payment Progress")
                st.pyplot(fig)
            
            st.markdown("---")
            st.markdown(f"<h5>My Quarterly Payment Goals for {current_quarter_for_display}:</h5>", unsafe_allow_html=True)
            quarterly_my_payment_goals_df = my_payment_goals_df[my_payment_goals_df["MonthYear"] == current_quarter_for_display]
            
            if not quarterly_my_payment_goals_df.empty:
                display_df = quarterly_my_payment_goals_df.copy()
                display_df['TargetAmount'] = display_df['TargetAmount'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                display_df['AchievedAmount'] = display_df['AchievedAmount'].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
                st.dataframe(display_df[['GoalDescription', 'TargetAmount', 'AchievedAmount', 'Status']].style.set_properties(**{'font-size': '14px', 'text-align': 'left'}), use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown("<h5>Update Payment Goal Progress:</h5>", unsafe_allow_html=True)
                with st.form(key="update_my_payment_goal_form"):
                    goals_list = quarterly_my_payment_goals_df["GoalDescription"].tolist()
                    selected_goal_desc = st.selectbox("Select Goal to Update:", goals_list, key="selected_payment_goal_to_update")
                    
                    if selected_goal_desc:
                        current_goal_data = quarterly_my_payment_goals_df[quarterly_my_payment_goals_df["GoalDescription"] == selected_goal_desc].iloc[0]
                        updated_achieved_amount = st.number_input("New Achieved Amount (INR):", min_value=0.0, step=100.0, format="%.2f", 
                                                                  value=float(current_goal_data["AchievedAmount"]) if pd.notna(current_goal_data["AchievedAmount"]) else 0.0,
                                                                  key="updated_payment_achieved_amt")
                        updated_status = st.selectbox("New Status:", status_options, index=status_options.index(current_goal_data["Status"]), key="updated_payment_goal_status")
                        
                        update_goal_btn = st.form_submit_button("🔄 Update My Payment Goal")

                        if update_goal_btn:
                            goal_index = st.session_state.payment_goals_df[
                                (st.session_state.payment_goals_df["Username"] == current_username) &
                                (st.session_state.payment_goals_df["MonthYear"] == current_quarter_for_display) &
                                (st.session_state.payment_goals_df["GoalDescription"] == selected_goal_desc)
                            ].index
                            
                            if not goal_index.empty:
                                st.session_state.payment_goals_df.loc[goal_index, "AchievedAmount"] = updated_achieved_amount
                                st.session_state.payment_goals_df.loc[goal_index, "Status"] = updated_status
                                try:
                                    st.session_state.payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                                    st.session_state.user_message = f"Payment goal '{selected_goal_desc}' updated successfully."
                                    st.session_state.message_type = "success"
                                except Exception as e:
                                    st.session_state.user_message = f"Error saving payment goal update: {e}"
                                    st.session_state.message_type = "error"
                                st.rerun()
                            else:
                                st.session_state.user_message = "Selected payment goal not found for update."
                                st.session_state.message_type = "error"
                                st.rerun()
                    else:
                        st.info("Select a payment goal to update its progress.")
            else:
                st.info(f"No payment goals assigned to you for {current_quarter_for_display} yet.")
        else:
            st.info("You currently have no payment goals assigned.")
    st.markdown('</div>', unsafe_allow_html=True)

def activity_log_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📋 Activity Log</h3>", unsafe_allow_html=True)
    
    current_role = st.session_state.auth.get("role")
    current_username = st.session_state.auth.get("username")

    df_display = st.session_state.activity_log_df.copy()
    
    if current_role == "admin":
        st.markdown("<h4>Admin: View All Employee Activities</h4>", unsafe_allow_html=True)
        # Filters for admin
        all_users = ["All"] + list(USERS.keys())
        selected_user = st.selectbox("Filter by Employee:", all_users, key="activity_log_user_filter")
        
        start_date = st.date_input("Start Date:", value=None, key="activity_log_start_date")
        end_date = st.date_input("End Date:", value=None, key="activity_log_end_date")

        if selected_user != "All":
            df_display = df_display[df_display["Username"] == selected_user]
        
        if start_date:
            df_display = df_display[pd.to_datetime(df_display["Timestamp"]).dt.date >= start_date]
        if end_date:
            df_display = df_display[pd.to_datetime(df_display["Timestamp"]).dt.date <= end_date]

    else: # Employee view
        st.markdown(f"<h4>My Recent Activities</h4>", unsafe_allow_html=True)
        df_display = df_display[df_display["Username"] == current_username]

        # Employee specific filter for recent activities (e.g., last 7 days)
        # You can add date filters here if desired, similar to admin.
        
    if df_display.empty:
        st.info("No activities to display for the selected filters.")
    else:
        # Convert Timestamp to datetime for sorting
        df_display["Timestamp"] = pd.to_datetime(df_display["Timestamp"])
        df_display = df_display.sort_values(by="Timestamp", ascending=False)
        
        for index, row in df_display.iterrows():
            st.markdown(f"<div class='card' style='padding:1rem; margin-bottom:1rem;'>", unsafe_allow_html=True)
            st.markdown(f"**Employee:** {row['Username']} | **Timestamp:** {row['Timestamp'].strftime('%Y-%m-%d %H:%M:%S')}", unsafe_allow_html=True)
            st.markdown(f"**Description:** {row['Description']}", unsafe_allow_html=True)
            
            image_file = row['ImageFile']
            image_path = os.path.join(ACTIVITY_PHOTOS_DIR, image_file)
            if image_file and os.path.exists(image_path):
                st.image(image_path, caption=f"Activity Photo ({row['Username']})", width=300)
            else:
                st.warning("Image not found.")
            st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# --- Authentication Functions ---
def login_page():
    st.image("path/to/your/company_logo.png", width=200) # Optional: Add your company logo
    st.markdown("<h2 style='text-align: center; color: #2c3e50;'>Employee Login</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", key="login_username_input", placeholder="Enter your username").strip()
        password = st.text_input("Password", type="password", key="login_password_input", placeholder="Enter your password").strip()
        login_button = st.form_submit_button("Login", type="primary", use_container_width=True)

        if login_button:
            if username in USERS and USERS[username]["password"] == password:
                st.session_state.auth["logged_in"] = True
                st.session_state.auth["username"] = username
                st.session_state.auth["role"] = USERS[username]["role"]
                st.session_state.user_message = "Login successful!"
                st.session_state.message_type = "success"
                st.rerun()
            else:
                st.session_state.user_message = "Invalid username or password."
                st.session_state.message_type = "error"
                st.rerun()

def logout():
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}
    st.session_state.user_message = "You have been logged out."
    st.session_state.message_type = "info"
    st.session_state.active_page = "Attendance" # Reset active page on logout
    st.rerun()

# --- Main Application Flow ---
if not st.session_state.auth["logged_in"]:
    login_page()
else:
    with st.sidebar:
        # Profile Section
        current_username = st.session_state.auth["username"]
        current_role = st.session_state.auth["role"]
        current_position = USERS[current_username]["position"]
        profile_photo_path = USERS[current_username]["profile_photo"]

        st.markdown(f"""
            <div class="user-profile-section">
                <img src="{profile_photo_path}" class="user-profile-img">
                <div class="welcome-text">Welcome, {current_username}!</div>
                <div class="user-position">{current_position}</div>
            </div>
            <div class="divider"></div>
        """, unsafe_allow_html=True)

        # Navigation Menu
        # Define navigation items
        nav_items_employee = [
            ("Attendance", "event_available"),
            ("Upload Activity Photo", "upload_file"),
            ("Claim Allowance", "payments"),
            ("Sales Goal Tracker", "track_changes"),
            ("Payment Goal Tracker", "paid"),
            ("Activity Log", "list_alt"),
        ]
        nav_items_admin = nav_items_employee # Admins can access all employee pages
        # You might want separate admin-only pages or add admin-specific tools here
        # Example: nav_items_admin.append(("Admin Dashboard", "admin_panel_settings"))

        nav_items = nav_items_admin if current_role == "admin" else nav_items_employee

        for page_name, icon_name in nav_items:
            # Check if this is the active page for styling
            is_active = "active-nav-item" if st.session_state.active_page == page_name else ""
            
            # Use a div to create the visual button, and an actual Streamlit button for functionality
            st.markdown(f"""
                <div class="sidebar-nav-item {is_active}">
                    <span class="material-symbols-outlined">{icon_name}</span> {page_name}
                </div>
            """, unsafe_allow_html=True)
            
            # Place the Streamlit button directly after the markdown.
            # This button will be invisible but clickable, and its click will update active_page
            if st.button(page_name, key=f"nav_btn_{page_name}", use_container_width=True):
                st.session_state.active_page = page_name
                st.rerun() # Rerun to switch content and apply active style

        # Logout Button (pushed to the bottom of the sidebar)
        st.markdown('<div class="logout-container">', unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn", use_container_width=True):
            logout()
        st.markdown('</div>', unsafe_allow_html=True)

    # Main Content Area
    st.markdown('<div class="main-content-area">', unsafe_allow_html=True)
    display_message() # Display messages at the top of the content area

    # Render content based on active page
    if st.session_state.active_page == "Attendance":
        attendance_page()
    elif st.session_state.active_page == "Upload Activity Photo":
        upload_activity_photo_page()
    elif st.session_state.active_page == "Claim Allowance":
        allowance_page()
    elif st.session_state.active_page == "Sales Goal Tracker":
        goal_tracker_page()
    elif st.session_state.active_page == "Payment Goal Tracker":
        payment_goals_page()
    elif st.session_state.active_page == "Activity Log":
        activity_log_page()
    
    # You can add an admin dashboard page here if you created one.
    # elif st.session_state.active_page == "Admin Dashboard":
    #     admin_dashboard_page()

    st.markdown('</div>', unsafe_allow_html=True)
