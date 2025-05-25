import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import pytz
# import sys # Not used, can be removed
import altair as alt # Keep for existing past goals chart

# --- Matplotlib Configuration ---
import matplotlib
matplotlib.use('Agg') # Use a non-interactive backend for Matplotlib
import matplotlib.pyplot as plt
import numpy as np # For bar chart positioning

# --- Pillow for placeholder image generation (optional) --
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# --- Function to render Altair bar chart (existing for past goals) ---
def render_goal_chart(df: pd.DataFrame, title: str):
    if df.empty:
        st.warning("No data available to plot.")
        return
    df = df.copy()
    df[["TargetAmount", "AchievedAmount"]] = df[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce")
    df = df.sort_values(by="MonthYear")

    long_df = df.melt(id_vars=["MonthYear"], value_vars=["TargetAmount", "AchievedAmount"],
                      var_name="Metric", value_name="Amount")
    chart = alt.Chart(long_df).mark_bar().encode(
        x=alt.X('MonthYear:N', title="Quarter"),
        y=alt.Y('Amount:Q', title="Amount (INR)"),
        color=alt.Color('Metric:N', scale=alt.Scale(domain=['TargetAmount', 'AchievedAmount'], range=["#3498db", "#2ecc71"])), # Explicit domain
        tooltip=["MonthYear", "Metric", "Amount"]
    ).properties(
        title=title,
        width="container"
    )
    st.altair_chart(chart, use_container_width=True)

# --- Function to create Matplotlib Donut Chart ---
def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#2ecc71', remaining_color='#f0f0f0', center_text_color=None):
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=90) # Smaller for admin view potentially
    fig.patch.set_alpha(0) 
    ax.patch.set_alpha(0)

    progress_percentage = max(0.0, min(float(progress_percentage), 100.0))
    remaining_percentage = 100.0 - progress_percentage

    if progress_percentage <= 0.01: # Handle near-zero to avoid tiny sliver
        sizes = [100.0]
        slice_colors = [remaining_color]
        actual_progress_display = 0.0 # Display 0% if effectively no progress
    elif progress_percentage >= 99.99: # Handle near-100
        sizes = [100.0]
        slice_colors = [achieved_color]
        actual_progress_display = 100.0
    else:
        sizes = [progress_percentage, remaining_percentage]
        slice_colors = [achieved_color, remaining_color]
        actual_progress_display = progress_percentage
    
    wedges, texts = ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False,
                           wedgeprops=dict(width=0.4, edgecolor='white')) 

    centre_circle = plt.Circle((0,0),0.60,fc='white') 
    fig.gca().add_artist(centre_circle)
    
    text_color_to_use = center_text_color if center_text_color else (achieved_color if actual_progress_display > 0 else '#4A4A4A')
    
    ax.text(0, 0, f"{actual_progress_display:.0f}%", 
            ha='center', va='center', 
            fontsize=12, fontweight='bold', 
            color=text_color_to_use)
    
    ax.axis('equal')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0) 
    return fig

# --- Function to create Matplotlib Grouped Bar Chart for Team Progress ---
def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee"):
    if summary_df.empty:
        return None

    labels = summary_df[user_col].tolist()
    target_amounts = summary_df[target_col].fillna(0).tolist()
    achieved_amounts = summary_df[achieved_col].fillna(0).tolist()

    x = np.arange(len(labels))  
    width = 0.35  

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
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0: 
                ax.annotate(f'{height:,.0f}', 
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=7, color='#333')
    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout(pad=1.5)
    return fig

html_css = """
<style>
    :root {
        --primary-color: #1c4e80; /* Dark Blue */
        --secondary-color: #2070c0; /* Medium Blue */
        --accent-color: #70a1d7; /* Light Blue */
        --success-color: #28a745; /* Green */
        --danger-color: #dc3545; /* Red */
        --warning-color: #ffc107; /* Yellow */
        --info-color: #17a2b8; /* Teal */

        --body-bg-color: #f4f6f9; /* Slightly lighter gray for body */
        --card-bg-color: #ffffff;
        --text-color: #343a40; /* Darker gray for text */
        --text-muted-color: #6c757d; /* Lighter gray for muted text */
        --border-color: #dee2e6; /* Standard border color */
        --input-border-color: #ced4da;

        --font-family-sans-serif: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
        --border-radius: 0.375rem; /* 6px */
        --border-radius-lg: 0.5rem; /* 8px */
        --box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.075);
        --box-shadow-sm: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }

    /* --- General --- */
    body {
        font-family: var(--font-family-sans-serif);
        background-color: var(--body-bg-color);
        color: var(--text-color);
        line-height: 1.6;
    }

    /* --- Titles & Headers --- */
    h1, h2, h3, h4, h5, h6 {
        color: var(--primary-color);
        font-weight: 600;
    }
    .main .block-container > div:first-child > div:first-child > div:first-child > h1 { /* Main page title */
        text-align: center;
        font-size: 2.6em;
        font-weight: 700;
        padding-bottom: 25px;
        border-bottom: 3px solid var(--accent-color);
        margin-bottom: 40px;
        letter-spacing: -0.5px;
    }

    /* --- Card Styling --- */
    .card {
        background-color: var(--card-bg-color);
        padding: 30px; /* Increased padding */
        border-radius: var(--border-radius-lg);
        box-shadow: var(--box-shadow);
        margin-bottom: 35px;
        border: 1px solid var(--border-color);
    }
    .card h3 { /* Page subheader inside card */
        margin-top: 0;
        color: var(--primary-color);
        border-bottom: 2px solid #e9ecef; /* Lighter, thicker border */
        padding-bottom: 15px;
        margin-bottom: 25px;
        font-size: 1.75em;
        font-weight: 600;
    }
    .card h4 { /* Section headers inside card */
        color: var(--secondary-color);
        margin-top: 30px;
        margin-bottom: 20px;
        font-size: 1.4em;
        padding-bottom: 8px;
        border-bottom: 1px solid #e0e0e0; /* Solid, lighter border */
    }
     .card h5 { /* Sub-section headers */
        font-size: 1.15em;
        color: var(--text-color);
        margin-top: 25px;
        margin-bottom: 12px;
        font-weight: 600;
    }
    .card h6 { /* Small text headers / labels */
        font-size: 1em;
        color: var(--text-muted-color);
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* --- Login Container --- */
    .login-container {
        max-width: 480px; /* Slightly wider */
        margin: 60px auto;
        border-top: 5px solid var(--secondary-color); /* Accent border top */
    }
    .login-container .stButton button {
        width: 100%;
        background-color: var(--secondary-color);
        font-size: 1.1em;
        padding: 12px 20px; /* Larger padding */
        border-radius: var(--border-radius);
    }
    .login-container .stButton button:hover {
        background-color: var(--primary-color);
    }

    /* --- Streamlit Button Styling (General) --- */
    .stButton button {
        background-color: var(--success-color);
        color: white;
        padding: 10px 24px; /* Adjusted padding */
        border: none;
        border-radius: var(--border-radius);
        font-size: 1.05em; /* Slightly larger font */
        font-weight: 500; /* Medium weight */
        transition: background-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
        box-shadow: var(--box-shadow-sm);
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: #218838; /* Darker green on hover */
        transform: translateY(-2px);
        box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
    }
    .stButton button:active {
        transform: translateY(0px);
        box-shadow: var(--box-shadow-sm);
    }
    .stButton button[id*="logout_button_sidebar"] { /* Sidebar logout */
        background-color: var(--danger-color) !important;
        border: 1px solid var(--danger-color) !important;
    }
    .stButton button[id*="logout_button_sidebar"]:hover {
        background-color: #c82333 !important; /* Darker red on hover */
        border-color: #c82333 !important;
    }

    /* --- Input Fields --- */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stDateInput input,
    .stTimeInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: var(--border-radius) !important;
        border: 1px solid var(--input-border-color) !important;
        padding: 10px 12px !important; /* Consistent padding */
        font-size: 1em !important;
        color: var(--text-color) !important;
        background-color: var(--card-bg-color) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: var(--text-muted-color) !important;
        opacity: 1;
    }
    .stTextArea textarea {
        min-height: 120px; /* Slightly taller */
    }
    /* Focus States for Inputs */
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus,
    .stDateInput input:focus,
    .stTimeInput input:focus,
    .stSelectbox div[data-baseweb="select"] > div:focus-within { /* More reliable for selectbox */
        border-color: var(--secondary-color) !important;
        box-shadow: 0 0 0 0.2rem rgba(32, 112, 192, 0.25) !important; /* Using RGB values for secondary color */
    }

    /* --- Sidebar --- */

        /* --- Sidebar --- */
    [data-testid="stSidebar"] {
        background-color: var(--primary-color);
        padding: 25px !important;
        box-shadow: 0.25rem 0 1rem rgba(0,0,0,0.1);
    }
    [data-testid="stSidebar"] .sidebar-content {
        padding-top: 10px;
    }
    /* General text color for p, h1-h3, and generic divs within the sidebar */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] div:not([data-testid="stRadio"]) { /* Target divs NOT part of radio group */
        color: #e9ecef !important; /* Lighter text for general content */
    }

    /* Specific styling for Radio Button LABELS in the sidebar */
    [data-testid="stSidebar"] .stRadio > label > div > p { /* Target the <p> inside the radio label structure */
        font-size: 1.05em !important;
        color: #a9d6e5 !important; /* Light Blue (accent color) for UNSELECTED radio labels */
        padding: 0; /* Reset padding as it might be inherited */
        margin: 0; /* Reset margin */
    }
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label > div > p { /* Selected Sidebar Radio Label Text */
        color: var(--card-bg-color) !important; /* Bright White for SELECTED radio label text */
        font-weight: 600;
    }

    /* Styling for the radio button's clickable area (background on hover/selection) */
    [data-testid="stSidebar"] .stRadio > label {
        padding: 10px 15px; /* Padding for the clickable area */
        border-radius: var(--border-radius);
        margin-bottom: 6px;
        transition: background-color 0.2s ease; /* Only transition background */
    }
    [data-testid="stSidebar"] .stRadio > label:hover {
        background-color: rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label { /* Background for selected radio */
        background-color: rgba(255, 255, 255, 0.15);
    }

    .welcome-text {
        font-size: 1.4em;
        font-weight: 600;
        margin-bottom: 25px;
        text-align: center;
        color: var(--card-bg-color) !important;
        border-bottom: 1px solid var(--accent-color);
        padding-bottom: 20px;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] > img {
        border-radius: 50%;
        border: 3px solid var(--accent-color);
        margin: 0 auto 10px auto;
        display: block;
    }

    /* --- Dataframe Styling --- */
    .stDataFrame {
        width: 100%;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-lg);
        overflow: hidden;
        box-shadow: var(--box-shadow-sm);
        margin-bottom: 25px;
    }
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
    }
    .stDataFrame table thead th {
        background-color: #e9ecef; /* Lighter, neutral header */
        color: var(--primary-color);
        font-weight: 600;
        text-align: left;
        padding: 14px 18px; /* Increased padding */
        border-bottom: 2px solid var(--border-color);
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stDataFrame table tbody td {
        padding: 12px 18px; /* Increased padding */
        border-bottom: 1px solid #f1f3f5; /* Softer internal borders */
        vertical-align: middle;
        color: var(--text-color);
        font-size: 0.9em;
    }
    .stDataFrame table tbody tr:last-child td {
        border-bottom: none;
    }
    .stDataFrame table tbody tr:hover {
        background-color: #f8f9fa; /* Subtle hover */
    }
    /* --- Styling for admin individual progress items in columns --- */
    .employee-progress-item {
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 15px;
        text-align: center;
        background-color: #fdfdfd; /* Slightly off-white */
        margin-bottom: 10px; /* Space below each item before the next row starts implicitly via st.columns */
    }
    .employee-progress-item h6 { /* Employee name title */
        margin-top: 0;
        margin-bottom: 5px;
        font-size: 1em;
        color: var(--primary-color);
        font-weight: 600;
    }
    .employee-progress-item p { /* Target/Achieved text */
        font-size: 0.85em;
        color: var(--text-muted-color);
        margin-bottom: 8px;
    }


    /* --- Columns for buttons --- */
    .button-column-container > div[data-testid="stHorizontalBlock"] {
        gap: 20px; /* Increased gap */
    }
    .button-column-container .stButton button {
        width: 100%;
    }

    /* Horizontal Radio Buttons (Main Content) */
    div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;
        gap: 10px; /* Slightly reduced gap for tighter look if many options */
        margin-bottom: 25px;
    }
    div[role="radiogroup"] > label { /* Unselected radio button */
        background-color: ##53687d;
        color: var(--text-muted-color);
        padding: 10px 18px;
        border-radius: var(--border-radius);
        border: 1px solid var(--input-border-color);
        cursor: pointer;
        transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
        font-size: 0.95em;
        font-weight: 500;
    }
    div[role="radiogroup"] > label:hover {
        background-color: #dde2e6;
        border-color: #adb5bd;
        color: var(--text-color);
    }
    div[role="radiogroup"] div[data-baseweb="radio"][aria-checked="true"] + label { /* Selected radio button */
        background-color: var(--secondary-color) !important;
        color: white !important;
        border-color: var(--secondary-color) !important;
        font-weight: 500;
    }

    /* --- Specific Section Headers (already well-defined, minor tweaks) --- */
    .employee-section-header {
        color: var(--secondary-color); margin-top: 30px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; font-size: 1.35em;
    }
    .record-type-header {
        font-size: 1.1em; color: var(--text-color); margin-top: 25px; margin-bottom: 12px; font-weight: 600;
    }
    .allowance-summary-header {
        font-size: 1.0em; color: var(--text-muted-color); margin-top: 18px; margin-bottom: 10px; font-weight: 500;
    }

    /* --- Image & Progress Bar --- */
    div[data-testid="stImage"] > img { /* General images, not sidebar one */
        border-radius: var(--border-radius-lg);
        border: 1px solid var(--border-color);
        box-shadow: var(--box-shadow-sm);
    }
    .stProgress > div > div { /* Progress bar fill */
        background-color: var(--secondary-color) !important;
        border-radius: var(--border-radius);
    }
    .stProgress { /* Progress bar container */
        border-radius: var(--border-radius);
        background-color: #e9ecef;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.95em !important;
        color: var(--text-muted-color) !important;
        font-weight: 500;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8em !important; /* Larger metric value */
        font-weight: 600;
        color: var(--primary-color);
    }


    /* --- Custom Notification Styling (Enhanced) --- */
    .custom-notification {
        padding: 15px 20px;
        border-radius: var(--border-radius);
        margin-bottom: 20px;
        font-size: 1em;
        border-left-width: 5px;
        border-left-style: solid;
        display: flex; /* For icon alignment if you add one */
        align-items: center;
    }
    .custom-notification.success {
        background-color: #d1e7dd; color: #0f5132; border-left-color: var(--success-color);
    }
    .custom-notification.error {
        background-color: #f8d7da; color: #842029; border-left-color: var(--danger-color);
    }
    .custom-notification.warning {
        background-color: #fff3cd; color: #664d03; border-left-color: var(--warning-color);
    }
    .custom-notification.info {
        background-color: #cff4fc; color: #055160; border-left-color: var(--info-color);
    }

    /* --- Badge Styling --- */
    .badge {
        display: inline-block;
        padding: 0.35em 0.65em; /* Slightly larger padding */
        font-size: 0.85em; /* Slightly larger font */
        font-weight: 600; /* Bolder */
        line-height: 1;
        color: #fff;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: var(--border-radius); /* Consistent border-radius */
    }
    .badge.green { background-color: var(--success-color); }
    .badge.red { background-color: var(--danger-color); }
    .badge.orange { background-color: var(--warning-color); }
    .badge.blue { background-color: var(--secondary-color); } /* Added a blue badge */
    .badge.grey { background-color: var(--text-muted-color); } /* Added a grey badge */

</style>
"""
st.markdown(html_css, unsafe_allow_html=True)

# --- Credentials & User Info ---
USERS = {
    "Geetali": {"password": "Geetali123", "role": "employee", "position": "Software Engineer", "profile_photo": "images/geetali.png"},
    "Nilesh": {"password": "Nilesh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "admin": {"password": "admin123", "role": "admin", "position": "System Administrator", "profile_photo": "images/admin.png"}
}

# --- Create dummy images folder and placeholder images for testing ---
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
                try:
                    font = ImageFont.truetype("arial.ttf", 40)
                except IOError:
                    font = ImageFont.load_default()

                text = user_key[:2].upper()
                if hasattr(draw, 'textbbox'): 
                    bbox = draw.textbbox((0,0), text, font=font)
                    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    text_x, text_y = (120 - text_width) / 2, (120 - text_height) / 2 - bbox[1] 
                elif hasattr(draw, 'textsize'): 
                    text_width, text_height = draw.textsize(text, font=font)
                    text_x, text_y = (120 - text_width) / 2, (120 - text_height) / 2
                else: 
                    text_x, text_y = 30,30 
                draw.text((text_x, text_y), text, fill=(28, 78, 128), font=font)
                img.save(img_path)
            except Exception: pass 


# --- File Paths ---
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"
GOALS_FILE = "goals.csv"
PAYMENT_GOALS_FILE = "payment_goals.csv"

# --- Timezone Configuration ---
TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'. Use valid Olson name."); st.stop()

def get_current_time_in_tz(): return datetime.now(timezone.utc).astimezone(tz)
def get_current_month_year_str(): return get_current_time_in_tz().strftime("%Y-%m")

# --- Load or create data ---
def load_data(path, columns):
    if os.path.exists(path):
        try:
            if os.path.getsize(path) > 0:
                df = pd.read_csv(path)
                for col in columns:
                    if col not in df.columns: df[col] = pd.NA 
                num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude"]
                for nc in num_cols:
                    if nc in df.columns: 
                         df[nc] = pd.to_numeric(df[nc], errors='coerce')
                return df
            else: return pd.DataFrame(columns=columns) 
        except pd.errors.EmptyDataError: return pd.DataFrame(columns=columns) 
        except Exception as e:
            st.error(f"Error loading {path}: {e}. Check file format. Empty DataFrame returned.")
            return pd.DataFrame(columns=columns)
    else: 
        df = pd.DataFrame(columns=columns)
        try: df.to_csv(path, index=False) 
        except Exception as e: st.warning(f"Could not create {path}: {e}")
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]


attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)


# --- Initialize Session State for Notifications ---
if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None

# --- Login Page ---
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}

if not st.session_state.auth["logged_in"]:
    st.title("🙂HR Dashboard Login")
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
            st.session_state.user_message = "Login successful!"; st.session_state.message_type = "success"
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# --- Main Application ---
st.title("👨‍💼 HR Dashboard")
current_user = st.session_state.auth

message_placeholder = st.empty()
if st.session_state.user_message:
    message_placeholder.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
    st.session_state.user_message = None; st.session_state.message_type = None

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user['username']}!</div>", unsafe_allow_html=True)
    nav_options = ["📆 Attendance", "🧾 Allowance", "🎯 Goal Tracker","💰 Payment Collection Tracker", "📊 View Logs"]
    nav = st.radio("Navigation", nav_options, key="sidebar_nav_main")
    user_sidebar_info = USERS.get(current_user["username"], {})
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]):
        st.image(user_sidebar_info["profile_photo"], width=100, use_column_width='auto') 
    st.markdown(f"<p style='text-align:center; font-size:0.9em; color: #e0e0e0;'>{user_sidebar_info.get('position', 'N/A')}</p>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔒 Logout", key="logout_button_sidebar", use_container_width=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."; st.session_state.message_type = "info"
        st.rerun()

# --- Helper function for quarter string ---
def get_quarter_str_for_year(year, for_current_display=False): 
    now_month = get_current_time_in_tz().month
    if 1 <= now_month <= 3: quarter_num_str = "Q1"
    elif 4 <= now_month <= 6: quarter_num_str = "Q2"
    elif 7 <= now_month <= 9: quarter_num_str = "Q3"
    else: quarter_num_str = "Q4"
    return f"{year}-{quarter_num_str}"

# --- Main Content Area ---
if nav == "📆 Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled for attendance.", icon="ℹ️")
    st.markdown("---")
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    common_data = {"Username": current_user["username"], "Latitude": pd.NA, "Longitude": pd.NA}

    with col1:
        if st.button("✅ Check In", key="check_in_btn_main", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            new_entry_data = {"Type": "Check-In", "Timestamp": now_str, **common_data}
            for col_name in ATTENDANCE_COLUMNS:
                if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA 
            new_entry = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
            attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
            try:
                attendance_df.to_csv(ATTENDANCE_FILE, index=False)
                st.session_state.user_message = f"Checked in at {now_str} (Location not recorded)."
                st.session_state.message_type = "success"
                st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error saving attendance: {e}"
                st.session_state.message_type = "error"
                st.rerun()
    with col2:
        if st.button("🚪 Check Out", key="check_out_btn_main", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            new_entry_data = {"Type": "Check-Out", "Timestamp": now_str, **common_data}
            for col_name in ATTENDANCE_COLUMNS:
                if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
            new_entry = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
            attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
            try:
                attendance_df.to_csv(ATTENDANCE_FILE, index=False)
                st.session_state.user_message = f"Checked out at {now_str} (Location not recorded)."
                st.session_state.message_type = "success"
                st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error saving attendance: {e}"
                st.session_state.message_type = "error"
                st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

elif nav == "🧾 Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    st.markdown("<h6>Select Allowance Type:</h6>", unsafe_allow_html=True)
    a_type = st.radio("", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allowance_type_radio_main", horizontal=True, label_visibility='collapsed')
    amount = st.number_input("Enter Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_main")
    reason = st.text_area("Reason for Allowance:", key="allowance_reason_main", placeholder="Please provide a clear justification...")
    if st.button("Submit Allowance Request", key="submit_allowance_btn_main", use_container_width=True):
        if a_type and amount > 0 and reason.strip():
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry_data = {"Username": current_user["username"], "Type": a_type, "Amount": amount, "Reason": reason, "Date": date_str}
            new_entry = pd.DataFrame([new_entry_data], columns=ALLOWANCE_COLUMNS)
            allowance_df = pd.concat([allowance_df, new_entry], ignore_index=True)
            try:
                allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                st.session_state.user_message = f"Allowance for ₹{amount:.2f} submitted."; st.session_state.message_type = "success"
                st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error saving allowance: {e}"; st.session_state.message_type = "error"
                st.rerun()
        else: st.warning("Please complete all fields with valid values.")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "🎯 Goal Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)

    TARGET_GOAL_YEAR = 2025
    current_quarter_for_display = get_quarter_str_for_year(TARGET_GOAL_YEAR, for_current_display=True)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio(
            "Action:",
            ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR}"],
            key="admin_goal_action_radio_2025_q",
            horizontal=True
        )
        if admin_action == "View Team Progress":
            st.markdown(f"<h5>Team Goal Progress for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            employee_users = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users: st.info("No employees found.")
            else:
                summary_list_sales = []
                for emp_name in employee_users:
                    emp_current_goal = goals_df[(goals_df["Username"].astype(str) == str(emp_name)) & (goals_df["MonthYear"].astype(str) == str(current_quarter_for_display))]
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
                    num_cols_sales = 3 
                    cols_sales = st.columns(num_cols_sales)
                    col_idx_sales = 0

                    for index, row in summary_df_sales.iterrows():
                        progress_percent = (row['Achieved'] / row['Target'] * 100) if row['Target'] > 0 else 0
                        # Use actual hex for Matplotlib if var() not working directly
                        donut_fig = create_donut_chart(progress_percent, achieved_color='#28a745') 
                        
                        current_col_sales = cols_sales[col_idx_sales % num_cols_sales]
                        with current_col_sales:
                            st.markdown(f"""
                            <div class="employee-progress-item">
                                <h6>{row['Employee']}</h6>
                                <p>Target: ₹{row['Target']:,.0f}<br>Achieved: ₹{row['Achieved']:,.0f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.pyplot(donut_fig, use_container_width=True)
                            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True) 
                        col_idx_sales += 1
                    
                    st.markdown("<hr style='margin-top: 10px; margin-bottom:25px;'>", unsafe_allow_html=True)

                    st.markdown("<h6>Overall Team Sales Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_sales = create_team_progress_bar_chart(summary_df_sales, title="Team Sales Target vs. Achieved", target_col="Target", achieved_col="Achieved")
                    if team_bar_fig_sales:
                        st.pyplot(team_bar_fig_sales, use_container_width=True)
                    else:
                        st.info("No sales data to plot for the team bar chart.")
                else:
                    st.info(f"No sales goals data found for {current_quarter_for_display} to display team progress.")

        elif admin_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set or Update Employee Goal ({TARGET_GOAL_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options = [u for u, d in USERS.items() if d["role"] == "employee"]
            if not employee_options: st.warning("No employees available to set goals for.")
            else:
                selected_emp = st.radio("Select Employee:", employee_options, key="goal_emp_radio_2025_q", horizontal=True)
                quarter_options = [f"{TARGET_GOAL_YEAR}-Q{i}" for i in range(1, 5)]
                selected_period = st.radio("Goal Period:", quarter_options, key="goal_period_radio_2025_q", horizontal=True)
                existing_g = goals_df[(goals_df["Username"].astype(str) == str(selected_emp)) & (goals_df["MonthYear"].astype(str) == str(selected_period))]
                g_desc, g_target, g_achieved, g_status = "", 0.0, 0.0, "Not Started"
                if not existing_g.empty:
                    g_data = existing_g.iloc[0]
                    g_desc = g_data.get("GoalDescription", ""); g_target = float(pd.to_numeric(g_data.get("TargetAmount", 0.0), errors='coerce') or 0.0)
                    g_achieved = float(pd.to_numeric(g_data.get("AchievedAmount", 0.0), errors='coerce') or 0.0); g_status = g_data.get("Status", "Not Started")
                    st.info(f"Editing existing goal for {selected_emp} - {selected_period}")
                with st.form(key=f"set_goal_form_{selected_emp}_{selected_period}_2025q"):
                    new_desc = st.text_area("Goal Description", value=g_desc); new_target = st.number_input("Target Sales (INR)", value=g_target, min_value=0.0, step=1000.0, format="%.2f")
                    new_achieved = st.number_input("Achieved Sales (INR)", value=g_achieved, min_value=0.0, step=100.0, format="%.2f"); new_status = st.radio("Status:", status_options, index=status_options.index(g_status), horizontal=True)
                    submitted = st.form_submit_button("Save Goal")
                if submitted:
                    if not new_desc.strip(): st.warning("Description is required.")
                    elif new_target <= 0 and new_status not in ["Cancelled", "On Hold", "Not Started"]: st.warning("Target must be > 0 unless status is Cancelled/On Hold/Not Started.")
                    else:
                        if not existing_g.empty:
                            goals_df.loc[existing_g.index[0]] = [selected_emp, selected_period, new_desc, new_target, new_achieved, new_status]; msg_verb = "updated"
                        else:
                            new_row = {"Username": selected_emp, "MonthYear": selected_period, "GoalDescription": new_desc, "TargetAmount": new_target, "AchievedAmount": new_achieved, "Status": new_status}
                            for col in GOALS_COLUMNS: new_row.setdefault(col, pd.NA) 
                            goals_df = pd.concat([goals_df, pd.DataFrame([new_row], columns=GOALS_COLUMNS)], ignore_index=True); msg_verb = "set"
                        try: goals_df.to_csv(GOALS_FILE, index=False); st.success(f"Goal for {selected_emp} ({selected_period}) {msg_verb}!"); st.rerun()
                        except Exception as e: st.error(f"Error saving goal: {e}")
    else: 
        st.markdown("<h4>My Sales Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        my_goals = goals_df[goals_df["Username"].astype(str) == str(current_user["username"])].copy()
        for col in ["TargetAmount", "AchievedAmount"]: my_goals[col] = pd.to_numeric(my_goals[col], errors="coerce").fillna(0.0)
        current_g = my_goals[my_goals["MonthYear"] == current_quarter_for_display]
        st.markdown(f"<h5>Current Goal Period: {current_quarter_for_display}</h5>", unsafe_allow_html=True)

        if not current_g.empty:
            g = current_g.iloc[0]
            target_amt = g["TargetAmount"]; achieved_amt = g["AchievedAmount"]
            st.markdown(f"**Description:** {g.get('GoalDescription', 'N/A')}")
            col_metrics_sales, col_chart_sales = st.columns([0.63, 0.37]) 
            with col_metrics_sales:
                sub_col1, sub_col2 = st.columns(2)
                sub_col1.metric("Target", f"₹{target_amt:,.0f}")
                sub_col2.metric("Achieved", f"₹{achieved_amt:,.0f}")
                st.metric("Status", g.get("Status", "In Progress"), label_visibility="labeled")
            with col_chart_sales:
                progress_percent_sales = (achieved_amt / target_amt * 100) if target_amt > 0 else 0.0
                st.markdown(f"<h6 style='text-align: center; margin-bottom: 0px; margin-top: -15px;'>Sales Progress</h6>", unsafe_allow_html=True)
                donut_fig_sales = create_donut_chart(progress_percent_sales, "Sales Progress", achieved_color='#28a745')
                st.pyplot(donut_fig_sales, use_container_width=True)
            st.markdown("---") 
            with st.form(key=f"update_achievement_{current_user['username']}_{current_quarter_for_display}"):
                new_val = st.number_input("Update Achieved Amount (INR):", value=achieved_amt, min_value=0.0, step=100.0, format="%.2f")
                submitted = st.form_submit_button("Update Achievement")
            if submitted:
                idx = current_g.index[0]
                goals_df.loc[idx, "AchievedAmount"] = new_val
                new_status = "Achieved" if new_val >= target_amt and target_amt > 0 else "In Progress"
                goals_df.loc[idx, "Status"] = new_status
                try: goals_df.to_csv(GOALS_FILE, index=False); st.success("Achievement updated!"); st.rerun()
                except Exception as e: st.error(f"Error saving update: {e}")
        else: st.info(f"No goal set for {current_quarter_for_display}. Contact your admin.")
        st.markdown("---")
        st.markdown("<h5>My Past Goals (2025)</h5>", unsafe_allow_html=True)
        past_goals = my_goals[(my_goals["MonthYear"].astype(str).str.startswith(str(TARGET_GOAL_YEAR))) & (my_goals["MonthYear"].astype(str) != current_quarter_for_display)]
        if not past_goals.empty:
            render_goal_chart(past_goals, "Past Sales Goal Performance") 
        else: st.info(f"No past goal records found for {TARGET_GOAL_YEAR}.")
    st.markdown("</div>", unsafe_allow_html=True)


elif nav == "💰 Payment Collection Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)

    TARGET_YEAR_PAYMENT = 2025 
    current_quarter_display_payment = get_quarter_str_for_year(TARGET_YEAR_PAYMENT, for_current_display=True)
    status_options_payment = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Set & Track Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action_payment = st.radio("Action:", ["View Team Progress", f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}"], key="admin_payment_action_2025", horizontal=True)
        if admin_action_payment == "View Team Progress":
            st.markdown(f"<h5>Team Payment Collection Progress for {current_quarter_display_payment}</h5>", unsafe_allow_html=True)
            employees_payment_list = [u for u, d in USERS.items() if d["role"] == "employee"]
            if not employees_payment_list: st.info("No employees found.")
            else:
                summary_list_payment = []
                for emp_pay_name in employees_payment_list:
                    record_payment = payment_goals_df[(payment_goals_df["Username"] == emp_pay_name) & (payment_goals_df["MonthYear"] == current_quarter_display_payment)]
                    target_p, achieved_p, status_p = 0.0, 0.0, "Not Set"
                    if not record_payment.empty:
                        rec_payment = record_payment.iloc[0]
                        target_p = float(pd.to_numeric(rec_payment["TargetAmount"], errors="coerce") or 0.0)
                        achieved_p = float(pd.to_numeric(rec_payment["AchievedAmount"], errors="coerce") or 0.0)
                        status_p = rec_payment.get("Status", "N/A")
                    summary_list_payment.append({"Employee": emp_pay_name, "Target": target_p, "Achieved": achieved_p, "Status": status_p})
                
                summary_df_payment = pd.DataFrame(summary_list_payment)

                if not summary_df_payment.empty:
                    st.markdown("<h6>Individual Collection Progress:</h6>", unsafe_allow_html=True)
                    num_cols_payment = 3
                    cols_payment = st.columns(num_cols_payment)
                    col_idx_payment = 0

                    for index, row in summary_df_payment.iterrows():
                        progress_percent_p = (row['Achieved'] / row['Target'] * 100) if row['Target'] > 0 else 0
                        donut_fig_p = create_donut_chart(progress_percent_p, achieved_color='#2070c0') # Blue
                        
                        current_col_p = cols_payment[col_idx_payment % num_cols_payment]
                        with current_col_p:
                            st.markdown(f"""
                            <div class="employee-progress-item">
                                <h6>{row['Employee']}</h6>
                                <p>Target: ₹{row['Target']:,.0f}<br>Collected: ₹{row['Achieved']:,.0f}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            st.pyplot(donut_fig_p, use_container_width=True)
                            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True) 
                        col_idx_payment += 1
                    
                    st.markdown("<hr style='margin-top: 10px; margin-bottom:25px;'>", unsafe_allow_html=True)

                    st.markdown("<h6>Overall Team Collection Performance:</h6>", unsafe_allow_html=True)
                    # For payment, let's use the secondary color for "Achieved" in the bar chart too
                    team_bar_fig_payment = create_team_progress_bar_chart(summary_df_payment, title="Team Collection Target vs. Achieved", target_col="Target", achieved_col="Achieved")
                    if team_bar_fig_payment:
                         # Modify colors for payment bar chart if desired
                        for bar_group in team_bar_fig_payment.axes[0].containers:
                            if bar_group.get_label() == 'Achieved':
                                for bar in bar_group:
                                    bar.set_color('#2070c0') # Blue for achieved payments
                        st.pyplot(team_bar_fig_payment, use_container_width=True)
                    else:
                        st.info("No collection data to plot for the team bar chart.")
                else:
                    st.info(f"No payment collection data found for {current_quarter_display_payment} to display team progress.")

        elif admin_action_payment == f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}":
            st.markdown(f"<h5>Set or Update Collection Goal ({TARGET_YEAR_PAYMENT} - Quarterly)</h5>", unsafe_allow_html=True)
            employees_for_payment_goal = [u for u, d in USERS.items() if d["role"] == "employee"]
            selected_emp_payment = st.radio("Select Employee:", employees_for_payment_goal, key="payment_emp_radio_2025", horizontal=True)
            quarters_payment = [f"{TARGET_YEAR_PAYMENT}-Q{i}" for i in range(1, 5)]
            selected_period_payment = st.radio("Quarter:", quarters_payment, key="payment_period_radio_2025", horizontal=True)
            existing_payment_goal = payment_goals_df[(payment_goals_df["Username"] == selected_emp_payment) & (payment_goals_df["MonthYear"] == selected_period_payment)]
            desc_payment, tgt_payment_val, ach_payment_val, stat_payment = "", 0.0, 0.0, "Not Started"
            if not existing_payment_goal.empty:
                g_payment = existing_payment_goal.iloc[0]
                desc_payment = g_payment.get("GoalDescription", ""); tgt_payment_val = float(pd.to_numeric(g_payment.get("TargetAmount", 0.0), errors='coerce') or 0.0)
                ach_payment_val = float(pd.to_numeric(g_payment.get("AchievedAmount", 0.0), errors='coerce') or 0.0); stat_payment = g_payment.get("Status", "Not Started")
            with st.form(f"form_payment_{selected_emp_payment}_{selected_period_payment}"): 
                new_desc_payment = st.text_input("Collection Goal Description", value=desc_payment); new_tgt_payment = st.number_input("Target Collection (INR)", value=tgt_payment_val, min_value=0.0, step=1000.0)
                new_ach_payment = st.number_input("Collected Amount (INR)", value=ach_payment_val, min_value=0.0, step=500.0); new_status_payment = st.selectbox("Status", status_options_payment, index=status_options_payment.index(stat_payment))
                submitted_payment = st.form_submit_button("Save Goal")
            if submitted_payment:
                if not new_desc_payment.strip(): st.warning("Goal description is required.")
                elif new_tgt_payment <= 0 and new_status_payment not in ["Cancelled", "Not Started"]: st.warning("Target must be greater than 0.")
                else:
                    if not existing_payment_goal.empty:
                        payment_goals_df.loc[existing_payment_goal.index[0]] = [selected_emp_payment, selected_period_payment, new_desc_payment, new_tgt_payment, new_ach_payment, new_status_payment]; msg_payment = "updated"
                    else:
                        new_row_payment = {"Username": selected_emp_payment, "MonthYear": selected_period_payment, "GoalDescription": new_desc_payment, "TargetAmount": new_tgt_payment, "AchievedAmount": new_ach_payment, "Status": new_status_payment}
                        for col in PAYMENT_GOALS_COLUMNS: new_row_payment.setdefault(col, pd.NA)
                        payment_goals_df = pd.concat([payment_goals_df, pd.DataFrame([new_row_payment], columns=PAYMENT_GOALS_COLUMNS)], ignore_index=True); msg_payment = "set"
                    try: payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False); st.success(f"Payment goal {msg_payment} for {selected_emp_payment} ({selected_period_payment})"); st.rerun()
                    except Exception as e: st.error(f"Error saving payment data: {e}")
    else: 
        st.markdown("<h4>My Payment Collection Goals (2025)</h4>", unsafe_allow_html=True)
        user_goals_payment = payment_goals_df[payment_goals_df["Username"] == current_user["username"]].copy()
        user_goals_payment[["TargetAmount", "AchievedAmount"]] = user_goals_payment[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        current_payment_goal_period = user_goals_payment[user_goals_payment["MonthYear"] == current_quarter_display_payment]
        st.markdown(f"<h5>Current Quarter: {current_quarter_display_payment}</h5>", unsafe_allow_html=True)

        if not current_payment_goal_period.empty:
            g_pay = current_payment_goal_period.iloc[0]
            tgt_pay = g_pay["TargetAmount"]; ach_pay = g_pay["AchievedAmount"]
            st.markdown(f"**Goal:** {g_pay.get('GoalDescription', '')}")
            col_metrics_pay, col_chart_pay = st.columns([0.63, 0.37]) 
            with col_metrics_pay:
                sub_col1_pay, sub_col2_pay = st.columns(2)
                sub_col1_pay.metric("Target", f"₹{tgt_pay:,.0f}")
                sub_col2_pay.metric("Collected", f"₹{ach_pay:,.0f}")
                st.metric("Status", g_pay.get("Status", "In Progress"), label_visibility="labeled")
            with col_chart_pay:
                progress_percent_pay = (ach_pay / tgt_pay * 100) if tgt_pay > 0 else 0.0
                st.markdown(f"<h6 style='text-align: center; margin-bottom: 0px; margin-top: -15px;'>Collection Progress</h6>", unsafe_allow_html=True)
                donut_fig_payment = create_donut_chart(progress_percent_pay, "Collection Progress", achieved_color='#2070c0') # Blue
                st.pyplot(donut_fig_payment, use_container_width=True)
            st.markdown("---") 
            with st.form(key=f"update_collection_{current_user['username']}_{current_quarter_display_payment}"): 
                new_ach_val_payment = st.number_input("Update Collected Amount (INR):", value=ach_pay, min_value=0.0, step=500.0)
                submit_collection_update = st.form_submit_button("Update Collection")
            if submit_collection_update:
                idx_pay = current_payment_goal_period.index[0]
                payment_goals_df.loc[idx_pay, "AchievedAmount"] = new_ach_val_payment
                payment_goals_df.loc[idx_pay, "Status"] = "Achieved" if new_ach_val_payment >= tgt_pay and tgt_pay > 0 else "In Progress"
                try: payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False); st.success("Collection updated."); st.rerun()
                except Exception as e: st.error(f"Error saving collection update: {e}")
        else: st.info(f"No collection goal set for {current_quarter_display_payment}.")
        st.markdown("<h5>Past Quarters</h5>", unsafe_allow_html=True)
        past_payment_goals = user_goals_payment[user_goals_payment["MonthYear"] != current_quarter_display_payment]
        if not past_payment_goals.empty:
            render_goal_chart(past_payment_goals, "Past Collection Performance") 
        else: st.info("No past collection goals found.")
    st.markdown('</div>', unsafe_allow_html=True)


elif nav == "📊 View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 View Logs</h3>", unsafe_allow_html=True)
    
    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: View Employee Records</h4>", unsafe_allow_html=True)
        selected_employee_log = st.selectbox("Select Employee:", list(USERS.keys()), key="log_employee_select_admin") 
        
        st.markdown(f"<h5>Attendance for {selected_employee_log}</h5>", unsafe_allow_html=True)
        emp_attendance_log = attendance_df[attendance_df["Username"] == selected_employee_log]
        if not emp_attendance_log.empty: st.dataframe(emp_attendance_log, use_container_width=True)
        else: st.warning("No attendance records found")
            
        st.markdown(f"<h5>Allowances for {selected_employee_log}</h5>", unsafe_allow_html=True)
        emp_allowance_log = allowance_df[allowance_df["Username"] == selected_employee_log]
        if not emp_allowance_log.empty: st.dataframe(emp_allowance_log, use_container_width=True)
        else: st.warning("No allowance records found")

        st.markdown(f"<h5>Sales Goals for {selected_employee_log}</h5>", unsafe_allow_html=True)
        emp_goals_log = goals_df[goals_df["Username"] == selected_employee_log]
        if not emp_goals_log.empty: st.dataframe(emp_goals_log, use_container_width=True)
        else: st.warning("No sales goals records found")

        st.markdown(f"<h5>Payment Collection Goals for {selected_employee_log}</h5>", unsafe_allow_html=True)
        emp_payment_goals_log = payment_goals_df[payment_goals_df["Username"] == selected_employee_log]
        if not emp_payment_goals_log.empty: st.dataframe(emp_payment_goals_log, use_container_width=True)
        else: st.warning("No payment collection goals records found")
            
    else:  
        st.markdown("<h4>My Records</h4>", unsafe_allow_html=True)
        st.markdown("<h5>My Attendance</h5>", unsafe_allow_html=True)
        my_attendance_log = attendance_df[attendance_df["Username"] == current_user["username"]]
        if not my_attendance_log.empty: st.dataframe(my_attendance_log, use_container_width=True)
        else: st.warning("No attendance records found for you")
            
        st.markdown("<h5>My Allowances</h5>", unsafe_allow_html=True)
        my_allowance_log = allowance_df[allowance_df["Username"] == current_user["username"]]
        if not my_allowance_log.empty: st.dataframe(my_allowance_log, use_container_width=True)
        else: st.warning("No allowance records found for you")

        st.markdown("<h5>My Sales Goals</h5>", unsafe_allow_html=True)
        my_goals_log = goals_df[goals_df["Username"] == current_user["username"]]
        if not my_goals_log.empty: st.dataframe(my_goals_log, use_container_width=True)
        else: st.warning("No sales goals records found for you")

        st.markdown("<h5>My Payment Collection Goals</h5>", unsafe_allow_html=True)
        my_payment_goals_log = payment_goals_df[payment_goals_df["Username"] == current_user["username"]]
        if not my_payment_goals_log.empty: st.dataframe(my_payment_goals_log, use_container_width=True)
        else: st.warning("No payment collection goals records found for you")
    
    st.markdown('</div>', unsafe_allow_html=True)
