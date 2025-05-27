# Placeholder for the corrected Streamlit app.py code
# Add your full working application logic here...
# import streamlit as st # Commented out the initial one, as it's re-imported later.
# st.title("Attendance Log System - Placeholder") # Removed this initial title


import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
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

# --- Function to render Plotly Express grouped bar chart ---
def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty:
        st.warning("No data available to plot.")
        return
    df_chart = df.copy()
    df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear",
                              value_vars=["TargetAmount", "AchievedAmount"],
                              var_name="Metric",
                              value_name="Amount")
    if df_melted.empty:
        st.warning(f"No data to plot for {chart_title} after processing.")
        return
    # Using Google-themed colors for charts
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group",
                 labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"},
                 title=chart_title,
                 color_discrete_map={'TargetAmount': 'var(--md-sys-color-secondary-container)', 'AchievedAmount': 'var(--md-sys-color-primary)'}) # Updated colors
    fig.update_layout(
        height=400, 
        xaxis_title="Quarter", 
        yaxis_title="Amount (INR)", 
        legend_title_text='Metric',
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='var(--md-sys-color-on-surface)')
    )
    fig.update_xaxes(type='category', gridcolor='var(--md-sys-color-outline-variant)', zerolinecolor='var(--md-sys-color-outline-variant)')
    fig.update_yaxes(gridcolor='var(--md-sys-color-outline-variant)', zerolinecolor='var(--md-sys-color-outline-variant)')
    st.plotly_chart(fig, use_container_width=True)

# --- Function to create Matplotlib Donut Chart ---
def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='var(--md-sys-color-primary)', remaining_color='var(--md-sys-color-surface-variant)', center_text_color=None):
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=100) # Increased DPI slightly for clarity
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    progress_percentage = max(0.0, min(float(progress_percentage), 100.0))
    remaining_percentage = 100.0 - progress_percentage
    if progress_percentage <= 0.01: sizes = [100.0]; slice_colors = [remaining_color]; actual_progress_display = 0.0
    elif progress_percentage >= 99.99: sizes = [100.0]; slice_colors = [achieved_color]; actual_progress_display = 100.0
    else: sizes = [progress_percentage, remaining_percentage]; slice_colors = [achieved_color, remaining_color]; actual_progress_display = progress_percentage
    
    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, 
           wedgeprops=dict(width=0.35, edgecolor=f"var(--md-sys-color-surface)")) # Use surface color for edge
    centre_circle = plt.Circle((0,0),0.65,fc=f"var(--md-sys-color-surface)"); fig.gca().add_artist(centre_circle) # Match card bg
    
    text_color_to_use = center_text_color if center_text_color else (achieved_color if actual_progress_display > 0 else 'var(--md-sys-color-on-surface-variant)')
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=11, fontweight='500', color=text_color_to_use, fontfamily='Roboto')
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig

# --- Function to create Matplotlib Grouped Bar Chart for Team Progress ---
def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee", target_color='var(--md-sys-color-secondary-container)', achieved_color='var(--md-sys-color-primary)'):
    if summary_df.empty: return None
    labels = summary_df[user_col].tolist(); target_amounts = summary_df[target_col].fillna(0).tolist(); achieved_amounts = summary_df[achieved_col].fillna(0).tolist()
    x = np.arange(len(labels)); width = 0.35
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.75), 4.5), dpi=100) # Adjusted size
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)

    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color=target_color, alpha=1)
    rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color=achieved_color, alpha=1)
    
    ax.set_ylabel('Amount (INR)', fontsize=10, color='var(--md-sys-color-on-surface-variant)', fontfamily='Roboto'); 
    ax.set_title(title, fontsize=13, fontweight='500', pad=15, color='var(--md-sys-color-on-surface)', fontfamily='Roboto')
    ax.set_xticks(x); 
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9, color='var(--md-sys-color-on-surface-variant)', fontfamily='Roboto'); 
    ax.legend(fontsize=9, frameon=False, labelcolor='var(--md-sys-color-on-surface-variant)')
    
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('var(--md-sys-color-outline-variant)'); 
    ax.spines['left'].set_color('var(--md-sys-color-outline-variant)')
    ax.yaxis.grid(True, linestyle=':', alpha=0.7, color='var(--md-sys-color-outline-variant)')
    ax.tick_params(colors='var(--md-sys-color-on-surface-variant)')
    
    def autolabel(rects, color):
        for rect in rects:
            height = rect.get_height()
            if height > 0: 
                ax.annotate(f'{height:,.0f}', xy=(rect.get_x() + rect.get_width() / 2, height), 
                            xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', 
                            fontsize=7, color=color, fontfamily='Roboto', fontweight='500')
    autolabel(rects1, 'var(--md-sys-color-on-secondary-container)')
    autolabel(rects2, 'var(--md-sys-color-on-primary)') # Text on primary bars
    
    fig.tight_layout(pad=1.0)
    return fig

html_css = """
<style>
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    :root {
        --md-sys-color-primary: #0B57D0;
        --md-sys-color-on-primary: #FFFFFF;
        --md-sys-color-primary-container: #D3E3FD;
        --md-sys-color-on-primary-container: #001B3D;
        --md-sys-color-secondary: #565E71;
        --md-sys-color-on-secondary: #FFFFFF;
        --md-sys-color-secondary-container: #DAE2F9;
        --md-sys-color-on-secondary-container: #131C2B;
        --md-sys-color-tertiary: #725572;
        --md-sys-color-on-tertiary: #FFFFFF;
        --md-sys-color-tertiary-container: #FBD7FA;
        --md-sys-color-on-tertiary-container: #2A122C;
        --md-sys-color-surface: #FCFCFF; 
        --md-sys-color-surface-variant: #E1E2EC;
        --md-sys-color-on-surface: #1A1C1E;
        --md-sys-color-on-surface-variant: #44474E;
        --md-sys-color-background: #F7F9FC; /* Slightly bluish grey */
        --md-sys-color-on-background: #1A1C1E;
        --md-sys-color-outline: #74777F;
        --md-sys-color-outline-variant: #C4C6CF;
        --md-sys-color-error: #B3261E;
        --md-sys-color-success: #1E8E3E; /* Google Green for success */

        --md-sys-font-family-main: 'Roboto', 'Inter', sans-serif;
        --md-sys-typescale-headline-small-font-size: 24px;
        --md-sys-typescale-title-large-font-size: 20px; /* Adjusted for app */
        --md-sys-typescale-title-medium-font-size: 16px;
        --md-sys-typescale-label-large-font-size: 14px;
        --md-sys-typescale-body-medium-font-size: 14px;

        --md-sys-shape-corner-extra-small: 4px;
        --md-sys-shape-corner-small: 8px;
        --md-sys-shape-corner-medium: 12px;
        --md-sys-shape-corner-full: 999px;

        --md-sys-elevation-level-0: none;
        --md-sys-elevation-level-1: 0px 1px 3px 0px rgba(0, 0, 0, 0.1), 0px 1px 2px 0px rgba(0, 0, 0, 0.06); /* Softer shadow */
        --md-sys-elevation-level-2: 0px 2px 6px 2px rgba(0, 0, 0, 0.15), 0px 1px 2px 0px rgba(0, 0, 0, 0.3);
    }

    body, .main {
        font-family: var(--md-sys-font-family-main);
        background-color: var(--md-sys-color-background) !important;
        color: var(--md-sys-color-on-background);
        font-size: var(--md-sys-typescale-body-medium-font-size);
        line-height: 1.5;
    }
    .main .block-container { 
        max-width: 1280px; 
        padding: 20px 28px !important; 
    }

    h1, h2, h3, h4, h5, h6 { color: var(--md-sys-color-on-surface); font-weight: 500; }
    .main .block-container > div:first-child > div:first-child > div:first-child > h1 { /* Streamlit App Title */
        font-size: var(--md-sys-typescale-headline-small-font-size); font-weight: 400; padding-bottom: 16px;
        margin-bottom: 28px; border-bottom: 1px solid var(--md-sys-color-outline-variant); text-align: left;
    }

    .card {
        background-color: var(--md-sys-color-surface); padding: 20px 24px; 
        border-radius: var(--md-sys-shape-corner-medium);
        border: 1px solid var(--md-sys-color-outline-variant); margin-bottom: 20px;
        box-shadow: var(--md-sys-elevation-level-0); 
    }
    .card h3 { /* Titles inside cards */
        margin-top: 0; padding-bottom: 12px; margin-bottom: 18px;
        font-size: var(--md-sys-typescale-title-large-font-size); font-weight: 500;
        border-bottom: 1px solid var(--md-sys-color-outline-variant);
    }
     .card h4 { font-size: var(--md-sys-typescale-title-medium-font-size); font-weight: 500; margin-bottom: 10px; color: var(--md-sys-color-on-surface-variant);}
     .card h5 { font-size: 1.05em; color: var(--md-sys-color-on-surface-variant); margin-top: 18px; margin-bottom: 8px; font-weight: 500;}
     .card h6 { font-size: 0.9em; color: var(--md-sys-color-on-surface-variant); margin-top: 0px; margin-bottom: 10px; font-weight: 500;}


    [data-testid="stSidebar"] {
        background-color: var(--md-sys-color-surface) !important; padding: 0px !important; 
        border-right: 1px solid var(--md-sys-color-outline-variant) !important; width: 260px !important; 
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] .main-sidebar-content-wrapper { display: flex; flex-direction: column; height: 100%; padding: 0; }
    [data-testid="stSidebar"] .sidebar-content { padding: 12px 0px !important; overflow-y: auto; flex-grow: 1; }
    
    .welcome-text { /* Your custom class for welcome message */
        font-size: var(--md-sys-typescale-title-medium-font-size); font-weight: 500;
        padding: 16px 20px 12px 20px; color: var(--md-sys-color-on-surface) !important;
    }
    [data-testid="stSidebar"] [data-testid="stImage"] > img {
        border-radius: 50%; margin: 0px 0px 4px 20px; width: 32px !important; height: 32px !important;
        border: 1px solid var(--md-sys-color-outline-variant);
    }
    [data-testid="stSidebar"] p[style*="text-align:center"] { /* User position */
        font-size: 13px; color: var(--md-sys-color-on-surface-variant) !important;
        margin-left: 20px !important; margin-top: -2px !important; margin-bottom: 12px !important;
        text-align: left !important;
    }
    [data-testid="stSidebar"] hr { margin: 12px 20px !important; border-color: var(--md-sys-color-outline-variant) !important; }
    
    [data-testid="stSidebar"] div[data-testid="stRadio"] > label[data-baseweb="radio"] { /* Radio group label e.g. "Navigation" */
        font-size: 11px !important; font-weight: 500 !important; color: var(--md-sys-color-on-surface-variant) !important;
        padding: 12px 20px 6px 20px !important; text-transform: uppercase; letter-spacing: 0.8px;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label { /* Each radio item's label */
        display: flex !important; align-items: center !important;
        padding: 9px 20px 9px 17px !important; /* L padding adjusted for active border */
        border-radius: 0 var(--md-sys-shape-corner-full) var(--md-sys-shape-corner-full) 0 !important;
        margin: 1px 0px 1px 4px !important; /* Small left margin for alignment */
        font-size: var(--md-sys-typescale-label-large-font-size) !important; font-weight: 400 !important;
        color: var(--md-sys-color-on-surface) !important;
        border-left: 3px solid transparent !important;
        transition: background-color 0.1s ease-out, color 0.1s ease-out, border-left-color 0.1s ease-out;
        width: calc(100% - 4px); /* Adjust width */
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
        background-color: var(--md-sys-color-surface-variant) !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label > div[data-baseweb="radio"] { display: none !important; }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[aria-checked="true"] + label {
        background-color: var(--md-sys-color-primary-container) !important;
        color: var(--md-sys-color-on-primary-container) !important;
        font-weight: 500 !important;
        border-left: 3px solid var(--md-sys-color-primary) !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label > div > p { /* The text within the radio label */
        display: flex; align-items: center; /* Helps if emojis are used */
    }

    .logout-section { margin-top: auto; padding: 8px 0px 12px 0px; }
    .logout-section hr { margin: 0px 20px 8px 20px !important; }
    [data-testid="stSidebar"] .stButton button[id*="logout_button_sidebar"] {
        display: flex !important; align-items: center !important; justify-content: flex-start !important;
        padding: 9px 20px 9px 17px !important; border-radius: 0 var(--md-sys-shape-corner-full) var(--md-sys-shape-corner-full) 0 !important;
        margin: 1px 0px 1px 4px !important; width: calc(100% - 4px) !important; background-color: transparent !important;
        color: var(--md-sys-color-on-surface) !important;
        font-size: var(--md-sys-typescale-label-large-font-size) !important; font-weight: 400 !important;
        border: none !important; text-align: left; border-left: 3px solid transparent !important;
    }
    [data-testid="stSidebar"] .stButton button[id*="logout_button_sidebar"]:hover {
        background-color: color-mix(in srgb, var(--md-sys-color-error) 8%, transparent) !important;
        color: var(--md-sys-color-error) !important;
    }
    /* For an icon with logout, you'd use emoji in button label: st.button("🔒 Logout") */

    .stButton:not([data-testid="stSidebar"] .stButton) button {
        background-color: var(--md-sys-color-primary) !important; color: var(--md-sys-color-on-primary) !important;
        padding: 9px 20px !important; border-radius: var(--md-sys-shape-corner-full) !important;
        font-size: var(--md-sys-typescale-label-large-font-size) !important; font-weight: 500 !important;
        border: none !important; box-shadow: var(--md-sys-elevation-level-1) !important;
        transition: background-color 0.1s ease-out, box-shadow 0.1s ease-out; text-transform: none;
    }
    .stButton:not([data-testid="stSidebar"] .stButton) button:hover {
        background-color: color-mix(in srgb, var(--md-sys-color-primary) 90%, black) !important;
        box-shadow: var(--md-sys-elevation-level-2) !important;
    }
    .stButton button[id*="check_in_btn"], 
    .stButton button[id*="submit_allowance_btn"], 
    .stButton button[id*="form_submit_button"], /* Check your actual form submit button keys */
    .stButton button[id*="save_goal"], /* If you have a save goal button */
    .stButton button[id*="update_achievement"] /* If you have update achievement button */
     { 
        background-color: var(--md-sys-color-primary) !important; /* Or var(--md-sys-color-success) if defined */
    }
    .stButton button[id*="check_out_btn"] { /* Example of a secondary-style button */
        background-color: transparent !important; color: var(--md-sys-color-primary) !important;
        border: 1px solid var(--md-sys-color-outline) !important; box-shadow: none !important;
    }
    .stButton button[id*="check_out_btn"]:hover {
        background-color: color-mix(in srgb, var(--md-sys-color-primary) 8%, transparent) !important;
    }

    .stTextInput > div > div > input, .stNumberInput > div > div > input, 
    .stDateInput > div > div > input, .stTimeInput > div > div > input,
    .stTextArea > div > div > textarea, 
    .stSelectbox > div > div[data-baseweb="select"] > div:first-child {
        border-radius: var(--md-sys-shape-corner-extra-small) !important;
        border: 1px solid var(--md-sys-color-outline) !important;
        background-color: var(--md-sys-color-surface) !important;
        color: var(--md-sys-color-on-surface) !important;
        padding: 12px 12px !important; /* Adjusted padding for better look */
        font-size: var(--md-sys-typescale-body-medium-font-size) !important;
        line-height: 1.5 !important;
        transition: border-color 0.1s ease-out, box-shadow 0.1s ease-out;
    }
    .stTextArea > div > div > textarea { padding: 12px !important; min-height: 90px; }
    .stTextInput > div > div > input:focus, .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus, .stTimeInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div[data-baseweb="select"][aria-expanded="true"] > div:first-child,
    .stSelectbox > div > div[data-baseweb="select"] > div:first-child:focus-within {
        border-color: var(--md-sys-color-primary) !important;
        box-shadow: 0 0 0 1px var(--md-sys-color-primary) !important;
    }
    .stTextInput input::placeholder, .stNumberInput input::placeholder, .stTextArea textarea::placeholder {
        color: var(--md-sys-color-on-surface-variant) !important; opacity: 0.6;
    }
    div[data-testid="stForm"] { border: none; padding: 0; } /* Remove default form border */

    /* DataFrames */
    .stDataFrame { border: 1px solid var(--md-sys-color-outline-variant); border-radius: var(--md-sys-shape-corner-small); box-shadow: none; overflow: hidden;}
    .stDataFrame table thead th { 
        background-color: var(--md-sys-color-surface-variant); 
        color: var(--md-sys-color-on-surface-variant); font-weight: 500; 
        border-bottom: 1px solid var(--md-sys-color-outline-variant); 
        font-size: var(--md-sys-typescale-label-large-font-size); text-transform:none; padding: 10px 14px;
        text-align: left;
    }
    .stDataFrame table tbody td { 
        color: var(--md-sys-color-on-surface); font-size: var(--md-sys-typescale-body-medium-font-size); 
        border-bottom: 1px solid var(--md-sys-color-outline-variant); padding: 10px 14px;
        vertical-align: middle;
    }
    .stDataFrame table tbody tr:last-child td { border-bottom: none; }
    .stDataFrame table tbody tr:hover { background-color: color-mix(in srgb, var(--md-sys-color-primary) 5%, transparent); }

    /* Metrics */
    div[data-testid="stMetric"] { padding: 8px 0px; /* More compact */ }
    div[data-testid="stMetricLabel"] {
        font-size: var(--md-sys-typescale-label-medium-font-size) !important; 
        color: var(--md-sys-color-on-surface-variant) !important; 
        font-weight: 400; text-transform: none; margin-bottom: 0px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 22px !important; /* Slightly smaller metric value */
        font-weight: 500; color: var(--md-sys-color-on-surface); line-height: 28px;
    }
    
    .employee-progress-item { 
        border: 1px solid var(--md-sys-color-outline-variant); background-color: var(--md-sys-color-surface); 
        border-radius: var(--md-sys-shape-corner-small); padding:12px; text-align:center;
    }
    .employee-progress-item h6 {margin-top:0; margin-bottom:4px; font-size:var(--md-sys-typescale-label-large-font-size); color: var(--md-sys-color-on-surface); font-weight: 500;}
    .employee-progress-item p {font-size:12px; color: var(--md-sys-color-on-surface-variant); margin-bottom:6px;}
    
    .record-type-header { 
        font-size: var(--md-sys-typescale-title-medium-font-size); color: var(--md-sys-color-on-surface); 
        margin-top: 20px; margin-bottom: 10px; font-weight: 500; 
        padding-bottom: 6px; border-bottom: 1px solid var(--md-sys-color-outline-variant); 
    }
    hr { border-color: var(--md-sys-color-outline-variant); margin: 20px 0; }

    .login-page-container { display: flex; justify-content: center; align-items: center; min-height: 90vh; padding: 20px; }
    .login-container.card { max-width: 400px; width: 100%; padding: 28px; }
    .login-container h3 { text-align:center; margin-bottom:20px; font-size: var(--md-sys-typescale-title-large-font-size); }
    
    /* Custom Notifications if you use them (st.success, st.error etc. have their own styling) */
    .custom-notification { padding: 12px 16px; border-radius: var(--md-sys-shape-corner-small); margin-bottom: 16px; font-size: var(--md-sys-typescale-body-medium-font-size); border-left-width: 4px; border-left-style: solid; display: flex; align-items: center; }
    .custom-notification.success { background-color: #E6F4EA; color: #135423; border-left-color: var(--md-sys-color-success); }
    .custom-notification.error { background-color: #FDECEA; color: #8C1D18; border-left-color: var(--md-sys-color-error); }
    .custom-notification.info { background-color: #E8F0FE; color: #001B3D; border-left-color: var(--md-sys-color-primary); }
</style>
"""
# The rest of your Python code (USERS, file paths, functions, Streamlit layout, etc.)
# should be EXACTLY as you provided in the previous message.
# I am pasting it here for completeness.

st.markdown(html_css, unsafe_allow_html=True)

# --- Credentials & User Info ---
USERS = {
    "Geetali": {"password": "Geetali123", "role": "employee", "position": "Software Engineer", "profile_photo": "images/geetali.png"},
    "Nilesh": {"password": "Nilesh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "Vishal": {"password": "Vishal123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/vishal.png"},
    "Santosh": {"password": "Santosh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/santosh.png"},
    "Deepak": {"password": "Deepak123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/deepak.png"},
    "Rahul": {"password": "Rahul123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/rahul.png"},
    "admin": {"password": "admin123", "role": "admin", "position": "System Administrator", "profile_photo": "images/admin.png"}
}

# --- Create dummy images folder and placeholder images ---
if not os.path.exists("images"):
    try: os.makedirs("images")
    except OSError: pass
if PILLOW_INSTALLED:
    for user_key, user_data in USERS.items():
        img_path = user_data.get("profile_photo")
        if img_path and not os.path.exists(img_path):
            try:
                img = Image.new('RGB', (120, 120), color = (200, 220, 240)); draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", 40)
                except IOError: font = ImageFont.load_default()
                text = user_key[:2].upper()
                if hasattr(draw, 'textbbox'): # More modern PIL
                    bbox = draw.textbbox((0,0), text, font=font); text_width, text_height = bbox[2]-bbox[0], bbox[3]-bbox[1]
                    text_x, text_y = (120-text_width)/2, (120-text_height)/2 - bbox[1] # Adjust y based on bbox[1]
                elif hasattr(draw, 'textsize'): # Older PIL
                    text_width, text_height = draw.textsize(text, font=font); text_x, text_y = (120-text_width)/2, (120-text_height)/2
                else: # Fallback if textsize and textbbox not available
                    text_x, text_y = 30,30
                draw.text((text_x, text_y), text, fill=(28,78,128), font=font); img.save(img_path)
            except Exception: pass # Ignore if placeholder creation fails

# --- File Paths & Timezone & Directories ---
ATTENDANCE_FILE = "attendance.csv"; ALLOWANCE_FILE = "allowances.csv"; GOALS_FILE = "goals.csv"; PAYMENT_GOALS_FILE = "payment_goals.csv"
ACTIVITY_LOG_FILE = "activity_log.csv"
ACTIVITY_PHOTOS_DIR = "activity_photos"
ATTENDANCE_PHOTOS_DIR = "attendance_photos" # Used if attendance page still captures its own photos

if not os.path.exists(ACTIVITY_PHOTOS_DIR):
    try: os.makedirs(ACTIVITY_PHOTOS_DIR)
    except OSError: pass
if not os.path.exists(ATTENDANCE_PHOTOS_DIR) and ATTENDANCE_PHOTOS_DIR != ACTIVITY_PHOTOS_DIR :
    try: os.makedirs(ATTENDANCE_PHOTOS_DIR)
    except OSError: pass

TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError: st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'."); st.stop()
def get_current_time_in_tz(): return datetime.now(timezone.utc).astimezone(tz)
def get_quarter_str_for_year(year, for_current_display=False): # Parameter for_current_display not used, can be removed
    now_month = get_current_time_in_tz().month
    if 1 <= now_month <= 3: return f"{year}-Q1"
    elif 4 <= now_month <= 6: return f"{year}-Q2"
    elif 7 <= now_month <= 9: return f"{year}-Q3"
    else: return f"{year}-Q4"

# --- Load or create data ---
def load_data(path, columns):
    if os.path.exists(path):
        try:
            if os.path.getsize(path) > 0:
                df = pd.read_csv(path)
                # Ensure all expected columns exist, add if missing
                for col in columns:
                    if col not in df.columns: df[col] = pd.NA # Use pd.NA for missing values
                # Convert specific columns to numeric, coercing errors
                num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude"]
                for nc in num_cols:
                    if nc in df.columns: df[nc] = pd.to_numeric(df[nc], errors='coerce')
                return df
            else: return pd.DataFrame(columns=columns) # File exists but is empty
        except pd.errors.EmptyDataError: return pd.DataFrame(columns=columns) # Explicitly handle EmptyDataError
        except Exception as e: st.error(f"Error loading {path}: {e}."); return pd.DataFrame(columns=columns)
    else:
        # File does not exist, create it with headers
        df = pd.DataFrame(columns=columns);
        try: df.to_csv(path, index=False)
        except Exception as e: st.warning(f"Could not create {path}: {e}") # Warn if creation fails
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"] # NO ImageFile for general attendance
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]

# --- Load DataFrames globally ---
attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
activity_log_df = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS)


# --- Session State & Login ---
if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}

if not st.session_state.auth["logged_in"]:
    # Centering the login form on the page
    st.markdown('<div class="login-page-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-container card">', unsafe_allow_html=True)
    st.markdown("<h3>🔐 Login</h3>", unsafe_allow_html=True) # Using the .card h3 style
    
    # Message display within the login card
    if st.session_state.user_message:
        if st.session_state.message_type == "error":
            st.error(st.session_state.user_message) # Use st.error for login errors
        else: # For success/info on logout
            st.info(st.session_state.user_message)
        st.session_state.user_message = None
        st.session_state.message_type = None

    uname = st.text_input("Username", key="login_uname")
    pwd = st.text_input("Password", type="password", key="login_pwd")
    if st.button("Login", key="login_button_main", use_container_width=True): # use_container_width for full-width button
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = "Login successful!" # This will be picked up by global message display
            st.session_state.message_type = "success"
            st.rerun()
        else: 
            st.session_state.user_message = "Invalid username or password." # Set for display on next run
            st.session_state.message_type = "error"
            st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True); st.stop()

# --- Main Application ---
current_user = st.session_state.auth

# --- Global Message Display for Main Application ---
if "user_message" in st.session_state and st.session_state.user_message:
    msg_type = st.session_state.get("message_type", "info")
    # Using Streamlit's native alert components which are now better styled by default or can be targeted
    if msg_type == "success":
        st.success(st.session_state.user_message, icon="✅")
    elif msg_type == "error":
        st.error(st.session_state.user_message, icon="❌")
    elif msg_type == "warning":
        st.warning(st.session_state.user_message, icon="⚠️")
    else: # info
        st.info(st.session_state.user_message, icon="ℹ️")
    st.session_state.user_message = None
    st.session_state.message_type = None


with st.sidebar:
    st.markdown('<div class="main-sidebar-content-wrapper">', unsafe_allow_html=True) # For flex layout
    # User Info Section
    st.markdown('<div class="sidebar-header-section">', unsafe_allow_html=True)
    st.markdown(f"<div class='welcome-text-sidebar'>👋 Welcome, {current_user['username']}!</div>", unsafe_allow_html=True)
    user_sidebar_info = USERS.get(current_user["username"], {})
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]):
        st.image(user_sidebar_info["profile_photo"]) # CSS will style it
    st.markdown(f"<p class='user-position-sidebar'>{user_sidebar_info.get('position', 'N/A')}</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)

    # Navigation
    # IMPORTANT: For icons with st.radio, use EMOJIS in the labels.
    # The CSS is designed to style the radio items like Google nav.
    nav_options_display = [
        "🗓️ Attendance", # Using emojis
        "📸 Upload Activity Photo",
        "🧾 Allowance",
        "🎯 Goal Tracker",
        "💰 Payment Collection Tracker",
        "📊 View Logs"
    ]
    # Mapping display options back to your original logic keys if they differ
    nav_logic_map = {
        "🗓️ Attendance": "📆 Attendance",
        "📸 Upload Activity Photo": "📸 Upload Activity Photo",
        "🧾 Allowance": "🧾 Allowance",
        "🎯 Goal Tracker": "🎯 Goal Tracker",
        "💰 Payment Collection Tracker": "💰 Payment Collection Tracker",
        "📊 View Logs": "📊 View Logs"
    }

    # Initialize nav_selection if it's not in session_state or is None
    if 'nav_selection_display' not in st.session_state or st.session_state.nav_selection_display is None:
        st.session_state.nav_selection_display = nav_options_display[0]

    # Get current index for st.radio
    try:
        current_nav_index = nav_options_display.index(st.session_state.nav_selection_display)
    except ValueError:
        current_nav_index = 0 # Default to first item if not found
        st.session_state.nav_selection_display = nav_options_display[0]


    selected_nav_display = st.radio(
        "MENU", # This label can be styled or hidden with CSS `label_visibility="collapsed"`
        nav_options_display, 
        key="sidebar_nav_main_radio", # Unique key
        index=current_nav_index,
        label_visibility="collapsed" # Hides the "MENU" label above radio but keeps it for accessibility
    )
    st.session_state.nav_selection_display = selected_nav_display # Store the selected display option
    nav = nav_logic_map[selected_nav_display] # Get the logic key

    # Logout section
    st.markdown("<div class='logout-section-sidebar'>", unsafe_allow_html=True)
    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True)
    if st.button("Logout", key="logout_button_sidebar", use_container_width=True): # Key for CSS targeting
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."
        st.session_state.message_type = "info"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True) # Close logout-section
    st.markdown("</div>", unsafe_allow_html=True) # Close main-sidebar-content-wrapper


#------------------------------------------------------------------------closed navbar

# --- Main Content ---
# The H3 titles within cards will use the .card h3 style from CSS
if nav == "📆 Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled for attendance. Photos for specific activities can be uploaded from the 'Upload Activity Photo' section.", icon="ℹ️")
    st.markdown("<hr>", unsafe_allow_html=True) # Use hr for thematic break, styled by CSS
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2); common_data = {"Username": current_user["username"], "Latitude": pd.NA, "Longitude": pd.NA}

    def process_general_attendance(attendance_type):
        global attendance_df 
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_data = {"Type": attendance_type, "Timestamp": now_str_display, **common_data}
        for col_name in ATTENDANCE_COLUMNS: 
            if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
        new_entry = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
        
        # Modify global df and save
        attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        try:
            attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."; st.session_state.message_type = "success"; st.rerun()
        except Exception as e: st.session_state.user_message = f"Error saving attendance: {e}"; st.session_state.message_type = "error"; st.rerun()

    with col1:
        if st.button("Check In", key="check_in_btn_main_page", use_container_width=True): # Key for CSS
            process_general_attendance("Check-In")
    with col2:
        if st.button("Check Out", key="check_out_btn_main_page", use_container_width=True): # Key for CSS
            process_general_attendance("Check-Out")
    st.markdown('</div></div>', unsafe_allow_html=True)

elif nav == "📸 Upload Activity Photo":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat = pd.NA; current_lon = pd.NA 
    with st.form(key="activity_photo_form_page"): # Unique key for the form
        st.markdown("<h6 class='form-field-label-custom'>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description of activity/visit:", key="activity_desc_page_unique") # Unique key
        img_file_buffer_activity = st.camera_input("Take a picture of your activity/visit", key="activity_camera_input_page_unique") # Unique key
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo and Log Activity", key="form_submit_button_upload_activity") # Key for CSS
    if submit_activity_photo:
        if img_file_buffer_activity is None: st.warning("Please take a picture before submitting.")
        elif not activity_description.strip(): st.warning("Please provide a description for the activity.")
        else:
            now_for_filename = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S")
            now_for_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            image_filename_activity = f"{current_user['username']}_activity_{now_for_filename}.jpg"
            image_path_activity = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_activity)
            try:
                with open(image_path_activity, "wb") as f: f.write(img_file_buffer_activity.getbuffer())
                new_activity_data = {"Username": current_user["username"], "Timestamp": now_for_display, "Description": activity_description, "ImageFile": image_filename_activity, "Latitude": current_lat, "Longitude": current_lon}
                for col_name in ACTIVITY_LOG_COLUMNS:
                    if col_name not in new_activity_data: new_activity_data[col_name] = pd.NA
                new_activity_entry = pd.DataFrame([new_activity_data], columns=ACTIVITY_LOG_COLUMNS)
                
                # Modify global df and save
                activity_log_df = pd.concat([activity_log_df, new_activity_entry], ignore_index=True)
                activity_log_df.to_csv(ACTIVITY_LOG_FILE, index=False)
                
                st.session_state.user_message = "Activity photo and log uploaded!"; st.session_state.message_type = "success"; st.rerun()
            except Exception as e: st.session_state.user_message = f"Error saving activity: {e}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "🧾 Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    # Using st.form for better layout and single submission
    with st.form(key="allowance_claim_form_page"): # Unique key
        st.markdown("<h6 class='form-field-label-custom'>Select Allowance Type:</h6>", unsafe_allow_html=True) # Custom class
        a_type = st.radio("", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allowance_type_radio_page_unique", horizontal=True, label_visibility='collapsed') # Unique key
        amount = st.number_input("Enter Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_page_unique") # Unique key
        reason = st.text_area("Reason for Allowance:", key="allowance_reason_page_unique", placeholder="Please provide a clear justification...") # Unique key
        submitted_allowance = st.form_submit_button("Submit Allowance Request", use_container_width=True, key="submit_allowance_btn_page") # Unique key for CSS

        if submitted_allowance:
            if a_type and amount > 0 and reason.strip():
                date_str = get_current_time_in_tz().strftime("%Y-%m-%d"); new_entry_data = {"Username": current_user["username"], "Type": a_type, "Amount": amount, "Reason": reason, "Date": date_str}
                new_entry = pd.DataFrame([new_entry_data], columns=ALLOWANCE_COLUMNS)
                
                # Modify global df and save
                allowance_df = pd.concat([allowance_df, new_entry], ignore_index=True)
                try:
                    allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                    st.session_state.user_message = f"Allowance for ₹{amount:.2f} submitted."; st.session_state.message_type = "success"; st.rerun()
                except Exception as e: st.session_state.user_message = f"Error submitting allowance: {e}"; st.session_state.message_type = "error"; st.rerun()
            else: st.warning("Please complete all fields with valid values.")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "🎯 Goal Tracker": # Assuming this is the Sales Goal Tracker
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_GOAL_YEAR = 2025; current_quarter_for_display = get_quarter_str_for_year(TARGET_GOAL_YEAR)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    # Use Google Green for sales achievements
    achieved_color_sales = 'var(--md-sys-color-success)' 
    target_color_sales = 'var(--md-sys-color-secondary-container)'


    if current_user["role"] == "admin":
        st.markdown("<h4 class='section-title'>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True) # Custom class
        admin_action = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR}"], key="admin_goal_action_radio_page_unique", horizontal=True) # Unique key
        if admin_action == "View Team Progress":
            st.markdown(f"<h5>Team Goal Progress for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            employee_users = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users: st.info("No employees found.")
            else:
                summary_list_sales = []
                for emp_name in employee_users:
                    emp_current_goal = goals_df[(goals_df["Username"].astype(str) == str(emp_name)) & (goals_df["MonthYear"].astype(str) == str(current_quarter_for_display))]
                    target, achieved, status_val = 0.0, 0.0, "Not Set"
                    if not emp_current_goal.empty:
                        g_data = emp_current_goal.iloc[0]; target = float(pd.to_numeric(g_data.get("TargetAmount"), errors='coerce') or 0.0)
                        achieved = float(pd.to_numeric(g_data.get("AchievedAmount", 0.0), errors='coerce') or 0.0); status_val = g_data.get("Status", "N/A")
                    summary_list_sales.append({"Employee": emp_name, "Target": target, "Achieved": achieved, "Status": status_val})
                summary_df_sales = pd.DataFrame(summary_list_sales)
                if not summary_df_sales.empty:
                    st.markdown("<h6>Individual Sales Progress:</h6>", unsafe_allow_html=True)
                    num_cols_sales = min(3, len(employee_users)) # Adjust columns based on number of users
                    cols_sales = st.columns(num_cols_sales)
                    col_idx_sales = 0
                    for index, row in summary_df_sales.iterrows():
                        progress_percent = (row['Achieved'] / row['Target'] * 100) if row['Target'] > 0 else 0
                        donut_fig = create_donut_chart(progress_percent, achieved_color=achieved_color_sales)
                        with cols_sales[col_idx_sales % num_cols_sales]:
                            st.markdown(f"<div class='employee-progress-item'><h6>{row['Employee']}</h6><p>Target: ₹{row['Target']:,.0f}<br>Achieved: ₹{row['Achieved']:,.0f}</p></div>", unsafe_allow_html=True)
                            st.pyplot(donut_fig, use_container_width=True); st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                        col_idx_sales += 1
                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Sales Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_sales = create_team_progress_bar_chart(summary_df_sales, title="Team Sales Target vs. Achieved", achieved_color=achieved_color_sales, target_color=target_color_sales)
                    if team_bar_fig_sales: st.pyplot(team_bar_fig_sales, use_container_width=True)
                    else: st.info("No sales data to plot for the team bar chart.")
                else: st.info(f"No sales goals data found for {current_quarter_for_display} to display team progress.")
        elif admin_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR}": # Admin Set/Edit Sales Goal
            st.markdown(f"<h5>Set or Update Employee Goal ({TARGET_GOAL_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options = [u for u,d in USERS.items() if d["role"]=="employee"];
            if not employee_options: st.warning("No employees available.");
            else:
                selected_emp = st.radio("Select Employee:", employee_options, key="goal_emp_radio_admin_set_page_unique", horizontal=True) # Unique key
                quarter_options = [f"{TARGET_GOAL_YEAR}-Q{i}" for i in range(1,5)]; selected_period = st.radio("Goal Period:", quarter_options, key="goal_period_radio_admin_set_page_unique", horizontal=True) # Unique key
                
                existing_g = goals_df[(goals_df["Username"].astype(str)==str(selected_emp)) & (goals_df["MonthYear"].astype(str)==str(selected_period))]
                g_desc,g_target,g_achieved,g_status = "",0.0,0.0,"Not Started"
                if not existing_g.empty:
                    g_data=existing_g.iloc[0]; g_desc=g_data.get("GoalDescription",""); g_target=float(pd.to_numeric(g_data.get("TargetAmount",0.0),errors='coerce') or 0.0)
                    g_achieved=float(pd.to_numeric(g_data.get("AchievedAmount",0.0),errors='coerce') or 0.0); g_status=g_data.get("Status","Not Started"); st.info(f"Editing goal for {selected_emp} - {selected_period}")
                
                with st.form(key=f"set_sales_goal_form_admin_page_unique"): # Unique key
                    new_desc=st.text_area("Goal Description",value=g_desc,key=f"desc_admin_sales_page_unique") # Unique key
                    new_target=st.number_input("Target Sales (INR)",value=g_target,min_value=0.0,step=1000.0,format="%.2f",key=f"target_admin_sales_page_unique") # Unique key
                    new_achieved=st.number_input("Achieved Sales (INR)",value=g_achieved,min_value=0.0,step=100.0,format="%.2f",key=f"achieved_admin_sales_page_unique") # Unique key
                    new_status=st.radio("Status:",status_options,index=status_options.index(g_status),horizontal=True,key=f"status_admin_sales_page_unique") # Unique key
                    submitted=st.form_submit_button("Save Goal", key="save_goal_admin_sales") # Unique key for CSS

                    if submitted:
                        if not new_desc.strip(): st.warning("Description is required.")
                        elif new_target <= 0 and new_status not in ["Cancelled","On Hold","Not Started"]: st.warning("Target > 0 required.")
                        else:
                            # Ensure global goals_df is modified
                            global goals_df
                            existing_g_indices=goals_df[(goals_df["Username"].astype(str)==str(selected_emp))&(goals_df["MonthYear"].astype(str)==str(selected_period))].index
                            if not existing_g_indices.empty: 
                                goals_df.loc[existing_g_indices[0]]=[selected_emp,selected_period,new_desc,new_target,new_achieved,new_status]; msg_verb="updated"
                            else:
                                new_row_data={"Username":selected_emp,"MonthYear":selected_period,"GoalDescription":new_desc,"TargetAmount":new_target,"AchievedAmount":new_achieved,"Status":new_status}
                                new_row_df=pd.DataFrame([new_row_data],columns=GOALS_COLUMNS); goals_df=pd.concat([goals_df,new_row_df],ignore_index=True); msg_verb="set"
                            try:
                                goals_df.to_csv(GOALS_FILE,index=False)
                                st.session_state.user_message=f"Sales goal for {selected_emp} ({selected_period}) {msg_verb}!"; st.session_state.message_type="success"; st.rerun()
                            except Exception as e: st.session_state.user_message=f"Error saving sales goal: {e}"; st.session_state.message_type="error"; st.rerun()
    else: # Employee View - Sales Goal
        st.markdown("<h4 class='section-title'>My Sales Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        my_goals = goals_df[goals_df["Username"].astype(str) == str(current_user["username"])].copy()
        my_goals[["TargetAmount", "AchievedAmount"]] = my_goals[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric,errors="coerce").fillna(0.0)
        current_g_df = my_goals[my_goals["MonthYear"] == current_quarter_for_display]
        st.markdown(f"<h5>Current Goal Period: {current_quarter_for_display}</h5>", unsafe_allow_html=True)
        if not current_g_df.empty:
            g = current_g_df.iloc[0]; target_amt = g["TargetAmount"]; achieved_amt = g["AchievedAmount"]
            st.markdown(f"**Description:** {g.get('GoalDescription', 'N/A')}")
            col_metrics_sales, col_chart_sales = st.columns([0.6, 0.4]) # Adjusted column ratio
            with col_metrics_sales:
                sub_col1,sub_col2=st.columns(2); sub_col1.metric("Target",f"₹{target_amt:,.0f}"); sub_col2.metric("Achieved",f"₹{achieved_amt:,.0f}")
                st.metric("Status",g.get("Status","In Progress"))
            with col_chart_sales:
                progress_percent_sales=(achieved_amt/target_amt*100) if target_amt > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:0px;'>Sales Progress</h6>",unsafe_allow_html=True) # Adjusted margin
                st.pyplot(create_donut_chart(progress_percent_sales, achieved_color=achieved_color_sales),use_container_width=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            with st.form(key=f"update_sales_achievement_form_employee_page_unique"): # Unique key
                new_val=st.number_input("Update Achieved Amount (INR):",value=achieved_amt,min_value=0.0,step=100.0,format="%.2f", key="employee_sales_ach_update_page_unique") # Unique key
                submitted_ach=st.form_submit_button("Update Achievement", key="update_achievement_sales_employee") # Key for CSS
                if submitted_ach:
                    # Ensure global goals_df is modified
                    global goals_df
                    idx = goals_df[(goals_df["Username"] == current_user["username"]) &(goals_df["MonthYear"] == current_quarter_for_display)].index
                    if not idx.empty:
                        goals_df.loc[idx[0],"AchievedAmount"]=new_val
                        new_status="Achieved" if new_val >= target_amt and target_amt > 0 else "In Progress"
                        goals_df.loc[idx[0],"Status"]=new_status
                        try:
                            goals_df.to_csv(GOALS_FILE,index=False)
                            st.session_state.user_message = "Achievement updated!"; st.session_state.message_type = "success"; st.rerun()
                        except Exception as e: st.session_state.user_message = f"Error updating achievement: {e}"; st.session_state.message_type = "error"; st.rerun()
                    else: st.session_state.user_message = "Could not find your current goal to update."; st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No goal set for {current_quarter_for_display}. Contact admin.")
        st.markdown("<hr>", unsafe_allow_html=True); st.markdown("<h5>My Past Sales Goals (2025)</h5>", unsafe_allow_html=True)
        past_goals = my_goals[(my_goals["MonthYear"].str.startswith(str(TARGET_GOAL_YEAR))) & (my_goals["MonthYear"].astype(str) != current_quarter_for_display)]
        if not past_goals.empty: render_goal_chart(past_goals, "Past Sales Goal Performance", achieved_color=achieved_color_sales, target_color=target_color_sales)
        else: st.info(f"No past goal records for {TARGET_GOAL_YEAR}.")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "💰 Payment Collection Tracker": # Restoring full Payment Collection Tracker functionality
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_YEAR_PAYMENT = 2025; current_quarter_display_payment = get_quarter_str_for_year(TARGET_YEAR_PAYMENT)
    status_options_payment = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    # Use Google Blue for payment achievements
    achieved_color_payment = 'var(--md-sys-color-primary)'
    target_color_payment = 'var(--md-sys-color-secondary-container)'


    if current_user["role"] == "admin":
        st.markdown("<h4 class='section-title'>Admin: Set & Track Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action_payment = st.radio("Action:", ["View Team Progress", f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}"], key="admin_payment_action_radio_page_unique", horizontal=True) # Unique key
        if admin_action_payment == "View Team Progress":
            st.markdown(f"<h5>Team Payment Collection Progress for {current_quarter_display_payment}</h5>", unsafe_allow_html=True)
            employees_payment_list = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employees_payment_list: st.info("No employees found.")
            else:
                summary_list_payment = []
                for emp_pay_name in employees_payment_list:
                    record_payment = payment_goals_df[(payment_goals_df["Username"]==emp_pay_name)&(payment_goals_df["MonthYear"]==current_quarter_display_payment)]
                    target_p,achieved_p,status_p=0.0,0.0,"Not Set"
                    if not record_payment.empty:
                        rec_payment=record_payment.iloc[0]; target_p=float(pd.to_numeric(rec_payment["TargetAmount"],errors='coerce') or 0.0)
                        achieved_p=float(pd.to_numeric(rec_payment["AchievedAmount"],errors='coerce') or 0.0); status_p=rec_payment.get("Status","N/A")
                    summary_list_payment.append({"Employee":emp_pay_name,"Target":target_p,"Achieved":achieved_p,"Status":status_p})
                summary_df_payment = pd.DataFrame(summary_list_payment)
                if not summary_df_payment.empty:
                    st.markdown("<h6>Individual Collection Progress:</h6>", unsafe_allow_html=True)
                    num_cols_payment = min(3, len(employees_payment_list))
                    cols_payment=st.columns(num_cols_payment); col_idx_payment=0
                    for index,row in summary_df_payment.iterrows():
                        progress_percent_p=(row['Achieved']/row['Target']*100) if row['Target'] > 0 else 0
                        donut_fig_p=create_donut_chart(progress_percent_p,achieved_color=achieved_color_payment)
                        with cols_payment[col_idx_payment%num_cols_payment]:
                            st.markdown(f"<div class='employee-progress-item'><h6>{row['Employee']}</h6><p>Target: ₹{row['Target']:,.0f}<br>Collected: ₹{row['Achieved']:,.0f}</p></div>",unsafe_allow_html=True)
                            st.pyplot(donut_fig_p,use_container_width=True); st.markdown("<div style='margin-bottom:15px;'></div>",unsafe_allow_html=True)
                        col_idx_payment+=1
                    st.markdown("<hr>",unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Collection Performance:</h6>",unsafe_allow_html=True)
                    team_bar_fig_payment = create_team_progress_bar_chart(summary_df_payment,title="Team Collection Target vs. Achieved", achieved_color=achieved_color_payment, target_color=target_color_payment)
                    if team_bar_fig_payment: st.pyplot(team_bar_fig_payment,use_container_width=True)
                    else: st.info("No collection data to plot for team bar chart.")
                else: st.info(f"No payment collection data for {current_quarter_display_payment}.")
        elif admin_action_payment == f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}": # Admin Set/Edit Payment Goal
            st.markdown(f"<h5>Set or Update Collection Goal ({TARGET_YEAR_PAYMENT} - Quarterly)</h5>", unsafe_allow_html=True)
            employees_for_payment_goal = [u for u,d in USERS.items() if d["role"]=="employee"];
            if not employees_for_payment_goal: st.warning("No employees available.")
            else:
                selected_emp_payment=st.radio("Select Employee:",employees_for_payment_goal,key="payment_emp_radio_admin_set_page_unique",horizontal=True) # Unique key
                quarters_payment=[f"{TARGET_YEAR_PAYMENT}-Q{i}" for i in range(1,5)]; selected_period_payment=st.radio("Quarter:",quarters_payment,key="payment_period_radio_admin_set_page_unique",horizontal=True) # Unique key
                
                existing_payment_goal=payment_goals_df[(payment_goals_df["Username"]==selected_emp_payment)&(payment_goals_df["MonthYear"]==selected_period_payment)]
                desc_payment,tgt_payment_val,ach_payment_val,stat_payment = "",0.0,0.0,"Not Started"
                if not existing_payment_goal.empty:
                    g_payment=existing_payment_goal.iloc[0]; desc_payment=g_payment.get("GoalDescription",""); tgt_payment_val=float(pd.to_numeric(g_payment.get("TargetAmount",0.0),errors='coerce') or 0.0)
                    ach_payment_val=float(pd.to_numeric(g_payment.get("AchievedAmount",0.0),errors='coerce') or 0.0); stat_payment=g_payment.get("Status","Not Started")
                    st.info(f"Editing payment goal for {selected_emp_payment} - {selected_period_payment}")
                
                with st.form(f"form_payment_admin_page_unique"): # Unique key
                    new_desc_payment=st.text_input("Collection Goal Description",value=desc_payment,key=f"desc_admin_payment_page_unique") # Unique key
                    new_tgt_payment=st.number_input("Target Collection (INR)",value=tgt_payment_val,min_value=0.0,step=1000.0,key=f"target_admin_payment_page_unique") # Unique key
                    new_ach_payment=st.number_input("Collected Amount (INR)",value=ach_payment_val,min_value=0.0,step=500.0,key=f"achieved_admin_payment_page_unique") # Unique key
                    new_status_payment=st.selectbox("Status",status_options_payment,index=status_options_payment.index(stat_payment),key=f"status_admin_payment_page_unique") # Unique key
                    submitted_payment=st.form_submit_button("Save Goal", key="save_goal_admin_payment") # Key for CSS

                    if submitted_payment:
                        if not new_desc_payment.strip(): st.warning("Description required.")
                        elif new_tgt_payment <= 0 and new_status_payment not in ["Cancelled","Not Started", "On Hold"]: st.warning("Target > 0 required unless status is Cancelled, Not Started or On Hold.")
                        else:
                            # Ensure global payment_goals_df is modified
                            global payment_goals_df
                            existing_pg_indices=payment_goals_df[(payment_goals_df["Username"]==selected_emp_payment)&(payment_goals_df["MonthYear"]==selected_period_payment)].index
                            if not existing_pg_indices.empty: 
                                payment_goals_df.loc[existing_pg_indices[0]]=[selected_emp_payment,selected_period_payment,new_desc_payment,new_tgt_payment,new_ach_payment,new_status_payment]; msg_payment="updated"
                            else:
                                new_row_data_p={"Username":selected_emp_payment,"MonthYear":selected_period_payment,"GoalDescription":new_desc_payment,"TargetAmount":new_tgt_payment,"AchievedAmount":new_ach_payment,"Status":new_status_payment}
                                new_row_df_p=pd.DataFrame([new_row_data_p],columns=PAYMENT_GOALS_COLUMNS); payment_goals_df=pd.concat([payment_goals_df,new_row_df_p],ignore_index=True); msg_payment="set"
                            try:
                                payment_goals_df.to_csv(PAYMENT_GOALS_FILE,index=False)
                                st.session_state.user_message=f"Payment goal {msg_payment} for {selected_emp_payment} ({selected_period_payment})"; st.session_state.message_type="success"; st.rerun()
                            except Exception as e: st.session_state.user_message=f"Error saving payment goal: {e}"; st.session_state.message_type="error"; st.rerun()
    else: # Employee View - Payment Goal
        st.markdown("<h4 class='section-title'>My Payment Collection Goals (2025)</h4>", unsafe_allow_html=True)
        user_goals_payment = payment_goals_df[payment_goals_df["Username"]==current_user["username"]].copy()
        user_goals_payment[["TargetAmount","AchievedAmount"]] = user_goals_payment[["TargetAmount","AchievedAmount"]].apply(pd.to_numeric,errors="coerce").fillna(0.0)
        current_payment_goal_period_df = user_goals_payment[user_goals_payment["MonthYear"]==current_quarter_display_payment]
        st.markdown(f"<h5>Current Quarter: {current_quarter_display_payment}</h5>", unsafe_allow_html=True)
        if not current_payment_goal_period_df.empty:
            g_pay=current_payment_goal_period_df.iloc[0]; tgt_pay=g_pay["TargetAmount"]; ach_pay=g_pay["AchievedAmount"]
            st.markdown(f"**Goal:** {g_pay.get('GoalDescription','')}")
            col_metrics_pay,col_chart_pay=st.columns([0.6, 0.4]) # Adjusted ratio
            with col_metrics_pay:
                sub_col1_pay,sub_col2_pay=st.columns(2); sub_col1_pay.metric("Target",f"₹{tgt_pay:,.0f}"); sub_col2_pay.metric("Collected",f"₹{ach_pay:,.0f}")
                st.metric("Status",g_pay.get("Status","In Progress"))
            with col_chart_pay:
                progress_percent_pay=(ach_pay/tgt_pay*100) if tgt_pay > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:0px;'>Collection Progress</h6>",unsafe_allow_html=True) # Adjusted margin
                st.pyplot(create_donut_chart(progress_percent_pay, achieved_color=achieved_color_payment),use_container_width=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            with st.form(key=f"update_payment_collection_form_employee_page_unique"): # Unique key
                new_ach_val_payment=st.number_input("Update Collected Amount (INR):",value=ach_pay,min_value=0.0,step=500.0, key="employee_payment_ach_update_page_unique") # Unique key
                submit_collection_update=st.form_submit_button("Update Collection", key="update_achievement_payment_employee") # Key for CSS
                if submit_collection_update:
                     # Ensure global payment_goals_df is modified
                    global payment_goals_df
                    idx_pay=payment_goals_df[(payment_goals_df["Username"]==current_user["username"])&(payment_goals_df["MonthYear"]==current_quarter_display_payment)].index
                    if not idx_pay.empty:
                        payment_goals_df.loc[idx_pay[0],"AchievedAmount"]=new_ach_val_payment
                        payment_goals_df.loc[idx_pay[0],"Status"]="Achieved" if new_ach_val_payment >= tgt_pay and tgt_pay > 0 else "In Progress"
                        try:
                            payment_goals_df.to_csv(PAYMENT_GOALS_FILE,index=False)
                            st.session_state.user_message = "Collection updated."; st.session_state.message_type = "success"; st.rerun()
                        except Exception as e: st.session_state.user_message = f"Error: {e}"; st.session_state.message_type = "error"; st.rerun()
                    else: st.session_state.user_message = "Could not find your current payment goal to update."; st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No collection goal for {current_quarter_display_payment}.")
        st.markdown("<hr>", unsafe_allow_html=True); st.markdown("<h5>Past Quarters</h5>", unsafe_allow_html=True)
        past_payment_goals = user_goals_payment[(user_goals_payment["MonthYear"].str.startswith(str(TARGET_YEAR_PAYMENT))) & (user_goals_payment["MonthYear"]!=current_quarter_display_payment)]
        if not past_payment_goals.empty: render_goal_chart(past_payment_goals,"Past Collection Performance", achieved_color=achieved_color_payment, target_color=target_color_payment)
        else: st.info("No past collection goals.")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "📊 View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>📊 View Logs</h3>", unsafe_allow_html=True)
    def display_activity_logs_with_photos(df_logs, user_name_for_header):
        if df_logs.empty: st.info(f"No activity logs for {user_name_for_header}."); return
        # Removed redundant user_name_for_header H5, as it's part of section title
        for index, row in df_logs.sort_values(by="Timestamp", ascending=False).iterrows():
            st.markdown("<hr style='margin: 12px 0;'>", unsafe_allow_html=True); 
            col_details, col_photo = st.columns([0.75, 0.25]) # Adjusted ratio
            with col_details:
                st.markdown(f"""
                    <div style="font-size: 13px;">
                        <b>Timestamp:</b> {row['Timestamp']}<br>
                        <b>Description:</b> {row.get('Description', 'N/A')}<br>
                        <b>Location:</b> {'Not Recorded' if pd.isna(row.get('Latitude')) else f"Lat: {row.get('Latitude'):.4f}, Lon: {row.get('Longitude'):.4f}"}
                    </div>
                """, unsafe_allow_html=True)
                if pd.notna(row['ImageFile']) and row['ImageFile'] != "": st.caption(f"Photo ID: {row['ImageFile']}")
                else: st.caption("No photo for this activity.")
            with col_photo:
                if pd.notna(row['ImageFile']) and row['ImageFile'] != "":
                    image_path_to_display = os.path.join(ACTIVITY_PHOTOS_DIR, str(row['ImageFile']))
                    if os.path.exists(image_path_to_display):
                        try: st.image(image_path_to_display, width=100, use_column_width='never') # Fixed width
                        except Exception as img_e: st.warning(f"Img err: {img_e}")
                    else: st.caption(f"Img missing")
    
    def display_generic_logs_custom(df_logs, record_type_name): # Removed user_name header from here
        if df_logs.empty: st.info(f"No {record_type_name.lower()} records found."); return
        st.dataframe(df_logs.reset_index(drop=True), use_container_width=True)


    if current_user["role"] == "admin":
        st.markdown("<h4 class='section-title'>Admin: View Employee Records</h4>", unsafe_allow_html=True)
        employee_name_list = [uname for uname in USERS.keys() if USERS[uname]["role"] == "employee"]
        selected_employee_log = st.selectbox("Select Employee:", employee_name_list, key="log_employee_select_admin_page_unique", index=0 if employee_name_list else None) # Unique key

        if selected_employee_log:
            st.markdown(f"<h5 style='margin-top:20px; font-weight:500;'>Records for: {selected_employee_log}</h5>", unsafe_allow_html=True)
            
            st.markdown("<h6 class='record-type-header'>Field Activity Logs</h6>", unsafe_allow_html=True)
            emp_activity_log = activity_log_df[activity_log_df["Username"] == selected_employee_log]
            display_activity_logs_with_photos(emp_activity_log, selected_employee_log)
            
            st.markdown("<h6 class='record-type-header'>General Attendance</h6>", unsafe_allow_html=True)
            emp_attendance_log = attendance_df[attendance_df["Username"] == selected_employee_log]
            if not emp_attendance_log.empty:
                display_cols_att = ["Type", "Timestamp"]
                if 'Latitude' in emp_attendance_log.columns and 'Longitude' in emp_attendance_log.columns:
                    emp_attendance_log['Location'] = emp_attendance_log.apply(lambda r: f"Lat:{r.get('Latitude'):.2f},Lon:{r.get('Longitude'):.2f}" if pd.notna(r.get('Latitude')) and pd.notna(r.get('Longitude')) else "N/R", axis=1)
                    display_cols_att.append("Location")
                st.dataframe(emp_attendance_log[display_cols_att].sort_values("Timestamp", ascending=False).reset_index(drop=True), use_container_width=True)
            else: st.info(f"No attendance records for {selected_employee_log}.")

            st.markdown("<h6 class='record-type-header'>Allowances</h6>", unsafe_allow_html=True)
            display_generic_logs_custom(allowance_df[allowance_df["Username"] == selected_employee_log].sort_values("Date", ascending=False), "Allowance")
            
            st.markdown("<h6 class='record-type-header'>Sales Goals</h6>", unsafe_allow_html=True)
            display_generic_logs_custom(goals_df[goals_df["Username"] == selected_employee_log].sort_values("MonthYear", ascending=False), "Sales Goal")

            st.markdown("<h6 class='record-type-header'>Payment Collection Goals</h6>", unsafe_allow_html=True)
            display_generic_logs_custom(payment_goals_df[payment_goals_df["Username"] == selected_employee_log].sort_values("MonthYear", ascending=False), "Payment Goal")
        elif employee_name_list :
             st.info("Please select an employee to view their logs.")
        else:
            st.info("No employee records to display.")
    else: # Employee view
        st.markdown(f"<h4 class='section-title'>My Records: {current_user['username']}</h4>", unsafe_allow_html=True)
        st.markdown("<h6 class='record-type-header'>My Field Activity Logs</h6>", unsafe_allow_html=True)
        display_activity_logs_with_photos(activity_log_df[activity_log_df["Username"] == current_user["username"]], current_user["username"])
        
        st.markdown("<h6 class='record-type-header'>My General Attendance</h6>", unsafe_allow_html=True)
        my_attendance_log = attendance_df[attendance_df["Username"] == current_user["username"]]
        if not my_attendance_log.empty:
            display_cols_my_att = ["Type", "Timestamp"]
            if 'Latitude' in my_attendance_log.columns and 'Longitude' in my_attendance_log.columns:
                my_attendance_log['Location'] = my_attendance_log.apply(lambda r: f"Lat:{r.get('Latitude'):.2f},Lon:{r.get('Longitude'):.2f}" if pd.notna(r.get('Latitude')) and pd.notna(r.get('Longitude')) else "N/R", axis=1)
                display_cols_my_att.append("Location")
            st.dataframe(my_attendance_log[display_cols_my_att].sort_values("Timestamp", ascending=False).reset_index(drop=True), use_container_width=True)
        else: st.info("No attendance records found for you.")
        
        st.markdown("<h6 class='record-type-header'>My Allowances</h6>", unsafe_allow_html=True)
        display_generic_logs_custom(allowance_df[allowance_df["Username"] == current_user["username"]].sort_values("Date", ascending=False), "Allowance")

        st.markdown("<h6 class='record-type-header'>My Sales Goals</h6>", unsafe_allow_html=True)
        display_generic_logs_custom(goals_df[goals_df["Username"] == current_user["username"]].sort_values("MonthYear", ascending=False), "Sales Goal")

        st.markdown("<h6 class='record-type-header'>My Payment Collection Goals</h6>", unsafe_allow_html=True)
        display_generic_logs_custom(payment_goals_df[payment_goals_df["Username"] == current_user["username"]].sort_values("MonthYear", ascending=False), "Payment Goal")
    st.markdown('</div>', unsafe_allow_html=True)
