import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from streamlit_option_menu import option_menu
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

# --- Global Configuration & Constants ---
TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError: st.error(f"Invalid TZ: {TARGET_TIMEZONE}"); st.stop()

ATTENDANCE_FILE = "attendance.csv"; ALLOWANCE_FILE = "allowances.csv"; GOALS_FILE = "goals.csv";
PAYMENT_GOALS_FILE = "payment_goals.csv"; ACTIVITY_LOG_FILE = "activity_log.csv";
ACTIVITY_PHOTOS_DIR = "activity_photos"
if not os.path.exists(ACTIVITY_PHOTOS_DIR): os.makedirs(ACTIVITY_PHOTOS_DIR, exist_ok=True)

def get_current_time_in_tz(): return datetime.now(timezone.utc).astimezone(tz)
def get_quarter_str_for_year(year):
    m = get_current_time_in_tz().month
    if 1<=m<=3: return f"{year}-Q1"; elif 4<=m<=6: return f"{year}-Q2";
    elif 7<=m<=9: return f"{year}-Q3"; else: return f"{year}-Q4"

def load_data(path, columns):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        try:
            df = pd.read_csv(path)
            for col in columns:
                if col not in df.columns: df[col] = pd.NA
            num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude"]
            for nc in num_cols:
                if nc in df.columns: df[nc] = pd.to_numeric(df[nc], errors='coerce')
            return df
        except Exception: return pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
        try: df.to_csv(path, index=False)
        except Exception: pass
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]

attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
activity_log_df = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS)

USERS = {
    "Geetali": {"password": "Geetali123", "role": "employee", "position": "Software Engineer", "profile_photo": "images/geetali.png"},
    "Nilesh": {"password": "Nilesh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "Vishal": {"password": "Vishal123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/vishal.png"},
    "Santosh": {"password": "Santosh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/santosh.png"},
    "Deepak": {"password": "Deepak123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/deepak.png"},
    "Rahul": {"password": "Rahul123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/rahul.png"},
    "admin": {"password": "admin123", "role": "admin", "position": "System Administrator", "profile_photo": "images/admin.png"}
}
if not os.path.exists("images"): os.makedirs("images", exist_ok=True)
if PILLOW_INSTALLED:
    for user_key, user_data in USERS.items():
        img_path = user_data.get("profile_photo")
        if img_path and not os.path.exists(img_path):
            try:
                img = Image.new('RGB', (120, 120), color=(220, 220, 220)); draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", 40)
                except IOError: font = ImageFont.load_default()
                text_content = user_key[:2].upper()
                if hasattr(draw, 'textbbox'):
                    bbox = draw.textbbox((0,0), text_content, font=font); w,h = bbox[2]-bbox[0], bbox[3]-bbox[1]
                    x,y = (120-w)/2 - bbox[0], (120-h)/2 - bbox[1]
                else: x,y = 30,30
                draw.text((x, y), text_content, fill=(100,100,100), font=font); img.save(img_path)
            except: pass

if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}
if "order_items" not in st.session_state: st.session_state.order_items = []
APP_MENU_OPTIONS = ["Attendance", "Upload Activity Photo", "Allowance", "Goal Tracker", "Payment Collection Tracker", "View Logs", "Create Order"]
if "active_page" not in st.session_state or st.session_state.active_page not in APP_MENU_OPTIONS:
    st.session_state.active_page = APP_MENU_OPTIONS[0]

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
<style>
    :root {
        --kaggle-blue: #20BEFF; --kaggle-dark-text: #333333; --kaggle-light-bg: #FFFFFF;
        --kaggle-content-bg: #F5F5F5; --kaggle-gray-border: #E0E0E0; --kaggle-hover-bg: #f0f8ff;
        --kaggle-selected-bg: #E6F7FF; --kaggle-selected-text: var(--kaggle-blue);
        --kaggle-icon-color: #555555; --kaggle-icon-selected-color: var(--kaggle-blue);
    }
    body { background-color: var(--kaggle-content-bg) !important; font-family: 'Roboto', sans-serif !important; }
    div[data-testid="stAppViewContainer"] > .main { background-color: var(--kaggle-content-bg) !important; padding: 1.5rem; }
    section[data-testid="stSidebar"] > div:first-child {
        background-color: var(--kaggle-light-bg) !important; border-right: 1px solid var(--kaggle-gray-border) !important;
        padding: 0px !important; height: 100vh; display: flex; flex-direction: column;
    }
    .sidebar-app-header { padding: 20px 16px 16px 16px; border-bottom: 1px solid var(--kaggle-gray-border); }
    .sidebar-app-header h2 { color: var(--kaggle-blue); font-size: 1.5rem; margin: 0; font-weight: 600; }
    .sidebar-app-header p { color: #666; font-size: 0.85rem; margin: 4px 0 0 0; }
    .sidebar-user-info-block { padding: 12px 16px; display: flex; align-items: center; gap: 12px; border-bottom: 1px solid var(--kaggle-gray-border); }
    .user-profile-img-display { border-radius: 50% !important; width: 40px !important; height: 40px !important; object-fit: cover !important; border: 1px solid var(--kaggle-gray-border) !important; }
    .user-details-text-block div:nth-child(1) { color: var(--kaggle-dark-text) !important; font-size: 0.95rem; font-weight: 500; }
    .user-details-text-block div:nth-child(2) { color: #777 !important; font-size: 0.8rem; }
    .logout-button-container-main { margin-top: auto; padding: 16px; border-top: 1px solid var(--kaggle-gray-border); }
    .logout-button-container-main .stButton button {
        background-color: transparent !important; color: #d32f2f !important; border: 1px solid #ef9a9a !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        font-size: 0.9rem !important; border-radius: 6px !important; width: 100% !important;
    }
    .logout-button-container-main .stButton button:hover { background-color: rgba(211, 47, 47, 0.05) !important; border-color: #d32f2f !important; }
    .card { border: 1px solid var(--kaggle-gray-border); border-radius: 8px; padding: 24px; margin-bottom: 20px; background-color: var(--kaggle-light-bg); box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
    .card h3 { color: var(--kaggle-blue); font-size: 1.3rem; margin-top: 0; margin-bottom: 1rem;}
    .custom-notification { padding: 1rem; border-radius: 6px; margin-bottom: 1rem; border: 1px solid transparent; font-size: 0.9rem; }
    .custom-notification.success { color: #0f5132; background-color: #d1e7dd; border-color: #badbcc; }
    .custom-notification.error { color: #842029; background-color: #f8d7da; border-color: #f5c2c7; }
</style>
""", unsafe_allow_html=True)

# --- PLOTTING FUNCTIONS ---
def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty: st.warning("No data to plot."); return
    df_chart = df.copy(); df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear", value_vars=["TargetAmount", "AchievedAmount"], var_name="Metric", value_name="Amount")
    if df_melted.empty: st.warning(f"No data to plot for {chart_title}."); return
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group", labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"}, title=chart_title, color_discrete_map={'TargetAmount': '#20BEFF', 'AchievedAmount': '#34A853'})
    fig.update_layout(height=400, legend_title_text='Metric', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font_color='#333333')
    fig.update_xaxes(type='category', showgrid=False, zeroline=False, color='#555555'); fig.update_yaxes(showgrid=True, gridcolor='rgba(0,0,0,0.05)', zeroline=False, color='#555555')
    st.plotly_chart(fig, use_container_width=True)

def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#20BEFF', remaining_color='#E0E0E0', center_text_color='#333333'):
    fig, ax = plt.subplots(figsize=(2.2, 2.2), dpi=110); fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    progress_percentage = max(0.0, min(float(progress_percentage), 100.0)); remaining_percentage = 100.0 - progress_percentage
    if progress_percentage <= 0.01: sizes = [100.0]; slice_colors = [remaining_color]; actual_progress_display = 0.0
    elif progress_percentage >= 99.99: sizes = [100.0]; slice_colors = [achieved_color]; actual_progress_display = 100.0
    else: sizes = [progress_percentage, remaining_percentage]; slice_colors = [achieved_color, remaining_color]; actual_progress_display = progress_percentage
    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.35, edgecolor='#FFFFFF'))
    centre_circle = plt.Circle((0,0),0.65,fc='#FFFFFF'); fig.gca().add_artist(centre_circle)
    text_color_to_use = center_text_color if actual_progress_display > 0 else '#777777'
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=10, fontweight='bold', color=text_color_to_use)
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0); return fig

def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee"):
    if summary_df.empty: return None
    labels = summary_df[user_col].tolist(); target_amounts = summary_df[target_col].fillna(0).tolist(); achieved_amounts = summary_df[achieved_col].fillna(0).tolist()
    x = np.arange(len(labels)); width = 0.35
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.7), 4.5), dpi=110, facecolor='rgba(0,0,0,0)'); ax.set_facecolor('rgba(0,0,0,0)')
    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color='rgba(32, 190, 255, 0.8)'); rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color='rgba(52, 168, 83, 0.8)')
    ax.set_ylabel('Amount (INR)', fontsize=9, color='#555555'); ax.set_title(title, fontsize=11, fontweight='bold', pad=12, color='#333333')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=8, color='#555555')
    legend = ax.legend(fontsize=8, facecolor='rgba(255,255,255,0.8)', edgecolor='#E0E0E0');
    for text in legend.get_texts(): text.set_color('#333333')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.spines['bottom'].set_color('#E0E0E0'); ax.spines['left'].set_color('#E0E0E0')
    ax.tick_params(axis='x', colors='#555555'); ax.tick_params(axis='y', colors='#555555')
    ax.yaxis.grid(True, linestyle='--', alpha=0.5, color='#E0E0E0')
    def autolabel(rects_group, bar_color_text):
        for rect_item in rects_group:
            height_item = rect_item.get_height()
            if height_item > 0: ax.annotate(f'{height_item:,.0f}', xy=(rect_item.get_x() + rect_item.get_width() / 2, height_item), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=6, color=bar_color_text)
    autolabel(rects1, '#007bff'); autolabel(rects2, '#188038'); fig.tight_layout(pad=1.2); return fig

# --- LOGIN PAGE ---
if not st.session_state.auth["logged_in"]:
    st.title("TrackSphere Login")
    message_placeholder_login = st.empty()
    if st.session_state.user_message:
        message_placeholder_login.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
        st.session_state.user_message = None; st.session_state.message_type = None
    st.markdown("<div class='card' style='max-width: 400px; margin: 3rem auto; padding: 2rem;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: var(--kaggle-blue);'>🔐 Login to TrackSphere</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname_app_k_v2")
    pwd = st.text_input("Password", type="password", key="login_pwd_app_k_v2")
    if st.button("Login", key="login_button_app_k_v2", type="primary", use_container_width=True):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = "Login successful!"; st.session_state.message_type = "success"
            st.session_state.active_page = APP_MENU_OPTIONS[0]
            st.rerun()
        else: st.error("Invalid username or password.")
    st.markdown("</div>", unsafe_allow_html=True); st.stop()

current_user = st.session_state.auth
message_placeholder_main = st.empty()
if st.session_state.user_message:
    message_placeholder_main.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
    st.session_state.user_message = None; st.session_state.message_type = None

with st.sidebar:
    st.markdown("""<div class="sidebar-app-header"><h2>TrackSphere</h2><p>Field Activity Tracker</p></div>""", unsafe_allow_html=True)
    current_username_sb = current_user.get('username', 'Guest')
    user_details_sb = USERS.get(current_username_sb, {})
    profile_photo_sb = user_details_sb.get("profile_photo", "")
    st.markdown('<div class="sidebar-user-info-block">', unsafe_allow_html=True)
    if profile_photo_sb and os.path.exists(profile_photo_sb) and PILLOW_INSTALLED:
        st.image(profile_photo_sb, width=40, new_class="user-profile-img-display") # Try adding a class if st.image supports it
    else:
        st.markdown(f"""<i class="bi bi-person-circle" style="font-size: 36px; color: var(--kaggle-icon-color); vertical-align:middle;"></i>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="user-details-text-block"><div>{current_username_sb}</div><div>{user_details_sb.get('position', 'N/A')}</div></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    app_menu_icons = ['calendar2-check', 'camera', 'wallet2', 'graph-up', 'cash-stack', 'journals', 'cart3']
    if st.session_state.get('active_page') not in APP_MENU_OPTIONS: st.session_state.active_page = APP_MENU_OPTIONS[0]
    default_idx = APP_MENU_OPTIONS.index(st.session_state.active_page)
    selected = option_menu(
        menu_title=None, options=APP_MENU_OPTIONS, icons=app_menu_icons, default_index=default_idx,
        orientation="vertical", on_change=lambda key: st.session_state.update(active_page=key),
        key='main_app_option_menu',
        styles={
            "container": {"padding": "5px 8px !important", "background-color": "var(--kaggle-light-bg)"},
            "icon": {"color": "var(--kaggle-icon-color)", "font-size": "18px", "margin-right":"10px"},
            "nav-link": {"font-size": "0.9rem", "text-align": "left", "margin": "4px 0px", "padding": "10px 16px", "color": "var(--kaggle-dark-text)", "border-radius": "6px", "--hover-color": "var(--kaggle-hover-bg)"},
            "nav-link-selected": {"background-color": "var(--kaggle-selected-bg)", "color": "var(--kaggle-selected-text)", "font-weight": "500"},
            "nav-link-selected > i.icon": {"color": "var(--kaggle-icon-selected-color) !important"}
        })
    st.markdown('<div class="logout-button-container-main">', unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_app_button_key_v2", use_container_width=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."; st.session_state.message_type = "info"
        st.session_state.active_page = APP_MENU_OPTIONS[0]; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN CONTENT PAGE ROUTING ---
if selected == "Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled for attendance. Photos for specific activities can be uploaded from the 'Upload Activity Photo' section.", icon="ℹ️")
    st.markdown("---")
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True) # Ensure this class has CSS if needed
    col1_att, col2_att = st.columns(2)
    common_data_att = {"Username": current_user["username"], "Latitude": pd.NA, "Longitude": pd.NA}
    def process_general_attendance(attendance_type):
        global attendance_df
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_data = {"Type": attendance_type, "Timestamp": now_str_display, **common_data_att}
        for col_name in ATTENDANCE_COLUMNS:
            if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
        new_entry = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
        attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        try:
            attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."; st.session_state.message_type = "success"; st.rerun()
        except Exception as e: st.session_state.user_message = f"Error saving attendance: {e}"; st.session_state.message_type = "error"; st.rerun()
    with col1_att:
        if st.button("✅ Check In", key="check_in_btn_att_page", use_container_width=True, type="primary"): process_general_attendance("Check-In")
    with col2_att:
        if st.button("🚪 Check Out", key="check_out_btn_att_page", use_container_width=True, type="primary"): process_general_attendance("Check-Out")
    st.markdown('</div></div>', unsafe_allow_html=True)

elif selected == "Upload Activity Photo":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat, current_lon = pd.NA, pd.NA
    with st.form(key="activity_photo_form_upload_page"):
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description:", key="activity_desc_upload_page")
        img_file_buffer_activity = st.camera_input("Take a picture:", key="activity_camera_upload_page")
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo & Log")
    if submit_activity_photo:
        if img_file_buffer_activity is None: st.warning("Please take a picture.")
        elif not activity_description.strip(): st.warning("Please provide a description.")
        else:
            now_for_filename = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S")
            now_for_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            image_filename_activity = f"{current_user['username']}_activity_{now_for_filename}.jpg"
            image_path_activity = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_activity)
            try:
                with open(image_path_activity, "wb") as f: f.write(img_file_buffer_activity.getbuffer())
                new_activity_data = {"Username": current_user['username'], "Timestamp": now_for_display, "Description": activity_description, "ImageFile": image_filename_activity, "Latitude": current_lat, "Longitude": current_lon}
                for col_name in ACTIVITY_LOG_COLUMNS:
                    if col_name not in new_activity_data: new_activity_data[col_name] = pd.NA
                new_activity_entry = pd.DataFrame([new_activity_data], columns=ACTIVITY_LOG_COLUMNS)
                activity_log_df = pd.concat([activity_log_df, new_activity_entry], ignore_index=True)
                activity_log_df.to_csv(ACTIVITY_LOG_FILE, index=False)
                st.session_state.user_message = "Activity photo and log uploaded!"; st.session_state.message_type = "success"; st.rerun()
            except Exception as e: st.session_state.user_message = f"Error saving activity: {e}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    a_type = st.radio("Type:", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allowance_type_radio_main_page", horizontal=True)
    amount = st.number_input("Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_main_page")
    reason = st.text_area("Reason:", key="allowance_reason_main_page", placeholder="Please provide a clear justification...")
    if st.button("Submit Allowance Request", key="submit_allowance_btn_main_page", use_container_width=True, type="primary"):
        if a_type and amount > 0 and reason.strip():
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry_data = {"Username": current_user["username"], "Type": a_type, "Amount": amount, "Reason": reason, "Date": date_str}
            new_entry = pd.DataFrame([new_entry_data], columns=ALLOWANCE_COLUMNS)
            allowance_df = pd.concat([allowance_df, new_entry], ignore_index=True)
            try:
                allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                st.session_state.user_message = f"Allowance for ₹{amount:.2f} submitted."; st.session_state.message_type = "success"; st.rerun()
            except Exception as e: st.session_state.user_message = f"Error submitting allowance: {e}"; st.session_state.message_type = "error"; st.rerun()
        else: st.warning("Please complete all fields with valid values.")
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Goal Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_GOAL_YEAR = 2025; current_quarter_for_display = get_quarter_str_for_year(TARGET_GOAL_YEAR)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR}"], key="admin_goal_action_radio_2025_q_gt", horizontal=True)
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
                    num_cols_display = min(3, len(summary_df_sales)) # Max 3 cols
                    if num_cols_display > 0:
                        cols_sales = st.columns(num_cols_display)
                        for idx_s, (index_s, row_s) in enumerate(summary_df_sales.iterrows()):
                            progress_percent = (row_s['Achieved'] / row_s['Target'] * 100) if row_s['Target'] > 0 else 0
                            donut_fig = create_donut_chart(progress_percent, achieved_color='#28a745')
                            with cols_sales[idx_s % num_cols_display]:
                                st.markdown(f"<div class='employee-progress-item'><h6>{row_s['Employee']}</h6><p>Target: ₹{row_s['Target']:,.0f}<br>Achieved: ₹{row_s['Achieved']:,.0f}</p></div>", unsafe_allow_html=True)
                                st.pyplot(donut_fig, use_container_width=True)
                                st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin-top: 10px; margin-bottom:25px;'>", unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Sales Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_sales = create_team_progress_bar_chart(summary_df_sales, title="Team Sales Target vs. Achieved", target_col="Target", achieved_col="Achieved")
                    if team_bar_fig_sales: st.pyplot(team_bar_fig_sales, use_container_width=True)
                    else: st.info("No sales data to plot for team bar chart.")
                else: st.info(f"No sales goals data for {current_quarter_for_display}.")
        elif admin_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set or Update Employee Goal ({TARGET_GOAL_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employee_options: st.warning("No employees available.")
            else:
                selected_emp = st.radio("Select Employee:", employee_options, key="goal_emp_radio_admin_set_gt", horizontal=True)
                quarter_options = [f"{TARGET_GOAL_YEAR}-Q{i}" for i in range(1,5)]; selected_period = st.radio("Goal Period:", quarter_options, key="goal_period_radio_admin_set_gt", horizontal=True)
                existing_g = goals_df[(goals_df["Username"] == selected_emp) & (goals_df["MonthYear"] == selected_period)]
                g_desc,g_target,g_achieved,g_status = "",0.0,0.0,status_options[0]
                if not existing_g.empty:
                    g_data=existing_g.iloc[0]; g_desc=g_data.get("GoalDescription",""); g_target=g_data.get("TargetAmount",0.0); g_achieved=g_data.get("AchievedAmount",0.0); g_status=g_data.get("Status",status_options[0])
                    st.info(f"Editing goal for {selected_emp} - {selected_period}")
                with st.form(key=f"set_goal_form_{selected_emp}_{selected_period}_admin_gt"):
                    new_desc=st.text_area("Goal Description",value=g_desc,key=f"desc_gt_admin")
                    new_target=st.number_input("Target Sales (INR)",value=float(g_target),min_value=0.0,step=1000.0,format="%.2f",key=f"target_gt_admin")
                    new_achieved=st.number_input("Achieved Sales (INR)",value=float(g_achieved),min_value=0.0,step=100.0,format="%.2f",key=f"achieved_gt_admin")
                    new_status=st.radio("Status:",status_options,index=status_options.index(g_status),horizontal=True,key=f"status_gt_admin")
                    submitted=st.form_submit_button("Save Goal")
                if submitted:
                    if not new_desc.strip(): st.warning("Description is required.")
                    elif new_target <= 0 and new_status not in ["Cancelled","On Hold","Not Started"]: st.warning("Target > 0 required.")
                    else:
                        # goals_df is global, modify it directly or a copy then reassign
                        idx_to_update = goals_df[(goals_df["Username"] == selected_emp) & (goals_df["MonthYear"] == selected_period)].index
                        if not idx_to_update.empty:
                            goals_df.loc[idx_to_update, ["GoalDescription", "TargetAmount", "AchievedAmount", "Status"]] = [new_desc, new_target, new_achieved, new_status]
                            msg_verb="updated"
                        else:
                            new_row_df=pd.DataFrame([{"Username":selected_emp,"MonthYear":selected_period,"GoalDescription":new_desc,"TargetAmount":new_target,"AchievedAmount":new_achieved,"Status":new_status}], columns=GOALS_COLUMNS)
                            goals_df=pd.concat([goals_df,new_row_df],ignore_index=True)
                            msg_verb="set"
                        try:
                            goals_df.to_csv(GOALS_FILE,index=False)
                            st.session_state.user_message=f"Goal for {selected_emp} ({selected_period}) {msg_verb}!"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e: st.session_state.user_message=f"Error saving goal: {e}"; st.session_state.message_type="error"; st.rerun()
    else: # Employee View
        st.markdown("<h4>My Sales Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        my_goals = goals_df[goals_df["Username"] == current_user["username"]].copy() # Use current_user
        for col in ["TargetAmount", "AchievedAmount"]: my_goals[col] = pd.to_numeric(my_goals[col], errors="coerce").fillna(0.0)
        current_g_df = my_goals[my_goals["MonthYear"] == current_quarter_for_display]
        st.markdown(f"<h5>Current Goal Period: {current_quarter_for_display}</h5>", unsafe_allow_html=True)
        if not current_g_df.empty:
            g = current_g_df.iloc[0]; target_amt = g["TargetAmount"]; achieved_amt = g["AchievedAmount"]
            st.markdown(f"**Description:** {g.get('GoalDescription', 'N/A')}")
            col_metrics_sales, col_chart_sales = st.columns([0.63,0.37])
            with col_metrics_sales:
                sub_col1,sub_col2=st.columns(2); sub_col1.metric("Target",f"₹{target_amt:,.0f}"); sub_col2.metric("Achieved",f"₹{achieved_amt:,.0f}")
                st.metric("Status",g.get("Status","In Progress"),label_visibility="labeled")
            with col_chart_sales:
                progress_percent_sales=(achieved_amt/target_amt*100) if target_amt > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:-15px;'>Sales Progress</h6>",unsafe_allow_html=True)
                donut_fig_sales=create_donut_chart(progress_percent_sales,"Sales Progress",achieved_color='#28a745'); st.pyplot(donut_fig_sales,use_container_width=True)
            st.markdown("---")
            with st.form(key=f"update_achievement_{current_user['username']}_{current_quarter_for_display}_gt"):
                new_val=st.number_input("Update Achieved Amount (INR):",value=achieved_amt,min_value=0.0,step=100.0,format="%.2f")
                submitted_ach=st.form_submit_button("Update Achievement")
            if submitted_ach:
                idx_update = goals_df[(goals_df["Username"] == current_user["username"]) & (goals_df["MonthYear"] == current_quarter_for_display)].index
                if not idx_update.empty:
                    goals_df.loc[idx_update[0],"AchievedAmount"]=new_val
                    goals_df.loc[idx_update[0],"Status"] = "Achieved" if new_val >= target_amt and target_amt > 0 else "In Progress"
                    try:
                        goals_df.to_csv(GOALS_FILE,index=False)
                        st.session_state.user_message = "Achievement updated!"; st.session_state.message_type = "success"; st.rerun()
                    except Exception as e: st.session_state.user_message = f"Error updating: {e}"; st.session_state.message_type = "error"; st.rerun()
                else: st.session_state.user_message = "Could not find goal to update."; st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No goal set for {current_quarter_for_display}. Contact admin.")
        st.markdown("---"); st.markdown("<h5>My Past Goals (2025)</h5>", unsafe_allow_html=True)
        past_goals = my_goals[(my_goals["MonthYear"].str.startswith(str(TARGET_GOAL_YEAR))) & (my_goals["MonthYear"] != current_quarter_for_display)]
        if not past_goals.empty: render_goal_chart(past_goals, "Past Sales Goal Performance")
        else: st.info(f"No past goal records for {TARGET_GOAL_YEAR}.")
    st.markdown("</div>", unsafe_allow_html=True)

elif selected == "Payment Collection Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    # ... (Paste your full Payment Collection Tracker logic here) ...
    st.write("Payment Collection Tracker content will go here.") # Placeholder
    st.markdown("</div>", unsafe_allow_html=True)

elif selected == "View Logs":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 View Logs</h3>", unsafe_allow_html=True)
    # ... (Paste your full View Logs logic here) ...
    st.write("View Logs content will go here.") # Placeholder
    st.markdown("</div>", unsafe_allow_html=True)

elif selected == "Create Order":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🛒 Create New Order</h3>", unsafe_allow_html=True)
    # ... (Paste your full Create Order logic here) ...
    try:
        stores_df = pd.read_csv("agri_stores.csv") # Ensure these files exist
        products_df = pd.read_csv("symplanta_products_with_images.csv")
        # ... your order creation UI ...
        st.write("Create Order form will go here.") # Placeholder
    except FileNotFoundError:
        st.error("Order data files (agri_stores.csv, symplanta_products_with_images.csv) not found.")
    st.markdown("</div>", unsafe_allow_html=True)
