import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---- CONFIG ----
USER_CREDENTIALS = {
    "admin": "admin123",
    "john": "pass123",
    "maya": "mypwd"
}

FILE_PATH = "attendance_log.csv"

# ---- CSS Styling ----
st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: auto;
            padding: 2rem;
            background-color: #f0f2f6;
            border-radius: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .stButton button {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# ---- LOGIN FORM ----
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    with st.container():
        st.markdown("<div class='login-container'>", unsafe_allow_html=True)
        st.subheader("🔐 Login to Attendance Log")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
                st.success("✅ Login successful!")
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")
        st.markdown("</div>", unsafe_allow_html=True)
else:
    # ---- Attendance App ----
    st.title("📋 Attendance Log App")

    name = st.text_input("Enter your name:")

    # Load existing data
    if os.path.exists(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
    else:
        df = pd.DataFrame(columns=["Name", "Status", "Timestamp"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Check In"):
            if name:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df = df._append({"Name": name, "Status": "Check-In", "Timestamp": timestamp}, ignore_index=True)
                df.to_csv(FILE_PATH, index=False)
                st.success(f"{name} checked in at {timestamp}")
            else:
                st.error("Please enter your name.")

    with col2:
        if st.button("🚪 Check Out"):
            if name:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df = df._append({"Name": name, "Status": "Check-Out", "Timestamp": timestamp}, ignore_index=True)
                df.to_csv(FILE_PATH, index=False)
                st.success(f"{name} checked out at {timestamp}")
            else:
                st.error("Please enter your name.")

    st.markdown("---")
    st.subheader("📊 Attendance Log")
    st.dataframe(df)

    if st.button("🔒 Log Out"):
        st.session_state.authenticated = False
        st.rerun()
