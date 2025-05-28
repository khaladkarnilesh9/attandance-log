# app.py
import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date
import os
import pytz
import plotly.express as px
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# --- Charting Functions ---
def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty: st.warning(f"No data available to plot for {chart_title}."); return
    df_chart = df.copy()
    df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear", value_vars=["TargetAmount", "AchievedAmount"], var_name="Metric", value_name="Amount")
    if df_melted.empty or df_melted['Amount'].sum() == 0: st.info(f"No data to plot for {chart_title} after processing."); return
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group", labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"}, title=chart_title, color_discrete_map={'TargetAmount': '#4285F4', 'AchievedAmount': '#34A853'})
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric'); fig.update_xaxes(type='category')
    st.plotly_chart(fig, use_container_width=True)

def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#34A853', remaining_color='#e0e0e0', center_text_color=None):
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=90); fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    try: progress_percentage = float(progress_percentage)
    except (ValueError, TypeError): progress_percentage = 0.0
    progress_percentage = max(0.0, min(progress_percentage, 100.0)); remaining_percentage = 100.0 - progress_percentage
    if progress_percentage <= 0.01: sizes, slice_colors, actual_progress_display = [100.0], [remaining_color], 0.0
    elif progress_percentage >= 99.99: sizes, slice_colors, actual_progress_display = [100.0], [achieved_color], 100.0
    else: sizes, slice_colors, actual_progress_display = [progress_percentage, remaining_percentage], [achieved_color, remaining_color], progress_percentage
    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.4, edgecolor='white'))
    centre_circle = plt.Circle((0,0),0.60,fc='white'); fig.gca().add_artist(centre_circle)
    text_color_to_use = center_text_color if center_text_color else (achieved_color if actual_progress_display > 0 else '#5f6368')
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=12, fontweight='bold', color=text_color_to_use)
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0); return fig

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
    def autolabel(rects_bar_func): # Renamed parameter
        for rect_bar_f in rects_bar_func:
            height_bar_f = rect_bar_f.get_height()
            if height_bar_f > 0: ax.annotate(f'{height_bar_f:,.0f}', xy=(rect_bar_f.get_x() + rect_bar_f.get_width() / 2, height_bar_f), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=7, color='#202124')
    autolabel(rects1); autolabel(rects2); fig.tight_layout(pad=1.5); return fig

# --- CSS Styling ---
html_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
    :root {
        --primary-color: #4285F4; --secondary-color: #34A853; --accent-color: #EA4335; --yellow-color: #FBBC05;
        --success-color: #34A853; --danger-color: #EA4335; --warning-color: #FBBC05; --info-color: #4285F4;
        --body-bg-color: #f8f9fa; --card-bg-color: #ffffff; --text-color: #202124; --text-muted-color: #5f6368;
        --border-color: #dadce0; --input-border-color: #dadce0;
        --font-family: 'Roboto', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        --border-radius: 8px; --border-radius-lg: 12px;
        --box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
        --box-shadow-sm: 0 1px 2px 0 rgba(60,64,67,0.1);
    }
    body { font-family: var(--font-family); background-color: var(--body-bg-color); color: var(--text-color); line-height: 1.5; font-weight: 400; }
    h1, h2, h3, h4, h5, h6 { color: var(--text-color); font-weight: 500; letter-spacing: -0.25px; }
    .main .block-container > div:first-child > div:first-child > div:first-child > h1 { text-align: left; font-size: 1.75rem; font-weight: 500; padding-bottom: 16px; margin-bottom: 24px; border-bottom: 1px solid var(--border-color); }
    .card { background-color: var(--card-bg-color); padding: 24px; border-radius: var(--border-radius); box-shadow: var(--box-shadow-sm); margin-bottom: 24px; border: 1px solid var(--border-color); }
    .card h3 { margin-top: 0; color: var(--text-color); padding-bottom: 12px; margin-bottom: 20px; font-size: 1.25rem; font-weight: 500; display: flex; align-items: center; }
    .card h3:before { content: ""; display: inline-block; width: 4px; height: 20px; background-color: var(--primary-color); margin-right: 12px; border-radius: 2px; }
    .card h4 { color: var(--text-color); margin-top: 24px; margin-bottom: 16px; font-size: 1.1rem; font-weight: 500; }
    .card h5 { font-size: 1rem; color: var(--text-color); margin-top: 20px; margin-bottom: 12px; font-weight: 500; }
    .card h6 { font-size: 0.875rem; color: var(--text-muted-color); margin-top: 0; margin-bottom: 12px; font-weight: 400; text-transform: uppercase; letter-spacing: 0.5px; }
    .form-field-label h6 { font-size: 0.875rem; color: var(--text-muted-color); margin-top: 16px; margin-bottom: 8px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
    .login-container { max-width: 480px; margin: 60px auto; border-top: 4px solid var(--primary-color); }
    .login-container .stButton button { width: 100%; background-color: var(--primary-color) !important; color: white !important; font-size: 1rem; padding: 12px 20px; border-radius: var(--border-radius); border: none !important; font-weight: 500 !important; box-shadow: none !important; transition: background-color 0.2s ease; }
    .login-container .stButton button:hover { background-color: #3367d6 !important; color: white !important; box-shadow: none !important; }
    .stButton:not(.login-container .stButton) button { background-color: var(--primary-color); color: white; padding: 10px 20px; border: none; border-radius: var(--border-radius); font-size: 0.875rem; font-weight: 500; transition: background-color 0.2s ease; box-shadow: none; cursor: pointer; }
    .stButton:not(.login-container .stButton) button:hover { background-color: #3367d6; box-shadow: none; }
    .stButton button[type="submit"] { background-color: var(--primary-color); } .stButton button[type="submit"]:hover { background-color: #3367d6; }
    .stButton button[id*="logout_button_sidebar"] { background-color: var(--danger-color) !important; border: none !important; color: white !important; font-weight: 500 !important; }
    .stButton button[id*="logout_button_sidebar"]:hover { background-color: #d33426 !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input, .stTimeInput input, .stSelectbox div[data-baseweb="select"] > div { border-radius: var(--border-radius) !important; border: 1px solid var(--input-border-color) !important; padding: 10px 12px !important; font-size: 0.875rem !important; color: var(--text-color) !important; background-color: var(--card-bg-color) !important; transition: border-color 0.2s ease, box-shadow 0.2s ease; }
    .stTextInput input::placeholder, .stNumberInput input::placeholder, .stTextArea textarea::placeholder { color: var(--text-muted-color) !important; opacity: 1; }
    .stTextArea textarea { min-height: 100px; }
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus, .stDateInput input:focus, .stTimeInput input:focus, .stSelectbox div[data-baseweb="select"] > div:focus-within { border-color: var(--primary-color) !important; box-shadow: 0 0 0 2px rgba(66,133,244,0.15) !important; }
    [data-testid="stSidebar"] { background-color: #ffffff; padding: 16px !important; box-shadow: 1px 0 2px 0 rgba(60,64,67,0.1), 1px 0 3px 1px rgba(60,64,67,0.1); border-right: 1px solid var(--border-color); }
    [data-testid="stSidebar"] .sidebar-content { padding-top: 8px; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] div:not([data-testid="stRadio"]) { color: var(--text-color) !important; }
    [data-testid="stSidebar"] .stRadio > label > div > p { font-size: 0.875rem !important; color: var(--text-color) !important; padding: 0; margin: 0; display: flex; align-items: center; }
    [data-testid="stSidebar"] .stRadio > label { padding: 8px 12px; border-radius: var(--border-radius); margin-bottom: 4px; transition: background-color 0.2s ease; display: flex; align-items: center; }
    [data-testid="stSidebar"] .stRadio > label:hover { background-color: rgba(66,133,244,0.08); }
    .welcome-text { font-size: 1rem; font-weight: 500; margin-bottom: 20px; text-align: center; color: var(--text-color) !important; padding-bottom: 16px; border-bottom: 1px solid var(--border-color); }
    [data-testid="stSidebar"] [data-testid="stImage"] > img { border-radius: 50%; border: 2px solid var(--border-color); margin: 0 auto 12px auto; display: block; }
    .stDataFrame { width: 100%; border: 1px solid var(--border-color); border-radius: var(--border-radius); overflow: hidden; box-shadow: var(--box-shadow-sm); margin-bottom: 20px; }
    .stDataFrame table { width: 100%; border-collapse: collapse; }
    .stDataFrame table thead th { background-color: #f8f9fa; color: var(--text-muted-color); font-weight: 500; text-align: left; padding: 12px 16px; border-bottom: 1px solid var(--border-color); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px; }
    .stDataFrame table tbody td { padding: 12px 16px; border-bottom: 1px solid var(--border-color); vertical-align: middle; color: var(--text-color); font-size: 0.875rem; }
    .stDataFrame table tbody tr:last-child td { border-bottom: none; }
    .stDataFrame table tbody tr:hover { background-color: #f1f3f4; }
    .employee-progress-item { border: 1px solid var(--border-color); border-radius: var(--border-radius); padding: 16px; text-align: center; background-color: var(--card-bg-color); margin-bottom: 12px; box-shadow: var(--box-shadow-sm); }
    .employee-progress-item h6 { margin-top: 0; margin-bottom: 8px; font-size: 0.875rem; color: var(--text-color); font-weight: 500; }
    .employee-progress-item p { font-size: 0.75rem; color: var(--text-muted-color); margin-bottom: 8px; }
    .button-column-container > div[data-testid="stHorizontalBlock"] { gap: 16px; }
    .button-column-container .stButton button { width: 100%; }
    div[role="radiogroup"] { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 20px; }
    div[role="radiogroup"] > label { background-color: white; color: var(--text-color); padding: 8px 16px; border-radius: var(--border-radius); border: 1px solid var(--border-color); cursor: pointer; transition: all 0.2s ease; font-size: 0.875rem; font-weight: 400; }
    div[role="radiogroup"] > label:hover { background-color: #f8f9fa; border-color: var(--border-color); }
    .employee-section-header { color: var(--text-color); margin-top: 24px; border-bottom: 1px solid var(--border-color); padding-bottom: 8px; font-size: 1.1rem; }
    .record-type-header { font-size: 1rem; color: var(--text-color); margin-top: 20px; margin-bottom: 12px; font-weight: 500; }
    div[data-testid="stImage"] > img { border-radius: var(--border-radius); border: 1px solid var(--border-color); box-shadow: var(--box-shadow-sm); }
    .stProgress > div > div { background-color: var(--primary-color) !important; border-radius: var(--border-radius); }
    .stProgress { border-radius: var(--border-radius); background-color: #e9ecef; }
    div[data-testid="stMetricLabel"] { font-size: 0.875rem !important; color: var(--text-muted-color) !important; font-weight: 400; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 500; color: var(--text-color); }
    .custom-notification { padding: 12px 16px; border-radius: var(--border-radius); margin-bottom: 16px; font-size: 0.875rem; border-left-width: 4px; border-left-style: solid; display: flex; align-items: center; background-color: white; box-shadow: var(--box-shadow-sm); }
    .custom-notification.success { background-color: #e6f4ea; color: var(--text-color); border-left-color: var(--success-color); }
    .custom-notification.error { background-color: #fce8e6; color: var(--text-color); border-left-color: var(--danger-color); }
    .custom-notification.warning { background-color: #fef7e0; color: var(--text-color); border-left-color: var(--warning-color); }
    .custom-notification.info { background-color: #e8f0fe; color: var(--text-color); border-left-color: var(--info-color); }
    .badge { display: inline-block; padding: 4px 8px; font-size: 0.75rem; font-weight: 500; line-height: 1; color: white; text-align: center; white-space: nowrap; vertical-align: baseline; border-radius: 12px; }
    .badge.green { background-color: var(--success-color); } .badge.red { background-color: var(--danger-color); } .badge.orange { background-color: var(--warning-color); } .badge.blue { background-color: var(--primary-color); } .badge.grey { background-color: var(--text-muted-color); }
    .metric-card { background-color: white; border-radius: var(--border-radius); padding: 16px; box-shadow: var(--box-shadow-sm); border: 1px solid var(--border-color); margin-bottom: 16px; }
    .metric-card-title { font-size: 0.75rem; color: var(--text-muted-color); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .metric-card-value { font-size: 1.5rem; font-weight: 500; color: var(--text-color); margin-bottom: 4px; }
    .metric-card-change { font-size: 0.75rem; display: flex; align-items: center; }
    .metric-card-change.positive { color: var(--success-color); } .metric-card-change.negative { color: var(--danger-color); }
    .stTabs [role="tablist"] { gap: 0px; margin-bottom: 0px; border-bottom: 1px solid var(--border-color); }
    .stTabs [role="tab"] { padding: 10px 16px; border-radius: 0; border: none; border-bottom: 2px solid transparent; background-color: transparent; color: var(--text-muted-color); font-size: 0.875rem; font-weight: 500; transition: all 0.2s ease; margin-right: 16px; position: relative; top: 1px; }
    .stTabs [role="tab"]:last-child { margin-right: 0; }
    .stTabs [role="tab"]:hover { background-color: transparent; color: var(--text-color); }
    .stTabs [aria-selected="true"] { background-color: transparent !important; color: var(--primary-color) !important; border-bottom: 2px solid var(--primary-color) !important; font-weight: 500; box-shadow: none !important; }
    .stDateInput input { background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='%235f6368'%3E%3Cpath d='M19 3h-1V1h-2v2H8V1H6v2H5c-1.11 0-1.99.9-1.99 2L3 19c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V8h14v11zM7 10h5v5H7v-5z'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 12px center; padding-right: 40px !important; }
    .material-symbols-outlined { font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 20; font-size: 20px; vertical-align: text-bottom; margin-right: 10px; color: inherit; }
    [data-testid="stSidebar"] .material-symbols-outlined { color: var(--text-muted-color); font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 20; font-size: 20px; }
    div[role="radiogroup"] div[data-baseweb="radio"] input[type="radio"]:checked + label, div[role="radiogroup"] div[data-baseweb="radio"][aria-checked="true"] + label { background-color: rgba(66, 133, 244, 0.15) !important; color: var(--primary-color) !important; border-color: var(--primary-color) !important; font-weight: 500 !important; }
    div[role="radiogroup"] input[type="radio"]:checked + div[data-testid="stRadioMark"], div[role="radiogroup"] input[type="radio"]:checked + label div[data-testid="stRadioMark"] { background-color: var(--primary-color) !important; border-color: var(--primary-color) !important; box-shadow: inset 0 0 0 4px var(--card-bg-color) !important; }
    div[role="radiogroup"] input[type="radio"]:checked + label::before { background-color: var(--primary-color) !important; border-color: var(--primary-color) !important; }
    [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label, [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label { background-color: rgba(66, 133, 244, 0.15) !important; }
    [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label > div > p, [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label > div > p { color: var(--primary-color) !important; font-weight: 500 !important; }
    [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label .material-symbols-outlined, [data-testid="stSidebar"] .stRadio div[aria-checked="true"] + label .material-symbols-outlined { color: var(--primary-color) !important; font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 20 !important; }
    [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + div[data-testid="stRadioMark"], [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label div[data-testid="stRadioMark"] { background-color: var(--primary-color) !important; border-color: var(--primary-color) !important; box-shadow: inset 0 0 0 4px #ffffff !important; }
    [data-testid="stSidebar"] .stRadio input[type="radio"]:checked + label::before { background-color: var(--primary-color) !important; border-color: var(--primary-color) !important; }
</style>
"""
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
                if hasattr(draw, 'textbbox'): # Modern Pillow
                    bbox = draw.textbbox((0,0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    text_x = (120 - text_width) / 2
                    text_y = (120 - text_height) / 2 - bbox[1] # Adjust for vertical alignment
                elif hasattr(draw, 'textsize'): # Older Pillow
                    text_width, text_height = draw.textsize(text, font=font)
                    text_x = (120 - text_width) / 2
                    text_y = (120 - text_height) / 2
                else: # Fallback
                    text_x, text_y = 30, 30
                draw.text((text_x, text_y), text, fill=(28,78,128), font=font); img.save(img_path)
            except Exception as e_img: st.warning(f"Could not create placeholder image for {user_key}: {e_img}", icon="🖼️")
else:
    pass # Warning handled during login if Pillow is missing

# --- File Paths & Timezone & Directories ---
ATTENDANCE_FILE = "attendance.csv"; ALLOWANCE_FILE = "allowances.csv"; GOALS_FILE = "goals.csv"
PAYMENT_GOALS_FILE = "payment_goals.csv"; ACTIVITY_LOG_FILE = "activity_log.csv"
ACTIVITY_PHOTOS_DIR = "activity_photos"
# Updated filenames based on your GitHub image
PRODUCTS_FILE = "symplanta_products_with_images.csv"
STORES_FILE = "agri_stores.csv"
ORDERS_FILE = "orders.csv"; ORDER_SUMMARY_FILE = "order_summary.csv"

for dir_path_create in [ACTIVITY_PHOTOS_DIR, "images"]:
    if not os.path.exists(dir_path_create):
        try: os.makedirs(dir_path_create)
        except OSError as e_dir: st.warning(f"Could not create directory {dir_path_create}: {e_dir}", icon="📁")

TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError: st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'.", icon="🌍"); st.stop()

def get_current_time_in_tz(): return datetime.now(timezone.utc).astimezone(tz)
def get_quarter_str_for_year(year):
    now_month = get_current_time_in_tz().month
    if 1 <= now_month <= 3: return f"{year}-Q1"; elif 4 <= now_month <= 6: return f"{year}-Q2"
    elif 7 <= now_month <= 9: return f"{year}-Q3"; else: return f"{year}-Q4"

def load_data(path, columns, parse_dates_cols=None):
    if os.path.exists(path):
        try:
            if os.path.getsize(path) > 0:
                df = pd.read_csv(path, parse_dates=parse_dates_cols)
                for col in columns: # Ensure all defined columns exist
                    if col not in df.columns: df[col] = pd.NA
                # Convert specific columns to numeric after ensuring they exist
                num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude", 
                            "UnitPrice", "Stock", "Quantity", "LineTotal", 
                            "Subtotal", "DiscountAmount", "TaxAmount", "GrandTotal", "Price"] # Added "Price" here
                for nc in num_cols:
                    if nc in df.columns: df[nc] = pd.to_numeric(df[nc], errors='coerce')
                return df
            else: return pd.DataFrame(columns=columns)
        except pd.errors.EmptyDataError: return pd.DataFrame(columns=columns)
        except Exception as e_load: st.error(f"Error loading {path}: {e_load}. Check file format/content.", icon="📄"); return pd.DataFrame(columns=columns)
    else: # File does not exist
        df = pd.DataFrame(columns=columns);
        try: df.to_csv(path, index=False) # Create empty file with headers
        except Exception as e_create: st.warning(f"Could not create file {path}: {e_create}", icon="📝")
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]

# Updated Product Columns to match symplanta_products_with_images.csv
PRODUCTS_COLUMNS_FROM_CSV = ["Product Name", "Category", "Size", "Price", "Image URL"]
# Internal structure we'll use, adding ProductVariantID and standardizing names
PRODUCTS_COLUMNS_INTERNAL = ["ProductVariantID", "ProductName", "Category", "UnitOfMeasure", "UnitPrice", "ImageURL", "SKU", "Stock", "Description"]

STORES_COLUMNS = ["StoreID", "StoreName", "ContactPerson", "ContactPhone", "Address", "VillageTown", "District", "State", "Pincode", "GSTIN", "StoreType"]
ORDERS_COLUMNS = ["OrderID", "OrderDate", "Salesperson", "StoreID", "ProductVariantID", "SKU", "ProductName", "Quantity", "UnitOfMeasure", "UnitPrice", "LineTotal"]
ORDER_SUMMARY_COLUMNS = ["OrderID", "OrderDate", "Salesperson", "StoreID", "StoreName", "Subtotal", "DiscountAmount", "TaxAmount", "GrandTotal", "Notes", "PaymentMode", "ExpectedDeliveryDate"]

attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS, parse_dates_cols=['Timestamp'])
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS, parse_dates_cols=['Date'])
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
activity_log_df = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS, parse_dates_cols=['Timestamp'])

# --- MODIFIED Product DataFrame Loading and Processing ---
raw_products_df = load_data(PRODUCTS_FILE, PRODUCTS_COLUMNS_FROM_CSV) # Use CSV columns for loading
products_df = pd.DataFrame(columns=PRODUCTS_COLUMNS_INTERNAL) # Initialize empty df with internal structure

if not raw_products_df.empty:
    temp_products_list = []
    # Check if 'Price' column was loaded as numeric, if not, coerce again
    if 'Price' in raw_products_df.columns and not pd.api.types.is_numeric_dtype(raw_products_df['Price']):
        raw_products_df['Price'] = pd.to_numeric(raw_products_df['Price'], errors='coerce')

    for index, row in raw_products_df.iterrows():
        product_name = str(row.get("Product Name", "")).strip() # Use .get for safety
        size = str(row.get("Size", "")).strip()
        variant_id = f"{product_name.replace(' ', '_').lower()}_{size.replace(' ', '_').replace('.', '').lower()}_{index}"
        
        temp_products_list.append({
            "ProductVariantID": variant_id,
            "ProductName": product_name,
            "Category": str(row.get("Category", "Uncategorized")).strip(),
            "UnitOfMeasure": size,
            "UnitPrice": row.get("Price", 0.0), # Already coerced in load_data or above
            "ImageURL": str(row.get("Image URL", "")).strip() if pd.notna(row.get("Image URL")) else None,
            "SKU": f"SYMP_{index+1:03d}_{size.replace(' ', '').upper()}", # Improved placeholder SKU
            "Stock": 100, # Placeholder - GET ACTUAL DATA
            "Description": f"{product_name} - {size}"
        })
    products_df = pd.DataFrame(temp_products_list, columns=PRODUCTS_COLUMNS_INTERNAL)
    if "UnitPrice" in products_df.columns: products_df["UnitPrice"] = products_df["UnitPrice"].fillna(0.0)
    if "Stock" in products_df.columns: products_df["Stock"] = pd.to_numeric(products_df["Stock"], errors='coerce').fillna(0)


stores_df = load_data(STORES_FILE, STORES_COLUMNS)
orders_df = load_data(ORDERS_FILE, ORDERS_COLUMNS, parse_dates_cols=['OrderDate'])
order_summary_df = load_data(ORDER_SUMMARY_FILE, ORDER_SUMMARY_COLUMNS, parse_dates_cols=['OrderDate', 'ExpectedDeliveryDate'])

def generate_order_id():
    global order_summary_df
    if order_summary_df.empty or "OrderID" not in order_summary_df.columns or order_summary_df["OrderID"].isnull().all(): return "ORD-00001"
    existing_ids_series = order_summary_df["OrderID"].astype(str).str.extract(r'ORD-(\d+)')
    if existing_ids_series.empty or existing_ids_series[0].isnull().all(): return "ORD-00001"
    valid_numeric_ids = pd.to_numeric(existing_ids_series[0], errors='coerce').dropna()
    if valid_numeric_ids.empty: next_num = 1
    else: next_num = int(valid_numeric_ids.max()) + 1
    return f"ORD-{next_num:05d}"

default_session_state = {
    "user_message": None, "message_type": None, "auth": {"logged_in": False, "username": None, "role": None},
    "order_line_items": [], "current_product_id_symplanta": None, "current_quantity_order": 1,
    "order_store_select": None, "order_notes": "", "order_discount": 0.0, "order_tax": 0.0,
    "selected_nav_label": None, "admin_order_view_selected_order_id": None
}
for key_ss, value_ss in default_session_state.items():
    if key_ss not in st.session_state: st.session_state[key_ss] = value_ss

if not st.session_state.auth["logged_in"]:
    st.title("Symplanta TrackSphere")
    st.markdown("### Field Force & Sales Order Management")
    if not PILLOW_INSTALLED: st.warning("Pillow library not installed. User profile images might not display. `pip install Pillow`", icon="⚠️")
    message_placeholder_login = st.empty()
    if st.session_state.user_message:
        message_placeholder_login.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
        st.session_state.user_message = None; st.session_state.message_type = None
    st.markdown('<div class="login-container card" style="margin-top: 30px;">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined' style='font-size: 1.5em; margin-right: 8px; vertical-align:bottom;'>login</span> Login</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname_main_key_v4")
    pwd = st.text_input("Password", type="password", key="login_pwd_main_key_v4")
    if st.button("Login", key="login_button_main_key_v4", type="primary"):
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
    message_placeholder_main.markdown(f"<div class='custom-notification {message_type_main}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
    st.session_state.user_message = None; st.session_state.message_type = None

with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user_auth['username']}!</div>", unsafe_allow_html=True)
    nav_options_base_icons = { "Dashboard": "<span class='material-symbols-outlined'>dashboard</span> Dashboard", "Attendance": "<span class='material-symbols-outlined'>event_available</span> Attendance", "Upload Activity": "<span class='material-symbols-outlined'>cloud_upload</span> Upload Activity", "Allowance": "<span class='material-symbols-outlined'>receipt_long</span> Allowance Claim",}
    nav_options_sales_person_icons = { "Create Order": "<span class='material-symbols-outlined'>add_shopping_cart</span> Create Order",}
    nav_options_goals_icons = { "Sales Goals": "<span class='material-symbols-outlined'>flag</span> Sales Goals", "Payment Collection": "<span class='material-symbols-outlined'>payments</span> Payment Collection",}
    nav_options_admin_manage_icons = { "Manage Records": "<span class='material-symbols-outlined'>admin_panel_settings</span> Manage Records",}
    nav_options_employee_logs_icons = { "My Records": "<span class='material-symbols-outlined'>article</span> My Records",}
    nav_options_with_icons = nav_options_base_icons.copy()
    if current_user_auth['role'] == 'sales_person': nav_options_with_icons.update(nav_options_sales_person_icons); nav_options_with_icons.update(nav_options_goals_icons); nav_options_with_icons.update(nav_options_employee_logs_icons)
    elif current_user_auth['role'] == 'admin': nav_options_with_icons.update(nav_options_goals_icons); nav_options_with_icons.update(nav_options_admin_manage_icons)
    elif current_user_auth['role'] == 'employee': nav_options_with_icons.update(nav_options_employee_logs_icons)
    option_labels = list(nav_options_with_icons.values()); option_keys = list(nav_options_with_icons.keys())
    if st.session_state.selected_nav_label is None or st.session_state.selected_nav_label not in option_labels: st.session_state.selected_nav_label = option_labels[0] if option_labels else None
    st.markdown("<h5 style='margin-top:0; margin-bottom:10px; font-weight:500; color: var(--text-color); padding-left:10px;'>Navigation</h5>", unsafe_allow_html=True)
    selected_nav_html_label = st.radio( "MainNavigationRadioSidebarKeyV4", options=option_labels, index=option_labels.index(st.session_state.selected_nav_label) if st.session_state.selected_nav_label in option_labels else 0, label_visibility="collapsed", key="sidebar_nav_radio_final_key_v4")
    st.session_state.selected_nav_label = selected_nav_html_label; nav = ""
    for key_nav_map, html_label_nav_map in nav_options_with_icons.items():
        if html_label_nav_map == selected_nav_html_label: nav = key_nav_map; break
    user_sidebar_info = USERS.get(current_user_auth["username"], {});
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]): st.image(user_sidebar_info["profile_photo"], width=100)
    elif PILLOW_INSTALLED: st.caption("Profile photo missing.")
    st.markdown( f"<p style='text-align:center; font-size:0.9em; color: var(--text-muted-color);'>{user_sidebar_info.get('position', 'N/A')}</p>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔒 Logout", key="logout_button_sidebar_final_key_v4", use_container_width=True):
        for key_to_reset_logout in default_session_state:
            if key_to_reset_logout == "auth": st.session_state[key_to_reset_logout] = {"logged_in": False, "username": None, "role": None}
            elif key_to_reset_logout in st.session_state: st.session_state[key_to_reset_logout] = default_session_state[key_to_reset_logout]
        st.session_state.user_message = "Logged out successfully."; st.session_state.message_type = "info"; st.rerun()

# --- Helper display functions ---
def display_activity_logs_section(df_logs_act_func, user_header_name_act_func):
    if df_logs_act_func.empty: st.info(f"No field activity logs found for {user_header_name_act_func}.", icon="📭"); return
    df_logs_act_sorted_func = df_logs_act_func.copy()
    df_logs_act_sorted_func['Timestamp'] = pd.to_datetime(df_logs_act_sorted_func['Timestamp'], errors='coerce')
    df_logs_act_sorted_func = df_logs_act_sorted_func.sort_values(by="Timestamp", ascending=False)
    for index_act_func, row_act_func in df_logs_act_sorted_func.iterrows():
        st.divider(); col_details_act_f, col_photo_act_f = st.columns([0.7, 0.3])
        with col_details_act_f:
            ts_disp_act_f = row_act_func['Timestamp'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row_act_func['Timestamp']) else 'N/A'
            loc_disp_act_f = 'Not Recorded' if pd.isna(row_act_func.get('Latitude')) or pd.isna(row_act_func.get('Longitude')) else f"Lat: {row_act_func.get('Latitude'):.4f}, Lon: {row_act_func.get('Longitude'):.4f}"
            st.markdown(f"**Timestamp:** {ts_disp_act_f}<br>**Description:** {row_act_func.get('Description', 'N/A')}<br>**Location:** {loc_disp_act_f}", unsafe_allow_html=True)
            if pd.notna(row_act_func.get('ImageFile')) and row_act_func.get('ImageFile') != "": st.caption(f"Photo: {row_act_func['ImageFile']}")
            else: st.caption("No photo.")
        with col_photo_act_f:
            if pd.notna(row_act_func.get('ImageFile')) and row_act_func.get('ImageFile') != "":
                img_path_disp_act_f = os.path.join(ACTIVITY_PHOTOS_DIR, str(row_act_func['ImageFile']))
                if os.path.exists(img_path_disp_act_f):
                    try: st.image(img_path_disp_act_f, width=150, caption=f"Activity Photo")
                    except Exception as img_e_act_f: st.warning(f"Img err: {img_e_act_f}", icon="⚠️")
                else: st.caption(f"Img file missing.")

def display_general_attendance_logs_section(df_logs_att_func, user_header_name_att_func):
    if df_logs_att_func.empty: st.info(f"No general attendance records for {user_header_name_att_func}.", icon="📭"); return
    df_logs_att_sorted_func = df_logs_att_func.copy()
    df_logs_att_sorted_func['Timestamp'] = pd.to_datetime(df_logs_att_sorted_func['Timestamp'], errors='coerce')
    df_logs_att_sorted_func = df_logs_att_sorted_func.sort_values(by="Timestamp", ascending=False)
    cols_to_show_att_f = ["Type", "Timestamp"]
    if 'Latitude' in df_logs_att_sorted_func.columns and 'Longitude' in df_logs_att_sorted_func.columns:
        df_logs_att_sorted_func['Location (Illustrative)'] = df_logs_att_sorted_func.apply(lambda r: f"{r['Latitude']:.4f}, {r['Longitude']:.4f}" if pd.notna(r['Latitude']) and pd.notna(r['Longitude']) else "NR", axis=1)
        cols_to_show_att_f.append('Location (Illustrative)')
    st.dataframe(df_logs_att_sorted_func[cols_to_show_att_f].reset_index(drop=True), use_container_width=True, hide_index=True, column_config={"Timestamp":st.column_config.DatetimeColumn("Timestamp",format="YYYY-MM-DD HH:mm:ss")})

# --- Main Content Logic ---
# (The entire if/elif/else block for pages will go here, starting with "Dashboard")
# (Make sure to use the updated variable names and logic for "Create Order" as shown previously)

if nav == "Dashboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>dashboard</span> Dashboard</h3>", unsafe_allow_html=True)
    st.write(f"Welcome to the Dashboard, {current_user_auth['username']}!")
    st.info("Dashboard content will be role-specific and show key metrics and summaries.", icon="📊")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Create Order" and current_user_auth['role'] == 'sales_person':
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>add_shopping_cart</span> Create New Sales Order</h3>", unsafe_allow_html=True)
    order_date_display_co = get_current_time_in_tz().strftime("%Y-%m-%d"); salesperson_name_display_co = current_user_auth["username"]
    st.markdown("<h4>Order Header</h4>", unsafe_allow_html=True)
    col_header1_co, col_header2_co = st.columns(2)
    with col_header1_co:
        st.text_input("Order Date", value=order_date_display_co, disabled=True, key="co_form_date_key_v4")
        st.text_input("Salesperson", value=salesperson_name_display_co, disabled=True, key="co_form_salesperson_key_v4")
    with col_header2_co:
        if stores_df.empty:
            st.warning("No stores in `agri_stores.csv`. Store selection is mandatory.", icon="🏬"); st.session_state.order_store_select = None
        else:
            store_options_dict_co = {row['StoreID']: f"{row['StoreName']} ({row['StoreID']})" for index, row in stores_df.iterrows()}
            current_store_sel_co = st.session_state.order_store_select
            options_for_sb_co = [None] + list(store_options_dict_co.keys())
            current_idx_sb_co = 0
            if current_store_sel_co in store_options_dict_co: current_idx_sb_co = options_for_sb_co.index(current_store_sel_co)
            selected_store_id_co = st.selectbox("Select Store *", options=options_for_sb_co, format_func=lambda x: "Select a store..." if x is None else store_options_dict_co[x], key="co_store_select_sb_key_v4", index=current_idx_sb_co)
            st.session_state.order_store_select = selected_store_id_co
    st.markdown("---"); st.markdown("<h4><span class='material-symbols-outlined'>playlist_add</span> Add Products to Order</h4>", unsafe_allow_html=True)
    if products_df.empty: st.error("Product catalog `symplanta_products_with_images.csv` is empty or not found.", icon="🚫")
    else:
        categories_list_co = ["All Categories"] + sorted(products_df['Category'].unique().tolist())
        selected_category_filter_co = st.selectbox("Filter by Product Category", options=categories_list_co, key="co_prod_cat_filter_key_v4")
        filtered_products_co = products_df.copy()
        if selected_category_filter_co != "All Categories": filtered_products_co = products_df[products_df['Category'] == selected_category_filter_co]
        if filtered_products_co.empty: st.info(f"No products for category: {selected_category_filter_co}" if selected_category_filter_co != "All Categories" else "No products available.", icon="ℹ️"); product_variant_options_co = {} # Changed name
        else: product_variant_options_co = { row['ProductVariantID']: f"{row['ProductName']} ({row['UnitOfMeasure']}) - ₹{row['UnitPrice']:.2f}" for index, row in filtered_products_co.iterrows()}
        col_prod_co, col_qty_co, col_add_btn_co = st.columns([3, 1, 1.2])
        with col_prod_co:
            current_prod_variant_id_co_sess = st.session_state.current_product_id_symplanta; # Use ProductVariantID
            options_prod_sb_co_v4 = [None] + list(product_variant_options_co.keys()); current_prod_idx_sb_co_v4 = 0
            if current_prod_variant_id_co_sess in product_variant_options_co: current_prod_idx_sb_co_v4 = options_prod_sb_co_v4.index(current_prod_variant_id_co_sess)
            else: st.session_state.current_product_id_symplanta = None # Reset if not in filtered
            selected_prod_variant_id_co = st.selectbox("Select Product (Name & Size) *", options=options_prod_sb_co_v4, format_func=lambda x: "Choose a product..." if x is None else product_variant_options_co.get(x, "Invalid Product"), key="co_prod_variant_select_actual_key_v4", index=current_prod_idx_sb_co_v4)
            st.session_state.current_product_id_symplanta = selected_prod_variant_id_co # Store ProductVariantID
        with col_qty_co: st.session_state.current_quantity_order = st.number_input("Quantity *", min_value=1, value=st.session_state.current_quantity_order, step=1, key="co_qty_input_key_v4")
        def add_item_to_order_cb_co_v4():
            if st.session_state.current_product_id_symplanta and st.session_state.current_quantity_order > 0:
                prod_info_co_v4 = products_df[products_df['ProductVariantID'] == st.session_state.current_product_id_symplanta]
                if prod_info_co_v4.empty: st.error("Selected product not found.", icon="❌"); return
                prod_info_co_v4 = prod_info_co_v4.iloc[0]
                existing_item_idx_co_v4 = next((i for i, item in enumerate(st.session_state.order_line_items) if item['ProductVariantID'] == st.session_state.current_product_id_symplanta), -1)
                if existing_item_idx_co_v4 != -1:
                    st.session_state.order_line_items[existing_item_idx_co_v4]['Quantity'] += st.session_state.current_quantity_order
                    st.session_state.order_line_items[existing_item_idx_co_v4]['LineTotal'] = st.session_state.order_line_items[existing_item_idx_co_v4]['Quantity'] * st.session_state.order_line_items[existing_item_idx_co_v4]['UnitPrice']
                    st.toast(f"Updated quantity for {prod_info_co_v4['ProductName']} ({prod_info_co_v4['UnitOfMeasure']}).", icon="🔄")
                else:
                    st.session_state.order_line_items.append({"ProductVariantID": prod_info_co_v4['ProductVariantID'], "SKU": prod_info_co_v4['SKU'], "ProductName": prod_info_co_v4['ProductName'], "Quantity": st.session_state.current_quantity_order, "UnitOfMeasure": prod_info_co_v4['UnitOfMeasure'], "UnitPrice": float(prod_info_co_v4['UnitPrice']), "LineTotal": st.session_state.current_quantity_order * float(prod_info_co_v4['UnitPrice']), "ImageURL": prod_info_co_v4['ImageURL']})
                    st.toast(f"Added {prod_info_co_v4['ProductName']} ({prod_info_co_v4['UnitOfMeasure']}) to order.", icon="✅")
                st.session_state.current_quantity_order = 1
            else: st.warning("Please select a product and specify quantity > 0.", icon="⚠️")
        with col_add_btn_co: st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True); st.button("➕ Add to Order", on_click=add_item_to_order_cb_co_v4, key="co_add_item_btn_key_v4")
    if st.session_state.order_line_items:
        st.markdown("---"); st.markdown("<h4><span class='material-symbols-outlined'>receipt_long</span> Current Order Items</h4>", unsafe_allow_html=True)
        for i_item_co_v4, item_data_co_v4 in enumerate(st.session_state.order_line_items):
            item_cols_co_v4 = st.columns([1, 3, 1, 1.5, 1.5, 0.5])
            with item_cols_co_v4[0]:
                if item_data_co_v4.get("ImageURL") and isinstance(item_data_co_v4.get("ImageURL"), str) and item_data_co_v4.get("ImageURL").startswith("http"): st.image(item_data_co_v4["ImageURL"], width=50)
                else: st.markdown("<span class='material-symbols-outlined' style='font-size:36px; color: var(--gg-grey-300);'>image_not_supported</span>", unsafe_allow_html=True)
            item_cols_co_v4[1].markdown(f"**{item_data_co_v4['ProductName']}** ({item_data_co_v4['SKU']}) <br><small>{item_data_co_v4['UnitOfMeasure']}</small>", unsafe_allow_html=True)
            item_cols_co_v4[2].markdown(f"{item_data_co_v4['Quantity']}"); item_cols_co_v4[3].markdown(f"₹{item_data_co_v4['UnitPrice']:.2f}"); item_cols_co_v4[4].markdown(f"**₹{item_data_co_v4['LineTotal']:.2f}**")
            if item_cols_co_v4[5].button("➖", key=f"co_delete_item_key_v4_{i_item_co_v4}", help="Remove item"): st.session_state.order_line_items.pop(i_item_co_v4); st.rerun()
            if i_item_co_v4 < len(st.session_state.order_line_items) -1 : st.divider()
        subtotal_co_v4 = sum(item['LineTotal'] for item in st.session_state.order_line_items)
        col_summary1_co_v4, col_summary2_co_v4 = st.columns(2)
        with col_summary1_co_v4:
            st.session_state.order_discount = st.number_input("Discount (₹)", value=st.session_state.order_discount, min_value=0.0, step=10.0, key="co_discount_val_key_v4")
            st.session_state.order_tax = st.number_input("Tax (₹)", value=st.session_state.order_tax, min_value=0.0, step=5.0, key="co_tax_val_key_v4", help="Total tax amount")
        grand_total_co_v4 = subtotal_co_v4 - st.session_state.order_discount + st.session_state.order_tax
        with col_summary2_co_v4: st.markdown(f"<div style='text-align:right; margin-top:20px;'><p style='margin-bottom:2px;'>Subtotal:  <strong>₹{subtotal_co_v4:,.2f}</strong></p><p style='margin-bottom:2px;color:var(--danger-color);'>Discount:  - ₹{st.session_state.order_discount:,.2f}</p><p style='margin-bottom:2px;'>Tax:  + ₹{st.session_state.order_tax:,.2f}</p><h4 style='margin-top:5px;border-top:1px solid var(--border-color);padding-top:5px;'>Grand Total:  ₹{grand_total_co_v4:,.2f}</h4></div>", unsafe_allow_html=True)
        st.session_state.order_notes = st.text_area("Order Notes/Payment/Delivery", value=st.session_state.order_notes, key="co_notes_val_key_v4", placeholder="E.g., UPI, Deliver by Tuesday")
        if st.button("✅ Submit Order", key="co_submit_order_btn_key_v4", type="primary", use_container_width=True):
            final_store_id_co_v4 = st.session_state.order_store_select; store_name_co_v4 = "N/A"
            if not final_store_id_co_v4: st.error("Store selection is mandatory.", icon="🏬")
            elif not st.session_state.order_line_items: st.error("Cannot submit an empty order.", icon="🛒")
            else:
                store_info_co_v4 = stores_df[stores_df['StoreID'] == final_store_id_co_v4]
                if not store_info_co_v4.empty: store_name_co_v4 = store_info_co_v4['StoreName'].iloc[0]
                else: st.error("Selected store details not found.", icon="❌"); st.stop()
                global orders_df, order_summary_df
                new_order_id_co_v4 = generate_order_id(); order_date_co_submit_v4 = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
                new_items_list_co_v4 = [{"OrderID":new_order_id_co_v4, "OrderDate":order_date_co_submit_v4, "Salesperson":salesperson_name_display_co, "StoreID":final_store_id_co_v4, "ProductVariantID":item_v4['ProductVariantID'], "SKU":item_v4['SKU'], "ProductName":item_v4['ProductName'], "Quantity":item_v4['Quantity'], "UnitOfMeasure":item_v4['UnitOfMeasure'], "UnitPrice":item_v4['UnitPrice'], "LineTotal":item_v4['LineTotal']} for item_v4 in st.session_state.order_line_items]
                new_orders_df_co_v4 = pd.DataFrame(new_items_list_co_v4, columns=ORDERS_COLUMNS); temp_orders_df_co_v4 = pd.concat([orders_df, new_orders_df_co_v4], ignore_index=True)
                summary_data_co_v4 = {"OrderID":new_order_id_co_v4, "OrderDate":order_date_co_submit_v4, "Salesperson":salesperson_name_display_co, "StoreID":final_store_id_co_v4, "StoreName":store_name_co_v4, "Subtotal":subtotal_co_v4, "DiscountAmount":st.session_state.order_discount, "TaxAmount":st.session_state.order_tax, "GrandTotal":grand_total_co_v4, "Notes":st.session_state.order_notes.strip(), "PaymentMode":pd.NA, "ExpectedDeliveryDate":pd.NA}
                new_summary_df_co_v4 = pd.DataFrame([summary_data_co_v4], columns=ORDER_SUMMARY_COLUMNS); temp_summary_df_co_v4 = pd.concat([order_summary_df, new_summary_df_co_v4], ignore_index=True)
                try:
                    temp_orders_df_co_v4.to_csv(ORDERS_FILE, index=False); temp_summary_df_co_v4.to_csv(ORDER_SUMMARY_FILE, index=False)
                    orders_df = temp_orders_df_co_v4; order_summary_df = temp_summary_df_co_v4
                    st.session_state.user_message = f"Order {new_order_id_co_v4} for '{store_name_co_v4}' submitted!"; st.session_state.message_type = "success"
                    st.session_state.order_line_items = []; st.session_state.current_product_id_symplanta = None; st.session_state.current_quantity_order = 1; st.session_state.order_store_select = None; st.session_state.order_notes = ""; st.session_state.order_discount = 0.0; st.session_state.order_tax = 0.0
                    st.rerun()
                except Exception as e_co_submit_v4: st.session_state.user_message = f"Error submitting order: {e_co_submit_v4}"; st.session_state.message_type = "error"; st.rerun()
    else: st.markdown("<br>", unsafe_allow_html=True); st.info("Add products to the order to see summary and submit.", icon="💡")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>event_available</span> Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services for general attendance are currently illustrative.", icon="ℹ️")
    st.markdown("---"); st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col_att1_std_v4, col_att2_std_v4 = st.columns(2)
    common_data_att_std_v4 = {"Username": current_user_auth["username"], "Latitude": pd.NA, "Longitude": pd.NA}
    def process_general_attendance_cb_std_v4(attendance_type_param_std_v4):
        global attendance_df
        now_str_att_std_v4 = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_att_std_v4 = {"Type": attendance_type_param_std_v4, "Timestamp": now_str_att_std_v4, **common_data_att_std_v4}
        for col_att_std_v4 in ATTENDANCE_COLUMNS:
            if col_att_std_v4 not in new_entry_att_std_v4: new_entry_att_std_v4[col_att_std_v4] = pd.NA
        new_df_att_std_v4 = pd.DataFrame([new_entry_att_std_v4], columns=ATTENDANCE_COLUMNS)
        temp_df_att_std_v4 = pd.concat([attendance_df, new_df_att_std_v4], ignore_index=True)
        try:
            temp_df_att_std_v4.to_csv(ATTENDANCE_FILE, index=False); attendance_df = temp_df_att_std_v4
            st.session_state.user_message = f"{attendance_type_param_std_v4} recorded."; st.session_state.message_type = "success"; st.rerun()
        except Exception as e_att_std_v4: st.session_state.user_message = f"Error: {e_att_std_v4}"; st.session_state.message_type = "error"; st.rerun()
    with col_att1_std_v4:
        if st.button("✅ Check In", key="att_checkin_btn_v4", use_container_width=True, on_click=process_general_attendance_cb_std_v4, args=("Check-In",)): pass
    with col_att2_std_v4:
        if st.button("🚪 Check Out", key="att_checkout_btn_v4", use_container_width=True, on_click=process_general_attendance_cb_std_v4, args=("Check-Out",)): pass
    st.markdown('</div></div>', unsafe_allow_html=True)

elif nav == "Upload Activity":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>cloud_upload</span> Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    lat_act_std_v4, lon_act_std_v4 = pd.NA, pd.NA
    with st.form(key="act_photo_form_std_v4"):
        st.markdown("<h6><span class='material-symbols-outlined'>description</span> Describe Activity:</h6>", unsafe_allow_html=True)
        desc_act_std_v4 = st.text_area("Description:", key="act_desc_std_v4", help="E.g., Met Client X, Demoed Product Y.")
        st.markdown("<h6><span class='material-symbols-outlined'>photo_camera</span> Capture Photo:</h6>", unsafe_allow_html=True)
        img_buf_act_std_v4 = st.camera_input("Take picture:", key="act_cam_std_v4", help="Photo provides context.")
        submit_act_std_v4 = st.form_submit_button("⬆️ Upload & Log", type="primary")
    if submit_act_std_v4:
        if img_buf_act_std_v4 is None: st.warning("Please take a picture.", icon="📸")
        elif not desc_act_std_v4.strip(): st.warning("Please provide a description.", icon="✏️")
        else:
            global activity_log_df
            now_fname_act_std_v4 = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S"); now_disp_act_std_v4 = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            img_fname_act_std_v4 = f"{current_user_auth['username']}_activity_{now_fname_act_std_v4}.jpg"; img_path_act_std_v4 = os.path.join(ACTIVITY_PHOTOS_DIR, img_fname_act_std_v4)
            try:
                with open(img_path_act_std_v4, "wb") as f_act_std_v4: f_act_std_v4.write(img_buf_act_std_v4.getbuffer())
                new_data_act_std_v4 = {"Username":current_user_auth["username"], "Timestamp":now_disp_act_std_v4, "Description":desc_act_std_v4, "ImageFile":img_fname_act_std_v4, "Latitude":lat_act_std_v4, "Longitude":lon_act_std_v4}
                for col_act_std_v4 in ACTIVITY_LOG_COLUMNS:
                    if col_act_std_v4 not in new_data_act_std_v4: new_data_act_std_v4[col_act_std_v4] = pd.NA
                new_entry_act_std_v4 = pd.DataFrame([new_data_act_std_v4], columns=ACTIVITY_LOG_COLUMNS)
                temp_df_act_std_v4 = pd.concat([activity_log_df, new_entry_act_std_v4], ignore_index=True)
                temp_df_act_std_v4.to_csv(ACTIVITY_LOG_FILE, index=False); activity_log_df = temp_df_act_std_v4
                st.session_state.user_message = "Activity logged successfully!"; st.session_state.message_type = "success"; st.rerun()
            except Exception as e_act_std_save_v4: st.session_state.user_message = f"Error: {e_act_std_save_v4}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>receipt_long</span> Claim Allowance</h3>", unsafe_allow_html=True)
    st.markdown("<div class='form-field-label'><h6>Select Allowance Type:</h6></div>", unsafe_allow_html=True)
    type_allow_std_v4 = st.radio("AllowTypeRadioStdV4", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allow_type_std_v4", horizontal=True, label_visibility='collapsed')
    amt_allow_std_v4 = st.number_input("Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allow_amt_std_v4")
    reason_allow_std_v4 = st.text_area("Reason:", key="allow_reason_std_v4", placeholder="Justification for claim...")
    if st.button("Submit Claim", key="allow_submit_std_v4", type="primary", use_container_width=True):
        if type_allow_std_v4 and amt_allow_std_v4 > 0 and reason_allow_std_v4.strip():
            global allowance_df
            date_allow_std_v4 = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_data_allow_std_v4 = {"Username":current_user_auth["username"], "Type":type_allow_std_v4, "Amount":amt_allow_std_v4, "Reason":reason_allow_std_v4, "Date":date_allow_std_v4}
            for col_allow_std_v4 in ALLOWANCE_COLUMNS:
                if col_allow_std_v4 not in new_data_allow_std_v4: new_data_allow_std_v4[col_allow_std_v4] = pd.NA
            new_entry_allow_std_v4 = pd.DataFrame([new_data_allow_std_v4], columns=ALLOWANCE_COLUMNS)
            temp_df_allow_std_v4 = pd.concat([allowance_df, new_entry_allow_std_v4], ignore_index=True)
            try:
                temp_df_allow_std_v4.to_csv(ALLOWANCE_FILE, index=False); allowance_df = temp_df_allow_std_v4
                st.session_state.user_message = f"Allowance claim submitted."; st.session_state.message_type = "success"; st.rerun()
            except Exception as e_allow_std_save_v4: st.session_state.user_message = f"Error: {e_allow_std_save_v4}"; st.session_state.message_type = "error"; st.rerun()
        else: st.warning("Please complete all fields for allowance claim.", icon="⚠️")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "Sales Goals":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>flag</span> Sales Goal Tracker (2025)</h3>", unsafe_allow_html=True)
    TARGET_SG_YEAR_V4 = 2025; current_q_sg_v4 = get_quarter_str_for_year(TARGET_SG_YEAR_V4); status_opts_sg_v4 = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    if current_user_auth["role"] == "admin":
        st.markdown("<h4>Admin: Manage Employee Sales Goals</h4>", unsafe_allow_html=True)
        admin_action_sg_v4 = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal"], key="admin_sg_action_v4", horizontal=True)
        if admin_action_sg_v4 == "View Team Progress":
            st.markdown(f"<h5>Team Progress for {current_q_sg_v4}</h5>", unsafe_allow_html=True)
            emp_list_sg_admin_v4 = [u for u,d in USERS.items() if d["role"] in ["employee","sales_person"]]
            if not emp_list_sg_admin_v4: st.info("No employees/salespersons.")
            else:
                summary_data_sg_admin_v4 = []
                for name_sg_v4 in emp_list_sg_admin_v4:
                    goal_data_sg_v4 = goals_df[(goals_df["Username"]==name_sg_v4)&(goals_df["MonthYear"]==current_q_sg_v4)]
                    data_to_append_sg_v4 = {"Employee":name_sg_v4, "TargetAmount":0.0, "AchievedAmount":0.0, "Status":"Not Set"}
                    if not goal_data_sg_v4.empty:
                        data_row_sg_v4 = goal_data_sg_v4.iloc[0]
                        data_to_append_sg_v4["TargetAmount"]=float(pd.to_numeric(data_row_sg_v4.get("TargetAmount"),errors='coerce').fillna(0.0))
                        data_to_append_sg_v4["AchievedAmount"]=float(pd.to_numeric(data_row_sg_v4.get("AchievedAmount"),errors='coerce').fillna(0.0))
                        data_to_append_sg_v4["Status"]=data_row_sg_v4.get("Status","Not Set")
                    summary_data_sg_admin_v4.append(data_to_append_sg_v4)
                summary_df_sg_admin_v4 = pd.DataFrame(summary_data_sg_admin_v4)
                if not summary_df_sg_admin_v4.empty:
                    st.markdown("<h6>Individual Progress:</h6>", unsafe_allow_html=True)
                    cols_sg_admin_v4 = st.columns(min(3, len(summary_df_sg_admin_v4)) if len(summary_df_sg_admin_v4)>0 else 1)
                    for i_sg_admin_v4, row_sg_admin_v4 in summary_df_sg_admin_v4.iterrows():
                        target_sg_admin_val_v4 = float(pd.to_numeric(row_sg_admin_v4.get('TargetAmount'), errors='coerce').fillna(0.0))
                        achieved_sg_admin_val_v4 = float(pd.to_numeric(row_sg_admin_v4.get('AchievedAmount'), errors='coerce').fillna(0.0))
                        prog_sg_admin_v4 = (achieved_sg_admin_val_v4/target_sg_admin_val_v4*100) if target_sg_admin_val_v4>0 else 0
                        donut_sg_admin_v4 = create_donut_chart(prog_sg_admin_v4);
                        with cols_sg_admin_v4[i_sg_admin_v4 % len(cols_sg_admin_v4)]:
                            st.markdown(f"<div class='employee-progress-item'><h6>{row_sg_admin_v4['Employee']}</h6><p>T: ₹{target_sg_admin_val_v4:,.0f} | A: ₹{achieved_sg_admin_val_v4:,.0f}</p></div>", unsafe_allow_html=True)
                            if donut_sg_admin_v4: st.pyplot(donut_sg_admin_v4, use_container_width=True); st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
                    st.markdown("<hr>"); st.markdown("<h6>Overall Team Performance:</h6>", unsafe_allow_html=True)
                    bar_sg_admin_v4 = create_team_progress_bar_chart(summary_df_sg_admin_v4, title="Team Sales: Target vs Achieved", target_col="TargetAmount", achieved_col="AchievedAmount")
                    if bar_sg_admin_v4: st.pyplot(bar_sg_admin_v4, use_container_width=True)
                    else: st.info("No data for team bar chart.")
                else: st.info(f"No sales goals data for {current_q_sg_v4}.")
        else: # Set/Edit Goal
            st.markdown(f"<h5>Set/Update Sales Goal ({TARGET_SG_YEAR_V4} - Quarterly)</h5>", unsafe_allow_html=True)
            emp_opts_sg_set_v4 = [u for u,d in USERS.items() if d["role"] in ["employee","sales_person"]]
            if not emp_opts_sg_set_v4: st.warning("No employees available.")
            else:
                sel_emp_sg_set_v4 = st.radio("Employee:", emp_opts_sg_set_v4, key="sg_set_emp_v4", horizontal=True)
                sel_q_sg_set_v4 = st.radio("Quarter:", [f"{TARGET_SG_YEAR_V4}-Q{i}" for i in range(1,5)], key="sg_set_q_v4", horizontal=True)
                existing_goal_sg_v4 = goals_df[(goals_df["Username"]==sel_emp_sg_set_v4)&(goals_df["MonthYear"]==sel_q_sg_set_v4)]
                desc_sg_v4, tgt_sg_v4, ach_sg_v4, stat_sg_v4 = ("",0.0,0.0,"Not Started")
                if not existing_goal_sg_v4.empty:
                    data_sg_v4 = existing_goal_sg_v4.iloc[0]; desc_sg_v4=data_sg_v4.get("GoalDescription",""); tgt_sg_v4=float(pd.to_numeric(data_sg_v4.get("TargetAmount",0.0),errors='coerce').fillna(0.0)); ach_sg_v4=float(pd.to_numeric(data_sg_v4.get("AchievedAmount",0.0),errors='coerce').fillna(0.0)); stat_sg_v4=data_sg_v4.get("Status","Not Started")
                    st.info(f"Editing goal for {sel_emp_sg_set_v4} - {sel_q_sg_set_v4}")
                with st.form(f"form_sg_set_{sel_emp_sg_set_v4}_{sel_q_sg_set_v4}_v4"):
                    n_desc_v4=st.text_area("Desc:",value=desc_sg_v4, key=f"desc_sg_v4_{sel_emp_sg_set_v4}_{sel_q_sg_set_v4}"); n_tgt_v4=st.number_input("Target:",value=tgt_sg_v4,min_value=0.0,step=1000.0,format="%.2f", key=f"tgt_sg_v4_{sel_emp_sg_set_v4}_{sel_q_sg_set_v4}")
                    n_ach_v4=st.number_input("Achieved:",value=ach_sg_v4,min_value=0.0,step=100.0,format="%.2f", key=f"ach_sg_v4_{sel_emp_sg_set_v4}_{sel_q_sg_set_v4}"); n_stat_v4=st.radio("Status:",status_opts_sg_v4,index=status_opts_sg_v4.index(stat_sg_v4),horizontal=True, key=f"stat_sg_v4_{sel_emp_sg_set_v4}_{sel_q_sg_set_v4}")
                    submit_sg_set_v4=st.form_submit_button("Save Goal", type="primary")
                if submit_sg_set_v4:
                    if not n_desc_v4.strip():st.warning("Desc required."); 
                    elif n_tgt_v4<=0 and n_stat_v4 not in ["Cancelled","On Hold","Not Started"]: st.warning("Target >0 unless status is Cancelled/On Hold/Not Started.")
                    else:
                        global goals_df
                        df_edit_v4=goals_df.copy(); idx_v4=df_edit_v4[(df_edit_v4["Username"]==sel_emp_sg_set_v4)&(df_edit_v4["MonthYear"]==sel_q_sg_set_v4)].index
                        data_save_v4={"Username":sel_emp_sg_set_v4,"MonthYear":sel_q_sg_set_v4,"GoalDescription":n_desc_v4,"TargetAmount":n_tgt_v4,"AchievedAmount":n_ach_v4,"Status":n_stat_v4}
                        for col_check_v4 in GOALS_COLUMNS:
                            if col_check_v4 not in data_save_v4: data_save_v4[col_check_v4]=pd.NA
                        if not idx_v4.empty: df_edit_v4.loc[idx_v4[0]]=pd.Series(data_save_v4); verb_v4="updated"
                        else: df_new_v4=pd.DataFrame([data_save_v4],columns=GOALS_COLUMNS); df_edit_v4=pd.concat([df_edit_v4,df_new_v4],ignore_index=True); verb_v4="set"
                        try: df_edit_v4.to_csv(GOALS_FILE,index=False); goals_df=df_edit_v4; st.session_state.user_message=f"Goal {verb_v4}!"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e_sg_save_v4: st.session_state.user_message=f"Error: {e_sg_save_v4}"; st.session_state.message_type="error"; st.rerun()
    elif current_user_auth["role"] in ["sales_person", "employee"]:
        st.markdown(f"<h4>My Sales Goals ({TARGET_SG_YEAR_V4})</h4>", unsafe_allow_html=True)
        my_goals_sg_v4 = goals_df[goals_df["Username"]==current_user_auth["username"]].copy()
        for col_num_v4 in ["TargetAmount","AchievedAmount"]: my_goals_sg_v4[col_num_v4]=pd.to_numeric(my_goals_sg_v4[col_num_v4],errors="coerce").fillna(0.0)
        current_g_sg_v4 = my_goals_sg_v4[my_goals_sg_v4["MonthYear"]==current_q_sg_v4]
        st.markdown(f"<h5>Current: {current_q_sg_v4}</h5>", unsafe_allow_html=True)
        if not current_g_sg_v4.empty:
            g_data_v4 = current_g_sg_v4.iloc[0]; tgt_v4=g_data_v4["TargetAmount"]; ach_v4=g_data_v4["AchievedAmount"]
            st.markdown(f"**Desc:** {g_data_v4.get('GoalDescription','N/A')}")
            m_cols_v4,c_cols_v4=st.columns([0.6,0.4]);
            with m_cols_v4: s1_v4,s2_v4=st.columns(2);s1_v4.metric("Target",f"₹{tgt_v4:,.0f}");s2_v4.metric("Achieved",f"₹{ach_v4:,.0f}");st.metric("Status",g_data_v4.get("Status","In Progress"),label_visibility="visible")
            with c_cols_v4: prog_v4=(ach_v4/tgt_v4*100)if tgt_v4>0 else 0;st.markdown("<h6 style='text-align:center;margin:0;'>Progress</h6>",unsafe_allow_html=True);d_fig_v4=create_donut_chart(prog_v4);st.pyplot(d_fig_v4,use_container_width=True)
            st.markdown("---")
            if current_user_auth["role"] == "sales_person":
                with st.form(f"form_upd_sg_{current_user_auth['username']}_{current_q_sg_v4}_v4"):
                    n_val_v4=st.number_input("Update Achieved (INR):",value=ach_v4,min_value=0.0,step=100.0,format="%.2f")
                    submit_upd_v4=st.form_submit_button("Update Achievement", type="primary")
                if submit_upd_v4:
                    global goals_df
                    df_edit_u_v4=goals_df.copy();idx_u_v4=df_edit_u_v4[(df_edit_u_v4["Username"]==current_user_auth["username"])&(df_edit_u_v4["MonthYear"]==current_q_sg_v4)].index
                    if not idx_u_v4.empty:
                        df_edit_u_v4.loc[idx_u_v4[0],"AchievedAmount"]=n_val_v4;df_edit_u_v4.loc[idx_u_v4[0],"Status"]="Achieved" if n_val_v4>=tgt_v4 and tgt_v4>0 else "In Progress"
                        try: df_edit_u_v4.to_csv(GOALS_FILE,index=False);goals_df=df_edit_u_v4;st.session_state.user_message="Achievement updated!";st.session_state.message_type="success";st.rerun()
                        except Exception as e_u_save_v4:st.session_state.user_message=f"Error: {e_u_save_v4}";st.session_state.message_type="error";st.rerun()
                    else: st.session_state.user_message="Goal not found.";st.session_state.message_type="error";st.rerun()
        else: st.info(f"No goal for {current_q_sg_v4}. Contact admin.")
        st.markdown(f"---");st.markdown(f"<h5>Past Goals ({TARGET_SG_YEAR_V4})</h5>",unsafe_allow_html=True)
        past_g_sg_v4=my_goals_sg_v4[(my_goals_sg_v4["MonthYear"].str.startswith(str(TARGET_SG_YEAR_V4)))&(my_goals_sg_v4["MonthYear"]!=current_q_sg_v4)]
        if not past_g_sg_v4.empty:render_goal_chart(past_g_sg_v4,"My Past Sales Goals")
        else: st.info(f"No past goals for {TARGET_SG_YEAR_V4}.")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Payment Collection":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>payments</span> Payment Collection Tracker (2025)</h3>", unsafe_allow_html=True)
    TARGET_PAY_YEAR_V4 = 2025; current_q_pay_v4 = get_quarter_str_for_year(TARGET_PAY_YEAR_V4); status_opts_pay_v4 = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    if current_user_auth["role"] == "admin":
        st.markdown("<h4>Admin: Manage Employee Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action_pay_v4 = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal"], key="admin_pay_action_v4", horizontal=True)
        if admin_action_pay_v4 == "View Team Progress":
            st.markdown(f"<h5>Team Progress for {current_q_pay_v4}</h5>", unsafe_allow_html=True)
            emp_list_pay_admin_v4 = [u for u,d in USERS.items() if d["role"] in ["employee","sales_person"]]
            if not emp_list_pay_admin_v4: st.info("No employees/salespersons.")
            else:
                summary_data_pay_admin_v4 = []
                for name_pay_v4 in emp_list_pay_admin_v4:
                    goal_data_pay_v4 = payment_goals_df[(payment_goals_df["Username"]==name_pay_v4)&(payment_goals_df["MonthYear"]==current_q_pay_v4)]
                    data_to_append_pay_v4 = {"Employee":name_pay_v4, "TargetAmount":0.0, "AchievedAmount":0.0, "Status":"Not Set"}
                    if not goal_data_pay_v4.empty:
                        data_row_pay_v4 = goal_data_pay_v4.iloc[0]
                        data_to_append_pay_v4["TargetAmount"]=float(pd.to_numeric(data_row_pay_v4.get("TargetAmount"),errors='coerce').fillna(0.0))
                        data_to_append_pay_v4["AchievedAmount"]=float(pd.to_numeric(data_row_pay_v4.get("AchievedAmount"),errors='coerce').fillna(0.0))
                        data_to_append_pay_v4["Status"]=data_row_pay_v4.get("Status","Not Set")
                    summary_data_pay_admin_v4.append(data_to_append_pay_v4)
                summary_df_pay_admin_v4 = pd.DataFrame(summary_data_pay_admin_v4)
                if not summary_df_pay_admin_v4.empty:
                    st.markdown("<h6>Individual Progress:</h6>", unsafe_allow_html=True)
                    cols_pay_admin_v4 = st.columns(min(3, len(summary_df_pay_admin_v4)) if len(summary_df_pay_admin_v4)>0 else 1)
                    for i_pay_admin_v4, row_pay_admin_v4 in summary_df_pay_admin_v4.iterrows():
                        target_pay_admin_val_v4 = float(pd.to_numeric(row_pay_admin_v4.get('TargetAmount'), errors='coerce').fillna(0.0))
                        achieved_pay_admin_val_v4 = float(pd.to_numeric(row_pay_admin_v4.get('AchievedAmount'), errors='coerce').fillna(0.0))
                        prog_pay_admin_v4 = (achieved_pay_admin_val_v4/target_pay_admin_val_v4*100) if target_pay_admin_val_v4>0 else 0
                        donut_pay_admin_v4 = create_donut_chart(prog_pay_admin_v4, achieved_color='#2070c0');
                        with cols_pay_admin_v4[i_pay_admin_v4 % len(cols_pay_admin_v4)]:
                            st.markdown(f"<div class='employee-progress-item'><h6>{row_pay_admin_v4['Employee']}</h6><p>T: ₹{target_pay_admin_val_v4:,.0f} | Coll: ₹{achieved_pay_admin_val_v4:,.0f}</p></div>", unsafe_allow_html=True)
                            if donut_pay_admin_v4: st.pyplot(donut_pay_admin_v4, use_container_width=True); st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
                    st.markdown("<hr>"); st.markdown("<h6>Overall Team Performance:</h6>", unsafe_allow_html=True)
                    bar_pay_admin_v4 = create_team_progress_bar_chart(summary_df_pay_admin_v4, title="Team Collection: Target vs Achieved", target_col="TargetAmount", achieved_col="AchievedAmount")
                    if bar_pay_admin_v4: 
                        for bar_group_pay_v4 in bar_pay_admin_v4.axes[0].containers:
                            if bar_group_pay_v4.get_label()=='Achieved': 
                                for bar_v4 in bar_group_pay_v4: bar_v4.set_color('#2070c0')
                        st.pyplot(bar_pay_admin_v4, use_container_width=True)
                    else: st.info("No data for team bar chart.")
                else: st.info(f"No payment collection goals data for {current_q_pay_v4}.")
        else: # Set/Edit Goal
            st.markdown(f"<h5>Set/Update Collection Goal ({TARGET_PAY_YEAR_V4} - Quarterly)</h5>", unsafe_allow_html=True)
            emp_opts_pay_set_v4 = [u for u,d in USERS.items() if d["role"] in ["employee","sales_person"]]
            if not emp_opts_pay_set_v4: st.warning("No employees available.")
            else:
                sel_emp_pay_set_v4 = st.radio("Employee:", emp_opts_pay_set_v4, key="pay_set_emp_v4", horizontal=True)
                sel_q_pay_set_v4 = st.radio("Quarter:", [f"{TARGET_PAY_YEAR_V4}-Q{i}" for i in range(1,5)], key="pay_set_q_v4", horizontal=True)
                existing_goal_pay_v4 = payment_goals_df[(payment_goals_df["Username"]==sel_emp_pay_set_v4)&(payment_goals_df["MonthYear"]==sel_q_pay_set_v4)]
                desc_pay_v4, tgt_pay_v4, ach_pay_v4, stat_pay_v4 = ("",0.0,0.0,"Not Started")
                if not existing_goal_pay_v4.empty:
                    data_pay_v4 = existing_goal_pay_v4.iloc[0]; desc_pay_v4=data_pay_v4.get("GoalDescription",""); tgt_pay_v4=float(pd.to_numeric(data_pay_v4.get("TargetAmount",0.0),errors='coerce').fillna(0.0)); ach_pay_v4=float(pd.to_numeric(data_pay_v4.get("AchievedAmount",0.0),errors='coerce').fillna(0.0)); stat_pay_v4=data_pay_v4.get("Status","Not Started")
                    st.info(f"Editing goal for {sel_emp_pay_set_v4} - {sel_q_pay_set_v4}")
                with st.form(f"form_pay_set_{sel_emp_pay_set_v4}_{sel_q_pay_set_v4}_v4"):
                    n_desc_pay_v4=st.text_area("Desc:",value=desc_pay_v4, key=f"desc_pay_v4_{sel_emp_pay_set_v4}_{sel_q_pay_set_v4}"); n_tgt_pay_v4=st.number_input("Target:",value=tgt_pay_v4,min_value=0.0,step=1000.0,format="%.2f", key=f"tgt_pay_v4_{sel_emp_pay_set_v4}_{sel_q_pay_set_v4}")
                    n_ach_pay_v4=st.number_input("Achieved:",value=ach_pay_v4,min_value=0.0,step=100.0,format="%.2f", key=f"ach_pay_v4_{sel_emp_pay_set_v4}_{sel_q_pay_set_v4}"); n_stat_pay_v4=st.selectbox("Status:",status_opts_pay_v4,index=status_opts_pay_v4.index(stat_pay_v4), key=f"stat_pay_v4_{sel_emp_pay_set_v4}_{sel_q_pay_set_v4}")
                    submit_pay_set_v4=st.form_submit_button("Save Goal", type="primary")
                if submit_pay_set_v4:
                    if not n_desc_pay_v4.strip():st.warning("Desc required."); 
                    elif n_tgt_pay_v4<=0 and n_stat_pay_v4 not in ["Cancelled","On Hold","Not Started"]: st.warning("Target >0 unless status is Cancelled/On Hold/Not Started.")
                    else:
                        global payment_goals_df
                        df_edit_pay_v4=payment_goals_df.copy(); idx_pay_v4=df_edit_pay_v4[(df_edit_pay_v4["Username"]==sel_emp_pay_set_v4)&(df_edit_pay_v4["MonthYear"]==sel_q_pay_set_v4)].index
                        data_save_pay_v4={"Username":sel_emp_pay_set_v4,"MonthYear":sel_q_pay_set_v4,"GoalDescription":n_desc_pay_v4,"TargetAmount":n_tgt_pay_v4,"AchievedAmount":n_ach_pay_v4,"Status":n_stat_pay_v4}
                        for col_check_pay_v4 in PAYMENT_GOALS_COLUMNS:
                            if col_check_pay_v4 not in data_save_pay_v4: data_save_pay_v4[col_check_pay_v4]=pd.NA
                        if not idx_pay_v4.empty: df_edit_pay_v4.loc[idx_pay_v4[0]]=pd.Series(data_save_pay_v4); verb_pay_v4="updated"
                        else: df_new_pay_v4=pd.DataFrame([data_save_pay_v4],columns=PAYMENT_GOALS_COLUMNS); df_edit_pay_v4=pd.concat([df_edit_pay_v4,df_new_pay_v4],ignore_index=True); verb_pay_v4="set"
                        try: df_edit_pay_v4.to_csv(PAYMENT_GOALS_FILE,index=False); payment_goals_df=df_edit_pay_v4; st.session_state.user_message=f"Payment Goal {verb_pay_v4}!"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e_pay_save_v4: st.session_state.user_message=f"Error: {e_pay_save_v4}"; st.session_state.message_type="error"; st.rerun()
    elif current_user_auth["role"] in ["sales_person", "employee"]:
        st.markdown(f"<h4>My Payment Collection Goals ({TARGET_PAY_YEAR_V4})</h4>", unsafe_allow_html=True)
        my_goals_pay_v4 = payment_goals_df[payment_goals_df["Username"]==current_user_auth["username"]].copy()
        for col_num_pay_v4 in ["TargetAmount","AchievedAmount"]: my_goals_pay_v4[col_num_pay_v4]=pd.to_numeric(my_goals_pay_v4[col_num_pay_v4],errors="coerce").fillna(0.0)
        current_g_pay_v4 = my_goals_pay_v4[my_goals_pay_v4["MonthYear"]==current_q_pay_v4]
        st.markdown(f"<h5>Current: {current_q_pay_v4}</h5>", unsafe_allow_html=True)
        if not current_g_pay_v4.empty:
            g_data_pay_v4 = current_g_pay_v4.iloc[0]; tgt_pay_v4=g_data_pay_v4["TargetAmount"]; ach_pay_v4=g_data_pay_v4["AchievedAmount"]
            st.markdown(f"**Desc:** {g_data_pay_v4.get('GoalDescription','N/A')}")
            m_cols_pay_v4,c_cols_pay_v4=st.columns([0.6,0.4]);
            with m_cols_pay_v4: s1_pay_v4,s2_pay_v4=st.columns(2);s1_pay_v4.metric("Target",f"₹{tgt_pay_v4:,.0f}");s2_pay_v4.metric("Collected",f"₹{ach_pay_v4:,.0f}");st.metric("Status",g_data_pay_v4.get("Status","In Progress"),label_visibility="visible")
            with c_cols_pay_v4: prog_pay_v4=(ach_pay_v4/tgt_pay_v4*100)if tgt_pay_v4>0 else 0;st.markdown("<h6 style='text-align:center;margin:0;'>Progress</h6>",unsafe_allow_html=True);d_fig_pay_v4=create_donut_chart(prog_pay_v4, achieved_color='#2070c0');st.pyplot(d_fig_pay_v4,use_container_width=True)
            st.markdown("---")
            if current_user_auth["role"] == "sales_person":
                with st.form(f"form_upd_pay_{current_user_auth['username']}_{current_q_pay_v4}_v4"):
                    n_val_pay_v4=st.number_input("Update Collected (INR):",value=ach_pay_v4,min_value=0.0,step=100.0,format="%.2f")
                    submit_upd_pay_v4=st.form_submit_button("Update Collection", type="primary")
                if submit_upd_pay_v4:
                    global payment_goals_df
                    df_edit_u_pay_v4=payment_goals_df.copy();idx_u_pay_v4=df_edit_u_pay_v4[(df_edit_u_pay_v4["Username"]==current_user_auth["username"])&(df_edit_u_pay_v4["MonthYear"]==current_q_pay_v4)].index
                    if not idx_u_pay_v4.empty:
                        df_edit_u_pay_v4.loc[idx_u_pay_v4[0],"AchievedAmount"]=n_val_pay_v4;df_edit_u_pay_v4.loc[idx_u_pay_v4[0],"Status"]="Achieved" if n_val_pay_v4>=tgt_pay_v4 and tgt_pay_v4>0 else "In Progress"
                        try: df_edit_u_pay_v4.to_csv(PAYMENT_GOALS_FILE,index=False);payment_goals_df=df_edit_u_pay_v4;st.session_state.user_message="Collection updated!";st.session_state.message_type="success";st.rerun()
                        except Exception as e_u_save_pay_v4:st.session_state.user_message=f"Error: {e_u_save_pay_v4}";st.session_state.message_type="error";st.rerun()
                    else: st.session_state.user_message="Goal not found.";st.session_state.message_type="error";st.rerun()
        else: st.info(f"No collection goal for {current_q_pay_v4}. Contact admin.")
        st.markdown(f"---");st.markdown(f"<h5>Past Collection Goals ({TARGET_PAY_YEAR_V4})</h5>",unsafe_allow_html=True)
        past_g_pay_v4=my_goals_pay_v4[(my_goals_pay_v4["MonthYear"].str.startswith(str(TARGET_PAY_YEAR_V4)))&(my_goals_pay_v4["MonthYear"]!=current_q_pay_v4)]
        if not past_g_pay_v4.empty:render_goal_chart(past_g_pay_v4,"My Past Collection Performance")
        else: st.info(f"No past collection goals for {TARGET_PAY_YEAR_V4}.")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Manage Records" and current_user_auth['role'] == 'admin':
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>admin_panel_settings</span> Manage Records</h3>", unsafe_allow_html=True)
    admin_record_view_options = ["Employee Activity & Logs", "Submitted Sales Orders"]
    admin_selected_record_view = st.radio( "Select Record Type:", options=admin_record_view_options, horizontal=True, key="admin_manage_record_type_radio_main_v4") # Unique key
    st.divider()
    if admin_selected_record_view == "Employee Activity & Logs":
        st.markdown("<h4>Employee Activity & Other Logs</h4>", unsafe_allow_html=True)
        emp_list_admin_logs_v4 = [name for name, data in USERS.items() if data["role"] != "admin"]
        if not emp_list_admin_logs_v4: st.info("No employees/salespersons found.")
        else:
            sel_emp_admin_logs_v4 = st.selectbox("Select Employee:", [""] + emp_list_admin_logs_v4, key="admin_log_emp_select_v4", format_func=lambda x: "Select an Employee..." if x == "" else x)
            if sel_emp_admin_logs_v4:
                st.markdown(f"<h4 class='employee-section-header'>Records for: {sel_emp_admin_logs_v4}</h4>", unsafe_allow_html=True)
                tab_titles_admin_log_view_v4 = ["Field Activity", "Attendance", "Allowances", "Sales Goals", "Payment Goals"]
                tabs_admin_log_view_v4 = st.tabs([f"<span class='material-symbols-outlined' style='vertical-align:middle; margin-right:5px;'>folder_shared</span> {title}" for title in tab_titles_admin_log_view_v4])
                with tabs_admin_log_view_v4[0]: data_act_v4 = activity_log_df[activity_log_df["Username"] == sel_emp_admin_logs_v4]; display_activity_logs_section(data_act_v4, sel_emp_admin_logs_v4)
                with tabs_admin_log_view_v4[1]: data_att_v4 = attendance_df[attendance_df["Username"] == sel_emp_admin_logs_v4]; display_general_attendance_logs_section(data_att_v4, sel_emp_admin_logs_v4)
                with tabs_admin_log_view_v4[2]:
                    st.markdown(f"<h5>Allowances</h5>", unsafe_allow_html=True); data_allow_v4 = allowance_df[allowance_df["Username"] == sel_emp_admin_logs_v4]
                    if not data_allow_v4.empty: st.dataframe(data_allow_v4.sort_values(by="Date",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
                    else: st.info("No allowance records.")
                with tabs_admin_log_view_v4[3]:
                    st.markdown(f"<h5>Sales Goals</h5>", unsafe_allow_html=True); data_goals_v4 = goals_df[goals_df["Username"] == sel_emp_admin_logs_v4]
                    if not data_goals_v4.empty: st.dataframe(data_goals_v4.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
                    else: st.info("No sales goals.")
                with tabs_admin_log_view_v4[4]:
                    st.markdown(f"<h5>Payment Goals</h5>", unsafe_allow_html=True); data_pay_goals_v4 = payment_goals_df[payment_goals_df["Username"] == sel_emp_admin_logs_v4]
                    if not data_pay_goals_v4.empty: st.dataframe(data_pay_goals_v4.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
                    else: st.info("No payment goals.")
            else: st.info("Select an employee to view records.")
    elif admin_selected_record_view == "Submitted Sales Orders":
        st.markdown("<h4>Submitted Sales Orders</h4>", unsafe_allow_html=True)
        if order_summary_df.empty: st.info("No orders submitted yet.")
        else:
            summary_disp_admin_orders_v4 = order_summary_df.copy(); summary_disp_admin_orders_v4['OrderDate_dt'] = pd.to_datetime(summary_disp_admin_orders_v4['OrderDate'], errors='coerce'); summary_disp_admin_orders_v4 = summary_disp_admin_orders_v4.sort_values(by="OrderDate_dt", ascending=False)
            st.markdown("<h6>Filter Orders:</h6>", unsafe_allow_html=True); f_cols_admin_ord_v4 = st.columns([1,1,2])
            sales_list_admin_ord_v4 = ["All"] + sorted(summary_disp_admin_orders_v4['Salesperson'].unique().tolist()); sel_sales_admin_ord_v4 = f_cols_admin_ord_v4[0].selectbox("Salesperson", sales_list_admin_ord_v4, key="admin_ord_filt_sales_v4")
            if sel_sales_admin_ord_v4 != "All": summary_disp_admin_orders_v4 = summary_disp_admin_orders_v4[summary_disp_admin_orders_v4['Salesperson'] == sel_sales_admin_ord_v4]
            store_filt_admin_ord_v4 = f_cols_admin_ord_v4[1].text_input("Store Name contains", key="admin_ord_filt_store_v4")
            if store_filt_admin_ord_v4.strip(): summary_disp_admin_orders_v4 = summary_disp_admin_orders_v4[summary_disp_admin_orders_v4['StoreName'].str.contains(store_filt_admin_ord_v4.strip(), case=False, na=False)]
            min_d_admin_v4 = (summary_disp_admin_orders_v4['OrderDate_dt'].min().date() if not summary_disp_admin_orders_v4.empty and pd.notna(summary_disp_admin_orders_v4['OrderDate_dt'].min()) else date.today()-timedelta(days=30))
            max_d_admin_v4 = (summary_disp_admin_orders_v4['OrderDate_dt'].max().date() if not summary_disp_admin_orders_v4.empty and pd.notna(summary_disp_admin_orders_v4['OrderDate_dt'].max()) else date.today())
            date_r_admin_ord_v4 = f_cols_admin_ord_v4[2].date_input("Date Range", value=(min_d_admin_v4,max_d_admin_v4), min_value=min_d_admin_v4, max_value=max_d_admin_v4, key="admin_ord_filt_date_v4")
            if len(date_r_admin_ord_v4)==2: start_d_admin_v4,end_d_admin_v4=date_r_admin_ord_v4; summary_disp_admin_orders_v4=summary_disp_admin_orders_v4[(summary_disp_admin_orders_v4['OrderDate_dt'].dt.date>=start_d_admin_v4)&(summary_disp_admin_orders_v4['OrderDate_dt'].dt.date<=end_d_admin_v4)]
            st.markdown("---")
            if summary_disp_admin_orders_v4.empty: st.info("No orders match filters.")
            else:
                st.markdown(f"<h6>Displaying {len(summary_disp_admin_orders_v4)} Order(s)</h6>", unsafe_allow_html=True)
                cols_summary_show_admin_v4 = ["OrderID", "OrderDate", "Salesperson", "StoreName", "GrandTotal", "Notes"]
                st.dataframe(summary_disp_admin_orders_v4[cols_summary_show_admin_v4].reset_index(drop=True),use_container_width=True,hide_index=True,column_config={"OrderDate":st.column_config.DatetimeColumn("Date",format="YYYY-MM-DD HH:mm"), "GrandTotal":st.column_config.NumberColumn("Total (₹)",format="₹ %.2f")})
                st.markdown("---"); st.markdown("<h6>View Order Details:</h6>", unsafe_allow_html=True)
                opts_ord_id_admin_v4 = [""]+summary_disp_admin_orders_v4["OrderID"].tolist()
                sel_ord_id_admin_details_v4 = st.selectbox("Select OrderID:",opts_ord_id_admin_v4, index=0 if not st.session_state.admin_order_view_selected_order_id else opts_ord_id_admin_v4.index(st.session_state.admin_order_view_selected_order_id) if st.session_state.admin_order_view_selected_order_id in opts_ord_id_admin_v4 else 0, format_func=lambda x: "Select Order ID..." if x=="" else x, key="admin_ord_details_sel_v4")
                st.session_state.admin_order_view_selected_order_id = sel_ord_id_admin_details_v4
                if sel_ord_id_admin_details_v4:
                    items_sel_admin_v4 = orders_df[orders_df['OrderID']==sel_ord_id_admin_details_v4]
                    if items_sel_admin_v4.empty: st.warning(f"No items for OrderID: {sel_ord_id_admin_details_v4}")
                    else:
                        st.markdown(f"<h6>Line Items for Order: {sel_ord_id_admin_details_v4}</h6>",unsafe_allow_html=True)
                        cols_items_show_admin_v4=["ProductName","SKU","Quantity","UnitOfMeasure","UnitPrice","LineTotal"]
                        st.dataframe(items_sel_admin_v4[cols_items_show_admin_v4].reset_index(drop=True),use_container_width=True,hide_index=True,column_config={"UnitPrice":st.column_config.NumberColumn("Price (₹)",format="₹ %.2f"),"LineTotal":st.column_config.NumberColumn("Item Total (₹)",format="₹ %.2f")})
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "My Records":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h3><span class='material-symbols-outlined'>article</span> My Records</h3>", unsafe_allow_html=True)
    my_username_rec_v4 = current_user_auth["username"]
    st.markdown(f"<h4 class='employee-section-header'>Activity & Records for: {my_username_rec_v4}</h4>", unsafe_allow_html=True)
    tab_titles_user_rec_page_v4 = ["Field Activity", "Attendance", "Allowances", "Sales Goals", "Payment Goals"]
    if current_user_auth['role'] == 'sales_person': tab_titles_user_rec_page_v4.append("My Submitted Orders")
    tabs_user_rec_page_v4 = st.tabs([f"<span class='material-symbols-outlined' style='vertical-align:middle; margin-right:5px;'>badge</span> {title}" for title in tab_titles_user_rec_page_v4])
    with tabs_user_rec_page_v4[0]: data_act_user_v4 = activity_log_df[activity_log_df["Username"] == my_username_rec_v4]; display_activity_logs_section(data_act_user_v4, "My")
    with tabs_user_rec_page_v4[1]: data_att_user_v4 = attendance_df[attendance_df["Username"] == my_username_rec_v4]; display_general_attendance_logs_section(data_att_user_v4, "My")
    with tabs_user_rec_page_v4[2]:
        st.markdown(f"<h5>My Allowances</h5>", unsafe_allow_html=True); data_allow_user_v4 = allowance_df[allowance_df["Username"] == my_username_rec_v4]
        if not data_allow_user_v4.empty: st.dataframe(data_allow_user_v4.sort_values(by="Date",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
        else: st.info("No allowance records.")
    with tabs_user_rec_page_v4[3]:
        st.markdown(f"<h5>My Sales Goals</h5>", unsafe_allow_html=True); data_goals_user_v4 = goals_df[goals_df["Username"] == my_username_rec_v4]
        if not data_goals_user_v4.empty: st.dataframe(data_goals_user_v4.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
        else: st.info("No sales goals.")
    with tabs_user_rec_page_v4[4]:
        st.markdown(f"<h5>My Payment Goals</h5>", unsafe_allow_html=True); data_pay_goals_user_v4 = payment_goals_df[payment_goals_df["Username"] == my_username_rec_v4]
        if not data_pay_goals_user_v4.empty: st.dataframe(data_pay_goals_user_v4.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
        else: st.info("No payment goals.")
    if current_user_auth['role'] == 'sales_person' and len(tabs_user_rec_page_v4) > 5:
        with tabs_user_rec_page_v4[5]:
            st.markdown(f"<h5>My Submitted Orders</h5>", unsafe_allow_html=True)
            my_orders_summary_v4 = order_summary_df[order_summary_df["Salesperson"] == my_username_rec_v4].copy()
            if my_orders_summary_v4.empty: st.info("You have not submitted any orders yet.")
            else:
                my_orders_summary_v4['OrderDate_dt'] = pd.to_datetime(my_orders_summary_v4['OrderDate'])
                my_orders_summary_v4 = my_orders_summary_v4.sort_values(by="OrderDate_dt", ascending=False)
                my_order_cols_to_show_v4 = ["OrderID", "OrderDate", "StoreName", "GrandTotal", "Notes"]
                st.dataframe(my_orders_summary_v4[my_order_cols_to_show_v4].reset_index(drop=True), use_container_width=True, hide_index=True,
                               column_config={"OrderDate": st.column_config.DatetimeColumn("Order Date", format="YYYY-MM-DD HH:mm"),
                                              "GrandTotal": st.column_config.NumberColumn("Total (₹)", format="₹ %.2f")})
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.error(f"Page '{nav}' not found or you do not have permission to view it.", icon="🚨")
    st.markdown("</div>", unsafe_allow_html=True)
