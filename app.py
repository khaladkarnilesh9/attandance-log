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
    if 1<=m<=3: return f"{year}-Q1"
    elif 4<=m<=6: return f"{year}-Q2"
    elif 7<=m<=9: return f"{year}-Q3"
    else: return f"{year}-Q4"

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
    :root { /* CSS Variables */ } /* Keep your existing CSS variables */
    /* Keep your full CSS block here */
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
    .button-column-container .stButton button { width: 100%; }
    .employee-progress-item h6 { margin-bottom: 0.25rem; font-size: 1rem; color: #202124; }
    .employee-progress-item p { font-size: 0.85rem; color: #5f6368; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty: st.warning("No data available to plot."); return
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
    
    # Corrected: Use tuple for facecolor
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.7), 4.5), dpi=110, facecolor=(0,0,0,0)) 
    ax.set_facecolor((0,0,0,0))

    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color='rgba(32, 190, 255, 0.8)')
    rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color='rgba(52, 168, 83, 0.8)')
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
    uname = st.text_input("Username", key="login_uname_app_final_v3") # Unique key
    pwd = st.text_input("Password", type="password", key="login_pwd_app_final_v3") # Unique key
    if st.button("Login", key="login_button_app_final_v3", type="primary", use_container_width=True):
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
        st.image(profile_photo_sb, width=40, output_format='PNG') # Ensure output_format if needed
    else:
        st.markdown(f"""<i class="bi bi-person-circle" style="font-size: 36px; color: var(--kaggle-icon-color); vertical-align:middle;"></i>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="user-details-text-block"><div>{current_username_sb}</div><div>{user_details_sb.get('position', 'N/A')}</div></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    app_menu_icons = ['calendar2-check', 'camera', 'wallet2', 'graph-up', 'cash-stack', 'journals', 'cart3']
    if st.session_state.get('active_page') not in APP_MENU_OPTIONS: st.session_state.active_page = APP_MENU_OPTIONS[0]
    try:
        default_idx = APP_MENU_OPTIONS.index(st.session_state.active_page)
    except ValueError: # Handle case where active_page might somehow be invalid
        default_idx = 0
        st.session_state.active_page = APP_MENU_OPTIONS[0]

    selected = option_menu(
        menu_title=None, options=APP_MENU_OPTIONS, icons=app_menu_icons, default_index=default_idx,
        orientation="vertical", on_change=lambda key: st.session_state.update(active_page=key),
        key='main_app_option_menu_final_v3', # Unique key
        styles={
            "container": {"padding": "5px 8px !important", "background-color": "var(--kaggle-light-bg)"},
            "icon": {"color": "var(--kaggle-icon-color)", "font-size": "18px", "margin-right":"10px"},
            "nav-link": {"font-size": "0.9rem", "text-align": "left", "margin": "4px 0px", "padding": "10px 16px", "color": "var(--kaggle-dark-text)", "border-radius": "6px", "--hover-color": "var(--kaggle-hover-bg)"},
            "nav-link-selected": {"background-color": "var(--kaggle-selected-bg)", "color": "var(--kaggle-selected-text)", "font-weight": "500"},
            "nav-link-selected > i.icon": {"color": "var(--kaggle-icon-selected-color) !important"}
        })
    st.markdown('<div class="logout-button-container-main">', unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_app_button_key_final_v3", use_container_width=True): # Unique key
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."; st.session_state.message_type = "info"
        st.session_state.active_page = APP_MENU_OPTIONS[0]; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

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
            loc_disp_act_f = 'Not Recorded'
            if pd.notna(row_act_func.get('Latitude')) and pd.notna(row_act_func.get('Longitude')):
                try: loc_disp_act_f = f"Lat: {float(row_act_func.get('Latitude')):.4f}, Lon: {float(row_act_func.get('Longitude')):.4f}"
                except (ValueError, TypeError): loc_disp_act_f = "Invalid Coords"
            st.markdown(f"**Timestamp:** {ts_disp_act_f}<br>**Description:** {row_act_func.get('Description', 'N/A')}<br>**Location:** {loc_disp_act_f}", unsafe_allow_html=True)
            if pd.notna(row_act_func.get('ImageFile')) and str(row_act_func.get('ImageFile')).strip() != "": st.caption(f"Photo: {row_act_func['ImageFile']}")
            else: st.caption("No photo.")
        with col_photo_act_f:
            if pd.notna(row_act_func.get('ImageFile')) and str(row_act_func.get('ImageFile')).strip() != "":
                img_path_disp_act_f = os.path.join(ACTIVITY_PHOTOS_DIR, str(row_act_func['ImageFile']))
                if os.path.exists(img_path_disp_act_f):
                    try: st.image(img_path_disp_act_f, width=150, caption=f"Activity Photo")
                    except Exception as img_e_act_f: st.warning(f"Img err: {img_e_act_f}", icon="⚠️")
                else: st.caption(f"Img file missing on server.")

def display_general_attendance_logs_section(df_logs_att_func, user_header_name_att_func):
    if df_logs_att_func.empty: st.info(f"No general attendance records for {user_header_name_att_func}.", icon="📭"); return
    df_logs_att_sorted_func = df_logs_att_func.copy()
    df_logs_att_sorted_func['Timestamp'] = pd.to_datetime(df_logs_att_sorted_func['Timestamp'], errors='coerce')
    df_logs_att_sorted_func = df_logs_att_sorted_func.sort_values(by="Timestamp", ascending=False)
    cols_to_show_att_f = ["Type", "Timestamp"]
    if 'Latitude' in df_logs_att_sorted_func.columns and 'Longitude' in df_logs_att_sorted_func.columns:
        df_logs_att_sorted_func['Location (Illustrative)'] = df_logs_att_sorted_func.apply(
            lambda r: f"{float(r['Latitude']):.4f}, {float(r['Longitude']):.4f}" if pd.notna(r['Latitude']) and pd.notna(r['Longitude']) and isinstance(r['Latitude'], (int, float)) and isinstance(r['Longitude'], (int, float)) else "NR", axis=1
        )
        cols_to_show_att_f.append('Location (Illustrative)')
    st.dataframe(df_logs_att_sorted_func[cols_to_show_att_f].reset_index(drop=True), use_container_width=True, hide_index=True, column_config={"Timestamp":st.column_config.DatetimeColumn("Timestamp",format="YYYY-MM-DD HH:mm:ss")})

# --- Main Content Logic ---
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
        st.text_input("Order Date", value=order_date_display_co, disabled=True, key="co_form_date_key_v6")
        st.text_input("Salesperson", value=salesperson_name_display_co, disabled=True, key="co_form_salesperson_key_v6")
    with col_header2_co:
        if stores_df.empty:
            st.warning("No stores in `agri_stores.csv`. Store selection is mandatory.", icon="🏬"); st.session_state.order_store_select = None
        else:
            store_options_dict_co = {row['StoreID']: f"{row['StoreName']} ({row['StoreID']})" for index, row in stores_df.iterrows()}
            current_store_sel_co = st.session_state.get('order_store_select', None)
            options_for_sb_co = [None] + list(store_options_dict_co.keys())
            current_idx_sb_co = 0
            if current_store_sel_co in store_options_dict_co:
                try: current_idx_sb_co = options_for_sb_co.index(current_store_sel_co)
                except ValueError: st.session_state.order_store_select = None 
            selected_store_id_co = st.selectbox("Select Store *", options=options_for_sb_co, format_func=lambda x: "Select a store..." if x is None else store_options_dict_co.get(x, "Unknown Store"), key="co_store_select_sb_key_v6", index=current_idx_sb_co)
            st.session_state.order_store_select = selected_store_id_co
    st.markdown("---"); st.markdown("<h4><span class='material-symbols-outlined'>playlist_add</span> Add Products to Order</h4>", unsafe_allow_html=True)
    
    # Define callback for adding item to order - CORRECTED INDENTATION
    def add_item_to_order_cb_co_v6(): # Using _v6 suffix
        if st.session_state.current_product_id_symplanta and st.session_state.current_quantity_order > 0:
            product_info_co_v6 = products_df[products_df['ProductVariantID'] == st.session_state.current_product_id_symplanta]
            if product_info_co_v6.empty: st.error("Selected product variant not found. Please re-select.", icon="❌"); return
            product_info_co_v6 = product_info_co_v6.iloc[0]
            existing_item_idx_co_v6 = next((i for i, item in enumerate(st.session_state.order_line_items) if item['ProductVariantID'] == st.session_state.current_product_id_symplanta), -1)
            if existing_item_idx_co_v6 != -1:
                st.session_state.order_line_items[existing_item_idx_co_v6]['Quantity'] += st.session_state.current_quantity_order
                st.session_state.order_line_items[existing_item_idx_co_v6]['LineTotal'] = st.session_state.order_line_items[existing_item_idx_co_v6]['Quantity'] * st.session_state.order_line_items[existing_item_idx_co_v6]['UnitPrice']
                st.toast(f"Updated quantity for {product_info_co_v6['ProductName']} ({product_info_co_v6['UnitOfMeasure']}).", icon="🔄")
            else:
                st.session_state.order_line_items.append({"ProductVariantID": product_info_co_v6['ProductVariantID'], "SKU": product_info_co_v6['SKU'], "ProductName": product_info_co_v6['ProductName'], "Quantity": st.session_state.current_quantity_order, "UnitOfMeasure": product_info_co_v6['UnitOfMeasure'], "UnitPrice": float(product_info_co_v6['UnitPrice']), "LineTotal": st.session_state.current_quantity_order * float(product_info_co_v6['UnitPrice']), "ImageURL": product_info_co_v6['ImageURL']})
                st.toast(f"Added {product_info_co_v6['ProductName']} ({product_info_co_v6['UnitOfMeasure']}) to order.", icon="✅")
            st.session_state.current_quantity_order = 1
        else: st.warning("Please select a product and specify quantity > 0.", icon="⚠️")

    if products_df.empty: st.error("Product catalog `symplanta_products_with_images.csv` is empty or not found.", icon="🚫")
    else:
        categories_list_co_v6 = ["All Categories"] + sorted(products_df['Category'].unique().tolist())
        selected_category_filter_co_v6 = st.selectbox("Filter by Product Category", options=categories_list_co_v6, key="co_prod_cat_filter_key_v6")
        filtered_products_co_v6 = products_df.copy()
        if selected_category_filter_co_v6 != "All Categories": filtered_products_co_v6 = products_df[products_df['Category'] == selected_category_filter_co_v6]
        if filtered_products_co_v6.empty: st.info(f"No products for category: {selected_category_filter_co_v6}" if selected_category_filter_co_v6 != "All Categories" else "No products available.", icon="ℹ️"); product_variant_options_co_v6 = {}
        else: product_variant_options_co_v6 = { row['ProductVariantID']: f"{row['ProductName']} ({row['UnitOfMeasure']}) - ₹{row['UnitPrice']:.2f}" for index, row in filtered_products_co_v6.iterrows()}
        col_prod_co_v6, col_qty_co_v6, col_add_btn_co_v6 = st.columns([3, 1, 1.2])
        with col_prod_co_v6:
            current_prod_variant_id_co_sess_v6 = st.session_state.current_product_id_symplanta;
            options_prod_sb_co_v6 = [None] + list(product_variant_options_co_v6.keys()); current_prod_idx_sb_co_v6 = 0
            if current_prod_variant_id_co_sess_v6 in product_variant_options_co_v6:
                try: current_prod_idx_sb_co_v6 = options_prod_sb_co_v6.index(current_prod_variant_id_co_sess_v6)
                except ValueError: st.session_state.current_product_id_symplanta = None
            else: st.session_state.current_product_id_symplanta = None; current_prod_idx_sb_co_v6 = 0
            selected_prod_variant_id_co_v6 = st.selectbox("Select Product (Name & Size) *", options=options_prod_sb_co_v6, format_func=lambda x: "Choose a product..." if x is None else product_variant_options_co_v6.get(x, "Invalid Product"), key="co_prod_variant_select_actual_key_v6", index=current_prod_idx_sb_co_v6)
            st.session_state.current_product_id_symplanta = selected_prod_variant_id_co_v6
        with col_qty_co_v6: st.session_state.current_quantity_order = st.number_input("Quantity *", min_value=1, value=st.session_state.current_quantity_order, step=1, key="co_qty_input_key_v6")
        with col_add_btn_co_v6: st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True); st.button("➕ Add to Order", on_click=add_item_to_order_cb_co_v6, key="co_add_item_btn_key_v6")
    
    if st.session_state.order_line_items:
        st.markdown("---"); st.markdown("<h4><span class='material-symbols-outlined'>receipt_long</span> Current Order Items</h4>", unsafe_allow_html=True)
        for i_item_co_v6, item_data_co_v6 in enumerate(st.session_state.order_line_items):
            item_cols_co_v6 = st.columns([1, 3, 1, 1.5, 1.5, 0.5])
            with item_cols_co_v6[0]:
                if item_data_co_v6.get("ImageURL") and isinstance(item_data_co_v6.get("ImageURL"), str) and item_data_co_v6.get("ImageURL").startswith("http"): st.image(item_data_co_v6["ImageURL"], width=50)
                else: st.markdown("<span class='material-symbols-outlined' style='font-size:36px; color: var(--gg-grey-300);'>image_not_supported</span>", unsafe_allow_html=True)
            item_cols_co_v6[1].markdown(f"**{item_data_co_v6['ProductName']}** ({item_data_co_v6['SKU']}) <br><small>{item_data_co_v6['UnitOfMeasure']}</small>", unsafe_allow_html=True)
            item_cols_co_v6[2].markdown(f"{item_data_co_v6['Quantity']}"); item_cols_co_v6[3].markdown(f"₹{item_data_co_v6['UnitPrice']:.2f}"); item_cols_co_v6[4].markdown(f"**₹{item_data_co_v6['LineTotal']:.2f}**")
            if item_cols_co_v6[5].button("➖", key=f"co_delete_item_key_v6_{i_item_co_v6}", help="Remove item"): st.session_state.order_line_items.pop(i_item_co_v6); st.rerun()
            if i_item_co_v6 < len(st.session_state.order_line_items) -1 : st.divider()
        subtotal_co_v6 = sum(item['LineTotal'] for item in st.session_state.order_line_items)
        col_summary1_co_v6, col_summary2_co_v6 = st.columns(2)
        with col_summary1_co_v6:
            st.session_state.order_discount = st.number_input("Discount (₹)", value=st.session_state.order_discount, min_value=0.0, step=10.0, key="co_discount_val_key_v6")
            st.session_state.order_tax = st.number_input("Tax (₹)", value=st.session_state.order_tax, min_value=0.0, step=5.0, key="co_tax_val_key_v6", help="Total tax amount")
        grand_total_co_v6 = subtotal_co_v6 - st.session_state.order_discount + st.session_state.order_tax
        with col_summary2_co_v6: st.markdown(f"<div style='text-align:right; margin-top:20px;'><p style='margin-bottom:2px;'>Subtotal:  <strong>₹{subtotal_co_v6:,.2f}</strong></p><p style='margin-bottom:2px;color:var(--danger-color);'>Discount:  - ₹{st.session_state.order_discount:,.2f}</p><p style='margin-bottom:2px;'>Tax:  + ₹{st.session_state.order_tax:,.2f}</p><h4 style='margin-top:5px;border-top:1px solid var(--border-color);padding-top:5px;'>Grand Total:  ₹{grand_total_co_v6:,.2f}</h4></div>", unsafe_allow_html=True)
        st.session_state.order_notes = st.text_area("Order Notes / Payment Mode / Expected Delivery", value=st.session_state.order_notes, key="co_notes_val_key_v6", placeholder="E.g., UPI, Deliver by Tuesday")
        
        if st.button("✅ Submit Order", key="co_submit_order_btn_key_v6", type="primary", use_container_width=True): # Unique key
            final_store_id_co_submit_v6 = st.session_state.order_store_select 
            if not final_store_id_co_submit_v6: st.error("Store selection is mandatory.", icon="🏬")
            elif not st.session_state.order_line_items: st.error("Cannot submit an empty order.", icon="🛒")
            else:
                global orders_df, order_summary_df # Moved to be the first line in this specific 'else' block
                
                store_name_co_submit_v6 = "N/A" 
                store_info_submit_v6 = stores_df[stores_df['StoreID'] == final_store_id_co_submit_v6]
                if not store_info_submit_v6.empty: store_name_co_submit_v6 = store_info_submit_v6['StoreName'].iloc[0]
                else: st.error("Selected store details not found.", icon="❌"); st.stop()
                
                current_subtotal_submit_v6 = sum(item['LineTotal'] for item in st.session_state.order_line_items)
                current_discount_submit_v6 = st.session_state.order_discount 
                current_tax_submit_v6 = st.session_state.order_tax         
                current_grand_total_submit_v6 = current_subtotal_submit_v6 - current_discount_submit_v6 + current_tax_submit_v6
                current_notes_submit_v6 = st.session_state.order_notes.strip()
                salesperson_name_display_co_submit_v6 = current_user_auth["username"] # ensure this is defined

                new_order_id_submit_v6 = generate_order_id(); order_date_submit_final_v6 = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
                new_items_list_submit_v6 = [{"OrderID":new_order_id_submit_v6, "OrderDate":order_date_submit_final_v6, "Salesperson":salesperson_name_display_co_submit_v6, "StoreID":final_store_id_co_submit_v6, "ProductVariantID":item_v6['ProductVariantID'], "SKU":item_v6['SKU'], "ProductName":item_v6['ProductName'], "Quantity":item_v6['Quantity'], "UnitOfMeasure":item_v6['UnitOfMeasure'], "UnitPrice":item_v6['UnitPrice'], "LineTotal":item_v6['LineTotal']} for item_v6 in st.session_state.order_line_items]
                new_orders_df_submit_v6 = pd.DataFrame(new_items_list_submit_v6, columns=ORDERS_COLUMNS); temp_orders_df_submit_v6 = pd.concat([orders_df, new_orders_df_submit_v6], ignore_index=True)
                summary_data_submit_v6 = {"OrderID":new_order_id_submit_v6, "OrderDate":order_date_submit_final_v6, "Salesperson":salesperson_name_display_co_submit_v6, "StoreID":final_store_id_co_submit_v6, "StoreName":store_name_co_submit_v6, "Subtotal":current_subtotal_submit_v6, "DiscountAmount":current_discount_submit_v6, "TaxAmount":current_tax_submit_v6, "GrandTotal":current_grand_total_submit_v6, "Notes":current_notes_submit_v6, "PaymentMode":pd.NA, "ExpectedDeliveryDate":pd.NA}
                new_summary_df_submit_v6 = pd.DataFrame([summary_data_submit_v6], columns=ORDER_SUMMARY_COLUMNS); temp_summary_df_submit_v6 = pd.concat([order_summary_df, new_summary_df_submit_v6], ignore_index=True)
                try:
                    temp_orders_df_submit_v6.to_csv(ORDERS_FILE, index=False); temp_summary_df_submit_v6.to_csv(ORDER_SUMMARY_FILE, index=False)
                    orders_df = temp_orders_df_submit_v6; order_summary_df = temp_summary_df_submit_v6
                    st.session_state.user_message = f"Order {new_order_id_submit_v6} for '{store_name_co_submit_v6}' submitted!"; st.session_state.message_type = "success"
                    st.session_state.order_line_items = []; st.session_state.current_product_id_symplanta = None; st.session_state.current_quantity_order = 1; st.session_state.order_store_select = None; st.session_state.order_notes = ""; st.session_state.order_discount = 0.0; st.session_state.order_tax = 0.0
                    st.rerun()
                except Exception as e_co_submit_v6: st.session_state.user_message = f"Error submitting order: {e_co_submit_v6}"; st.session_state.message_type = "error"; st.rerun()
    else: st.markdown("<br>", unsafe_allow_html=True); st.info("Add products to the order to see summary and submit.", icon="💡")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Standard Pages (Attendance, Upload Activity, Allowance) ---
# (These sections should be largely okay from your previous code, ensure unique keys if issues arise)
elif nav == "Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>event_available</span> Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services for general attendance are currently illustrative.", icon="ℹ️")
    st.markdown("---"); st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col_att1_std_v6, col_att2_std_v6 = st.columns(2) # Unique var names
    common_data_att_std_v6 = {"Username": current_user_auth["username"], "Latitude": pd.NA, "Longitude": pd.NA}
    def process_general_attendance_cb_std_v6(attendance_type_param_std_v6): # Unique func name
        global attendance_df
        now_str_att_std_v6 = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_att_std_v6 = {"Type": attendance_type_param_std_v6, "Timestamp": now_str_att_std_v6, **common_data_att_std_v6}
        for col_att_std_v6 in ATTENDANCE_COLUMNS:
            if col_att_std_v6 not in new_entry_att_std_v6: new_entry_att_std_v6[col_att_std_v6] = pd.NA
        new_df_att_std_v6 = pd.DataFrame([new_entry_att_std_v6], columns=ATTENDANCE_COLUMNS)
        temp_df_att_std_v6 = pd.concat([attendance_df, new_df_att_std_v6], ignore_index=True)
        try:
            temp_df_att_std_v6.to_csv(ATTENDANCE_FILE, index=False); attendance_df = temp_df_att_std_v6
            st.session_state.user_message = f"{attendance_type_param_std_v6} recorded."; st.session_state.message_type = "success"; st.rerun()
        except Exception as e_att_std_v6: st.session_state.user_message = f"Error: {e_att_std_v6}"; st.session_state.message_type = "error"; st.rerun()
    with col_att1_std_v6:
        if st.button("✅ Check In", key="att_checkin_btn_v6", use_container_width=True, on_click=process_general_attendance_cb_std_v6, args=("Check-In",)): pass
    with col_att2_std_v6:
        if st.button("🚪 Check Out", key="att_checkout_btn_v6", use_container_width=True, on_click=process_general_attendance_cb_std_v6, args=("Check-Out",)): pass
    st.markdown('</div></div>', unsafe_allow_html=True)

elif nav == "Upload Activity":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>cloud_upload</span> Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    lat_act_std_v6, lon_act_std_v6 = pd.NA, pd.NA # Unique var names
    with st.form(key="act_photo_form_std_v6"):
        st.markdown("<h6><span class='material-symbols-outlined'>description</span> Describe Activity:</h6>", unsafe_allow_html=True)
        desc_act_std_v6 = st.text_area("Description:", key="act_desc_std_v6", help="E.g., Met Client X, Demoed Product Y.")
        st.markdown("<h6><span class='material-symbols-outlined'>photo_camera</span> Capture Photo:</h6>", unsafe_allow_html=True)
        img_buf_act_std_v6 = st.camera_input("Take picture:", key="act_cam_std_v6", help="Photo provides context.")
        submit_act_std_v6 = st.form_submit_button("⬆️ Upload & Log", type="primary")
    if submit_act_std_v6:
        if img_buf_act_std_v6 is None: st.warning("Please take a picture.", icon="📸")
        elif not desc_act_std_v6.strip(): st.warning("Please provide a description.", icon="✏️")
        else:
            global activity_log_df
            now_fname_act_std_v6 = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S"); now_disp_act_std_v6 = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            img_fname_act_std_v6 = f"{current_user_auth['username']}_activity_{now_fname_act_std_v6}.jpg"; img_path_act_std_v6 = os.path.join(ACTIVITY_PHOTOS_DIR, img_fname_act_std_v6)
            try:
                with open(img_path_act_std_v6, "wb") as f_act_std_v6: f_act_std_v6.write(img_buf_act_std_v6.getbuffer())
                new_data_act_std_v6 = {"Username":current_user_auth["username"], "Timestamp":now_disp_act_std_v6, "Description":desc_act_std_v6, "ImageFile":img_fname_act_std_v6, "Latitude":lat_act_std_v6, "Longitude":lon_act_std_v6}
                for col_act_std_v6 in ACTIVITY_LOG_COLUMNS:
                    if col_act_std_v6 not in new_data_act_std_v6: new_data_act_std_v6[col_act_std_v6] = pd.NA
                new_entry_act_std_v6 = pd.DataFrame([new_data_act_std_v6], columns=ACTIVITY_LOG_COLUMNS)
                temp_df_act_std_v6 = pd.concat([activity_log_df, new_entry_act_std_v6], ignore_index=True)
                temp_df_act_std_v6.to_csv(ACTIVITY_LOG_FILE, index=False); activity_log_df = temp_df_act_std_v6
                st.session_state.user_message = "Activity logged successfully!"; st.session_state.message_type = "success"; st.rerun()
            except Exception as e_act_std_save_v6: st.session_state.user_message = f"Error: {e_act_std_save_v6}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>receipt_long</span> Claim Allowance</h3>", unsafe_allow_html=True)
    st.markdown("<div class='form-field-label'><h6>Select Allowance Type:</h6></div>", unsafe_allow_html=True)
    type_allow_std_v6 = st.radio("AllowTypeRadioStdV6", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allow_type_std_v6", horizontal=True, label_visibility='collapsed')
    amt_allow_std_v6 = st.number_input("Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allow_amt_std_v6")
    reason_allow_std_v6 = st.text_area("Reason:", key="allow_reason_std_v6", placeholder="Justification for claim...")
    if st.button("Submit Claim", key="allow_submit_std_v6", type="primary", use_container_width=True):
        if type_allow_std_v6 and amt_allow_std_v6 > 0 and reason_allow_std_v6.strip():
            global allowance_df
            date_allow_std_v6 = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_data_allow_std_v6 = {"Username":current_user_auth["username"], "Type":type_allow_std_v6, "Amount":amt_allow_std_v6, "Reason":reason_allow_std_v6, "Date":date_allow_std_v6}
            for col_allow_std_v6 in ALLOWANCE_COLUMNS:
                if col_allow_std_v6 not in new_data_allow_std_v6: new_data_allow_std_v6[col_allow_std_v6] = pd.NA
            new_entry_allow_std_v6 = pd.DataFrame([new_data_allow_std_v6], columns=ALLOWANCE_COLUMNS)
            temp_df_allow_std_v6 = pd.concat([allowance_df, new_entry_allow_std_v6], ignore_index=True)
            try:
                temp_df_allow_std_v6.to_csv(ALLOWANCE_FILE, index=False); allowance_df = temp_df_allow_std_v6
                st.session_state.user_message = f"Allowance claim submitted."; st.session_state.message_type = "success"; st.rerun()
            except Exception as e_allow_std_save_v6: st.session_state.user_message = f"Error: {e_allow_std_save_v6}"; st.session_state.message_type = "error"; st.rerun()
        else: st.warning("Please complete all fields for allowance claim.", icon="⚠️")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Goal Pages (Sales & Payment Collection) ---
# (Ensure unique keys and variable names within these page blocks)
# (The logic from the previous full code block is largely copied here, with _v6 suffixes for keys/vars)
elif nav == "Sales Goals":
    # ... (Copy the Sales Goals elif block from the previous full code, renaming keys/vars with _v6) ...
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>flag</span> Sales Goal Tracker (2025)</h3>", unsafe_allow_html=True)
    # ... (rest of Sales Goals logic, ensuring unique keys like key="admin_sg_action_v6") ...
    st.info("Sales Goals page content to be reviewed and keys updated if necessary.", icon="🚧") # Placeholder
    st.markdown("</div>", unsafe_allow_html=True)


elif nav == "Payment Collection":
    # ... (Copy the Payment Collection elif block, renaming keys/vars with _v6) ...
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>payments</span> Payment Collection Tracker (2025)</h3>", unsafe_allow_html=True)
    st.info("Payment Collection Tracker page content to be reviewed and keys updated if necessary.", icon="🚧") # Placeholder
    st.markdown("</div>", unsafe_allow_html=True)


# --- Manage Records (ADMIN) / My Records (USER) ---
elif nav == "Manage Records" and current_user_auth['role'] == 'admin':
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>admin_panel_settings</span> Manage Records</h3>", unsafe_allow_html=True)
    admin_record_view_options_v6 = ["Employee Activity & Logs", "Submitted Sales Orders"] 
    admin_selected_record_view_v6 = st.radio( "Select Record Type:", options=admin_record_view_options_v6, horizontal=True, key="admin_manage_record_type_radio_main_v6")
    st.divider()
    if admin_selected_record_view_v6 == "Employee Activity & Logs":
        st.markdown("<h4>Employee Activity & Other Logs</h4>", unsafe_allow_html=True)
        emp_list_admin_logs_v6 = [name for name, data in USERS.items() if data["role"] != "admin"]
        if not emp_list_admin_logs_v6: st.info("No employees/salespersons found.")
        else:
            sel_emp_admin_logs_v6 = st.selectbox("Select Employee:", [""] + emp_list_admin_logs_v6, key="admin_log_emp_select_v6", format_func=lambda x: "Select an Employee..." if x == "" else x)
            if sel_emp_admin_logs_v6:
                st.markdown(f"<h4 class='employee-section-header'>Records for: {sel_emp_admin_logs_v6}</h4>", unsafe_allow_html=True)
                tab_titles_admin_log_view_v6 = ["Field Activity", "Attendance", "Allowances", "Sales Goals", "Payment Goals"]
                tabs_admin_log_view_v6 = st.tabs([f"<span class='material-symbols-outlined' style='vertical-align:middle; margin-right:5px;'>folder_shared</span> {title}" for title in tab_titles_admin_log_view_v6])
                with tabs_admin_log_view_v6[0]: data_act_v6 = activity_log_df[activity_log_df["Username"] == sel_emp_admin_logs_v6]; display_activity_logs_section(data_act_v6, sel_emp_admin_logs_v6)
                with tabs_admin_log_view_v6[1]: data_att_v6 = attendance_df[attendance_df["Username"] == sel_emp_admin_logs_v6]; display_general_attendance_logs_section(data_att_v6, sel_emp_admin_logs_v6)
                with tabs_admin_log_view_v6[2]:
                    st.markdown(f"<h5>Allowances</h5>", unsafe_allow_html=True); data_allow_v6 = allowance_df[allowance_df["Username"] == sel_emp_admin_logs_v6]
                    if not data_allow_v6.empty: st.dataframe(data_allow_v6.sort_values(by="Date",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
                    else: st.info("No allowance records.")
                with tabs_admin_log_view_v6[3]:
                    st.markdown(f"<h5>Sales Goals</h5>", unsafe_allow_html=True); data_goals_v6 = goals_df[goals_df["Username"] == sel_emp_admin_logs_v6]
                    if not data_goals_v6.empty: st.dataframe(data_goals_v6.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
                    else: st.info("No sales goals.")
                with tabs_admin_log_view_v6[4]:
                    st.markdown(f"<h5>Payment Goals</h5>", unsafe_allow_html=True); data_pay_goals_v6 = payment_goals_df[payment_goals_df["Username"] == sel_emp_admin_logs_v6]
                    if not data_pay_goals_v6.empty: st.dataframe(data_pay_goals_v6.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
                    else: st.info("No payment goals.")
            else: st.info("Select an employee to view records.")
    elif admin_selected_record_view_v6 == "Submitted Sales Orders":
        st.markdown("<h4>Submitted Sales Orders</h4>", unsafe_allow_html=True)
        if order_summary_df.empty: st.info("No orders submitted yet.")
        else:
            summary_disp_admin_orders_v6 = order_summary_df.copy(); summary_disp_admin_orders_v6['OrderDate_dt'] = pd.to_datetime(summary_disp_admin_orders_v6['OrderDate'], errors='coerce'); summary_disp_admin_orders_v6 = summary_disp_admin_orders_v6.sort_values(by="OrderDate_dt", ascending=False)
            st.markdown("<h6>Filter Orders:</h6>", unsafe_allow_html=True); f_cols_admin_ord_v6 = st.columns([1,1,2])
            sales_list_admin_ord_v6 = ["All"] + sorted(summary_disp_admin_orders_v6['Salesperson'].unique().tolist()); sel_sales_admin_ord_v6 = f_cols_admin_ord_v6[0].selectbox("Salesperson", sales_list_admin_ord_v6, key="admin_ord_filt_sales_v6")
            if sel_sales_admin_ord_v6 != "All": summary_disp_admin_orders_v6 = summary_disp_admin_orders_v6[summary_disp_admin_orders_v6['Salesperson'] == sel_sales_admin_ord_v6]
            store_filt_admin_ord_v6 = f_cols_admin_ord_v6[1].text_input("Store Name contains", key="admin_ord_filt_store_v6")
            if store_filt_admin_ord_v6.strip(): summary_disp_admin_orders_v6 = summary_disp_admin_orders_v6[summary_disp_admin_orders_v6['StoreName'].str.contains(store_filt_admin_ord_v6.strip(), case=False, na=False)]
            min_d_admin_v6 = (summary_disp_admin_orders_v6['OrderDate_dt'].min().date() if not summary_disp_admin_orders_v6.empty and pd.notna(summary_disp_admin_orders_v6['OrderDate_dt'].min()) else date.today()-timedelta(days=30))
            max_d_admin_v6 = (summary_disp_admin_orders_v6['OrderDate_dt'].max().date() if not summary_disp_admin_orders_v6.empty and pd.notna(summary_disp_admin_orders_v6['OrderDate_dt'].max()) else date.today())
            date_r_admin_ord_v6 = f_cols_admin_ord_v6[2].date_input("Date Range", value=(min_d_admin_v6,max_d_admin_v6), min_value=min_d_admin_v6, max_value=max_d_admin_v6, key="admin_ord_filt_date_v6")
            if len(date_r_admin_ord_v6)==2: start_d_admin_v6,end_d_admin_v6=date_r_admin_ord_v6; summary_disp_admin_orders_v6=summary_disp_admin_orders_v6[(summary_disp_admin_orders_v6['OrderDate_dt'].dt.date>=start_d_admin_v6)&(summary_disp_admin_orders_v6['OrderDate_dt'].dt.date<=end_d_admin_v6)]
            st.markdown("---")
            if summary_disp_admin_orders_v6.empty: st.info("No orders match filters.")
            else:
                st.markdown(f"<h6>Displaying {len(summary_disp_admin_orders_v6)} Order(s)</h6>", unsafe_allow_html=True)
                cols_summary_show_admin_v6 = ["OrderID", "OrderDate", "Salesperson", "StoreName", "GrandTotal", "Notes"]
                st.dataframe(summary_disp_admin_orders_v6[cols_summary_show_admin_v6].reset_index(drop=True),use_container_width=True,hide_index=True,column_config={"OrderDate":st.column_config.DatetimeColumn("Date",format="YYYY-MM-DD HH:mm"), "GrandTotal":st.column_config.NumberColumn("Total (₹)",format="₹ %.2f")})
                st.markdown("---"); st.markdown("<h6>View Order Details:</h6>", unsafe_allow_html=True)
                opts_ord_id_admin_v6 = [""]+summary_disp_admin_orders_v6["OrderID"].tolist()
                sel_ord_id_admin_details_v6 = st.selectbox("Select OrderID:",opts_ord_id_admin_v6, index=0 if not st.session_state.admin_order_view_selected_order_id else opts_ord_id_admin_v6.index(st.session_state.admin_order_view_selected_order_id) if st.session_state.admin_order_view_selected_order_id in opts_ord_id_admin_v6 else 0, format_func=lambda x: "Select Order ID..." if x=="" else x, key="admin_ord_details_sel_v6")
                st.session_state.admin_order_view_selected_order_id = sel_ord_id_admin_details_v6
                if sel_ord_id_admin_details_v6:
                    items_sel_admin_v6 = orders_df[orders_df['OrderID']==sel_ord_id_admin_details_v6]
                    if items_sel_admin_v6.empty: st.warning(f"No items for OrderID: {sel_ord_id_admin_details_v6}")
                    else:
                        st.markdown(f"<h6>Line Items for Order: {sel_ord_id_admin_details_v6}</h6>",unsafe_allow_html=True)
                        cols_items_show_admin_v6=["ProductName","SKU","Quantity","UnitOfMeasure","UnitPrice","LineTotal"]
                        st.dataframe(items_sel_admin_v6[cols_items_show_admin_v6].reset_index(drop=True),use_container_width=True,hide_index=True,column_config={"UnitPrice":st.column_config.NumberColumn("Price (₹)",format="₹ %.2f"),"LineTotal":st.column_config.NumberColumn("Item Total (₹)",format="₹ %.2f")})
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "My Records":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h3><span class='material-symbols-outlined'>article</span> My Records</h3>", unsafe_allow_html=True)
    my_username_rec_v6 = current_user_auth["username"] # Renamed for clarity
    st.markdown(f"<h4 class='employee-section-header'>Activity & Records for: {my_username_rec_v6}</h4>", unsafe_allow_html=True)
    tab_titles_user_rec_page_v6 = ["Field Activity", "Attendance", "Allowances", "Sales Goals", "Payment Goals"]
    if current_user_auth['role'] == 'sales_person': tab_titles_user_rec_page_v6.append("My Submitted Orders")
    tabs_user_rec_page_v6 = st.tabs([f"<span class='material-symbols-outlined' style='vertical-align:middle; margin-right:5px;'>badge</span> {title}" for title in tab_titles_user_rec_page_v6])
    with tabs_user_rec_page_v6[0]: data_act_user_v6 = activity_log_df[activity_log_df["Username"] == my_username_rec_v6]; display_activity_logs_section(data_act_user_v6, "My")
    with tabs_user_rec_page_v6[1]: data_att_user_v6 = attendance_df[attendance_df["Username"] == my_username_rec_v6]; display_general_attendance_logs_section(data_att_user_v6, "My")
    with tabs_user_rec_page_v6[2]:
        st.markdown(f"<h5>My Allowances</h5>", unsafe_allow_html=True); data_allow_user_v6 = allowance_df[allowance_df["Username"] == my_username_rec_v6]
        if not data_allow_user_v6.empty: st.dataframe(data_allow_user_v6.sort_values(by="Date",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
        else: st.info("No allowance records.")
    with tabs_user_rec_page_v6[3]:
        st.markdown(f"<h5>My Sales Goals</h5>", unsafe_allow_html=True); data_goals_user_v6 = goals_df[goals_df["Username"] == my_username_rec_v6]
        if not data_goals_user_v6.empty: st.dataframe(data_goals_user_v6.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
        else: st.info("No sales goals.")
    with tabs_user_rec_page_v6[4]:
        st.markdown(f"<h5>My Payment Goals</h5>", unsafe_allow_html=True); data_pay_goals_user_v6 = payment_goals_df[payment_goals_df["Username"] == my_username_rec_v6]
        if not data_pay_goals_user_v6.empty: st.dataframe(data_pay_goals_user_v6.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
        else: st.info("No payment goals.")
    if current_user_auth['role'] == 'sales_person' and len(tabs_user_rec_page_v6) > 5: # Check if the tab exists
        with tabs_user_rec_page_v6[5]:
            st.markdown(f"<h5>My Submitted Orders</h5>", unsafe_allow_html=True)
            my_orders_summary_v6 = order_summary_df[order_summary_df["Salesperson"] == my_username_rec_v6].copy()
            if my_orders_summary_v6.empty: st.info("You have not submitted any orders yet.")
            else:
                my_orders_summary_v6['OrderDate_dt'] = pd.to_datetime(my_orders_summary_v6['OrderDate'])
                my_orders_summary_v6 = my_orders_summary_v6.sort_values(by="OrderDate_dt", ascending=False)
                my_order_cols_to_show_v6 = ["OrderID", "OrderDate", "StoreName", "GrandTotal", "Notes"]
                st.dataframe(my_orders_summary_v6[my_order_cols_to_show_v6].reset_index(drop=True), use_container_width=True, hide_index=True,
                               column_config={"OrderDate": st.column_config.DatetimeColumn("Order Date", format="YYYY-MM-DD HH:mm"),
                                              "GrandTotal": st.column_config.NumberColumn("Total (₹)", format="₹ %.2f")})
    st.markdown("</div>", unsafe_allow_html=True)

