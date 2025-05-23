import streamlit as st
import pandas as pd
from datetime import datetime
import os
import hashlib

# ---------------------------
# CONFIGURATION
# ---------------------------

# Hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Users with hashed passwords
USERS = {
    "employee1": {"password": hash_password("emp123"), "role": "employee"},
    "employee2": {"password": hash_password("emp456"), "role": "employee"},
    "admin": {"password": hash_password("admin123"), "role": "admin"},
}

# File paths
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"

# Load or initialize DataFrames
def load_data(path, columns):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame(columns=columns)

attendance_df = load_data(ATTENDANCE_FILE, ["Username", "Type", "Timestamp"])
allowance_df = load_data(ALLOWANCE_FILE, ["Username", "Type", "Amount", "Reason", "Date"])

# ---------------------------
# LOGIN
# ---------------------------

st.set_page_config(page_title="HR Dashboard", layout="centered")
st.title("👨‍💼 HR Dashboard")

if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}

if not st.session_state.auth["logged_in"]:
    st.subheader("🔐 Login")
    uname = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        user = USERS.get(uname)
        if user and user["password"] == hash_password(pwd):
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user["role"]}
            st.success("Login successful.")
            st.rerun()
        else:
            st.error("Invalid username or password.")
    st.stop()

# ---------------------------
# SIDEBAR
# ---------------------------

user = st.session_state.auth
st.sidebar.title(f"👋 Welcome, {user['username']}")
nav = st.sidebar.radio("Menu", ["📆 Attendance", "🧾 Allowance", "📊 View Logs", "🔒 Logout"])

# ---------------------------
# LOGOUT
# ---------------------------

if nav == "🔒 Logout":
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}
    st.rerun()

# ---------------------------
# ATTENDANCE
# ---------------------------

if nav == "📆 Attendance":
    st.header("🕒 Digital Attendance")
    col1, col2 = st.columns(2)

    if col1.button("✅ Check In"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        attendance_df = attendance_df._append({"Username": user["username"], "Type": "Check-In", "Timestamp": now}, ignore_index=True)
        attendance_df.to_csv(ATTENDANCE_FILE, index=False)
        st.success("Checked in successfully.")

    if col2.button("🚪 Check Out"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        attendance_df = attendance_df._append({"Username": user["username"], "Type": "Check-Out", "Timestamp": now}, ignore_index=True)
        attendance_df.to_csv(ATTENDANCE_FILE, index=False)
        st.success("Checked out successfully.")

# ---------------------------
# ALLOWANCE
# ---------------------------

elif nav == "🧾 Allowance":
    st.header("💼 Travel & 🍽️ Dinner Allowance")
    a_type = st.selectbox("Select Allowance Type", ["Travel", "Dinner"])
    amount = st.number_input("Amount", min_value=0.0, step=10.0)
    reason = st.text_area("Reason")

    if st.button("Submit Allowance"):
        date = datetime.now().strftime("%Y-%m-%d")
        allowance_df = allowance_df._append({
            "Username": user["username"],
            "Type": a_type,
            "Amount": amount,
            "Reason": reason,
            "Date": date
        }, ignore_index=True)
        allowance_df.to_csv(ALLOWANCE_FILE, index=False)
        st.success(f"{a_type} allowance submitted.")

# ---------------------------
# VIEW LOGS
# ---------------------------

elif nav == "📊 View Logs":
    st.header("📋 View Logs")
    if user["role"] == "admin":
        # Admin sees everything
        st.subheader("🕒 All Attendance Records")
        full_attendance = pd.read_csv(ATTENDANCE_FILE)
        st.dataframe(full_attendance)

        st.download_button("📤 Download Attendance (Excel)",
                           full_attendance.to_excel(index=False, engine='openpyxl'),
                           file_name="attendance_log.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.subheader("💼 All Allowance Records")
        full_allowance = pd.read_csv(ALLOWANCE_FILE)
        st.dataframe(full_allowance)

        st.download_button("📤 Download Allowances (Excel)",
                           full_allowance.to_excel(index=False, engine='openpyxl'),
                           file_name="allowance_log.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        # Employee sees their own data
        st.subheader("🕒 My Attendance")
        my_attendance = attendance_df[attendance_df["Username"] == user["username"]]
        st.dataframe(my_attendance)

        st.subheader("💼 My Allowances")
        my_allowances = allowance_df[allowance_df["Username"] == user["username"]]
        st.dataframe(my_allowances)
