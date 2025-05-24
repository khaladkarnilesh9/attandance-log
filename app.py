import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import pytz
import sys # Not strictly needed in this version unless for specific path debugging elsewhere
import altair as alt

# --- Helper Chart Function (defined but not currently called in main nav) ---
def render_goal_chart(df: pd.DataFrame, title: str):
    if not isinstance(df, pd.DataFrame) or df.empty: # Added type check
        st.warning(f"No data or invalid data provided for chart: {title}")
        return
    
    df_chart = df.copy()
    # Ensure necessary columns exist before trying to process them
    required_cols = ["TargetAmount", "AchievedAmount", "MonthYear"]
    if not all(col in df_chart.columns for col in required_cols):
        st.error(f"Chart data for '{title}' is missing one or more required columns: {required_cols}")
        return

    df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    df_chart = df_chart.sort_values(by="MonthYear")

    try:
        long_df = df_chart.melt(id_vars=["MonthYear"], value_vars=["TargetAmount", "AchievedAmount"],
                          var_name="Metric", value_name="Amount")
        chart = alt.Chart(long_df).mark_bar().encode(
            x=alt.X('MonthYear:N', title="Period (YYYY-QX)"), # Updated title
            y=alt.Y('Amount:Q', title="Amount (INR)"),
            color=alt.Color('Metric:N', scale=alt.Scale(domain=['TargetAmount', 'AchievedAmount'], range=["#3498db", "#2ecc71"])), # Explicit domain
            tooltip=["MonthYear", "Metric", "Amount"]
        ).properties(
            title=title,
            # width="container" # 'container' can sometimes cause issues, let Altair decide or set fixed
        )
        st.altair_chart(chart, use_container_width=True)
    except Exception as e_chart:
        st.error(f"Could not generate chart for '{title}': {e_chart}")


# from streamlit_geolocation import streamlit_geolocation # Geolocation is disabled

# --- Pillow for placeholder image generation (optional) --
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# --- CSS ---
html_css = """
<style>
    /* --- General --- */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f0f2f5;
        color: #333;
    }
    /* --- Titles & Headers --- */
    h1, h2 { color: #1c4e80; }
    .main .block-container > div:first-child > div:first-child > div:first-child > h1 {
        text-align: center; font-size: 2.5em; padding-bottom: 20px;
        border-bottom: 2px solid #70a1d7; margin-bottom: 30px;
    }
    /* --- Card Styling (Consolidated) --- */
    .card {
        background-color: #ffffff; /* Prefer #ffffff for better contrast over #f9f9f9 */
        padding: 25px; /* Unified padding */
        border-radius: 10px; /* Unified radius */
        box-shadow: 0 4px 8px rgba(0,0,0,0.05); /* Unified shadow */
        margin-bottom: 30px; /* Unified margin */
    }
    .card h3 { margin-top: 0; color: #1c4e80; border-bottom: 1px solid #e0e0e0;
               padding-bottom: 10px; margin-bottom: 20px; font-size: 1.5em; }
    .card h4 { color: #2070c0; margin-top: 25px; margin-bottom: 15px; font-size: 1.25em;
               padding-bottom: 5px; border-bottom: 1px dashed #d0d0d0; }
    .card h5 { font-size: 1.1em; color: #333; margin-top: 20px; margin-bottom: 10px; font-weight: 600; }
    .card h6 { font-size: 0.95em; color: #495057; margin-top: 15px; margin-bottom: 8px; font-weight: 500; }
    
    /* --- Login Container --- */
    .login-container { max-width: 450px; margin: 50px auto; }
    .login-container .stButton button { width: 100%; background-color: #2070c0; font-size: 1.1em; }
    .login-container .stButton button:hover { background-color: #1c4e80; }

    /* --- Streamlit Button Styling --- */
    .stButton button {
        background-color: #28a745; color: white; padding: 10px 20px; border: none;
        border-radius: 5px; font-size: 1em; font-weight: bold;
        transition: background-color 0.3s ease, transform 0.1s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer;
    }
    .stButton button:hover { background-color: #218838; transform: translateY(-1px); }
    .stButton button:active { transform: translateY(0px); }
    .stButton button[id*="logout_button_sidebar"] { background-color: #dc3545 !important; }
    .stButton button[id*="logout_button_sidebar"]:hover { background-color: #c82333 !important; }

    /* --- Input Fields --- */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, 
    .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 5px !important; border: 1px solid #ced4da !important;
        padding: 10px !important; font-size: 1em !important; 
        color: #212529 !important; background-color: #fff !important;
    }
    .stTextInput input::placeholder, .stNumberInput input::placeholder, .stTextArea textarea::placeholder {
        color: #6c757d !important; opacity: 1;
    }
    .stTextArea textarea { min-height: 100px; }
    .card .stTextInput input, .card .stNumberInput input, .card .stTextArea textarea {
        color: #212529 !important; background-color: #fff !important;
    }

    /* --- Sidebar --- */
    [data-testid="stSidebar"] { background-color: #1c4e80; padding: 20px !important; }
    [data-testid="stSidebar"] .sidebar-content { padding-top: 20px; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] div, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ffffff !important; }
    [data-testid="stSidebar"] .stRadio > label { font-size: 1.1em !important; color: #a9d6e5 !important; padding-bottom: 8px; }
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] > label { color: #ffffff !important; font-weight: bold; }
    .welcome-text { font-size: 1.3em; font-weight: bold; margin-bottom: 25px; text-align: center; 
                    color: #ffffff; border-bottom: 1px solid #70a1d7; padding-bottom: 15px;}

    /* --- Dataframe Styling --- */
    .stDataFrame { width: 100%; border: 1px solid #d1d9e1; border-radius: 8px; overflow: hidden; 
                   box-shadow: 0 2px 4px rgba(0,0,0,0.06); margin-bottom: 20px; }
    .stDataFrame table { width: 100%; border-collapse: collapse; }
    .stDataFrame table thead th { background-color: #f0f2f5; color: #1c4e80; font-weight: 600; text-align: left; 
                                 padding: 12px 15px; border-bottom: 2px solid #c5cdd5; font-size: 0.9em; }
    .stDataFrame table tbody td { padding: 10px 15px; border-bottom: 1px solid #e7eaf0; vertical-align: middle; 
                                color: #333; font-size: 0.875em; }
    .stDataFrame table tbody tr:last-child td { border-bottom: none; }
    .stDataFrame table tbody tr:hover { background-color: #e9ecef; }

    /* --- Columns for buttons --- */
    .button-column-container > div[data-testid="stHorizontalBlock"] { gap: 15px; }
    .button-column-container .stButton button { width: 100%; }

    /* Horizontal Radio Buttons */
    div[role="radiogroup"] { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px; }
    div[role="radiogroup"] > label { background-color: #86a7c7; padding: 8px 15px; border-radius: 20px; 
                                   border: 1px solid #ced4da; cursor: pointer; 
                                   transition: background-color 0.2s ease, border-color 0.2s ease; font-size: 0.95em; }
    div[role="radiogroup"] > label:hover { background-color: #dde2e6; border-color: #adb5bd; }
    div[role="radiogroup"] div[data-baseweb="radio"][aria-checked="true"] + label { 
        background-color: #2070c0 !important; color: white !important; 
        border-color: #1c4e80 !important; font-weight: 500; 
    }

    /* --- Specific Headers --- */
    .employee-section-header { color: #2070c0; margin-top: 30px; border-bottom: 1px solid #e0e0e0; 
                               padding-bottom: 5px; font-size: 1.3em; }
    .record-type-header { font-size: 1.1em; color: #333; margin-top: 20px; margin-bottom: 10px; font-weight: 600; }
    .allowance-summary-header { font-size: 1.0em; color: #495057; margin-top: 15px; margin-bottom: 8px; font-weight: 550; }
    
    div[data-testid="stImage"] > img { border-radius: 8px; border: 2px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stProgress > div > div { background-color: #2070c0 !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.9em !important; color: #555 !important; }

    /* --- Custom Notification Styling --- */
    .custom-notification { padding: 10px 15px; border-radius: 5px; margin-bottom: 15px; 
                           font-size: 0.95em; border-left: 5px solid; }
    .custom-notification.success { background-color: #d4edda; color: #155724; border-left-color: #28a745; }
    .custom-notification.error   { background-color: #f8d7da; color: #721c24; border-left-color: #dc3545; }
    .custom-notification.warning { background-color: #fff3cd; color: #856404; border-left-color: #ffc107; }
    .custom-notification.info    { background-color: #d1ecf1; color: #0c5460; border-left-color: #17a2b8; }

    /* --- Badge Styling (Consolidated) --- */
    .badge { display: inline-block; padding: 0.35em .65em; font-size: .75em; font-weight: 700; 
             line-height: 1; color: #fff; text-align: center; white-space: nowrap; 
             vertical-align: baseline; border-radius: .375rem; }
    .badge.status-achieved    { background-color: #198754; } /* Green */
    .badge.status-in-progress { background-color: #0dcaf0; } /* Cyan/Info */
    .badge.status-not-started { background-color: #6c757d; } /* Gray/Secondary */
    .badge.status-on-hold     { background-color: #ffc107; color: #000; } /* Yellow/Warning - dark text */
    .badge.status-cancelled   { background-color: #dc3545; } /* Red/Danger */
    .badge.status-default     { background-color: #adb5bd; } /* Lighter gray */
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
                try: font = ImageFont.truetype("arial.ttf", 40)
                except IOError: font = ImageFont.load_default()
                text = user_key[:2].upper()
                if hasattr(draw, 'textbbox'):
                    bbox = draw.textbbox((0,0), text, font=font)
                    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    text_x, text_y = (120 - text_width) / 2, (120 - text_height) / 2 - bbox[1]
                elif hasattr(draw, 'textsize'):
                    text_width, text_height = draw.textsize(text, font=font)
                    text_x, text_y = (120 - text_width) / 2, (120 - text_height) / 2
                else: text_x, text_y = 30,30
                draw.text((text_x, text_y), text, fill=(28, 78, 128), font=font)
                img.save(img_path)
            except Exception: pass


# --- File Paths ---
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"
GOALS_FILE = "goals.csv" # For Sales Goals
PAYMENT_GOALS_FILE = "payment_goals.csv" # For Payment Collection Goals

# --- Timezone Configuration ---
TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'. Use valid Olson name."); st.stop()

def get_current_time_in_tz(): return datetime.now(timezone.utc).astimezone(tz)
# def get_current_month_year_str(): return get_current_time_in_tz().strftime("%Y-%m") # Not directly used for quarterly logic

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
                    if nc in columns and nc in df.columns:
                         df[nc] = pd.to_numeric(df[nc], errors='coerce')
                # Ensure string columns that might be used for merging/comparison are strings
                str_cols = ["Username", "MonthYear"]
                for sc in str_cols:
                    if sc in columns and sc in df.columns:
                        df[sc] = df[sc].astype(str)
                return df
            else: return pd.DataFrame(columns=columns)
        except pd.errors.EmptyDataError: return pd.DataFrame(columns=columns)
        except Exception as e:
            st.error(f"Error loading {path}: {e}. Empty DataFrame returned.")
            return pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
        try: df.to_csv(path, index=False)
        except Exception as e: st.warning(f"Could not create {path}: {e}")
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
# For Sales Goals, MonthYear will store "YYYY-QX"
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
# For Payment Collection Goals, MonthYear will store "YYYY-QX"
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]


attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS) # Sales Goals
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS) # Payment Goals

# --- Initialize Session State for Notifications ---
if "user_message" not in st.session_state:
    st.session_state.user_message = None
if "message_type" not in st.session_state:
    st.session_state.message_type = None

# --- Login Page ---
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}

if not st.session_state.auth["logged_in"]:
    st.title("🙂HR Dashboard Login")
    message_placeholder_login = st.empty()
    if st.session_state.user_message:
        message_placeholder_login.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
        st.session_state.user_message = None
        st.session_state.message_type = None

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
            st.error("Invalid username or password.")
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# --- Main Application ---
st.title("👨‍💼 HR Dashboard")
current_user = st.session_state.auth

message_placeholder = st.empty()
if st.session_state.user_message:
    message_placeholder.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
    st.session_state.user_message = None
    st.session_state.message_type = None

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user['username']}!</div>", unsafe_allow_html=True)
    nav_options = ["📆 Attendance", "🧾 Allowance", "🎯 Sales Goal Tracker", "💰 Payment Collection Tracker", "📊 View Logs"]
    nav = st.radio("Navigation", nav_options, key="sidebar_nav_main_v2") # Ensure unique key
    user_sidebar_info = USERS.get(current_user["username"], {})
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]):
        st.image(user_sidebar_info["profile_photo"], width=80, use_column_width='auto')
    st.markdown(f"<p style='text-align:center; font-size:0.9em; color: #e0e0e0;'>{user_sidebar_info.get('position', 'N/A')}</p>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔒 Logout", key="logout_button_sidebar", use_container_width=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."
        st.session_state.message_type = "info"
        st.rerun()

# --- Helper function for Quarterly Logic ---
def get_quarter_str_for_year(year_to_check, use_current_moment=False):
    if use_current_moment:
        month_for_quarter = get_current_time_in_tz().month
    else: # Default to Q1 for a given year if not using current moment
        month_for_quarter = 1
    
    if 1 <= month_for_quarter <= 3: quarter_num_str = "Q1"
    elif 4 <= month_for_quarter <= 6: quarter_num_str = "Q2"
    elif 7 <= month_for_quarter <= 9: quarter_num_str = "Q3"
    else: quarter_num_str = "Q4"
    return f"{year_to_check}-{quarter_num_str}"

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
                st.session_state.message_type = "success"; st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error saving attendance: {e}"
                st.session_state.message_type = "error"; st.rerun()
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
                st.session_state.message_type = "success"; st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error saving attendance: {e}"
                st.session_state.message_type = "error"; st.rerun()
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
                st.session_state.user_message = f"Allowance for ₹{amount:.2f} submitted."
                st.session_state.message_type = "success"; st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error saving allowance: {e}"
                st.session_state.message_type = "error"; st.rerun()
        else:
            st.warning("Please complete all fields with valid values.")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "🎯 Sales Goal Tracker": # Renamed from "Goal Tracker" for clarity
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    
    TARGET_SALES_GOAL_YEAR = 2025
    current_quarter_for_sales_display = get_quarter_str_for_year(TARGET_SALES_GOAL_YEAR, use_current_moment=True)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage Sales Goals</h4>", unsafe_allow_html=True)
        admin_action_sales = st.radio( "Action:", ["View Team Sales Progress", f"Set/Edit Sales Goal for {TARGET_SALES_GOAL_YEAR}"],
            key="admin_sales_goal_action_2025_q", horizontal=True )

        if admin_action_sales == "View Team Sales Progress":
            st.markdown(f"<h5>Team Sales Goal Progress for {current_quarter_for_sales_display}</h5>", unsafe_allow_html=True)
            # ... (Display logic for team sales progress - similar to payment tracker's team view)
            employee_users = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users: st.info("No employees found.")
            else:
                summary_data = []
                for emp_name in employee_users:
                    user_info_gt = USERS.get(emp_name, {})
                    emp_current_goal = goals_df[ (goals_df["Username"].astype(str) == str(emp_name)) & (goals_df["MonthYear"].astype(str) == str(current_quarter_for_sales_display)) ]
                    target, achieved, prog_val, goal_desc, status_val = 0.0, 0.0, 0.0, "Not Set", "N/A"
                    if not emp_current_goal.empty:
                        g_data = emp_current_goal.iloc[0]
                        target = pd.to_numeric(g_data.get("TargetAmount"), errors='coerce').fillna(0.0)
                        achieved = pd.to_numeric(g_data.get("AchievedAmount"), errors='coerce').fillna(0.0)
                        if target > 0: prog_val = min(achieved / target, 1.0)
                        goal_desc = g_data.get("GoalDescription", "N/A")
                        status_val = g_data.get("Status", "N/A")
                    summary_data.append({ "Photo": user_info_gt.get("profile_photo",""), "Employee": emp_name, "Position": user_info_gt.get("position","N/A"),
                                          "Goal": goal_desc, "Target": target, "Achieved": achieved, "Progress": prog_val, "Status": status_val })
                if summary_data:
                    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True, column_config={
                        "Photo": st.column_config.ImageColumn("Pic", width="small"), "Target": st.column_config.NumberColumn("Target (₹)", format="%.0f"),
                        "Achieved": st.column_config.NumberColumn("Achieved (₹)", format="%.0f"), "Progress": st.column_config.ProgressColumn("Progress", format="%.0f%%", min_value=0, max_value=1)})
                # Option to show chart for team progress (can be enabled)
                # team_sales_df_for_chart = goals_df[goals_df["MonthYear"].str.startswith(str(TARGET_SALES_GOAL_YEAR))]
                # if not team_sales_df_for_chart.empty:
                #     render_goal_chart(team_sales_df_for_chart.groupby('MonthYear', as_index=False)[['TargetAmount', 'AchievedAmount']].sum(), "Overall Team Sales Goals vs Achievement 2025")


        elif admin_action_sales == f"Set/Edit Sales Goal for {TARGET_SALES_GOAL_YEAR}":
            st.markdown(f"<h5>Set or Update Sales Goal ({TARGET_SALES_GOAL_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options = [u for u, d in USERS.items() if d["role"] == "employee"]
            current_selected_employee_sales = None
            if not employee_options: st.warning("No employees available.")
            else:
                if "sales_goal_sel_emp_2025_q" not in st.session_state or st.session_state.sales_goal_sel_emp_2025_q not in employee_options:
                    st.session_state.sales_goal_sel_emp_2025_q = employee_options[0]
                try: emp_radio_idx = employee_options.index(st.session_state.sales_goal_sel_emp_2025_q)
                except ValueError: emp_radio_idx = 0; st.session_state.sales_goal_sel_emp_2025_q = employee_options[0] if employee_options else None
                
                selected_emp_radio_sales = st.radio("Select Employee:", employee_options, index=emp_radio_idx, key="sales_goal_emp_radio_2025_q", horizontal=True)
                if st.session_state.sales_goal_sel_emp_2025_q != selected_emp_radio_sales:
                    st.session_state.sales_goal_sel_emp_2025_q = selected_emp_radio_sales
                current_selected_employee_sales = st.session_state.sales_goal_sel_emp_2025_q

            quarter_options_sales = [f"{TARGET_SALES_GOAL_YEAR}-Q{i}" for i in range(1, 5)]
            current_selected_period_sales = None
            if not quarter_options_sales: st.error("Quarter options list empty!")
            else:
                default_period_sales = get_quarter_str_for_year(TARGET_SALES_GOAL_YEAR, use_current_moment=True)
                if "sales_goal_target_period_2025_q" not in st.session_state or st.session_state.sales_goal_target_period_2025_q not in quarter_options_sales:
                    st.session_state.sales_goal_target_period_2025_q = default_period_sales if default_period_sales in quarter_options_sales else quarter_options_sales[0]
                try: period_radio_idx_sales = quarter_options_sales.index(st.session_state.sales_goal_target_period_2025_q)
                except ValueError: period_radio_idx_sales = quarter_options_sales.index(default_period_sales) if default_period_sales in quarter_options_sales else 0; st.session_state.sales_goal_target_period_2025_q = quarter_options_sales[period_radio_idx_sales]
                
                selected_period_radio_sales = st.radio(f"Goal Period ({TARGET_SALES_GOAL_YEAR} - Quarter):", options=quarter_options_sales, index=period_radio_idx_sales, key="sales_goal_period_radio_2025_q", horizontal=True)
                if st.session_state.sales_goal_target_period_2025_q != selected_period_radio_sales:
                    st.session_state.sales_goal_target_period_2025_q = selected_period_radio_sales
                current_selected_period_sales = st.session_state.sales_goal_target_period_2025_q
            
            if current_selected_employee_sales and current_selected_period_sales:
                existing_g_sales = goals_df[(goals_df["Username"].astype(str) == str(current_selected_employee_sales)) & (goals_df["MonthYear"].astype(str) == str(current_selected_period_sales))]
                g_desc, g_target, g_achieved, g_status_val = "", 0.0, 0.0, "Not Started"
                if not existing_g_sales.empty:
                    g_d_sales = existing_g_sales.iloc[0]
                    g_desc = g_d_sales.get("GoalDescription", "")
                    raw_target = g_d_sales.get("TargetAmount"); g_target = 0.0 if pd.isna(raw_target) else (0.0 if pd.isna(pd.to_numeric(raw_target, errors='coerce')) else float(pd.to_numeric(raw_target, errors='coerce')))
                    raw_achieved = g_d_sales.get("AchievedAmount"); g_achieved = 0.0 if pd.isna(raw_achieved) else (0.0 if pd.isna(pd.to_numeric(raw_achieved, errors='coerce')) else float(pd.to_numeric(raw_achieved, errors='coerce')))
                    g_status_val = g_d_sales.get("Status", "Not Started")
                    st.info(f"Editing sales goal for {current_selected_employee_sales} for {current_selected_period_sales}.")

                form_key_sales = f"set_sales_goal_form_{current_selected_employee_sales}_{current_selected_period_sales}_2025q"
                with st.form(key=form_key_sales):
                    new_g_desc = st.text_area("Sales Goal Description:", value=g_desc, key=f"desc_sales_2025q_{current_selected_employee_sales}_{current_selected_period_sales}")
                    new_g_target = st.number_input("Target Sales (INR):", value=g_target, min_value=0.0, step=1000.0, format="%.2f", key=f"target_sales_2025q_{current_selected_employee_sales}_{current_selected_period_sales}")
                    new_g_achieved = st.number_input("Achieved Sales (INR):", value=g_achieved, min_value=0.0, step=100.0, format="%.2f", key=f"achieved_sales_2025q_{current_selected_employee_sales}_{current_selected_period_sales}")
                    status_radio_idx_sales = status_options.index(g_status_val) if g_status_val in status_options else 0
                    new_g_status = st.radio("Status:", options=status_options, index=status_radio_idx_sales, key=f"status_sales_radio_{current_selected_employee_sales}_{current_selected_period_sales}", horizontal=True)
                    submitted_sales = st.form_submit_button("Save Sales Goal")

                if submitted_sales:
                    if not new_g_desc.strip(): st.warning("Description needed.")
                    elif new_g_target <= 0 and new_g_status not in ["Cancelled", "On Hold", "Not Started"]: st.warning("Target > 0 unless status is Cancelled/On Hold/Not Started.")
                    else:
                        if not existing_g_sales.empty:
                            goals_df.loc[existing_g_sales.index[0]] = [current_selected_employee_sales, current_selected_period_sales, new_g_desc, new_g_target, new_g_achieved, new_g_status]
                            msg_verb="updated"
                        else:
                            new_g_entry_data = {"Username": current_selected_employee_sales, "MonthYear": current_selected_period_sales, "GoalDescription": new_g_desc, 
                                                "TargetAmount": new_g_target, "AchievedAmount": new_g_achieved, "Status": new_g_status}
                            for col_name in GOALS_COLUMNS:
                                if col_name not in new_g_entry_data: new_g_entry_data[col_name] = pd.NA
                            new_g_entry = pd.DataFrame([new_g_entry_data], columns=GOALS_COLUMNS)
                            goals_df = pd.concat([goals_df, new_g_entry], ignore_index=True)
                            msg_verb="set"
                        try:
                            goals_df.to_csv(GOALS_FILE, index=False)
                            st.session_state.user_message = f"Sales goal for {current_selected_employee_sales} ({current_selected_period_sales}) {msg_verb}!"
                            st.session_state.message_type = "success"; st.rerun()
                        except Exception as e:
                            st.session_state.user_message = f"Error saving sales goal: {e}"
                            st.session_state.message_type = "error"; st.rerun()
    else: # Employee Sales Goal View
        st.markdown("<h4>My Sales Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        my_all_goals = goals_df[goals_df["Username"].astype(str) == str(current_user["username"])].copy()
        if not my_all_goals.empty:
            for col_n in ["TargetAmount", "AchievedAmount"]: my_all_goals[col_n] = pd.to_numeric(my_all_goals[col_n], errors='coerce').fillna(0.0)

        current_g_sales = my_all_goals[my_all_goals["MonthYear"].astype(str) == str(current_quarter_for_sales_display)]
        st.markdown(f"<h5>Current Sales Goal Period: {current_quarter_for_sales_display}</h5>", unsafe_allow_html=True)
        if not current_g_sales.empty:
            g_e_sales = current_g_sales.iloc[0]
            target_amt = pd.to_numeric(g_e_sales.get("TargetAmount"), errors='coerce').fillna(0.0)
            achieved_amt = pd.to_numeric(g_e_sales.get("AchievedAmount"), errors='coerce').fillna(0.0)
            prog_val = min(achieved_amt / target_amt, 1.0) if target_amt > 0 else 0.0
            st.markdown(f"**Description:** {g_e_sales.get('GoalDescription', 'N/A')}")
            c1,c2,c3 = st.columns(3)
            c1.metric("Target Sales", f"₹{target_amt:,.0f}"); c2.metric("Achieved Sales", f"₹{achieved_amt:,.0f}")
            with c3: st.metric("Status", g_e_sales.get('Status','In Progress')); st.progress(prog_val); st.caption(f"{prog_val*100:.1f}% Completed")
            st.markdown("---")
            st.markdown(f"<h6>Update My Sales Achievement for {current_quarter_for_sales_display}</h6>", unsafe_allow_html=True)
            with st.form(key=f"update_sales_ach_form_{current_user['username']}_2025q"):
                new_ach_val_sales = st.number_input("My Total Achieved Sales (INR):", value=float(achieved_amt), min_value=0.0, step=100.0, format="%.2f", key=f"emp_sales_ach_update_{current_quarter_for_sales_display}")
                submit_upd_sales = st.form_submit_button("Update Sales Achievement")
            if submit_upd_sales:
                idx_to_update = current_g_sales.index[0]
                goals_df.loc[idx_to_update, "AchievedAmount"] = new_ach_val_sales
                goals_df.loc[idx_to_update, "Status"] = "Achieved" if new_ach_val_sales >= target_amt and target_amt > 0 else "In Progress"
                try:
                    goals_df.to_csv(GOALS_FILE, index=False)
                    st.session_state.user_message = "Sales achievement updated!"
                    st.session_state.message_type = "success"; st.rerun()
                except Exception as e:
                    st.session_state.user_message = f"Error updating sales achievement: {e}"
                    st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No sales goal set for you for {current_quarter_for_sales_display}. Contact admin.")
        
        st.markdown("---")
        st.markdown("<h5>My Sales Goals Visualized (2025)</h5>", unsafe_allow_html=True)
        employee_sales_goals_2025 = my_all_goals[my_all_goals["MonthYear"].astype(str).str.startswith(str(TARGET_SALES_GOAL_YEAR))]
        if not employee_sales_goals_2025.empty:
            render_goal_chart(employee_sales_goals_2025, f"{current_user['username']}'s Sales Goals vs Achievement {TARGET_SALES_GOAL_YEAR}")
        else:
            st.info(f"No sales goal data to visualize for {TARGET_SALES_GOAL_YEAR}.")


        st.markdown("---")
        st.markdown("<h5>My Past Sales Goals (2025)</h5>", unsafe_allow_html=True)
        past_g_sales = my_all_goals[(my_all_goals["MonthYear"].astype(str).str.startswith(str(TARGET_SALES_GOAL_YEAR))) & (my_all_goals["MonthYear"].astype(str) != str(current_quarter_for_sales_display))].sort_values(by="MonthYear", ascending=False)
        if not past_g_sales.empty:
            st.dataframe(past_g_sales[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]], hide_index=True, use_container_width=True,
                         column_config={"TargetAmount":st.column_config.NumberColumn(format="₹%.0f"), "AchievedAmount":st.column_config.NumberColumn(format="₹%.0f")})
        else: st.info(f"No past sales goal records found for {TARGET_SALES_GOAL_YEAR} (excluding current quarter).")
    st.markdown('</div>', unsafe_allow_html=True)


elif nav == "💰 Payment Collection Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)

    TARGET_PAYMENT_YEAR = 2025 # Using a separate constant for clarity, though it's the same year
    current_quarter_for_payment_display = get_quarter_str_for_year(TARGET_PAYMENT_YEAR, use_current_moment=True)
    status_options_payment = ["Not Started", "Collection In Progress", "Collection Complete", "Overdue", "Cancelled"] # Slightly different statuses

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action_payment = st.radio("Action:", ["View Team Collection Progress", f"Set/Edit Collection Goal for {TARGET_PAYMENT_YEAR}"],
            key="admin_payment_action_2025_q", horizontal=True)

        if admin_action_payment == "View Team Collection Progress":
            st.markdown(f"<h5>Team Payment Collection Progress for {current_quarter_for_payment_display}</h5>", unsafe_allow_html=True)
            employee_users = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users: st.info("No employees found.")
            else:
                summary_data_payment = []
                for emp_name in employee_users:
                    user_info_payment = USERS.get(emp_name, {})
                    emp_current_payment_goal = payment_goals_df[(payment_goals_df["Username"].astype(str) == str(emp_name)) & (payment_goals_df["MonthYear"].astype(str) == str(current_quarter_for_payment_display))]
                    target, achieved, prog_val = 0.0, 0.0, 0.0
                    goal_desc, status_val = "Not Set", "N/A" # Default status for payment
                    if not emp_current_payment_goal.empty:
                        p_data = emp_current_payment_goal.iloc[0]
                        target = pd.to_numeric(p_data.get("TargetAmount"), errors='coerce').fillna(0.0)
                        achieved = pd.to_numeric(p_data.get("AchievedAmount"), errors='coerce').fillna(0.0)
                        if target > 0: prog_val = min(achieved / target, 1.0)
                        goal_desc = p_data.get("GoalDescription", "N/A")
                        status_val = p_data.get("Status", "N/A")
                    summary_data_payment.append({"Photo": user_info_payment.get("profile_photo",""), "Employee": emp_name, "Position": user_info_payment.get("position","N/A"),
                                                 "Goal": goal_desc, "Target Collection": target, "Amount Collected": achieved, "Progress": prog_val, "Status": status_val})
                if summary_data_payment:
                    st.dataframe(pd.DataFrame(summary_data_payment), use_container_width=True, hide_index=True, column_config={
                        "Photo": st.column_config.ImageColumn("Pic", width="small"), "Target Collection": st.column_config.NumberColumn("Target (₹)", format="%.0f"),
                        "Amount Collected": st.column_config.NumberColumn("Collected (₹)", format="%.0f"), "Progress": st.column_config.ProgressColumn("Progress", format="%.0f%%", min_value=0, max_value=1)})
                
                # Option to show chart for team payment progress
                # team_payment_df_for_chart = payment_goals_df[payment_goals_df["MonthYear"].str.startswith(str(TARGET_PAYMENT_YEAR))]
                # if not team_payment_df_for_chart.empty:
                #    render_goal_chart(team_payment_df_for_chart.groupby('MonthYear', as_index=False)[['TargetAmount', 'AchievedAmount']].sum(), "Overall Team Payment Collection vs Target 2025")


        elif admin_action_payment == f"Set/Edit Collection Goal for {TARGET_PAYMENT_YEAR}":
            st.markdown(f"<h5>Set or Update Payment Collection Goal ({TARGET_PAYMENT_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options_payment = [u for u, d in USERS.items() if d["role"] == "employee"]
            current_selected_employee_payment = None
            if not employee_options_payment: st.warning("No employees available.")
            else:
                if "payment_goal_sel_emp_2025_q" not in st.session_state or st.session_state.payment_goal_sel_emp_2025_q not in employee_options_payment:
                    st.session_state.payment_goal_sel_emp_2025_q = employee_options_payment[0]
                try: emp_radio_idx_payment = employee_options_payment.index(st.session_state.payment_goal_sel_emp_2025_q)
                except ValueError: emp_radio_idx_payment = 0; st.session_state.payment_goal_sel_emp_2025_q = employee_options_payment[0] if employee_options_payment else None
                
                selected_emp_radio_payment = st.radio("Select Employee:", employee_options_payment, index=emp_radio_idx_payment, key="payment_goal_emp_radio_2025_q", horizontal=True)
                if st.session_state.payment_goal_sel_emp_2025_q != selected_emp_radio_payment:
                    st.session_state.payment_goal_sel_emp_2025_q = selected_emp_radio_payment
                current_selected_employee_payment = st.session_state.payment_goal_sel_emp_2025_q

            quarter_options_payment = [f"{TARGET_PAYMENT_YEAR}-Q{i}" for i in range(1, 5)]
            current_selected_period_payment = None
            if not quarter_options_payment: st.error("Quarter options list empty!")
            else:
                default_period_payment = get_quarter_str_for_year(TARGET_PAYMENT_YEAR, use_current_moment=True)
                if "payment_goal_target_period_2025_q" not in st.session_state or st.session_state.payment_goal_target_period_2025_q not in quarter_options_payment:
                    st.session_state.payment_goal_target_period_2025_q = default_period_payment if default_period_payment in quarter_options_payment else quarter_options_payment[0]
                try: period_radio_idx_payment = quarter_options_payment.index(st.session_state.payment_goal_target_period_2025_q)
                except ValueError: period_radio_idx_payment = quarter_options_payment.index(default_period_payment) if default_period_payment in quarter_options_payment else 0; st.session_state.payment_goal_target_period_2025_q = quarter_options_payment[period_radio_idx_payment]
                
                selected_period_radio_payment = st.radio(f"Goal Period ({TARGET_PAYMENT_YEAR} - Quarter):", options=quarter_options_payment, index=period_radio_idx_payment, key="payment_goal_period_radio_2025_q", horizontal=True)
                if st.session_state.payment_goal_target_period_2025_q != selected_period_radio_payment:
                    st.session_state.payment_goal_target_period_2025_q = selected_period_radio_payment
                current_selected_period_payment = st.session_state.payment_goal_target_period_2025_q
            
            if current_selected_employee_payment and current_selected_period_payment:
                existing_p_goal = payment_goals_df[(payment_goals_df["Username"].astype(str) == str(current_selected_employee_payment)) & (payment_goals_df["MonthYear"].astype(str) == str(current_selected_period_payment))]
                p_desc, p_target, p_achieved, p_status_val = "", 0.0, 0.0, "Not Started"
                if not existing_p_goal.empty:
                    p_g_data = existing_p_goal.iloc[0]
                    p_desc = p_g_data.get("GoalDescription", "")
                    raw_p_target = p_g_data.get("TargetAmount"); p_target = 0.0 if pd.isna(raw_p_target) else (0.0 if pd.isna(pd.to_numeric(raw_p_target, errors='coerce')) else float(pd.to_numeric(raw_p_target, errors='coerce')))
                    raw_p_achieved = p_g_data.get("AchievedAmount"); p_achieved = 0.0 if pd.isna(raw_p_achieved) else (0.0 if pd.isna(pd.to_numeric(raw_p_achieved, errors='coerce')) else float(pd.to_numeric(raw_p_achieved, errors='coerce')))
                    p_status_val = p_g_data.get("Status", "Not Started")
                    st.info(f"Editing payment collection goal for {current_selected_employee_payment} for {current_selected_period_payment}.")

                form_key_payment = f"set_payment_goal_form_{current_selected_employee_payment}_{current_selected_period_payment}_2025q"
                with st.form(key=form_key_payment):
                    new_p_desc = st.text_area("Payment Goal Description:", value=p_desc, key=f"desc_payment_2025q_{current_selected_employee_payment}_{current_selected_period_payment}")
                    new_p_target = st.number_input("Target Collection (INR):", value=p_target, min_value=0.0, step=1000.0, format="%.2f", key=f"target_payment_2025q_{current_selected_employee_payment}_{current_selected_period_payment}")
                    new_p_achieved = st.number_input("Amount Collected (INR):", value=p_achieved, min_value=0.0, step=100.0, format="%.2f", key=f"achieved_payment_2025q_{current_selected_employee_payment}_{current_selected_period_payment}")
                    status_radio_idx_payment = status_options_payment.index(p_status_val) if p_status_val in status_options_payment else 0
                    new_p_status = st.radio("Status:", options=status_options_payment, index=status_radio_idx_payment, key=f"status_payment_radio_{current_selected_employee_payment}_{current_selected_period_payment}", horizontal=True)
                    submitted_payment = st.form_submit_button("Save Payment Goal")

                if submitted_payment:
                    if not new_p_desc.strip(): st.warning("Description needed.")
                    elif new_p_target <= 0 and new_p_status not in ["Cancelled", "On Hold", "Not Started"]: st.warning("Target > 0 unless status is Cancelled/On Hold/Not Started.")
                    else:
                        if not existing_p_goal.empty:
                            payment_goals_df.loc[existing_p_goal.index[0]] = [current_selected_employee_payment, current_selected_period_payment, new_p_desc, new_p_target, new_p_achieved, new_p_status]
                            msg_verb="updated"
                        else:
                            new_p_entry_data = {"Username": current_selected_employee_payment, "MonthYear": current_selected_period_payment, "GoalDescription": new_p_desc,
                                                "TargetAmount": new_p_target, "AchievedAmount": new_p_achieved, "Status": new_p_status}
                            for col_name in PAYMENT_GOALS_COLUMNS:
                                if col_name not in new_p_entry_data: new_p_entry_data[col_name] = pd.NA
                            new_p_entry = pd.DataFrame([new_p_entry_data], columns=PAYMENT_GOALS_COLUMNS)
                            payment_goals_df = pd.concat([payment_goals_df, new_p_entry], ignore_index=True)
                            msg_verb="set"
                        try:
                            payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                            st.session_state.user_message = f"Payment goal for {current_selected_employee_payment} ({current_selected_period_payment}) {msg_verb}!"
                            st.session_state.message_type = "success"; st.rerun()
                        except Exception as e:
                            st.session_state.user_message = f"Error saving payment goal: {e}"
                            st.session_state.message_type = "error"; st.rerun()
    else: # Employee Payment Collection Goal View
        st.markdown("<h4>My Payment Collection Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        my_all_payment_goals = payment_goals_df[payment_goals_df["Username"].astype(str) == str(current_user["username"])].copy()
        if not my_all_payment_goals.empty:
            for col_n in ["TargetAmount", "AchievedAmount"]: my_all_payment_goals[col_n] = pd.to_numeric(my_all_payment_goals[col_n], errors='coerce').fillna(0.0)

        current_p_goal_emp = my_all_payment_goals[my_all_payment_goals["MonthYear"].astype(str) == str(current_quarter_for_payment_display)]
        st.markdown(f"<h5>Current Collection Period: {current_quarter_for_payment_display}</h5>", unsafe_allow_html=True)
        if not current_p_goal_emp.empty:
            p_g_e = current_p_goal_emp.iloc[0]
            p_target_amt = pd.to_numeric(p_g_e.get("TargetAmount"), errors='coerce').fillna(0.0)
            p_achieved_amt = pd.to_numeric(p_g_e.get("AchievedAmount"), errors='coerce').fillna(0.0)
            p_prog_val = min(p_achieved_amt / p_target_amt, 1.0) if p_target_amt > 0 else 0.0
            st.markdown(f"**Description:** {p_g_e.get('GoalDescription', 'N/A')}")
            pc1,pc2,pc3 = st.columns(3)
            pc1.metric("Target Collection", f"₹{p_target_amt:,.0f}"); pc2.metric("Amount Collected", f"₹{p_achieved_amt:,.0f}")
            with pc3: st.metric("Status", p_g_e.get('Status','In Progress')); st.progress(p_prog_val); st.caption(f"{p_prog_val*100:.1f}% Collected")
            st.markdown("---")
            st.markdown(f"<h6>Update My Collection for {current_quarter_for_payment_display}</h6>", unsafe_allow_html=True)
            with st.form(key=f"update_payment_ach_form_{current_user['username']}_2025q"):
                new_p_ach_val = st.number_input("My Total Amount Collected (INR):", value=float(p_achieved_amt), min_value=0.0, step=100.0, format="%.2f", key=f"emp_payment_ach_update_{current_quarter_for_payment_display}")
                submit_upd_payment = st.form_submit_button("Update Amount Collected")
            if submit_upd_payment:
                idx_to_update_payment = current_p_goal_emp.index[0]
                payment_goals_df.loc[idx_to_update_payment, "AchievedAmount"] = new_p_ach_val
                payment_goals_df.loc[idx_to_update_payment, "Status"] = "Collection Complete" if new_p_ach_val >= p_target_amt and p_target_amt > 0 else "Collection In Progress"
                try:
                    payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                    st.session_state.user_message = "Collected amount updated!"
                    st.session_state.message_type = "success"; st.rerun()
                except Exception as e:
                    st.session_state.user_message = f"Error updating collected amount: {e}"
                    st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No payment collection goal set for you for {current_quarter_for_payment_display}. Contact admin.")

        st.markdown("---")
        st.markdown("<h5>My Payment Collection Visualized (2025)</h5>", unsafe_allow_html=True)
        employee_payment_goals_2025 = my_all_payment_goals[my_all_payment_goals["MonthYear"].astype(str).str.startswith(str(TARGET_PAYMENT_YEAR))]
        if not employee_payment_goals_2025.empty:
            render_goal_chart(employee_payment_goals_2025, f"{current_user['username']}'s Payment Collection vs Target {TARGET_PAYMENT_YEAR}")
        else:
            st.info(f"No payment collection data to visualize for {TARGET_PAYMENT_YEAR}.")

        st.markdown("---")
        st.markdown("<h5>My Past Payment Collection Goals (2025)</h5>", unsafe_allow_html=True)
        past_p_goals = my_all_payment_goals[(my_all_payment_goals["MonthYear"].astype(str).str.startswith(str(TARGET_PAYMENT_YEAR))) & (my_all_payment_goals["MonthYear"].astype(str) != str(current_quarter_for_payment_display))].sort_values(by="MonthYear", ascending=False)
        if not past_p_goals.empty:
            st.dataframe(past_p_goals[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]], hide_index=True, use_container_width=True,
                         column_config={"TargetAmount":st.column_config.NumberColumn(format="₹%.0f"), "AchievedAmount":st.column_config.NumberColumn(format="₹%.0f")})
        else: st.info(f"No past payment collection goal records found for {TARGET_PAYMENT_YEAR} (excluding current quarter).")
    st.markdown('</div>', unsafe_allow_html=True)


elif nav == "📊 View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if current_user["role"] == "admin":
        st.markdown("<h3>📊 Employee Data Logs</h3>", unsafe_allow_html=True) # Use h3 from card styling
        employee_names = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
        if not employee_names: st.info("No employees found or no employee data to display.")
        else:
            for emp_name in employee_names:
                user_info = USERS.get(emp_name, {})
                profile_col1, profile_col2 = st.columns([1, 4])
                with profile_col1:
                    if user_info.get("profile_photo") and os.path.exists(user_info.get("profile_photo")):
                        st.image(user_info.get("profile_photo"), width=80)
                with profile_col2:
                    st.markdown(f"<h4 class='employee-section-header' style='margin-bottom: 5px; margin-top:0px; border-bottom: none; font-size: 1.2em;'>👤 {emp_name}</h4>", unsafe_allow_html=True)
                    st.markdown(f"**Position:** {user_info.get('position', 'N/A')}")
                st.markdown("---")

                # Attendance
                st.markdown("<h5 class='record-type-header'>🕒 Attendance Records:</h5>", unsafe_allow_html=True)
                emp_attendance = attendance_df[attendance_df["Username"].astype(str) == str(emp_name)].copy()
                if not emp_attendance.empty:
                    display_cols_att = [col for col in ATTENDANCE_COLUMNS if col != 'Username']
                    admin_att_display = emp_attendance[display_cols_att].copy()
                    for col_name_map in ['Latitude', 'Longitude']:
                        if col_name_map in admin_att_display.columns:
                            admin_att_display[col_name_map] = pd.to_numeric(admin_att_display[col_name_map], errors='coerce').apply(lambda x: f"{x:.4f}" if pd.notna(x) else "N/A")
                    st.dataframe(admin_att_display, use_container_width=True, hide_index=True)
                    # Map - Geolocation is disabled, so map won't show relevant data
                    # st.markdown("<h6 class='allowance-summary-header'>🗺️ Attendance Locations Map:</h6>", unsafe_allow_html=True)
                    # map_data_admin = emp_attendance.dropna(subset=['Latitude', 'Longitude']).copy() # This will be empty
                    # if not map_data_admin.empty: st.map(map_data_admin.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'}))
                    # else: st.caption(f"No location data for map for {emp_name} (geolocation disabled).")
                else: st.caption(f"No attendance records for {emp_name}.")

                # Allowances
                st.markdown("<h5 class='record-type-header' style='margin-top:25px;'>💰 Allowance Section:</h5>", unsafe_allow_html=True)
                emp_allowances = allowance_df[allowance_df["Username"].astype(str) == str(emp_name)].copy()
                if not emp_allowances.empty:
                    emp_allowances['Amount'] = pd.to_numeric(emp_allowances['Amount'], errors='coerce').fillna(0.0)
                    st.metric(label=f"Grand Total Allowance for {emp_name}", value=f"₹{emp_allowances['Amount'].sum():,.2f}")
                    st.markdown("<h6 class='allowance-summary-header'>📅 Monthly Allowance Summary:</h6>", unsafe_allow_html=True)
                    emp_allow_sum = emp_allowances.dropna(subset=['Amount']).copy()
                    if 'Date' in emp_allow_sum.columns:
                        emp_allow_sum['Date'] = pd.to_datetime(emp_allow_sum['Date'], errors='coerce')
                        emp_allow_sum.dropna(subset=['Date'], inplace=True) # Remove rows with invalid dates
                    if not emp_allow_sum.empty and 'Date' in emp_allow_sum.columns:
                        emp_allow_sum['YearMonth'] = emp_allow_sum['Date'].dt.strftime('%Y-%m')
                        monthly_summary = emp_allow_sum.groupby('YearMonth')['Amount'].sum().reset_index().sort_values('YearMonth', ascending=False)
                        st.dataframe(monthly_summary.rename(columns={'Amount': 'Total Amount (₹)', 'YearMonth': 'Month'}), use_container_width=True, hide_index=True)
                    else: st.caption("No valid allowance data for monthly summary.")
                    st.markdown("<h6 class='allowance-summary-header' style='margin-top:20px;'>📋 Detailed Allowance Requests:</h6>", unsafe_allow_html=True)
                    st.dataframe(emp_allowances[[c for c in ALLOWANCE_COLUMNS if c != 'Username']], use_container_width=True, hide_index=True)
                else: st.caption(f"No allowance requests for {emp_name}.")
                
                # Sales Goals for this employee
                st.markdown("<h5 class='record-type-header' style='margin-top:25px;'>🎯 Sales Goal History (2025):</h5>", unsafe_allow_html=True)
                emp_sales_goals_all = goals_df[(goals_df["Username"].astype(str) == str(emp_name)) & (goals_df["MonthYear"].astype(str).str.startswith(str(TARGET_SALES_GOAL_YEAR)))].copy()
                if not emp_sales_goals_all.empty:
                    for col_n in ["TargetAmount", "AchievedAmount"]: emp_sales_goals_all[col_n] = pd.to_numeric(emp_sales_goals_all[col_n], errors='coerce').fillna(0.0)
                    st.dataframe(emp_sales_goals_all[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]], hide_index=True, use_container_width=True,
                                 column_config={"TargetAmount":st.column_config.NumberColumn(format="₹%.0f"), "AchievedAmount":st.column_config.NumberColumn(format="₹%.0f")})
                    render_goal_chart(emp_sales_goals_all, f"{emp_name}'s Sales Goals vs Achievement {TARGET_SALES_GOAL_YEAR}")
                else:
                    st.caption(f"No sales goals found for {emp_name} for {TARGET_SALES_GOAL_YEAR}.")

                # Payment Collection Goals for this employee
                st.markdown("<h5 class='record-type-header' style='margin-top:25px;'>💰 Payment Collection Goal History (2025):</h5>", unsafe_allow_html=True)
                emp_payment_goals_all = payment_goals_df[(payment_goals_df["Username"].astype(str) == str(emp_name)) & (payment_goals_df["MonthYear"].astype(str).str.startswith(str(TARGET_PAYMENT_YEAR)))].copy()
                if not emp_payment_goals_all.empty:
                    for col_n in ["TargetAmount", "AchievedAmount"]: emp_payment_goals_all[col_n] = pd.to_numeric(emp_payment_goals_all[col_n], errors='coerce').fillna(0.0)
                    st.dataframe(emp_payment_goals_all[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]], hide_index=True, use_container_width=True,
                                 column_config={"TargetAmount":st.column_config.NumberColumn("Target Coll. (₹)", format="%.0f"), "AchievedAmount":st.column_config.NumberColumn("Amt. Collected (₹)", format="%.0f")})
                    render_goal_chart(emp_payment_goals_all, f"{emp_name}'s Payment Collection vs Target {TARGET_PAYMENT_YEAR}")

                else:
                    st.caption(f"No payment collection goals found for {emp_name} for {TARGET_PAYMENT_YEAR}.")


                if emp_name != employee_names[-1]: st.markdown("<hr style='margin-top: 25px; margin-bottom:10px;'>", unsafe_allow_html=True)

    else: # Employee's Own View
        st.markdown("<h3>📊 My Profile & Logs</h3>", unsafe_allow_html=True)
        my_user_info = USERS.get(current_user["username"], {})
        profile_col1_my, profile_col2_my = st.columns([1, 4])
        with profile_col1_my:
            if my_user_info.get("profile_photo") and os.path.exists(my_user_info.get("profile_photo")):
                st.image(my_user_info.get("profile_photo"), width=80)
        with profile_col2_my:
            st.markdown(f"**Name:** {current_user['username']}")
            st.markdown(f"**Position:** {my_user_info.get('position', 'N/A')}")
        st.markdown("---")

        st.markdown("<h4 class='record-type-header'>📅 My Attendance History</h4>", unsafe_allow_html=True)
        my_att_raw = attendance_df[attendance_df["Username"].astype(str) == str(current_user["username"])].copy()
        final_display_df = pd.DataFrame()
        my_att_proc = pd.DataFrame()

        if not my_att_raw.empty:
            my_att_proc = my_att_raw.copy()
            my_att_proc['Timestamp'] = pd.to_datetime(my_att_proc['Timestamp'], errors='coerce')
            my_att_proc.dropna(subset=['Timestamp'], inplace=True)
            if not my_att_proc.empty:
                my_att_proc['Latitude'] = pd.to_numeric(my_att_proc['Latitude'], errors='coerce')
                my_att_proc['Longitude'] = pd.to_numeric(my_att_proc['Longitude'], errors='coerce')
                my_att_proc['DateOnly'] = my_att_proc['Timestamp'].dt.date
                check_ins_df = my_att_proc[my_att_proc['Type'] == 'Check-In'].copy()
                check_outs_df = my_att_proc[my_att_proc['Type'] == 'Check-Out'].copy()
                first_check_in_cols = ['DateOnly', 'Check-In FullTime', 'Check-In Latitude', 'Check-In Longitude']
                first_check_ins_sel = pd.DataFrame(columns=first_check_in_cols)
                if not check_ins_df.empty:
                    first_check_ins_grouped = check_ins_df.loc[check_ins_df.groupby('DateOnly')['Timestamp'].idxmin()]
                    first_check_ins_sel = first_check_ins_grouped[['DateOnly', 'Timestamp', 'Latitude', 'Longitude']].rename(
                        columns={'Timestamp': 'Check-In FullTime', 'Latitude': 'Check-In Latitude', 'Longitude': 'Check-In Longitude'})
                last_check_out_cols = ['DateOnly', 'Check-Out FullTime', 'Check-Out Latitude', 'Check-Out Longitude']
                last_check_outs_sel = pd.DataFrame(columns=last_check_out_cols)
                if not check_outs_df.empty:
                    last_check_outs_grouped = check_outs_df.loc[check_outs_df.groupby('DateOnly')['Timestamp'].idxmax()]
                    last_check_outs_sel = last_check_outs_grouped[['DateOnly', 'Timestamp', 'Latitude', 'Longitude']].rename(
                        columns={'Timestamp': 'Check-Out FullTime', 'Latitude': 'Check-Out Latitude', 'Longitude': 'Check-Out Longitude'})
                for df_sel in [first_check_ins_sel, last_check_outs_sel]:
                    if 'DateOnly' in df_sel.columns and not df_sel.empty:
                        df_sel['DateOnly'] = pd.to_datetime(df_sel['DateOnly']).dt.date
                if not first_check_ins_sel.empty and not last_check_outs_sel.empty: combined_df = pd.merge(first_check_ins_sel, last_check_outs_sel, on='DateOnly', how='outer')
                elif not first_check_ins_sel.empty:
                    combined_df = first_check_ins_sel.copy()
                    for col_name_c in last_check_out_cols[1:]:
                        if 'Time' in col_name_c: combined_df[col_name_c] = pd.NaT
                        else: combined_df[col_name_c] = pd.NA
                elif not last_check_outs_sel.empty:
                    combined_df = last_check_outs_sel.copy()
                    for col_name_c in first_check_in_cols[1:]:
                        if 'Time' in col_name_c: combined_df[col_name_c] = pd.NaT
                        else: combined_df[col_name_c] = pd.NA
                else:
                    all_combined_cols = list(dict.fromkeys(first_check_in_cols + last_check_out_cols))
                    combined_df = pd.DataFrame(columns=all_combined_cols)

                if not combined_df.empty:
                    combined_df = combined_df.sort_values(by='DateOnly', ascending=False, ignore_index=True)
                    for ft_col in ['Check-In FullTime', 'Check-Out FullTime']:
                        if ft_col in combined_df.columns: combined_df[ft_col] = pd.to_datetime(combined_df[ft_col], errors='coerce')
                    def format_duration(row):
                        if pd.notna(row.get('Check-In FullTime')) and pd.notna(row.get('Check-Out FullTime')) and row['Check-Out FullTime'] > row['Check-In FullTime']:
                            secs = (row['Check-Out FullTime'] - row['Check-In FullTime']).total_seconds(); return f"{int(secs//3600)}h {int((secs%3600)//60)}m"
                        return "N/A"
                    combined_df['Duration'] = combined_df.apply(format_duration, axis=1)
                    for t_col, new_name in [('Check-In FullTime', 'Check-In Time'), ('Check-Out FullTime', 'Check-Out Time')]:
                        combined_df[new_name] = combined_df.get(t_col, pd.Series(dtype='datetime64[ns]')).apply(lambda x: x.strftime('%H:%M:%S') if pd.notna(x) else 'N/A')
                    combined_df['Date'] = combined_df.get('DateOnly', pd.Series(dtype='object')).apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else 'N/A')
                    final_cols = ['Date', 'Check-In Time', 'Check-In Latitude', 'Check-In Longitude', 'Check-Out Time', 'Check-Out Latitude', 'Check-Out Longitude', 'Duration']
                    final_display_df = combined_df[[c for c in final_cols if c in combined_df.columns]].copy()
                    final_display_df.rename(columns={'Check-In Time': 'Check-In', 'Check-In Latitude': 'In Lat', 'Check-In Longitude': 'In Lon', 'Check-Out Time': 'Check-Out', 'Check-Out Latitude': 'Out Lat', 'Check-Out Longitude': 'Out Lon'}, inplace=True)
                    for loc_col in ['In Lat', 'In Lon', 'Out Lat', 'Out Lon']:
                        if loc_col in final_display_df.columns: final_display_df[loc_col] = final_display_df[loc_col].apply(lambda x: f"{x:.4f}" if pd.notna(x) and isinstance(x, (float,int)) else ("N/A" if pd.isna(x) else str(x)))
        if not final_display_df.empty: st.dataframe(final_display_df, use_container_width=True, hide_index=True)
        elif my_att_raw.empty: st.info("You have no attendance records yet.")
        else: st.info("No processed attendance data (check timestamp formats).")

        # Map disabled as geolocation is disabled
        # st.markdown("<h6 class='allowance-summary-header'>🗺️ My Attendance Locations Map:</h6>", unsafe_allow_html=True)
        # if not my_att_proc.empty:
        #     my_map_data = my_att_proc.dropna(subset=['Latitude', 'Longitude']).copy()
        #     if not my_map_data.empty: st.map(my_map_data.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'}))
        #     else: st.info("No valid location data for map.")
        # elif my_att_raw.empty: st.info("No attendance records for map.")
        # else: st.info("No valid attendance data with locations for map (geolocation disabled).")

        st.markdown("<h4 class='record-type-header' style='margin-top:25px;'>🧾 My Allowance Request History</h4>", unsafe_allow_html=True)
        my_allowances = allowance_df[allowance_df["Username"].astype(str) == str(current_user["username"])].copy()
        if not my_allowances.empty: st.dataframe(my_allowances[[c for c in ALLOWANCE_COLUMNS if c != 'Username' and c in my_allowances.columns]], use_container_width=True, hide_index=True)
        else: st.info("You have not submitted any allowance requests yet.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- REMOVE ORPHANED BADGE LINES ---
# status_badge = f"<span class='badge {badge_color}'>{status}</span>" # This line was causing NameError
# st.markdown(f"Status: {status_badge}", unsafe_allow_html=True)     # This line was causing NameError
# badge_color = "green" if status == "Achieved" else "orange" if status == "In Progress" else "red" # This line was causing NameError
