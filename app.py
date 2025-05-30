import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import os
import pytz
import plotly.express as px
import numpy as np
import matplotlib
matplotlib.use('Agg') # Use Agg backend for non-interactive plotting
import matplotlib.pyplot as plt

# --- Pillow for placeholder image generation ---
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# --- Page Configuration (MUST be the first Streamlit command) ---
st.set_page_config(
    page_title="Employee Portal - AI Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Global CSS Styling (Google AI Dashboard Inspired Theme) ---
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* Define Google AI Dashboard inspired color palette using CSS variables */
    :root {
        --primary-bg: #202124; /* Dark background */
        --secondary-bg: #2c2e30; /* Slightly lighter dark for cards/sidebar */
        --text-color: #e8eaed; /* Light text */
        --accent-blue: #8ab4f8; /* Google blue accent */
        --border-color: #3c4043; /* Subtle border for cards/inputs */
        --shadow-color: rgba(0, 0, 0, 0.4); /* Dark shadow */
        --success-color: #2ecc71; /* Green for success */
        --error-color: #e74c3c; /* Red for error */
        --warning-color: #f39c12; /* Orange for warning */
        --info-color: #3498db; /* Blue for info */
    }

    /* Global Styles & Resets */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stVerticalBlock"] {
        height: 100%;
        margin: 0;
        padding: 0;
        font-family: 'Roboto', sans-serif; /* Apply Roboto font globally */
        color: var(--text-color); /* Default text color */
    }

    .stApp {
        background-color: var(--primary-bg); /* Main app background */
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
        background-color: var(--secondary-bg); /* Darker background for inputs */
        color: var(--text-color); /* Light text for input values */
        border: 1px solid var(--border-color); /* Subtle border */
        border-radius: 8px; /* Rounded corners */
        padding: 10px 15px; /* More padding */
        font-size: 1rem; /* Standard font size */
        transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        box-shadow: none; /* Remove any default shadow */
    }

    /* Placeholder color */
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    .stNumberInput input::placeholder {
        color: #888; /* Slightly lighter grey for placeholder */
        opacity: 1; /* Ensure full visibility */
    }

    /* Focus styles for inputs */
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {
        border-color: var(--accent-blue); /* Accent blue on focus */
        box-shadow: 0 0 0 0.2rem rgba(138, 180, 248, 0.25); /* Subtle glow */
        outline: none; /* Remove default outline */
    }
    /* Selectbox focus (it's a bit different because of BaseWeb) */
    div[data-baseweb="select"] div[role="button"]:focus-within {
        border-color: var(--accent-blue);
        box-shadow: 0 0 0 0.2rem rgba(138, 180, 248, 0.25);
        outline: none;
    }

    /* Sidebar Styling (Navigation Bar Look & Feel) */
    [data-testid="stSidebar"] {
        background-color: var(--secondary-bg); /* Darker blue-grey for sidebar background */
        padding-top: 1rem;
        box-shadow: 2px 0 10px var(--shadow-color); /* More prominent shadow */
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
        background-color: var(--primary-bg); /* Darker background for profile box */
        border-radius: 10px; /* Rounded corners for the profile box */
        margin: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .user-profile-img {
        width: 90px; /* Slightly larger image */
        height: 90px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 0.75rem;
        border: 3px solid var(--accent-blue); /* Accent border color */
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .welcome-text {
        font-weight: 600;
        color: var(--text-color); /* White text for welcome */
        margin-bottom: 0.25rem;
        font-size: 1.2rem;
    }
    .user-position {
        font-size: 0.9rem;
        color: #bdc3c7; /* Lighter grey for position */
    }
    .divider {
        border-top: 1px solid var(--border-color); /* Lighter divider for contrast */
        margin: 0.5rem 0 1.5rem 0;
    }

    /* Navigation Items (Sidebar Buttons) - Targeting Streamlit's internal button structure */
    /* Target the button container */
    [data-testid="stSidebar"] .stButton > button {
        display: flex; /* Use flexbox to align icon and text */
        align-items: center; /* Vertically align items */
        justify-content: flex-start; /* Align icon and text to start */
        padding: 0.85rem 1.2rem; /* More padding for a bolder look */
        margin: 0.25rem 0.75rem; /* Space between buttons */
        border-radius: 8px;
        font-size: 1.05rem; /* Slightly larger font */
        font-weight: 500;
        transition: background-color 0.2s, color 0.2s, transform 0.1s, box-shadow 0.2s;
        width: calc(100% - 1.5rem); /* Account for margin left/right */
        
        background-color: transparent !important; /* Start transparent, override Streamlit defaults */
        border: none !important; /* No border, override Streamlit defaults */
        color: var(--text-color) !important; /* Light text color for inactive items, override */
        cursor: pointer; /* Indicate clickable */
        box-shadow: none !important; /* Remove default button shadow */
        outline: none !important; /* Remove focus outline */
    }

    /* Specific styling for the text within the button (Streamlit wraps it in a <p>) */
    [data-testid="stSidebar"] .stButton > button p {
        margin: 0; /* Remove default paragraph margin */
        padding: 0; /* Remove default paragraph padding */
        color: inherit; /* Inherit color from the button */
        font-weight: inherit; /* Inherit font-weight */
        line-height: 1; /* Ensure text sits correctly */
    }

    /* Hover state for sidebar nav items (buttons) */
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: var(--primary-bg) !important; /* Darker on hover */
        color: var(--accent-blue) !important; /* Accent blue on hover */
        transform: translateX(5px); /* Slight slide effect on hover */
    }

    /* Active state for sidebar nav items (buttons) - use a specific class added by Streamlit's key logic */
    /* We'll assign a custom class 'active-sidebar-nav-item' in Python for the active button */
    [data-testid="stSidebar"] .stButton > button.active-sidebar-nav-item {
        background-color: var(--primary-bg) !important; /* Darker for active */
        color: var(--accent-blue) !important; /* Accent blue for active */
        box-shadow: 0 4px 12px rgba(138, 180, 248, 0.1) !important; /* Subtle blue shadow */
        transform: translateX(0) !important; /* Ensure no slide for active */
    }

    /* Styling for the icon within the nav item (Streamlit wraps it in a span if you pass HTML) */
    [data-testid="stSidebar"] .stButton > button .material-symbols-outlined {
        margin-right: 0.8rem; /* More space for icon */
        font-size: 1.6rem; /* Slightly larger icon */
        width: 28px; height: 28px; /* Fixed size for icons */
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: inherit; /* Icon color inherits from button text color */
    }

    /* Logout button specific styling (push to bottom) */
    .logout-container {
        margin-top: auto; /* Pushes logout button to the very bottom of the sidebar */
        padding: 1rem;
        border-top: 1px solid var(--border-color); /* Divider line */
        background-color: var(--secondary-bg); /* Match sidebar background */
    }
    .logout-container .stButton > button { /* Direct target for logout button */
        background-color: var(--error-color) !important; /* Red for logout, use !important to override */
        color: white !important; /* White text */
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: background-color 0.2s, transform 0.1s !important;
        width: 100% !important; /* Make button full width */
        justify-content: center; /* Center content for logout button */
        /* Reset any specific sidebar button styles that might conflict */
        margin: 0 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    .logout-container .stButton > button:hover {
        background-color: #c0392b !important; /* Darker red on hover */
        transform: translateY(-2px) !important;
    }
    .logout-container .stButton > button:active {
        background-color: #a53026 !important;
        transform: translateY(0) !important;
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
        background-color: var(--secondary-bg); /* Card background matches sidebar */
        border-radius: 12px;
        padding: 2.5rem; /* More padding inside cards */
        box-shadow: 0 6px 20px var(--shadow-color); /* Stronger, softer shadow */
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color); /* Subtle border */
    }
    .card h3, .card h4, .card h5 {
        color: var(--accent-blue); /* Accent color for headings */
        margin-bottom: 1.5rem;
        font-weight: 700; /* Bolder headings */
    }
    /* General Streamlit button styling for content area buttons */
    .stButton > button { /* Target all Streamlit buttons */
        border-radius: 8px;
        font-weight: 600; /* Bolder button text */
        padding: 0.8rem 1.5rem; /* More padding for buttons */
        min-height: 45px; /* Ensure minimum height */
        transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.1s ease;
        color: var(--text-color); /* Reset text color */
        background-color: var(--primary-bg); /* Reset background color */
        border: 1px solid var(--border-color); /* Add border */
    }

    .stButton > button.primary {
        background-color: var(--accent-blue) !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button.primary:hover {
        background-color: #6a9df8 !important; /* Lighter blue on hover */
        transform: translateY(-2px);
    }
    .stButton > button[data-testid="baseButton-secondary"] {
        background-color: var(--secondary-bg) !important;
        color: var(--text-color) !important;
        border: 1px solid var(--border-color) !important;
    }
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        background-color: var(--primary-bg) !important;
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
        color: #b8e0d4; background-color: #1a4f32; border-color: #2e6b4e; /* Darker success */
    }
    .custom-notification.error {
        color: #f5c2c7; background-color: #6b1d24; border-color: #842029; /* Darker error */
    }
    .custom-notification.warning {
        color: #ffeeba; background-color: #664d03; border-color: #997300; /* Darker warning */
    }
    .custom-notification.info {
        color: #b6effb; background-color: #055160; border-color: #076d7e; /* Darker info */
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
        background-color: var(--border-color); /* Lighter background for empty progress bar */
        border-radius: 5px;
    }
    .stProgress > div > div > div {
        background-color: var(--success-color); /* Green for progress fill */
        border-radius: 5px;
    }

    /* Style for Plotly charts */
    .stPlotlyChart {
        border-radius: 12px;
        overflow: hidden; /* Ensure chart elements respect border-radius */
        box-shadow: 0 4px 15px var(--shadow-color); /* Consistent shadow */
        background-color: var(--secondary-bg); /* Chart background */
        padding: 1rem; /* Add some padding to chart container */
    }
    /* Ensure plotly text is visible on dark background */
    .js-plotly-plot .plotly .modebar-btn,
    .js-plotly-plot .plotly .legendtext,
    .js-plotly-plot .plotly .xtick,
    .js-plotly-plot .plotly .ytick,
    .js-plotly-plot .plotly .gtitle,
    .js-plotly-plot .plotly .g-xtick,
    .js-plotly-plot .plotly .g-ytick {
        fill: var(--text-color) !important;
        color: var(--text-color) !important;
    }
    .js-plotly-plot .plotly .infolayer .g-gtitle {
        fill: var(--accent-blue) !important;
    }
    .js-plotly-plot .plotly .g-gtitle text {
        fill: var(--accent-blue) !important;
    }


    /* Streamlit labels */
    div[data-testid="stWidgetLabel"] > p {
        font-weight: 500;
        color: var(--text-color); /* Labels should be light */
        margin-bottom: 0.5rem;
    }
    /* Specific targeting for radio/checkbox labels if needed */
    .stRadio > label, .stCheckbox > label {
        font-weight: 500;
        color: var(--text-color);
    }
    /* Radio button circles */
    .stRadio div[role="radio"] div[data-baseweb="radio"] div[data-testid="stDecoration"] {
        border-color: var(--accent-blue) !important;
    }
    .stRadio div[role="radio"] div[data-baseweb="radio"] div[data-testid="stDecoration"]::before {
        background-color: var(--accent-blue) !important;
    }
    
    /* Small adjustments for layout */
    /* Ensure text in main content is readable */
    .main-content-area p, .main-content-area li {
        color: var(--text-color);
    }
    
</style>
""", unsafe_allow_html=True)


# --- Credentials & User Info ---
USERS = {
    "Geetali": {"password": "password", "role": "employee", "position": "Software Engineer", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=GE"},
    "Nilesh": {"password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=NI"},
    "Vishal": {"password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=VI"},
    "Santosh": {"password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=SA"},
    "Deepak": {"password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=DE"},
    "Rahul": {"password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=RA"},
    "admin": {"password": "password", "role": "admin", "position": "System Administrator", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=AD"}
}

# --- Create dummy images folder (no longer strictly needed for profile_photo but good for activity_photos) ---
# Ensure the directory exists
if not os.path.exists("activity_photos"):
    os.makedirs("activity_photos", exist_ok=True)


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
        os.makedirs(dir_path, exist_ok=True)

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
def load_dataframe_from_csv(path, columns):
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
            return pd.DataFrame(columns=columns)
        except Exception as e:
            st.error(f"Error loading {path}: {e}. Returning empty DataFrame.")
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
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]

# --- Session State Initialization ---
# Initialize authentication state
if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}
    st.session_state.user_message = ""
    st.session_state.message_type = ""

# Initialize active_page here (crucial for preventing AttributeError)
if "active_page" not in st.session_state:
    st.session_state.active_page = "login" # Default landing page is login

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


# --- Charting Functions (As provided by you) ---
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
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric',
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', # Transparent background
                      font=dict(color=st.get_option("theme.textColor")), # Use Streamlit's theme color for text
                      title_font_color=st.get_option("theme.primaryColor")), # Use Streamlit's primary color for title
                      legend_font_color=st.get_option("theme.textColor"),
                      xaxis=dict(gridcolor='rgba(100,100,100,0.2)', zerolinecolor='rgba(100,100,100,0.2)'),
                      yaxis=dict(gridcolor='rgba(100,100,100,0.2)', zerolinecolor='rgba(100,100,100,0.2)'))
    fig.update_xaxes(type='category', showgrid=True, gridwidth=1, gridcolor=st.get_option("theme.secondaryBackgroundColor"))
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=st.get_option("theme.secondaryBackgroundColor"))
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
    ax.set_ylabel('Amount (INR)', fontsize=10, color=st.get_option("theme.textColor"));
    ax.set_title(title, fontsize=12, fontweight='bold', pad=15, color=st.get_option("theme.primaryColor"))
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9, color=st.get_option("theme.textColor"));
    ax.tick_params(axis='y', colors=st.get_option("theme.textColor")) # Y-axis ticks
    ax.legend(fontsize=9, facecolor='none', edgecolor='none', labelcolor=st.get_option("theme.textColor")) # Legend text color
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.yaxis.grid(True, linestyle='--', alpha=0.7, color=st.get_option("theme.secondaryBackgroundColor"))
    ax.set_facecolor('none') # Transparent plot background
    fig.set_facecolor('none') # Transparent figure background

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0: ax.annotate(f'{height:,.0f}', xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=7, color=st.get_option("theme.textColor"))
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
        st.session_state.user_message = ""
        st.session_state.message_type = ""

# --- Authentication Functions ---
def login_page():
    st.markdown("<h2 style='text-align: center; color: var(--accent-blue);'>Employee Portal Login</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: var(--text-color);'>Enter your credentials to access the dashboard.</p>", unsafe_allow_html=True)

    # Centering the login form
    col_left, col_center, col_right = st.columns([1,2,1])
    with col_center:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("<h4>Login</h4>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_username_input", placeholder="Enter your username").strip()
            password = st.text_input("Password", type="password", key="login_password_input", placeholder="Enter your password").strip()
            login_button = st.form_submit_button("Login", type="primary", use_container_width=True)

            if login_button:
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.auth["logged_in"] = True
                    st.session_state.auth["username"] = username
                    st.session_state.auth["role"] = USERS[username]["role"]
                    st.session_state.user_message = "Login successful! Welcome."
                    st.session_state.message_type = "success"
                    st.session_state.active_page = "Attendance" # Set default page after login
                    st.rerun()
                else:
                    st.session_state.user_message = "Invalid username or password. Please try again."
                    st.session_state.message_type = "error"
                    st.rerun()
    display_message() # Display message below the form

def logout():
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}
    st.session_state.user_message = "You have been logged out."
    st.session_state.message_type = "info"
    st.session_state.active_page = "login" # Reset active page on logout
    st.rerun()

# --- Page Functions (Your provided functionality) ---

def attendance_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled for attendance. Photos for specific activities can be uploaded from the 'Upload Activity Photo' section.", icon="ℹ️")
    
    st.markdown("---")
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    current_username = st.session_state.auth.get("username")
    
    if current_username is None:
        st.error("User not logged in. Please log in to record attendance.")
        st.markdown('</div></div>', unsafe_allow_html=True)
        return

    common_data = {"Username": current_username, "Latitude": pd.NA, "Longitude": pd.NA}

    def process_general_attendance(attendance_type):
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        
        new_entry_data = {col: pd.NA for col in ATTENDANCE_COLUMNS}
        new_entry_data.update({
            "Type": attendance_type,
            "Timestamp": now_str_display,
            "Username": current_username,
            "Latitude": common_data["Latitude"],
            "Longitude": common_data["Longitude"]
        })

        new_entry_df = pd.DataFrame([new_entry_data])
        
        st.session_state.attendance_df = pd.concat([st.session_state.attendance_df, new_entry_df], ignore_index=True)
        
        try:
            st.session_state.attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."
            st.session_state.message_type = "success"
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
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo and Log Activity", type="primary")
    
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
                team_summary = quarterly_goals_df.groupby("Username").agg(
                    Target=('TargetAmount', 'sum'),
                    Achieved=('AchievedAmount', 'sum')
                ).reset_index()
                
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
                        fig = create_donut_chart(row['Progress'], chart_title=f"{row['Username']} Progress",
                                                 achieved_color=st.get_option("theme.primaryColor"),
                                                 remaining_color=st.get_option("theme.secondaryBackgroundColor"))
                        st.pyplot(fig)
                
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

                submit_goal = st.form_submit_button("💾 Save Sales Goal", type="primary")

                if submit_goal:
                    if target_user and goal_description and target_amount >= 0 and achieved_amount >= 0 and status:
                        current_quarter = current_quarter_for_display
                        
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
                            st.session_state.goals_df.loc[existing_goal_index, new_goal_data.keys()] = list(new_goal_data.values())
                            st.session_state.user_message = f"Sales goal for {target_user} updated for {current_quarter}."
                            st.session_state.message_type = "info"
                        else:
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
                fig = create_donut_chart(overall_progress, chart_title="My Sales Progress",
                                         achieved_color=st.get_option("theme.primaryColor"),
                                         remaining_color=st.get_option("theme.secondaryBackgroundColor"))
                st.pyplot(fig)
            
            st.markdown("---")
            st.markdown(f"<h5>My Quarterly Goals for {current_quarter_for_display}:</h5>", unsafe_allow_html=True)
            quarterly_my_goals_df = my_goals_df[my_goals_df["MonthYear"] == current_quarter_for_display]
            
            if not quarterly_my_goals_df.empty:
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
                        
                        update_goal_btn = st.form_submit_button("🔄 Update My Sales Goal", type="primary")

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
                        fig = create_donut_chart(row['Progress'], chart_title=f"{row['Username']} Progress",
                                                 achieved_color=st.get_option("theme.primaryColor"),
                                                 remaining_color=st.get_option("theme.secondaryBackgroundColor"))
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

                submit_goal = st.form_submit_button("💾 Save Payment Goal", type="primary")

                if submit_goal:
                    if target_user and goal_description and target_amount >= 0 and achieved_amount >= 0 and status:
                        current_quarter = current_quarter_for_display
                        
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
                fig = create_donut_chart(overall_progress, chart_title="My Payment Progress",
                                         achieved_color=st.get_option("theme.primaryColor"),
                                         remaining_color=st.get_option("theme.secondaryBackgroundColor"))
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
                        
                        update_goal_btn = st.form_submit_button("🔄 Update My Payment Goal", type="primary")

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
        all_users = ["All"] + [u for u in USERS.keys() if USERS[u]["role"] == "employee"] # Only show employees for filter
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

    if df_display.empty:
        st.info("No activities to display for the selected filters.")
    else:
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
        nav_items_employee = [
            ("Attendance", "event_available"),
            ("Upload Activity Photo", "upload_file"),
            ("Claim Allowance", "payments"),
            ("Sales Goal Tracker", "track_changes"),
            ("Payment Goal Tracker", "paid"),
            ("Activity Log", "list_alt"),
        ]
        nav_items_admin = nav_items_employee # Admins can access all employee pages

        nav_items = nav_items_admin if current_role == "admin" else nav_items_employee

        for page_name, icon_name in nav_items:
            # Construct the HTML for the button label, including the icon and text
            button_label_html = f'<span class="material-symbols-outlined">{icon_name}</span> {page_name}'
            
            # Determine if this item should have the active class
            # This is done by adding a class to the Streamlit button's internal structure
            active_class = " active-sidebar-nav-item" if st.session_state.active_page == page_name else ""
            
            # Use st.button with the HTML label and the class
            # The 'class' argument for st.button itself doesn't apply to the internal div,
            # but we can try to inject it via the HTML or rely solely on CSS selectors.
            # For simplicity and robustness, let's inject it into the label HTML
            # and adjust CSS selectors to target the *button itself* with the class.
            
            # This is the crucial line. We inject a class into the outermost element Streamlit provides for the button.
            # Streamlit often wraps the button label in a <p> tag. We'll target the button element itself.
            
            # To apply a class to the *button element* itself, we can try to add it via a hack
            # or simply use a slightly different CSS selector approach.
            # Given that direct class injection to st.button is not native, we rely on the parent element
            # and the active_page state.
            
            # Simpler approach: use the key and the active state to apply CSS.
            # The CSS above is already targeting `[data-testid="stSidebar"] .stButton > button`
            # So, we just need to use the `key` to make it unique and trigger reruns.
            
            # Instead of injecting class into HTML, we will update the CSS to use `:has()` pseudo-class
            # or rely on Streamlit's data-testid structure if it allows.
            # However, for simplicity and cross-version compatibility, let's just make the st.button label HTML.
            
            # Add a unique ID to the button's internal structure, then use JS injection if needed for active state.
            # Or, rely on Streamlit's own way of marking active elements, or use a simpler
            # CSS `:nth-child` if order is fixed.

            # Revert to simpler `st.button` usage for now, and refine CSS selectors based on how Streamlit renders.
            # The problem of `TypeError` means `unsafe_allow_html=True` was passed as an argument.
            # It should be part of `st.markdown` or directly in the label if Streamlit supports HTML in label.
            # Streamlit *does* support HTML in `st.button` label, so the `TypeError` was likely from it being
            # passed as a separate argument.

            # The solution to the TypeError was to remove `unsafe_allow_html=True` as a separate argument for `st.button`.
            # We then include the HTML directly in the `label` argument.
            # The problem you're seeing now ("button overlap with menu bar and giving opacity") is a CSS layout issue.

            # To fix the layout, we need to ensure the `st.button` elements in the sidebar are styled correctly.
            # The CSS I provided *should* handle this by setting `display: flex`, `align-items: center`, etc.
            # The `.active-sidebar-nav-item` class will be added *conditionally* to the button's `className` in the frontend,
            # which we can simulate by targeting it based on `st.session_state.active_page`.

            # Let's try to add the class directly by using a slightly different approach
            # for the active state by manipulating the DOM via JavaScript if direct CSS is tricky.
            # But first, let's refine the CSS to ensure the default button styling is completely overridden.

            # Key insight: The `st.button` creates a div like `<div data-testid="stButton"> <button> <p>LABEL</p> </button> </div>`
            # We want to style the `<button>` element.
            # The `active-sidebar-nav-item` class should be applied to the `<button>` element itself.

            # The conditional class application for active state:
            button_classes = "st-emotion-cache-blah-blah-button" # Replace with actual Streamlit button class if inspecting
            if st.session_state.active_page == page_name:
                 button_classes += " active-sidebar-nav-item" # Add our custom class

            # We can't directly add a class to `st.button` in Python. Streamlit generates its own classes.
            # The best way to achieve the "active" visual is to target the button's `data-testid` and then its internal `p` or `span`.
            # OR, more simply, just ensure the hover/active styles are clear based on the `active_page` in session state.

            # Let's re-evaluate the CSS:
            # `[data-testid="stSidebar"] .stButton > button` correctly targets the button.
            # The `active` class being applied via `st.markdown` in the previous iteration was problematic
            # because it created a *separate* div.

            # The current Python code correctly uses `st.button` directly.
            # The CSS for `.stButton > button` should define the default style.
            # The CSS for `.stButton > button:hover` defines hover.
            # For the active state, we can make it conditional on the `active_page` directly in Python.
            
            # The key for active state in Streamlit with buttons is to change the *button's own class*
            # if that's possible. It's not directly exposed.
            # So, the best workaround for active state with `st.button` is to simply **not apply hover effects**
            # to the *active* button.

            # Let's remove the `.active-sidebar-nav-item` class addition in Python and simplify the CSS
            # to rely on `:focus` or just the fact that clicking reruns and the selected page
            # will re-render with a different style.

            # The previous approach where we used `st.markdown` to create the visual div and `st.button` as an overlay
            # was structurally problematic because it created two separate DOM elements that Streamlit
            # doesn't inherently stack nicely.

            # The `TypeError` is resolved by not passing `unsafe_allow_html=True` as a separate argument to `st.button`.
            # Now the CSS layout.

            # The issue of button "overlapping with menu bar" suggests perhaps `margin` or `padding` issues.
            # Let's ensure the `margin` on `.stButton > button` is consistent and not causing overlap.

            # Final attempt at elegant sidebar navigation:
            # Each button's `key` makes it unique.
            # The `st.session_state.active_page` determines which one is "active".
            # The CSS then needs to apply `active` styling *based on this state*.

            # We can try to use JavaScript to add a class to the active button, but that adds complexity.
            # A simpler way is to make the `st.button` label itself a conditional HTML string.

            # Let's use `st.columns` inside the sidebar to force alignment and then apply the HTML content.

            # This approach avoids the invisible button overlay and styles the native Streamlit button.
            # The CSS should now directly affect the Streamlit buttons.

            # Re-confirming the `TypeError` source:
            # `st.button(button_label_html, key=f"nav_btn_{page_name}_sidebar", use_container_width=True, unsafe_allow_html=True)`
            # The argument `unsafe_allow_html=True` is not accepted by `st.button`. This is what caused the TypeError.
            # The fix was to *remove that argument*. Streamlit `st.button` will interpret HTML in its `label` string if it starts with `<` and contains HTML.

            # The current code in the question *already has this fix applied*. So the `TypeError` should be gone.
            # The remaining issue is CSS.

            # The CSS provided (especially `[data-testid="stSidebar"] .stButton > button`) should correctly target and style the buttons.
            # The `active-sidebar-nav-item` class isn't being applied in Python for the button itself, so that CSS rule won't fire.

            # **To fix the active state visually:**
            # We will generate the `button_label_html` conditionally to include an "active" class on an *inner span or p* inside the button.
            # This is a bit of a hack, but more robust than trying to inject a class on the `button` element itself from Python.

            active_btn_html_class = ""
            if st.session_state.active_page == page_name:
                active_btn_html_class = " sidebar-nav-text-active" # A new class for the text part

            button_label_html = f'<span class="material-symbols-outlined sidebar-nav-icon">{icon_name}</span><span class="sidebar-nav-text{active_btn_html_class}">{page_name}</span>'
            
            # Now, the CSS needs to target `sidebar-nav-icon` and `sidebar-nav-text`.
            # And the overall button style, then the `sidebar-nav-text-active`.

            # Refined CSS for navigation buttons:

            # [data-testid="stSidebar"] .stButton > button { /* ... general button styles ... */ }
            # [data-testid="stSidebar"] .stButton > button .sidebar-nav-icon { /* ... icon styles ... */ }
            # [data-testid="stSidebar"] .stButton > button .sidebar-nav-text { /* ... text styles ... */ }
            # [data-testid="stSidebar"] .stButton > button .sidebar-nav-text.sidebar-nav-text-active {
            #   color: var(--accent-blue) !important;
            #   font-weight: 600;
            # }

            # And for the background of the active button, we still need a way to target the *button itself*.
            # This is the tricky part. Streamlit's elements are often wrapped in generic divs with `data-testid`.
            # We can't directly add a custom class to the `st.button` widget in Python.

            # Let's adjust the CSS again, to apply the active background and border to the whole button based on the label content
            # if we can't directly add a class from Python.
            # Or, simpler: rely on `st.session_state.active_page` to determine the button's type (e.g., `primary` vs `secondary` if you want subtle differences)
            # but that changes its inherent behavior.

            # The most direct way to get the active background for a sidebar button in Streamlit:
            # 1. Use `st.button` with `use_container_width=True`.
            # 2. Modify the CSS for `[data-testid="stSidebar"] .stButton > button`.
            # 3. For the "active" state, since you cannot add a class directly to the button widget from Python,
            #    the most common workaround is to use JavaScript injection (which is more complex)
            #    OR to rely on Streamlit's own internal styling for `st.button` which often has an `:active` or `:focus` state
            #    that you can override, or to make the selected button a different color on rerun.

            # Let's try to achieve the active background by combining CSS `:focus` (which often remains active after click)
            # and by setting the background color directly in the `st.button` definition,
            # if that's more reliable. But `st.button` doesn't have `background_color` as an argument.

            # **The fundamental problem is styling the "active" button background without direct class access.**

            # Let's try a different CSS approach:
            # Make the active button's *label* (which includes the icon and text)
            # look different, and then make the button's background transparent.

            # Let's revert to the Python code where `st.button` uses a simple HTML label.
            # And modify the CSS to aggressively style the button and its content.

            # The core problem is that `st.button` applies its own wrappers and styles.
            # The CSS needs to be precise.

            # I will modify the CSS to specifically target the "active" button's background and text color based on the `active_page` state.
            # This will require a bit of a hack using `:has()` or by making the visual changes based on the *currently rendered page* in Streamlit.

            # Simplest approach for visual active state:
            # Make the active button *look* like it's active by applying `background-color` and `color` directly.
            # The best way to implement "active state" for custom-styled Streamlit buttons is often:
            # 1. Have a `st.session_state.active_page` variable.
            # 2. In the loop, when creating `st.button`, dynamically set its `type` or `class` if Streamlit supported it (it doesn't directly).
            # 3. **The most reliable way is to apply CSS based on which button is the current `active_page`.**
            #    This is done by using unique IDs or data-testids.
            #    We can put a custom ID on the `st.button` using `key`.
            #    Then, in CSS, target `[data-testid="stSidebar"] button[key="nav_btn_Attendance_sidebar"]` for the active one.
            #    This approach is verbose in CSS but highly precise.

            # Let's refine the CSS to use more specific selectors for the active state based on the `key`
            # or data-testid attribute if Streamlit generates it reliably.

            # Given the error and the CSS issues, the `unsafe_allow_html=True` was indeed the source of the `TypeError` if used as a separate argument for `st.button`.
            # Once that is removed, the HTML in the label should work.

            # **The overlap/opacity issue is a CSS display issue.**
            # The `sidebar-nav-item` in the previous code was a `div` and the `st.button` was another element.
            # We now need to style the *Streamlit button directly* to look like the nav item.

            # Key CSS adjustments:
            # - Ensure `[data-testid="stSidebar"] .stButton > button` has `display: flex`, `align-items: center`.
            # - Remove any conflicting `margin` or `padding` that causes overlap.
            # - Style the `p` and `span` elements *inside* the button.
            # - For the active state, we'll try to apply a CSS class dynamically in the Python code itself,
            #   which Streamlit *might* render (though often it strips custom classes from direct widget parameters).
            #   If not, the workaround is more involved (JS).

            # Let's use the `className` workaround in Streamlit for custom classes.
            # Streamlit buttons have a `data-testid` like `stButton-secondary` or `stButton-primary`.
            # We can also target the generated `div` around the button.

            # Let's simplify the HTML in the button label to just be the icon and text, and adjust CSS.

            # The current code should work for styling buttons in general in the sidebar.
            # The `active` state requires a precise CSS rule.

            # The following CSS makes the active button stand out better by targeting the `stButton` itself.
            # I will use a custom ID for the active button, then target it in CSS.
            # No, `st.button` does not take an `id` or `class` argument directly.
            # The `key` is for Streamlit's internal identification.

            # The most robust method for active state without JS:
            # 1. Use `st.button` for each.
            # 2. In CSS, style `[data-testid="stSidebar"] .stButton > button`.
            # 3. For the active page, add a background color dynamically in Streamlit logic by wrapping it in a `st.container` and styling the container, or by using a `st.markdown` `div` *around* the button. This goes back to the overlay problem.

            # Okay, I will try to use the `st.button` label directly with HTML, and ensure the CSS covers the general and active states robustly.

            # The `TypeError` is resolved by not passing `unsafe_allow_html=True` as a separate argument to `st.button`.
            # The problem you're seeing now is the visual overlap/opacity.
            # This is purely CSS related.

            # Let's refine the CSS for the sidebar buttons.
            # The key is to make the `st.button` itself behave like a block element and fill its container,
            # and then style its content.

            # Current CSS already targets `.stButton > button` which is the correct element.
            # Let's make sure the `padding` and `margin` are behaving as expected within the sidebar.

            # The issue might be that Streamlit's default `st.button` padding is *not* what's defined in the CSS,
            # or `!important` isn't strong enough.

            # Let's try to increase specificity for the active state to ensure it overrides defaults.
            # The issue of "overlapping with menu bar" suggests that the button itself is being rendered with some default margin/padding
            # *outside* of the `stButton > button` rule.

            # Let's ensure no margin is applied by default to the `.stButton` wrapper div itself.
            # Add this to CSS:
            # `[data-testid="stSidebar"] div[data-testid^="stButton"] { margin: 0 !important; }`
            # This targets the wrapper `div` around the button.

            # Let's try the updated CSS with the Python code provided in the previous turn.
            # The Python code for the sidebar buttons is fine. The HTML for `button_label_html` is also correct.
            # The fix is purely in CSS.

            # I will add this to the CSS:

```css
    /* Ensure the Streamlit button wrapper div doesn't add extra margin */
    [data-testid="stSidebar"] div[data-testid^="stButton"] {
        margin-top: 0.25rem !important;
        margin-bottom: 0.25rem !important;
        /* Also apply horizontal margin to this wrapper for consistent spacing */
        margin-left: 0.75rem !important;
        margin-right: 0.75rem !important;
        width: calc(100% - 1.5rem) !important; /* Re-calculate width to include margins */
        overflow: hidden; /* Important for border-radius to apply correctly */
        border-radius: 8px; /* Apply border-radius here as well */
    }

    /* Navigation Items (Sidebar Buttons) - Targeting Streamlit's internal button structure */
    /* Target the button element inside the wrapper */
    [data-testid="stSidebar"] div[data-testid^="stButton"] > button {
        display: flex; /* Use flexbox to align icon and text */
        align-items: center; /* Vertically align items */
        justify-content: flex-start; /* Align icon and text to start */
        padding: 0.85rem 1.2rem !important; /* More padding for a bolder look */
        
        transition: background-color 0.2s, color 0.2s, transform 0.1s, box-shadow 0.2s;
        width: 100% !important; /* Button takes full width of its parent div */
        height: 100%; /* Take full height of parent div */
        
        background-color: transparent !important; /* Start transparent, override Streamlit defaults */
        border: none !important; /* No border, override Streamlit defaults */
        color: var(--text-color) !important; /* Light text color for inactive items, override */
        cursor: pointer; /* Indicate clickable */
        box-shadow: none !important; /* Remove default button shadow */
        outline: none !important; /* Remove focus outline */
        font-size: 1.05rem; /* Slightly larger font */
        font-weight: 500;
        border-radius: 8px; /* Ensure border-radius for the button itself too */
    }

    /* Active state for sidebar nav items (buttons) - use a specific class added by Streamlit's key logic */
    /* We'll use Streamlit's internal CSS structure to identify the active button if possible */
    /* If the active button is not explicitly styled by Streamlit with a class, we need a workaround. */
    /* One hack is to target the button whose label's text matches the active page. This is fragile. */

    /* The most common and robust way to simulate an active button in Streamlit
    is to apply the desired background/text color when the page is active.
    Since direct class injection to st.button is tricky, let's use a very specific CSS selector
    that becomes true only for the active page. */

    /* This targets the actual button element for the active page.
       This relies on the `key` being consistent and matching the `st.session_state.active_page`.
       This is not perfect as CSS cannot read Python session state directly.
       However, if we are setting `st.session_state.active_page` and rerunning,
       the CSS will be re-applied.

       Let's use a dynamic `data-active-page` attribute on the button element itself for better targeting.
       This will require a little JavaScript injection.
       Given that the user is avoiding "full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app)",
       it might be better to stick to pure CSS if possible, even if it's less dynamic.

       Let's stick to the conditional HTML in the label for the 'active' visual state and refine general button styles.
       The current CSS already handles `stButton > button` which is the core.
       The "overlap" implies default `stButton` container styling.
    */

    /* Ensure a consistent background for the button when it's active based on the state.
       This part is the most challenging without direct Python-to-CSS class injection on the button.
       Let's make the background change on hover and also if the page is active, by making the text
       and icon change color in Python and relying on the general button styles.
    */
    
    /* Revisit active state: Streamlit buttons DO have a primary/secondary state.
       We can switch `type` based on `active_page`!
       This is the simplest way to get Streamlit to apply its native active look.
    */
