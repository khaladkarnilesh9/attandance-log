# ... (all your existing imports and functions up to the USERS dictionary) ...
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import pytz
import plotly.express as px
import plotly.graph_objects as go # For more custom Plotly charts if needed

# --- Matplotlib Configuration ---
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# --- Pillow for placeholder image generation ---
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# --- (Your existing chart functions: render_goal_chart, create_donut_chart, create_team_progress_bar_chart) ---
# These are great and will be reused or adapted.

# --- (Your existing html_css, USERS, image creation, file paths, timezone setup) ---
# --- (Your existing load_data function and DataFrame loading) ---
# --- (Your existing session state and login logic) ---

# ... (your existing code until the sidebar navigation) ...

# --- Main Application ---
current_user = st.session_state.auth

# --- Global Message Display for Main Application ---
message_placeholder_main = st.empty()
if "user_message" in st.session_state and st.session_state.user_message:
    message_type_main = st.session_state.get("message_type", "info")
    message_placeholder_main.markdown(
        f"<div class='custom-notification {message_type_main}'>{st.session_state.user_message}</div>",
        unsafe_allow_html=True
    )
    st.session_state.user_message = None
    st.session_state.message_type = None


with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user['username']}!</div>", unsafe_allow_html=True)

    # ***** NEW: Added Dashboard Option *****
    nav_options = [
        "📊 Dashboard", # New
        "📆 Attendance",
        "📸 Upload Activity Photo",
        "🧾 Allowance",
        "🎯 Goal Tracker",
        "💰 Payment Collection Tracker",
        "📊 View Logs"
    ]

    nav = st.radio("Navigation", nav_options, key="sidebar_nav_main")

    user_sidebar_info = USERS.get(current_user["username"], {})
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]):
        st.image(user_sidebar_info["profile_photo"], width=100)

    st.markdown(
        f"<p style='text-align:center; font-size:0.9em; color: #e0e0e0;'>{user_sidebar_info.get('position', 'N/A')}</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    if st.button("🔒 Logout", key="logout_button_sidebar", use_container_width=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."
        st.session_state.message_type = "info"
        st.rerun()

# --- (Your existing page content for Attendance, Upload, Allowance, etc.) ---

# ***** NEW: DASHBOARD SECTION *****
elif nav == "📊 Dashboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 Performance Dashboard</h3>", unsafe_allow_html=True)

    # --- Helper functions for dashboard metrics ---
    def get_check_ins_today(df):
        today_date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
        # Ensure 'Timestamp' is datetime before comparison
        df['Timestamp_dt'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        return df[df['Timestamp_dt'].dt.strftime("%Y-%m-%d") == today_date_str].shape[0]

    def get_active_users_today(df):
        today_date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
        df['Timestamp_dt'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        return df[df['Timestamp_dt'].dt.strftime("%Y-%m-%d") == today_date_str]['Username'].nunique()

    def get_overall_goal_progress(goals_df, current_quarter):
        quarter_goals = goals_df[goals_df["MonthYear"] == current_quarter].copy()
        if quarter_goals.empty:
            return 0, 0, 0
        quarter_goals["TargetAmount"] = pd.to_numeric(quarter_goals["TargetAmount"], errors='coerce').fillna(0)
        quarter_goals["AchievedAmount"] = pd.to_numeric(quarter_goals["AchievedAmount"], errors='coerce').fillna(0)
        total_target = quarter_goals["TargetAmount"].sum()
        total_achieved = quarter_goals["AchievedAmount"].sum()
        progress_percent = (total_achieved / total_target * 100) if total_target > 0 else 0
        return total_target, total_achieved, progress_percent

    def get_allowances_this_month(allowance_df):
        current_month_year = get_current_time_in_tz().strftime("%Y-%m")
        allowance_df['Date_dt'] = pd.to_datetime(allowance_df['Date'], errors='coerce')
        month_allowances = allowance_df[allowance_df['Date_dt'].dt.strftime("%Y-%m") == current_month_year].copy()
        month_allowances["Amount"] = pd.to_numeric(month_allowances["Amount"], errors='coerce').fillna(0)
        return month_allowances["Amount"].sum(), month_allowances.shape[0]

    TARGET_YEAR = 2025 # Assuming this is consistent
    current_quarter = get_quarter_str_for_year(TARGET_YEAR)

    if current_user["role"] == "admin":
        st.markdown("<h4>🚀 Admin Overview</h4>", unsafe_allow_html=True)
        st.markdown(f"<h6>Key Metrics for {current_quarter} & Today</h6>", unsafe_allow_html=True)

        # Calculate KPIs
        num_employees = len([u for u, data in USERS.items() if data["role"] == "employee"])
        check_ins_today_count = get_check_ins_today(attendance_df)
        active_users_today_count = get_active_users_today(attendance_df)

        sales_target, sales_achieved, sales_progress = get_overall_goal_progress(goals_df, current_quarter)
        payment_target, payment_achieved, payment_progress = get_overall_goal_progress(payment_goals_df, current_quarter)
        allowance_sum_month, allowance_count_month = get_allowances_this_month(allowance_df)

        # Display KPIs
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric(label="👥 Total Employees", value=num_employees)
            st.metric(label="✅ Check-ins Today", value=f"{check_ins_today_count}")
        with kpi2:
            st.metric(label="🎯 Sales Goal Progress (Team)", value=f"{sales_progress:.1f}%",
                      delta=f"₹{sales_achieved:,.0f} / ₹{sales_target:,.0f}",
                      delta_color="off") # 'off' uses default color, can be "normal", "inverse"
            st.metric(label="💰 Payment Goal Progress (Team)", value=f"{payment_progress:.1f}%",
                      delta=f"₹{payment_achieved:,.0f} / ₹{payment_target:,.0f}",
                      delta_color="off")
        with kpi3:
            st.metric(label="🚶 Active Users Today", value=f"{active_users_today_count}")
            st.metric(label="💸 Allowances This Month", value=f"₹{allowance_sum_month:,.0f}",
                      delta=f"{allowance_count_month} claims", delta_color="off")

        st.markdown("---")
        st.markdown(f"<h4>📊 Team Performance Details ({current_quarter})</h4>", unsafe_allow_html=True)

        # Team Sales Performance Chart
        summary_list_sales_dash = []
        employee_users_dash = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
        for emp_name in employee_users_dash:
            emp_current_goal = goals_df[(goals_df["Username"] == emp_name) & (goals_df["MonthYear"] == current_quarter)]
            target, achieved = 0.0, 0.0
            if not emp_current_goal.empty:
                g_data = emp_current_goal.iloc[0]
                target = float(pd.to_numeric(g_data.get("TargetAmount"), errors='coerce') or 0.0)
                achieved = float(pd.to_numeric(g_data.get("AchievedAmount", 0.0), errors='coerce') or 0.0)
            summary_list_sales_dash.append({"Employee": emp_name, "Target": target, "Achieved": achieved})
        summary_df_sales_dash = pd.DataFrame(summary_list_sales_dash)

        if not summary_df_sales_dash.empty:
            team_sales_bar_fig_dash = create_team_progress_bar_chart(summary_df_sales_dash, title="Team Sales Performance", target_col="Target", achieved_col="Achieved")
            if team_sales_bar_fig_dash:
                st.pyplot(team_sales_bar_fig_dash, use_container_width=True)
            else:
                st.info("No sales data to plot for the team bar chart.")
        else:
            st.info("No sales goals data to display team progress.")

        # Team Payment Collection Performance Chart (similar logic)
        summary_list_payment_dash = []
        for emp_name in employee_users_dash:
            emp_current_payment_goal = payment_goals_df[(payment_goals_df["Username"] == emp_name) & (payment_goals_df["MonthYear"] == current_quarter)]
            target_p, achieved_p = 0.0, 0.0
            if not emp_current_payment_goal.empty:
                pg_data = emp_current_payment_goal.iloc[0]
                target_p = float(pd.to_numeric(pg_data.get("TargetAmount"), errors='coerce') or 0.0)
                achieved_p = float(pd.to_numeric(pg_data.get("AchievedAmount", 0.0), errors='coerce') or 0.0)
            summary_list_payment_dash.append({"Employee": emp_name, "Target": target_p, "Achieved": achieved_p})
        summary_df_payment_dash = pd.DataFrame(summary_list_payment_dash)

        if not summary_df_payment_dash.empty:
            team_payment_bar_fig_dash = create_team_progress_bar_chart(summary_df_payment_dash, title="Team Payment Collection Performance", target_col="Target", achieved_col="Achieved")
            if team_payment_bar_fig_dash:
                # Custom color for achieved bars in payment chart on dashboard
                for bar_group in team_payment_bar_fig_dash.axes[0].containers:
                    if bar_group.get_label()=='Achieved':
                        for bar_item in bar_group: bar_item.set_color('#2070c0') # Achieved color for payment
                st.pyplot(team_payment_bar_fig_dash, use_container_width=True)
            else:
                st.info("No collection data to plot for the team bar chart.")
        else:
            st.info("No payment collection data to display team progress.")

        # (Optional: Add more charts like daily check-ins trend, recent activities, etc.)
        st.markdown("---")
        st.markdown("<h4>📋 Recent Activity Logs (Last 5)</h4>", unsafe_allow_html=True)
        if not activity_log_df.empty:
            # Ensure Timestamp is datetime and sort
            activity_log_df_sorted_dash = activity_log_df.copy()
            activity_log_df_sorted_dash['Timestamp_dt'] = pd.to_datetime(activity_log_df_sorted_dash['Timestamp'], errors='coerce')
            activity_log_df_sorted_dash = activity_log_df_sorted_dash.sort_values(by="Timestamp_dt", ascending=False)

            recent_activities = activity_log_df_sorted_dash.head(5)[["Username", "Timestamp", "Description"]]
            st.dataframe(recent_activities, use_container_width=True, hide_index=True)
        else:
            st.info("No activity logs recorded yet.")


    else: # Employee Dashboard View
        st.markdown("<h4>🎯 My Performance Snapshot</h4>", unsafe_allow_html=True)
        st.markdown(f"<h6>Key Metrics for {current_quarter}</h6>", unsafe_allow_html=True)

        # My Sales Goal
        my_sales_goals = goals_df[goals_df["Username"] == current_user["username"]].copy()
        my_sales_goals[["TargetAmount", "AchievedAmount"]] = my_sales_goals[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        current_sales_goal_df = my_sales_goals[my_sales_goals["MonthYear"] == current_quarter]

        sales_target_emp, sales_achieved_emp, sales_status_emp = 0.0, 0.0, "Not Set"
        if not current_sales_goal_df.empty:
            sg = current_sales_goal_df.iloc[0]
            sales_target_emp = sg["TargetAmount"]
            sales_achieved_emp = sg["AchievedAmount"]
            sales_status_emp = sg.get("Status", "In Progress")

        # My Payment Goal
        my_payment_goals = payment_goals_df[payment_goals_df["Username"] == current_user["username"]].copy()
        my_payment_goals[["TargetAmount", "AchievedAmount"]] = my_payment_goals[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        current_payment_goal_df = my_payment_goals[my_payment_goals["MonthYear"] == current_quarter]

        payment_target_emp, payment_achieved_emp, payment_status_emp = 0.0, 0.0, "Not Set"
        if not current_payment_goal_df.empty:
            pg = current_payment_goal_df.iloc[0]
            payment_target_emp = pg["TargetAmount"]
            payment_achieved_emp = pg["AchievedAmount"]
            payment_status_emp = pg.get("Status", "In Progress")

        # Last Check-in
        my_attendance = attendance_df[attendance_df["Username"] == current_user["username"]].copy()
        last_check_in_time_str = "N/A"
        if not my_attendance.empty:
            my_attendance['Timestamp_dt'] = pd.to_datetime(my_attendance['Timestamp'], errors='coerce')
            my_attendance = my_attendance.sort_values(by="Timestamp_dt", ascending=False)
            if not my_attendance.empty:
                 last_check_in_time_str = my_attendance.iloc[0]["Timestamp_dt"].strftime("%Y-%m-%d %H:%M") if pd.notna(my_attendance.iloc[0]["Timestamp_dt"]) else "N/A"


        emp_kpi1, emp_kpi2 = st.columns(2)
        with emp_kpi1:
            st.metric(label="My Sales Target", value=f"₹{sales_target_emp:,.0f}")
            st.metric(label="My Sales Achieved", value=f"₹{sales_achieved_emp:,.0f}")
            st.markdown(f"**Sales Status:** <span class='badge blue'>{sales_status_emp}</span>", unsafe_allow_html=True)

        with emp_kpi2:
            st.metric(label="My Collection Target", value=f"₹{payment_target_emp:,.0f}")
            st.metric(label="My Collection Achieved", value=f"₹{payment_achieved_emp:,.0f}")
            st.markdown(f"**Collection Status:** <span class='badge blue'>{payment_status_emp}</span>", unsafe_allow_html=True)

        st.metric(label="My Last Activity Time", value=last_check_in_time_str)


        st.markdown("---")
        st.markdown("<h5>My Goal Progress Visualized:</h5>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("<h6 style='text-align:center;'>Sales Progress</h6>", unsafe_allow_html=True)
            sales_progress_percent_emp = (sales_achieved_emp / sales_target_emp * 100) if sales_target_emp > 0 else 0
            sales_donut_fig_emp = create_donut_chart(sales_progress_percent_emp, achieved_color='#28a745')
            st.pyplot(sales_donut_fig_emp, use_container_width=True)

        with chart_col2:
            st.markdown("<h6 style='text-align:center;'>Collection Progress</h6>", unsafe_allow_html=True)
            payment_progress_percent_emp = (payment_achieved_emp / payment_target_emp * 100) if payment_target_emp > 0 else 0
            payment_donut_fig_emp = create_donut_chart(payment_progress_percent_emp, achieved_color='#2070c0')
            st.pyplot(payment_donut_fig_emp, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True) # Close main card

# --- (Your existing View Logs page content) ---
# ... (ensure the rest of your application code follows) ...
