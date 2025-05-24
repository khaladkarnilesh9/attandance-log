import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import pytz
import sys

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


# --- Sidebar ---
with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user['username']}!</div>", unsafe_allow_html=True)
    nav_options = ["📆 Attendance", "🧾 Allowance", "🎯 Goal Tracker", "📊 View Logs"]
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

elif nav == "🎯 Goal Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker</h3>", unsafe_allow_html=True)
    current_month_year = get_current_month_year_str() # Should be defined elsewhere or get_current_month_year_str()
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio(
            "Action:", 
            ["View Team Progress", "Set/Edit Employee Goal"], 
            key="admin_goal_action_radio_main", # Ensure this key is unique
            horizontal=True
        )

        if admin_action == "View Team Progress":
            st.markdown(f"<h5>Team Goal Progress for {current_month_year}</h5>", unsafe_allow_html=True)
            employee_users = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users: 
                st.info("No employees found.")
            else:
                summary_data = []
                for emp_name in employee_users:
                    user_info_gt = USERS.get(emp_name, {})
                    emp_current_goal = goals_df[(goals_df["Username"] == emp_name) & (goals_df["MonthYear"] == current_month_year)]
                    target, achieved, prog_val, goal_desc, status_val = 0.0, 0.0, 0.0, "Not Set", "N/A"
                    if not emp_current_goal.empty:
                        g_data = emp_current_goal.iloc[0]
                        target = pd.to_numeric(g_data.get("TargetAmount"), errors='coerce').fillna(0.0)
                        achieved = pd.to_numeric(g_data.get("AchievedAmount"), errors='coerce').fillna(0.0)
                        if target > 0: prog_val = min(achieved / target, 1.0)
                        goal_desc, status_val = g_data.get("GoalDescription", "N/A"), g_data.get("Status", "N/A")
                    summary_data.append({
                        "Photo": user_info_gt.get("profile_photo",""), "Employee": emp_name, "Position": user_info_gt.get("position","N/A"),
                        "Goal": goal_desc, "Target": target, "Achieved": achieved, "Progress": prog_val, "Status": status_val 
                    })
                if summary_data:
                    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True, column_config={
                        "Photo": st.column_config.ImageColumn("Pic", width="small"),
                        "Target": st.column_config.NumberColumn("Target (₹)", format="%.0f"),
                        "Achieved": st.column_config.NumberColumn("Achieved (₹)", format="%.0f"),
                        "Progress": st.column_config.ProgressColumn("Progress", format="%.0f%%", min_value=0, max_value=1)
                    })
        # CORRECTED INDENTATION FOR THIS ELIF BLOCK
        elif admin_action == "Set/Edit Employee Goal":
            st.markdown("<h5>Set or Update Employee Goal</h5>", unsafe_allow_html=True)

            employee_options = [u for u, d in USERS.items() if d["role"] == "employee"]
            
            # Initialize session state for employee selectbox if not present or if current value is invalid
            if not employee_options:
                st.warning("No employees available to set goals for.")
                current_selected_employee = None # No employee to select
            else:
                if "goal_tracker_sel_emp" not in st.session_state or \
                   st.session_state.goal_tracker_sel_emp not in employee_options:
                    st.session_state.goal_tracker_sel_emp = employee_options[0]
            
                def update_selected_employee():
                    st.session_state.goal_tracker_sel_emp = st.session_state.goal_sel_emp_key_admin # Use the widget's key to get value
                
                sel_emp_widget_val = st.selectbox(
                    "Select Employee:", 
                    employee_options, 
                    index=employee_options.index(st.session_state.goal_tracker_sel_emp), # Index from session state
                    key="goal_sel_emp_key_admin", # Unique key for this widget
                    on_change=update_selected_employee
                )
                current_selected_employee = st.session_state.goal_tracker_sel_emp # Work with the value from session state
                # st.write(f"DEBUG: Admin - Selected Employee (from state): {current_selected_employee}")


            # Month Selectbox Logic
            year_now = get_current_time_in_tz().year
            current_month_year_str = get_current_month_year_str()
            
            months_list = []
            try:
                base_months = [datetime(y,m,1).strftime("%Y-%m") for y in range(year_now-1, year_now+2) for m in range(1,13)]
                months_list = sorted(list(set(base_months + [current_month_year_str])), reverse=True)
            except Exception as e_months:
                st.error(f"Error generating months_list: {e_months}")
                months_list = [current_month_year_str] if isinstance(current_month_year_str, str) else ["2024-01"] 
            
            if not months_list:
                st.error("Month list is empty! Cannot proceed with month selection.")
                current_selected_month = None # No month to select
            else:
                initial_target_month = current_month_year_str
                if "goal_tracker_target_month" not in st.session_state or \
                   st.session_state.goal_tracker_target_month not in months_list:
                    st.session_state.goal_tracker_target_month = initial_target_month if initial_target_month in months_list else months_list[0]

                try:
                    def_m_idx = months_list.index(st.session_state.goal_tracker_target_month)
                except ValueError:
                    def_m_idx = 0 
                    st.session_state.goal_tracker_target_month = months_list[0]
            
                def update_selected_month():
                    st.session_state.goal_tracker_target_month = st.session_state.goal_month_key_admin # Use widget's key
                
                # st.write(f"DEBUG: Admin - Month list: {months_list}")
                # st.write(f"DEBUG: Admin - Default month index: {def_m_idx}")

                target_m_y_widget_val = st.selectbox(
                    "Goal Month (YYYY-MM):", 
                    options=months_list,
                    index=def_m_idx, 
                    key="goal_month_key_admin", # Unique key for this widget
                    on_change=update_selected_month
                )
                current_selected_month = st.session_state.goal_tracker_target_month # Work with value from session state
                # st.write(f"DEBUG: Admin - Selected Month (from state): {current_selected_month}")

            # Proceed with form logic only if an employee and month are selected
            if current_selected_employee and current_selected_month:
                # st.write(f"DEBUG: Admin - Using Employee: {current_selected_employee}, Month: {current_selected_month} for form.")
                existing_g = goals_df[(goals_df["Username"] == current_selected_employee) & (goals_df["MonthYear"] == current_selected_month)]
                
                g_desc, g_target, g_achieved, g_status = "", 0.0, 0.0, "Not Started"
                if not existing_g.empty:
                    g_d = existing_g.iloc[0]
                    g_desc = g_d.get("GoalDescription","")
                    g_target = pd.to_numeric(g_d.get("TargetAmount"),errors='coerce').fillna(0.0)
                    g_achieved = pd.to_numeric(g_d.get("AchievedAmount"),errors='coerce').fillna(0.0)
                    g_status = g_d.get("Status","Not Started")
                    st.info(f"Editing existing goal for {current_selected_employee} for {current_selected_month}.")

                form_key = f"set_goal_form_{current_selected_employee}_{current_selected_month}_main_v4" # New form key
                with st.form(key=form_key):
                    # st.write(f"DEBUG: Form Key: {form_key}")
                    new_g_desc = st.text_area("Goal Description:", value=g_desc, key=f"desc_{current_selected_employee}_{current_selected_month}")
                    new_g_target = st.number_input("Target Sales (INR):", value=g_target, min_value=0.0, step=1000.0, format="%.2f", key=f"target_{current_selected_employee}_{current_selected_month}")
                    new_g_achieved = st.number_input("Achieved Sales (INR):", value=g_achieved, min_value=0.0, step=100.0, format="%.2f", key=f"achieved_{current_selected_employee}_{current_selected_month}")
                    
                    status_default_index = 0
                    if g_status in status_options:
                        status_default_index = status_options.index(g_status)
                    new_g_status = st.selectbox("Status:", status_options, index=status_default_index, key=f"status_{current_selected_employee}_{current_selected_month}")
                    submitted = st.form_submit_button("Save Goal")

                if submitted:
                    if not new_g_desc.strip(): st.warning("Description needed.")
                    elif new_g_target <= 0 and new_g_status not in ["Cancelled", "On Hold", "Not Started"]: st.warning("Target > 0 unless Cancelled/On Hold/Not Started.")
                    else:
                        if not existing_g.empty:
                            goals_df.loc[existing_g.index[0]] = [current_selected_employee, current_selected_month, new_g_desc, new_g_target, new_g_achieved, new_g_status]
                            msg_verb="updated"
                        else:
                            new_g_entry = pd.DataFrame([{
                                "Username": current_selected_employee, "MonthYear": current_selected_month, 
                                "GoalDescription": new_g_desc, "TargetAmount": new_g_target, 
                                "AchievedAmount": new_g_achieved, "Status": new_g_status
                            }], columns=GOALS_COLUMNS)
                            goals_df = pd.concat([goals_df, new_g_entry], ignore_index=True)
                            msg_verb="set"
                        try:
                            goals_df.to_csv(GOALS_FILE, index=False)
                            st.session_state.user_message = f"Goal for {current_selected_employee} ({current_selected_month}) {msg_verb}!"
                            st.session_state.message_type = "success"
                            st.rerun()
                        except Exception as e:
                            st.session_state.user_message = f"Error saving goal: {e}"
                            st.session_state.message_type = "error"
                            st.rerun()
            else:
                if not current_selected_employee and employee_options: # Only show if employees exist but none selected (shouldn't happen with current logic)
                    st.warning("Please select an employee to proceed.")
                # If month list was empty, error already shown.
                # If current_selected_month is None due to empty month list, this implies an issue handled above.

    else: # Employee View (current_user["role"] == "employee")
        st.markdown("<h4>My Sales Goals</h4>", unsafe_allow_html=True)
        my_all_goals = goals_df[goals_df["Username"] == current_user["username"]].copy()
        if not my_all_goals.empty:
            for col_n in ["TargetAmount", "AchievedAmount"]: my_all_goals[col_n] = pd.to_numeric(my_all_goals[col_n], errors='coerce').fillna(0.0)

        current_g = my_all_goals[my_all_goals["MonthYear"] == current_month_year]
        st.markdown(f"<h5>Current Goal: {current_month_year}</h5>", unsafe_allow_html=True)
        if not current_g.empty:
            g_e = current_g.iloc[0]
            target_amt, achieved_amt = g_e.get("TargetAmount",0.0), g_e.get("AchievedAmount",0.0)
            prog_val = min(achieved_amt / target_amt, 1.0) if target_amt > 0 else 0.0
            st.markdown(f"**Description:** {g_e.get('GoalDescription', 'N/A')}")
            c1,c2,c3 = st.columns(3)
            c1.metric("Target Sales", f"₹{target_amt:,.0f}")
            c2.metric("Achieved Sales", f"₹{achieved_amt:,.0f}")
            with c3: 
                st.metric("Status", g_e.get('Status','In Progress'))
                st.progress(prog_val)
                st.caption(f"{prog_val*100:.1f}% Completed")
            st.markdown("---")
            st.markdown("<h6>Update My Achievement (Current Month)</h6>", unsafe_allow_html=True)
            with st.form(key=f"update_ach_form_{current_user['username']}_main"):
                new_ach_val = st.number_input("My Total Achieved Sales (INR):", value=achieved_amt, min_value=0.0, step=100.0, format="%.2f", key=f"emp_ach_update_{current_month_year}")
                submit_upd = st.form_submit_button("Update My Achieved Amount")
            if submit_upd:
                idx_to_update = current_g.index[0]
                goals_df.loc[idx_to_update, "AchievedAmount"] = new_ach_val
                goals_df.loc[idx_to_update, "Status"] = "Achieved" if new_ach_val >= target_amt and target_amt > 0 else "In Progress"
                try:
                    goals_df.to_csv(GOALS_FILE, index=False)
                    st.session_state.user_message = "Achievement updated!"
                    st.session_state.message_type = "success"
                    st.rerun()
                except Exception as e:
                    st.session_state.user_message = f"Error updating achievement: {e}"
                    st.session_state.message_type = "error"
                    st.rerun()
        else: 
            st.info(f"No goal set for you for {current_month_year}. Contact admin.")
        st.markdown("---")
        st.markdown("<h5>My Past Goals History</h5>", unsafe_allow_html=True)
        past_g = my_all_goals[my_all_goals["MonthYear"] != current_month_year].sort_values(by="MonthYear", ascending=False)
        if not past_g.empty:
            st.dataframe(
                past_g[["MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]], 
                hide_index=True, 
                use_container_width=True,
                column_config={
                    "TargetAmount":st.column_config.NumberColumn(format="₹%.0f"), 
                    "AchievedAmount":st.column_config.NumberColumn(format="₹%.0f")
                }
            )
        else: 
            st.info("No past goal records found.")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "📊 View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if current_user["role"] == "admin":
        st.markdown("<h3 class='page-subheader'>📊 Employee Data Logs</h3>", unsafe_allow_html=True)
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

                st.markdown("<h5 class='record-type-header'>🕒 Attendance Records:</h5>", unsafe_allow_html=True)
                emp_attendance = attendance_df[attendance_df["Username"] == emp_name].copy()
                if not emp_attendance.empty:
                    emp_attendance['Latitude'] = pd.to_numeric(emp_attendance['Latitude'], errors='coerce')
                    emp_attendance['Longitude'] = pd.to_numeric(emp_attendance['Longitude'], errors='coerce')
                    display_cols_att = [col for col in ATTENDANCE_COLUMNS if col != 'Username']
                    admin_att_display = emp_attendance[display_cols_att].copy()
                    for col_name_map in ['Latitude', 'Longitude']: # Renamed col to col_name_map to avoid conflict
                        if col_name_map in admin_att_display.columns:
                            admin_att_display[col_name_map] = admin_att_display[col_name_map].apply(lambda x: f"{x:.4f}" if pd.notna(x) and isinstance(x, (float, int)) else "N/A")
                    st.dataframe(admin_att_display, use_container_width=True, hide_index=True)
                    st.markdown("<h6 class='allowance-summary-header'>🗺️ Attendance Locations Map:</h6>", unsafe_allow_html=True)
                    map_data_admin = emp_attendance.dropna(subset=['Latitude', 'Longitude']).copy()
                    if not map_data_admin.empty:
                        map_df_renamed = map_data_admin.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
                        st.map(map_df_renamed[['latitude', 'longitude']])
                    else: st.caption(f"No valid location data for map for {emp_name}.")
                else: st.caption(f"No attendance records for {emp_name}.")

                st.markdown("<h5 class='record-type-header'>💰 Allowance Section:</h5>", unsafe_allow_html=True)
                emp_allowances = allowance_df[allowance_df["Username"] == emp_name].copy()
                if not emp_allowances.empty:
                    emp_allowances['Amount'] = pd.to_numeric(emp_allowances['Amount'], errors='coerce').fillna(0.0)
                    st.metric(label=f"Grand Total Allowance for {emp_name}", value=f"₹{emp_allowances['Amount'].sum():,.2f}")
                    st.markdown("<h6 class='allowance-summary-header'>📅 Monthly Allowance Summary:</h6>", unsafe_allow_html=True)
                    emp_allow_sum = emp_allowances.dropna(subset=['Amount']).copy()
                    if 'Date' in emp_allow_sum.columns:
                        emp_allow_sum['Date'] = pd.to_datetime(emp_allow_sum['Date'], errors='coerce')
                        emp_allow_sum.dropna(subset=['Date'], inplace=True)
                    if not emp_allow_sum.empty and 'Date' in emp_allow_sum.columns:
                        emp_allow_sum['YearMonth'] = emp_allow_sum['Date'].dt.strftime('%Y-%m')
                        monthly_summary = emp_allow_sum.groupby('YearMonth')['Amount'].sum().reset_index().sort_values('YearMonth', ascending=False)
                        st.dataframe(monthly_summary.rename(columns={'Amount': 'Total Amount (₹)', 'YearMonth': 'Month'}), use_container_width=True, hide_index=True)
                    else: st.caption("No valid allowance data for monthly summary.")
                    st.markdown("<h6 class='allowance-summary-header'>📋 Detailed Allowance Requests:</h6>", unsafe_allow_html=True)
                    st.dataframe(emp_allowances[[c for c in ALLOWANCE_COLUMNS if c != 'Username']], use_container_width=True, hide_index=True)
                else: st.caption(f"No allowance requests for {emp_name}.")
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
        my_att_raw = attendance_df[attendance_df["Username"] == current_user["username"]].copy()
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
                
                if not first_check_ins_sel.empty and not last_check_outs_sel.empty:
                    combined_df = pd.merge(first_check_ins_sel, last_check_outs_sel, on='DateOnly', how='outer')
                elif not first_check_ins_sel.empty:
                    combined_df = first_check_ins_sel.copy()
                    for col_name_c in last_check_out_cols[1:]: # Renamed col to col_name_c
                        if 'Time' in col_name_c: combined_df[col_name_c] = pd.NaT
                        else: combined_df[col_name_c] = pd.NA
                elif not last_check_outs_sel.empty:
                    combined_df = last_check_outs_sel.copy()
                    for col_name_c in first_check_in_cols[1:]: # Renamed col to col_name_c
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

        st.markdown("<h6 class='allowance-summary-header'>🗺️ My Attendance Locations Map:</h6>", unsafe_allow_html=True)
        if not my_att_proc.empty:
            my_map_data = my_att_proc.dropna(subset=['Latitude', 'Longitude']).copy()
            if not my_map_data.empty:
                map_df_renamed_my = my_map_data.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
                st.map(map_df_renamed_my[['latitude', 'longitude']])
            else: st.info("No valid location data for map.")
        elif my_att_raw.empty: st.info("No attendance records for map.")
        else: st.info("No valid attendance data with locations for map.")

        st.markdown("<h4 class='record-type-header'>🧾 My Allowance Request History</h4>", unsafe_allow_html=True)
        my_allowances = allowance_df[allowance_df["Username"] == current_user["username"]].copy()
        if not my_allowances.empty: st.dataframe(my_allowances[[c for c in ALLOWANCE_COLUMNS if c != 'Username' and c in my_allowances.columns]], use_container_width=True, hide_index=True)
        else: st.info("You have not submitted any allowance requests yet.")
    st.markdown('</div>', unsafe_allow_html=True)
