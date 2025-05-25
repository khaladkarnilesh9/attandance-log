import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import pytz
import sys
import altair as alt

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
        color=alt.Color('Metric:N', scale=alt.Scale(range=["#3498db", "#2ecc71"])),
        tooltip=["MonthYear", "Metric", "Amount"]
    ).properties(
        title=title,
        width="container"
    )
    st.altair_chart(chart, use_container_width=True)


# from streamlit_geolocation import streamlit_geolocation # Geolocation is disabled

# --- Pillow for placeholder image generation (optional) --
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

html_css = """
<style>
    /* --- General --- */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f0f2f5; /* Light gray background */
        color: #333;
    }
    /* --- Titles & Headers --- */
    h1, h2 { /* Global H1, H2 */
        color: #1c4e80; /* Dark blue for headers */
    }
    .main .block-container > div:first-child > div:first-child > div:first-child > h1 { /* Main page title */
        text-align: center;
        font-size: 2.5em;
        padding-bottom: 20px;
        border-bottom: 2px solid #70a1d7;
        margin-bottom: 30px;
    }
    /* --- Card Styling --- */
    .card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
    }
    .card h3 { /* Page subheader inside card, e.g., "Digital Attendance" */
        margin-top: 0;
        color: #1c4e80;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 10px;
        margin-bottom: 20px;
        font-size: 1.5em;
    }
    .card h4 { /* Section headers inside card, e.g., "Admin: Manage Goals", "My Sales Goals" */
        color: #2070c0;
        margin-top: 25px;
        margin-bottom: 15px;
        font-size: 1.25em;
        padding-bottom: 5px;
        border-bottom: 1px dashed #d0d0d0;
    }
     .card h5 { /* Sub-section headers, e.g., "Team Goal Progress", "Attendance Records:" */
        font-size: 1.1em;
        color: #333;
        margin-top: 20px; /* Increased top margin slightly */
        margin-bottom: 10px;
        font-weight: 600;
    }
    .card h6 { /* Small text headers, e.g., for radio groups, map titles */
        font-size: 0.95em; /* Slightly larger for better readability */
        color: #495057;
        margin-top: 15px; /* Added top margin */
        margin-bottom: 8px;
        font-weight: 500;
    }
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

    /* --- Input Fields (MODIFIED SECTION) --- */
    .stTextInput input, 
    .stNumberInput input, 
    .stTextArea textarea, 
    .stSelectbox div[data-baseweb="select"] > div { /* General selectbox styling for consistency */
        border-radius: 5px !important; 
        border: 1px solid #ced4da !important;
        padding: 10px !important; 
        font-size: 1em !important; 
        color: #212529 !important;      /* Ensure dark text color */
        background-color: #fff !important; /* Ensure white background */
    }
    /* Ensure placeholder text is also visible if it was an issue */
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #6c757d !important; /* A standard placeholder color */
        opacity: 1; /* Ensure it's not transparent */
    }

    .stTextArea textarea { 
        min-height: 100px;
        /* The color and background should be inherited from the rule above */
    }

    /* If inputs are specifically within a card and need more specific overriding: */
    .card .stTextInput input,
    .card .stNumberInput input,
    .card .stTextArea textarea {
        color: #212529 !important; 
        background-color: #fff !important;
    }
    /* --- END OF MODIFIED INPUT FIELDS SECTION --- */

    /* --- Sidebar --- */
    [data-testid="stSidebar"] { background-color: #1c4e80; padding: 20px !important; }
    [data-testid="stSidebar"] .sidebar-content { padding-top: 20px; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] div, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ffffff !important; }
    [data-testid="stSidebar"] .stRadio > label { font-size: 1.1em !important; color: #a9d6e5 !important; padding-bottom: 8px; }
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] > label { color: #ffffff !important; font-weight: bold; }
    .welcome-text { font-size: 1.3em; font-weight: bold; margin-bottom: 25px; text-align: center; color: #ffffff; border-bottom: 1px solid #70a1d7; padding-bottom: 15px;}

    /* --- Dataframe Styling --- */
    .stDataFrame { width: 100%; border: 1px solid #d1d9e1; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.06); margin-bottom: 20px; }
    .stDataFrame table { width: 100%; border-collapse: collapse; }
    .stDataFrame table thead th { background-color: #f0f2f5; color: #1c4e80; font-weight: 600; text-align: left; padding: 12px 15px; border-bottom: 2px solid #c5cdd5; font-size: 0.9em; }
    .stDataFrame table tbody td { padding: 10px 15px; border-bottom: 1px solid #e7eaf0; vertical-align: middle; color: #333; font-size: 0.875em; }
    .stDataFrame table tbody tr:last-child td { border-bottom: none; }
    .stDataFrame table tbody tr:hover { background-color: #e9ecef; }

    /* --- Columns for buttons --- */
    .button-column-container > div[data-testid="stHorizontalBlock"] { gap: 15px; }
    .button-column-container .stButton button { width: 100%; }

    /* Horizontal Radio Buttons */
    div[role="radiogroup"] { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px; }
    div[role="radiogroup"] > label { background-color: #86a7c7; padding: 8px 15px; border-radius: 20px; border: 1px solid #ced4da; cursor: pointer; transition: background-color 0.2s ease, border-color 0.2s ease; font-size: 0.95em; }
    div[role="radiogroup"] > label:hover { background-color: #dde2e6; border-color: #adb5bd; }
    div[role="radiogroup"] div[data-baseweb="radio"][aria-checked="true"] + label { background-color: #2070c0 !important; color: white !important; border-color: #1c4e80 !important; font-weight: 500; }

    /* --- Employee/Record Specific Headers (used in View Logs and Goal Tracker) --- */
    .employee-section-header { /* For Admin view: "Records for: Employee Name" */
        color: #2070c0; margin-top: 30px; border-bottom: 1px solid #e0e0e0; padding-bottom: 5px; font-size: 1.3em;
    }
    .record-type-header { /* For "Attendance Records:", "Allowance Section:" */
        font-size: 1.1em; color: #333; margin-top: 20px; margin-bottom: 10px; font-weight: 600;
    }
    .allowance-summary-header { /* For map titles, "Monthly Allowance Summary" */
        font-size: 1.0em; color: #495057; margin-top: 15px; margin-bottom: 8px; font-weight: 550;
    }
    div[data-testid="stImage"] > img { border-radius: 8px; border: 2px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stProgress > div > div { background-color: #2070c0 !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.9em !important; color: #555 !important; }

    /* --- Custom Notification Styling --- */
    .custom-notification {
        padding: 10px 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        font-size: 0.95em;
        border-left: 5px solid;
    }
    .custom-notification.success {
        background-color: #d4edda; /* Light green */
        color: #155724; /* Dark green */
        border-left-color: #28a745; /* Green accent */
    }
    .custom-notification.error {
        background-color: #f8d7da; /* Light red */
        color: #721c24; /* Dark red */
        border-left-color: #dc3545; /* Red accent */
    }
    .custom-notification.warning {
        background-color: #fff3cd; /* Light yellow */
        color: #856404; /* Dark yellow */
        border-left-color: #ffc107; /* Yellow accent */
    }
     .custom-notification.info {
        background-color: #d1ecf1; /* Light blue */
        color: #0c5460; /* Dark blue */
        border-left-color: #17a2b8; /* Blue accent */
    }


        .card {
        background-color: #f9f9f9;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
    }
    .badge.green { background-color: #2ecc71; }
    .badge.red { background-color: #e74c3c; }
    .badge.orange { background-color: #f39c12; }




    
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
                    if nc in columns and nc in df.columns:
                         df[nc] = pd.to_numeric(df[nc], errors='coerce')
                return df
            else: return pd.DataFrame(columns=columns)
        except pd.errors.EmptyDataError: return pd.DataFrame(columns=columns)
        except Exception as e:
            # This error will be shown directly on the page, not suitable for session state message
            st.error(f"Error loading {path}: {e}. Empty DataFrame returned.")
            return pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
        try: df.to_csv(path, index=False)
        except Exception as e: st.warning(f"Could not create {path}: {e}") # Shows directly
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]

attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)

# --- Initialize Session State for Notifications ---
if "user_message" not in st.session_state:
    st.session_state.user_message = None
if "message_type" not in st.session_state:
    st.session_state.message_type = None # e.g., "success", "error", "warning", "info"

# --- Login Page ---
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}

if not st.session_state.auth["logged_in"]:
    st.title("🙂HR Dashboard Login")
    # Display pending messages on login page too, if any (e.g., from a previous logout)
    message_placeholder_login = st.empty()
    if st.session_state.user_message:
        message_placeholder_login.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
        st.session_state.user_message = None # Clear after displaying
        st.session_state.message_type = None

    st.markdown('<div class="login-container card">', unsafe_allow_html=True)
    st.markdown("<h3>🔐 Login</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname")
    pwd = st.text_input("Password", type="password", key="login_pwd")
    if st.button("Login", key="login_button"):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = "Login successful!" # SET MESSAGE
            st.session_state.message_type = "success"         # SET TYPE
            st.rerun()
        else:
            # For errors on the login page, st.error is fine as no immediate rerun
            st.error("Invalid username or password.")
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# --- Main Application ---
st.title("👨‍💼 HR Dashboard")
current_user = st.session_state.auth

# --- Dedicated Message Placeholder for Main App ---
message_placeholder = st.empty()
if st.session_state.user_message:
    message_placeholder.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
    st.session_state.user_message = None # Clear after displaying
    st.session_state.message_type = None
#------------------------------------------------------------------------------------------------
PAYMENT_GOALS_FILE = "payment_goals.csv"
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]

if os.path.exists(PAYMENT_GOALS_FILE):
    payment_goals_df = pd.read_csv(PAYMENT_GOALS_FILE)
else:
    payment_goals_df = pd.DataFrame(columns=PAYMENT_GOALS_COLUMNS)


# --- Sidebar -------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user['username']}!</div>", unsafe_allow_html=True)
    nav_options = ["📆 Attendance", "🧾 Allowance", "🎯 Goal Tracker","💰 Payment Collection Tracker", "📊 View Logs"]
    nav = st.radio("Navigation", nav_options, key="sidebar_nav_main")
    user_sidebar_info = USERS.get(current_user["username"], {})
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]):
        st.image(user_sidebar_info["profile_photo"], width=80, use_column_width='auto')
    st.markdown(f"<p style='text-align:center; font-size:0.9em; color: #e0e0e0;'>{user_sidebar_info.get('position', 'N/A')}</p>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔒 Logout", key="logout_button_sidebar", use_container_width=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully." # SET MESSAGE
        st.session_state.message_type = "info"                  # SET TYPE
        st.rerun()

# --- Main Content Area ---
if nav == "📆 Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)

    lat, lon = None, None 
    st.info("📍 Location services are currently disabled for attendance.", icon="ℹ️")

    st.markdown("---")
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    common_data = {
        "Username": current_user["username"],
        "Latitude": pd.NA,
        "Longitude": pd.NA
    }

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
                st.rerun() # Rerun to show the error message at the top
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
#--------------------------------------------------------------------start-viewlog---------------------------------------------
            for emp_name in employee_names:
                st.markdown(f"--- PROCESSING {emp_name.upper()} ---", unsafe_allow_html=True) # More visible separator
                user_info = USERS.get(emp_name, {})
                
                # --- Profile Info ---
                st.write(f"DEBUG ({emp_name}): Displaying profile info.")
                # ... your profile columns and st.image/st.markdown for position ...
                profile_col1, profile_col2 = st.columns([1, 4])
                with profile_col1:
                    if user_info.get("profile_photo") and os.path.exists(user_info.get("profile_photo")):
                        st.image(user_info.get("profile_photo"), width=80)
                        st.write(f"DEBUG ({emp_name}): Photo displayed.")
                    else:
                        st.write(f"DEBUG ({emp_name}): No photo found or path invalid.")
                with profile_col2:
                    st.markdown(f"<h4 class='employee-section-header' style='margin-bottom: 5px; margin-top:0px; border-bottom: none; font-size: 1.2em;'>👤 {emp_name}</h4>", unsafe_allow_html=True)
                    st.markdown(f"**Position:** {user_info.get('position', 'N/A')}")
                    st.write(f"DEBUG ({emp_name}): Name and Position displayed.")
                st.markdown("---")


                # --- Attendance ---
                st.markdown("<h5 class='record-type-header'>🕒 Attendance Records:</h5>", unsafe_allow_html=True)
                emp_attendance = attendance_df[attendance_df["Username"].astype(str) == str(emp_name)].copy()
                st.write(f"DEBUG ({emp_name}): emp_attendance empty? {emp_attendance.empty}. Shape: {emp_attendance.shape if not emp_attendance.empty else 'N/A'}")
                if not emp_attendance.empty:
                    # ... (your existing processing for admin_att_display) ...
                    display_cols_att = [col for col in ATTENDANCE_COLUMNS if col != 'Username']
                    admin_att_display = emp_attendance[display_cols_att].copy()
                    # ... (formatting lat/lon) ...
                    st.write(f"DEBUG ({emp_name}): admin_att_display for st.dataframe (Attendance):")
                    st.dataframe(admin_att_display, use_container_width=True, hide_index=True) # Check if this renders
                else: 
                    st.caption(f"No attendance records for {emp_name}.")
                    st.write(f"DEBUG ({emp_name}): Displayed 'No attendance records' caption.")

                # --- Allowances ---
                st.markdown("<h5 class='record-type-header' style='margin-top:25px;'>💰 Allowance Section:</h5>", unsafe_allow_html=True)
                emp_allowances = allowance_df[allowance_df["Username"].astype(str) == str(emp_name)].copy()
                st.write(f"DEBUG ({emp_name}): emp_allowances empty? {emp_allowances.empty}. Shape: {emp_allowances.shape if not emp_allowances.empty else 'N/A'}")
                if not emp_allowances.empty:
                    # ... (your existing processing for allowances) ...
                    st.write(f"DEBUG ({emp_name}): Displaying allowance metric and dataframes.")
                    st.metric(label=f"Grand Total Allowance for {emp_name}", value=f"₹{pd.to_numeric(emp_allowances['Amount'], errors='coerce').fillna(0.0).sum():,.2f}")
                    # ... (monthly summary and detailed requests dataframes) ...
                    st.dataframe(emp_allowances[[c for c in ALLOWANCE_COLUMNS if c != 'Username']], use_container_width=True, hide_index=True)
                else: 
                    st.caption(f"No allowance requests for {emp_name}.")
                    st.write(f"DEBUG ({emp_name}): Displayed 'No allowance requests' caption.")

                # --- Sales Goals ---
                st.markdown("<h5 class='record-type-header' style='margin-top:25px;'>🎯 Sales Goal History (2025):</h5>", unsafe_allow_html=True)
                emp_sales_goals_all = goals_df[(goals_df["Username"].astype(str) == str(emp_name)) & (goals_df["MonthYear"].astype(str).str.startswith(str(TARGET_SALES_GOAL_YEAR)))].copy()
                st.write(f"DEBUG ({emp_name}): emp_sales_goals_all empty? {emp_sales_goals_all.empty}. Shape: {emp_sales_goals_all.shape if not emp_sales_goals_all.empty else 'N/A'}")
                if not emp_sales_goals_all.empty:
                    # ... (processing and dataframe) ...
                    st.write(f"DEBUG ({emp_name}): Displaying sales goals dataframe and chart.")
                    st.dataframe(emp_sales_goals_all[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]], hide_index=True, use_container_width=True,
                                 column_config={"TargetAmount":st.column_config.NumberColumn(format="₹%.0f"), "AchievedAmount":st.column_config.NumberColumn(format="%.0f")})
                    render_goal_chart(emp_sales_goals_all, f"{emp_name}'s Sales Goals vs Achievement {TARGET_SALES_GOAL_YEAR}")
                else:
                    st.caption(f"No sales goals found for {emp_name} for {TARGET_SALES_GOAL_YEAR}.")
                    st.write(f"DEBUG ({emp_name}): Displayed 'No sales goals' caption.")

                # --- Payment Collection Goals ---
                st.markdown("<h5 class='record-type-header' style='margin-top:25px;'>💰 Payment Collection Goal History (2025):</h5>", unsafe_allow_html=True)
                emp_payment_goals_all = payment_goals_df[(payment_goals_df["Username"].astype(str) == str(emp_name)) & (payment_goals_df["MonthYear"].astype(str).str.startswith(str(TARGET_PAYMENT_YEAR)))].copy()
                st.write(f"DEBUG ({emp_name}): emp_payment_goals_all empty? {emp_payment_goals_all.empty}. Shape: {emp_payment_goals_all.shape if not emp_payment_goals_all.empty else 'N/A'}")
                if not emp_payment_goals_all.empty:
                    # ... (processing and dataframe) ...
                    st.write(f"DEBUG ({emp_name}): Displaying payment goals dataframe and chart.")
                    st.dataframe(emp_payment_goals_all[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]], hide_index=True, use_container_width=True,
                                 column_config={"TargetAmount":st.column_config.NumberColumn("Target Coll. (₹)", format="%.0f"), "AchievedAmount":st.column_config.NumberColumn("Amt. Collected (₹)", format="%.0f")})
                    render_goal_chart(emp_payment_goals_all, f"{emp_name}'s Payment Collection vs Target {TARGET_PAYMENT_YEAR}")

                else:
                    st.caption(f"No payment collection goals found for {emp_name} for {TARGET_PAYMENT_YEAR}.")
                    st.write(f"DEBUG ({emp_name}): Displayed 'No payment collection goals' caption.")

                if emp_name != employee_names[-1]: st.markdown("<hr style='margin-top: 25px; margin-bottom:10px;'>", unsafe_allow_html=True)
#--------------------------------------------------------------------end-viewlog---------------------------------------------


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
                st.session_state.message_type = "success"
                st.rerun()
            except Exception as e:
                st.session_state.user_message = f"Error saving allowance: {e}"
                st.session_state.message_type = "error"
                st.rerun()
        else:
            # For immediate warnings not followed by rerun, st.warning is fine
            st.warning("Please complete all fields with valid values.")
    st.markdown('</div>', unsafe_allow_html=True)
#-----------------------------------------------------------------------------
# Helper function to get the current quarter string for a GIVEN year
# This is slightly different now as the target year is fixed for goal setting
def get_quarter_str_for_year(year, for_current_display=False):
    # If for_current_display is True, use today's month to determine the quarter for the given year.
    # Otherwise, you might want a fixed default like Q1 of that year.
    # For simplicity in goal setting, we often default to Q1 of the target year.
    # For display of "current" progress, we'll use today's actual quarter but map it to the fixed year.
    
    now_month = get_current_time_in_tz().month # Today's actual month
    
    if 1 <= now_month <= 3:
        quarter_num_str = "Q1"
    elif 4 <= now_month <= 6:
        quarter_num_str = "Q2"
    elif 7 <= now_month <= 9:
        quarter_num_str = "Q3"
    else:  # 10 <= now_month <= 12
        quarter_num_str = "Q4"
        
    return f"{year}-{quarter_num_str}"

#-------------------------------------------------------

# --- Main Goal Tracker Navigation Block ---
if nav == "🎯 Goal Tracker":
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
            if not employee_users:
                st.info("No employees found.")
            else:
                summary_data = []
                for emp_name in employee_users:
                    user_info_gt = USERS.get(emp_name, {})
                    emp_current_goal = goals_df[
                        (goals_df["Username"].astype(str) == str(emp_name)) &
                        (goals_df["MonthYear"].astype(str) == str(current_quarter_for_display))
                    ]
                    target, achieved, prog_val = 0.0, 0.0, 0.0
                    goal_desc, status_val = "Not Set", "N/A"
                    if not emp_current_goal.empty:
                        g_data = emp_current_goal.iloc[0]
                        raw_target = g_data.get("TargetAmount")
                        raw_achieved = g_data.get("AchievedAmount", 0.0)

                        try:
                            achieved = float(raw_achieved)
                        except (ValueError, TypeError):
                            achieved = 0.0

                        try:
                            target = float(raw_target)
                        except (ValueError, TypeError):
                            target = 0.0

                        prog_val = min(achieved / target, 1.0) if target > 0 else 0.0
                        goal_desc = g_data.get("GoalDescription", "N/A")
                        status_val = g_data.get("Status", "N/A")

                    summary_data.append({
                        "Photo": user_info_gt.get("profile_photo", ""),
                        "Employee": emp_name,
                        "Position": user_info_gt.get("position", "N/A"),
                        "Goal": goal_desc,
                        "Target": target,
                        "Achieved": achieved,
                        "Progress": prog_val,
                        "Status": status_val
                    })

                if summary_data:
                    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True,
                                 column_config={
                                     "Photo": st.column_config.ImageColumn("Pic", width="small"),
                                     "Target": st.column_config.NumberColumn("Target (₹)", format="%.0f"),
                                     "Achieved": st.column_config.NumberColumn("Achieved (₹)", format="%.0f"),
                                     "Progress": st.column_config.ProgressColumn("Progress", format="%.0f%%", min_value=0, max_value=1)
                                 })

        elif admin_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set or Update Employee Goal ({TARGET_GOAL_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)

            employee_options = [u for u, d in USERS.items() if d["role"] == "employee"]
            if not employee_options:
                st.warning("No employees available to set goals for.")
            else:
                # Maintain selected employee
                selected_emp = st.radio("Select Employee:", employee_options,
                                        key="goal_emp_radio_2025_q", horizontal=True)

                # Maintain selected quarter
                quarter_options = [f"{TARGET_GOAL_YEAR}-Q{i}" for i in range(1, 5)]
                selected_period = st.radio("Goal Period:", quarter_options,
                                           key="goal_period_radio_2025_q", horizontal=True)

                # Load existing goal if any
                existing_g = goals_df[
                    (goals_df["Username"].astype(str) == str(selected_emp)) &
                    (goals_df["MonthYear"].astype(str) == str(selected_period))
                ]

                g_desc, g_target, g_achieved, g_status = "", 0.0, 0.0, "Not Started"
                if not existing_g.empty:
                    g_data = existing_g.iloc[0]
                    g_desc = g_data.get("GoalDescription", "")
                    g_target = float(pd.to_numeric(g_data.get("TargetAmount", 0.0), errors='coerce') or 0.0)
                    g_achieved = float(pd.to_numeric(g_data.get("AchievedAmount", 0.0), errors='coerce') or 0.0)
                    g_status = g_data.get("Status", "Not Started")
                    st.info(f"Editing existing goal for {selected_emp} - {selected_period}")

                with st.form(key=f"set_goal_form_{selected_emp}_{selected_period}_2025q"):
                    new_desc = st.text_area("Goal Description", value=g_desc)
                    new_target = st.number_input("Target Sales (INR)", value=g_target, min_value=0.0, step=1000.0, format="%.2f")
                    new_achieved = st.number_input("Achieved Sales (INR)", value=g_achieved, min_value=0.0, step=100.0, format="%.2f")
                    new_status = st.radio("Status:", status_options,
                                          index=status_options.index(g_status), horizontal=True)
                    submitted = st.form_submit_button("Save Goal")

                if submitted:
                    if not new_desc.strip():
                        st.warning("Description is required.")
                    elif new_target <= 0 and new_status not in ["Cancelled", "On Hold", "Not Started"]:
                        st.warning("Target must be > 0 unless status is Cancelled/On Hold/Not Started.")
                    else:
                        if not existing_g.empty:
                            goals_df.loc[existing_g.index[0]] = [selected_emp, selected_period, new_desc,
                                                                 new_target, new_achieved, new_status]
                            msg_verb = "updated"
                        else:
                            new_row = {
                                "Username": selected_emp,
                                "MonthYear": selected_period,
                                "GoalDescription": new_desc,
                                "TargetAmount": new_target,
                                "AchievedAmount": new_achieved,
                                "Status": new_status
                            }
                            for col in GOALS_COLUMNS:
                                new_row.setdefault(col, pd.NA)
                            goals_df = pd.concat([goals_df, pd.DataFrame([new_row])], ignore_index=True)
                            msg_verb = "set"

                        try:
                            goals_df.to_csv(GOALS_FILE, index=False)
                            st.success(f"Goal for {selected_emp} ({selected_period}) {msg_verb}!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error saving goal: {e}")
    else:
        # Employee View
        st.markdown("<h4>My Sales Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        my_goals = goals_df[goals_df["Username"].astype(str) == str(current_user["username"])].copy()
        for col in ["TargetAmount", "AchievedAmount"]:
            my_goals[col] = pd.to_numeric(my_goals[col], errors="coerce").fillna(0.0)

        current_g = my_goals[my_goals["MonthYear"] == current_quarter_for_display]
        st.markdown(f"<h5>Current Goal Period: {current_quarter_for_display}</h5>", unsafe_allow_html=True)

        if not current_g.empty:
            g = current_g.iloc[0]
            target_amt = g["TargetAmount"]
            achieved_amt = g["AchievedAmount"]
            progress = min(achieved_amt / target_amt, 1.0) if target_amt > 0 else 0.0

            st.markdown(f"**Description:** {g.get('GoalDescription', 'N/A')}")
            c1, c2, c3 = st.columns(3)
            c1.metric("Target", f"₹{target_amt:,.0f}")
            c2.metric("Achieved", f"₹{achieved_amt:,.0f}")
            with c3:
                st.metric("Status", g.get("Status", "In Progress"))
                st.progress(progress)
                st.caption(f"{progress*100:.1f}% Complete")

            st.markdown("---")
            with st.form(key=f"update_achievement_{current_user['username']}_{current_quarter_for_display}"):
                new_val = st.number_input("Update Achieved Amount (INR):", value=achieved_amt, min_value=0.0, step=100.0, format="%.2f")
                submitted = st.form_submit_button("Update Achievement")

            if submitted:
                idx = current_g.index[0]
                goals_df.loc[idx, "AchievedAmount"] = new_val
                new_status = "Achieved" if new_val >= target_amt and target_amt > 0 else "In Progress"
                goals_df.loc[idx, "Status"] = new_status
                try:
                    goals_df.to_csv(GOALS_FILE, index=False)
                    st.success("Achievement updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving update: {e}")
        else:
            st.info(f"No goal set for {current_quarter_for_display}. Contact your admin.")

        st.markdown("---")
        st.markdown("<h5>My Past Goals (2025)</h5>", unsafe_allow_html=True)
        past_goals = my_goals[
            (my_goals["MonthYear"].astype(str).str.startswith(str(TARGET_GOAL_YEAR))) &
            (my_goals["MonthYear"].astype(str) != current_quarter_for_display)
        ]
        if not past_goals.empty:
            st.dataframe(past_goals[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]],
                         hide_index=True, use_container_width=True,
                         column_config={
                             "TargetAmount": st.column_config.NumberColumn(format="₹%.0f"),
                             "AchievedAmount": st.column_config.NumberColumn(format="₹%.0f")
                         })
        else:
            st.info(f"No past goal records found for {TARGET_GOAL_YEAR}.")

    st.markdown("</div>", unsafe_allow_html=True)

from io import BytesIO

# def download_combined_excel(sales_df, payment_df, current_user):
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         sales_df.to_excel(writer, index=False, sheet_name="Sales Goals")
#         payment_df.to_excel(writer, index=False, sheet_name="Payment Goals")
#         writer.save()
#     return output.getvalue()

# # Only show for admin or current user's data
# sales_export_df = goals_df if current_user["role"] == "admin" else goals_df[goals_df["Username"] == current_user["username"]]
# payment_export_df = payment_goals_df if current_user["role"] == "admin" else payment_goals_df[payment_goals_df["Username"] == current_user["username"]]

# excel_data = download_combined_excel(sales_export_df, payment_export_df, current_user)
# st.download_button("📂 Download Combined Report (Excel)", data=excel_data,
#                    file_name="sales_payment_goals.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    
#-------------------------------------payemnt collection logic-----------------------------------

if nav == "💰 Payment Collection Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)

    TARGET_YEAR = 2025
    current_quarter_display = get_quarter_str_for_year(TARGET_YEAR, for_current_display=True)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Set & Track Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio(
            "Action:",
            ["View Team Progress", f"Set/Edit Collection Target for {TARGET_YEAR}"],
            key="admin_payment_action_2025",
            horizontal=True
        )

        if admin_action == "View Team Progress":
            st.markdown(f"<h5>Team Payment Progress - {current_quarter_display}</h5>", unsafe_allow_html=True)
            employees = [u for u, d in USERS.items() if d["role"] == "employee"]
            summary = []
            for emp in employees:
                user_data = USERS.get(emp, {})
                record = payment_goals_df[
                    (payment_goals_df["Username"] == emp) &
                    (payment_goals_df["MonthYear"] == current_quarter_display)
                ]
                if not record.empty:
                    rec = record.iloc[0]
                    tgt = float(pd.to_numeric(rec["TargetAmount"], errors="coerce") or 0.0)
                    ach = float(pd.to_numeric(rec["AchievedAmount"], errors="coerce") or 0.0)
                    prog = min(ach / tgt, 1.0) if tgt > 0 else 0.0
                    summary.append({
                        "Employee": emp,
                        "Position": user_data.get("position", ""),
                        "Target": tgt,
                        "Collected": ach,
                        "Progress": prog,
                        "Status": rec.get("Status", "N/A")
                    })
            if summary:
                st.dataframe(pd.DataFrame(summary), use_container_width=True,
                             column_config={
                                 "Target": st.column_config.NumberColumn("Target (₹)", format="%.0f"),
                                 "Collected": st.column_config.NumberColumn("Collected (₹)", format="%.0f"),
                                 "Progress": st.column_config.ProgressColumn("Progress", format="%.0f%%", min_value=0, max_value=1)
                             })
            else:
                st.info("No goals set for current quarter.")
        
        elif admin_action == f"Set/Edit Collection Target for {TARGET_YEAR}":
            st.markdown(f"<h5>Set or Update Collection Goal ({TARGET_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employees = [u for u, d in USERS.items() if d["role"] == "employee"]
            selected_emp = st.radio("Select Employee:", employees, key="payment_emp_radio_2025", horizontal=True)
            quarters = [f"{TARGET_YEAR}-Q{i}" for i in range(1, 5)]
            selected_period = st.radio("Quarter:", quarters, key="payment_period_radio_2025", horizontal=True)

            existing = payment_goals_df[
                (payment_goals_df["Username"] == selected_emp) &
                (payment_goals_df["MonthYear"] == selected_period)
            ]
            desc, tgt, ach, stat = "", 0.0, 0.0, "Not Started"
            if not existing.empty:
                g = existing.iloc[0]
                desc = g.get("GoalDescription", "")
                tgt = float(pd.to_numeric(g.get("TargetAmount", 0.0), errors="coerce") or 0.0)
                ach = float(pd.to_numeric(g.get("AchievedAmount", 0.0), errors="coerce") or 0.0)
                stat = g.get("Status", "Not Started")

            with st.form(f"form_payment_{selected_emp}_{selected_period}"):
                new_desc = st.text_input("Collection Goal Description", value=desc)
                new_tgt = st.number_input("Target Collection (INR)", value=tgt, min_value=0.0, step=1000.0)
                new_ach = st.number_input("Collected Amount (INR)", value=ach, min_value=0.0, step=500.0)
                new_status = st.selectbox("Status", status_options, index=status_options.index(stat))
                submitted = st.form_submit_button("Save Goal")

            if submitted:
                if not new_desc.strip():
                    st.warning("Goal description is required.")
                elif new_tgt <= 0 and new_status not in ["Cancelled", "Not Started"]:
                    st.warning("Target must be greater than 0.")
                else:
                    if not existing.empty:
                        payment_goals_df.loc[existing.index[0]] = [selected_emp, selected_period, new_desc, new_tgt, new_ach, new_status]
                        msg = "updated"
                    else:
                        new_row = {
                            "Username": selected_emp,
                            "MonthYear": selected_period,
                            "GoalDescription": new_desc,
                            "TargetAmount": new_tgt,
                            "AchievedAmount": new_ach,
                            "Status": new_status
                        }
                        payment_goals_df = pd.concat([payment_goals_df, pd.DataFrame([new_row])], ignore_index=True)
                        msg = "set"

                    try:
                        payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                        st.success(f"Payment goal {msg} for {selected_emp} ({selected_period})")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving data: {e}")

    else:
        # Employee side
        st.markdown("<h4>My Payment Collection Goals (2025)</h4>", unsafe_allow_html=True)
        user_goals = payment_goals_df[payment_goals_df["Username"] == current_user["username"]].copy()
        user_goals[["TargetAmount", "AchievedAmount"]] = user_goals[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0.0)

        current = user_goals[user_goals["MonthYear"] == current_quarter_display]
        st.markdown(f"<h5>Current Quarter: {current_quarter_display}</h5>", unsafe_allow_html=True)

        if not current.empty:
            g = current.iloc[0]
            tgt = g["TargetAmount"]
            ach = g["AchievedAmount"]
            prog = min(ach / tgt, 1.0) if tgt > 0 else 0.0

            st.markdown(f"**Goal:** {g.get('GoalDescription', '')}")
            st.metric("Target", f"₹{tgt:,.0f}")
            st.metric("Collected", f"₹{ach:,.0f}")
            st.progress(prog)
            st.caption(f"{prog * 100:.1f}% Complete")

            with st.form(key=f"update_collection_{current_user['username']}_{current_quarter_display}"):
                new_ach = st.number_input("Update Collected Amount (INR):", value=ach, min_value=0.0, step=500.0)
                submit = st.form_submit_button("Update Collection")
            if submit:
                idx = current.index[0]
                payment_goals_df.loc[idx, "AchievedAmount"] = new_ach
                payment_goals_df.loc[idx, "Status"] = "Achieved" if new_ach >= tgt and tgt > 0 else "In Progress"
                try:
                    payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                    st.success("Collection updated.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving update: {e}")
        else:
            st.info(f"No collection goal set for {current_quarter_display}.")

        # Past performance
        st.markdown("<h5>Past Quarters</h5>", unsafe_allow_html=True)
        past = user_goals[user_goals["MonthYear"] != current_quarter_display]
        if not past.empty:
            st.dataframe(past[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]],
                         use_container_width=True)
        else:
            st.info("No past collection goals found.")

    st.markdown('</div>', unsafe_allow_html=True)

status = "Achieved"  # Or "In Progress", or "Pending"
badge_color = "green" if status == "Achieved" else "orange" if status == "In Progress" else "red"
status_badge = f"<span class='badge {badge_color}'>{status}</span>"
st.markdown(f"Status: {status_badge}", unsafe_allow_html=True)



badge_color = "green" if status == "Achieved" else "orange" if status == "In Progress" else "red"
status_badge = f"<span class='badge {badge_color}'>{status}</span>"
st.markdown(f"Status: {status_badge}", unsafe_allow_html=True)
