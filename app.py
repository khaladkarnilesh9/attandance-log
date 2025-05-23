import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import os
import pytz

# --- CSS ---
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
    /* --- Logout Button Style specific to its key --- */
    .stButton button[id*="logout_button_sidebar"] { /* Targets button with key containing 'logout_button_sidebar' */
         background-color: #dc3545 !important; /* Red for logout */
    }
    .stButton button[id*="logout_button_sidebar"]:hover {
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

    /* --- Dataframe Styling (NEW/UPDATED) --- */
    .stDataFrame {
        width: 100%; /* Ensures the container takes full width if use_container_width is not set on st.dataframe */
        border: 1px solid #d1d9e1;      /* Light border, slightly more defined */
        border-radius: 8px;             /* Consistent rounded corners */
        overflow: hidden;               /* Crucial for border-radius on child table */
        box-shadow: 0 2px 4px rgba(0,0,0,0.06); /* Subtle shadow for depth */
        margin-bottom: 20px;            /* Space below the table */
    }

    /* Target the actual table element for specific table properties */
    .stDataFrame table {
        width: 100%;                    /* Ensure table takes full width of .stDataFrame */
        border-collapse: collapse;      /* Cleaner borders */
    }

    /* Table Header Cells (th) */
    .stDataFrame table thead th {
        background-color: #f0f2f5;      /* Light gray background, matches page bg or slightly distinct */
        color: #1c4e80;                 /* Dark blue text, consistent with other headers */
        font-weight: 600;               /* Bolder text for headers */
        text-align: left;               /* Standard alignment for table headers */
        padding: 12px 15px;             /* Comfortable padding */
        border-bottom: 2px solid #c5cdd5;/* Clear separator for header */
        font-size: 0.9em;               /* Slightly smaller header font */
    }

    /* Table Body Cells (td) */
    .stDataFrame table tbody td {
        padding: 10px 15px;             /* Padding for data cells */
        border-bottom: 1px solid #e7eaf0;/* Light line between rows */
        vertical-align: middle;         /* Align cell content vertically */
        color: #333;                    /* Standard text color */
        font-size: 0.875em;             /* Slightly smaller font for data */
    }

    /* Remove bottom border from the last row's cells */
    .stDataFrame table tbody tr:last-child td {
        border-bottom: none;
    }

    /* Hover effect for table rows in the body */
    .stDataFrame table tbody tr:hover {
        background-color: #e9ecef;      /* Light hover effect */
    }
    /* End of New Dataframe Styling */


    /* --- Columns for buttons (more direct) --- */
    .button-column-container > div[data-testid="stHorizontalBlock"] { /* Target Streamlit's column block */
        gap: 15px; /* Space between columns */
    }
     .button-column-container .stButton button {
        width: 100%; /* Make buttons in columns full width of column */
    }
    /* --- Page Sub Headers --- */
    .page-subheader {
        font-size: 1.8em;
        color: #1c4e80;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid #e0e0e0;
    }

/* Styling for Horizontal Radio Buttons */
div[role="radiogroup"] { /* Targets the container for radio buttons */
    display: flex;
    flex-wrap: wrap; /* Allow wrapping if too many options */
    gap: 15px;      /* Space between radio items */
    margin-bottom: 20px; /* Space below the radio group */
}

div[role="radiogroup"] > label { /* Targets individual radio button labels */
    background-color: #86a7c7; /* Light background for each option */
    padding: 8px 15px;
    border-radius: 20px; /* Pill shape */
    border: 1px solid #ced4da;
    cursor: pointer;
    transition: background-color 0.2s ease, border-color 0.2s ease;
    font-size: 0.95em;
}

div[role="radiogroup"] > label:hover {
    background-color: #dde2e6;
    border-color: #adb5bd;
}

div[role="radiogroup"] div[data-baseweb="radio"][aria-checked="true"] + label {
    background-color: #2070c0 !important; /* Primary blue for selected */
    color: white !important;
    border-color: #1c4e80 !important;
    font-weight: 500;
}

/* Small header for radio group */
.card h6 {
    font-size: 0.9em;
    color: #495057; /* Slightly muted color */
    margin-bottom: 8px;
    font-weight: 500;
}

.employee-section-header {
    color: #2070c0; /* Accent blue */
    margin-top: 30px;
    border-bottom: 1px solid #e0e0e0;
    padding-bottom: 5px;
    font-size: 1.3em; /* Adjust as needed */
}
.record-type-header {
    font-size: 1.1em;
    color: #333; /* Dark gray */
    margin-top: 15px;
    margin-bottom: 5px;
}
    
</style>
"""
st.markdown(html_css, unsafe_allow_html=True)

# --- Credentials ---
USERS = {
    "Geetali": {"password": "Geetali123", "role": "employee"},
    "Nilesh": {"password": "Nilesh123", "role": "employee"},
    "admin": {"password": "admin123", "role": "admin"}
}

# --- File Paths ---
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"

# --- Timezone Configuration ---
TARGET_TIMEZONE = "Asia/Kolkata"
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
    st.title("🙂HR Dashboard Login")
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
st.title("👨‍💼 HR Dashboard")

current_user = st.session_state.auth

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user['username']}!</div>", unsafe_allow_html=True)
    nav_options = ["📆 Attendance", "🧾 Allowance", "📊 View Logs"]
    nav = st.radio("Navigation", nav_options, key="sidebar_nav")
    if st.button("🔒 Logout", key="logout_button_sidebar", use_container_width=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.success("Logged out successfully.")
        st.rerun()

# --- Main Content Area ---
if nav == "📆 Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='page-subheader'>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Check In", key="check_in_btn", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            new_entry_att = pd.DataFrame([{"Username": current_user["username"], "Type": "Check-In", "Timestamp": now_str}])
            attendance_df = pd.concat([attendance_df, new_entry_att], ignore_index=True)
            try:
                attendance_df.to_csv(ATTENDANCE_FILE, index=False)
                st.success(f"Checked in at {now_str} ({TARGET_TIMEZONE}).")
            except Exception as e:
                st.error(f"Error saving attendance data: {e}")
    with col2:
        if st.button("🚪 Check Out", key="check_out_btn", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            new_entry_att = pd.DataFrame([{"Username": current_user["username"], "Type": "Check-Out", "Timestamp": now_str}])
            attendance_df = pd.concat([attendance_df, new_entry_att], ignore_index=True)
            try:
                attendance_df.to_csv(ATTENDANCE_FILE, index=False)
                st.success(f"Checked out at {now_str} ({TARGET_TIMEZONE}).")
            except Exception as e:
                st.error(f"Error saving attendance data: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


elif nav == "🧾 Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='page-subheader'>💼 Claim Allowance</h3>", unsafe_allow_html=True)

    st.markdown("<h6>Select Allowance Type:</h6>", unsafe_allow_html=True) 
    allowance_types = ["Travel", "Dinner", "Medical", "Internet", "Other"] 
    a_type = st.radio(
        "", 
        options=allowance_types,
        key="allowance_type_radio",
        horizontal=True,
        label_visibility='collapsed' 
    )
    
    amount = st.number_input("Enter Amount (INR):", min_value=0.0, step=10.0, format="%.2f", key="allowance_amount")
    reason = st.text_area("Reason for Allowance:", key="allowance_reason", placeholder="Please provide a clear justification...")

    if st.button("Submit Allowance Request", key="submit_allowance_btn", use_container_width=True): 
        if a_type and amount > 0 and reason.strip(): 
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry_data = {
                "Username": current_user["username"],
                "Type": a_type,
                "Amount": amount,
                "Reason": reason,
                "Date": date_str
            }
            new_entry_df = pd.DataFrame([new_entry_data])
            temp_allowance_df = pd.concat([allowance_df, new_entry_df], ignore_index=True)
            
            try:
                temp_allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                allowance_df = temp_allowance_df 
                st.success(f"Your {a_type} allowance request for {amount:.2f} INR on {date_str} ({TARGET_TIMEZONE}) has been submitted successfully.")
            except Exception as e:
                st.error(f"Error saving allowance data: {e}")
                st.warning("Your allowance request was not saved due to an error. Please try again.")
        else:
            if not a_type:
                 st.warning("Please select an allowance type.")
            elif not (amount > 0):
                 st.warning("Please enter a valid positive amount.")
            elif not reason.strip():
                 st.warning("Please provide a reason for the allowance.")
            else:
                 st.warning("Please complete all fields for the allowance request.")
                 
    st.markdown('</div>', unsafe_allow_html=True) 


elif nav == "📊 View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True) 

    if current_user["role"] == "admin":
        st.markdown("<h3 class='page-subheader'>📊 Employee Data Logs</h3>", unsafe_allow_html=True)
        
        employee_names = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
        
        if not employee_names:
            st.info("No employees found in the system or no employee data to display.")
        else:
            for emp_name in employee_names:
                # Use defined CSS classes for headers
                st.markdown(f"<h4 class='employee-section-header'>👤 Records for: {emp_name}</h4>", unsafe_allow_html=True)

                st.markdown("<h5 class='record-type-header'>🕒 Attendance Records:</h5>", unsafe_allow_html=True)
                emp_attendance = attendance_df[attendance_df["Username"] == emp_name]
                if not emp_attendance.empty:
                    st.dataframe(emp_attendance.drop(columns=['Username'], errors='ignore'), use_container_width=True)
                else:
                    st.caption(f"No attendance records found for {emp_name}.")

                # Add a specific style for the allowance header if needed, or adjust margin via class
                st.markdown("<h5 class='record-type-header' style='margin-top: 25px;'>💰 Allowance Requests:</h5>", unsafe_allow_html=True)
                emp_allowances = allowance_df[allowance_df["Username"] == emp_name]
                if not emp_allowances.empty:
                    st.dataframe(emp_allowances.drop(columns=['Username'], errors='ignore'), use_container_width=True)
                else:
                    st.caption(f"No allowance requests found for {emp_name}.")
                
                if emp_name != employee_names[-1]: # Add horizontal rule unless it's the last employee
                    st.markdown("---") 

    else: 
        st.markdown("<h3 class='page-subheader'>📅 My Attendance History</h3>", unsafe_allow_html=True)
        my_attendance = attendance_df[attendance_df["Username"] == current_user["username"]]
        if not my_attendance.empty:
            st.dataframe(my_attendance, use_container_width=True)
        else:
            st.info("You have no attendance records yet. Use the 'Attendance' page to check in/out.")

        st.markdown("<h3 class='page-subheader' style='margin-top: 30px;'>🧾 My Allowance Request History</h3>", unsafe_allow_html=True)
        my_allowances = allowance_df[allowance_df["Username"] == current_user["username"]]
        if not my_allowances.empty:
            st.dataframe(my_allowances, use_container_width=True)
        else:
            st.info("You have not submitted any allowance requests yet.")

    st.markdown('</div>', unsafe_allow_html=True)
