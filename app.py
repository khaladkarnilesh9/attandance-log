import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import os
import pytz

# --- CSS (as defined above) ---
html_css = """
<style>
    /* --- General --- */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f0f2f5; /* Light gray background */
        color: #333;
    }
    /* --- Titles & Headers --- */
    h1, h2, h3, h4, h5, h6 {
        color: #1c4e80; /* Dark blue for headers */
    }
    .main .block-container > div:first-child > div:first-child > div:first-child > h1 { /* Main page title (very specific selector) */
        text-align: center;
        font-size: 2.5em;
        padding-bottom: 20px;
        border-bottom: 2px solid #70a1d7; /* Lighter blue accent */
        margin-bottom: 30px;
    }
    /* --- Card Styling --- */
    .card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px; /* Increased margin */
    }
    .card h3 {
        margin-top: 0;
        color: #1c4e80; /* Dark blue */
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 10px;
        margin-bottom: 20px;
        font-size: 1.5em; /* Larger card titles */
    }
    /* --- Login Container --- */
    .login-container {
        max-width: 450px; /* Slightly wider */
        margin: 50px auto; /* Centering */
    }
    .login-container .stButton button {
        width: 100%;
        background-color: #2070c0; /* Blue login button */
        font-size: 1.1em; /* Larger login button text */
    }
    .login-container .stButton button:hover {
        background-color: #1c4e80; /* Darker blue on hover */
    }
    /* --- Streamlit Button Styling --- */
    .stButton button {
        background-color: #28a745; /* Green for general actions */
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        font-size: 1em;
        font-weight: bold;
        transition: background-color 0.3s ease, transform 0.1s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        cursor: pointer; /* Add cursor pointer */
    }
    .stButton button:hover {
        background-color: #218838; /* Darker green */
        transform: translateY(-1px);
    }
    .stButton button:active {
        transform: translateY(0px);
    }
    /* --- Logout Button Style (can be more specific if needed) --- */
    /* We will target it by making its key or label unique in the st.button call */
    /* For now, a generic "secondary" kind if used, or a more specific selector */
    /* Example if you make the logout button key 'logout_button' */
    .stButton[data-testid="stButton"] button[id*="logout_button"] { /* Approximation */
         background-color: #dc3545 !important; /* Red for logout */
    }
    .stButton[data-testid="stButton"] button[id*="logout_button"]:hover {
         background-color: #c82333 !important; /* Darker red */
    }
    /* --- Input Fields (Limited Styling Possible) --- */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 5px !important;
        border: 1px solid #ced4da !important;
        padding: 10px !important;
        font-size: 1em; /* Consistent font size */
    }
    .stTextArea textarea {
        min-height: 100px;
    }
    /* --- Sidebar --- */
    [data-testid="stSidebar"] { /* More robust Streamlit sidebar selector */
        background-color: #1c4e80; /* Dark blue sidebar */
        padding: 20px !important;
    }
    [data-testid="stSidebar"] .sidebar-content {
         padding-top: 20px;
    }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] div, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important; /* White text in sidebar */
    }
    [data-testid="stSidebar"] .stRadio > label { /* Radio button labels in sidebar */
        font-size: 1.1em !important;
        color: #a9d6e5 !important; /* Lighter blue for inactive */
        padding-bottom: 8px; /* Spacing */
    }
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] > label { /* Active radio button label */
        color: #ffffff !important;
        font-weight: bold;
    }
    .welcome-text {
        font-size: 1.3em; /* Adjusted size */
        font-weight: bold;
        margin-bottom: 25px;
        text-align: center;
        color: #ffffff;
        border-bottom: 1px solid #70a1d7;
        padding-bottom: 15px;
    }
    /* --- Dataframe --- */
    .stDataFrame {
        width: 100%;
        border: 1px solid #dee2e6;
        border-radius: 5px;
    }
    /* --- Columns for buttons (more direct) --- */
    .button-column-container > div { /* Targets the columns directly if wrapped */
        display: flex;
        justify-content: center;
    }
    /* --- Page Sub Headers --- */
    .page-subheader {
        font-size: 1.8em;
        color: #1c4e80;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #e0e0e0;
    }
</style>
"""
st.markdown(html_css, unsafe_allow_html=True)

# --- Credentials ---
USERS = {
    "employee1": {"password": "emp123", "role": "employee"},
    "employee2": {"password": "emp456", "role": "employee"},
    "admin": {"password": "admin123", "role": "admin"}
}

# --- File Paths ---
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"

# --- Timezone Configuration ---
TARGET_TIMEZONE = "Asia/Kolkata" # Example: Indian Standard Time
try:
    tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'. Please use a valid Olson timezone name.")
    st.stop()

def get_current_time_in_tz():
    utc_now = datetime.now(timezone.utc)
    target_tz_now = utc_now.astimezone(tz)
    return target_tz_now

# --- Load or create data ---
def load_data(path, columns):
    if os.path.exists(path):
        try:
            if os.path.getsize(path) > 0:
                df = pd.read_csv(path)
                for col in columns:
                    if col not in df.columns:
                        df[col] = pd.NA
                return df
            else:
                return pd.DataFrame(columns=columns)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=columns)
        except Exception as e:
            st.error(f"Error loading data from {path}: {e}. Returning empty DataFrame.")
            return pd.DataFrame(columns=columns)
    else:
        return pd.DataFrame(columns=columns)

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]

attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)


# --- Initialize Session State ---
if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}

# --- Login Page ---
if not st.session_state.auth["logged_in"]:
    st.title("👨‍💼 HR Dashboard Login") # Moved title here for login page
    st.markdown('<div class="login-container card">', unsafe_allow_html=True)
    st.markdown("<h3>🔐 Login</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname")
    pwd = st.text_input("Password", type="password", key="login_pwd")
    if st.button("Login", key="login_button"):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- Main Application ---
st.title("👨‍💼 HR Dashboard") # Main title for logged-in users

current_user = st.session_state.auth

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user['username']}!</div>", unsafe_allow_html=True)
    nav_options = ["📆 Attendance", "🧾 Allowance", "📊 View Logs"]
    # Add specific key to logout button for styling if needed
    # For now, we rely on it being the last option or using more general CSS
    nav = st.radio("Navigation", nav_options, key="sidebar_nav")
    if st.button("🔒 Logout", key="logout_button_sidebar", use_container_width=True): # use_container_width for full width
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.success("Logged out successfully.")
        st.rerun()
        # Add custom class for styling logout button if required:
        # This requires knowing the exact HTML Streamlit generates or using JavaScript,
        # which is more complex. Styling based on key or `kind` is simpler.
        # For the CSS: .stButton button[id*="logout_button_sidebar"] { background-color: #dc3545 !important; }
        # (Note: Streamlit mangles keys for IDs, so `id*=` is a partial match)

# --- Main Content Area ---
if nav == "📆 Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='page-subheader'>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    
    # Using st.columns for button layout
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True) # Wrapper for columns
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Check In", key="check_in_btn", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = pd.DataFrame([{"Username": current_user["username"], "Type": "Check-In", "Timestamp": now_str}])
            attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
            attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            st.success(f"Checked in at {now_str} ({TARGET_TIMEZONE}).")
    with col2:
        if st.button("🚪 Check Out", key="check_out_btn", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = pd.DataFrame([{"Username": current_user["username"], "Type": "Check-Out", "Timestamp": now_str}])
            attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
            attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            st.success(f"Checked out at {now_str} ({TARGET_TIMEZONE}).")
    st.markdown('</div>', unsafe_allow_html=True) # End button-column-container
    st.markdown('</div>', unsafe_allow_html=True) # End card

elif nav == "🧾 Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='page-subheader'>💼 Travel & 🍽️ Dinner Allowance</h3>", unsafe_allow_html=True)
    a_type = st.selectbox("Select Allowance Type", ["Travel", "Dinner"], key="allowance_type")
    amount = st.number_input("Enter amount", min_value=0.0, step=10.0, format="%.2f", key="allowance_amount")
    reason = st.text_area("Reason for allowance", key="allowance_reason")
    if st.button("Submit Allowance", key="submit_allowance_btn"):
        if amount > 0 and reason.strip():
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry = pd.DataFrame([{
                "Username": current_user["username"], "Type": a_type,
                "Amount": amount, "Reason": reason, "Date": date_str
            }])
            allowance_df = pd.concat([allowance_df, new_entry], ignore_index=True)
            allowance_df.to_csv(ALLOWANCE_FILE, index=False)
            st.success(f"{a_type} allowance submitted for {date_str} ({TARGET_TIMEZONE}).")
        else:
            st.warning("Please provide a valid amount and reason.")
    st.markdown('</div>', unsafe_allow_html=True) # End card

elif nav == "📊 View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if current_user["role"] == "admin":
        st.markdown("<h3 class='page-subheader'>📋 All Employee Attendance</h3>", unsafe_allow_html=True)
        if not attendance_df.empty:
            st.dataframe(attendance_df, use_container_width=True)
        else:
            st.info("No attendance records yet.")
        
        st.markdown("<h3 class='page-subheader' style='margin-top: 30px;'>📋 All Allowance Requests</h3>", unsafe_allow_html=True)
        if not allowance_df.empty:
            st.dataframe(allowance_df, use_container_width=True)
        else:
            st.info("No allowance requests yet.")
    else: # Employee's own view
        st.markdown("<h3 class='page-subheader'>📅 My Attendance Logs</h3>", unsafe_allow_html=True)
        my_attendance = attendance_df[attendance_df["Username"] == current_user["username"]]
        if not my_attendance.empty:
            st.dataframe(my_attendance, use_container_width=True)
        else:
            st.info("You have no attendance records yet.")

        st.markdown("<h3 class='page-subheader' style='margin-top: 30px;'>🧾 My Allowance Requests</h3>", unsafe_allow_html=True)
        my_allowances = allowance_df[allowance_df["Username"] == current_user["username"]]
        if not my_allowances.empty:
            st.dataframe(my_allowances, use_container_width=True)
        else:
            st.info("You have no allowance requests yet.")
    st.markdown('</div>', unsafe_allow_html=True) # End card
