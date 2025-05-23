import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import os
import pytz
from streamlit_geolocation import streamlit_geolocation # IMPORTED

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
    font-weight: 600; /* Made it slightly bolder */
}

/* Add to your html_css string */
.allowance-summary-header {
    font-size: 1.0em; /* Slightly smaller or adjust as needed */
    color: #495057;   /* Muted color */
    margin-top: 15px;
    margin-bottom: 8px;
    font-weight: 550;
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
                # Ensure all expected columns exist, add them with pd.NA if not
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
        # Create new file with headers if it doesn't exist
        df = pd.DataFrame(columns=columns)
        try:
            df.to_csv(path, index=False)
        except Exception as e:
            st.warning(f"Could not create file {path}: {e}")
        return df


ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"] # ADDED Latitude, Longitude
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

    # --- Get Geolocation ---
    location_data = streamlit_geolocation(key="attendance_page_location") # Unique key
    lat, lon = None, None
    if location_data and 'latitude' in location_data and 'longitude' in location_data:
        lat = location_data['latitude']
        lon = location_data['longitude']
        accuracy = location_data.get('accuracy')
        accuracy_str = f"(Accuracy: {accuracy:.0f}m)" if accuracy else ""
        st.caption(f"📍 Current Location: Lat {lat:.4f}, Lon {lon:.4f} {accuracy_str}")
        st.markdown(f"[View on Google Maps](https://www.google.com/maps?q={lat},{lon})", unsafe_allow_html=True)
    else:
        st.warning("📍 Location access denied or unavailable. Please allow location access in your browser for accurate check-in/out.")
    st.markdown("---") # Separator

    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Check In", key="check_in_btn", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            new_entry_data = {
                "Username": current_user["username"],
                "Type": "Check-In",
                "Timestamp": now_str,
                "Latitude": lat if lat is not None else pd.NA,
                "Longitude": lon if lon is not None else pd.NA
            }
            # Ensure all columns from ATTENDANCE_COLUMNS are present
            for col_name in ATTENDANCE_COLUMNS:
                if col_name not in new_entry_data:
                    new_entry_data[col_name] = pd.NA

            new_entry_att = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
            attendance_df = pd.concat([attendance_df, new_entry_att], ignore_index=True)
            try:
                attendance_df.to_csv(ATTENDANCE_FILE, index=False)
                location_msg = f"at Lat: {lat:.4f}, Lon: {lon:.4f}" if lat and lon else "(location not recorded)"
                st.success(f"Checked in at {now_str} ({TARGET_TIMEZONE}) {location_msg}.")
            except Exception as e:
                st.error(f"Error saving attendance data: {e}")
    with col2:
        if st.button("🚪 Check Out", key="check_out_btn", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            new_entry_data = {
                "Username": current_user["username"],
                "Type": "Check-Out",
                "Timestamp": now_str,
                "Latitude": lat if lat is not None else pd.NA,
                "Longitude": lon if lon is not None else pd.NA
            }
            for col_name in ATTENDANCE_COLUMNS:
                if col_name not in new_entry_data:
                    new_entry_data[col_name] = pd.NA

            new_entry_att = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
            attendance_df = pd.concat([attendance_df, new_entry_att], ignore_index=True)
            try:
                attendance_df.to_csv(ATTENDANCE_FILE, index=False)
                location_msg = f"at Lat: {lat:.4f}, Lon: {lon:.4f}" if lat and lon else "(location not recorded)"
                st.success(f"Checked out at {now_str} ({TARGET_TIMEZONE}) {location_msg}.")
            except Exception as e:
                st.error(f"Error saving attendance data: {e}")
    st.markdown('</div>', unsafe_allow_html=True) # end button-column-container
    st.markdown('</div>', unsafe_allow_html=True) # end card


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
            # Ensure all columns from ALLOWANCE_COLUMNS are present
            for col_name in ALLOWANCE_COLUMNS:
                if col_name not in new_entry_data:
                    new_entry_data[col_name] = pd.NA

            new_entry_df = pd.DataFrame([new_entry_data], columns=ALLOWANCE_COLUMNS)
            # It's safer to concat with the globally loaded allowance_df then assign back
            allowance_df = pd.concat([allowance_df, new_entry_df], ignore_index=True)

            try:
                allowance_df.to_csv(ALLOWANCE_FILE, index=False)
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


# ... (previous code remains the same) ...

# ... (Keep all your existing code before the "📊 View Logs" section's `else` for employee view) ...

elif nav == "📊 View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)

    if current_user["role"] == "admin":
        # --- ADMIN VIEW ---
        st.markdown("<h3 class='page-subheader'>📊 Employee Data Logs</h3>", unsafe_allow_html=True)
        employee_names = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]

        if not employee_names:
            st.info("No employees found or no employee data to display.")
        else:
            for emp_name in employee_names:
                st.markdown(f"<h4 class='employee-section-header'>👤 Records for: {emp_name}</h4>", unsafe_allow_html=True)

                # Attendance (Admin)
                st.markdown("<h5 class='record-type-header'>🕒 Attendance Records:</h5>", unsafe_allow_html=True)
                emp_attendance = attendance_df[attendance_df["Username"] == emp_name].copy()
                if not emp_attendance.empty:
                    emp_attendance['Latitude'] = pd.to_numeric(emp_attendance['Latitude'], errors='coerce')
                    emp_attendance['Longitude'] = pd.to_numeric(emp_attendance['Longitude'], errors='coerce')
                    
                    display_cols_att = [col for col in ATTENDANCE_COLUMNS if col != 'Username']
                    admin_att_display = emp_attendance[display_cols_att].copy()
                    for col in ['Latitude', 'Longitude']:
                        if col in admin_att_display.columns:
                            admin_att_display[col] = admin_att_display[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) and isinstance(x, (float, int)) else "N/A")
                    st.dataframe(admin_att_display, use_container_width=True, hide_index=True)

                    # Map (Admin)
                    st.markdown("<h6 class='allowance-summary-header' style='margin-top: 10px;'>🗺️ Attendance Locations Map:</h6>", unsafe_allow_html=True)
                    map_data_admin = emp_attendance.dropna(subset=['Latitude', 'Longitude']).copy()
                    if not map_data_admin.empty:
                        map_data_admin_st_map = map_data_admin.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
                        st.map(map_data_admin_st_map[['latitude', 'longitude']])
                    else:
                        st.caption(f"No valid location data for map for {emp_name}.")
                else:
                    st.caption(f"No attendance records for {emp_name}.")

                # Allowances (Admin - simplified error handling and display)
                st.markdown("<h5 class='record-type-header' style='margin-top: 25px;'>💰 Allowance Section:</h5>", unsafe_allow_html=True)
                emp_allowances = allowance_df[allowance_df["Username"] == emp_name].copy()
                if not emp_allowances.empty:
                    emp_allowances['Amount'] = pd.to_numeric(emp_allowances['Amount'], errors='coerce')
                    grand_total_allowance = emp_allowances['Amount'].sum() # NaNs are skipped by sum
                    st.metric(label=f"Grand Total Allowance for {emp_name}", value=f"{grand_total_allowance:,.2f} INR")

                    st.markdown("<h6 class='allowance-summary-header'>📅 Monthly Allowance Summary:</h6>", unsafe_allow_html=True)
                    emp_allowances_summary = emp_allowances.dropna(subset=['Amount']).copy() # Process only valid amounts
                    if 'Date' in emp_allowances_summary.columns:
                        emp_allowances_summary['Date'] = pd.to_datetime(emp_allowances_summary['Date'], errors='coerce')
                        emp_allowances_summary.dropna(subset=['Date'], inplace=True) # Drop rows where date is invalid
                    
                    if not emp_allowances_summary.empty and 'Date' in emp_allowances_summary.columns:
                        emp_allowances_summary['YearMonth'] = emp_allowances_summary['Date'].dt.strftime('%Y-%m')
                        monthly_summary = emp_allowances_summary.groupby('YearMonth')['Amount'].sum().reset_index()
                        monthly_summary = monthly_summary.sort_values('YearMonth', ascending=False)
                        monthly_summary.rename(columns={'Amount': 'Total Amount (INR)', 'YearMonth': 'Month'}, inplace=True)
                        st.dataframe(monthly_summary, use_container_width=True, hide_index=True)
                    else:
                        st.caption("No valid allowance data to summarize by month.")
                    
                    st.markdown("<h6 class='allowance-summary-header' style='margin-top: 20px;'>📋 Detailed Allowance Requests:</h6>", unsafe_allow_html=True)
                    display_cols_allow_admin = [col for col in ALLOWANCE_COLUMNS if col != 'Username']
                    st.dataframe(emp_allowances[display_cols_allow_admin], use_container_width=True, hide_index=True)
                else:
                    st.caption(f"No allowance requests for {emp_name}.")
                
                if emp_name != employee_names[-1]: st.markdown("---")
    else:
        # --- EMPLOYEE'S OWN VIEW ---
        st.markdown("<h3 class='page-subheader'>📅 My Attendance History</h3>", unsafe_allow_html=True)
        my_attendance_raw = attendance_df[attendance_df["Username"] == current_user["username"]].copy()

        final_display_df = pd.DataFrame() # Initialize to ensure it's always defined
        my_attendance_proc = pd.DataFrame() # Initialize for map

        if not my_attendance_raw.empty:
            my_attendance_proc = my_attendance_raw.copy()
            my_attendance_proc['Timestamp'] = pd.to_datetime(my_attendance_proc['Timestamp'], errors='coerce')
            my_attendance_proc.dropna(subset=['Timestamp'], inplace=True) # CRITICAL: Remove invalid timestamps

            if not my_attendance_proc.empty:
                my_attendance_proc['Latitude'] = pd.to_numeric(my_attendance_proc['Latitude'], errors='coerce')
                my_attendance_proc['Longitude'] = pd.to_numeric(my_attendance_proc['Longitude'], errors='coerce')
                my_attendance_proc['DateOnly'] = my_attendance_proc['Timestamp'].dt.date

                check_ins_df = my_attendance_proc[my_attendance_proc['Type'] == 'Check-In'].copy()
                check_outs_df = my_attendance_proc[my_attendance_proc['Type'] == 'Check-Out'].copy()

                # Prepare empty DFs with correct columns for selection
                first_check_in_cols = ['DateOnly', 'Check-In FullTime', 'Check-In Latitude', 'Check-In Longitude']
                first_check_ins_sel = pd.DataFrame(columns=first_check_in_cols)
                if not check_ins_df.empty:
                    first_check_ins_grouped = check_ins_df.loc[check_ins_df.groupby('DateOnly')['Timestamp'].idxmin()]
                    first_check_ins_sel = first_check_ins_grouped[['DateOnly', 'Timestamp', 'Latitude', 'Longitude']].rename(
                        columns={'Timestamp': 'Check-In FullTime', 'Latitude': 'Check-In Latitude', 'Longitude': 'Check-In Longitude'}
                    )

                last_check_out_cols = ['DateOnly', 'Check-Out FullTime', 'Check-Out Latitude', 'Check-Out Longitude']
                last_check_outs_sel = pd.DataFrame(columns=last_check_out_cols)
                if not check_outs_df.empty:
                    last_check_outs_grouped = check_outs_df.loc[check_outs_df.groupby('DateOnly')['Timestamp'].idxmax()]
                    last_check_outs_sel = last_check_outs_grouped[['DateOnly', 'Timestamp', 'Latitude', 'Longitude']].rename(
                        columns={'Timestamp': 'Check-Out FullTime', 'Latitude': 'Check-Out Latitude', 'Longitude': 'Check-Out Longitude'}
                    )
                
                # Ensure DateOnly is consistently typed for merging (object of date objects or datetime)
                for df_sel in [first_check_ins_sel, last_check_outs_sel]:
                    if 'DateOnly' in df_sel.columns and not df_sel.empty:
                        df_sel['DateOnly'] = pd.to_datetime(df_sel['DateOnly']).dt.date


                # Combine check-ins and check-outs
                if not first_check_ins_sel.empty and not last_check_outs_sel.empty:
                    combined_df = pd.merge(first_check_ins_sel, last_check_outs_sel, on='DateOnly', how='outer')
                elif not first_check_ins_sel.empty:
                    combined_df = first_check_ins_sel.copy()
                    for col in last_check_out_cols[1:]: combined_df[col] = pd.NaT if 'Time' in col else pd.NA
                elif not last_check_outs_sel.empty:
                    combined_df = last_check_outs_sel.copy()
                    for col in first_check_in_cols[1:]: combined_df[col] = pd.NaT if 'Time' in col else pd.NA
                else: # Both first_check_ins_sel and last_check_outs_sel are empty
                    all_combined_cols = list(dict.fromkeys(first_check_in_cols + last_check_out_cols)) # Unique columns
                    combined_df = pd.DataFrame(columns=all_combined_cols)


                if not combined_df.empty:
                    combined_df = combined_df.sort_values(by='DateOnly', ascending=False, ignore_index=True)

                    # Ensure FullTime columns are datetime for duration calculation
                    if 'Check-In FullTime' in combined_df.columns:
                        combined_df['Check-In FullTime'] = pd.to_datetime(combined_df['Check-In FullTime'], errors='coerce')
                    if 'Check-Out FullTime' in combined_df.columns:
                        combined_df['Check-Out FullTime'] = pd.to_datetime(combined_df['Check-Out FullTime'], errors='coerce')

                    def format_duration_series(row):
                        if pd.notna(row.get('Check-In FullTime')) and pd.notna(row.get('Check-Out FullTime')):
                            if row['Check-Out FullTime'] > row['Check-In FullTime']:
                                duration = row['Check-Out FullTime'] - row['Check-In FullTime']
                                total_seconds = duration.total_seconds()
                                hours = int(total_seconds // 3600)
                                minutes = int((total_seconds % 3600) // 60)
                                return f"{hours}h {minutes}m"
                        return "N/A"
                    combined_df['Duration'] = combined_df.apply(format_duration_series, axis=1)

                    combined_df['Check-In Time'] = combined_df.get('Check-In FullTime', pd.Series(dtype='datetime64[ns]')).apply(lambda x: x.strftime('%H:%M:%S') if pd.notna(x) else 'N/A')
                    combined_df['Check-Out Time'] = combined_df.get('Check-Out FullTime', pd.Series(dtype='datetime64[ns]')).apply(lambda x: x.strftime('%H:%M:%S') if pd.notna(x) else 'N/A')
                    combined_df['Date'] = combined_df.get('DateOnly', pd.Series(dtype='object')).apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else 'N/A')
                    
                    # Define desired columns for the final display DataFrame
                    desired_cols_order = [
                        'Date', 'Check-In Time', 'Check-In Latitude', 'Check-In Longitude',
                        'Check-Out Time', 'Check-Out Latitude', 'Check-Out Longitude', 'Duration'
                    ]
                    # Select only existing columns from combined_df in the desired order
                    final_display_df_cols = [col for col in desired_cols_order if col in combined_df.columns]
                    final_display_df = combined_df[final_display_df_cols].copy()


                    final_display_df.rename(columns={
                        'Check-In Time': 'Check-In', 'Check-In Latitude': 'In Lat', 'Check-In Longitude': 'In Lon',
                        'Check-Out Time': 'Check-Out', 'Check-Out Latitude': 'Out Lat', 'Check-Out Longitude': 'Out Lon'
                    }, inplace=True)

                    for col_name_map in ['In Lat', 'In Lon', 'Out Lat', 'Out Lon']:
                        if col_name_map in final_display_df.columns: # Check if column exists after rename
                            final_display_df[col_name_map] = final_display_df[col_name_map].apply(
                                lambda x: f"{x:.4f}" if pd.notna(x) and isinstance(x, (float, int)) else ("N/A" if pd.isna(x) else str(x))
                            )
        # Display logic for employee attendance table
        if not final_display_df.empty:
            st.dataframe(final_display_df, use_container_width=True, hide_index=True)
        elif my_attendance_raw.empty: # Initial check: raw data was empty
            st.info("You have no attendance records yet. Use the 'Attendance' page to check in/out.")
        else: # Raw data existed, but processing (e.g., bad timestamps) led to no displayable data
            st.info("No processed attendance data to display (possibly due to invalid timestamp formats).")

        # Map for employee's own attendance
        st.markdown("<h6 class='allowance-summary-header' style='margin-top: 10px;'>🗺️ My Attendance Locations Map:</h6>", unsafe_allow_html=True)
        if not my_attendance_proc.empty: # Use the cleaned my_attendance_proc
            my_map_data = my_attendance_proc.dropna(subset=['Latitude', 'Longitude']).copy()
            if not my_map_data.empty:
                my_map_data_for_st_map = my_map_data.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
                st.map(my_map_data_for_st_map[['latitude', 'longitude']])
            else:
                st.info("No valid location data to display on the map for your attendance records.")
        elif my_attendance_raw.empty:
             st.info("No attendance records to show on map.")
        else:
             st.info("No valid attendance data with locations to show on map (possibly due to invalid timestamps).")


        # --- My Allowance Request History (remains mostly the same, ensure column existence) ---
        st.markdown("<h3 class='page-subheader' style='margin-top: 30px;'>🧾 My Allowance Request History</h3>", unsafe_allow_html=True)
        my_allowances = allowance_df[allowance_df["Username"] == current_user["username"]].copy()
        if not my_allowances.empty:
            display_cols_my_allow = [col for col in ALLOWANCE_COLUMNS if col != 'Username' and col in my_allowances.columns]
            st.dataframe(my_allowances[display_cols_my_allow], use_container_width=True, hide_index=True)
        else:
            st.info("You have not submitted any allowance requests yet.")

    st.markdown('</div>', unsafe_allow_html=True)  # End card

# ... (rest of your code, including the app footer if any) ...
