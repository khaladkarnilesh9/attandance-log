# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import pytz
import plotly.express as px
import plotly.graph_objects as go # For more custom Plotly charts if needed

# --- Matplotlib Configuration ---
import matplotlib
matplotlib.use('Agg') # Recommended for Streamlit
import matplotlib.pyplot as plt
import numpy as np

# --- Pillow for placeholder image generation ---
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False
    st.warning("Pillow library is not installed. Placeholder images for users might not be generated. Install with: pip install Pillow")

# --- Function to render Plotly Express grouped bar chart ---
def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty:
        st.warning(f"No data available to plot for {chart_title}.")
        return
    df_chart = df.copy()
    # Ensure 'TargetAmount' and 'AchievedAmount' are numeric, coercing errors and filling NaNs with 0
    df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear",
                              value_vars=["TargetAmount", "AchievedAmount"],
                              var_name="Metric",
                              value_name="Amount")
    if df_melted.empty or df_melted['Amount'].sum() == 0 : # Check if there's any actual data to plot
        st.info(f"No data to plot for {chart_title} after processing.")
        return
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group",
                 labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"},
                 title=chart_title,
                 color_discrete_map={'TargetAmount': '#3498db', 'AchievedAmount': '#2ecc71'})
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric')
    fig.update_xaxes(type='category') # Important for categorical data like "YYYY-Q#"
    st.plotly_chart(fig, use_container_width=True)

# --- Function to create Matplotlib Donut Chart ---
def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#2ecc71', remaining_color='#f0f0f0', center_text_color=None):
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=90) # Small, efficient size
    fig.patch.set_alpha(0) # Transparent background for the figure
    ax.patch.set_alpha(0)  # Transparent background for the axes

    # Ensure progress_percentage is a float and within 0-100
    try:
        progress_percentage = float(progress_percentage)
    except (ValueError, TypeError):
        progress_percentage = 0.0 # Default to 0 if conversion fails
    progress_percentage = max(0.0, min(progress_percentage, 100.0))

    remaining_percentage = 100.0 - progress_percentage

    if progress_percentage <= 0.01: # Handle near-zero progress
        sizes = [100.0]
        slice_colors = [remaining_color]
        actual_progress_display = 0.0
    elif progress_percentage >= 99.99: # Handle near-full progress
        sizes = [100.0]
        slice_colors = [achieved_color]
        actual_progress_display = 100.0
    else:
        sizes = [progress_percentage, remaining_percentage]
        slice_colors = [achieved_color, remaining_color]
        actual_progress_display = progress_percentage

    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.4, edgecolor='white'))
    centre_circle = plt.Circle((0,0),0.60,fc='white')
    fig.gca().add_artist(centre_circle)

    # Determine text color for the center
    text_color_to_use = center_text_color if center_text_color else (achieved_color if actual_progress_display > 0 else '#4A4A4A')

    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=12, fontweight='bold', color=text_color_to_use)
    ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0) # Remove extra whitespace
    return fig

# --- Function to create Matplotlib Grouped Bar Chart for Team Progress ---
def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee"):
    if summary_df.empty:
        # st.info(f"No data to plot for {title}.") # Info message handled by caller
        return None

    labels = summary_df[user_col].tolist()
    target_amounts = summary_df[target_col].fillna(0).tolist() # Ensure NaNs are 0
    achieved_amounts = summary_df[achieved_col].fillna(0).tolist() # Ensure NaNs are 0

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.8), 5), dpi=100)
    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color='#3498db', alpha=0.8)
    rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color='#2ecc71', alpha=0.8)

    ax.set_ylabel('Amount (INR)', fontsize=10)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)
    ax.legend(fontsize=9)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7) # Add a light grid for readability

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            if height > 0: # Only label if height is positive
                ax.annotate(f'{height:,.0f}', # Format as integer with comma
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=7, color='#333')
    autolabel(rects1)
    autolabel(rects2)
    fig.tight_layout(pad=1.5) # Adjust layout to prevent labels from overlapping
    return fig


html_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    :root {
        --primary-color: #1c4e80; --secondary-color: #2070c0; --accent-color: #70a1d7;
        --success-color: #28a745; --danger-color: #dc3545; --warning-color: #ffc107; --info-color: #17a2b8;
        --body-bg-color: #f4f6f9; --card-bg-color: #ffffff; --text-color: #343a40; --text-muted-color: #6c757d;
        --border-color: #dee2e6; --input-border-color: #ced4da;
        --font-family-sans-serif: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
        --border-radius: 0.375rem; --border-radius-lg: 0.5rem;
        --box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.075); --box-shadow-sm: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }
    body {font-family: var(--font-family-sans-serif); background-color: var(--body-bg-color); color: var(--text-color); line-height: 1.6; font-weight: 400;}
    h1, h2, h3, h4, h5, h6 {color: var(--primary-color); font-weight: 600;}
    .main .block-container > div:first-child > div:first-child > div:first-child > h1 {text-align: center; font-size: 2.6em; font-weight: 700; padding-bottom: 25px; border-bottom: 3px solid var(--accent-color); margin-bottom: 40px; letter-spacing: -0.5px;}
    .card {background-color: var(--card-bg-color); padding: 30px; border-radius: var(--border-radius-lg); box-shadow: var(--box-shadow); margin-bottom: 35px; border: 1px solid var(--border-color);}
    .card h3 {margin-top: 0; color: var(--primary-color); border-bottom: 2px solid #e9ecef; padding-bottom: 15px; margin-bottom: 25px; font-size: 1.75em;}
    .card h4 {color: var(--secondary-color); margin-top: 30px; margin-bottom: 20px; font-size: 1.4em; padding-bottom: 8px; border-bottom: 1px solid #e0e0e0;}
    .card h5 {font-size: 1.15em; color: var(--text-color); margin-top: 25px; margin-bottom: 12px;}
    .card h6 {font-size: 0.95em; color: var(--text-muted-color); margin-top: 0px; margin-bottom: 15px; font-weight: 500;}
    .form-field-label h6 {font-size: 1em; color: var(--text-muted-color); margin-top: 20px; margin-bottom: 10px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px;}
    .login-container {max-width: 480px; margin: 60px auto; border-top: 5px solid var(--secondary-color);}
    .login-container .stButton button {width: 100%; background-color: var(--secondary-color) !important; color: white !important; font-size: 1.1em; padding: 12px 20px; border-radius: var(--border-radius); border: none !important; font-weight: 600 !important; box-shadow: var(--box-shadow-sm) !important;}
    .login-container .stButton button:hover {background-color: var(--primary-color) !important; color: white !important; box-shadow: var(--box-shadow) !important;}
    .stButton:not(.login-container .stButton) button {background-color: var(--success-color); color: white; padding: 10px 24px; border: none; border-radius: var(--border-radius); font-size: 1.05em; font-weight: 500; transition: background-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease; box-shadow: var(--box-shadow-sm); cursor: pointer;}
    .stButton:not(.login-container .stButton) button:hover {background-color: #218838; transform: translateY(-2px); box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);}
    .stButton:not(.login-container .stButton) button:active {transform: translateY(0px); box-shadow: var(--box-shadow-sm);}
    .stButton button[id*="logout_button_sidebar"] {background-color: var(--danger-color) !important; border: 1px solid var(--danger-color) !important; color: white !important; font-weight: 500 !important;}
    .stButton button[id*="logout_button_sidebar"]:hover {background-color: #c82333 !important; border-color: #c82333 !important;}
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] > div {border-radius: var(--border-radius) !important; border: 1px solid var(--input-border-color) !important; padding: 10px 12px !important; font-size: 1em !important; color: var(--text-color) !important; background-color: var(--card-bg-color) !important; transition: border-color 0.2s ease, box-shadow 0.2s ease;}
    .stTextInput input::placeholder, .stNumberInput input::placeholder, .stTextArea textarea::placeholder {color: var(--text-muted-color) !important; opacity: 1;}
    .stTextArea textarea {min-height: 120px;}
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus, .stDateInput input:focus, .stTimeInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within {border-color: var(--secondary-color) !important; box-shadow: 0 0 0 0.2rem rgba(32, 112, 192, 0.25) !important;}
    [data-testid="stSidebar"] {background-color: var(--primary-color); padding: 25px !important; box-shadow: 0.25rem 0 1rem rgba(0,0,0,0.1);}
    [data-testid="stSidebar"] .sidebar-content {padding-top: 10px;}
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] div:not([data-testid="stRadio"]) {color: #e9ecef !important;}
    [data-testid="stSidebar"] .stRadio > label > div > p {font-size: 1.05em !important; color: var(--accent-color) !important; padding: 0; margin: 0;}
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label > div > p {color: var(--card-bg-color) !important; font-weight: 600;}
    [data-testid="stSidebar"] .stRadio > label {padding: 10px 15px; border-radius: var(--border-radius); margin-bottom: 6px; transition: background-color 0.2s ease;}
    [data-testid="stSidebar"] .stRadio > label:hover {background-color: rgba(255, 255, 255, 0.08);}
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label {background-color: rgba(255, 255, 255, 0.15);}
    .welcome-text {font-size: 1.4em; font-weight: 600; margin-bottom: 25px; text-align: center; color: var(--card-bg-color) !important; border-bottom: 1px solid var(--accent-color); padding-bottom: 20px;}
    [data-testid="stSidebar"] [data-testid="stImage"] > img {border-radius: 50%; border: 3px solid var(--accent-color); margin: 0 auto 10px auto; display: block;}
    .stDataFrame {width: 100%; border: 1px solid var(--border-color); border-radius: var(--border-radius-lg); overflow: hidden; box-shadow: var(--box-shadow-sm); margin-bottom: 25px;}
    .stDataFrame table {width: 100%; border-collapse: collapse;}
    .stDataFrame table thead th {background-color: #e9ecef; color: var(--primary-color); font-weight: 600; text-align: left; padding: 14px 18px; border-bottom: 2px solid var(--border-color); font-size: 0.9em; text-transform: uppercase; letter-spacing: 0.5px;}
    .stDataFrame table tbody td {padding: 12px 18px; border-bottom: 1px solid #f1f3f5; vertical-align: middle; color: var(--text-color); font-size: 0.9em;}
    .stDataFrame table tbody tr:last-child td {border-bottom: none;}
    .stDataFrame table tbody tr:hover {background-color: #f8f9fa;}
    .employee-progress-item {border: 1px solid var(--border-color); border-radius: var(--border-radius); padding: 15px; text-align: center; background-color: #fdfdfd; margin-bottom: 10px;}
    .employee-progress-item h6 {margin-top: 0; margin-bottom: 5px; font-size: 1em; color: var(--primary-color);}
    .employee-progress-item p {font-size: 0.85em; color: var(--text-muted-color); margin-bottom: 8px;}
    .button-column-container > div[data-testid="stHorizontalBlock"] {gap: 20px;}
    .button-column-container .stButton button {width: 100%;}
    div[role="radiogroup"] {display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 25px;}
    div[role="radiogroup"] > label {background-color: #f0f2f5; color: var(--text-color); padding: 10px 18px; border-radius: var(--border-radius); border: 1px solid var(--input-border-color); cursor: pointer; transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease; font-size: 0.95em; font-weight: 500;}
    div[role="radiogroup"] > label:hover {background-color: #e9ecef; border-color: #adb5bd;}
    div[role="radiogroup"] div[data-baseweb="radio"][aria-checked="true"] + label {background-color: var(--secondary-color) !important; color: white !important; border-color: var(--secondary-color) !important; font-weight: 500;}
    .employee-section-header {color: var(--secondary-color); margin-top: 30px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; font-size: 1.35em;}
    .record-type-header {font-size: 1.2em; color: var(--text-color); margin-top: 25px; margin-bottom: 12px; font-weight: 600;}
    div[data-testid="stImage"] > img {border-radius: var(--border-radius-lg); border: 1px solid var(--border-color); box-shadow: var(--box-shadow-sm);}
    .stProgress > div > div {background-color: var(--secondary-color) !important; border-radius: var(--border-radius);}
    .stProgress {border-radius: var(--border-radius); background-color: #e9ecef;}
    div[data-testid="stMetricLabel"] {font-size: 0.95em !important; color: var(--text-muted-color) !important; font-weight: 500;}
    div[data-testid="stMetricValue"] {font-size: 1.8em !important; font-weight: 600; color: var(--primary-color);}
    .custom-notification {padding: 15px 20px; border-radius: var(--border-radius); margin-bottom: 20px; font-size: 1em; border-left-width: 5px; border-left-style: solid; display: flex; align-items: center;}
    .custom-notification.success {background-color: #d1e7dd; color: #0f5132; border-left-color: var(--success-color);}
    .custom-notification.error {background-color: #f8d7da; color: #842029; border-left-color: var(--danger-color);}
    .custom-notification.warning {background-color: #fff3cd; color: #664d03; border-left-color: var(--warning-color);}
    .custom-notification.info {background-color: #cff4fc; color: #055160; border-left-color: var(--info-color);}
    .badge {display: inline-block; padding: 0.35em 0.65em; font-size: 0.85em; font-weight: 600; line-height: 1; color: #fff; text-align: center; white-space: nowrap; vertical-align: baseline; border-radius: var(--border-radius);}
    .badge.green {background-color: var(--success-color);}
    .badge.red {background-color: var(--danger-color);}
    .badge.orange {background-color: var(--warning-color);}
    .badge.blue {background-color: var(--secondary-color);}
    .badge.grey {background-color: var(--text-muted-color);}
</style>
"""
st.set_page_config(layout="wide", page_title="TrackSphere") # Set wide layout and page title
st.markdown(html_css, unsafe_allow_html=True)

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
    except OSError as e: st.warning(f"Could not create images directory: {e}")
if PILLOW_INSTALLED:
    for user_key, user_data in USERS.items():
        img_path = user_data.get("profile_photo")
        if img_path and not os.path.exists(img_path):
            try:
                img = Image.new('RGB', (120, 120), color = (200, 220, 240)); draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", 40) # Try to load a common font
                except IOError: font = ImageFont.load_default() # Fallback
                text = user_key[:2].upper() # Use first two initials

                # Get text bounding box to center it properly
                if hasattr(draw, 'textbbox'): # More modern PIL/Pillow
                    bbox = draw.textbbox((0,0), text, font=font)
                    text_width, text_height = bbox[2]-bbox[0], bbox[3]-bbox[1]
                    text_x, text_y = (120-text_width)/2, (120-text_height)/2 - bbox[1] # Adjust y based on bbox[1]
                elif hasattr(draw, 'textsize'): # Older PIL/Pillow
                    text_width, text_height = draw.textsize(text, font=font)
                    text_x, text_y = (120-text_width)/2, (120-text_height)/2
                else: # Fallback if textsize and textbbox not available
                    text_x, text_y = 30,30 # Approximate center

                draw.text((text_x, text_y), text, fill=(28,78,128), font=font)
                img.save(img_path)
            except Exception as e: st.warning(f"Could not create placeholder image for {user_key}: {e}")
# else: if not PILLOW_INSTALLED, a warning is already shown.

# --- File Paths & Timezone & Directories ---
ATTENDANCE_FILE = "attendance.csv"; ALLOWANCE_FILE = "allowances.csv"; GOALS_FILE = "goals.csv"; PAYMENT_GOALS_FILE = "payment_goals.csv"
ACTIVITY_LOG_FILE = "activity_log.csv"
ACTIVITY_PHOTOS_DIR = "activity_photos"
# ATTENDANCE_PHOTOS_DIR is not used anymore since attendance doesn't take photos directly.

if not os.path.exists(ACTIVITY_PHOTOS_DIR):
    try: os.makedirs(ACTIVITY_PHOTOS_DIR)
    except OSError as e: st.warning(f"Could not create {ACTIVITY_PHOTOS_DIR}: {e}")

TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError: st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'. Application cannot proceed correctly."); st.stop()

def get_current_time_in_tz(): return datetime.now(timezone.utc).astimezone(tz)

def get_quarter_str_for_year(year, for_current_display=False): # Parameter for_current_display not used.
    now_month = get_current_time_in_tz().month # Use current month to determine current quarter
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
                # Ensure all expected columns exist, add if missing
                for col in columns:
                    if col not in df.columns: df[col] = pd.NA # Use pd.NA for proper handling of missing values
                # Convert specific columns to numeric, coercing errors
                num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude"]
                for nc in num_cols:
                    if nc in df.columns: df[nc] = pd.to_numeric(df[nc], errors='coerce') # NaNs will be handled later or by fillna(0)
                return df
            else: return pd.DataFrame(columns=columns) # File exists but is empty
        except pd.errors.EmptyDataError: return pd.DataFrame(columns=columns) # Explicitly handle EmptyDataError
        except Exception as e: st.error(f"Error loading {path}: {e}. Returning empty DataFrame."); return pd.DataFrame(columns=columns)
    else:
        # File does not exist, create it with headers
        df = pd.DataFrame(columns=columns)
        try: df.to_csv(path, index=False)
        except Exception as e: st.warning(f"Could not create {path}: {e}") # Warn if creation fails
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]

# --- Load DataFrames globally ---
attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
activity_log_df = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS)


# --- Session State & Login ---
if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}

if not st.session_state.auth["logged_in"]:
    st.title("TrackSphere Login")
    message_placeholder_login = st.empty()
    if st.session_state.user_message:
        message_placeholder_login.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
        st.session_state.user_message = None; st.session_state.message_type = None

    st.markdown('<div class="login-container card">', unsafe_allow_html=True)
    st.markdown("<h3>🔐 Login</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname")
    pwd = st.text_input("Password", type="password", key="login_pwd")
    if st.button("Login", key="login_button"):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = "Login successful!"
            st.session_state.message_type = "success"
            st.rerun()
        else:
            st.error("Invalid username or password.") # This error displays directly
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # Stop execution if not logged in

# --- Main Application ---
current_user = st.session_state.auth # User is authenticated at this point

# --- Global Message Display for Main Application (after login) ---
message_placeholder_main = st.empty()
if "user_message" in st.session_state and st.session_state.user_message:
    message_type_main = st.session_state.get("message_type", "info") # Default to info
    message_placeholder_main.markdown(
        f"<div class='custom-notification {message_type_main}'>{st.session_state.user_message}</div>",
        unsafe_allow_html=True
    )
    # Clear the message after displaying it so it doesn't reappear on next interaction without a new message
    st.session_state.user_message = None
    st.session_state.message_type = None


with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user['username']}!</div>", unsafe_allow_html=True)

    nav_options = [
        "📊 Dashboard",
        "📆 Attendance",
        "📸 Upload Activity Photo",
        "🧾 Allowance",
        "🎯 Goal Tracker",
        "💰 Payment Collection Tracker",
        "📊 View Logs"
    ]
    nav = st.radio("Navigation", nav_options, key="sidebar_nav_main")

    user_sidebar_info = USERS.get(current_user["username"], {})
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]):
        st.image(user_sidebar_info["profile_photo"], width=100)
    elif PILLOW_INSTALLED: # If PILLOW is installed but image specific path doesn't exist (should have been created)
        st.caption("Profile photo not found.")
    # No message if PILLOW is not installed, as a general warning was already given.

    st.markdown(
        f"<p style='text-align:center; font-size:0.9em; color: #e0e0e0;'>{user_sidebar_info.get('position', 'N/A')}</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    if st.button("🔒 Logout", key="logout_button_sidebar", use_container_width=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."
        st.session_state.message_type = "info"
        st.rerun()

# --- Main Content Area ---
if nav == "📊 Dashboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 Performance Dashboard</h3>", unsafe_allow_html=True)

    # --- Helper functions for dashboard metrics (local to this block) ---
    def get_check_ins_today(df_att):
        today_date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
        df_att_copy = df_att.copy() # Work on a copy
        df_att_copy['Timestamp_dt'] = pd.to_datetime(df_att_copy['Timestamp'], errors='coerce')
        return df_att_copy[df_att_copy['Timestamp_dt'].dt.strftime("%Y-%m-%d") == today_date_str].shape[0]

    def get_active_users_today(df_att):
        today_date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
        df_att_copy = df_att.copy()
        df_att_copy['Timestamp_dt'] = pd.to_datetime(df_att_copy['Timestamp'], errors='coerce')
        return df_att_copy[df_att_copy['Timestamp_dt'].dt.strftime("%Y-%m-%d") == today_date_str]['Username'].nunique()

    def get_overall_goal_progress(df_goals, current_quarter_str):
        quarter_goals_df = df_goals[df_goals["MonthYear"] == current_quarter_str].copy()
        if quarter_goals_df.empty:
            return 0, 0, 0
        quarter_goals_df["TargetAmount"] = pd.to_numeric(quarter_goals_df["TargetAmount"], errors='coerce').fillna(0)
        quarter_goals_df["AchievedAmount"] = pd.to_numeric(quarter_goals_df["AchievedAmount"], errors='coerce').fillna(0)
        total_target = quarter_goals_df["TargetAmount"].sum()
        total_achieved = quarter_goals_df["AchievedAmount"].sum()
        progress_percent = (total_achieved / total_target * 100) if total_target > 0 else 0
        return total_target, total_achieved, progress_percent

    def get_allowances_this_month(df_allow):
        current_month_year_str = get_current_time_in_tz().strftime("%Y-%m")
        df_allow_copy = df_allow.copy()
        df_allow_copy['Date_dt'] = pd.to_datetime(df_allow_copy['Date'], errors='coerce')
        month_allowances_df = df_allow_copy[df_allow_copy['Date_dt'].dt.strftime("%Y-%m") == current_month_year_str].copy()
        month_allowances_df["Amount"] = pd.to_numeric(month_allowances_df["Amount"], errors='coerce').fillna(0)
        return month_allowances_df["Amount"].sum(), month_allowances_df.shape[0]

    TARGET_YEAR_DASH = 2025 # Consistent target year for dashboard overview
    current_quarter_dashboard = get_quarter_str_for_year(TARGET_YEAR_DASH)

    if current_user["role"] == "admin":
        st.markdown("<h4>🚀 Admin Overview</h4>", unsafe_allow_html=True)
        st.markdown(f"<h6>Key Metrics for {current_quarter_dashboard} & Today</h6>", unsafe_allow_html=True)

        num_employees = len([u for u, data in USERS.items() if data["role"] == "employee"])
        check_ins_today_count = get_check_ins_today(attendance_df)
        active_users_today_count = get_active_users_today(attendance_df)
        sales_target, sales_achieved, sales_progress = get_overall_goal_progress(goals_df, current_quarter_dashboard)
        payment_target, payment_achieved, payment_progress = get_overall_goal_progress(payment_goals_df, current_quarter_dashboard)
        allowance_sum_month, allowance_count_month = get_allowances_this_month(allowance_df)

        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric(label="👥 Total Employees", value=num_employees)
            st.metric(label="✅ Check-ins Today", value=f"{check_ins_today_count}")
        with kpi2:
            st.metric(label=f"🎯 Sales Progress ({current_quarter_dashboard})", value=f"{sales_progress:.1f}%",
                      delta=f"₹{sales_achieved:,.0f} / ₹{sales_target:,.0f}", delta_color="off")
            st.metric(label=f"💰 Collection Progress ({current_quarter_dashboard})", value=f"{payment_progress:.1f}%",
                      delta=f"₹{payment_achieved:,.0f} / ₹{payment_target:,.0f}", delta_color="off")
        with kpi3:
            st.metric(label="🚶 Active Users Today", value=f"{active_users_today_count}")
            st.metric(label="💸 Allowances This Month", value=f"₹{allowance_sum_month:,.0f}",
                      delta=f"{allowance_count_month} claims", delta_color="off")
        st.markdown("---")
        st.markdown(f"<h4>📊 Team Performance Details ({current_quarter_dashboard})</h4>", unsafe_allow_html=True)

        employee_users_dash = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
        summary_list_sales_dash = []
        for emp_name in employee_users_dash:
            emp_current_goal = goals_df[(goals_df["Username"] == emp_name) & (goals_df["MonthYear"] == current_quarter_dashboard)]
            target, achieved = 0.0, 0.0
            if not emp_current_goal.empty:
                g_data = emp_current_goal.iloc[0]
                target = float(pd.to_numeric(g_data.get("TargetAmount"), errors='coerce').fillna(0.0))
                achieved = float(pd.to_numeric(g_data.get("AchievedAmount"), errors='coerce').fillna(0.0))
            summary_list_sales_dash.append({"Employee": emp_name, "Target": target, "Achieved": achieved})
        summary_df_sales_dash = pd.DataFrame(summary_list_sales_dash)
        if not summary_df_sales_dash.empty:
            team_sales_bar_fig_dash = create_team_progress_bar_chart(summary_df_sales_dash, title="Team Sales Performance", target_col="Target", achieved_col="Achieved")
            if team_sales_bar_fig_dash: st.pyplot(team_sales_bar_fig_dash, use_container_width=True)
            else: st.info("No sales data to plot team bar chart.")
        else: st.info("No sales goals data for team progress.")

        summary_list_payment_dash = []
        for emp_name in employee_users_dash:
            emp_current_payment_goal = payment_goals_df[(payment_goals_df["Username"] == emp_name) & (payment_goals_df["MonthYear"] == current_quarter_dashboard)]
            target_p, achieved_p = 0.0, 0.0
            if not emp_current_payment_goal.empty:
                pg_data = emp_current_payment_goal.iloc[0]
                target_p = float(pd.to_numeric(pg_data.get("TargetAmount"), errors='coerce').fillna(0.0))
                achieved_p = float(pd.to_numeric(pg_data.get("AchievedAmount"), errors='coerce').fillna(0.0))
            summary_list_payment_dash.append({"Employee": emp_name, "Target": target_p, "Achieved": achieved_p})
        summary_df_payment_dash = pd.DataFrame(summary_list_payment_dash)
        if not summary_df_payment_dash.empty:
            team_payment_bar_fig_dash = create_team_progress_bar_chart(summary_df_payment_dash, title="Team Payment Collection Performance")
            if team_payment_bar_fig_dash:
                for bar_group in team_payment_bar_fig_dash.axes[0].containers:
                    if bar_group.get_label()=='Achieved': # Ensure label matches
                        for bar_item in bar_group: bar_item.set_color('#2070c0') # Payment achieved color
                st.pyplot(team_payment_bar_fig_dash, use_container_width=True)
            else: st.info("No collection data to plot team bar chart.")
        else: st.info("No payment collection data for team progress.")

        st.markdown("---")
        st.markdown("<h4>📋 Recent Activity Logs (Last 5)</h4>", unsafe_allow_html=True)
        if not activity_log_df.empty:
            activity_log_df_sorted_dash = activity_log_df.copy()
            activity_log_df_sorted_dash['Timestamp_dt'] = pd.to_datetime(activity_log_df_sorted_dash['Timestamp'], errors='coerce')
            activity_log_df_sorted_dash = activity_log_df_sorted_dash.sort_values(by="Timestamp_dt", ascending=False)
            recent_activities = activity_log_df_sorted_dash.head(5)[["Username", "Timestamp", "Description"]]
            st.dataframe(recent_activities, use_container_width=True, hide_index=True)
        else: st.info("No activity logs recorded yet.")
    else: # Employee Dashboard View
        st.markdown("<h4>🎯 My Performance Snapshot</h4>", unsafe_allow_html=True)
        st.markdown(f"<h6>Key Metrics for {current_quarter_dashboard}</h6>", unsafe_allow_html=True)
        my_sales_goals = goals_df[goals_df["Username"] == current_user["username"]].copy()
        my_sales_goals[["TargetAmount", "AchievedAmount"]] = my_sales_goals[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        current_sales_goal_df = my_sales_goals[my_sales_goals["MonthYear"] == current_quarter_dashboard]
        sales_target_emp, sales_achieved_emp, sales_status_emp = 0.0, 0.0, "Not Set"
        if not current_sales_goal_df.empty:
            sg = current_sales_goal_df.iloc[0]; sales_target_emp = sg["TargetAmount"]; sales_achieved_emp = sg["AchievedAmount"]; sales_status_emp = sg.get("Status", "In Progress")

        my_payment_goals = payment_goals_df[payment_goals_df["Username"] == current_user["username"]].copy()
        my_payment_goals[["TargetAmount", "AchievedAmount"]] = my_payment_goals[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        current_payment_goal_df = my_payment_goals[my_payment_goals["MonthYear"] == current_quarter_dashboard]
        payment_target_emp, payment_achieved_emp, payment_status_emp = 0.0, 0.0, "Not Set"
        if not current_payment_goal_df.empty:
            pg = current_payment_goal_df.iloc[0]; payment_target_emp = pg["TargetAmount"]; payment_achieved_emp = pg["AchievedAmount"]; payment_status_emp = pg.get("Status", "In Progress")

        my_attendance = attendance_df[attendance_df["Username"] == current_user["username"]].copy()
        last_check_in_time_str = "N/A"
        if not my_attendance.empty:
            my_attendance['Timestamp_dt'] = pd.to_datetime(my_attendance['Timestamp'], errors='coerce')
            my_attendance_sorted = my_attendance.sort_values(by="Timestamp_dt", ascending=False) # Sort before taking iloc[0]
            if not my_attendance_sorted.empty and pd.notna(my_attendance_sorted.iloc[0]["Timestamp_dt"]):
                 last_check_in_time_str = my_attendance_sorted.iloc[0]["Timestamp_dt"].strftime("%Y-%m-%d %H:%M")

        emp_kpi1, emp_kpi2 = st.columns(2)
        with emp_kpi1:
            st.metric(label="My Sales Target", value=f"₹{sales_target_emp:,.0f}")
            st.metric(label="My Sales Achieved", value=f"₹{sales_achieved_emp:,.0f}")
            st.markdown(f"**Sales Status:** <span class='badge blue'>{sales_status_emp}</span>", unsafe_allow_html=True)
        with emp_kpi2:
            st.metric(label="My Collection Target", value=f"₹{payment_target_emp:,.0f}")
            st.metric(label="My Collection Achieved", value=f"₹{payment_achieved_emp:,.0f}")
            st.markdown(f"**Collection Status:** <span class='badge blue'>{payment_status_emp}</span>", unsafe_allow_html=True)
        st.metric(label="My Last Activity Time", value=last_check_in_time_str, help="Based on general attendance or activity log.")
        st.markdown("---")
        st.markdown("<h5>My Goal Progress Visualized:</h5>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("<h6 style='text-align:center;'>Sales Progress</h6>", unsafe_allow_html=True)
            sales_progress_percent_emp = (sales_achieved_emp / sales_target_emp * 100) if sales_target_emp > 0 else 0
            sales_donut_fig_emp = create_donut_chart(sales_progress_percent_emp, achieved_color='#28a745')
            if sales_donut_fig_emp: st.pyplot(sales_donut_fig_emp, use_container_width=True)
        with chart_col2:
            st.markdown("<h6 style='text-align:center;'>Collection Progress</h6>", unsafe_allow_html=True)
            payment_progress_percent_emp = (payment_achieved_emp / payment_target_emp * 100) if payment_target_emp > 0 else 0
            payment_donut_fig_emp = create_donut_chart(payment_progress_percent_emp, achieved_color='#2070c0')
            if payment_donut_fig_emp: st.pyplot(payment_donut_fig_emp, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True) # Close main card for Dashboard

elif nav == "📆 Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled for general attendance. Photos for specific field activities can be uploaded from the 'Upload Activity Photo' section.", icon="ℹ️")
    st.markdown("---"); st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2); common_data = {"Username": current_user["username"], "Latitude": pd.NA, "Longitude": pd.NA}

    def process_general_attendance(attendance_type):
        global attendance_df # Ensure we intend to modify the global df (though direct concat and save is better)
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_data = {"Type": attendance_type, "Timestamp": now_str_display, **common_data}
        # Ensure all columns are present as per ATTENDANCE_COLUMNS definition
        for col_name in ATTENDANCE_COLUMNS:
            if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
        new_entry = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)

        # It's generally better to use st.rerun() and let data reload at the top.
        # However, for immediate feedback and to keep changes minimal to original logic:
        temp_attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        try:
            temp_attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            # Update the global DataFrame in memory for the current session run, though it will be reloaded on rerun
            attendance_df = temp_attendance_df
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."; st.session_state.message_type = "success"; st.rerun()
        except Exception as e: st.session_state.user_message = f"Error saving attendance: {e}"; st.session_state.message_type = "error"; st.rerun()

    with col1:
        if st.button("✅ Check In", key="check_in_btn_main_no_photo", use_container_width=True):
            process_general_attendance("Check-In")
    with col2:
        if st.button("🚪 Check Out", key="check_out_btn_main_no_photo", use_container_width=True):
            process_general_attendance("Check-Out")
    st.markdown('</div></div>', unsafe_allow_html=True) # Original had </div></div>

elif nav == "📸 Upload Activity Photo":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat, current_lon = pd.NA, pd.NA # Location capture not implemented here
    with st.form(key="activity_photo_form"):
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description of activity/visit:", key="activity_desc", help="E.g., Met with Client X at their office regarding Project Y.")
        img_file_buffer_activity = st.camera_input("Take a picture of your activity/visit", key="activity_camera_input")
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo and Log Activity")

elif nav == "📸 Upload Activity Photo":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat, current_lon = pd.NA, pd.NA # Location capture not implemented here
    with st.form(key="activity_photo_form"):
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description of activity/visit:", key="activity_desc", help="E.g., Met with Client X at their office regarding Project Y.")
        img_file_buffer_activity = st.camera_input("Take a picture of your activity/visit", key="activity_camera_input")
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo and Log Activity")

    if submit_activity_photo:
        if img_file_buffer_activity is None:
            st.warning("Please take a picture before submitting.")
        elif not activity_description.strip():
            st.warning("Please provide a description for the activity.")
        else:
            # ***** CORRECTED PLACEMENT OF GLOBAL DECLARATION *****
            global activity_log_df # Declare global at the start of this block

            now_for_filename = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S")
            now_for_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            image_filename_activity = f"{current_user['username']}_activity_{now_for_filename}.jpg"
            image_path_activity = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_activity)
            try:
                with open(image_path_activity, "wb") as f: f.write(img_file_buffer_activity.getbuffer())
                new_activity_data = {"Username": current_user["username"], "Timestamp": now_for_display, "Description": activity_description, "ImageFile": image_filename_activity, "Latitude": current_lat, "Longitude": current_lon}
                for col_name in ACTIVITY_LOG_COLUMNS: # Ensure all columns
                    if col_name not in new_activity_data: new_activity_data[col_name] = pd.NA
                new_activity_entry = pd.DataFrame([new_activity_data], columns=ACTIVITY_LOG_COLUMNS)

                # Now, activity_log_df is correctly understood as the global one for reading and writing
                temp_activity_log_df = pd.concat([activity_log_df, new_activity_entry], ignore_index=True)
                temp_activity_log_df.to_csv(ACTIVITY_LOG_FILE, index=False)
                activity_log_df = temp_activity_log_df # Update in-memory df
                st.session_state.user_message = "Activity photo and log uploaded!"; st.session_state.message_type = "success"; st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error saving activity: {e}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


elif nav == "🧾 Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    st.markdown("<div class='form-field-label'><h6>Select Allowance Type:</h6></div>", unsafe_allow_html=True)
    a_type = st.radio("", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allowance_type_radio_main", horizontal=True, label_visibility='collapsed')
    amount = st.number_input("Enter Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_main")
    reason = st.text_area("Reason for Allowance:", key="allowance_reason_main", placeholder="Please provide a clear justification for the allowance claim...")
    if st.button("Submit Allowance Request", key="submit_allowance_btn_main", use_container_width=True):
        if a_type and amount > 0 and reason.strip():
            global allowance_df # To update global df
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry_data = {"Username": current_user["username"], "Type": a_type, "Amount": amount, "Reason": reason, "Date": date_str}
            for col_name in ALLOWANCE_COLUMNS: # Ensure all columns
                if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
            new_entry = pd.DataFrame([new_entry_data], columns=ALLOWANCE_COLUMNS)

            temp_allowance_df = pd.concat([allowance_df, new_entry], ignore_index=True)
            try:
                temp_allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                allowance_df = temp_allowance_df # Update in-memory df
                st.session_state.user_message = f"Allowance for ₹{amount:.2f} submitted."; st.session_state.message_type = "success"; st.rerun()
            except Exception as e: st.session_state.user_message = f"Error submitting allowance: {e}"; st.session_state.message_type = "error"; st.rerun()
        else: st.warning("Please complete all fields with valid values.")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "🎯 Goal Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_GOAL_YEAR_TRACKER = 2025; current_quarter_for_display_tracker = get_quarter_str_for_year(TARGET_GOAL_YEAR_TRACKER)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Sales Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR_TRACKER}"], key="admin_goal_action_radio_sales", horizontal=True)
        if admin_action == "View Team Progress":
            st.markdown(f"<h5>Team Goal Progress for {current_quarter_for_display_tracker}</h5>", unsafe_allow_html=True)
            employee_users = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users: st.info("No employees found.")
            else:
                summary_list_sales = []
                for emp_name in employee_users:
                    emp_current_goal = goals_df[(goals_df["Username"].astype(str) == str(emp_name)) & (goals_df["MonthYear"].astype(str) == str(current_quarter_for_display_tracker))]
                    target, achieved, status_val = 0.0, 0.0, "Not Set"
                    if not emp_current_goal.empty:
                        g_data = emp_current_goal.iloc[0]; target = float(pd.to_numeric(g_data.get("TargetAmount"), errors='coerce').fillna(0.0))
                        achieved = float(pd.to_numeric(g_data.get("AchievedAmount", 0.0), errors='coerce').fillna(0.0)); status_val = g_data.get("Status", "N/A")
                    summary_list_sales.append({"Employee": emp_name, "Target": target, "Achieved": achieved, "Status": status_val})
                summary_df_sales_tracker = pd.DataFrame(summary_list_sales)
                if not summary_df_sales_tracker.empty:
                    st.markdown("<h6>Individual Sales Progress:</h6>", unsafe_allow_html=True); num_cols_sales = 3; cols_sales = st.columns(num_cols_sales); col_idx_sales = 0
                    for index, row in summary_df_sales_tracker.iterrows():
                        progress_percent = (row['Achieved'] / row['Target'] * 100) if row['Target'] > 0 else 0; donut_fig = create_donut_chart(progress_percent, achieved_color='#28a745')
                        current_col_sales = cols_sales[col_idx_sales % num_cols_sales]
                        with current_col_sales:
                            st.markdown(f"<div class='employee-progress-item'><h6>{row['Employee']}</h6><p>Target: ₹{row['Target']:,.0f}<br>Achieved: ₹{row['Achieved']:,.0f}</p></div>", unsafe_allow_html=True)
                            if donut_fig: st.pyplot(donut_fig, use_container_width=True); st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                        col_idx_sales += 1
                    st.markdown("<hr style='margin-top: 10px; margin-bottom:25px;'>", unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Sales Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_sales_tracker = create_team_progress_bar_chart(summary_df_sales_tracker, title="Team Sales Target vs. Achieved", target_col="Target", achieved_col="Achieved")
                    if team_bar_fig_sales_tracker: st.pyplot(team_bar_fig_sales_tracker, use_container_width=True)
                    else: st.info("No sales data to plot for the team bar chart.")
                else: st.info(f"No sales goals data found for {current_quarter_for_display_tracker} to display team progress.")
        elif admin_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR_TRACKER}":
            st.markdown(f"<h5>Set or Update Employee Goal ({TARGET_GOAL_YEAR_TRACKER} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employee_options: st.warning("No employees available.")
            else:
                selected_emp = st.radio("Select Employee:", employee_options, key="goal_emp_radio_admin_set_sales", horizontal=True)
                quarter_options = [f"{TARGET_GOAL_YEAR_TRACKER}-Q{i}" for i in range(1,5)]; selected_period = st.radio("Goal Period:", quarter_options, key="goal_period_radio_admin_set_sales", horizontal=True)
                temp_goals_df_edit = goals_df.copy(); existing_g = temp_goals_df_edit[(temp_goals_df_edit["Username"].astype(str)==str(selected_emp)) & (temp_goals_df_edit["MonthYear"].astype(str)==str(selected_period))]
                g_desc,g_target,g_achieved,g_status = "",0.0,0.0,"Not Started"
                if not existing_g.empty:
                    g_data=existing_g.iloc[0]; g_desc=g_data.get("GoalDescription",""); g_target=float(pd.to_numeric(g_data.get("TargetAmount",0.0),errors='coerce').fillna(0.0))
                    g_achieved=float(pd.to_numeric(g_data.get("AchievedAmount",0.0),errors='coerce').fillna(0.0)); g_status=g_data.get("Status","Not Started"); st.info(f"Editing goal for {selected_emp} - {selected_period}")
                with st.form(key=f"set_goal_form_{selected_emp}_{selected_period}_admin_sales"):
                    new_desc=st.text_area("Goal Description",value=g_desc,key=f"desc_{selected_emp}_{selected_period}_g_admin_sales")
                    new_target=st.number_input("Target Sales (INR)",value=g_target,min_value=0.0,step=1000.0,format="%.2f",key=f"target_{selected_emp}_{selected_period}_g_admin_sales")
                    new_achieved=st.number_input("Achieved Sales (INR)",value=g_achieved,min_value=0.0,step=100.0,format="%.2f",key=f"achieved_{selected_emp}_{selected_period}_g_admin_sales")
                    new_status=st.radio("Status:",status_options,index=status_options.index(g_status),horizontal=True,key=f"status_{selected_emp}_{selected_period}_g_admin_sales")
                    submitted=st.form_submit_button("Save Goal")
                if submitted:
                    if not new_desc.strip(): st.warning("Description is required.")
                    elif new_target <= 0 and new_status not in ["Cancelled","On Hold","Not Started"]: st.warning("Target amount must be greater than 0 unless the status is Cancelled, On Hold, or Not Started.")
                    else:
                        global goals_df # To update global df
                        editable_goals_df=goals_df.copy(); existing_g_indices=editable_goals_df[(editable_goals_df["Username"].astype(str)==str(selected_emp))&(editable_goals_df["MonthYear"].astype(str)==str(selected_period))].index
                        if not existing_g_indices.empty: editable_goals_df.loc[existing_g_indices[0]]=[selected_emp,selected_period,new_desc,new_target,new_achieved,new_status]; msg_verb="updated"
                        else:
                            new_row_data={"Username":selected_emp,"MonthYear":selected_period,"GoalDescription":new_desc,"TargetAmount":new_target,"AchievedAmount":new_achieved,"Status":new_status}
                            for col_name in GOALS_COLUMNS: # Ensure all columns
                                if col_name not in new_row_data: new_row_data[col_name]=pd.NA
                            new_row_df=pd.DataFrame([new_row_data],columns=GOALS_COLUMNS); editable_goals_df=pd.concat([editable_goals_df,new_row_df],ignore_index=True); msg_verb="set"
                        try:
                            editable_goals_df.to_csv(GOALS_FILE,index=False)
                            goals_df = editable_goals_df # Update in-memory
                            st.session_state.user_message=f"Sales Goal for {selected_emp} ({selected_period}) {msg_verb}!"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e: st.session_state.user_message=f"Error saving sales goal: {e}"; st.session_state.message_type="error"; st.rerun()
    else: # Employee View for Sales Goals
        st.markdown("<h4>My Sales Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        my_goals_sales = goals_df[goals_df["Username"].astype(str) == str(current_user["username"])].copy()
        for col in ["TargetAmount", "AchievedAmount"]: my_goals_sales[col] = pd.to_numeric(my_goals_sales[col], errors="coerce").fillna(0.0)
        current_g_df_sales = my_goals_sales[my_goals_sales["MonthYear"] == current_quarter_for_display_tracker]
        st.markdown(f"<h5>Current Goal Period: {current_quarter_for_display_tracker}</h5>", unsafe_allow_html=True)
        if not current_g_df_sales.empty:
            g = current_g_df_sales.iloc[0]; target_amt = g["TargetAmount"]; achieved_amt = g["AchievedAmount"]
            st.markdown(f"**Description:** {g.get('GoalDescription', 'N/A')}")
            col_metrics_sales, col_chart_sales = st.columns([0.63,0.37])
            with col_metrics_sales:
                sub_col1,sub_col2=st.columns(2); sub_col1.metric("Target",f"₹{target_amt:,.0f}"); sub_col2.metric("Achieved",f"₹{achieved_amt:,.0f}")
                st.metric("Status",g.get("Status","In Progress"),label_visibility="labeled")
            with col_chart_sales:
                progress_percent_sales=(achieved_amt/target_amt*100) if target_amt > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:-15px;'>Sales Progress</h6>",unsafe_allow_html=True)
                donut_fig_sales=create_donut_chart(progress_percent_sales,"Sales Progress",achieved_color='#28a745')
                if donut_fig_sales: st.pyplot(donut_fig_sales,use_container_width=True)
            st.markdown("---")
            with st.form(key=f"update_achievement_sales_{current_user['username']}_{current_quarter_for_display_tracker}"):
                new_val=st.number_input("Update Achieved Amount (INR):",value=achieved_amt,min_value=0.0,step=100.0,format="%.2f")
                submitted_ach=st.form_submit_button("Update Achievement")
            if submitted_ach:
                global goals_df # To update global df
                editable_goals_df = goals_df.copy()
                idx = editable_goals_df[(editable_goals_df["Username"] == current_user["username"]) &(editable_goals_df["MonthYear"] == current_quarter_for_display_tracker)].index
                if not idx.empty:
                    editable_goals_df.loc[idx[0],"AchievedAmount"]=new_val
                    new_status="Achieved" if new_val >= target_amt and target_amt > 0 else "In Progress"
                    editable_goals_df.loc[idx[0],"Status"]=new_status
                    try:
                        editable_goals_df.to_csv(GOALS_FILE,index=False)
                        goals_df = editable_goals_df # Update in-memory
                        st.session_state.user_message = "Sales achievement updated!"; st.session_state.message_type = "success"; st.rerun()
                    except Exception as e: st.session_state.user_message = f"Error updating sales achievement: {e}"; st.session_state.message_type = "error"; st.rerun()
                else: st.session_state.user_message = "Could not find your current sales goal to update."; st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No sales goal set for {current_quarter_for_display_tracker}. Contact admin.")
        st.markdown("---"); st.markdown(f"<h5>My Past Sales Goals ({TARGET_GOAL_YEAR_TRACKER})</h5>", unsafe_allow_html=True)
        past_goals_sales = my_goals_sales[(my_goals_sales["MonthYear"].astype(str).str.startswith(str(TARGET_GOAL_YEAR_TRACKER))) & (my_goals_sales["MonthYear"].astype(str) != current_quarter_for_display_tracker)]
        if not past_goals_sales.empty: render_goal_chart(past_goals_sales, "Past Sales Goal Performance")
        else: st.info(f"No past sales goal records for {TARGET_GOAL_YEAR_TRACKER}.")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "💰 Payment Collection Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_YEAR_PAYMENT_TRACKER = 2025; current_quarter_display_payment_tracker = get_quarter_str_for_year(TARGET_YEAR_PAYMENT_TRACKER)
    status_options_payment = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Set & Track Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action_payment = st.radio("Action:", ["View Team Progress", f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT_TRACKER}"], key="admin_payment_action_admin_set_collection", horizontal=True)
        if admin_action_payment == "View Team Progress":
            st.markdown(f"<h5>Team Payment Collection Progress for {current_quarter_display_payment_tracker}</h5>", unsafe_allow_html=True)
            employees_payment_list = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employees_payment_list: st.info("No employees found.")
            else:
                summary_list_payment = []
                for emp_pay_name in employees_payment_list:
                    record_payment = payment_goals_df[(payment_goals_df["Username"]==emp_pay_name)&(payment_goals_df["MonthYear"]==current_quarter_display_payment_tracker)]
                    target_p,achieved_p,status_p=0.0,0.0,"Not Set"
                    if not record_payment.empty:
                        rec_payment=record_payment.iloc[0]; target_p=float(pd.to_numeric(rec_payment["TargetAmount"],errors='coerce').fillna(0.0))
                        achieved_p=float(pd.to_numeric(rec_payment["AchievedAmount"],errors='coerce').fillna(0.0)); status_p=rec_payment.get("Status","N/A")
                    summary_list_payment.append({"Employee":emp_pay_name,"Target":target_p,"Achieved":achieved_p,"Status":status_p})
                summary_df_payment_tracker = pd.DataFrame(summary_list_payment)
                if not summary_df_payment_tracker.empty:
                    st.markdown("<h6>Individual Collection Progress:</h6>", unsafe_allow_html=True); num_cols_payment=3; cols_payment=st.columns(num_cols_payment); col_idx_payment=0
                    for index,row in summary_df_payment_tracker.iterrows():
                        progress_percent_p=(row['Achieved']/row['Target']*100) if row['Target'] > 0 else 0; donut_fig_p=create_donut_chart(progress_percent_p,achieved_color='#2070c0')
                        current_col_p=cols_payment[col_idx_payment%num_cols_payment]
                        with current_col_p:
                            st.markdown(f"<div class='employee-progress-item'><h6>{row['Employee']}</h6><p>Target: ₹{row['Target']:,.0f}<br>Collected: ₹{row['Achieved']:,.0f}</p></div>",unsafe_allow_html=True)
                            if donut_fig_p: st.pyplot(donut_fig_p,use_container_width=True); st.markdown("<div style='margin-bottom:15px;'></div>",unsafe_allow_html=True)
                        col_idx_payment+=1
                    st.markdown("<hr style='margin-top:10px;margin-bottom:25px;'>",unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Collection Performance:</h6>",unsafe_allow_html=True)
                    team_bar_fig_payment_tracker = create_team_progress_bar_chart(summary_df_payment_tracker,title="Team Collection Target vs. Achieved",target_col="Target",achieved_col="Achieved")
                    if team_bar_fig_payment_tracker:
                        for bar_group in team_bar_fig_payment_tracker.axes[0].containers:
                            if bar_group.get_label()=='Achieved':
                                for bar in bar_group: bar.set_color('#2070c0')
                        st.pyplot(team_bar_fig_payment_tracker,use_container_width=True)
                    else: st.info("No collection data to plot for team bar chart.")
                else: st.info(f"No payment collection data for {current_quarter_display_payment_tracker}.")
        elif admin_action_payment == f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT_TRACKER}":
            st.markdown(f"<h5>Set or Update Collection Goal ({TARGET_YEAR_PAYMENT_TRACKER} - Quarterly)</h5>", unsafe_allow_html=True)
            employees_for_payment_goal = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employees_for_payment_goal: st.warning("No employees available.")
            else:
                selected_emp_payment=st.radio("Select Employee:",employees_for_payment_goal,key="payment_emp_radio_admin_set_collection",horizontal=True)
                quarters_payment=[f"{TARGET_YEAR_PAYMENT_TRACKER}-Q{i}" for i in range(1,5)]; selected_period_payment=st.radio("Quarter:",quarters_payment,key="payment_period_radio_admin_set_collection",horizontal=True)
                temp_payment_goals_df_edit=payment_goals_df.copy(); existing_payment_goal=temp_payment_goals_df_edit[(temp_payment_goals_df_edit["Username"]==selected_emp_payment)&(temp_payment_goals_df_edit["MonthYear"]==selected_period_payment)]
                desc_payment,tgt_payment_val,ach_payment_val,stat_payment = "",0.0,0.0,"Not Started"
                if not existing_payment_goal.empty:
                    g_payment=existing_payment_goal.iloc[0]; desc_payment=g_payment.get("GoalDescription",""); tgt_payment_val=float(pd.to_numeric(g_payment.get("TargetAmount",0.0),errors='coerce').fillna(0.0))
                    ach_payment_val=float(pd.to_numeric(g_payment.get("AchievedAmount",0.0),errors='coerce').fillna(0.0)); stat_payment=g_payment.get("Status","Not Started")
                    st.info(f"Editing payment goal for {selected_emp_payment} - {selected_period_payment}")
                with st.form(f"form_payment_{selected_emp_payment}_{selected_period_payment}_admin_collection"):
                    new_desc_payment=st.text_input("Collection Goal Description",value=desc_payment,key=f"desc_pay_{selected_emp_payment}_{selected_period_payment}_p_admin_collection")
                    new_tgt_payment=st.number_input("Target Collection (INR)",value=tgt_payment_val,min_value=0.0,step=1000.0,key=f"target_pay_{selected_emp_payment}_{selected_period_payment}_p_admin_collection")
                    new_ach_payment=st.number_input("Collected Amount (INR)",value=ach_payment_val,min_value=0.0,step=500.0,key=f"achieved_pay_{selected_emp_payment}_{selected_period_payment}_p_admin_collection")
                    new_status_payment=st.selectbox("Status",status_options_payment,index=status_options_payment.index(stat_payment),key=f"status_pay_{selected_emp_payment}_{selected_period_payment}_p_admin_collection")
                    submitted_payment=st.form_submit_button("Save Goal")
                if submitted_payment:
                    if not new_desc_payment.strip(): st.warning("Description required.")
                    elif new_tgt_payment <= 0 and new_status_payment not in ["Cancelled","Not Started", "On Hold"]: st.warning("Target amount must be greater than 0 unless status is Cancelled, Not Started or On Hold.")
                    else:
                        global payment_goals_df # To update global df
                        editable_payment_goals_df=payment_goals_df.copy(); existing_pg_indices=editable_payment_goals_df[(editable_payment_goals_df["Username"]==selected_emp_payment)&(editable_payment_goals_df["MonthYear"]==selected_period_payment)].index
                        if not existing_pg_indices.empty: editable_payment_goals_df.loc[existing_pg_indices[0]]=[selected_emp_payment,selected_period_payment,new_desc_payment,new_tgt_payment,new_ach_payment,new_status_payment]; msg_payment="updated"
                        else:
                            new_row_data_p={"Username":selected_emp_payment,"MonthYear":selected_period_payment,"GoalDescription":new_desc_payment,"TargetAmount":new_tgt_payment,"AchievedAmount":new_ach_payment,"Status":new_status_payment}
                            for col_name in PAYMENT_GOALS_COLUMNS: # Ensure all columns
                                if col_name not in new_row_data_p: new_row_data_p[col_name]=pd.NA
                            new_row_df_p=pd.DataFrame([new_row_data_p],columns=PAYMENT_GOALS_COLUMNS); editable_payment_goals_df=pd.concat([editable_payment_goals_df,new_row_df_p],ignore_index=True); msg_payment="set"
                        try:
                            editable_payment_goals_df.to_csv(PAYMENT_GOALS_FILE,index=False)
                            payment_goals_df = editable_payment_goals_df # Update in-memory
                            st.session_state.user_message=f"Payment goal {msg_payment} for {selected_emp_payment} ({selected_period_payment})"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e: st.session_state.user_message=f"Error saving payment goal: {e}"; st.session_state.message_type="error"; st.rerun()
    else: # Employee View for Payment Collection
        st.markdown(f"<h4>My Payment Collection Goals ({TARGET_YEAR_PAYMENT_TRACKER})</h4>", unsafe_allow_html=True)
        user_goals_payment = payment_goals_df[payment_goals_df["Username"]==current_user["username"]].copy()
        user_goals_payment[["TargetAmount","AchievedAmount"]] = user_goals_payment[["TargetAmount","AchievedAmount"]].apply(pd.to_numeric,errors="coerce").fillna(0.0)
        current_payment_goal_period_df = user_goals_payment[user_goals_payment["MonthYear"]==current_quarter_display_payment_tracker]
        st.markdown(f"<h5>Current Quarter: {current_quarter_display_payment_tracker}</h5>", unsafe_allow_html=True)
        if not current_payment_goal_period_df.empty:
            g_pay=current_payment_goal_period_df.iloc[0]; tgt_pay=g_pay["TargetAmount"]; ach_pay=g_pay["AchievedAmount"]
            st.markdown(f"**Goal:** {g_pay.get('GoalDescription','')}")
            col_metrics_pay,col_chart_pay=st.columns([0.63,0.37])
            with col_metrics_pay:
                sub_col1_pay,sub_col2_pay=st.columns(2); sub_col1_pay.metric("Target",f"₹{tgt_pay:,.0f}"); sub_col2_pay.metric("Collected",f"₹{ach_pay:,.0f}")
                st.metric("Status",g_pay.get("Status","In Progress"),label_visibility="labeled")
            with col_chart_pay:
                progress_percent_pay=(ach_pay/tgt_pay*100) if tgt_pay > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:-15px;'>Collection Progress</h6>",unsafe_allow_html=True)
                donut_fig_payment=create_donut_chart(progress_percent_pay,"Collection Progress",achieved_color='#2070c0')
                if donut_fig_payment: st.pyplot(donut_fig_payment,use_container_width=True)
            st.markdown("---")
            with st.form(key=f"update_collection_{current_user['username']}_{current_quarter_display_payment_tracker}"):
                new_ach_val_payment=st.number_input("Update Collected Amount (INR):",value=ach_pay,min_value=0.0,step=500.0)
                submit_collection_update=st.form_submit_button("Update Collection")
            if submit_collection_update:
                global payment_goals_df # To update global df
                editable_payment_goals_df = payment_goals_df.copy()
                idx_pay=editable_payment_goals_df[(editable_payment_goals_df["Username"]==current_user["username"])&(editable_payment_goals_df["MonthYear"]==current_quarter_display_payment_tracker)].index
                if not idx_pay.empty:
                    editable_payment_goals_df.loc[idx_pay[0],"AchievedAmount"]=new_ach_val_payment
                    editable_payment_goals_df.loc[idx_pay[0],"Status"]="Achieved" if new_ach_val_payment >= tgt_pay and tgt_pay > 0 else "In Progress"
                    try:
                        editable_payment_goals_df.to_csv(PAYMENT_GOALS_FILE,index=False)
                        payment_goals_df = editable_payment_goals_df # Update in-memory
                        st.session_state.user_message = "Collection updated."; st.session_state.message_type = "success"; st.rerun()
                    except Exception as e: st.session_state.user_message = f"Error updating collection: {e}"; st.session_state.message_type = "error"; st.rerun()
                else: st.session_state.user_message = "Could not find your current payment goal to update."; st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No collection goal for {current_quarter_display_payment_tracker}.")
        st.markdown(f"<h5>Past Quarters ({TARGET_YEAR_PAYMENT_TRACKER})</h5>", unsafe_allow_html=True)
        past_payment_goals = user_goals_payment[(user_goals_payment["MonthYear"].str.startswith(str(TARGET_YEAR_PAYMENT_TRACKER))) & (user_goals_payment["MonthYear"]!=current_quarter_display_payment_tracker)]
        if not past_payment_goals.empty: render_goal_chart(past_payment_goals,"Past Collection Performance")
        else: st.info("No past collection goals for this year.")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "📊 View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 View Logs</h3>", unsafe_allow_html=True)
    def display_activity_logs_with_photos(df_logs, user_name_for_header):
        if df_logs.empty: st.info(f"No activity logs for {user_name_for_header}."); return
        df_logs_sorted = df_logs.copy()
        df_logs_sorted['Timestamp_dt'] = pd.to_datetime(df_logs_sorted['Timestamp'], errors='coerce') # Convert for sorting
        df_logs_sorted = df_logs_sorted.sort_values(by="Timestamp_dt", ascending=False)

        st.markdown(f"<h5>Field Activity Logs for: {user_name_for_header}</h5>", unsafe_allow_html=True)
        for index, row in df_logs_sorted.iterrows():
            st.markdown("---"); col_details, col_photo = st.columns([0.7, 0.3])
            with col_details:
                ts_display = row['Timestamp_dt'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['Timestamp_dt']) else row['Timestamp']
                st.markdown(f"**Timestamp:** {ts_display}<br>**Description:** {row.get('Description', 'N/A')}<br>**Location:** {'Not Recorded' if pd.isna(row.get('Latitude')) or pd.isna(row.get('Longitude')) else f"Lat: {row.get('Latitude'):.4f}, Lon: {row.get('Longitude'):.4f}"}", unsafe_allow_html=True)
                if pd.notna(row.get('ImageFile')) and row.get('ImageFile') != "": st.caption(f"Photo ID: {row['ImageFile']}")
                else: st.caption("No photo for this activity.")
            with col_photo:
                if pd.notna(row.get('ImageFile')) and row.get('ImageFile') != "":
                    image_path_to_display = os.path.join(ACTIVITY_PHOTOS_DIR, str(row['ImageFile']))
                    if os.path.exists(image_path_to_display):
                        try: st.image(image_path_to_display, width=150)
                        except Exception as img_e: st.warning(f"Could not load image {row['ImageFile']}: {img_e}")
                    else: st.caption(f"Photo missing: {row['ImageFile']}")
    def display_attendance_logs(df_logs, user_name_for_header):
        if df_logs.empty: st.warning(f"No general attendance records for {user_name_for_header}."); return
        df_logs_sorted = df_logs.copy()
        df_logs_sorted['Timestamp_dt'] = pd.to_datetime(df_logs_sorted['Timestamp'], errors='coerce')
        df_logs_sorted = df_logs_sorted.sort_values(by="Timestamp_dt", ascending=False)

        st.markdown(f"<h5>General Attendance Records for: {user_name_for_header}</h5>", unsafe_allow_html=True)
        columns_to_show = ["Type", "Timestamp"] # Start with basic columns
        # Create a display 'Location' column if Lat/Lon exist
        if 'Latitude' in df_logs_sorted.columns and 'Longitude' in df_logs_sorted.columns:
            df_logs_sorted['Location'] = df_logs_sorted.apply(
                lambda row: f"Lat: {row['Latitude']:.4f}, Lon: {row['Longitude']:.4f}"
                if pd.notna(row['Latitude']) and pd.notna(row['Longitude']) else "Not Recorded", axis=1
            )
            columns_to_show.append('Location')
        st.dataframe(df_logs_sorted[columns_to_show].reset_index(drop=True), use_container_width=True, hide_index=True)

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: View Employee Records</h4>", unsafe_allow_html=True)
        employee_name_list = [name for name, data in USERS.items() if data["role"] == "employee"] # Only employees
        if not employee_name_list:
            st.info("No employees found to display logs for.")
        else:
            selected_employee_log = st.selectbox("Select Employee:", employee_name_list, key="log_employee_select_admin_logs")
            if selected_employee_log: # Proceed only if an employee is selected
                st.markdown(f"<h4 class='employee-section-header'>Records for {selected_employee_log}</h4>", unsafe_allow_html=True)

                st.markdown("<h5 class='record-type-header'>Field Activity Logs</h5>", unsafe_allow_html=True)
                emp_activity_log = activity_log_df[activity_log_df["Username"] == selected_employee_log]
                display_activity_logs_with_photos(emp_activity_log, selected_employee_log)

                st.markdown("<h5 class='record-type-header'>General Attendance</h5>", unsafe_allow_html=True)
                emp_attendance_log = attendance_df[attendance_df["Username"] == selected_employee_log]
                display_attendance_logs(emp_attendance_log, selected_employee_log)

                st.markdown("<h5 class='record-type-header'>Allowances</h5>", unsafe_allow_html=True)
                emp_allowance_log = allowance_df[allowance_df["Username"] == selected_employee_log]
                if not emp_allowance_log.empty: st.dataframe(emp_allowance_log.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
                else: st.info("No allowance records found.")

                st.markdown("<h5 class='record-type-header'>Sales Goals</h5>", unsafe_allow_html=True)
                emp_goals_log = goals_df[goals_df["Username"] == selected_employee_log]
                if not emp_goals_log.empty: st.dataframe(emp_goals_log.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
                else: st.info("No sales goals records found.")

                st.markdown("<h5 class='record-type-header'>Payment Collection Goals</h5>", unsafe_allow_html=True)
                emp_payment_goals_log = payment_goals_df[payment_goals_df["Username"] == selected_employee_log]
                if not emp_payment_goals_log.empty: st.dataframe(emp_payment_goals_log.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
                else: st.info("No payment collection goals records found.")
            # else: No employee selected, selectbox has a default or is empty.
    else: # Employee view for logs
        st.markdown("<h4>My Records</h4>", unsafe_allow_html=True)

        st.markdown("<h5 class='record-type-header'>My Field Activity Logs</h5>", unsafe_allow_html=True)
        my_activity_log = activity_log_df[activity_log_df["Username"] == current_user["username"]]
        display_activity_logs_with_photos(my_activity_log, current_user["username"])

        st.markdown("<h5 class='record-type-header'>My General Attendance</h5>", unsafe_allow_html=True)
        my_attendance_log = attendance_df[attendance_df["Username"] == current_user["username"]]
        display_attendance_logs(my_attendance_log, current_user["username"])

        st.markdown("<h5 class='record-type-header'>My Allowances</h5>", unsafe_allow_html=True)
        my_allowance_log = allowance_df[allowance_df["Username"] == current_user["username"]]
        if not my_allowance_log.empty: st.dataframe(my_allowance_log.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
        else: st.info("No allowance records found for you.")

        st.markdown("<h5 class='record-type-header'>My Sales Goals</h5>", unsafe_allow_html=True)
        my_goals_log = goals_df[goals_df["Username"] == current_user["username"]]
        if not my_goals_log.empty: st.dataframe(my_goals_log.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
        else: st.info("No sales goals records found for you.")

        st.markdown("<h5 class='record-type-header'>My Payment Collection Goals</h5>", unsafe_allow_html=True)
        my_payment_goals_log = payment_goals_df[payment_goals_df["Username"] == current_user["username"]]
        if not my_payment_goals_log.empty: st.dataframe(my_payment_goals_log.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
        else: st.info("No payment collection goals records found for you.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.error("Page not found or navigation error.") # Fallback for unknown nav item
