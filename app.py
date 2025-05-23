import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- Credentials (In real app, store securely or hash) ---
USERS = {
    "employee1": {"password": "emp123", "role": "employee"},
    "employee2": {"password": "emp456", "role": "employee"},
    "admin": {"password": "admin123", "role": "admin"}
}

# --- File Paths ---
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"

# --- Load or create data ---
def load_data(path, columns):
    return pd.read_csv(path) if os.path.exists(path) else pd.DataFrame(columns=columns)

attendance_df = load_data(ATTENDANCE_FILE, ["Username", "Type", "Timestamp"])
allowance_df = load_data(ALLOWANCE_FILE, ["Username", "Type", "Amount", "Reason", "Date"])

# --- Login System ---
st.title("👨‍💼 HR Dashboard")

if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}

if not st.session_state.auth["logged_in"]:
    st.subheader("🔐 Login")
    uname = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        user = USERS.get(uname)
        if user and user["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user["role"]}
            st.success("Login successful.")
            st.rerun()
        else:
            st.error("Invalid credentials.")
    st.stop()

# --- Sidebar Navigation ---
user = st.session_state.auth
st.sidebar.title(f"👋 Welcome, {user['username']}")
nav = st.sidebar.radio("Navigation", ["📆 Attendance", "🧾 Allowance", "📊 View Logs", "🔒 Logout"])

# --- Logout ---
if nav == "🔒 Logout":
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}
    st.rerun()

# --- Attendance Section ---
if nav == "📆 Attendance":
    st.header("🕒 Digital Attendance")
    col1, col2 = st.columns(2)
    if col1.button("✅ Check In"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        attendance_df = attendance_df._append({"Username": user["username"], "Type": "Check-In", "Timestamp": now}, ignore_index=True)
        attendance_df.to_csv(ATTENDANCE_FILE, index=False)
        st.success("Checked in.")

    if col2.button("🚪 Check Out"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        attendance_df = attendance_df._append({"Username": user["username"], "Type": "Check-Out", "Timestamp": now}, ignore_index=True)
        attendance_df.to_csv(ATTENDANCE_FILE, index=False)
        st.success("Checked out.")

# --- Allowance Section ---
elif nav == "🧾 Allowance":
    st.header("💼 Travel & 🍽️ Dinner Allowance")
    a_type = st.selectbox("Select Allowance Type", ["Travel", "Dinner"])
    amount = st.number_input("Enter amount", min_value=0.0, step=10.0)
    reason = st.text_area("Reason")
    if st.button("Submit Allowance"):
        date = datetime.now().strftime("%Y-%m-%d")
        allowance_df = allowance_df._append({"Username": user["username"], "Type": a_type, "Amount": amount, "Reason": reason, "Date": date}, ignore_index=True)
        allowance_df.to_csv(ALLOWANCE_FILE, index=False)
        st.success(f"{a_type} allowance submitted.")

# --- Admin View ---
elif nav == "📊 View Logs":
    if user["role"] == "admin":
        st.header("📋 All Employee Attendance")
        st.dataframe(pd.read_csv(ATTENDANCE_FILE))
        st.header("📋 All Allowance Requests")
        st.dataframe(pd.read_csv(ALLOWANCE_FILE))
    else:
        st.header("📅 My Attendance Logs")
        my_attendance = attendance_df[attendance_df["Username"] == user["username"]]
        st.dataframe(my_attendance)

        st.header("🧾 My Allowance Requests")
        my_allowances = allowance_df[allowance_df["Username"] == user["username"]]
        st.dataframe(my_allowances)
