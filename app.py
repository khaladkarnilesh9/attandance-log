# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date # Added date for date_input
import os
import pytz
import plotly.express as px

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
    # No st.warning here, will handle in image creation if needed

# --- Charting Functions (render_goal_chart, create_donut_chart, create_team_progress_bar_chart) ---
def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty:
        st.warning(f"No data available to plot for {chart_title}.")
        return
    df_chart = df.copy()
    df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear",
                              value_vars=["TargetAmount", "AchievedAmount"],
                              var_name="Metric",
                              value_name="Amount")
    if df_melted.empty or df_melted['Amount'].sum() == 0:
        st.info(f"No data to plot for {chart_title} after processing.")
        return
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group",
                 labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"},
                 title=chart_title,
                 color_discrete_map={'TargetAmount': '#4285F4', 'AchievedAmount': '#34A853'})
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric')
    fig.update_xaxes(type='category')
    st.plotly_chart(fig, use_container_width=True)

def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#34A853', remaining_color='#e0e0e0', center_text_color=None):
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=90)
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    try: progress_percentage = float(progress_percentage)
    except (ValueError, TypeError): progress_percentage = 0.0
    progress_percentage = max(0.0, min(progress_percentage, 100.0))
    remaining_percentage = 100.0 - progress_percentage
    if progress_percentage <= 0.01: sizes = [100.0]; slice_colors = [remaining_color]; actual_progress_display = 0.0
    elif progress_percentage >= 99.99: sizes = [100.0]; slice_colors = [achieved_color]; actual_progress_display = 100.0
    else: sizes = [progress_percentage, remaining_percentage]; slice_colors = [achieved_color, remaining_color]; actual_progress_display = progress_percentage
    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.4, edgecolor='white'))
    centre_circle = plt.Circle((0,0),0.60,fc='white'); fig.gca().add_artist(centre_circle)
    text_color_to_use = center_text_color if center_text_color else (achieved_color if actual_progress_display > 0 else '#5f6368')
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=12, fontweight='bold', color=text_color_to_use)
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig

def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee"):
    if summary_df.empty: return None
    labels = summary_df[user_col].tolist(); target_amounts = summary_df[target_col].fillna(0).tolist(); achieved_amounts = summary_df[achieved_col].fillna(0).tolist()
    x = np.arange(len(labels)); width = 0.35
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.8), 5), dpi=100)
    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color='#4285F4', alpha=0.9)
    rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color='#34A853', alpha=0.9)
    ax.set_ylabel('Amount (INR)', fontsize=10); ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9); ax.legend(fontsize=9)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.yaxis.grid(True, linestyle='--', alpha=0.6)
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0: ax.annotate(f'{height:,.0f}', xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=7, color='#202124')
    autolabel(rects1); autolabel(rects2)
    fig.tight_layout(pad=1.5)
    return fig

# --- CSS Styling ---
html_css = """
<style>
    /* Import Google Fonts (Roboto for text) */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    /* Import Google Material Symbols Outlined (for icons) */
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

    :root {
        --primary-color: #4285F4;  /* Google blue */
        --secondary-color: #34A853;  /* Google green */
        --accent-color: #EA4335;  /* Google red */
        --yellow-color: #FBBC05;  /* Google yellow */
        --success-color: #34A853;
        --danger-color: #EA4335;
        --warning-color: #FBBC05;
        --info-color: #4285F4;
        --body-bg-color: #f8f9fa; /* Light grey, common in Google UIs */
        --card-bg-color: #ffffff;
        --text-color: #202124; /* Google's primary text color */
        --text-muted-color: #5f6368; /* Google's secondary text color */
        --border-color: #dadce0; /* Google's common border color */
        --input-border-color: #dadce0;
        --font-family: 'Roboto', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        --border-radius: 8px; /* Slightly more rounded like Google's newer designs */
        --border-radius-lg: 12px;
        --box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15); /* Google-like shadow */
        --box-shadow-sm: 0 1px 2px 0 rgba(60,64,67,0.1);
    }

    body {
        font-family: var(--font-family);
        background-color: var(--body-bg-color);
        color: var(--text-color);
        line-height: 1.5;
        font-weight: 400;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-color);
        font-weight: 500; /* Slightly bolder headings */
        letter-spacing: -0.25px; /* Common in Google typography for larger text */
    }

    /* Main page title (Streamlit's default h1) */
    .main .block-container > div:first-child > div:first-child > div:first-child > h1 {
        text-align: left; /* Default is left, but good to be explicit */
        font-size: 1.75rem; /* Approx 28px */
        font-weight: 500;
        padding-bottom: 16px;
        margin-bottom: 24px;
        border-bottom: 1px solid var(--border-color);
    }

    .card {
        background-color: var(--card-bg-color);
        padding: 24px;
        border-radius: var(--border-radius);
        box-shadow: var(--box-shadow-sm);
        margin-bottom: 24px;
        border: 1px solid var(--border-color);
    }

    .card h3 { /* Section titles within cards */
        margin-top: 0;
        color: var(--text-color);
        padding-bottom: 12px;
        margin-bottom: 20px;
        font-size: 1.25rem; /* Approx 20px */
        font-weight: 500;
        display: flex;
        align-items: center;
    }

    .card h3:before { /* Decorative accent bar for card h3 */
        content: "";
        display: inline-block;
        width: 4px;
        height: 20px; /* Adjusted to match typical line height of h3 */
        background-color: var(--primary-color);
        margin-right: 12px;
        border-radius: 2px;
    }

    .card h4 {
        color: var(--text-color);
        margin-top: 24px;
        margin-bottom: 16px;
        font-size: 1.1rem; /* Approx 17-18px */
        font-weight: 500;
    }

    .card h5 {
        font-size: 1rem; /* 16px */
        color: var(--text-color);
        margin-top: 20px;
        margin-bottom: 12px;
        font-weight: 500;
    }

    .card h6 { /* Sub-labels or small titles */
        font-size: 0.875rem; /* 14px */
        color: var(--text-muted-color);
        margin-top: 0; /* Remove default top margin if it's the first element */
        margin-bottom: 12px;
        font-weight: 400; /* Lighter for sub-labels */
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .form-field-label h6 { /* Specific styling for form field labels if wrapped in h6 */
        font-size: 0.875rem;
        color: var(--text-muted-color);
        margin-top: 16px;
        margin-bottom: 8px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .login-container {
        max-width: 480px;
        margin: 60px auto;
        border-top: 4px solid var(--primary-color); /* Accent top border */
    }

    .login-container .stButton button {
        width: 100%;
        background-color: var(--primary-color) !important;
        color: white !important;
        font-size: 1rem; /* 16px */
        padding: 12px 20px;
        border-radius: var(--border-radius);
        border: none !important;
        font-weight: 500 !important;
        box-shadow: none !important; /* Flat button style */
        transition: background-color 0.2s ease;
    }

    .login-container .stButton button:hover {
        background-color: #3367d6 !important; /* Darker Google blue */
        color: white !important;
        box-shadow: none !important;
    }

    /* General Streamlit buttons (not in login) */
    .stButton:not(.login-container .stButton) button {
        background-color: var(--primary-color);
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: var(--border-radius);
        font-size: 0.875rem; /* 14px */
        font-weight: 500;
        transition: background-color 0.2s ease;
        box-shadow: none; /* Flatter buttons */
        cursor: pointer;
    }

    .stButton:not(.login-container .stButton) button:hover {
        background-color: #3367d6; /* Darker Google blue */
        box-shadow: none;
    }

    .stButton button[type="submit"] { /* Primary action buttons */
         background-color: var(--primary-color);
    }
    .stButton button[type="submit"]:hover {
         background-color: #3367d6;
    }


    .stButton button[id*="logout_button_sidebar"] { /* Specific for sidebar logout */
        background-color: var(--danger-color) !important;
        border: none !important;
        color: white !important;
        font-weight: 500 !important;
    }

    .stButton button[id*="logout_button_sidebar"]:hover {
        background-color: #d33426 !important; /* Darker Google red */
    }

    /* Input Fields: Text, Number, TextArea, Date, Time, Selectbox */
    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stDateInput input,
    .stTimeInput input,
    .stSelectbox div[data-baseweb="select"] > div { /* Targets the inner div of stSelectbox */
        border-radius: var(--border-radius) !important;
        border: 1px solid var(--input-border-color) !important;
        padding: 10px 12px !important;
        font-size: 0.875rem !important; /* 14px */
        color: var(--text-color) !important;
        background-color: var(--card-bg-color) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .stTextInput input::placeholder,
    .stNumberInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: var(--text-muted-color) !important;
        opacity: 1; /* Ensure placeholder is fully visible */
    }

    .stTextArea textarea {
        min-height: 100px; /* Slightly reduced */
    }

    /* Focus styles for inputs */
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus,
    .stDateInput input:focus,
    .stTimeInput input:focus,
    .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 2px rgba(66,133,244,0.15) !important; /* Subtle focus ring, Google style */
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff; /* Sidebar background, often white in Google UIs */
        padding: 16px !important; /* Consistent padding */
        box-shadow: 1px 0 2px 0 rgba(60,64,67,0.1), 1px 0 3px 1px rgba(60,64,67,0.1); /* Subtle right shadow */
        border-right: 1px solid var(--border-color);
    }

    [data-testid="stSidebar"] .sidebar-content {
        padding-top: 8px; /* Small top padding inside content area */
    }

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] div:not([data-testid="stRadio"]) { /* General text in sidebar */
        color: var(--text-color) !important;
    }

    /* Sidebar Radio Button (Navigation) Specifics */
    [data-testid="stSidebar"] .stRadio > label > div > p { /* Radio button labels in sidebar */
        font-size: 0.875rem !important; /* 14px */
        color: var(--text-color) !important;
        padding: 0;
        margin: 0;
        display: flex; /* To align icon and text if icon is part of this <p> */
        align-items: center;
    }

    [data-testid="stSidebar"] .stRadio > label { /* Radio button container */
        padding: 8px 12px;
        border-radius: var(--border-radius);
        margin-bottom: 4px;
        transition: background-color 0.2s ease;
        display: flex; /* For icon alignment if icon is direct child */
        align-items: center;
    }

    [data-testid="stSidebar"] .stRadio > label:hover {
        background-color: rgba(66,133,244,0.08); /* Light blue on hover */
    }


    .welcome-text { /* User welcome text in sidebar */
        font-size: 1rem; /* 16px */
        font-weight: 500;
        margin-bottom: 20px;
        text-align: center;
        color: var(--text-color) !important;
        padding-bottom: 16px;
        border-bottom: 1px solid var(--border-color);
    }

    [data-testid="stSidebar"] [data-testid="stImage"] > img { /* Profile image in sidebar */
        border-radius: 50%; /* Circular image */
        border: 2px solid var(--border-color);
        margin: 0 auto 12px auto;
        display: block;
    }

    /* DataFrame Styling */
    .stDataFrame {
        width: 100%;
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        overflow: hidden; /* Ensures border-radius clips content */
        box-shadow: var(--box-shadow-sm);
        margin-bottom: 20px;
    }

    .stDataFrame table {
        width: 100%;
        border-collapse: collapse; /* Clean table lines */
    }

    .stDataFrame table thead th {
        background-color: #f8f9fa; /* Light grey header, common in Google tables */
        color: var(--text-muted-color);
        font-weight: 500;
        text-align: left;
        padding: 12px 16px;
        border-bottom: 1px solid var(--border-color);
        font-size: 0.75rem; /* Smaller header text (12px) */
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .stDataFrame table tbody td {
        padding: 12px 16px;
        border-bottom: 1px solid var(--border-color); /* Lighter lines between rows */
        vertical-align: middle;
        color: var(--text-color);
        font-size: 0.875rem; /* 14px */
    }

    .stDataFrame table tbody tr:last-child td {
        border-bottom: none; /* Remove bottom border from last row */
    }

    .stDataFrame table tbody tr:hover {
        background-color: #f1f3f4; /* Slightly darker hover for rows */
    }

    /* Employee Progress Items (used in Goal Trackers, Dashboard) */
    .employee-progress-item {
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius);
        padding: 16px;
        text-align: center;
        background-color: var(--card-bg-color);
        margin-bottom: 12px;
        box-shadow: var(--box-shadow-sm);
    }

    .employee-progress-item h6 {
        margin-top: 0;
        margin-bottom: 8px;
        font-size: 0.875rem; /* 14px */
        color: var(--text-color);
        font-weight: 500;
    }

    .employee-progress-item p {
        font-size: 0.75rem; /* 12px */
        color: var(--text-muted-color);
        margin-bottom: 8px;
    }

    /* Button Layout in Columns */
    .button-column-container > div[data-testid="stHorizontalBlock"] { /* Targets columns holding buttons */
        gap: 16px; /* Space between buttons in columns */
    }

    .button-column-container .stButton button {
        width: 100%; /* Make buttons fill column width */
    }

    /* Radio buttons used for horizontal choices (e.g., Allowance Type, Admin Actions) */
    div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap; /* Allow radios to wrap on smaller screens */
        gap: 8px; /* Space between radio buttons */
        margin-bottom: 20px;
    }

    div[role="radiogroup"] > label { /* Individual radio button label container */
        background-color: white;
        color: var(--text-color);
        padding: 8px 16px;
        border-radius: var(--border-radius);
        border: 1px solid var(--border-color);
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.875rem; /* 14px */
        font-weight: 400; /* Regular weight for unselected */
    }

    div[role="radiogroup"] > label:hover {
        background-color: #f8f9fa; /* Light hover effect */
        border-color: var(--border-color); /* Keep border consistent on hover */
    }

    .employee-section-header { /* Header for sections like "Records for [Employee Name]" */
        color: var(--text-color);
        margin-top: 24px;
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 8px;
        font-size: 1.1rem; /* ~17-18px */
    }

    .record-type-header { /* Headers for "Field Activity Logs", "General Attendance", etc. */
        font-size: 1rem; /* 16px */
        color: var(--text-color);
        margin-top: 20px;
        margin-bottom: 12px;
        font-weight: 500;
    }

    /* General Image Styling (if not sidebar profile) */
    div[data-testid="stImage"] > img {
        border-radius: var(--border-radius);
        border: 1px solid var(--border-color);
        box-shadow: var(--box-shadow-sm);
    }

    /* Progress Bar */
    .stProgress > div > div { /* The actual progress bar fill */
        background-color: var(--primary-color) !important;
        border-radius: var(--border-radius); /* Match container radius for smooth look */
    }

    .stProgress { /* The progress bar container */
        border-radius: var(--border-radius);
        background-color: #e9ecef; /* Lighter background for the track (Google's choice often) */
    }

    /* Metric Widget Styling */
    div[data-testid="stMetricLabel"] {
        font-size: 0.875rem !important; /* 14px */
        color: var(--text-muted-color) !important;
        font-weight: 400;
    }

    div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important; /* Approx 24px, slightly smaller than default for compactness */
        font-weight: 500;
        color: var(--text-color);
    }

    /* Custom Notification Boxes (Success, Error, Warning, Info) */
    .custom-notification {
        padding: 12px 16px;
        border-radius: var(--border-radius);
        margin-bottom: 16px;
        font-size: 0.875rem; /* 14px */
        border-left-width: 4px; /* Accent border on the left */
        border-left-style: solid;
        display: flex;
        align-items: center;
        background-color: white; /* Base background */
        box-shadow: var(--box-shadow-sm);
    }

    .custom-notification.success {
        background-color: #e6f4ea; /* Lighter green, common for success messages */
        color: var(--text-color); /* Keep text readable */
        border-left-color: var(--success-color);
    }

    .custom-notification.error {
        background-color: #fce8e6; /* Lighter red */
        color: var(--text-color);
        border-left-color: var(--danger-color);
    }

    .custom-notification.warning {
        background-color: #fef7e0; /* Lighter yellow */
        color: var(--text-color);
        border-left-color: var(--warning-color);
    }

    .custom-notification.info {
        background-color: #e8f0fe; /* Lighter blue */
        color: var(--text-color);
        border-left-color: var(--info-color);
    }

    /* Badges for Status etc. */
    .badge {
        display: inline-block;
        padding: 4px 8px; /* Smaller padding for a neater look */
        font-size: 0.75rem; /* 12px, smaller font */
        font-weight: 500;
        line-height: 1;
        color: white;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 12px; /* Pill shape, common in Google UIs */
    }

    .badge.green { background-color: var(--success-color); }
    .badge.red { background-color: var(--danger-color); }
    .badge.orange { background-color: var(--warning-color); }
    .badge.blue { background-color: var(--primary-color); }
    .badge.grey { background-color: var(--text-muted-color); }

    /* Google Analytics-like cards (can be used with st.markdown for custom KPIs) */
    .metric-card {
        background-color: white;
        border-radius: var(--border-radius);
        padding: 16px;
        box-shadow: var(--box-shadow-sm);
        border: 1px solid var(--border-color);
        margin-bottom: 16px; /* Space below card */
    }

    .metric-card-title {
        font-size: 0.75rem; /* 12px */
        color: var(--text-muted-color);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    .metric-card-value {
        font-size: 1.5rem; /* 24px */
        font-weight: 500;
        color: var(--text-color);
        margin-bottom: 4px; /* Space between value and change indicator */
    }

    .metric-card-change { /* For delta values if you construct them manually */
        font-size: 0.75rem; /* 12px */
        display: flex;
        align-items: center;
    }

    .metric-card-change.positive { color: var(--success-color); }
    .metric-card-change.negative { color: var(--danger-color); }

    /* Google-style tabs (for st.tabs) */
    .stTabs [role="tablist"] { /* The container for tab buttons */
        gap: 0px; /* Remove gap to make tabs touch if desired, or keep small gap e.g., 2px */
        margin-bottom: 0px; /* Remove bottom margin to connect with tab content */
        border-bottom: 1px solid var(--border-color); /* Underline for the whole tab bar */
    }

    .stTabs [role="tab"] { /* Individual tab button */
        padding: 10px 16px; /* Adjust padding for comfort */
        border-radius: 0; /* Make tabs rectangular, or var(--border-radius) var(--border-radius) 0 0; for top rounded */
        border: none; /* Remove individual borders */
        border-bottom: 2px solid transparent; /* Placeholder for active indicator */
        background-color: transparent; /* No background for inactive tabs */
        color: var(--text-muted-color);
        font-size: 0.875rem; /* 14px */
        font-weight: 500; /* Medium weight for tabs */
        transition: all 0.2s ease;
        margin-right: 16px; /* Space between tabs */
        position: relative;
        top: 1px; /* Align with the bottom border of the tablist */
    }
    .stTabs [role="tab"]:last-child {
        margin-right: 0;
    }

    .stTabs [role="tab"]:hover {
        background-color: transparent; /* No background change on hover for this style */
        color: var(--text-color); /* Text color changes on hover */
    }

    .stTabs [aria-selected="true"] { /* Active tab */
        background-color: transparent !important;
        color: var(--primary-color) !important;
        border-bottom: 2px solid var(--primary-color) !important; /* Active indicator line */
        font-weight: 500;
        box-shadow: none !important;
    }

    /* Google-style date picker icon */
    .stDateInput input {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='%235f6368'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7v-5z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: right 12px center;
        padding-right: 40px !important; /* Ensure text doesn't overlap icon */
    }
    
    /* Styling for Material Symbols (used for navigation icons etc.) */
    .material-symbols-outlined {
      font-variation-settings:
      'FILL' 0,  /* 0 for outlined, 1 for filled */
      'wght' 400, /* Font weight - 300 (Light) to 500 (Medium) is good for UI */
      'GRAD' 0,  /* Optical grade */
      'opsz' 20; /* Optical size (20 or 24 is common for UI) */
      font-size: 20px; /* Explicit icon size, can match opsz */
      vertical-align: text-bottom; /* Better alignment with text */
      margin-right: 10px; /* Space between icon and text */
      color: inherit; /* Inherit color from parent by default */
    }

    /* Sidebar specific icon styling */
    [data-testid="stSidebar"] .material-symbols-outlined {
        color: var(--text-muted-color); /* Default icon color in sidebar */
        font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 20;
        font-size: 20px;
    }
    
    /* === AGGRESSIVE OVERRIDE FOR SELECTED RADIO BUTTON COLOR === */
    /* For the main content area radio buttons */
    div[role="radiogroup"] div[data-baseweb="radio"] input[type="radio"]:checked + label,
    div[role="radiogroup"] div[data-baseweb="radio"][aria-checked="true"] + label {
        background-color: rgba(66, 133, 244, 0.15) !important; 
        color: var(--primary-color) !important;            
        border-color: var(--primary-color) !important;       
        font-weight: 500 !important; 
    }
    div[role="radiogroup"] input[type="radio"]:checked + div[data-testid="stRadioMark"],
    div[role="radiogroup"] input[type="radio"]:checked + label div[data-testid="stRadioMark"] { 
        background-color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
        box-shadow: inset 0 0 0 4px var(--card-bg-color) !important; 
    }
    div[role="radiogroup"] input[type="radio"]:checked + label::before {
        background-color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
    }

    /* For the sidebar radio buttons */
    [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label,
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label {
        background-color: rgba(66, 133, 244, 0.15) !important; 
    }
    [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label > div > p,
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label > div > p {
        color: var(--primary-color) !important;
        font-weight: 500 !important;
    }
    [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label .material-symbols-outlined,
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label .material-symbols-outlined {
        color: var(--primary-color) !important;
        font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 20 !important;
    }
    [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + div[data-testid="stRadioMark"],
    [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label div[data-testid="stRadioMark"] {
        background-color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
        box-shadow: inset 0 0 0 4px #ffffff !important; 
    }
    [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label::before {
        background-color: var(--primary-color) !important;
        border-color: var(--primary-color) !important;
    }
</style>
"""
# --- End of Chunk 1 ---
# --- Chunk 2: Global Vars, Constants, Helpers ---

st.set_page_config(layout="wide", page_title="Symplanta TrackSphere")
st.markdown(html_css, unsafe_allow_html=True)

# --- Credentials & User Info ---
USERS = {
    "Geetali": {"password": "Geetali123", "role": "employee", "position": "Software Engineer", "profile_photo": "images/geetali.png"},
    "Nilesh": {"password": "Nilesh123", "role": "sales_person", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "Vishal": {"password": "Vishal123", "role": "sales_person", "position": "Sales Executive", "profile_photo": "images/vishal.png"},
    "Santosh": {"password": "Santosh123", "role": "sales_person", "position": "Sales Executive", "profile_photo": "images/santosh.png"},
    "Deepak": {"password": "Deepak123", "role": "sales_person", "position": "Sales Executive", "profile_photo": "images/deepak.png"},
    "Rahul": {"password": "Rahul123", "role": "sales_person", "position": "Sales Executive", "profile_photo": "images/rahul.png"},
    "admin": {"password": "admin123", "role": "admin", "position": "System Administrator", "profile_photo": "images/admin.png"}
}

# --- Image Directory and Placeholder Creation ---
if not os.path.exists("images"):
    try: os.makedirs("images")
    except OSError as e: st.warning(f"Could not create images directory: {e}")

if PILLOW_INSTALLED:
    for user_key, user_data in USERS.items():
        img_path = user_data.get("profile_photo")
        if img_path and not os.path.exists(img_path):
            try:
                img = Image.new('RGB', (120, 120), color = (220, 230, 240)); draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", 40)
                except IOError: font = ImageFont.load_default()
                text = user_key[:2].upper()
                if hasattr(draw, 'textbbox'):
                    bbox = draw.textbbox((0,0), text, font=font); text_width, text_height = bbox[2]-bbox[0], bbox[3]-bbox[1]
                    text_x, text_y = (120-text_width)/2, (120-text_height)/2 - bbox[1]
                elif hasattr(draw, 'textsize'):
                    text_width, text_height = draw.textsize(text, font=font); text_x, text_y = (120-text_width)/2, (120-text_height)/2
                else: text_x, text_y = 30,30
                draw.text((text_x, text_y), text, fill=(28,78,128), font=font); img.save(img_path)
            except Exception as e: st.warning(f"Could not create placeholder image for {user_key}: {e}")
else:
    # This warning will now appear in the main app area if Pillow is not installed, as sidebar might not be rendered yet.
    # Consider moving it to after login if it's too intrusive.
    pass # Warning will be shown later if needed

# --- File Paths & Timezone & Directories ---
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"
GOALS_FILE = "goals.csv"
PAYMENT_GOALS_FILE = "payment_goals.csv"
ACTIVITY_LOG_FILE = "activity_log.csv"
ACTIVITY_PHOTOS_DIR = "activity_photos"

PRODUCTS_FILE = "products.csv"
STORES_FILE = "stores.csv"
ORDERS_FILE = "orders.csv"
ORDER_SUMMARY_FILE = "order_summary.csv"

for dir_path in [ACTIVITY_PHOTOS_DIR, "images"]:
    if not os.path.exists(dir_path):
        try: os.makedirs(dir_path)
        except OSError as e: st.warning(f"Could not create directory {dir_path}: {e}")

TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError: st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'."); st.stop()

def get_current_time_in_tz(): return datetime.now(timezone.utc).astimezone(tz)

def get_quarter_str_for_year(year):
    now_month = get_current_time_in_tz().month
    if 1 <= now_month <= 3: return f"{year}-Q1"
    elif 4 <= now_month <= 6: return f"{year}-Q2"
    elif 7 <= now_month <= 9: return f"{year}-Q3"
    else: return f"{year}-Q4"

def load_data(path, columns, parse_dates_cols=None):
    if os.path.exists(path):
        try:
            if os.path.getsize(path) > 0:
                df = pd.read_csv(path, parse_dates=parse_dates_cols)
                for col in columns:
                    if col not in df.columns: df[col] = pd.NA
                num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude", "UnitPrice", "Stock", "Quantity", "LineTotal", "Subtotal", "DiscountAmount", "TaxAmount", "GrandTotal"]
                for nc in num_cols:
                    if nc in df.columns: df[nc] = pd.to_numeric(df[nc], errors='coerce')
                return df
            else: return pd.DataFrame(columns=columns)
        except pd.errors.EmptyDataError: return pd.DataFrame(columns=columns)
        except Exception as e: st.error(f"Error loading {path}: {e}."); return pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
        try: df.to_csv(path, index=False)
        except Exception as e: st.warning(f"Could not create {path}: {e}")
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]
PRODUCTS_COLUMNS = ["ProductID", "SKU", "ProductName", "Category", "UnitPrice", "UnitOfMeasure", "Stock", "Description"]
STORES_COLUMNS = ["StoreID", "StoreName", "ContactPerson", "ContactPhone", "Address", "VillageTown", "District", "State", "Pincode", "GSTIN", "StoreType"]
ORDERS_COLUMNS = ["OrderID", "OrderDate", "Salesperson", "StoreID", "ProductID", "SKU", "ProductName", "Quantity", "UnitOfMeasure", "UnitPrice", "LineTotal"]
ORDER_SUMMARY_COLUMNS = ["OrderID", "OrderDate", "Salesperson", "StoreID", "StoreName", "Subtotal", "DiscountAmount", "TaxAmount", "GrandTotal", "Notes", "PaymentMode", "ExpectedDeliveryDate"]

attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS, parse_dates_cols=['Timestamp'])
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS, parse_dates_cols=['Date'])
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
activity_log_df = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS, parse_dates_cols=['Timestamp'])
products_df = load_data(PRODUCTS_FILE, PRODUCTS_COLUMNS)
if not products_df.empty:
    for col in ["UnitPrice", "Stock"]:
        if col in products_df.columns: products_df[col] = pd.to_numeric(products_df[col], errors='coerce').fillna(0)
stores_df = load_data(STORES_FILE, STORES_COLUMNS)
orders_df = load_data(ORDERS_FILE, ORDERS_COLUMNS, parse_dates_cols=['OrderDate'])
order_summary_df = load_data(ORDER_SUMMARY_FILE, ORDER_SUMMARY_COLUMNS, parse_dates_cols=['OrderDate', 'ExpectedDeliveryDate'])

def generate_order_id():
    global order_summary_df
    if order_summary_df.empty or "OrderID" not in order_summary_df.columns or order_summary_df["OrderID"].isnull().all():
        return "ORD-00001"
    existing_ids_series = order_summary_df["OrderID"].astype(str).str.extract(r'ORD-(\d+)')
    if existing_ids_series.empty or existing_ids_series[0].isnull().all():
        return "ORD-00001"
    valid_numeric_ids = pd.to_numeric(existing_ids_series[0], errors='coerce').dropna()
    if valid_numeric_ids.empty:
        next_num = 1
    else:
        next_num = int(valid_numeric_ids.max()) + 1
    return f"ORD-{next_num:05d}"

# --- End of Chunk 2 ---

# --- Chunk 3: Session State and Login ---

default_session_state = {
    "user_message": None, "message_type": None,
    "auth": {"logged_in": False, "username": None, "role": None},
    "order_line_items": [], "current_product_id_symplanta": None, "current_quantity_order": 1,
    "order_store_select": None, "order_notes": "", "order_discount": 0.0, "order_tax": 0.0,
    "selected_nav_label": None,
    "admin_order_view_selected_order_id": None
}
for key, value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = value

if not st.session_state.auth["logged_in"]:
    st.title("Symplanta TrackSphere")
    st.markdown("### Field Force & Sales Order Management")
    if not PILLOW_INSTALLED: # Show Pillow warning on login page if not installed
        st.warning("Pillow library not installed. User profile images might not display. `pip install Pillow`", icon="⚠️")

    message_placeholder_login = st.empty()
    if st.session_state.user_message:
        message_placeholder_login.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
        st.session_state.user_message = None; st.session_state.message_type = None

    st.markdown('<div class="login-container card" style="margin-top: 30px;">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined' style='font-size: 1.5em; margin-right: 8px; vertical-align:bottom;'>login</span> Login</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname_main")
    pwd = st.text_input("Password", type="password", key="login_pwd_main")
    if st.button("Login", key="login_button_main", type="primary"):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = f"Welcome back, {uname}!"; st.session_state.message_type = "success"
            st.session_state.selected_nav_label = None
            st.rerun()
        else: st.error("Invalid username or password.")
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

current_user_auth = st.session_state.auth

message_placeholder_main = st.empty()
if "user_message" in st.session_state and st.session_state.user_message:
    message_type_main = st.session_state.get("message_type", "info")
    message_placeholder_main.markdown(
        f"<div class='custom-notification {message_type_main}'>{st.session_state.user_message}</div>",
        unsafe_allow_html=True
    )
    st.session_state.user_message = None
    st.session_state.message_type = None

# --- End of Chunk 3 ---

# --- Chunk 4: Sidebar Navigation ---

with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user_auth['username']}!</div>", unsafe_allow_html=True)

    nav_options_base = {
        "Dashboard": "<span class='material-symbols-outlined'>dashboard</span> Dashboard",
        "Attendance": "<span class='material-symbols-outlined'>calendar_month</span> Attendance",
        "Upload Activity": "<span class='material-symbols-outlined'>upload_file</span> Upload Activity",
        "Allowance": "<span class='material-symbols-outlined'>receipt_long</span> Allowance Claim",
    }
    nav_options_sales = {
        "Create Order": "<span class='material-symbols-outlined'>add_shopping_cart</span> Create Order",
    }
    nav_options_goals = {
        "Sales Goals": "<span class='material-symbols-outlined'>flag</span> Sales Goals",
        "Payment Collection": "<span class='material-symbols-outlined'>payments</span> Payment Collection",
    }
    nav_options_admin_logs_and_orders = { # Combined for admin
        "Manage Records": "<span class='material-symbols-outlined'>admin_panel_settings</span> Manage Records", # Single entry for admin logs/orders
    }
    nav_options_employee_logs = {
         "My Records": "<span class='material-symbols-outlined'>article</span> My Records",
    }

    nav_options_with_icons = nav_options_base.copy()
    if current_user_auth['role'] == 'sales_person':
        nav_options_with_icons.update(nav_options_sales)
        nav_options_with_icons.update(nav_options_goals)
        nav_options_with_icons.update(nav_options_employee_logs)
    elif current_user_auth['role'] == 'admin':
        nav_options_with_icons.update(nav_options_goals)
        nav_options_with_icons.update(nav_options_admin_logs_and_orders) # Admin gets Manage Records
    elif current_user_auth['role'] == 'employee':
        nav_options_with_icons.update(nav_options_employee_logs)

    option_labels = list(nav_options_with_icons.values())
    option_keys = list(nav_options_with_icons.keys())

    if st.session_state.selected_nav_label is None or st.session_state.selected_nav_label not in option_labels:
        st.session_state.selected_nav_label = option_labels[0] if option_labels else None

    st.markdown("<h5 style='margin-top:0; margin-bottom:10px; font-weight:500; color: var(--text-color); padding-left:10px;'>Navigation</h5>", unsafe_allow_html=True)
    selected_nav_html_label = st.radio(
        "MainNavigationRadio",
        options=option_labels,
        index=option_labels.index(st.session_state.selected_nav_label) if st.session_state.selected_nav_label in option_labels else 0,
        label_visibility="collapsed",
        key="sidebar_nav_radio_key_main" # Ensure a unique key
    )
    st.session_state.selected_nav_label = selected_nav_html_label

    nav = ""
    for key_nav, html_label_nav in nav_options_with_icons.items():
        if html_label_nav == selected_nav_html_label:
            nav = key_nav
            break

    user_sidebar_info = USERS.get(current_user_auth["username"], {})
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]):
        st.image(user_sidebar_info["profile_photo"], width=100)
    elif PILLOW_INSTALLED: st.caption("Profile photo not available.")

    st.markdown(
        f"<p style='text-align:center; font-size:0.9em; color: var(--text-muted-color);'>{user_sidebar_info.get('position', 'N/A')}</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")
    if st.button("🔒 Logout", key="logout_button_sidebar_main_key", use_container_width=True): # Unique key
        for key_to_reset in default_session_state:
            if key_to_reset == "auth":
                 st.session_state[key_to_reset] = {"logged_in": False, "username": None, "role": None}
            else:
                st.session_state[key_to_reset] = default_session_state[key_to_reset]
        st.session_state.user_message = "Logged out successfully."
        st.session_state.message_type = "info"
        st.rerun()


        
# --- End of Chunk 4 ---

# --- Chunk 5: Dashboard, Create Order ---

if nav == "Dashboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>dashboard</span> Dashboard</h3>", unsafe_allow_html=True)
    st.write(f"Welcome to the Dashboard, {current_user_auth['username']}!")
    st.info("Dashboard content to be implemented. This will show key metrics and summaries based on your role.")
    # Add role-specific dashboard content here if desired
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Create Order" and current_user_auth['role'] == 'sales_person':
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>add_shopping_cart</span> Create New Sales Order</h3>", unsafe_allow_html=True)

    order_date_display = get_current_time_in_tz().strftime("%Y-%m-%d")
    salesperson_name_display = current_user_auth["username"]

    st.markdown("<h4>Order Header</h4>", unsafe_allow_html=True)
    col_header1, col_header2 = st.columns(2)
    with col_header1:
        st.text_input("Order Date", value=order_date_display, disabled=True, key="order_form_date_val")
        st.text_input("Salesperson", value=salesperson_name_display, disabled=True, key="order_form_salesperson_val")
    with col_header2:
        if stores_df.empty:
            st.warning("No stores found. Please add stores to 'stores.csv'. Store selection is crucial for orders.", icon="🏬")
            selected_store_id_form = None
            # Fallback to manual entry (less ideal)
            # selected_store_name_manual_form = st.text_input("Store Name (Manual Entry)", key="manual_store_order_form")
            # st.session_state.order_store_select = "MANUAL_" + selected_store_name_manual_form if selected_store_name_manual_form.strip() else None
            st.session_state.order_store_select = None # Force selection if list is empty
        else:
            store_options_dict_form = {row['StoreID']: f"{row['StoreName']} ({row['StoreID']})" for index, row in stores_df.iterrows()}
            current_store_selection_form = st.session_state.order_store_select # Already a key or None
            
            # Prepare options for selectbox, ensuring current selection is valid
            options_for_sb = [None] + list(store_options_dict_form.keys())
            current_index_sb = 0 # Default to "Select a store..."
            if current_store_selection_form in store_options_dict_form:
                current_index_sb = options_for_sb.index(current_store_selection_form)

            selected_store_id_form = st.selectbox(
                "Select Store *",
                options=options_for_sb,
                format_func=lambda x: "Select a store..." if x is None else store_options_dict_form[x],
                key="order_store_select_form_sb",
                index=current_index_sb
            )
            st.session_state.order_store_select = selected_store_id_form

    st.markdown("---")
    st.markdown("<h4><span class='material-symbols-outlined'>playlist_add</span> Add Products to Order</h4>", unsafe_allow_html=True)

    if products_df.empty:
        st.error("Product catalog ('products.csv') is empty or not found. Cannot create orders.", icon="🚫")
    else:
        categories_list_form = ["All Categories"] + sorted(products_df['Category'].unique().tolist())
        selected_category_filter_form = st.selectbox("Filter by Product Category", options=categories_list_form, key="order_product_cat_filter_form")

        filtered_products_order_form = products_df.copy()
        if selected_category_filter_form != "All Categories":
            filtered_products_order_form = products_df[products_df['Category'] == selected_category_filter_form]

        if filtered_products_order_form.empty:
            st.info(f"No products found for category: {selected_category_filter_form}" if selected_category_filter_form != "All Categories" else "No products available.", icon="ℹ️")
            product_options_order_form = {}
        else:
            product_options_order_form = {
                row['ProductID']: f"{row['ProductName']} ({row['SKU']}) - ₹{row['UnitPrice']:.2f} / {row['UnitOfMeasure']}"
                for index, row in filtered_products_order_form.iterrows()
            }

        col_prod_form, col_qty_form, col_add_btn_form = st.columns([3, 1, 1.2])
        with col_prod_form:
            current_prod_id_val_form = st.session_state.current_product_id_symplanta
            options_prod_sb = [None] + list(product_options_order_form.keys())
            current_prod_idx_sb = 0
            if current_prod_id_val_form in product_options_order_form:
                current_prod_idx_sb = options_prod_sb.index(current_prod_id_val_form)

            selected_product_id_order_form = st.selectbox(
                "Select Product *",
                options=options_prod_sb,
                format_func=lambda x: "Choose a product..." if x is None else product_options_order_form[x],
                key="order_product_select_actual_form",
                index=current_prod_idx_sb
            )
            st.session_state.current_product_id_symplanta = selected_product_id_order_form

        with col_qty_form:
            st.session_state.current_quantity_order = st.number_input("Quantity *", min_value=1, value=st.session_state.current_quantity_order, step=1, key="order_quantity_input_val_form")

        def add_item_to_order_cb_form():
            if st.session_state.current_product_id_symplanta and st.session_state.current_quantity_order > 0:
                product_info_form = products_df[products_df['ProductID'] == st.session_state.current_product_id_symplanta].iloc[0]
                existing_item_index_form = -1
                for i_form, item_in_order_form in enumerate(st.session_state.order_line_items):
                    if item_in_order_form['ProductID'] == st.session_state.current_product_id_symplanta:
                        existing_item_index_form = i_form
                        break
                if existing_item_index_form != -1:
                    st.session_state.order_line_items[existing_item_index_form]['Quantity'] += st.session_state.current_quantity_order
                    st.session_state.order_line_items[existing_item_index_form]['LineTotal'] = st.session_state.order_line_items[existing_item_index_form]['Quantity'] * st.session_state.order_line_items[existing_item_index_form]['UnitPrice']
                    st.toast(f"Updated quantity for {product_info_form['ProductName']}.", icon="🔄")
                else:
                    st.session_state.order_line_items.append({
                        "ProductID": product_info_form['ProductID'], "SKU": product_info_form['SKU'],
                        "ProductName": product_info_form['ProductName'], "Quantity": st.session_state.current_quantity_order,
                        "UnitOfMeasure": product_info_form['UnitOfMeasure'], "UnitPrice": float(product_info_form['UnitPrice']),
                        "LineTotal": st.session_state.current_quantity_order * float(product_info_form['UnitPrice'])
                    })
                    st.toast(f"Added {product_info_form['ProductName']} to order.", icon="✅")
                st.session_state.current_quantity_order = 1
            else:
                st.warning("Please select a product and specify quantity > 0.", icon="⚠️")

        with col_add_btn_form:
            st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
            st.button("➕ Add to Order", on_click=add_item_to_order_cb_form, key="add_to_order_button_main_form")

    if st.session_state.order_line_items:
        st.markdown("---")
        st.markdown("<h4><span class='material-symbols-outlined'>receipt_long</span> Current Order Items</h4>", unsafe_allow_html=True)
        for i_item_disp, item_data_disp in enumerate(st.session_state.order_line_items):
            item_cols_disp = st.columns([4, 1, 2, 2, 1])
            item_cols_disp[0].markdown(f"**{item_data_disp['ProductName']}** ({item_data_disp['SKU']}) <br><small>{item_data_disp['UnitOfMeasure']}</small>", unsafe_allow_html=True)
            item_cols_disp[1].markdown(f"{item_data_disp['Quantity']}")
            item_cols_disp[2].markdown(f"₹{item_data_disp['UnitPrice']:.2f}")
            item_cols_disp[3].markdown(f"**₹{item_data_disp['LineTotal']:.2f}**")
            if item_cols_disp[4].button("➖", key=f"delete_item_order_form_{i_item_disp}", help="Remove this item"):
                st.session_state.order_line_items.pop(i_item_disp)
                st.rerun()
            if i_item_disp < len(st.session_state.order_line_items) -1 : st.divider()

        subtotal_order_form = sum(item['LineTotal'] for item in st.session_state.order_line_items)
        col_summary1_form, col_summary2_form = st.columns(2)
        with col_summary1_form:
            st.session_state.order_discount = st.number_input("Discount Amount (₹)", min_value=0.0, value=st.session_state.order_discount, step=10.0, key="order_form_discount_val_main")
            st.session_state.order_tax = st.number_input("Tax Amount (₹)", min_value=0.0, value=st.session_state.order_tax, step=5.0, key="order_form_tax_val_main", help="Enter total tax amount if applicable")
        grand_total_order_form = subtotal_order_form - st.session_state.order_discount + st.session_state.order_tax
        with col_summary2_form:
            st.markdown(f"""
            <div style='text-align:right; margin-top: 20px;'>
                <p style='margin-bottom: 2px;'>Subtotal:    <strong>₹{subtotal_order_form:,.2f}</strong></p>
                <p style='margin-bottom: 2px; color: var(--danger-color);'>Discount:    - ₹{st.session_state.order_discount:,.2f}</p>
                <p style='margin-bottom: 2px;'>Tax:    + ₹{st.session_state.order_tax:,.2f}</p>
                <h4 style='margin-top: 5px; border-top: 1px solid var(--border-color); padding-top:5px;'>Grand Total:    ₹{grand_total_order_form:,.2f}</h4>
            </div>
            """, unsafe_allow_html=True)

        st.session_state.order_notes = st.text_area("Order Notes / Payment Mode / Expected Delivery", value=st.session_state.order_notes, key="order_form_notes_val_main", placeholder="E.g., Payment by UPI, Deliver by next Tuesday")

        if st.button("✅ Submit Order", key="submit_order_button_main_page", type="primary", use_container_width=True):
            final_selected_store_id_submit = st.session_state.order_store_select
            store_name_for_summary_submit = "N/A"

            if not final_selected_store_id_submit : # Must select a store
                st.error("Store selection is mandatory. Please select a store.", icon="🏬")
            elif not st.session_state.order_line_items:
                st.error("Cannot submit an empty order. Please add products.", icon="🛒")
            else: # Store selected and items exist
                store_info_submit_df = stores_df[stores_df['StoreID'] == final_selected_store_id_submit]
                if not store_info_submit_df.empty:
                    store_name_for_summary_submit = store_info_submit_df['StoreName'].iloc[0]
                else: # Should not happen if store ID is valid
                    st.error("Internal error: Selected store details not found.", icon="❌")
                    st.stop()

                global orders_df, order_summary_df
                new_order_id_val_submit = generate_order_id()
                order_date_submit_val_final = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
                new_order_items_list_submit_final = []
                for item_data_submit_final in st.session_state.order_line_items:
                    new_order_items_list_submit_final.append({
                        "OrderID": new_order_id_val_submit, "OrderDate": order_date_submit_val_final,
                        "Salesperson": salesperson_name_display, "StoreID": final_selected_store_id_submit,
                        "ProductID": item_data_submit_final['ProductID'], "SKU": item_data_submit_final['SKU'],
                        "ProductName": item_data_submit_final['ProductName'], "Quantity": item_data_submit_final['Quantity'],
                        "UnitOfMeasure": item_data_submit_final['UnitOfMeasure'], "UnitPrice": item_data_submit_final['UnitPrice'],
                        "LineTotal": item_data_submit_final['LineTotal']
                    })
                new_orders_entries_df_submit_final = pd.DataFrame(new_order_items_list_submit_final, columns=ORDERS_COLUMNS)
                temp_orders_df_submit_final = pd.concat([orders_df, new_orders_entries_df_submit_final], ignore_index=True)
                summary_data_submit_final = {
                    "OrderID": new_order_id_val_submit, "OrderDate": order_date_submit_val_final,
                    "Salesperson": salesperson_name_display, "StoreID": final_selected_store_id_submit,
                    "StoreName": store_name_for_summary_submit, "Subtotal": subtotal_order_form,
                    "DiscountAmount": st.session_state.order_discount, "TaxAmount": st.session_state.order_tax,
                    "GrandTotal": grand_total_order_form, "Notes": st.session_state.order_notes.strip(),
                    "PaymentMode": pd.NA, "ExpectedDeliveryDate": pd.NA
                }
                new_summary_entry_df_submit_final = pd.DataFrame([summary_data_submit_final], columns=ORDER_SUMMARY_COLUMNS)
                temp_order_summary_df_submit_final = pd.concat([order_summary_df, new_summary_entry_df_submit_final], ignore_index=True)
                try:
                    temp_orders_df_submit_final.to_csv(ORDERS_FILE, index=False)
                    temp_order_summary_df_submit_final.to_csv(ORDER_SUMMARY_FILE, index=False)
                    orders_df = temp_orders_df_submit_final
                    order_summary_df = temp_order_summary_df_submit_final
                    st.session_state.user_message = f"Order {new_order_id_val_submit} for '{store_name_for_summary_submit}' submitted successfully!"
                    st.session_state.message_type = "success"
                    st.session_state.order_line_items = []
                    st.session_state.current_product_id_symplanta = None
                    st.session_state.current_quantity_order = 1
                    st.session_state.order_store_select = None
                    st.session_state.order_notes = ""
                    st.session_state.order_discount = 0.0
                    st.session_state.order_tax = 0.0
                    st.rerun()
                except Exception as e_submit:
                    st.session_state.user_message = f"Error submitting order: {e_submit}"
                    st.session_state.message_type = "error"
                    st.rerun()
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Add products to the order to see summary and submit.", icon="💡")
    st.markdown("</div>", unsafe_allow_html=True)

# --- End of Chunk 5 ---

**Chunk 6: Attendance, Upload Activity, Allowance Pages**

```python
# --- Chunk 6: Attendance, Upload Activity, Allowance ---

elif nav == "Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>calendar_month</span> Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services for general attendance are currently illustrative. Photos for specific field activities can be uploaded from the 'Upload Activity' section.", icon="ℹ️")
    st.markdown("---"); st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col_att1, col_att2 = st.columns(2)
    common_data_att = {"Username": current_user_auth["username"], "Latitude": pd.NA, "Longitude": pd.NA}

    def process_general_attendance_cb(attendance_type_param):
        global attendance_df
        now_str_display_att = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_data_att = {"Type": attendance_type_param, "Timestamp": now_str_display_att, **common_data_att}
        for col_name_att in ATTENDANCE_COLUMNS:
            if col_name_att not in new_entry_data_att: new_entry_data_att[col_name_att] = pd.NA
        new_entry_att = pd.DataFrame([new_entry_data_att], columns=ATTENDANCE_COLUMNS)
        temp_attendance_df_att = pd.concat([attendance_df, new_entry_att], ignore_index=True)
        try:
            temp_attendance_df_att.to_csv(ATTENDANCE_FILE, index=False)
            attendance_df = temp_attendance_df_att
            st.session_state.user_message = f"{attendance_type_param} recorded at {now_str_display_att}."; st.session_state.message_type = "success"; st.rerun()
        except Exception as e_att: st.session_state.user_message = f"Error saving attendance: {e_att}"; st.session_state.message_type = "error"; st.rerun()

    with col_att1:
        if st.button("✅ Check In", key="check_in_btn_page_main", use_container_width=True, on_click=process_general_attendance_cb, args=("Check-In",)):
            pass
    with col_att2:
        if st.button("🚪 Check Out", key="check_out_btn_page_main", use_container_width=True, on_click=process_general_attendance_cb, args=("Check-Out",)):
            pass
    st.markdown('</div></div>', unsafe_allow_html=True)

elif nav == "Upload Activity":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>upload_file</span> Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat_act, current_lon_act = pd.NA, pd.NA

    with st.form(key="activity_photo_form_main_page"):
        st.markdown("<h6><span class='material-symbols-outlined'>description</span> Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description_val = st.text_area("Brief description of activity/visit:", key="activity_desc_val_page", help="E.g., Met with Client X, Demoed Product Y.")
        st.markdown("<h6><span class='material-symbols-outlined'>photo_camera</span> Capture Activity Photo:</h6>", unsafe_allow_html=True)
        img_file_buffer_activity_val = st.camera_input("Take a picture of your activity/visit", key="activity_camera_input_val_page", help="A photo provides context to your activity.")
        submit_activity_photo_btn = st.form_submit_button("⬆️ Upload Photo and Log Activity", type="primary")

    if submit_activity_photo_btn:
        if img_file_buffer_activity_val is None: st.warning("Please take a picture before submitting.", icon="📸")
        elif not activity_description_val.strip(): st.warning("Please provide a description for the activity.", icon="✏️")
        else:
            global activity_log_df
            now_for_filename_act = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S")
            now_for_display_act = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            image_filename_act = f"{current_user_auth['username']}_activity_{now_for_filename_act}.jpg"
            image_path_act = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_act)
            try:
                with open(image_path_act, "wb") as f_act: f_act.write(img_file_buffer_activity_val.getbuffer())
                new_activity_data_val = {"Username": current_user_auth["username"], "Timestamp": now_for_display_act, "Description": activity_description_val, "ImageFile": image_filename_act, "Latitude": current_lat_act, "Longitude": current_lon_act}
                for col_name_act in ACTIVITY_LOG_COLUMNS:
                    if col_name_act not in new_activity_data_val: new_activity_data_val[col_name_act] = pd.NA
                new_activity_entry_df = pd.DataFrame([new_activity_data_val], columns=ACTIVITY_LOG_COLUMNS)
                temp_activity_log_df_val = pd.concat([activity_log_df, new_activity_entry_df], ignore_index=True)
                temp_activity_log_df_val.to_csv(ACTIVITY_LOG_FILE, index=False)
                activity_log_df = temp_activity_log_df_val
                st.session_state.user_message = "Activity photo and log uploaded successfully!"; st.session_state.message_type = "success"; st.rerun()
            except Exception as e_act_save: st.session_state.user_message = f"Error saving activity: {e_act_save}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>receipt_long</span> Claim Allowance</h3>", unsafe_allow_html=True)
    st.markdown("<div class='form-field-label'><h6>Select Allowance Type:</h6></div>", unsafe_allow_html=True)
    a_type_val = st.radio("AllowanceTypeRadioPage", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allowance_type_radio_page_main", horizontal=True, label_visibility='collapsed')
    amount_val = st.number_input("Enter Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_page_main")
    reason_val = st.text_area("Reason for Allowance:", key="allowance_reason_page_main", placeholder="Please provide a clear justification for the allowance claim...")
    if st.button("Submit Allowance Request", key="submit_allowance_btn_page_main", type="primary", use_container_width=True):
        if a_type_val and amount_val > 0 and reason_val.strip():
            global allowance_df
            date_str_allow = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry_data_allow = {"Username": current_user_auth["username"], "Type": a_type_val, "Amount": amount_val, "Reason": reason_val, "Date": date_str_allow}
            for col_name_allow in ALLOWANCE_COLUMNS:
                if col_name_allow not in new_entry_data_allow: new_entry_data_allow[col_name_allow] = pd.NA
            new_entry_allow_df = pd.DataFrame([new_entry_data_allow], columns=ALLOWANCE_COLUMNS)
            temp_allowance_df_val = pd.concat([allowance_df, new_entry_allow_df], ignore_index=True)
            try:
                temp_allowance_df_val.to_csv(ALLOWANCE_FILE, index=False)
                allowance_df = temp_allowance_df_val
                st.session_state.user_message = f"Allowance claim for ₹{amount_val:.2f} submitted."; st.session_state.message_type = "success"; st.rerun()
            except Exception as e_allow_save: st.session_state.user_message = f"Error submitting allowance: {e_allow_save}"; st.session_state.message_type = "error"; st.rerun()
        else: st.warning("Please complete all fields with valid values for allowance claim.", icon="⚠️")
    st.markdown('</div>', unsafe_allow_html=True)

# --- End of Chunk 6 ---
# --- Chunk 7: Sales Goals Page ---

elif nav == "Sales Goals":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>flag</span> Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_GOAL_YEAR_SALES = 2025
    current_quarter_sales_display = get_quarter_str_for_year(TARGET_GOAL_YEAR_SALES)
    status_options_goals = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    if current_user_auth["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Sales Goals</h4>", unsafe_allow_html=True)
        admin_action_sales_goals = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR_SALES}"], key="admin_sales_goal_action_radio_page", horizontal=True)
        if admin_action_sales_goals == "View Team Progress":
            st.markdown(f"<h5>Team Sales Goal Progress for {current_quarter_sales_display}</h5>", unsafe_allow_html=True)
            employee_users_list_sg = [uname for uname, udata in USERS.items() if udata["role"] in ["employee", "sales_person"]]
            if not employee_users_list_sg: st.info("No employees/salespersons found.")
            else:
                summary_list_sales_page_sg = []
                for emp_name_sg_admin_view in employee_users_list_sg:
                    emp_current_sg_admin_view = goals_df[(goals_df["Username"].astype(str) == str(emp_name_sg_admin_view)) & (goals_df["MonthYear"].astype(str) == str(current_quarter_sales_display))]
                    target_sg_val, achieved_sg_val, status_val_sg_val = 0.0, 0.0, "Not Set"
                    if not emp_current_sg_admin_view.empty:
                        g_data_sg_av = emp_current_sg_admin_view.iloc[0]
                        target_sg_val = float(pd.to_numeric(g_data_sg_av.get("TargetAmount"), errors='coerce').fillna(0.0))
                        achieved_sg_val = float(pd.to_numeric(g_data_sg_av.get("AchievedAmount"), errors='coerce').fillna(0.0))
                        status_val_sg_val = g_data_sg_av.get("Status", "N/A")
                    summary_list_sales_page_sg.append({"Employee": emp_name_sg_admin_view, "Target": target_sg_val, "Achieved": achieved_sg_val, "Status": status_val_sg_val})
                summary_df_sales_page_sg_display = pd.DataFrame(summary_list_sales_page_sg)
                if not summary_df_sales_page_sg_display.empty:
                    st.markdown("<h6>Individual Sales Progress:</h6>", unsafe_allow_html=True)
                    num_cols_sg_disp = min(3, len(summary_df_sales_page_sg_display)) if len(summary_df_sales_page_sg_display) > 0 else 1
                    cols_sg_disp = st.columns(num_cols_sg_disp)
                    for idx_sg_disp, row_sg_disp in summary_df_sales_page_sg_display.iterrows():
                        progress_pct_sg_disp = (row_sg_disp['Achieved'] / row_sg_disp['Target'] * 100) if row_sg_disp['Target'] > 0 else 0
                        donut_fig_sg_disp = create_donut_chart(progress_pct_sg_disp, achieved_color='#34A853')
                        with cols_sg_disp[idx_sg_disp % num_cols_sg_disp]:
                            st.markdown(f"<div class='employee-progress-item'><h6>{row_sg_disp['Employee']}</h6><p>Target: ₹{row_sg_disp['Target']:,.0f}<br>Achieved: ₹{row_sg_disp['Achieved']:,.0f}</p></div>", unsafe_allow_html=True)
                            if donut_fig_sg_disp: st.pyplot(donut_fig_sg_disp, use_container_width=True)
                            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin-top: 10px; margin-bottom:25px;'>", unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Sales Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_sg_page_disp = create_team_progress_bar_chart(summary_df_sales_page_sg_display, title="Team Sales Target vs. Achieved")
                    if team_bar_fig_sg_page_disp: st.pyplot(team_bar_fig_sg_page_disp, use_container_width=True)
                    else: st.info("No sales data to plot team bar chart.")
                else: st.info(f"No sales goals data found for {current_quarter_sales_display} to display team progress.")

        elif admin_action_sales_goals == f"Set/Edit Goal for {TARGET_GOAL_YEAR_SALES}":
            st.markdown(f"<h5>Set or Update Employee Sales Goal ({TARGET_GOAL_YEAR_SALES} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options_sg_admin_set = [u for u,d in USERS.items() if d["role"] in ["employee", "sales_person"]]
            if not employee_options_sg_admin_set: st.warning("No employees/salespersons available.")
            else:
                selected_emp_sg_admin_set = st.radio("Select Employee:", employee_options_sg_admin_set, key="sg_emp_radio_admin_set_page", horizontal=True)
                quarter_options_sg_admin_set = [f"{TARGET_GOAL_YEAR_SALES}-Q{i}" for i in range(1,5)]
                selected_period_sg_admin_set = st.radio("Goal Period:", quarter_options_sg_admin_set, key="sg_period_radio_admin_set_page", horizontal=True)
                existing_sg_admin_set = goals_df[(goals_df["Username"].astype(str)==str(selected_emp_sg_admin_set)) & (goals_df["MonthYear"].astype(str)==str(selected_period_sg_admin_set))]
                g_desc_sg_set, g_target_sg_set, g_achieved_sg_set, g_status_sg_set = "", 0.0, 0.0, "Not Started"
                if not existing_sg_admin_set.empty:
                    g_data_sg_edit_set = existing_sg_admin_set.iloc[0]
                    g_desc_sg_set=g_data_sg_edit_set.get("GoalDescription","")
                    g_target_sg_set=float(pd.to_numeric(g_data_sg_edit_set.get("TargetAmount"),errors='coerce').fillna(0.0))
                    g_achieved_sg_set=float(pd.to_numeric(g_data_sg_edit_set.get("AchievedAmount"),errors='coerce').fillna(0.0))
                    g_status_sg_set=g_data_sg_edit_set.get("Status","Not Started")
                    st.info(f"Editing sales goal for {selected_emp_sg_admin_set} - {selected_period_sg_admin_set}")
                with st.form(key=f"set_sg_form_{selected_emp_sg_admin_set}_{selected_period_sg_admin_set}_page"):
                    new_desc_sg_set=st.text_area("Goal Description",value=g_desc_sg_set,key=f"desc_sg_admin_edit_page")
                    new_target_sg_set=st.number_input("Target Sales (INR)",value=g_target_sg_set,min_value=0.0,step=1000.0,format="%.2f",key=f"target_sg_admin_edit_page")
                    new_achieved_sg_set=st.number_input("Achieved Sales (INR)",value=g_achieved_sg_set,min_value=0.0,step=100.0,format="%.2f",key=f"achieved_sg_admin_edit_page")
                    new_status_sg_set=st.radio("Status:",status_options_goals,index=status_options_goals.index(g_status_sg_set),horizontal=True,key=f"status_sg_admin_edit_page")
                    submitted_sg_admin_set=st.form_submit_button("Save Sales Goal", type="primary")
                if submitted_sg_admin_set:
                    if not new_desc_sg_set.strip(): st.warning("Description is required.")
                    elif new_target_sg_set <= 0 and new_status_sg_set not in ["Cancelled","On Hold","Not Started"]: st.warning("Target amount must be > 0 unless status is Cancelled, On Hold, or Not Started.")
                    else:
                        global goals_df
                        editable_goals_df_admin_set = goals_df.copy()
                        existing_sg_indices_admin_set = editable_goals_df_admin_set[(editable_goals_df_admin_set["Username"].astype(str)==str(selected_emp_sg_admin_set))&(editable_goals_df_admin_set["MonthYear"].astype(str)==str(selected_period_sg_admin_set))].index
                        update_data_sg_set = {"Username":selected_emp_sg_admin_set,"MonthYear":selected_period_sg_admin_set,"GoalDescription":new_desc_sg_set,"TargetAmount":new_target_sg_set,"AchievedAmount":new_achieved_sg_set,"Status":new_status_sg_set}
                        for col_name_sg_check_set in GOALS_COLUMNS:
                            if col_name_sg_check_set not in update_data_sg_set: update_data_sg_set[col_name_sg_check_set]=pd.NA
                        if not existing_sg_indices_admin_set.empty:
                            editable_goals_df_admin_set.loc[existing_sg_indices_admin_set[0]] = pd.Series(update_data_sg_set)
                            msg_verb_sg_set="updated"
                        else:
                            new_row_df_sg_admin_set = pd.DataFrame([update_data_sg_set], columns=GOALS_COLUMNS)
                            editable_goals_df_admin_set = pd.concat([editable_goals_df_admin_set, new_row_df_sg_admin_set], ignore_index=True)
                            msg_verb_sg_set="set"
                        try:
                            editable_goals_df_admin_set.to_csv(GOALS_FILE,index=False)
                            goals_df = editable_goals_df_admin_set
                            st.session_state.user_message=f"Sales Goal for {selected_emp_sg_admin_set} ({selected_period_sg_admin_set}) {msg_verb_sg_set}!"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e_sg_save_set: st.session_state.user_message=f"Error saving sales goal: {e_sg_save_set}"; st.session_state.message_type="error"; st.rerun()
    
    elif current_user_auth['role'] in ['sales_person', 'employee']:
        st.markdown(f"<h4>My Sales Goals ({TARGET_GOAL_YEAR_SALES} - Quarterly)</h4>", unsafe_allow_html=True)
        my_goals_sg_user_view = goals_df[goals_df["Username"].astype(str) == str(current_user_auth["username"])].copy()
        for col_sg_num_uv in ["TargetAmount", "AchievedAmount"]: my_goals_sg_user_view[col_sg_num_uv] = pd.to_numeric(my_goals_sg_user_view[col_sg_num_uv], errors="coerce").fillna(0.0)
        current_sg_user_df_view = my_goals_sg_user_view[my_goals_sg_user_view["MonthYear"] == current_quarter_sales_display]
        st.markdown(f"<h5>Current Goal Period: {current_quarter_sales_display}</h5>", unsafe_allow_html=True)
        if not current_sg_user_df_view.empty:
            g_sg_user_view = current_sg_user_df_view.iloc[0]; target_amt_sg_user_v = g_sg_user_view["TargetAmount"]; achieved_amt_sg_user_v = g_sg_user_view["AchievedAmount"]
            st.markdown(f"**Description:** {g_sg_user_view.get('GoalDescription', 'N/A')}")
            col_metrics_sg_user_v, col_chart_sg_user_v = st.columns([0.6, 0.4])
            with col_metrics_sg_user_v:
                sub_col1_sg_user_v,sub_col2_sg_user_v=st.columns(2)
                sub_col1_sg_user_v.metric("Target",f"₹{target_amt_sg_user_v:,.0f}")
                sub_col2_sg_user_v.metric("Achieved",f"₹{achieved_amt_sg_user_v:,.0f}")
                st.metric("Status",g_sg_user_view.get("Status","In Progress"),label_visibility="visible")
            with col_chart_sg_user_v:
                progress_pct_sg_user_v=(achieved_amt_sg_user_v/target_amt_sg_user_v*100) if target_amt_sg_user_v > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:0px;'>Sales Progress</h6>",unsafe_allow_html=True)
                donut_fig_sg_user_v=create_donut_chart(progress_pct_sg_user_v,"Sales Progress",achieved_color='#34A853')
                if donut_fig_sg_user_v: st.pyplot(donut_fig_sg_user_v,use_container_width=True)
            st.markdown("---")
            if current_user_auth['role'] == 'sales_person':
                with st.form(key=f"update_achievement_sg_{current_user_auth['username']}_{current_quarter_sales_display}_page"):
                    new_val_sg_user_v=st.number_input("Update My Achieved Sales (INR):",value=achieved_amt_sg_user_v,min_value=0.0,step=100.0,format="%.2f")
                    submitted_ach_sg_user_v=st.form_submit_button("Update My Achievement", type="primary")
                if submitted_ach_sg_user_v:
                    global goals_df
                    editable_goals_df_user_v = goals_df.copy()
                    idx_sg_user_v = editable_goals_df_user_v[(editable_goals_df_user_v["Username"] == current_user_auth["username"]) &(editable_goals_df_user_v["MonthYear"] == current_quarter_sales_display)].index
                    if not idx_sg_user_v.empty:
                        editable_goals_df_user_v.loc[idx_sg_user_v[0],"AchievedAmount"]=new_val_sg_user_v
                        new_status_sg_user_v="Achieved" if new_val_sg_user_v >= target_amt_sg_user_v and target_amt_sg_user_v > 0 else "In Progress"
                        editable_goals_df_user_v.loc[idx_sg_user_v[0],"Status"]=new_status_sg_user_v
                        try:
                            editable_goals_df_user_v.to_csv(GOALS_FILE,index=False)
                            goals_df = editable_goals_df_user_v
                            st.session_state.user_message = "Your sales achievement updated!"; st.session_state.message_type = "success"; st.rerun()
                        except Exception as e_sg_user_save_v: st.session_state.user_message = f"Error updating sales achievement: {e_sg_user_save_v}"; st.session_state.message_type = "error"; st.rerun()
                    else: st.session_state.user_message = "Could not find your current sales goal to update."; st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No sales goal set for you for {current_quarter_sales_display}. Please contact your administrator.")
        st.markdown(f"---"); st.markdown(f"<h5>My Past Sales Goals ({TARGET_GOAL_YEAR_SALES})</h5>", unsafe_allow_html=True)
        past_goals_sg_user_v = my_goals_sg_user_view[(my_goals_sg_user_view["MonthYear"].astype(str).str.startswith(str(TARGET_GOAL_YEAR_SALES))) & (my_goals_sg_user_view["MonthYear"].astype(str) != current_quarter_sales_display)]
        if not past_goals_sg_user_v.empty: render_goal_chart(past_goals_sg_user_v, "My Past Sales Goal Performance")
        else: st.info(f"No past sales goal records for {TARGET_GOAL_YEAR_SALES}.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- End of Chunk 7 ---
**Chunk 8: Payment Collection Page**

```python
# --- Chunk 8: Payment Collection Page ---

elif nav == "Payment Collection":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>payments</span> Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_YEAR_PAY_TRACKER = 2025
    current_quarter_pay_display = get_quarter_str_for_year(TARGET_YEAR_PAY_TRACKER)
    status_options_pay = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    if current_user_auth["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action_pay = st.radio("Action:", ["View Team Progress", f"Set/Edit Collection Target for {TARGET_YEAR_PAY_TRACKER}"], key="admin_pay_goal_action_radio_page", horizontal=True)
        if admin_action_pay == "View Team Progress":
            st.markdown(f"<h5>Team Payment Collection Progress for {current_quarter_pay_display}</h5>", unsafe_allow_html=True)
            employee_users_pay_list_admin = [uname for uname, udata in USERS.items() if udata["role"] in ["employee", "sales_person"]]
            if not employee_users_pay_list_admin: st.info("No employees/salespersons found.")
            else:
                summary_list_pay_page_admin = []
                for emp_name_pay_admin_v in employee_users_pay_list_admin:
                    emp_current_pay_goal_admin_v = payment_goals_df[(payment_goals_df["Username"].astype(str) == str(emp_name_pay_admin_v)) & (payment_goals_df["MonthYear"].astype(str) == str(current_quarter_pay_display))]
                    target_pay_v, achieved_pay_v, status_val_pay_v = 0.0, 0.0, "Not Set"
                    if not emp_current_pay_goal_admin_v.empty:
                        g_data_pay_v = emp_current_pay_goal_admin_v.iloc[0]
                        target_pay_v = float(pd.to_numeric(g_data_pay_v.get("TargetAmount"), errors='coerce').fillna(0.0))
                        achieved_pay_v = float(pd.to_numeric(g_data_pay_v.get("AchievedAmount"), errors='coerce').fillna(0.0))
                        status_val_pay_v = g_data_pay_v.get("Status", "N/A")
                    summary_list_pay_page_admin.append({"Employee": emp_name_pay_admin_v, "Target": target_pay_v, "Achieved": achieved_pay_v, "Status": status_val_pay_v})
                summary_df_pay_page_admin_disp = pd.DataFrame(summary_list_pay_page_admin)
                if not summary_df_pay_page_admin_disp.empty:
                    st.markdown("<h6>Individual Collection Progress:</h6>", unsafe_allow_html=True)
                    num_cols_pay_disp = min(3, len(summary_df_pay_page_admin_disp)) if len(summary_df_pay_page_admin_disp) > 0 else 1
                    cols_pay_disp = st.columns(num_cols_pay_disp)
                    for idx_pay_disp, row_pay_disp in summary_df_pay_page_admin_disp.iterrows():
                        progress_pct_pay_disp = (row_pay_disp['Achieved'] / row_pay_disp['Target'] * 100) if row_pay_disp['Target'] > 0 else 0
                        donut_fig_pay_admin_disp = create_donut_chart(progress_pct_pay_disp, achieved_color='#2070c0')
                        with cols_pay_disp[idx_pay_disp % num_cols_pay_disp]:
                            st.markdown(f"<div class='employee-progress-item'><h6>{row_pay_disp['Employee']}</h6><p>Target: ₹{row_pay_disp['Target']:,.0f}<br>Collected: ₹{row_pay_disp['Achieved']:,.0f}</p></div>", unsafe_allow_html=True)
                            if donut_fig_pay_admin_disp: st.pyplot(donut_fig_pay_admin_disp, use_container_width=True)
                            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin-top: 10px; margin-bottom:25px;'>", unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Collection Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_pay_page_disp = create_team_progress_bar_chart(summary_df_pay_page_admin_disp, title="Team Collection Target vs. Achieved")
                    if team_bar_fig_pay_page_disp:
                        for bar_group_pay_d in team_bar_fig_pay_page_disp.axes[0].containers:
                            if bar_group_pay_d.get_label()=='Achieved':
                                for bar_d in bar_group_pay_d: bar_d.set_color('#2070c0')
                        st.pyplot(team_bar_fig_pay_page_disp, use_container_width=True)
                    else: st.info("No collection data to plot team bar chart.")
                else: st.info(f"No payment collection data found for {current_quarter_pay_display} to display team progress.")

        elif admin_action_pay == f"Set/Edit Collection Target for {TARGET_YEAR_PAY_TRACKER}":
            st.markdown(f"<h5>Set or Update Employee Collection Goal ({TARGET_YEAR_PAY_TRACKER} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options_pay_admin_set = [u for u,d in USERS.items() if d["role"] in ["employee", "sales_person"]]
            if not employee_options_pay_admin_set: st.warning("No employees/salespersons available.")
            else:
                selected_emp_pay_admin_set = st.radio("Select Employee:", employee_options_pay_admin_set, key="pay_emp_radio_admin_set_page", horizontal=True)
                quarter_options_pay_admin_set = [f"{TARGET_YEAR_PAY_TRACKER}-Q{i}" for i in range(1,5)]
                selected_period_pay_admin_set = st.radio("Goal Period:", quarter_options_pay_admin_set, key="pay_period_radio_admin_set_page", horizontal=True)
                existing_pay_admin_set = payment_goals_df[(payment_goals_df["Username"].astype(str)==str(selected_emp_pay_admin_set)) & (payment_goals_df["MonthYear"].astype(str)==str(selected_period_pay_admin_set))]
                g_desc_pay_set, g_target_pay_set, g_achieved_pay_set, g_status_pay_set = "", 0.0, 0.0, "Not Started"
                if not existing_pay_admin_set.empty:
                    g_data_pay_edit_set = existing_pay_admin_set.iloc[0]
                    g_desc_pay_set=g_data_pay_edit_set.get("GoalDescription","")
                    g_target_pay_set=float(pd.to_numeric(g_data_pay_edit_set.get("TargetAmount"),errors='coerce').fillna(0.0))
                    g_achieved_pay_set=float(pd.to_numeric(g_data_pay_edit_set.get("AchievedAmount"),errors='coerce').fillna(0.0))
                    g_status_pay_set=g_data_pay_edit_set.get("Status","Not Started")
                    st.info(f"Editing payment collection goal for {selected_emp_pay_admin_set} - {selected_period_pay_admin_set}")
                with st.form(key=f"set_pay_goal_form_{selected_emp_pay_admin_set}_{selected_period_pay_admin_set}_page"):
                    new_desc_pay_set=st.text_area("Collection Goal Description",value=g_desc_pay_set,key=f"desc_pay_admin_edit_page") # Changed to text_area
                    new_target_pay_set=st.number_input("Target Collection (INR)",value=g_target_pay_set,min_value=0.0,step=1000.0,format="%.2f",key=f"target_pay_admin_edit_page")
                    new_achieved_pay_set=st.number_input("Collected Amount (INR)",value=g_achieved_pay_set,min_value=0.0,step=100.0,format="%.2f",key=f"achieved_pay_admin_edit_page")
                    new_status_pay_set=st.selectbox("Status",status_options_pay,index=status_options_pay.index(g_status_pay_set),key=f"status_pay_admin_edit_page")
                    submitted_pay_admin_set=st.form_submit_button("Save Collection Goal", type="primary")
                if submitted_pay_admin_set:
                    if not new_desc_pay_set.strip(): st.warning("Description is required.")
                    elif new_target_pay_set <= 0 and new_status_pay_set not in ["Cancelled","On Hold","Not Started"]: st.warning("Target amount must be > 0 unless status is Cancelled, On Hold, or Not Started.")
                    else:
                        global payment_goals_df
                        editable_pay_goals_df_admin_set = payment_goals_df.copy()
                        existing_pay_indices_admin_set = editable_pay_goals_df_admin_set[(editable_pay_goals_df_admin_set["Username"].astype(str)==str(selected_emp_pay_admin_set))&(editable_pay_goals_df_admin_set["MonthYear"].astype(str)==str(selected_period_pay_admin_set))].index
                        update_data_pay_set = {"Username":selected_emp_pay_admin_set,"MonthYear":selected_period_pay_admin_set,"GoalDescription":new_desc_pay_set,"TargetAmount":new_target_pay_set,"AchievedAmount":new_achieved_pay_set,"Status":new_status_pay_set}
                        for col_name_pay_check_set in PAYMENT_GOALS_COLUMNS:
                            if col_name_pay_check_set not in update_data_pay_set: update_data_pay_set[col_name_pay_check_set]=pd.NA
                        if not existing_pay_indices_admin_set.empty:
                            editable_pay_goals_df_admin_set.loc[existing_pay_indices_admin_set[0]] = pd.Series(update_data_pay_set)
                            msg_verb_pay_set="updated"
                        else:
                            new_row_df_pay_admin_set = pd.DataFrame([update_data_pay_set], columns=PAYMENT_GOALS_COLUMNS)
                            editable_pay_goals_df_admin_set = pd.concat([editable_pay_goals_df_admin_set, new_row_df_pay_admin_set], ignore_index=True)
                            msg_verb_pay_set="set"
                        try:
                            editable_pay_goals_df_admin_set.to_csv(PAYMENT_GOALS_FILE,index=False)
                            payment_goals_df = editable_pay_goals_df_admin_set
                            st.session_state.user_message=f"Payment Collection Goal for {selected_emp_pay_admin_set} ({selected_period_pay_admin_set}) {msg_verb_pay_set}!"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e_pay_save_set: st.session_state.user_message=f"Error saving payment collection goal: {e_pay_save_set}"; st.session_state.message_type="error"; st.rerun()
    
    elif current_user_auth['role'] in ['sales_person', 'employee']:
        st.markdown(f"<h4>My Payment Collection Goals ({TARGET_YEAR_PAY_TRACKER} - Quarterly)</h4>", unsafe_allow_html=True)
        my_goals_pay_user_view = payment_goals_df[payment_goals_df["Username"].astype(str) == str(current_user_auth["username"])].copy()
        for col_pay_num_uv in ["TargetAmount", "AchievedAmount"]: my_goals_pay_user_view[col_pay_num_uv] = pd.to_numeric(my_goals_pay_user_view[col_pay_num_uv], errors="coerce").fillna(0.0)
        current_pay_user_df_view = my_goals_pay_user_view[my_goals_pay_user_view["MonthYear"] == current_quarter_pay_display]
        st.markdown(f"<h5>Current Goal Period: {current_quarter_pay_display}</h5>", unsafe_allow_html=True)
        if not current_pay_user_df_view.empty:
            g_pay_user_view = current_pay_user_df_view.iloc[0]; target_amt_pay_user_v = g_pay_user_view["TargetAmount"]; achieved_amt_pay_user_v = g_pay_user_view["AchievedAmount"]
            st.markdown(f"**Description:** {g_pay_user_view.get('GoalDescription', 'N/A')}")
            col_metrics_pay_user_v, col_chart_pay_user_v = st.columns([0.6, 0.4])
            with col_metrics_pay_user_v:
                sub_col1_pay_user_v,sub_col2_pay_user_v=st.columns(2)
                sub_col1_pay_user_v.metric("Target",f"₹{target_amt_pay_user_v:,.0f}")
                sub_col2_pay_user_v.metric("Collected",f"₹{achieved_amt_pay_user_v:,.0f}")
                st.metric("Status",g_pay_user_view.get("Status","In Progress"),label_visibility="visible")
            with col_chart_pay_user_v:
                progress_pct_pay_user_v=(achieved_amt_pay_user_v/target_amt_pay_user_v*100) if target_amt_pay_user_v > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:0px;'>Collection Progress</h6>",unsafe_allow_html=True)
                donut_fig_pay_user_v=create_donut_chart(progress_pct_pay_user_v,"Collection Progress",achieved_color='#2070c0')
                if donut_fig_pay_user_v: st.pyplot(donut_fig_pay_user_v,use_container_width=True)
            st.markdown("---")
            if current_user_auth['role'] == 'sales_person':
                with st.form(key=f"update_achievement_pay_{current_user_auth['username']}_{current_quarter_pay_display}_page"):
                    new_val_pay_user_v=st.number_input("Update My Collected Amount (INR):",value=achieved_amt_pay_user_v,min_value=0.0,step=100.0,format="%.2f")
                    submitted_ach_pay_user_v=st.form_submit_button("Update My Collection", type="primary")
                if submitted_ach_pay_user_v:
                    global payment_goals_df
                    editable_pay_goals_df_user_v = payment_goals_df.copy()
                    idx_pay_user_v = editable_pay_goals_df_user_v[(editable_pay_goals_df_user_v["Username"] == current_user_auth["username"]) &(editable_pay_goals_df_user_v["MonthYear"] == current_quarter_pay_display)].index
                    if not idx_pay_user_v.empty:
                        editable_pay_goals_df_user_v.loc[idx_pay_user_v[0],"AchievedAmount"]=new_val_pay_user_v
                        new_status_pay_user_v="Achieved" if new_val_pay_user_v >= target_amt_pay_user_v and target_amt_pay_user_v > 0 else "In Progress"
                        editable_pay_goals_df_user_v.loc[idx_pay_user_v[0],"Status"]=new_status_pay_user_v
                        try:
                            editable_pay_goals_df_user_v.to_csv(PAYMENT_GOALS_FILE,index=False)
                            payment_goals_df = editable_pay_goals_df_user_v
                            st.session_state.user_message = "Your payment collection updated!"; st.session_state.message_type = "success"; st.rerun()
                        except Exception as e_pay_user_save_v: st.session_state.user_message = f"Error updating collection: {e_pay_user_save_v}"; st.session_state.message_type = "error"; st.rerun()
                    else: st.session_state.user_message = "Could not find your current payment collection goal to update."; st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No payment collection goal set for you for {current_quarter_pay_display}. Please contact your administrator.")
        st.markdown(f"---"); st.markdown(f"<h5>My Past Collection Goals ({TARGET_YEAR_PAY_TRACKER})</h5>", unsafe_allow_html=True)
        past_goals_pay_user_v = my_goals_pay_user_view[(my_goals_pay_user_view["MonthYear"].astype(str).str.startswith(str(TARGET_YEAR_PAY_TRACKER))) & (my_goals_pay_user_view["MonthYear"].astype(str) != current_quarter_pay_display)]
        if not past_goals_pay_user_v.empty: render_goal_chart(past_goals_pay_user_v, "My Past Collection Performance")
        else: st.info(f"No past payment collection goal records for {TARGET_YEAR_PAY_TRACKER}.")
    st.markdown("</div>", unsafe_allow_html=True)

# --- End of Chunk 8 ---
# --- Chunk 9: Manage Records (Admin) / My Records (Employee/Sales) & Fallback ---

elif nav == "Manage Records" and current_user_auth['role'] == 'admin':
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>admin_panel_settings</span> Manage Records</h3>", unsafe_allow_html=True)

    admin_record_view_options = ["View Activity Logs", "View Submitted Orders"]
    admin_selected_record_view = st.radio(
        "Select Record Type to Manage:",
        options=admin_record_view_options,
        horizontal=True,
        key="admin_manage_record_type_radio"
    )
    st.divider()

    if admin_selected_record_view == "View Activity Logs":
        st.markdown("<h4>Employee Activity & Other Logs</h4>", unsafe_allow_html=True)
        employee_name_list_logs_admin_manage = [name for name, data in USERS.items() if data["role"] != "admin"]
        if not employee_name_list_logs_admin_manage: st.info("No employees/salespersons found.")
        else:
            selected_employee_log_admin_manage = st.selectbox("Select Employee:", [""] + employee_name_list_logs_admin_manage, key="log_employee_select_admin_manage_page", format_func=lambda x: "Select an Employee..." if x == "" else x)
            if selected_employee_log_admin_manage:
                st.markdown(f"<h4 class='employee-section-header'>Records for: {selected_employee_log_admin_manage}</h4>", unsafe_allow_html=True)
                tab_titles_admin_manage = ["Field Activity", "Attendance", "Allowances", "Sales Goals", "Payment Goals"]
                tabs_admin_manage = st.tabs([f"<span class='material-symbols-outlined' style='vertical-align:middle; margin-right:5px;'>folder_shared</span> {title}" for title in tab_titles_admin_manage])
                with tabs_admin_manage[0]:
                    emp_activity_log_admin_m = activity_log_df[activity_log_df["Username"] == selected_employee_log_admin_manage]
                    display_activity_logs_section(emp_activity_log_admin_m, selected_employee_log_admin_manage) # Reusing display function
                with tabs_admin_manage[1]:
                    emp_attendance_log_admin_m = attendance_df[attendance_df["Username"] == selected_employee_log_admin_manage]
                    display_general_attendance_logs_section(emp_attendance_log_admin_m, selected_employee_log_admin_manage) # Reusing
                with tabs_admin_manage[2]:
                    st.markdown(f"<h5>Allowances Claimed</h5>", unsafe_allow_html=True)
                    emp_allowance_log_admin_m = allowance_df[allowance_df["Username"] == selected_employee_log_admin_manage]
                    if not emp_allowance_log_admin_m.empty: st.dataframe(emp_allowance_log_admin_m.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
                    else: st.info("No allowance records found.")
                with tabs_admin_manage[3]:
                    st.markdown(f"<h5>Sales Goals</h5>", unsafe_allow_html=True)
                    emp_goals_log_admin_m = goals_df[goals_df["Username"] == selected_employee_log_admin_manage]
                    if not emp_goals_log_admin_m.empty: st.dataframe(emp_goals_log_admin_m.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
                    else: st.info("No sales goals records found.")
                with tabs_admin_manage[4]:
                    st.markdown(f"<h5>Payment Collection Goals</h5>", unsafe_allow_html=True)
                    emp_payment_goals_log_admin_m = payment_goals_df[payment_goals_df["Username"] == selected_employee_log_admin_manage]
                    if not emp_payment_goals_log_admin_m.empty: st.dataframe(emp_payment_goals_log_admin_m.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
                    else: st.info("No payment collection goals records found.")
            else: st.info("Please select an employee from the dropdown to view their records.")

    elif admin_selected_record_view == "View Submitted Orders":
        st.markdown("<h4>Submitted Sales Orders</h4>", unsafe_allow_html=True)
        if order_summary_df.empty:
            st.info("No orders have been submitted yet.")
        else:
            display_orders_summary_admin = order_summary_df.copy()
            display_orders_summary_admin['OrderDate_dt'] = pd.to_datetime(display_orders_summary_admin['OrderDate'], errors='coerce')
            display_orders_summary_admin = display_orders_summary_admin.sort_values(by="OrderDate_dt", ascending=False)
            
            st.markdown("<h6>Filter Orders:</h6>", unsafe_allow_html=True)
            filter_cols_admin_order = st.columns([1,1,2])
            salesperson_list_admin_order = ["All"] + sorted(display_orders_summary_admin['Salesperson'].unique().tolist())
            selected_salesperson_filter_admin = filter_cols_admin_order[0].selectbox("Salesperson", salesperson_list_admin_order, key="admin_order_filter_salesperson_manage")
            if selected_salesperson_filter_admin != "All":
                display_orders_summary_admin = display_orders_summary_admin[display_orders_summary_admin['Salesperson'] == selected_salesperson_filter_admin]

            store_name_filter_text_admin = filter_cols_admin_order[1].text_input("Store Name contains", key="admin_order_filter_storename_manage")
            if store_name_filter_text_admin.strip():
                display_orders_summary_admin = display_orders_summary_admin[display_orders_summary_admin['StoreName'].str.contains(store_name_filter_text_admin.strip(), case=False, na=False)]
            
            min_date_orders_admin = display_orders_summary_admin['OrderDate_dt'].min().date() if not display_orders_summary_admin.empty and pd.notna(display_orders_summary_admin['OrderDate_dt'].min()) else date.today() - timedelta(days=30)
            max_date_orders_admin = display_orders_summary_admin['OrderDate_dt'].max().date() if not display_orders_summary_admin.empty and pd.notna(display_orders_summary_admin['OrderDate_dt'].max()) else date.today()
            date_range_orders_admin = filter_cols_admin_order[2].date_input(
                "Order Date Range", value=(min_date_orders_admin, max_date_orders_admin),
                min_value=min_date_orders_admin, max_value=max_date_orders_admin, key="admin_order_filter_daterange_manage"
            )
            if len(date_range_orders_admin) == 2:
                start_date_filter_admin, end_date_filter_admin = date_range_orders_admin
                display_orders_summary_admin = display_orders_summary_admin[
                    (display_orders_summary_admin['OrderDate_dt'].dt.date >= start_date_filter_admin) &
                    (display_orders_summary_admin['OrderDate_dt'].dt.date <= end_date_filter_admin)
                ]
            
            st.markdown("---")
            if display_orders_summary_admin.empty: st.info("No orders match the current filter criteria.")
            else:
                st.markdown(f"<h6>Displaying {len(display_orders_summary_admin)} Order(s)</h6>", unsafe_allow_html=True)
                summary_cols_to_show_admin = ["OrderID", "OrderDate", "Salesperson", "StoreName", "GrandTotal", "Notes"]
                st.dataframe(
                    display_orders_summary_admin[summary_cols_to_show_admin].reset_index(drop=True), use_container_width=True, hide_index=True,
                    column_config={
                        "OrderDate": st.column_config.DatetimeColumn("Order Date", format="YYYY-MM-DD HH:mm"),
                        "GrandTotal": st.column_config.NumberColumn("Total (₹)", format="₹ %.2f")
                    }
                )
                st.markdown("---")
                st.markdown("<h6>View Order Details:</h6>", unsafe_allow_html=True)
                order_id_options_admin = [""] + display_orders_summary_admin["OrderID"].tolist()
                selected_order_id_admin_details = st.selectbox(
                    "Select OrderID to View Line Items", options=order_id_options_admin,
                    index=0 if not st.session_state.admin_order_view_selected_order_id else order_id_options_admin.index(st.session_state.admin_order_view_selected_order_id) if st.session_state.admin_order_view_selected_order_id in order_id_options_admin else 0,
                    format_func=lambda x: "Select an Order ID..." if x == "" else x, key="admin_order_details_select_manage"
                )
                st.session_state.admin_order_view_selected_order_id = selected_order_id_admin_details
                if selected_order_id_admin_details:
                    order_line_items_selected_admin = orders_df[orders_df['OrderID'] == selected_order_id_admin_details]
                    if order_line_items_selected_admin.empty: st.warning(f"No line items found for OrderID: {selected_order_id_admin_details}")
                    else:
                        st.markdown(f"<h6>Line Items for Order: {selected_order_id_admin_details}</h6>", unsafe_allow_html=True)
                        line_item_cols_to_show_admin = ["ProductName", "SKU", "Quantity", "UnitOfMeasure", "UnitPrice", "LineTotal"]
                        st.dataframe(
                            order_line_items_selected_admin[line_item_cols_to_show_admin].reset_index(drop=True), use_container_width=True, hide_index=True,
                            column_config={
                                "UnitPrice": st.column_config.NumberColumn("Price (₹)", format="₹ %.2f"),
                                "LineTotal": st.column_config.NumberColumn("Item Total (₹)", format="₹ %.2f")
                            }
                        )
    st.markdown("</div>", unsafe_allow_html=True)


elif nav == "My Records":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h3><span class='material-symbols-outlined'>article</span> My Records</h3>", unsafe_allow_html=True)
    my_username_log_rec = current_user_auth["username"]
    st.markdown(f"<h4 class='employee-section-header'>Activity & Records for: {my_username_log_rec}</h4>", unsafe_allow_html=True)
    
    tab_titles_user_rec = ["Field Activity", "Attendance", "Allowances", "Sales Goals", "Payment Goals"]
    tabs_user_rec = st.tabs([f"<span class='material-symbols-outlined' style='vertical-align:middle; margin-right:5px;'>badge</span> {title}" for title in tab_titles_user_rec])

    with tabs_user_rec[0]: # Field Activity
        my_activity_log_user_rec = activity_log_df[activity_log_df["Username"] == my_username_log_rec]
        display_activity_logs_section(my_activity_log_user_rec, "My") # Reusing display function
    with tabs_user_rec[1]: # Attendance
        my_attendance_log_user_rec = attendance_df[attendance_df["Username"] == my_username_log_rec]
        display_general_attendance_logs_section(my_attendance_log_user_rec, "My") # Reusing
    with tabs_user_rec[2]: # Allowances
        st.markdown(f"<h5>My Allowances Claimed</h5>", unsafe_allow_html=True)
        my_allowance_log_user_rec = allowance_df[allowance_df["Username"] == my_username_log_rec]
        if not my_allowance_log_user_rec.empty: st.dataframe(my_allowance_log_user_rec.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
        else: st.info("No allowance records found for you.")
    with tabs_user_rec[3]: # Sales Goals
        st.markdown(f"<h5>My Sales Goals</h5>", unsafe_allow_html=True)
        my_goals_log_user_rec = goals_df[goals_df["Username"] == my_username_log_rec]
        if not my_goals_log_user_rec.empty: st.dataframe(my_goals_log_user_rec.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
        else: st.info("No sales goals records found for you.")
    with tabs_user_rec[4]: # Payment Goals
        st.markdown(f"<h5>My Payment Collection Goals</h5>", unsafe_allow_html=True)
        my_payment_goals_log_user_rec = payment_goals_df[payment_goals_df["Username"] == my_username_log_rec]
        if not my_payment_goals_log_user_rec.empty: st.dataframe(my_payment_goals_log_user_rec.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True, hide_index=True)
        else: st.info("No payment collection goals records found for you.")
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.error(f"Page '{nav}' not found or you do not have permission to view it.", icon="🚨")
    st.markdown("</div>", unsafe_allow_html=True)

# --- End of Chunk 9 ---

