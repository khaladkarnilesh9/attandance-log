import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import os
import pytz

# --- CSS (Keep your existing html_css string here) ---
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
    /* --- Dataframe --- */
    .stDataFrame {
        width: 100%;
        border: 1px solid #dee2e6;
        border-radius: 5px;
    }
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

    /* ... (your existing CSS) ... */

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

/* Styling for the selected radio button's label */
/* This selector is tricky because Streamlit doesn't add a simple 'checked' class to the label itself */
/* We target the div that Streamlit marks as 'aria-checked="true"' and then style its SIBLING label */
/* This might need adjustment based on exact Streamlit version / HTML structure */
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

/* ... (rest of your CSS) ... */


    
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
                        df[col] = pd.NA # Use pandas' NA for missing values
                return df
            else: # File exists but is empty
                return pd.DataFrame(columns=columns)
        except pd.errors.EmptyDataError: # read_csv on an empty file (or only headers)
            return pd.DataFrame(columns=columns)
        except Exception as e:
            st.error(f"Error loading data from {path}: {e}. Returning empty DataFrame.")
            return pd.DataFrame(columns=columns)
    else: # File does not exist
        return pd.DataFrame(columns=columns)

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]

# Load dataframes at the start. These are global.
attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)


# --- Initialize Session State ---
if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}

# --- Login Page ---
if not st.session_state.auth["logged_in"]:
    st.title("👨‍💼 HR Dashboard Login")
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
    nav = st.radio("Menu", nav_options, key="sidebar_nav")
    if st.button("🔒 Logout", key="logout_button_sidebar", use_container_width=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.success("Logged out successfully.")
        st.rerun()

# --- Main Content Area ---

# ... (Keep all your existing code before the "📆 Attendance" section) ...
// Check if an interval with this ID already exists to avoid multiple intervals
// The script_id (e.g., 'ea49a98d-0690-427e-a694-4e01d33ebbad') is dynamically generated by Python's uuid.uuid4()
if (!window.clockInterval_ea49a98d-0690-427e-a694-4e01d33ebbad) {
    updateClock(); // Initial call to display clock immediately
    // If no interval with this specific ID is found on the window object, create a new one
    window.clockInterval_ea49a98d-0690-427e-a694-4e01d33ebbad = setInterval(updateClock, 1000); // Update every second
} else {
    // If an interval with this ID *already exists* (meaning this script block might have been re-executed by Streamlit
    // without a full page reload, but the previous JS environment partially persists),
    // we don't want to create a *new* duplicate interval.
    // Instead, we just call updateClock() once to ensure the displayed time is current,
    // especially if the re-execution caused a momentary display lag.
    // The existing interval will continue to run.
    updateClock();
}

# --- Main Content Area ---
if nav == "📆 Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='page-subheader'>🕒 Digital Attendance</h3>", unsafe_allow_html=True)

    # --- Live Digital Clock ---
    clock_placeholder = st.empty() # Create a placeholder for the clock

    # JavaScript to update the clock
    # We'll make the clock update every second.
    # The ID 'live-clock' will be targeted by the JS.
    # We use a unique ID for the script tag itself to help prevent re-execution issues if possible.
    # Though Streamlit's rerun behavior might still re-render it.
    import uuid
    script_id = str(uuid.uuid4()) # Generate a unique ID for the script tag

    js_code = f"""
    <div id="live-clock-container" style="text-align: center; margin-bottom: 20px;">
        <span id="live-clock" style="font-size: 2.2em; font-weight: bold; color: #1c4e80; letter-spacing: 2px; background-color: #e9ecef; padding: 10px 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"></span>
        <br>
        <span id="live-date" style="font-size: 1.1em; color: #495057;"></span>
    </div>
    <script id="{script_id}">
    function updateClock() {{
        const now = new Date();
        const clockElement = document.getElementById('live-clock');
        const dateElement = document.getElementById('live-date');

        if (clockElement && dateElement) {{
            // Time formatting
            let hours = now.getHours();
            const minutes = now.getMinutes().toString().padStart(2, '0');
            const seconds = now.getSeconds().toString().padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12; // the hour '0' should be '12'
            const hoursStr = hours.toString().padStart(2, '0');
            
            clockElement.textContent = `${{hoursStr}}:${{minutes}}:${{seconds}} ${{ampm}}`;

            // Date formatting
            const options = {{ weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }};
            dateElement.textContent = now.toLocaleDateString(undefined, options) + ' ({TARGET_TIMEZONE})';
        }}
    }}

    // Check if an interval with this ID already exists to avoid multiple intervals
    if (!window.clockInterval_{script_id}) {{
        updateClock(); // Initial call to display clock immediately
        window.clockInterval_{script_id} = setInterval(updateClock, 1000); // Update every second
    }} else {{
        // If interval exists, ensure clock is updated in case of Streamlit partial rerun
        updateClock();
    }}
    </script>
    """
    clock_placeholder.markdown(js_code, unsafe_allow_html=True)
    # --- End Live Digital Clock ---

    st.markdown('<div class="button-column-container">', unsafe_allow_html=True) # Wrapper for columns
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Check In", key="check_in_btn", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S") # Server-side TZ aware time for record
            new_entry_att = pd.DataFrame([{"Username": current_user["username"], "Type": "Check-In", "Timestamp": now_str}])
            attendance_df = pd.concat([attendance_df, new_entry_att], ignore_index=True)
            try:
                attendance_df.to_csv(ATTENDANCE_FILE, index=False)
                st.success(f"Checked in at {now_str} ({TARGET_TIMEZONE}).")
            except Exception as e:
                st.error(f"Error saving attendance data: {e}")
    with col2:
        if st.button("🚪 Check Out", key="check_out_btn", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S") # Server-side TZ aware time for record
            new_entry_att = pd.DataFrame([{"Username": current_user["username"], "Type": "Check-Out", "Timestamp": now_str}])
            attendance_df = pd.concat([attendance_df, new_entry_att], ignore_index=True)
            try:
                attendance_df.to_csv(ATTENDANCE_FILE, index=False)
                st.success(f"Checked out at {now_str} ({TARGET_TIMEZONE}).")
            except Exception as e:
                st.error(f"Error saving attendance data: {e}")
    st.markdown('</div>', unsafe_allow_html=True) # End button-column-container
    st.markdown('</div>', unsafe_allow_html=True) # End card

# ... (Keep all your existing code after the "📆 Attendance" section) ...
# ... (Keep all your existing code before the "🧾 Allowance" section) ...

elif nav == "🧾 Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='page-subheader'>💼 Claim Allowance</h3>", unsafe_allow_html=True) # Renamed for clarity

    # --- Allowance Type with Radio Buttons ---
    st.markdown("<h6>Select Allowance Type:</h6>", unsafe_allow_html=True) # Custom small header for the radio
    allowance_types = ["Travel", "Dinner", "Medical", "Internet", "Other"] # Add more types if needed
    # Use st.radio with horizontal=True
    a_type = st.radio(
        "", # Remove label here, use markdown above
        options=allowance_types,
        key="allowance_type_radio",
        horizontal=True,
        label_visibility='collapsed' # Hides the default label from st.radio
    )
    # st.write(f"Selected type: {a_type}") # For debugging

    amount = st.number_input("Enter Amount (INR):", min_value=0.0, step=10.0, format="%.2f", key="allowance_amount")
    reason = st.text_area("Reason for Allowance:", key="allowance_reason", placeholder="Please provide a clear justification...")

    if st.button("Submit Allowance Request", key="submit_allowance_btn", use_container_width=True): # Made button full width
        if a_type and amount > 0 and reason.strip(): # Ensure a_type is selected
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
                allowance_df = temp_allowance_df # Update global df only on success
                st.success(f"Your {a_type} allowance request for {amount:.2f} INR on {date_str} ({TARGET_TIMEZONE}) has been submitted successfully.")
                # Optionally clear inputs after successful submission
                # st.session_state.allowance_amount = 0.0
                # st.session_state.allowance_reason = ""
                # st.rerun() # To see the cleared inputs, but might be disruptive
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
                 
    st.markdown('</div>', unsafe_allow_html=True) # End card

# ... (Keep all your existing code after the "🧾 Allowance" section) ...




elif nav == "📊 View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    if current_user["role"] == "admin":
        st.markdown("<h3 class='page-subheader'>📋 All Employee Attendance</h3>", unsafe_allow_html=True)
        if not attendance_df.empty:
            st.dataframe(attendance_df, use_container_width=True)
        else:
            st.info("No attendance records yet.")

        st.markdown("<h3 class='page-subheader' style='margin-top: 30px;'>📋 All Allowance Requests</h3>", unsafe_allow_html=True)
        # st.write(f"Displaying allowance_df with {len(allowance_df)} rows in Admin View.") # Uncomment for debugging
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
        # st.write(f"Displaying my_allowances with {len(my_allowances)} rows in User View.") # Uncomment for debugging
        if not my_allowances.empty:
            st.dataframe(my_allowances, use_container_width=True)
        else:
            st.info("You have no allowance requests yet.")
    st.markdown('</div>', unsafe_allow_html=True)
