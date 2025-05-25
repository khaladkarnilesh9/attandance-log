import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import pytz
# import sys # Not used, can be removed
import altair as alt # Keep for existing past goals chart
import plotly.express as px # <--- ADD THIS IMPORT


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

# --- Function to render Altair bar chart (for past goals) ---
# --- Function to render Plotly Express grouped bar chart (for past goals) ---
def render_goal_chart(df: pd.DataFrame, chart_title: str): # Renamed title to chart_title for clarity
    if df.empty:
        st.warning("No data available to plot.")
        return

    df_chart = df.copy()
    # Ensure columns are numeric, coercing errors to NaN, then fill NaN with 0 for plotting
    df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)

    # Melt the DataFrame to long format, which is suitable for Plotly Express's color mapping
    df_melted = df_chart.melt(id_vars="MonthYear",
                              value_vars=["TargetAmount", "AchievedAmount"],
                              var_name="Metric",
                              value_name="Amount")

    if df_melted.empty:
        st.warning(f"No data to plot for {chart_title} after processing.")
        return

    fig = px.bar(df_melted,
                 x="MonthYear",
                 y="Amount",
                 color="Metric",
                 barmode="group",  # This creates side-by-side (parallel) bars
                 labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"},
                 title=chart_title,
                 color_discrete_map={ # Optional: customize colors
                     'TargetAmount': '#3498db',  # Blue
                     'AchievedAmount': '#2ecc71' # Green
                 }
                )

    fig.update_layout(
        height=400, # You can adjust the height
        xaxis_title="Quarter",
        yaxis_title="Amount (INR)",
        legend_title_text='Metric'
    )
    # To ensure labels like "2025-Q1" are not abbreviated if they are long
    fig.update_xaxes(type='category') 

    st.plotly_chart(fig, use_container_width=True)

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

html_css = """
html_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --primary-color: #1c4e80;
        --secondary-color: #2070c0;
        --accent-color: #70a1d7;
        --success-color: #28a745;
        --danger-color: #dc3545;
        --warning-color: #ffc107;
        --info-color: #17a2b8;

        --body-bg-color: #f4f6f9;
        --card-bg-color: #ffffff;
        --text-color: #343a40;
        --text-muted-color: #6c757d;
        --border-color: #dee2e6;
        --input-border-color: #ced4da;

        --font-family-sans-serif: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
        --border-radius: 0.375rem;
        --border-radius-lg: 0.5rem;
        --box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.075);
        --box-shadow-sm: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }

    body {
        font-family: var(--font-family-sans-serif);
        background-color: var(--body-bg-color);
        color: var(--text-color);
        line-height: 1.6;
        font-weight: 400;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--primary-color);
        font-weight: 600;
    }
    .main .block-container > div:first-child > div:first-child > div:first-child > h1 {
        text-align: center;
        font-size: 2.6em;
        font-weight: 700;
        padding-bottom: 25px;
        border-bottom: 3px solid var(--accent-color);
        margin-bottom: 40px;
        letter-spacing: -0.5px;
    }

    .card {
        background-color: var(--card-bg-color);
        padding: 30px;
        border-radius: var(--border-radius-lg);
        box-shadow: var(--box-shadow);
        margin-bottom: 35px;
        border: 1px solid var(--border-color);
    }
    .card h3 {
        margin-top: 0;
        color: var(--primary-color);
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 15px;
        margin-bottom: 25px;
        font-size: 1.75em;
    }
    .card h4 {
        color: var(--secondary-color);
        margin-top: 30px;
        margin-bottom: 20px;
        font-size: 1.4em;
        padding-bottom: 8px;
        border-bottom: 1px solid #e0e0e0;
    }
     .card h5 {
        font-size: 1.15em;
        color: var(--text-color);
        margin-top: 25px;
        margin-bottom: 12px;
    }
    .card h6 {
        font-size: 0.95em;
        color: var(--text-muted-color);
        margin-top: 0px;
        margin-bottom: 15px;
        font-weight: 500;
    }
    .form-field-label h6 {
        font-size: 1em;
        color: var(--text-muted-color);
        margin-top: 20px;
        margin-bottom: 10px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .login-container {
        max-width: 480px;
        margin: 60px auto;
        border-top: 5px solid var(--secondary-color);
    }
    .login-container .stButton button {
        width: 100%;
        background-color: var(--secondary-color) !important;
        color: white !important;
        font-size: 1.1em;
        padding: 12px 20px;
        border-radius: var(--border-radius);
        border: none !important;
        font-weight: 600 !important;
        box-shadow: var(--box-shadow-sm) !important;
    }
    .login-container .stButton button:hover {
        background-color: var(--primary-color) !important;
        color: white !important;
        box-shadow: var(--box-shadow) !important;
    }

    .stButton:not(.login-container .stButton) button {
        background-color: var(--success-color);
        color: white;
        padding: 10px 24px;
        border: none;
        border-radius: var(--border-radius);
        font-size: 1.05em;
        font-weight: 500;
        transition: background-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease;
        box-shadow: var(--box-shadow-sm);
        cursor: pointer;
    }
    .stButton:not(.login-container .stButton) button:hover {
        background-color: #218838;
        transform: translateY(-2px);
        box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1);
    }
    .stButton:not(.login-container .stButton) button:active {
        transform: translateY(0px);
        box-shadow: var(--box-shadow-sm);
    }
    .stButton button[id*="logout_button_sidebar"] {
        background-color: var(--danger-color) !important;
        border: 1px solid var(--danger-color) !important;
        color: white !important;
        font-weight: 500 !important;
    }
    .stButton button[id*="logout_button_sidebar"]:hover {
        background-color: #c82333 !important;
        border-color: #c82333 !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stDateInput input,
    .stTimeInput input,
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: var(--border-radius) !important;
        border: 1px solid var(--input-border-color) !important;
        padding: 10px 12px !important;
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
        min-height: 120px;
    }
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus,
    .stDateInput input:focus,
    .stTimeInput input:focus,
    .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border-color: var(--secondary-color) !important;
        box-shadow: 0 0 0 0.2rem rgba(32, 112, 192, 0.25) !important;
    }

    [data-testid="stSidebar"] {
        background-color: var(--primary-color);
        padding: 25px !important;
        box-shadow: 0.25rem 0 1rem rgba(0,0,0,0.1);
    }
    [data-testid="stSidebar"] .sidebar-content {
        padding-top: 10px;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] div:not([data-testid="stRadio"]) {
        color: #e9ecef !important;
    }
    [data-testid="stSidebar"] .stRadio > label > div > p {
        font-size: 1.05em !important;
        color: var(--accent-color) !important;
        padding: 0;
        margin: 0;
    }
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label > div > p {
        color: var(--card-bg-color) !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] .stRadio > label {
        padding: 10px 15px;
        border-radius: var(--border-radius);
        margin-bottom: 6px;
        transition: background-color 0.2s ease;
    }
    [data-testid="stSidebar"] .stRadio > label:hover {
        background-color: rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label {
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
        background-color: #e9ecef;
        color: var(--primary-color);
        font-weight: 600;
        text-align: left;
        padding: 14px 18px;
        border-bottom: 2px solid var(--border-color);
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stDataFrame table tbody td {
        padding: 12px 18px;
        border-bottom: 1px solid #f1f3f5;
        vertical-align: middle;
        color: var(--text-color);
        font-size: 0.9em;
    }
    .stDataFrame table tbody tr:last-child td {
        border-bottom: none;
    }
    .stDataFrame table tbody tr:hover {
        background-color: #f8f9fa;
    }
    .employee-progress-item {
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 15px;
        text-align: center;
        background-color: #fdfdfd;
        margin-bottom: 10px;
    }
    .employee-progress-item h6 {
        margin-top: 0;
        margin-bottom: 5px;
        font-size: 1em;
        color: var(--primary-color);
    }
    .employee-progress-item p {
        font-size: 0.85em;
        color: var(--text-muted-color);
        margin-bottom: 8px;
    }

    .button-column-container > div[data-testid="stHorizontalBlock"] {
        gap: 20px;
    }
    .button-column-container .stButton button {
        width: 100%;
    }

    div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 25px;
    }
    div[role="radiogroup"] > label {
        background-color: #668fb8;
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
        background-color: #295a8c;
        border-color: #adb5bd;
        color: var(--text-color);
    }
    div[role="radiogroup"] div[data-baseweb="radio"][aria-checked="true"] + label {
        background-color: var(--secondary-color) !important;
        color: white !important;
        border-color: var(--secondary-color) !important;
        font-weight: 500;
    }

    .employee-section-header {
        color: var(--secondary-color); margin-top: 30px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; font-size: 1.35em;
    }
    .record-type-header {
        font-size: 1.2em; color: var(--text-color); margin-top: 25px; margin-bottom: 12px; font-weight: 600;
    }

    div[data-testid="stImage"] > img {
        border-radius: var(--border-radius-lg);
        border: 1px solid var(--border-color);
        box-shadow: var(--box-shadow-sm);
    }
    .stProgress > div > div {
        background-color: var(--secondary-color) !important;
        border-radius: var(--border-radius);
    }
    .stProgress {
        border-radius: var(--border-radius);
        background-color: #e9ecef;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.95em !important;
        color: var(--text-muted-color) !important;
        font-weight: 500;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8em !important;
        font-weight: 600;
        color: var(--primary-color);
    }

    .custom-notification {
        padding: 15px 20px;
        border-radius: var(--border-radius);
        margin-bottom: 20px;
        font-size: 1em;
        border-left-width: 5px;
        border-left-style: solid;
        display: flex;
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

    .badge {
        display: inline-block;
        padding: 0.35em 0.65em;
        font-size: 0.85em;
        font-weight: 600;
        line-height: 1;
        color: #fff;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: var(--border-radius);
    }
    .badge.green { background-color: var(--success-color); }
    .badge.red { background-color: var(--danger-color); }
    .badge.orange { background-color: var(--warning-color); }
    .badge.blue { background-color: var(--secondary-color); }
    .badge.grey { background-color: var(--text-muted-color); }

</style>
"""
# --- (The rest of your Python script from the USERS dictionary onwards) ---
st.markdown(html_css, unsafe_allow_html=True)

# --- Credentials & User Info ---
USERS = {
    "Geetali": {"password": "Geetali123", "role": "employee", "position": "Software Engineer", "profile_photo": "images/geetali.png"},
    "Nilesh": {"password": "Nilesh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "Vishal": {"password": "Vishal123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "Santosh": {"password": "Santosh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "Deepak": {"password": "Deepak123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "Rahul": {"password": "Rahul123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
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

# ... (Keep all existing imports and function definitions) ...

# --- Load or create data ---
# (load_data function remains the same)

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]

# --- Load DataFrames globally at the start of the script execution ---
# These will be updated if changes are made and saved
attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS) # Initial load
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS) # Initial load

# ... (Rest of the initial setup: Session State, Login Page) ...

# --- Main Application ---
st.title("👨‍💼 HR Dashboard")
current_user = st.session_state.auth

# --- Dedicated Message Placeholder for Main App ---
# ... (message placeholder logic) ...

# --- Sidebar ---
# ... (sidebar logic) ...

# --- Main Content Area ---
# ... (Attendance and Allowance sections remain the same) ...

elif nav == "🎯 Goal Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)

    TARGET_GOAL_YEAR = 2025
    current_quarter_for_display = get_quarter_str_for_year(TARGET_GOAL_YEAR, for_current_display=True)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    # Make goals_df accessible and modifiable within this scope
    global goals_df # Declare that we intend to modify the global goals_df

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio(
            "Action:",
            ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR}"],
            key="admin_goal_action_radio_2025_q",
            horizontal=True
        )
        if admin_action == "View Team Progress":
            # This view will now use the potentially updated global goals_df
            # ... (existing View Team Progress logic using goals_df)
            st.markdown(f"<h5>Team Goal Progress for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            employee_users = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users: st.info("No employees found.")
            else:
                summary_list_sales = []
                # Use the global goals_df which should be up-to-date
                current_goals_df = goals_df 
                for emp_name in employee_users:
                    emp_current_goal = current_goals_df[(current_goals_df["Username"].astype(str) == str(emp_name)) & (current_goals_df["MonthYear"].astype(str) == str(current_quarter_for_display))]
                    # ... (rest of summary_list_sales population)
                    target, achieved, status_val = 0.0, 0.0, "Not Set"
                    if not emp_current_goal.empty:
                        g_data = emp_current_goal.iloc[0]
                        target = float(pd.to_numeric(g_data.get("TargetAmount"), errors='coerce') or 0.0)
                        achieved = float(pd.to_numeric(g_data.get("AchievedAmount", 0.0), errors='coerce') or 0.0)
                        status_val = g_data.get("Status", "N/A")
                    summary_list_sales.append({"Employee": emp_name, "Target": target, "Achieved": achieved, "Status": status_val})

                summary_df_sales = pd.DataFrame(summary_list_sales)
                # ... (rest of displaying charts for admin)

        elif admin_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set or Update Employee Goal ({TARGET_GOAL_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options = [u for u, d in USERS.items() if d["role"] == "employee"]
            if not employee_options: st.warning("No employees available to set goals for.")
            else:
                selected_emp = st.radio("Select Employee:", employee_options, key="goal_emp_radio_2025_q_admin_set", horizontal=True) # Ensure unique key
                quarter_options = [f"{TARGET_GOAL_YEAR}-Q{i}" for i in range(1, 5)]
                selected_period = st.radio("Goal Period:", quarter_options, key="goal_period_radio_2025_q_admin_set", horizontal=True) # Ensure unique key
                
                # Use a temporary copy for finding existing goal to avoid modifying global df prematurely
                temp_goals_df = goals_df.copy()
                existing_g = temp_goals_df[(temp_goals_df["Username"].astype(str) == str(selected_emp)) & (temp_goals_df["MonthYear"].astype(str) == str(selected_period))]
                
                g_desc, g_target, g_achieved, g_status = "", 0.0, 0.0, "Not Started"
                if not existing_g.empty:
                    g_data = existing_g.iloc[0]
                    g_desc = g_data.get("GoalDescription", ""); 
                    g_target = float(pd.to_numeric(g_data.get("TargetAmount", 0.0), errors='coerce') or 0.0)
                    g_achieved = float(pd.to_numeric(g_data.get("AchievedAmount", 0.0), errors='coerce') or 0.0); 
                    g_status = g_data.get("Status", "Not Started")
                    st.info(f"Editing existing goal for {selected_emp} - {selected_period}")

                with st.form(key=f"set_goal_form_{selected_emp}_{selected_period}_2025q_admin"): # Ensure unique key
                    new_desc = st.text_area("Goal Description", value=g_desc, key=f"desc_{selected_emp}_{selected_period}")
                    new_target = st.number_input("Target Sales (INR)", value=g_target, min_value=0.0, step=1000.0, format="%.2f", key=f"target_{selected_emp}_{selected_period}")
                    new_achieved = st.number_input("Achieved Sales (INR)", value=g_achieved, min_value=0.0, step=100.0, format="%.2f", key=f"achieved_{selected_emp}_{selected_period}") # Admin can set achieved
                    new_status = st.radio("Status:", status_options, index=status_options.index(g_status), horizontal=True, key=f"status_{selected_emp}_{selected_period}")
                    submitted = st.form_submit_button("Save Goal")

                if submitted:
                    if not new_desc.strip(): st.warning("Description is required.")
                    elif new_target <= 0 and new_status not in ["Cancelled", "On Hold", "Not Started"]: st.warning("Target must be > 0 unless status is Cancelled/On Hold/Not Started.")
                    else:
                        # Create a mutable copy of the global DataFrame for modification
                        editable_goals_df = goals_df.copy()
                        existing_g_indices = editable_goals_df[
                            (editable_goals_df["Username"].astype(str) == str(selected_emp)) &
                            (editable_goals_df["MonthYear"].astype(str) == str(selected_period))
                        ].index

                        if not existing_g_indices.empty:
                            # Update existing row
                            editable_goals_df.loc[existing_g_indices[0]] = [selected_emp, selected_period, new_desc, new_target, new_achieved, new_status]
                            msg_verb = "updated"
                        else:
                            # Add new row
                            new_row_data = {
                                "Username": selected_emp, "MonthYear": selected_period,
                                "GoalDescription": new_desc, "TargetAmount": new_target,
                                "AchievedAmount": new_achieved, "Status": new_status
                            }
                            # Ensure all columns are present, filling missing with pd.NA
                            for col_name in GOALS_COLUMNS:
                                if col_name not in new_row_data:
                                    new_row_data[col_name] = pd.NA
                            
                            new_row_df = pd.DataFrame([new_row_data], columns=GOALS_COLUMNS)
                            editable_goals_df = pd.concat([editable_goals_df, new_row_df], ignore_index=True)
                            msg_verb = "set"
                        
                        try:
                            editable_goals_df.to_csv(GOALS_FILE, index=False)
                            # *** IMPORTANT: Re-assign the global DataFrame ***
                            goals_df = load_data(GOALS_FILE, GOALS_COLUMNS) 
                            st.session_state.user_message = f"Goal for {selected_emp} ({selected_period}) {msg_verb}!"
                            st.session_state.message_type = "success"
                            st.rerun() 
                        except Exception as e: 
                            st.error(f"Error saving goal: {e}")
    else: # Employee View for Sales Goals
        # This view will now use the potentially updated global goals_df
        # ... (existing Employee View logic using goals_df)
        st.markdown("<h4>My Sales Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        # Use the global goals_df which should be up-to-date
        my_goals = goals_df[goals_df["Username"].astype(str) == str(current_user["username"])].copy()
        # ... (rest of employee goal display and update logic)


    st.markdown("</div>", unsafe_allow_html=True)


elif nav == "💰 Payment Collection Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)

    TARGET_YEAR_PAYMENT = 2025
    current_quarter_display_payment = get_quarter_str_for_year(TARGET_YEAR_PAYMENT, for_current_display=True)
    status_options_payment = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    # Make payment_goals_df accessible and modifiable
    global payment_goals_df # Declare we intend to modify global payment_goals_df

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Set & Track Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action_payment = st.radio("Action:", ["View Team Progress", f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}"], key="admin_payment_action_2025_admin_set", horizontal=True) # Unique key
        if admin_action_payment == "View Team Progress":
            # This view will now use the potentially updated global payment_goals_df
            # ... (existing View Team Progress logic using payment_goals_df)
            st.markdown(f"<h5>Team Payment Collection Progress for {current_quarter_display_payment}</h5>", unsafe_allow_html=True)
            employees_payment_list = [u for u, d in USERS.items() if d["role"] == "employee"]
            if not employees_payment_list: st.info("No employees found.")
            else:
                summary_list_payment = []
                current_payment_df = payment_goals_df # Use the global, potentially updated df
                for emp_pay_name in employees_payment_list:
                    record_payment = current_payment_df[(current_payment_df["Username"] == emp_pay_name) & (current_payment_df["MonthYear"] == current_quarter_display_payment)]
                    # ... (rest of summary_list_payment population)
                    target_p, achieved_p, status_p = 0.0, 0.0, "Not Set"
                    if not record_payment.empty:
                        rec_payment = record_payment.iloc[0]
                        target_p = float(pd.to_numeric(rec_payment["TargetAmount"], errors="coerce") or 0.0)
                        achieved_p = float(pd.to_numeric(rec_payment["AchievedAmount"], errors="coerce") or 0.0)
                        status_p = rec_payment.get("Status", "N/A")
                    summary_list_payment.append({"Employee": emp_pay_name, "Target": target_p, "Achieved": achieved_p, "Status": status_p})
                
                summary_df_payment = pd.DataFrame(summary_list_payment)
                # ... (rest of displaying charts for admin)

        elif admin_action_payment == f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}":
            st.markdown(f"<h5>Set or Update Collection Goal ({TARGET_YEAR_PAYMENT} - Quarterly)</h5>", unsafe_allow_html=True)
            employees_for_payment_goal = [u for u, d in USERS.items() if d["role"] == "employee"]
            selected_emp_payment = st.radio("Select Employee:", employees_for_payment_goal, key="payment_emp_radio_2025_admin_set", horizontal=True) # Unique key
            quarters_payment = [f"{TARGET_YEAR_PAYMENT}-Q{i}" for i in range(1, 5)]
            selected_period_payment = st.radio("Quarter:", quarters_payment, key="payment_period_radio_2025_admin_set", horizontal=True) # Unique key
            
            temp_payment_goals_df = payment_goals_df.copy()
            existing_payment_goal = temp_payment_goals_df[
                (temp_payment_goals_df["Username"] == selected_emp_payment) &
                (temp_payment_goals_df["MonthYear"] == selected_period_payment)
            ]
            desc_payment, tgt_payment_val, ach_payment_val, stat_payment = "", 0.0, 0.0, "Not Started"
            if not existing_payment_goal.empty:
                g_payment = existing_payment_goal.iloc[0]
                desc_payment = g_payment.get("GoalDescription", ""); 
                tgt_payment_val = float(pd.to_numeric(g_payment.get("TargetAmount", 0.0), errors="coerce") or 0.0)
                ach_payment_val = float(pd.to_numeric(g_payment.get("AchievedAmount", 0.0), errors="coerce") or 0.0); 
                stat_payment = g_payment.get("Status", "Not Started")

            with st.form(f"form_payment_{selected_emp_payment}_{selected_period_payment}_admin"): # Unique key
                new_desc_payment = st.text_input("Collection Goal Description", value=desc_payment, key=f"desc_pay_{selected_emp_payment}_{selected_period_payment}")
                new_tgt_payment = st.number_input("Target Collection (INR)", value=tgt_payment_val, min_value=0.0, step=1000.0, key=f"target_pay_{selected_emp_payment}_{selected_period_payment}")
                new_ach_payment = st.number_input("Collected Amount (INR)", value=ach_payment_val, min_value=0.0, step=500.0, key=f"achieved_pay_{selected_emp_payment}_{selected_period_payment}") # Admin can set achieved
                new_status_payment = st.selectbox("Status", status_options_payment, index=status_options_payment.index(stat_payment), key=f"status_pay_{selected_emp_payment}_{selected_period_payment}")
                submitted_payment = st.form_submit_button("Save Goal")

            if submitted_payment:
                if not new_desc_payment.strip(): st.warning("Goal description is required.")
                elif new_tgt_payment <= 0 and new_status_payment not in ["Cancelled", "Not Started"]: st.warning("Target must be greater than 0.")
                else:
                    editable_payment_goals_df = payment_goals_df.copy()
                    existing_pg_indices = editable_payment_goals_df[
                        (editable_payment_goals_df["Username"] == selected_emp_payment) &
                        (editable_payment_goals_df["MonthYear"] == selected_period_payment)
                    ].index

                    if not existing_pg_indices.empty:
                        editable_payment_goals_df.loc[existing_pg_indices[0]] = [selected_emp_payment, selected_period_payment, new_desc_payment, new_tgt_payment, new_ach_payment, new_status_payment]
                        msg_payment = "updated"
                    else:
                        new_row_data_p = {
                            "Username": selected_emp_payment, "MonthYear": selected_period_payment,
                            "GoalDescription": new_desc_payment, "TargetAmount": new_tgt_payment,
                            "AchievedAmount": new_ach_payment, "Status": new_status_payment
                        }
                        for col_name in PAYMENT_GOALS_COLUMNS:
                            if col_name not in new_row_data_p:
                                new_row_data_p[col_name] = pd.NA
                        
                        new_row_df_p = pd.DataFrame([new_row_data_p], columns=PAYMENT_GOALS_COLUMNS)
                        editable_payment_goals_df = pd.concat([editable_payment_goals_df, new_row_df_p], ignore_index=True)
                        msg_payment = "set"
                    
                    try:
                        editable_payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                        # *** IMPORTANT: Re-assign the global DataFrame ***
                        payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
                        st.session_state.user_message = f"Payment goal {msg_payment} for {selected_emp_payment} ({selected_period_payment})"
                        st.session_state.message_type = "success"
                        st.rerun()
                    except Exception as e: 
                        st.error(f"Error saving payment data: {e}")
    else: # Employee side for payment collection
        # This view will now use the potentially updated global payment_goals_df
        # ... (existing Employee View logic using payment_goals_df)
        st.markdown("<h4>My Payment Collection Goals (2025)</h4>", unsafe_allow_html=True)
        user_goals_payment = payment_goals_df[payment_goals_df["Username"] == current_user["username"]].copy()
        # ... (rest of employee payment goal display and update logic)

    st.markdown('</div>', unsafe_allow_html=True)

# ... (View Logs section remains the same) ...


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
