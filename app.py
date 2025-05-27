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

# --- Charting Functions (Modified for new color scheme based on CSS variables) ---
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
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group",
                 labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"},
                 title=chart_title,
                 color_discrete_map={'TargetAmount': 'hsl(209,61%,50%)', 'AchievedAmount': 'hsl(145,63%,49%)'}) # Approx CSS vars
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric',
                      plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                      font=dict(color="#343a40")) # Approx --text-color
    fig.update_xaxes(type='category', gridcolor='rgba(222,226,230,0.5)', zerolinecolor='rgba(222,226,230,0.5)')
    fig.update_yaxes(gridcolor='rgba(222,226,230,0.5)', zerolinecolor='rgba(222,226,230,0.5)')
    st.plotly_chart(fig, use_container_width=True)

def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#2ecc71', remaining_color='#f0f0f0', center_text_color=None):
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=100) 
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    progress_percentage = max(0.0, min(float(progress_percentage), 100.0))
    remaining_percentage = 100.0 - progress_percentage
    if progress_percentage <= 0.01: sizes = [100.0]; slice_colors = [remaining_color]; actual_progress_display = 0.0
    elif progress_percentage >= 99.99: sizes = [100.0]; slice_colors = [achieved_color]; actual_progress_display = 100.0
    else: sizes = [progress_percentage, remaining_percentage]; slice_colors = [achieved_color, remaining_color]; actual_progress_display = progress_percentage
    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.35, edgecolor="#ffffff")) 
    centre_circle = plt.Circle((0,0),0.65,fc="#ffffff"); fig.gca().add_artist(centre_circle) 
    text_color_to_use = center_text_color if center_text_color else (achieved_color if actual_progress_display > 0 else '#4A4A4A')
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=11, fontweight='bold', color=text_color_to_use, fontfamily='Inter')
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    return fig

def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee", target_color='#3498db', achieved_color='#2ecc71'):
    if summary_df.empty: return None
    labels = summary_df[user_col].tolist(); target_amounts = summary_df[target_col].fillna(0).tolist(); achieved_amounts = summary_df[achieved_col].fillna(0).tolist()
    x = np.arange(len(labels)); width = 0.35
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.75), 4.5), dpi=100) 
    fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color=target_color, alpha=0.8)
    rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color=achieved_color, alpha=0.8)
    ax.set_ylabel('Amount (INR)', fontsize=10, color="#6c757d", fontfamily='Inter'); 
    ax.set_title(title, fontsize=13, fontweight='600', pad=15, color="#1c4e80", fontfamily='Inter')
    ax.set_xticks(x); 
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9, color="#6c757d", fontfamily='Inter'); 
    ax.legend(fontsize=9, frameon=False, labelcolor="#6c757d")
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color("#dee2e6"); 
    ax.spines['left'].set_color("#dee2e6")
    ax.yaxis.grid(True, linestyle='--', alpha=0.7, color="#dee2e6")
    ax.tick_params(colors="#6c757d")
    def autolabel(rects, color_text): 
        for rect in rects:
            height = rect.get_height()
            if height > 0: 
                ax.annotate(f'{height:,.0f}', xy=(rect.get_x() + rect.get_width() / 2, height), 
                            xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', 
                            fontsize=7, color=color_text, fontfamily='Inter', fontweight='500') 
    autolabel(rects1, '#333')
    autolabel(rects2, '#333') 
    fig.tight_layout(pad=1.0)
    return fig

html_css = """
<style>
    @import url('https://fonts.googleapis.com/icon?family=Material+Icons');
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'); /* Using Inter as primary */

    :root {
        /* Google Material 3 Inspired Palette - Primary Tones */
        --g-primary: #0B57D0; /* Google Blue */
        --g-on-primary: #FFFFFF;
        --g-primary-container: #D3E3FD;
        --g-on-primary-container: #001B3D;

        /* Surface & Background Tones */
        --g-surface: #FCFCFF; /* Or #FDFBFF or #FEFBFF based on M3 tonal palettes */
        --g-surface-variant: #E1E2EC; /* For elements like outlines, dividers, muted backgrounds */
        --g-on-surface: #1A1C1E; /* Main text color on surfaces */
        --g-on-surface-variant: #44474E; /* Secondary text, icons */
        --g-background: #F7F9FC; /* Overall page background, slightly off-white */
        --g-on-background: #1A1C1E;

        /* Outline & Accent Tones */
        --g-outline: #74777F;
        --g-outline-variant: #C4C6CF;
        --g-error: #B3261E;
        --g-success: #1E8E3E; /* Google's recommended green */
        --g-warning: #F9AB00; /* Google's recommended yellow/orange */

        /* Typography */
        --g-font-family: 'Inter', 'Roboto', sans-serif;
        --g-font-size-headline-s: 24px;
        --g-font-size-title-l: 20px;
        --g-font-size-title-m: 16px;
        --g-font-size-label-l: 14px;
        --g-font-size-body-m: 14px;
        --g-font-size-body-s: 12px;

        /* Shape & Elevation */
        --g-shape-corner-xs: 4px;
        --g-shape-corner-s: 8px;
        --g-shape-corner-m: 12px;
        --g-shape-corner-full: 999px;
        --g-elevation-1: 0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
        --g-elevation-2: 0px 1px 2px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15);

        /* Custom app specific, can inherit from above or be distinct */
        --app-primary-color: var(--g-primary); /* Your primary branding color */
        --app-secondary-color: var(--g-secondary, #565E71); /* A secondary color */
        --app-accent-color: var(--g-primary-container); /* For accents like active nav bg */
        --app-text-color: var(--g-on-surface);
        --app-text-muted-color: var(--g-on-surface-variant);
        --app-body-bg-color: var(--g-background);
        --app-card-bg-color: var(--g-surface);
        --app-border-color: var(--g-outline-variant);
        --app-input-border-color: var(--g-outline);
    }

    body, .main {
        font-family: var(--g-font-family);
        background-color: var(--app-body-bg-color) !important;
        color: var(--app-text-color);
        font-size: var(--g-font-size-body-m);
        line-height: 1.6;
    }
    .main .block-container { 
        max-width: 1200px; 
        padding: 24px 32px !important; 
    }

    /* Headers (h1-h6 used by st.markdown or st.title etc.) */
    h1, h2, h3, h4, h5, h6 { color: var(--app-text-color); font-weight: 500; }
    
    /* Card Styling (matches your Python's use of <div class="card">) */
    .card {
        background-color: var(--app-card-bg-color); padding: 24px; 
        border-radius: var(--g-shape-corner-m);
        border: 1px solid var(--app-border-color); margin-bottom: 24px;
        box-shadow: var(--g-elevation-1); /* Subtle shadow for cards */
    }
    .card h3 { /* Your Python page titles inside cards */
        margin-top: 0 !important; padding-bottom: 16px !important; margin-bottom: 20px !important;
        font-size: var(--g-font-size-title-l) !important; font-weight: 500 !important;
        border-bottom: 1px solid var(--app-border-color) !important;
        color: var(--app-primary-color) !important; 
    }
     .card h4 { /* Section titles like "Admin: Manage..." */
        font-size: var(--g-font-size-title-m) !important; font-weight: 500 !important; 
        margin-top: 24px !important; margin-bottom: 12px !important; 
        color: var(--app-secondary-color) !important; /* Use app's secondary color */
     }
     .card h5 { /* Sub-section titles */
        font-size: 1.05em !important; color: var(--app-text-color) !important; margin-top: 20px !important; 
        margin-bottom: 10px !important; font-weight: 500 !important;
     }
     .card h6 { /* Smallest headers, e.g., "Individual Sales Progress" */
        font-size: 0.95em !important; color: var(--app-text-muted-color) !important; margin-top: 18px !important; 
        margin-bottom: 10px !important; font-weight: 500 !important; text-transform: uppercase; letter-spacing: 0.3px;
     }
    /* Form field labels (if you use st.markdown("<h6 class='form-field-label-custom'>...</h6>") */
    .form-field-label h6, h6.form-field-label-custom { /* Targeting your existing class */
        font-size: var(--g-font-size-label-l) !important; font-weight: 500 !important;
        color: var(--app-text-muted-color) !important; margin-top: 16px !important;
        margin-bottom: 6px !important; text-transform: none !important; letter-spacing: 0.1px !important;
    }


    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: var(--app-card-bg-color) !important; /* Use card bg for sidebar */
        padding: 0px !important; 
        border-right: 1px solid var(--app-border-color) !important; width: 260px !important; 
        box-shadow: var(--g-elevation-1) !important; /* Add a subtle shadow to sidebar */
    }
    [data-testid="stSidebar"] > div:first-child { 
        display: flex; flex-direction: column; height: 100vh; 
    }
    [data-testid="stSidebar"] .sidebar-content { 
        padding: 8px 0px !important; /* Reduced top/bottom padding for content */
        overflow-y: auto; flex-grow: 1;
    }
    
    /* Sidebar Header */
    .welcome-text { /* Your python uses this for "Welcome, User!" */
        font-size: var(--g-font-size-title-m) !important; font-weight: 500 !important;
        padding: 20px 20px 8px 20px !important; 
        color: var(--app-text-color) !important;
        text-align: left !important; border-bottom: none !important; /* Remove bottom border */
    }
    [data-testid="stSidebar"] [data-testid="stImage"] > img { 
        border-radius: 50%; margin: 0px 0px 4px 20px; width: 40px !important; height: 40px !important;
        border: 2px solid var(--app-accent-color) !important; /* Use app accent */
    }
    [data-testid="stSidebar"] p[style*="text-align:center"] { /* User position */
        font-size: var(--g-font-size-body-s) !important; color: var(--app-text-muted-color) !important;
        margin-left: 20px !important; margin-top: -2px !important; margin-bottom: 16px !important;
        text-align: left !important;
    }
    [data-testid="stSidebar"] hr { 
        margin: 16px 20px !important; border-color: var(--app-border-color) !important; 
    }
    
    /* Sidebar Navigation (st.radio) */
    [data-testid="stSidebar"] div[data-testid="stRadio"] > label[data-baseweb="radio"] { /* Radio group label "Navigation" */
        font-size: 11px !important; font-weight: 500 !important; color: var(--app-text-muted-color) !important;
        padding: 16px 20px 8px 20px !important; text-transform: uppercase; letter-spacing: 0.8px;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label { 
        display: flex !important; align-items: center !important;
        padding: 10px 20px 10px 17px !important; 
        border-radius: 0 var(--g-shape-corner-full) var(--g-shape-corner-full) 0 !important;
        margin: 2px 0px 2px 8px !important; /* Indent nav items slightly */
        font-size: var(--g-font-size-label-l) !important; font-weight: 400 !important;
        color: var(--app-text-color) !important;
        border-left: 3px solid transparent !important;
        transition: background-color 0.15s ease-out, color 0.15s ease-out, border-left-color 0.15s ease-out;
        width: calc(100% - 8px); 
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label:hover {
        background-color: var(--g-surface-variant) !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label > div[data-baseweb="radio"] { display: none !important; }
    [data-testid="stSidebar"] div[data-testid="stRadio"] div[aria-checked="true"] + label {
        background-color: var(--app-accent-color) !important;
        color: var(--g-on-primary-container) !important; /* Ensure good contrast on accent */
        font-weight: 500 !important;
        border-left: 3px solid var(--app-primary-color) !important;
    }
    [data-testid="stSidebar"] div[data-testid="stRadio"] label > div > p { 
        display: flex; align-items: center; color: inherit !important; font-size: inherit !important;
    }

    /* Sidebar Logout Button */
    .logout-section-wrapper { margin-top: auto; padding-bottom: 16px; } 
    .logout-section-wrapper hr { margin: 8px 20px !important; }
    [data-testid="stSidebar"] .stButton button[id*="logout_button_sidebar"] {
        background-color: var(--g-error) !important; 
        border: 1px solid var(--g-error) !important; 
        color: var(--g-on-error) !important; 
        font-weight: 500 !important;
        border-radius: var(--g-shape-corner-full) !important;
        padding: 8px 16px !important;
        margin: 0 16px !important; 
        width: calc(100% - 32px) !important;
        text-align: center !important; /* Centered logout text */
    }
    [data-testid="stSidebar"] .stButton button[id*="logout_button_sidebar"]:hover {
        background-color: color-mix(in srgb, var(--g-error) 85%, black) !important; 
        border-color: color-mix(in srgb, var(--g-error) 85%, black) !important;
    }
    
    /* Main Content Buttons - Using your original color scheme for these as requested */
    .stButton:not([data-testid="stSidebar"] .stButton) button {
        background-color: var(--success-color) !important; 
        color: white !important; padding: 10px 24px !important; border: none !important; 
        border-radius: 0.375rem !important;
        font-size: 1.05em !important; font-weight: 500 !important; 
        transition: background-color 0.2s ease, transform 0.15s ease, box-shadow 0.2s ease; 
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075) !important; 
        cursor: pointer;
    }
    .stButton:not([data-testid="stSidebar"] .stButton) button:hover {
        background-color: #218838 !important; 
        transform: translateY(-2px); 
        box-shadow: 0 0.25rem 0.5rem rgba(0,0,0,0.1) !important;
    }
     /* Specific button overrides from your original CSS */
    .stButton button[key*="check_out_btn_main_no_photo"] { /* Your key for check out */
        background-color: var(--danger-color) !important; /* Example: if check out was danger */
    }
    .stButton button[key*="check_out_btn_main_no_photo"]:hover {
        background-color: #c82333 !important;
    }
    /* Add other specific button overrides if you had them */


    /* Input Fields Styling */
    .stTextInput input, .stNumberInput input, .stDateInput input, .stTimeInput input,
    .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        border-radius: var(--g-shape-corner-xs) !important; /* Using extra-small for inputs */
        border: 1px solid var(--app-input-border-color) !important;
        background-color: var(--app-card-bg-color) !important; /* Match card bg */
        color: var(--app-text-color) !important;
        padding: 10px 12px !important; 
        font-size: var(--g-font-size-body-m) !important;
        transition: border-color 0.15s ease-out, box-shadow 0.15s ease-out;
    }
    .stTextArea textarea { min-height: 100px; }
    .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus, 
    .stTimeInput input:focus, .stTextArea textarea:focus, 
    .stSelectbox div[data-baseweb="select"] > div:focus-within {
        border-color: var(--app-primary-color) !important; /* Use app primary for focus */
        box-shadow: 0 0 0 1px var(--app-primary-color) !important;
    }
    .stTextInput input::placeholder, .stNumberInput input::placeholder, .stTextArea textarea::placeholder {
        color: var(--app-text-muted-color) !important; opacity: 0.7;
    }
    /* Streamlit's default labels above inputs */
    div[data-testid="stTextInput"] > label, div[data-testid="stNumberInput"] > label,
    div[data-testid="stTextArea"] > label, div[data-testid="stDateInput"] > label,
    div[data-testid="stTimeInput"] > label, div[data-testid="stSelectbox"] > label {
        font-size: var(--g-font-size-body-s) !important; 
        color: var(--app-text-muted-color) !important;
        margin-bottom: 4px !important; padding-left: 2px !important; font-weight: 500;
    }
    div[data-testid="stForm"] { border: none; padding: 0; } 

    /* DataFrames */
    .stDataFrame { border: 1px solid var(--app-border-color); border-radius: var(--g-shape-corner-s); box-shadow: none; overflow: hidden;}
    .stDataFrame table thead th { 
        background-color: var(--g-surface-variant); 
        color: var(--app-text-muted-color); font-weight: 500; 
        border-bottom: 1px solid var(--app-border-color); 
        font-size: var(--g-font-size-label-l); text-transform:none; padding: 10px 14px;
        text-align: left;
    }
    .stDataFrame table tbody td { 
        color: var(--app-text-color); font-size: var(--g-font-size-body-m); 
        border-bottom: 1px solid var(--app-border-color); padding: 10px 14px;
        vertical-align: middle;
    }
    .stDataFrame table tbody tr:last-child td { border-bottom: none; }
    .stDataFrame table tbody tr:hover { background-color: color-mix(in srgb, var(--app-primary-color) 5%, transparent); }

    /* Metrics */
    div[data-testid="stMetric"] { padding: 8px 0px; }
    div[data-testid="stMetricLabel"] { /* Original metric label style */
        font-size: 0.95em !important; color: var(--app-text-muted-color) !important; font-weight: 500;
    }
    div[data-testid="stMetricValue"] { /* Original metric value style */
        font-size: 1.8em !important; font-weight: 600; color: var(--app-primary-color);
    }
    
    .employee-progress-item { 
        border: 1px solid var(--app-border-color); background-color: var(--app-card-bg-color); 
        border-radius: var(--g-shape-corner-s); padding:12px; text-align:center;
    }
    .employee-progress-item h6 {margin-top:0; margin-bottom:4px; font-size:var(--g-font-size-label-l); color: var(--app-primary-color); font-weight: 500;}
    .employee-progress-item p {font-size:12px; color: var(--app-text-muted-color); margin-bottom:6px;}
    
    .record-type-header { /* Your h6 class for log sections */
        font-size: 1.2em !important; color: var(--app-text-color) !important; 
        margin-top: 25px !important; margin-bottom: 12px !important; font-weight: 600 !important; 
        padding-bottom: 6px; border-bottom: 1px solid var(--app-border-color); 
    }
    hr { border-color: var(--app-border-color); margin: 20px 0; } /* Main content hr */

    /* Login Page Specifics */
    .login-page-container { display: flex; justify-content: center; align-items: center; min-height: 90vh; padding: 20px; }
    .login-container.card { max-width: 420px; width: 100%; padding: 28px; 
        border: 1px solid var(--app-border-color); 
        box-shadow: var(--g-elevation-1); 
    }
    .login-container h3 { /* Login card title */
        text-align:center; margin-bottom:24px; font-size: var(--g-font-size-title-l);
        color: var(--app-primary-color) !important; /* Match other h3 in card */
    }
    .login-container .stButton button { /* Login button specific */
        background-color: var(--app-primary-color) !important;
    }
    .login-container .stButton button:hover {
        background-color: color-mix(in srgb, var(--app-primary-color) 85%, black) !important;
    }
    
    /* Your Original Custom Notification Styling */
    .custom-notification {padding: 15px 20px; border-radius: var(--g-shape-corner-s); margin-bottom: 20px; font-size: 1em; border-left-width: 5px; border-left-style: solid; display: flex; align-items: center;}
    .custom-notification.success {background-color: #d1e7dd; color: #0f5132; border-left-color: var(--md-sys-color-success);}
    .custom-notification.error {background-color: #f8d7da; color: #842029; border-left-color: var(--md-sys-color-error);}
    .custom-notification.warning {background-color: #fff3cd; color: #664d03; border-left-color: var(--g-warning);}
    .custom-notification.info {background-color: #cff4fc; color: #055160; border-left-color: var(--app-primary-color);}

</style>
"""
# Python code continues from here...
# (The rest of your Python code remains exactly the same as you provided)
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
if 'nav_selection_display' not in st.session_state: st.session_state.nav_selection_display = None # For sidebar state


if not st.session_state.auth["logged_in"]:
    # Using markdown for layout, card class for styling from CSS
    st.markdown('<div class="login-page-container">', unsafe_allow_html=True) 
    st.markdown('<div class="login-container card">', unsafe_allow_html=True) 
    st.markdown("<h3>🔐 Login</h3>", unsafe_allow_html=True) # Will be styled by .card h3
    
    # Message display for login
    if st.session_state.user_message: 
        # Using st.error for login errors for consistency with how Streamlit shows them
        if st.session_state.message_type == "error":
            st.error(st.session_state.user_message, icon="❌")
        else: # For info like "Logged out"
            st.info(st.session_state.user_message, icon="ℹ️")
        st.session_state.user_message = None # Clear after display
        st.session_state.message_type = None

    uname = st.text_input("Username", key="login_uname_final_css") # Unique key
    pwd = st.text_input("Password", type="password", key="login_pwd_final_css") # Unique key
    if st.button("Login", key="login_button_final_css", use_container_width=True): # Unique key
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            # Initialize sidebar navigation state on login
            nav_options_display_on_login = [ # Original nav options from your Python
                "📆 Attendance", "📸 Upload Activity Photo", "🧾 Allowance", 
                "🎯 Goal Tracker", "💰 Payment Collection Tracker", "📊 View Logs"
            ]
            st.session_state.nav_selection_display = nav_options_display_on_login[0]

            st.session_state.user_message = "Login successful!"
            st.session_state.message_type = "success"
            st.rerun()
        else: 
            st.session_state.user_message = "Invalid username or password."
            st.session_state.message_type = "error"
            st.rerun() 
    st.markdown('</div></div>', unsafe_allow_html=True); st.stop()


current_user = st.session_state.auth 

# Global Message Display for main app area (after login)
if "user_message" in st.session_state and st.session_state.user_message:
    message_type_main = st.session_state.get("message_type", "info") 
    # Using Streamlit's native alerts which are generally well-styled
    if message_type_main == "success":
        st.success(st.session_state.user_message, icon="✅")
    elif message_type_main == "error":
        st.error(st.session_state.user_message, icon="❌")
    elif message_type_main == "warning":
        st.warning(st.session_state.user_message, icon="⚠️")
    else: # info
        st.info(st.session_state.user_message, icon="ℹ️")
    st.session_state.user_message = None # Clear after display
    st.session_state.message_type = None


with st.sidebar:
    # This outer div helps in making the sidebar scrollable if content exceeds viewport
    # and allows pushing logout to the bottom with flexbox.
    st.markdown('<div style="display: flex; flex-direction: column; height: 100vh;">', unsafe_allow_html=True)
    
    # User Info Section
    st.markdown(f"<div class='welcome-text'>{current_user['username']}!</div>", unsafe_allow_html=True) # Using your original .welcome-text
    user_sidebar_info = USERS.get(current_user["username"], {})
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]):
        st.image(user_sidebar_info["profile_photo"], width=100) # Your original image display
    st.markdown(
        f"<p style='text-align:center; font-size:0.9em; color: #e0e0e0;'>{user_sidebar_info.get('position', 'N/A')}</p>", # Your original position display
        unsafe_allow_html=True
    )
    st.markdown("---") # Your original divider

    # Navigation - This will be inside .sidebar-content which is scrollable
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True) # Start of scrollable content
    
    # Using your original nav_options for display and logic
    nav_options = [
        "📆 Attendance",
        "📸 Upload Activity Photo",
        "🧾 Allowance",
        "🎯 Goal Tracker",
        "💰 Payment Collection Tracker",
        "📊 View Logs"
    ]

    # Initialize nav selection state using the original nav_options
    if 'nav_selection_key_original' not in st.session_state or st.session_state.nav_selection_key_original not in nav_options:
        st.session_state.nav_selection_key_original = nav_options[0]
    
    try:
        current_nav_index = nav_options.index(st.session_state.nav_selection_key_original)
    except ValueError:
        current_nav_index = 0 # Default to first item
        st.session_state.nav_selection_key_original = nav_options[0]

    # Use st.radio with the original nav_options
    # The CSS will style these radio items. Emojis are part of the label text.
    nav = st.radio(
        "Navigation", # This is your original radio group label
        nav_options, 
        key="sidebar_nav_main_final_css", # A unique key for this radio group
        index=current_nav_index
        # label_visibility="visible" # Or "collapsed" if you prefer to hide "Navigation"
    )
    # Update session state if the selection changed
    if st.session_state.nav_selection_key_original != nav:
        st.session_state.nav_selection_key_original = nav 
        # No rerun needed here, st.radio itself causes a rerun upon change.
        # The 'nav' variable will hold the newly selected option for the current run.

    st.markdown('</div>', unsafe_allow_html=True) # End of scrollable content

    # Logout section
    st.markdown("<div class='logout-section-wrapper'>", unsafe_allow_html=True) 
    st.markdown("<hr class='sidebar-divider'>", unsafe_allow_html=True) # Use class if specific styling needed
    if st.button("🔒 Logout", key="logout_button_sidebar", use_container_width=True): 
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."
        st.session_state.message_type = "info"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True) 
    st.markdown("</div>", unsafe_allow_html=True) # Close main flex wrapper for sidebar


# --- Main Content (Using original 'nav' variable as per your Python logic) ---
if nav == "📆 Attendance": # Logic key from nav_options
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True) 
    st.info("📍 Location services are currently disabled for attendance. Photos for specific activities can be uploaded from the 'Upload Activity Photo' section.", icon="ℹ️") 
    st.markdown("---"); st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2); common_data = {"Username": current_user["username"], "Latitude": pd.NA, "Longitude": pd.NA}

    def process_general_attendance(attendance_type):
        global attendance_df 
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_data = {"Type": attendance_type, "Timestamp": now_str_display, **common_data}
        for col_name_att in ATTENDANCE_COLUMNS: 
            if col_name_att not in new_entry_data: new_entry_data[col_name_att] = pd.NA
        new_entry = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
        # Your original logic: temp_attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        # To modify global directly:
        attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        try:
            attendance_df.to_csv(ATTENDANCE_FILE, index=False) # Save the modified global df
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."; st.session_state.message_type = "success"; st.rerun()
        except Exception as e: st.session_state.user_message = f"Error saving attendance: {e}"; st.session_state.message_type = "error"; st.rerun()

    with col1:
        if st.button("✅ Check In", key="check_in_btn_main_content_final_css", use_container_width=True): 
            process_general_attendance("Check-In")
    with col2:
        if st.button("🚪 Check Out", key="check_out_btn_main_content_final_css", use_container_width=True): 
            process_general_attendance("Check-Out")
    st.markdown('</div></div>', unsafe_allow_html=True)

elif nav == "📸 Upload Activity Photo": # Logic key
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True) 
    current_lat = pd.NA; current_lon = pd.NA 
    with st.form(key="activity_photo_form_final_css"): 
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True) 
        activity_description = st.text_area("Brief description of activity/visit:", key="activity_desc_final_css") 
        img_file_buffer_activity = st.camera_input("Take a picture of your activity/visit", key="activity_camera_input_final_css") 
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo and Log Activity", key="activity_photo_form-Submit_final_css") 

    if submit_activity_photo:
        global activity_log_df 
        
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
                for col_name_act in ACTIVITY_LOG_COLUMNS: 
                    if col_name_act not in new_activity_data: new_activity_data[col_name_act] = pd.NA
                new_activity_entry = pd.DataFrame([new_activity_data], columns=ACTIVITY_LOG_COLUMNS)
                
                # Modify global df and save
                activity_log_df = pd.concat([activity_log_df, new_activity_entry], ignore_index=True)
                activity_log_df.to_csv(ACTIVITY_LOG_FILE, index=False)
                
                st.session_state.user_message = "Activity photo and log uploaded!"; st.session_state.message_type = "success"; st.rerun()
            except Exception as e: st.session_state.user_message = f"Error saving activity: {e}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "🧾 Allowance": # Logic key
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True) 
    with st.form(key="allowance_form_final_css"): 
        st.markdown("<h6 class='form-field-label-custom'>Select Allowance Type:</h6>", unsafe_allow_html=True) 
        a_type = st.radio("", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allowance_type_radio_final_css", horizontal=True, label_visibility='collapsed') 
        amount = st.number_input("Enter Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_final_css") 
        reason = st.text_area("Reason for Allowance:", key="allowance_reason_final_css", placeholder="Please provide a clear justification...") 
        submitted_allowance = st.form_submit_button("Submit Allowance Request", use_container_width=True, key="submit_allowance_btn_final_css") 

        if submitted_allowance:
            global allowance_df

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

elif nav == "🎯 Goal Tracker": # Logic key
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True) 
    TARGET_GOAL_YEAR = 2025; current_quarter_for_display = get_quarter_str_for_year(TARGET_GOAL_YEAR)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    achieved_color_sales = '#2ecc71' # Your original green
    target_color_sales = '#3498db'   # Your original blue


    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True) 
        admin_action = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR}"], key="admin_goal_action_radio_final_css", horizontal=True) 
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
                    num_cols_sales = min(3, len(employee_users) if employee_users else 1)
                    cols_sales = st.columns(num_cols_sales); col_idx_sales = 0
                    for index, row in summary_df_sales.iterrows():
                        progress_percent = (row['Achieved'] / row['Target'] * 100) if row['Target'] > 0 else 0
                        donut_fig = create_donut_chart(progress_percent, achieved_color=achieved_color_sales) # Original color
                        with cols_sales[col_idx_sales % num_cols_sales]:
                            st.markdown(f"<div class='employee-progress-item'><h6>{row['Employee']}</h6><p>Target: ₹{row['Target']:,.0f}<br>Achieved: ₹{row['Achieved']:,.0f}</p></div>", unsafe_allow_html=True)
                            st.pyplot(donut_fig, use_container_width=True); st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                        col_idx_sales += 1
                    st.markdown("<hr>", unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Sales Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_sales = create_team_progress_bar_chart(summary_df_sales, title="Team Sales Target vs. Achieved", achieved_color=achieved_color_sales, target_color=target_color_sales) # Original colors
                    if team_bar_fig_sales: st.pyplot(team_bar_fig_sales, use_container_width=True)
                    else: st.info("No sales data to plot for the team bar chart.")
                else: st.info(f"No sales goals data found for {current_quarter_for_display} to display team progress.")
        elif admin_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set or Update Employee Goal ({TARGET_GOAL_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options = [u for u,d in USERS.items() if d["role"]=="employee"];
            if not employee_options: st.warning("No employees available.");
            else:
                selected_emp = st.radio("Select Employee:", employee_options, key="goal_emp_radio_admin_set_final_css", horizontal=True) 
                quarter_options = [f"{TARGET_GOAL_YEAR}-Q{i}" for i in range(1,5)]; selected_period = st.radio("Goal Period:", quarter_options, key="goal_period_radio_admin_set_final_css", horizontal=True) 
                
                existing_g = goals_df[(goals_df["Username"].astype(str)==str(selected_emp)) & (goals_df["MonthYear"].astype(str)==str(selected_period))]
                g_desc,g_target,g_achieved,g_status = "",0.0,0.0,"Not Started"
                if not existing_g.empty:
                    g_data=existing_g.iloc[0]; g_desc=g_data.get("GoalDescription",""); g_target=float(pd.to_numeric(g_data.get("TargetAmount",0.0),errors='coerce') or 0.0)
                    g_achieved=float(pd.to_numeric(g_data.get("AchievedAmount",0.0),errors='coerce') or 0.0); g_status=g_data.get("Status","Not Started"); st.info(f"Editing goal for {selected_emp} - {selected_period}")
                
                with st.form(key=f"set_sales_goal_form_admin_final_css_{selected_emp}_{selected_period}"): 
                    new_desc=st.text_area("Goal Description",value=g_desc,key=f"desc_admin_sales_final_css_{selected_emp}_{selected_period}") 
                    new_target=st.number_input("Target Sales (INR)",value=g_target,min_value=0.0,step=1000.0,format="%.2f",key=f"target_admin_sales_final_css_{selected_emp}_{selected_period}") 
                    new_achieved=st.number_input("Achieved Sales (INR)",value=g_achieved,min_value=0.0,step=100.0,format="%.2f",key=f"achieved_admin_sales_final_css_{selected_emp}_{selected_period}") 
                    new_status=st.radio("Status:",status_options,index=status_options.index(g_status),horizontal=True,key=f"status_admin_sales_final_css_{selected_emp}_{selected_period}") 
                    submitted=st.form_submit_button("Save Goal", key="set_goal_form-Submit_final_css") 

                    if submitted:
                        global goals_df 
                        if not new_desc.strip(): st.warning("Description is required.")
                        elif new_target <= 0 and new_status not in ["Cancelled","On Hold","Not Started"]: st.warning("Target > 0 required.")
                        else:
                            # Logic to modify a copy and then reassign to global or modify global directly
                            editable_goals_df_admin = goals_df.copy() # Work on a copy
                            existing_g_indices_admin=editable_goals_df_admin[(editable_goals_df_admin["Username"].astype(str)==str(selected_emp))&(editable_goals_df_admin["MonthYear"].astype(str)==str(selected_period))].index
                            if not existing_g_indices_admin.empty: 
                                editable_goals_df_admin.loc[existing_g_indices_admin[0]]=[selected_emp,selected_period,new_desc,new_target,new_achieved,new_status]; msg_verb="updated"
                            else:
                                new_row_data={"Username":selected_emp,"MonthYear":selected_period,"GoalDescription":new_desc,"TargetAmount":new_target,"AchievedAmount":new_achieved,"Status":new_status}
                                for col_name_iter in GOALS_COLUMNS: 
                                    if col_name_iter not in new_row_data: new_row_data[col_name_iter]=pd.NA
                                new_row_df=pd.DataFrame([new_row_data],columns=GOALS_COLUMNS); editable_goals_df_admin=pd.concat([editable_goals_df_admin,new_row_df],ignore_index=True); msg_verb="set"
                            try:
                                editable_goals_df_admin.to_csv(GOALS_FILE,index=False)
                                goals_df = load_data(GOALS_FILE, GOALS_COLUMNS) # Reload global df
                                st.session_state.user_message=f"Sales goal for {selected_emp} ({selected_period}) {msg_verb}!"; st.session_state.message_type="success"; st.rerun()
                            except Exception as e: st.session_state.user_message=f"Error saving sales goal: {e}"; st.session_state.message_type="error"; st.rerun()
    else: 
        st.markdown("<h4 class='section-title'>My Sales Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True) 
        my_goals = goals_df[goals_df["Username"].astype(str) == str(current_user["username"])].copy()
        my_goals[["TargetAmount", "AchievedAmount"]] = my_goals[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric,errors="coerce").fillna(0.0)
        current_g_df = my_goals[my_goals["MonthYear"] == current_quarter_for_display]
        st.markdown(f"<h5>Current Goal Period: {current_quarter_for_display}</h5>", unsafe_allow_html=True)
        if not current_g_df.empty:
            g = current_g_df.iloc[0]; target_amt = g["TargetAmount"]; achieved_amt = g["AchievedAmount"]
            st.markdown(f"**Description:** {g.get('GoalDescription', 'N/A')}")
            col_metrics_sales, col_chart_sales = st.columns([0.6, 0.4]) 
            with col_metrics_sales:
                sub_col1,sub_col2=st.columns(2); sub_col1.metric("Target",f"₹{target_amt:,.0f}"); sub_col2.metric("Achieved",f"₹{achieved_amt:,.0f}")
                st.metric("Status",g.get("Status","In Progress"))
            with col_chart_sales:
                progress_percent_sales=(achieved_amt/target_amt*100) if target_amt > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:0px;'>Sales Progress</h6>",unsafe_allow_html=True)
                st.pyplot(create_donut_chart(progress_percent_sales, achieved_color=achieved_color_sales),use_container_width=True) # Original color
            st.markdown("<hr>", unsafe_allow_html=True)
            with st.form(key=f"update_sales_achievement_form_employee_content_final_v4_{current_user['username']}_{current_quarter_for_display}"): 
                new_val=st.number_input("Update Achieved Amount (INR):",value=achieved_amt,min_value=0.0,step=100.0,format="%.2f", key=f"employee_sales_ach_update_content_final_v4_{current_user['username']}_{current_quarter_for_display}") 
                submitted_ach=st.form_submit_button("Update Achievement", key="update_achievement-Submit_final") 
                if submitted_ach:
                    global goals_df 
                    
                    # Your original logic used editable_goals_df then saved it and then reloaded goals_df
                    # To align with the global modification pattern:
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
        if not past_goals.empty: render_goal_chart(past_goals, "Past Sales Goal Performance") # Default colors for this chart will be from function
        else: st.info(f"No past goal records for {TARGET_GOAL_YEAR}.")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "💰 Payment Collection Tracker": # Logic key
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3 class='card-title'>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True) 
    TARGET_YEAR_PAYMENT = 2025; current_quarter_display_payment = get_quarter_str_for_year(TARGET_YEAR_PAYMENT)
    status_options_payment = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    achieved_color_payment = '#2070c0' # Your original payment color
    target_color_payment = '#a1c4fd' # A lighter blue for target, can be adjusted

    if current_user["role"] == "admin":
        st.markdown("<h4 class='section-title'>Admin: Set & Track Payment Collection Goals</h4>", unsafe_allow_html=True) 
        admin_action_payment = st.radio("Action:", ["View Team Progress", f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}"], key="admin_payment_action_radio_content_final_v4", horizontal=True) 
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
                    num_cols_payment = min(3, len(employees_payment_list) if employees_payment_list else 1)
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
        elif admin_action_payment == f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT}":
            st.markdown(f"<h5>Set or Update Collection Goal ({TARGET_YEAR_PAYMENT} - Quarterly)</h5>", unsafe_allow_html=True)
            employees_for_payment_goal = [u for u,d in USERS.items() if d["role"]=="employee"];
            if not employees_for_payment_goal: st.warning("No employees available.")
            else:
                selected_emp_payment=st.radio("Select Employee:",employees_for_payment_goal,key="payment_emp_radio_admin_set_content_final_v4", horizontal=True) 
                quarters_payment=[f"{TARGET_YEAR_PAYMENT}-Q{i}" for i in range(1,5)]; selected_period_payment=st.radio("Quarter:",quarters_payment,key="payment_period_radio_admin_set_content_final_v4", horizontal=True) 
                
                existing_payment_goal=payment_goals_df[(payment_goals_df["Username"]==selected_emp_payment)&(payment_goals_df["MonthYear"]==selected_period_payment)]
                desc_payment,tgt_payment_val,ach_payment_val,stat_payment = "",0.0,0.0,"Not Started"
                if not existing_payment_goal.empty:
                    g_payment=existing_payment_goal.iloc[0]; desc_payment=g_payment.get("GoalDescription",""); tgt_payment_val=float(pd.to_numeric(g_payment.get("TargetAmount",0.0),errors='coerce') or 0.0)
                    ach_payment_val=float(pd.to_numeric(g_payment.get("AchievedAmount",0.0),errors='coerce') or 0.0); stat_payment=g_payment.get("Status","Not Started")
                    st.info(f"Editing payment goal for {selected_emp_payment} - {selected_period_payment}")
                
                with st.form(f"form_payment_admin_content_final_v4_{selected_emp_payment}_{selected_period_payment}"): 
                    new_desc_payment=st.text_input("Collection Goal Description",value=desc_payment,key=f"desc_admin_payment_content_final_v4_{selected_emp_payment}_{selected_period_payment}") 
                    new_tgt_payment=st.number_input("Target Collection (INR)",value=tgt_payment_val,min_value=0.0,step=1000.0,key=f"target_admin_payment_content_final_v4_{selected_emp_payment}_{selected_period_payment}") 
                    new_ach_payment=st.number_input("Collected Amount (INR)",value=ach_payment_val,min_value=0.0,step=500.0,key=f"achieved_admin_payment_content_final_v4_{selected_emp_payment}_{selected_period_payment}") 
                    new_status_payment=st.selectbox("Status",status_options_payment,index=status_options_payment.index(stat_payment),key=f"status_admin_payment_content_final_v4_{selected_emp_payment}_{selected_period_payment}") 
                    submitted_payment=st.form_submit_button("Save Goal", key="form_payment-Submit_v4") 

                    if submitted_payment:
                        global payment_goals_df 
                        if not new_desc_payment.strip(): st.warning("Description required.")
                        elif new_tgt_payment <= 0 and new_status_payment not in ["Cancelled","Not Started", "On Hold"]: st.warning("Target > 0 required unless status is Cancelled, Not Started or On Hold.")
                        else:
                            editable_payment_goals_df_admin = payment_goals_df.copy() # Work on a copy
                            existing_pg_indices_admin=editable_payment_goals_df_admin[(editable_payment_goals_df_admin["Username"]==selected_emp_payment)&(editable_payment_goals_df_admin["MonthYear"]==selected_period_payment)].index
                            if not existing_pg_indices_admin.empty: 
                                editable_payment_goals_df_admin.loc[existing_pg_indices_admin[0]]=[selected_emp_payment,selected_period_payment,new_desc_payment,new_tgt_payment,new_ach_payment,new_status_payment]; msg_payment="updated"
                            else:
                                new_row_data_p={"Username":selected_emp_payment,"MonthYear":selected_period_payment,"GoalDescription":new_desc_payment,"TargetAmount":new_tgt_payment,"AchievedAmount":new_ach_payment,"Status":new_status_payment}
                                for col_name_iter_p in PAYMENT_GOALS_COLUMNS: 
                                     if col_name_iter_p not in new_row_data_p: new_row_data_p[col_name_iter_p]=pd.NA
                                new_row_df_p=pd.DataFrame([new_row_data_p],columns=PAYMENT_GOALS_COLUMNS); editable_payment_goals_df_admin=pd.concat([editable_payment_goals_df_admin,new_row_df_p],ignore_index=True); msg_payment="set"
                            try:
                                editable_payment_goals_df_admin.to_csv(PAYMENT_GOALS_FILE,index=False)
                                payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS) # Reload global
                                st.session_state.user_message=f"Payment goal {msg_payment} for {selected_emp_payment} ({selected_period_payment})"; st.session_state.message_type="success"; st.rerun()
                            except Exception as e: st.session_state.user_message=f"Error saving payment goal: {e}"; st.session_state.message_type="error"; st.rerun()
    else: 
        st.markdown("<h4 class='section-title'>My Payment Collection Goals (2025)</h4>", unsafe_allow_html=True) 
        user_goals_payment = payment_goals_df[payment_goals_df["Username"]==current_user["username"]].copy()
        user_goals_payment[["TargetAmount","AchievedAmount"]] = user_goals_payment[["TargetAmount","AchievedAmount"]].apply(pd.to_numeric,errors="coerce").fillna(0.0)
        current_payment_goal_period_df = user_goals_payment[user_goals_payment["MonthYear"]==current_quarter_display_payment]
        st.markdown(f"<h5>Current Quarter: {current_quarter_display_payment}</h5>", unsafe_allow_html=True)
        if not current_payment_goal_period_df.empty:
            g_pay=current_payment_goal_period_df.iloc[0]; tgt_pay=g_pay["TargetAmount"]; ach_pay=g_pay["AchievedAmount"]
            st.markdown(f"**Goal:** {g_pay.get('GoalDescription','')}")
            col_metrics_pay,col_chart_pay=st.columns([0.6, 0.4]) 
            with col_metrics_pay:
                sub_col1_pay,sub_col2_pay=st.columns(2); sub_col1_pay.metric("Target",f"₹{tgt_pay:,.0f}"); sub_col2_pay.metric("Collected",f"₹{ach_pay:,.0f}")
                st.metric("Status",g_pay.get("Status","In Progress"))
            with col_chart_pay:
                progress_percent_pay=(ach_pay/tgt_pay*100) if tgt_pay > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:0px;'>Collection Progress</h6>",unsafe_allow_html=True)
                st.pyplot(create_donut_chart(progress_percent_pay, achieved_color=achieved_color_payment),use_container_width=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            with st.form(key=f"update_payment_collection_form_employee_content_final_v4_{current_user['username']}_{current_quarter_display_payment}"): 
                new_ach_val_payment=st.number_input("Update Collected Amount (INR):",value=ach_pay,min_value=0.0,step=500.0, key=f"employee_payment_ach_update_content_final_v4_{current_user['username']}_{current_quarter_display_payment}") 
                submit_collection_update=st.form_submit_button("Update Collection", key="update_collection-Submit_final") 
                if submit_collection_update:
                    global payment_goals_df 
                    
                    # Your original logic used editable_payment_goals_df then saved it and then reloaded
                    # To align with the global modification pattern:
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
        if df_logs.empty: st.info(f"No activity logs found."); return 
        df_logs_sorted = df_logs.sort_values(by="Timestamp", ascending=False).copy()
        for index, row in df_logs_sorted.iterrows():
            st.markdown("<hr style='margin: 12px 0;'>", unsafe_allow_html=True); 
            col_details, col_photo = st.columns([0.75, 0.25]) 
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
                        try: st.image(image_path_to_display, width=100, use_column_width='never') 
                        except Exception as img_e: st.warning(f"Img err: {img_e}")
                    else: st.caption(f"Img missing")
    
    def display_generic_logs_custom(df_logs, record_type_name): 
        if df_logs.empty: st.info(f"No {record_type_name.lower()} records found."); return
        st.dataframe(df_logs.reset_index(drop=True), use_container_width=True)


    if current_user["role"] == "admin":
        st.markdown("<h4 class='section-title'>Admin: View Employee Records</h4>", unsafe_allow_html=True) 
        employee_name_list = [uname for uname in USERS.keys() if USERS[uname]["role"] == "employee"]
        selected_employee_log = st.selectbox("Select Employee:", employee_name_list, key="log_employee_select_admin_content_final_page_v3", index=0 if employee_name_list else None) 

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
                    emp_attendance_log_copy = emp_attendance_log.copy() 
                    emp_attendance_log_copy['Location'] = emp_attendance_log_copy.apply(lambda r: f"Lat:{r.get('Latitude'):.2f},Lon:{r.get('Longitude'):.2f}" if pd.notna(r.get('Latitude')) and pd.notna(r.get('Longitude')) else "N/R", axis=1)
                    st.dataframe(emp_attendance_log_copy[display_cols_att + ['Location']].sort_values("Timestamp", ascending=False).reset_index(drop=True), use_container_width=True)
                else:
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
    else: 
        st.markdown(f"<h4 class='section-title'>My Records: {current_user['username']}</h4>", unsafe_allow_html=True) 
        st.markdown("<h6 class='record-type-header'>My Field Activity Logs</h6>", unsafe_allow_html=True)
        display_activity_logs_with_photos(activity_log_df[activity_log_df["Username"] == current_user["username"]], current_user["username"])
        
        st.markdown("<h6 class='record-type-header'>My General Attendance</h6>", unsafe_allow_html=True)
        my_attendance_log = attendance_df[attendance_df["Username"] == current_user["username"]]
        if not my_attendance_log.empty:
            display_cols_my_att = ["Type", "Timestamp"]
            if 'Latitude' in my_attendance_log.columns and 'Longitude' in my_attendance_log.columns: 
                my_attendance_log_copy = my_attendance_log.copy() 
                my_attendance_log_copy['Location'] = my_attendance_log_copy.apply(lambda r: f"Lat:{r.get('Latitude'):.2f},Lon:{r.get('Longitude'):.2f}" if pd.notna(r.get('Latitude')) and pd.notna(r.get('Longitude')) else "N/R", axis=1)
                st.dataframe(my_attendance_log_copy[display_cols_my_att + ['Location']].sort_values("Timestamp", ascending=False).reset_index(drop=True), use_container_width=True)
            else:
                st.dataframe(my_attendance_log[display_cols_my_att].sort_values("Timestamp", ascending=False).reset_index(drop=True), use_container_width=True)
        else: st.info("No attendance records found for you.")
        
        st.markdown("<h6 class='record-type-header'>My Allowances</h6>", unsafe_allow_html=True)
        display_generic_logs_custom(allowance_df[allowance_df["Username"] == current_user["username"]].sort_values("Date", ascending=False), "Allowance")

        st.markdown("<h6 class='record-type-header'>My Sales Goals</h6>", unsafe_allow_html=True)
        display_generic_logs_custom(goals_df[goals_df["Username"] == current_user["username"]].sort_values("MonthYear", ascending=False), "Sales Goal")

        st.markdown("<h6 class='record-type-header'>My Payment Collection Goals</h6>", unsafe_allow_html=True)
        display_generic_logs_custom(payment_goals_df[payment_goals_df["Username"] == current_user["username"]].sort_values("MonthYear", ascending=False), "Payment Goal")
    st.markdown('</div>', unsafe_allow_html=True)
