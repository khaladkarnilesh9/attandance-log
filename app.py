import streamlit as st
import pandas as pd
from datetime import datetime, timezone # Added timezone
import os
import pytz # Import pytz


# --- Credentials (In real app, store securely or hash) ---
USERS = {
    "Nilesh khaladkar": {"password": "emp123", "role": "employee"},
    "employee2": {"password": "emp456", "role": "employee"},
    "admin": {"password": "admin123", "role": "admin"}
}

# --- File Paths ---
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"

TARGET_TIMEZONE = "Asia/Kolkata" # Example: Indian Standard Time
# You MUST change "Asia/Kolkata" to the correct Olson timezone name for your needs.
# To see all available timezone names:
# import pytz
# print(pytz.all_timezones)
try:
    tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'. Please use a valid Olson timezone name.")
    st.stop()

# --- Helper function to get current time in target timezone ---
def get_current_time_in_tz():
    # Get current UTC time
    utc_now = datetime.now(timezone.utc)
    # Convert to target timezone
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

# --- Login System ---
st.title("👨‍💼 HR Dashboard")

if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}

if not st.session_state.auth["logged_in"]:
    st.subheader("🔐 Login")
    uname = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.success("Login successful.")
            st.rerun()
        else:
            st.error("Invalid credentials.")
    st.stop()

current_user = st.session_state.auth
st.sidebar.title(f"👋 Welcome, {current_user['username']}")
nav = st.sidebar.radio("Navigation", ["📆 Attendance", "🧾 Allowance", "📊 View Logs", "🔒 Logout"])

if nav == "🔒 Logout":
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}
    st.success("Logged out successfully.")
    st.rerun()

if nav == "📆 Attendance":
    st.header("🕒 Digital Attendance")
    col1, col2 = st.columns(2)
    if col1.button("✅ Check In"):
        # Use the helper function for timezone-aware time
        now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = pd.DataFrame([{"Username": current_user["username"], "Type": "Check-In", "Timestamp": now_str}])
        attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        attendance_df.to_csv(ATTENDANCE_FILE, index=False)
        st.success(f"Checked in at {now_str} ({TARGET_TIMEZONE}).") # Show timezone

    if col2.button("🚪 Check Out"):
        # Use the helper function for timezone-aware time
        now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry = pd.DataFrame([{"Username": current_user["username"], "Type": "Check-Out", "Timestamp": now_str}])
        attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        attendance_df.to_csv(ATTENDANCE_FILE, index=False)
        st.success(f"Checked out at {now_str} ({TARGET_TIMEZONE}).") # Show timezone

elif nav == "🧾 Allowance":
    st.header("💼 Travel & 🍽️ Dinner Allowance")
    a_type = st.selectbox("Select Allowance Type", ["Travel", "Dinner"])
    amount = st.number_input("Enter amount", min_value=0.0, step=10.0, format="%.2f")
    reason = st.text_area("Reason")
    if st.button("Submit Allowance"):
        if amount > 0 and reason.strip():
            # Use the helper function for timezone-aware date
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry = pd.DataFrame([{
                "Username": current_user["username"],
                "Type": a_type,
                "Amount": amount,
                "Reason": reason,
                "Date": date_str # Date is fine, but consistency can be good
            }])
            allowance_df = pd.concat([allowance_df, new_entry], ignore_index=True)
            allowance_df.to_csv(ALLOWANCE_FILE, index=False)
            st.success(f"{a_type} allowance submitted for {date_str} ({TARGET_TIMEZONE}).")
        else:
            st.warning("Please provide a valid amount and reason.")

elif nav == "📊 View Logs":
    if current_user["role"] == "admin":
        st.header("📋 All Employee Attendance")
        st.dataframe(attendance_df)
        st.header("📋 All Allowance Requests")
        st.dataframe(allowance_df)
    else:
        st.header("📅 My Attendance Logs")
        my_attendance = attendance_df[attendance_df["Username"] == current_user["username"]]
        st.dataframe(my_attendance)

        st.header("🧾 My Allowance Requests")
        my_allowances = allowance_df[allowance_df["Username"] == current_user["username"]]
        st.dataframe(my_allowances)
