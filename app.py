import streamlit as st
import pandas as pd
from datetime import datetime
import os

# CSV file to store attendance
FILE_PATH = "attendance_log.csv"

# Load existing data or create new DataFrame
if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
else:
    df = pd.DataFrame(columns=["Name", "Status", "Timestamp"])

st.title("📋 Attendance Log App")

# Input field for name
name = st.text_input("Enter your name:")

# Buttons for Check-in / Check-out
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

# Display log table
if os.path.exists(FILE_PATH):
    df = pd.read_csv(FILE_PATH)
    st.dataframe(df)
else:
    st.info("No attendance records yet.")
