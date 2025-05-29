import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date # Added date for View Logs filter
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
# New files for Create Order
ORDERS_FILE = "orders.csv"
ORDER_SUMMARY_FILE = "order_summary.csv"


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
            num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude", "UnitPrice", "LineTotal", "Subtotal", "DiscountAmount", "TaxAmount", "GrandTotal"] # Added order numeric cols
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
# Columns for new order CSVs
ORDERS_COLUMNS = ["OrderID", "OrderDate", "Salesperson", "StoreID", "ProductVariantID", "SKU", "ProductName", "Quantity", "UnitOfMeasure", "UnitPrice", "LineTotal"]
ORDER_SUMMARY_COLUMNS = ["OrderID", "OrderDate", "Salesperson", "StoreID", "StoreName", "Subtotal", "DiscountAmount", "TaxAmount", "GrandTotal", "Notes", "PaymentMode", "ExpectedDeliveryDate"]


attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
activity_log_df = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS)
# Load new order dataframes
orders_df = load_data(ORDERS_FILE, ORDERS_COLUMNS)
order_summary_df = load_data(ORDER_SUMMARY_FILE, ORDER_SUMMARY_COLUMNS)


USERS = {
    "Geetali": {"password": "Geetali123", "role": "employee", "position": "Software Engineer", "profile_photo": "images/geetali.png"},
    "Nilesh": {"password": "Nilesh123", "role": "sales_person", "position": "Sales Executive", "profile_photo": "images/nilesh.png"}, # Example role for order creation
    "Vishal": {"password": "Vishal123", "role": "sales_person", "position": "Sales Executive", "profile_photo": "images/vishal.png"},
    "admin": {"password": "admin123", "role": "admin", "position": "System Administrator", "profile_photo": "images/admin.png"}
} # Simplified USERS for example
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

# Order creation specific session state items
if "order_line_items" not in st.session_state: st.session_state.order_line_items = []
if "current_product_id_symplanta" not in st.session_state: st.session_state.current_product_id_symplanta = None
if "current_quantity_order" not in st.session_state: st.session_state.current_quantity_order = 1
if "order_store_select" not in st.session_state: st.session_state.order_store_select = None
if "order_notes" not in st.session_state: st.session_state.order_notes = ""
if "order_discount" not in st.session_state: st.session_state.order_discount = 0.0
if "order_tax" not in st.session_state: st.session_state.order_tax = 0.0
if "admin_order_view_selected_order_id" not in st.session_state: st.session_state.admin_order_view_selected_order_id = None


APP_MENU_OPTIONS_BASE = ["Attendance", "Upload Activity", "Allowance", "Sales Goals", "Payment Collection"]
APP_MENU_ICONS_BASE = ['calendar2-check', 'cloud-upload', 'wallet2', 'flag', 'payments']

# Dynamically add/remove menu items based on role
current_role_for_menu = st.session_state.auth.get("role", "") # Get role before login page

if current_role_for_menu == 'admin':
    APP_MENU_OPTIONS = ["Dashboard"] + APP_MENU_OPTIONS_BASE + ["Create Order", "Manage Records"]
    APP_MENU_ICONS   = ["speedometer2"] + APP_MENU_ICONS_BASE + ["cart-plus", "gear-fill"]
elif current_role_for_menu == 'sales_person':
    APP_MENU_OPTIONS = ["Dashboard"] + APP_MENU_OPTIONS_BASE + ["Create Order", "My Records"]
    APP_MENU_ICONS   = ["speedometer2"] + APP_MENU_ICONS_BASE + ["cart-plus", "person-lines-fill"]
else: # Default employee or other roles
    APP_MENU_OPTIONS = ["Dashboard"] + APP_MENU_OPTIONS_BASE + ["My Records"]
    APP_MENU_ICONS   = ["speedometer2"] + APP_MENU_ICONS_BASE + ["person-lines-fill"]


if "active_page" not in st.session_state or st.session_state.active_page not in APP_MENU_OPTIONS:
    st.session_state.active_page = APP_MENU_OPTIONS[0]


st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
<!-- Link for Material Symbols Outlined -->
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
<style>
    :root { /* CSS Variables */ } /* Keep your existing CSS variables */
    :root {
        --kaggle-blue: #20BEFF; --kaggle-dark-text: #333333; --kaggle-light-bg: #FFFFFF;
        --kaggle-content-bg: #F5F5F5; --kaggle-gray-border: #E0E0E0; --kaggle-hover-bg: #f0f8ff;
        --kaggle-selected-bg: #E6F7FF; --kaggle-selected-text: var(--kaggle-blue);
        --kaggle-icon-color: #555555; --kaggle-icon-selected-color: var(--kaggle-blue);
        --danger-color: #dc3545; /* Bootstrap danger for discount */
        --border-color: #ced4da; /* General border color */
    }
    /* Ensure Material Symbols Outlined are styled if used in st.markdown for logout */
    .material-symbols-outlined { font-family: 'Material Symbols Outlined'; font-size: 18px; vertical-align: middle; margin-right: 8px;}
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
    .employee-section-header {font-size: 1.1rem; color: var(--kaggle-dark-text); margin-top:1rem; margin-bottom:0.5rem; border-bottom: 1px solid var(--kaggle-gray-border); padding-bottom: 0.3rem;}
    .form-field-label h6 {font-size: 0.9rem; color: #555; margin-bottom:0.2rem;}
</style>
""", unsafe_allow_html=True)

# (Plotting functions: render_goal_chart, create_donut_chart, create_team_progress_bar_chart - keep as corrected previously)
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
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.7), 4.5), dpi=110, facecolor=(0,0,0,0)) 
    ax.set_facecolor((0,0,0,0))
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
    uname = st.text_input("Username", key="login_uname_app_final_v4")
    pwd = st.text_input("Password", type="password", key="login_pwd_app_final_v4")
    if st.button("Login", key="login_button_app_final_v4", type="primary", use_container_width=True):
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
        # Use the class on the img tag via markdown if possible or style img within the container
        st.markdown(f'<img src="data:image/png;base64,..." class="user-profile-img-display">', unsafe_allow_html=True) # This line would need base64 encoded image
        # Or more simply, if st.image is styled by parent:
        st.image(profile_photo_sb, width=40)
    else:
        st.markdown(f"""<i class="bi bi-person-circle" style="font-size: 36px; color: var(--kaggle-icon-color); vertical-align:middle;"></i>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="user-details-text-block"><div>{current_username_sb}</div><div>{user_details_sb.get('position', 'N/A')}</div></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Dynamically build menu based on role (example)
    role_based_options = APP_MENU_OPTIONS.copy() # Start with base
    role_based_icons = ['calendar2-check', 'camera', 'wallet2', 'graph-up', 'cash-stack', 'journals', 'cart3'] # Base icons

    # Add "Home" if not present (for default landing)
    if "Home" not in role_based_options:
        role_based_options.insert(0, "Home")
        role_based_icons.insert(0, 'house-door') # Icon for Home

    if current_user.get("role") == "admin":
        pass # Admin might see all default options or have specific ones not covered here
    elif current_user.get("role") == "sales_person":
        pass # Sales person sees the default set
    else: # Default employee
        # Example: Remove "Create Order" if not for all employees
        if "Create Order" in role_based_options:
            idx_to_remove = role_based_options.index("Create Order")
            role_based_options.pop(idx_to_remove)
            role_based_icons.pop(idx_to_remove)


    if st.session_state.get('active_page') not in role_based_options: st.session_state.active_page = role_based_options[0]
    try: default_idx = role_based_options.index(st.session_state.active_page)
    except ValueError: default_idx = 0; st.session_state.active_page = role_based_options[0]

    selected = option_menu(
        menu_title=None, options=role_based_options, icons=role_based_icons, default_index=default_idx,
        orientation="vertical", on_change=lambda key: st.session_state.update(active_page=key),
        key='main_app_option_menu_final_v4', # Unique key
        styles={
            "container": {"padding": "5px 8px !important", "background-color": "var(--kaggle-light-bg)"},
            "icon": {"color": "var(--kaggle-icon-color)", "font-size": "18px", "margin-right":"10px"},
            "nav-link": {"font-size": "0.9rem", "text-align": "left", "margin": "4px 0px", "padding": "10px 16px", "color": "var(--kaggle-dark-text)", "border-radius": "6px", "--hover-color": "var(--kaggle-hover-bg)"},
            "nav-link-selected": {"background-color": "var(--kaggle-selected-bg)", "color": "var(--kaggle-selected-text)", "font-weight": "500"},
            "nav-link-selected > i.icon": {"color": "var(--kaggle-icon-selected-color) !important"}
        })
    st.markdown('<div class="logout-button-container-main">', unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_app_button_key_final_v4", use_container_width=True): # Unique key
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."; st.session_state.message_type = "info"
        st.session_state.active_page = role_based_options[0]; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# --- MAIN CONTENT PAGE ROUTING ---
# (PAGES: Attendance, Upload Activity Photo are assumed to be complete from previous versions)
if selected == "Attendance":
    # --- Start of Attendance Page Logic ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled. Photos for specific activities can be uploaded from 'Upload Activity Photo'.", icon="ℹ️")
    st.markdown("---")
    common_data_att = {"Username": current_user["username"], "Latitude": pd.NA, "Longitude": pd.NA}
    col1_att, col2_att = st.columns(2)
    def process_general_attendance(attendance_type): # Defined locally or globally if reused
        global attendance_df # To modify global df
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_data = {"Type": attendance_type, "Timestamp": now_str_display, **common_data_att}
        for col_name in ATTENDANCE_COLUMNS:
            if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
        new_entry = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
        
        temp_attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
        try:
            temp_attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            attendance_df = temp_attendance_df # Update global df
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."; st.session_state.message_type = "success"; st.rerun()
        except Exception as e: st.session_state.user_message = f"Error saving attendance: {e}"; st.session_state.message_type = "error"; st.rerun()
    with col1_att:
        if st.button("✅ Check In", key="check_in_btn_att_page_final_v3", use_container_width=True, type="primary"): process_general_attendance("Check-In")
    with col2_att:
        if st.button("🚪 Check Out", key="check_out_btn_att_page_final_v3", use_container_width=True, type="primary"): process_general_attendance("Check-Out")
    st.markdown('</div>', unsafe_allow_html=True) # Close card
    
# --- End of Attendance Page Logic ---

elif selected == "Upload Activity Photo":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat, current_lon = pd.NA, pd.NA # Placeholder
    with st.form(key="activity_photo_form_upload_page_final_v3"): # Ensured unique key
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description:", key="activity_desc_upload_page_final_v3")
        img_file_buffer_activity = st.camera_input("Take a picture:", key="activity_camera_upload_page_final_v3")
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo & Log")
    if submit_activity_photo:
        if img_file_buffer_activity is None: st.warning("Please take a picture.")
        elif not activity_description.strip(): st.warning("Please provide a description.")
        else:
            # No 'global activity_log_df' here
            temp_activity_log_df = activity_log_df.copy() # Operate on a copy

            now_for_filename = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S")
            now_for_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            image_filename_activity = f"{current_user['username']}_activity_{now_for_filename}.jpg"
            image_path_activity = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_activity)
            try:
                with open(image_path_activity, "wb") as f: f.write(img_file_buffer_activity.getbuffer())
                new_activity_data = {"Username": current_user['username'], "Timestamp": now_for_display, "Description": activity_description, "ImageFile": image_filename_activity, "Latitude": current_lat, "Longitude": current_lon}
                for col_name in ACTIVITY_LOG_COLUMNS: # Ensure all columns are present
                    if col_name not in new_activity_data: new_activity_data[col_name] = pd.NA
                
                new_activity_entry = pd.DataFrame([new_activity_data], columns=ACTIVITY_LOG_COLUMNS)
                temp_activity_log_df = pd.concat([temp_activity_log_df, new_activity_entry], ignore_index=True)
                
                temp_activity_log_df.to_csv(ACTIVITY_LOG_FILE, index=False)
                activity_log_df = temp_activity_log_df # Update global DataFrame AFTER successful save
                
                st.session_state.user_message = "Activity photo and log uploaded!"; st.session_state.message_type = "success"; st.rerun()
            except Exception as e: st.session_state.user_message = f"Error saving activity: {e}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Next page logic (elif selected == "Allowance":)

# Previous page logic (elif selected == "Upload Activity Photo":)
# ...

elif selected == "Allowance":
    # --- Start of Allowance Page Logic ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    a_type = st.radio("Type:", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allowance_type_radio_main_page_final_v3", horizontal=True)
    amount = st.number_input("Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_main_page_final_v3")
    reason = st.text_area("Reason:", key="allowance_reason_main_page_final_v3", placeholder="Please provide a clear justification...")
    if st.button("Submit Allowance Request", key="submit_allowance_btn_main_page_final_v3", use_container_width=True, type="primary"):
        if a_type and amount > 0 and reason.strip():
            # No 'global allowance_df' here
            temp_allowance_df = allowance_df.copy() # Work on a copy

            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry_data = {"Username": current_user["username"], "Type": a_type, "Amount": amount, "Reason": reason, "Date": date_str}
            for col_name in ALLOWANCE_COLUMNS: # Ensure all columns are present
                if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
            
            new_entry = pd.DataFrame([new_entry_data], columns=ALLOWANCE_COLUMNS)
            temp_allowance_df = pd.concat([temp_allowance_df, new_entry], ignore_index=True)
            
            try:
                temp_allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                allowance_df = temp_allowance_df # Update global DataFrame AFTER successful save
                
                st.session_state.user_message = f"Allowance for ₹{amount:.2f} submitted."; st.session_state.message_type = "success"; st.rerun()
            except Exception as e: st.session_state.user_message = f"Error submitting allowance: {e}"; st.session_state.message_type = "error"; st.rerun()
        else: st.warning("Please complete all fields with valid values.")
    st.markdown('</div>', unsafe_allow_html=True)
    # --- End of Allowance Page Logic ---

# Next page logic (elif selected == "Goal Tracker":)
# ...


    # --- End of Allowance Page Logic ---

elif selected == "Goal Tracker":
    # --- Start of Goal Tracker Page Logic ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_GOAL_YEAR = 2025; current_quarter_for_display = get_quarter_str_for_year(TARGET_GOAL_YEAR)
    status_options_gt = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"] # Renamed variable
    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True)
        admin_action_gt = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR}"], key="admin_goal_action_radio_gt_final_v3", horizontal=True)
        if admin_action_gt == "View Team Progress":
            st.markdown(f"<h5>Team Goal Progress for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            employee_users_gt = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users_gt: st.info("No employees found.")
            else:
                summary_list_sales_gt = []
                for emp_name_gt in employee_users_gt:
                    emp_current_goal_gt = goals_df[(goals_df["Username"] == emp_name_gt) & (goals_df["MonthYear"] == current_quarter_for_display)]
                    target_gt, achieved_gt, status_val_gt = 0.0, 0.0, "Not Set"
                    if not emp_current_goal_gt.empty:
                        g_data_gt = emp_current_goal_gt.iloc[0]; target_gt = float(pd.to_numeric(g_data_gt.get("TargetAmount"), errors='coerce') or 0.0)
                        achieved_gt = float(pd.to_numeric(g_data_gt.get("AchievedAmount", 0.0), errors='coerce') or 0.0); status_val_gt = g_data_gt.get("Status", "N/A")
                    summary_list_sales_gt.append({"Employee": emp_name_gt, "Target": target_gt, "Achieved": achieved_gt, "Status": status_val_gt})
                summary_df_sales_gt = pd.DataFrame(summary_list_sales_gt)
                if not summary_df_sales_gt.empty:
                    st.markdown("<h6>Individual Sales Progress:</h6>", unsafe_allow_html=True);
                    num_cols_display_admin_gt = min(3, len(summary_df_sales_gt))
                    if num_cols_display_admin_gt > 0:
                        cols_sales_admin_gt = st.columns(num_cols_display_admin_gt)
                        for idx_admin_gt, (index_admin_gt, row_admin_gt) in enumerate(summary_df_sales_gt.iterrows()):
                            progress_percent_admin_gt = (row_admin_gt['Achieved'] / row_admin_gt['Target'] * 100) if row_admin_gt['Target'] > 0 else 0.0
                            donut_fig_admin_gt = create_donut_chart(progress_percent_admin_gt, achieved_color='#28a745')
                            with cols_sales_admin_gt[idx_admin_gt % num_cols_display_admin_gt]:
                                st.markdown(f"<div class='employee-progress-item'><h6>{row_admin_gt['Employee']}</h6><p>Target: ₹{row_admin_gt['Target']:,.0f}<br>Achieved: ₹{row_admin_gt['Achieved']:,.0f}</p></div>", unsafe_allow_html=True)
                                st.pyplot(donut_fig_admin_gt, use_container_width=True); st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin-top:10px; margin-bottom:25px;'>", unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Sales Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_admin_gt = create_team_progress_bar_chart(summary_df_sales_gt, title="Team Sales Target vs. Achieved", target_col="Target", achieved_col="Achieved")
                    if team_bar_fig_admin_gt: st.pyplot(team_bar_fig_admin_gt, use_container_width=True)
                    else: st.info("No sales data to plot team bar chart.")
                else: st.info(f"No sales goals data for {current_quarter_for_display}.")
        elif admin_action_gt == f"Set/Edit Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set or Update Employee Goal ({TARGET_GOAL_YEAR} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options_admin_form_gt = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employee_options_admin_form_gt: st.warning("No employees available.")
            else:
                selected_emp_admin_form_gt = st.radio("Select Employee:", employee_options_admin_form_gt, key="goal_emp_radio_admin_gt_form_final", horizontal=True)
                quarter_options_admin_form_gt = [f"{TARGET_GOAL_YEAR}-Q{i}" for i in range(1,5)]; selected_period_admin_form_gt = st.radio("Goal Period:", quarter_options_admin_form_gt, key="goal_period_radio_admin_gt_form_final", horizontal=True)
                temp_goals_df_admin_form = goals_df.copy()
                existing_g_admin_form_gt = temp_goals_df_admin_form[(temp_goals_df_admin_form["Username"] == selected_emp_admin_form_gt) & (temp_goals_df_admin_form["MonthYear"] == selected_period_admin_form_gt)]
                g_desc_admin_form,g_target_admin_form,g_achieved_admin_form,g_status_admin_form = "",0.0,0.0,status_options_gt[0]
                if not existing_g_admin_form_gt.empty:
                    g_data_admin_form=existing_g_admin_form_gt.iloc[0]; g_desc_admin_form=g_data_admin_form.get("GoalDescription",""); g_target_admin_form=g_data_admin_form.get("TargetAmount",0.0); g_achieved_admin_form=g_data_admin_form.get("AchievedAmount",0.0); g_status_admin_form=g_data_admin_form.get("Status",status_options_gt[0])
                    st.info(f"Editing goal for {selected_emp_admin_form_gt} - {selected_period_admin_form_gt}")
                with st.form(key=f"set_goal_form_{selected_emp_admin_form_gt}_{selected_period_admin_form_gt}_admin_final_gt_form_v3"): # Unique form key
                    new_desc_admin_form=st.text_area("Goal Description",value=g_desc_admin_form,key=f"desc_gt_final_form_admin")
                    new_target_admin_form=st.number_input("Target Sales (INR)",value=float(g_target_admin_form),min_value=0.0,step=1000.0,format="%.2f",key=f"target_gt_final_form_admin")
                    new_achieved_admin_form=st.number_input("Achieved Sales (INR)",value=float(g_achieved_admin_form),min_value=0.0,step=100.0,format="%.2f",key=f"achieved_gt_final_form_admin")
                    new_status_admin_form=st.radio("Status:",status_options_gt,index=status_options_gt.index(g_status_admin_form),horizontal=True,key=f"status_gt_final_form_admin")
                    submitted_admin_form_gt=st.form_submit_button("Save Goal")
                if submitted_admin_form_gt:
                    if not new_desc_admin_form.strip(): st.warning("Description required.")
                    elif new_target_admin_form <= 0 and new_status_admin_form not in ["Cancelled","On Hold","Not Started"]: st.warning("Target > 0 required.")
                    else:
                        editable_goals_df_admin_save = goals_df.copy() # Operate on a copy
                        idx_to_update_admin_save_gt = editable_goals_df_admin_save[(editable_goals_df_admin_save["Username"] == selected_emp_admin_form_gt) & (editable_goals_df_admin_save["MonthYear"] == selected_period_admin_form_gt)].index
                        if not idx_to_update_admin_save_gt.empty:
                            editable_goals_df_admin_save.loc[idx_to_update_admin_save_gt, ["GoalDescription", "TargetAmount", "AchievedAmount", "Status"]] = [new_desc_admin_form, new_target_admin_form, new_achieved_admin_form, new_status_admin_form]
                            msg_verb_admin_save_gt="updated"
                        else:
                            new_row_df_admin_save_gt=pd.DataFrame([{"Username":selected_emp_admin_form_gt,"MonthYear":selected_period_admin_form_gt,"GoalDescription":new_desc_admin_form,"TargetAmount":new_target_admin_form,"AchievedAmount":new_achieved_admin_form,"Status":new_status_admin_form}], columns=GOALS_COLUMNS)
                            editable_goals_df_admin_save=pd.concat([editable_goals_df_admin_save,new_row_df_admin_save_gt],ignore_index=True)
                            msg_verb_admin_save_gt="set"
                        try:
                            editable_goals_df_admin_save.to_csv(GOALS_FILE,index=False)
                            goals_df = editable_goals_df_admin_save # Update global DataFrame
                            st.session_state.user_message=f"Goal for {selected_emp_admin_form_gt} ({selected_period_admin_form_gt}) {msg_verb_admin_save_gt}!"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e: st.session_state.user_message=f"Error saving goal: {e}"; st.session_state.message_type="error"; st.rerun()
    else: # Employee View
        st.markdown("<h4>My Sales Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        my_goals_emp_gt = goals_df[goals_df["Username"] == current_user["username"]].copy()
        for col_emp_gt in ["TargetAmount", "AchievedAmount"]: my_goals_emp_gt[col_emp_gt] = pd.to_numeric(my_goals_emp_gt[col_emp_gt], errors="coerce").fillna(0.0)
        current_g_df_emp_gt = my_goals_emp_gt[my_goals_emp_gt["MonthYear"] == current_quarter_for_display]
        st.markdown(f"<h5>Current Goal Period: {current_quarter_for_display}</h5>", unsafe_allow_html=True)
        if not current_g_df_emp_gt.empty:
            g_emp_gt = current_g_df_emp_gt.iloc[0]; target_amt_emp_gt = g_emp_gt["TargetAmount"]; achieved_amt_emp_gt = g_emp_gt["AchievedAmount"]
            st.markdown(f"**Description:** {g_emp_gt.get('GoalDescription', 'N/A')}")
            col_metrics_emp_gt, col_chart_emp_gt = st.columns([0.63,0.37])
            with col_metrics_emp_gt:
                sub_col1_emp_gt,sub_col2_emp_gt=st.columns(2); sub_col1_emp_gt.metric("Target",f"₹{target_amt_emp_gt:,.0f}"); sub_col2_emp_gt.metric("Achieved",f"₹{achieved_amt_emp_gt:,.0f}")
                st.metric("Status",g_emp_gt.get("Status","In Progress"),label_visibility="labeled")
            with col_chart_emp_gt:
                progress_percent_emp_gt=(achieved_amt_emp_gt/target_amt_emp_gt*100) if target_amt_emp_gt > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:-15px;'>Sales Progress</h6>",unsafe_allow_html=True)
                donut_fig_emp_gt=create_donut_chart(progress_percent_emp_gt,"Sales Progress",achieved_color='#28a745'); st.pyplot(donut_fig_emp_gt,use_container_width=True)
            st.markdown("---")
            with st.form(key=f"update_achievement_{current_user['username']}_{current_quarter_for_display}_final_gt_form_v3"): # Unique form key
                new_val_emp_gt=st.number_input("Update Achieved Amount (INR):",value=achieved_amt_emp_gt,min_value=0.0,step=100.0,format="%.2f")
                submitted_ach_emp_gt=st.form_submit_button("Update Achievement")
            if submitted_ach_emp_gt:
                editable_goals_df_emp_save = goals_df.copy()
                idx_update_emp_save_gt = editable_goals_df_emp_save[(editable_goals_df_emp_save["Username"] == current_user["username"]) & (editable_goals_df_emp_save["MonthYear"] == current_quarter_for_display)].index
                if not idx_update_emp_save_gt.empty:
                    target_amt_for_status_emp = editable_goals_df_emp_save.loc[idx_update_emp_save_gt[0], "TargetAmount"]
                    editable_goals_df_emp_save.loc[idx_update_emp_save_gt[0],"AchievedAmount"]=new_val_emp_gt
                    editable_goals_df_emp_save.loc[idx_update_emp_save_gt[0],"Status"] = "Achieved" if new_val_emp_gt >= target_amt_for_status_emp and target_amt_for_status_emp > 0 else "In Progress"
                    try:
                        editable_goals_df_emp_save.to_csv(GOALS_FILE,index=False)
                        goals_df = editable_goals_df_emp_save # Update global
                        st.session_state.user_message = "Achievement updated!"; st.session_state.message_type = "success"; st.rerun()
                    except Exception as e: st.session_state.user_message = f"Error updating: {e}"; st.session_state.message_type = "error"; st.rerun()
                else: st.session_state.user_message = "Could not find goal to update."; st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No goal set for {current_quarter_for_display}. Contact admin.")
        st.markdown("---"); st.markdown("<h5>My Past Goals (2025)</h5>", unsafe_allow_html=True)
        past_goals_emp_gt = my_goals_emp_gt[(my_goals_emp_gt["MonthYear"].str.startswith(str(TARGET_GOAL_YEAR))) & (my_goals_emp_gt["MonthYear"] != current_quarter_for_display)]
        if not past_goals_emp_gt.empty: render_goal_chart(past_goals_emp_gt, "Past Sales Goal Performance")
        else: st.info(f"No past goal records for {TARGET_GOAL_YEAR}.")
    st.markdown("</div>", unsafe_allow_html=True)
    # --- End of Goal Tracker Page Logic ---

elif selected == "Payment Collection Tracker":
    # --- Start of Payment Collection Tracker Page Logic ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Collection Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_YEAR_PAYMENT_PCT = 2025; current_quarter_display_payment_pct = get_quarter_str_for_year(TARGET_YEAR_PAYMENT_PCT)
    status_options_payment_pct = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Set & Track Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action_payment_pct = st.radio("Action:", ["View Team Progress", f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT_PCT}"], key="admin_payment_action_admin_set_pct_final_v2", horizontal=True)
        if admin_action_payment_pct == "View Team Progress":
            st.markdown(f"<h5>Team Payment Collection Progress for {current_quarter_display_payment_pct}</h5>", unsafe_allow_html=True)
            employees_payment_list_pct = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employees_payment_list_pct: st.info("No employees found.")
            else:
                summary_list_payment_pct = []
                for emp_pay_name_pct in employees_payment_list_pct:
                    record_payment_pct = payment_goals_df[(payment_goals_df["Username"]==emp_pay_name_pct)&(payment_goals_df["MonthYear"]==current_quarter_display_payment_pct)]
                    target_p_pct,achieved_p_pct,status_p_pct=0.0,0.0,"Not Set"
                    if not record_payment_pct.empty:
                        rec_payment_pct=record_payment_pct.iloc[0]; target_p_pct=float(pd.to_numeric(rec_payment_pct.get("TargetAmount"),errors='coerce') or 0.0)
                        achieved_p_pct=float(pd.to_numeric(rec_payment_pct.get("AchievedAmount"),errors='coerce') or 0.0); status_p_pct=rec_payment_pct.get("Status","N/A")
                    summary_list_payment_pct.append({"Employee":emp_pay_name_pct,"Target":target_p_pct,"Achieved":achieved_p_pct,"Status":status_p_pct})
                summary_df_payment_pct = pd.DataFrame(summary_list_payment_pct)
                if not summary_df_payment_pct.empty:
                    st.markdown("<h6>Individual Collection Progress:</h6>", unsafe_allow_html=True)
                    num_cols_payment_display_pct = min(3, len(summary_df_payment_pct))
                    if num_cols_payment_display_pct > 0:
                        cols_payment_pct = st.columns(num_cols_payment_display_pct)
                        for idx_p_pct, (index_p_pct,row_p_pct) in enumerate(summary_df_payment_pct.iterrows()):
                            progress_percent_p_pct=(row_p_pct['Achieved']/row_p_pct['Target']*100) if row_p_pct['Target'] > 0 else 0
                            donut_fig_p_pct=create_donut_chart(progress_percent_p_pct,achieved_color='#2070c0')
                            with cols_payment_pct[idx_p_pct % num_cols_payment_display_pct]:
                                st.markdown(f"<div class='employee-progress-item'><h6>{row_p_pct['Employee']}</h6><p>Target: ₹{row_p_pct['Target']:,.0f}<br>Collected: ₹{row_p_pct['Achieved']:,.0f}</p></div>",unsafe_allow_html=True)
                                st.pyplot(donut_fig_p_pct,use_container_width=True); st.markdown("<div style='margin-bottom:15px;'></div>",unsafe_allow_html=True)
                    st.markdown("<hr style='margin-top:10px;margin-bottom:25px;'>",unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Collection Performance:</h6>",unsafe_allow_html=True)
                    team_bar_fig_payment_pct = create_team_progress_bar_chart(summary_df_payment_pct,title="Team Collection Target vs. Achieved",target_col="Target",achieved_col="Achieved")
                    if team_bar_fig_payment_pct:
                        for bar_group_pct in team_bar_fig_payment_pct.axes[0].containers:
                            if bar_group_pct.get_label()=='Achieved':
                                for bar_pct in bar_group_pct: bar_pct.set_color('#2070c0')
                        st.pyplot(team_bar_fig_payment_pct,use_container_width=True)
                    else: st.info("No collection data to plot for team bar chart.")
                else: st.info(f"No payment collection data for {current_quarter_display_payment_pct}.")
        elif admin_action_payment_pct == f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT_PCT}":
            st.markdown(f"<h5>Set or Update Collection Goal ({TARGET_YEAR_PAYMENT_PCT} - Quarterly)</h5>", unsafe_allow_html=True)
            employees_for_payment_goal_pct = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employees_for_payment_goal_pct: st.warning("No employees available.")
            else:
                selected_emp_payment_pct=st.radio("Select Employee:",employees_for_payment_goal_pct,key="payment_emp_radio_admin_set_pct_final_v2_form",horizontal=True)
                quarters_payment_pct=[f"{TARGET_YEAR_PAYMENT_PCT}-Q{i}" for i in range(1,5)]; selected_period_payment_pct=st.radio("Quarter:",quarters_payment_pct,key="payment_period_radio_admin_set_pct_final_v2_form",horizontal=True)
                temp_payment_goals_df_admin_form = payment_goals_df.copy()
                existing_payment_goal_pct=temp_payment_goals_df_admin_form[(temp_payment_goals_df_admin_form["Username"]==selected_emp_payment_pct)&(temp_payment_goals_df_admin_form["MonthYear"]==selected_period_payment_pct)]
                desc_payment_pct,tgt_payment_val_pct,ach_payment_val_pct,stat_payment_pct = "",0.0,0.0,status_options_payment_pct[0]
                if not existing_payment_goal_pct.empty:
                    g_payment_pct=existing_payment_goal_pct.iloc[0]; desc_payment_pct=g_payment_pct.get("GoalDescription",""); tgt_payment_val_pct=g_payment_pct.get("TargetAmount",0.0)
                    ach_payment_val_pct=g_payment_pct.get("AchievedAmount",0.0); stat_payment_pct=g_payment_pct.get("Status",status_options_payment_pct[0])
                    st.info(f"Editing payment goal for {selected_emp_payment_pct} - {selected_period_payment_pct}")
                with st.form(f"form_payment_{selected_emp_payment_pct}_{selected_period_payment_pct}_admin_pct_final_v3"): # Unique form key
                    new_desc_payment_pct=st.text_input("Collection Goal Description",value=desc_payment_pct,key=f"desc_pay_pct_admin_final")
                    new_tgt_payment_pct=st.number_input("Target Collection (INR)",value=float(tgt_payment_val_pct),min_value=0.0,step=1000.0,key=f"target_pay_pct_admin_final")
                    new_ach_payment_pct=st.number_input("Collected Amount (INR)",value=float(ach_payment_val_pct),min_value=0.0,step=500.0,key=f"achieved_pay_pct_admin_final")
                    new_status_payment_pct=st.selectbox("Status",status_options_payment_pct,index=status_options_payment_pct.index(stat_payment_pct),key=f"status_pay_pct_admin_final")
                    submitted_payment_pct=st.form_submit_button("Save Goal")
                if submitted_payment_pct:
                    if not new_desc_payment_pct.strip(): st.warning("Description required.")
                    elif new_tgt_payment_pct <= 0 and new_status_payment_pct not in ["Cancelled","Not Started", "On Hold"]: st.warning("Target > 0 required unless status is Cancelled, Not Started or On Hold.")
                    else:
                        editable_payment_goals_df = payment_goals_df.copy()
                        existing_pg_indices_pct=editable_payment_goals_df[(editable_payment_goals_df["Username"]==selected_emp_payment_pct)&(editable_payment_goals_df["MonthYear"]==selected_period_payment_pct)].index
                        if not existing_pg_indices_pct.empty:
                            editable_payment_goals_df.loc[existing_pg_indices_pct[0]]=[selected_emp_payment_pct,selected_period_payment_pct,new_desc_payment_pct,new_tgt_payment_pct,new_ach_payment_pct,new_status_payment_pct]
                            msg_payment_pct="updated"
                        else:
                            new_row_data_p_pct={"Username":selected_emp_payment_pct,"MonthYear":selected_period_payment_pct,"GoalDescription":new_desc_payment_pct,"TargetAmount":new_tgt_payment_pct,"AchievedAmount":new_ach_payment_pct,"Status":new_status_payment_pct}
                            for col_name_pct in PAYMENT_GOALS_COLUMNS:
                                if col_name_pct not in new_row_data_p_pct: new_row_data_p_pct[col_name_pct]=pd.NA
                            new_row_df_p_pct=pd.DataFrame([new_row_data_p_pct],columns=PAYMENT_GOALS_COLUMNS)
                            editable_payment_goals_df=pd.concat([editable_payment_goals_df,new_row_df_p_pct],ignore_index=True)
                            msg_payment_pct="set"
                        try:
                            editable_payment_goals_df.to_csv(PAYMENT_GOALS_FILE,index=False)
                            payment_goals_df = editable_payment_goals_df # Update global
                            st.session_state.user_message=f"Payment goal {msg_payment_pct} for {selected_emp_payment_pct} ({selected_period_payment_pct})"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e: st.session_state.user_message=f"Error saving payment goal: {e}"; st.session_state.message_type="error"; st.rerun()
    else: # Employee View
        st.markdown("<h4>My Payment Collection Goals (2025)</h4>", unsafe_allow_html=True)
        user_goals_payment_e_pct = payment_goals_df[payment_goals_df["Username"]==current_user["username"]].copy()
        user_goals_payment_e_pct[["TargetAmount","AchievedAmount"]] = user_goals_payment_e_pct[["TargetAmount","AchievedAmount"]].apply(pd.to_numeric,errors="coerce").fillna(0.0)
        current_payment_goal_e_df_pct = user_goals_payment_e_pct[user_goals_payment_e_pct["MonthYear"]==current_quarter_display_payment_pct]
        st.markdown(f"<h5>Current Quarter: {current_quarter_display_payment_pct}</h5>", unsafe_allow_html=True)
        if not current_payment_goal_e_df_pct.empty:
            g_pay_e_pct=current_payment_goal_e_df_pct.iloc[0]; tgt_pay_e_pct=g_pay_e_pct["TargetAmount"]; ach_pay_e_pct=g_pay_e_pct["AchievedAmount"]
            st.markdown(f"**Goal:** {g_pay_e_pct.get('GoalDescription','')}")
            col_metrics_pay_e_pct,col_chart_pay_e_pct=st.columns([0.63,0.37])
            with col_metrics_pay_e_pct:
                sub_col1_pay_e_pct,sub_col2_pay_e_pct=st.columns(2); sub_col1_pay_e_pct.metric("Target",f"₹{tgt_pay_e_pct:,.0f}"); sub_col2_pay_e_pct.metric("Collected",f"₹{ach_pay_e_pct:,.0f}")
                st.metric("Status",g_pay_e_pct.get("Status","In Progress"),label_visibility="labeled")
            with col_chart_pay_e_pct:
                progress_percent_pay_e_pct=(ach_pay_e_pct/tgt_pay_e_pct*100) if tgt_pay_e_pct > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:-15px;'>Collection Progress</h6>",unsafe_allow_html=True)
                donut_fig_payment_e_pct=create_donut_chart(progress_percent_pay_e_pct,"Collection Progress",achieved_color='#2070c0'); st.pyplot(donut_fig_payment_e_pct,use_container_width=True)
            st.markdown("---")
            with st.form(key=f"update_collection_{current_user['username']}_{current_quarter_display_payment_pct}_final_pct_form_v3"): # Unique form key
                new_ach_val_payment_e_pct=st.number_input("Update Collected Amount (INR):",value=ach_pay_e_pct,min_value=0.0,step=500.0)
                submit_collection_update_e_pct=st.form_submit_button("Update Collection")
            if submit_collection_update_e_pct:
                editable_payment_goals_df_emp = payment_goals_df.copy()
                idx_pay_e_pct=editable_payment_goals_df_emp[(editable_payment_goals_df_emp["Username"]==current_user["username"])&(editable_payment_goals_df_emp["MonthYear"]==current_quarter_display_payment_pct)].index
                if not idx_pay_e_pct.empty:
                    target_for_status_pct = editable_payment_goals_df_emp.loc[idx_pay_e_pct[0], "TargetAmount"]
                    editable_payment_goals_df_emp.loc[idx_pay_e_pct[0],"AchievedAmount"]=new_ach_val_payment_e_pct
                    editable_payment_goals_df_emp.loc[idx_pay_e_pct[0],"Status"]="Achieved" if new_ach_val_payment_e_pct >= target_for_status_pct and target_for_status_pct > 0 else "In Progress"
                    try:
                        editable_payment_goals_df_emp.to_csv(PAYMENT_GOALS_FILE,index=False)
                        payment_goals_df = editable_payment_goals_df_emp # Update global
                        st.session_state.user_message = "Collection updated."; st.session_state.message_type = "success"; st.rerun()
                    except Exception as e: st.session_state.user_message = f"Error updating collection: {e}"; st.session_state.message_type = "error"; st.rerun()
                else: st.session_state.user_message = "Could not find current payment goal."; st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No collection goal for {current_quarter_display_payment_pct}.")
        st.markdown("<h5>Past Quarters</h5>", unsafe_allow_html=True)
        past_payment_goals_e_pct = user_goals_payment_e_pct[user_goals_payment_e_pct["MonthYear"]!=current_quarter_display_payment_pct]
        if not past_payment_goals_e_pct.empty: render_goal_chart(past_payment_goals_e_pct,"Past Collection Performance")
        else: st.info("No past collection goals.")
    st.markdown('</div>', unsafe_allow_html=True)
    # --- End of Payment Collection Tracker Page Logic ---

elif selected == "View Logs":
    # --- Start of View Logs Page Logic ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📊 View Logs</h3>", unsafe_allow_html=True)
    def display_activity_logs_with_photos(df_logs_display, user_name_for_header_display):
        if df_logs_display.empty: st.info(f"No activity logs for {user_name_for_header_display}."); return
        df_logs_sorted_display = df_logs_display.sort_values(by="Timestamp", ascending=False).copy()
        st.markdown(f"<h5>Field Activity Logs for: {user_name_for_header_display}</h5>", unsafe_allow_html=True)
        for index_display, row_display in df_logs_sorted_display.iterrows():
            st.markdown("---"); col_details_display, col_photo_display = st.columns([0.7, 0.3])
            with col_details_display:
                st.markdown(f"**Timestamp:** {row_display['Timestamp']}<br>**Description:** {row_display.get('Description', 'N/A')}<br>**Location:** {'Not Recorded' if pd.isna(row_display.get('Latitude')) else f"Lat: {row_display.get('Latitude'):.4f}, Lon: {row_display.get('Longitude'):.4f}"}", unsafe_allow_html=True)
                if pd.notna(row_display['ImageFile']) and row_display['ImageFile'] != "": st.caption(f"Photo ID: {row_display['ImageFile']}")
                else: st.caption("No photo for this activity.")
            with col_photo_display:
                if pd.notna(row_display['ImageFile']) and row_display['ImageFile'] != "":
                    image_path_to_display_log = os.path.join(ACTIVITY_PHOTOS_DIR, str(row_display['ImageFile']))
                    if os.path.exists(image_path_to_display_log):
                        try: st.image(image_path_to_display_log, width=150)
                        except Exception as img_e_display: st.warning(f"Img err: {img_e_display}")
                    else: st.caption(f"Img missing")
    def display_attendance_logs_view(df_logs_att_view, user_name_for_header_att_view):
        if df_logs_att_view.empty: st.warning(f"No general attendance records for {user_name_for_header_att_view}."); return
        df_logs_sorted_att_view = df_logs_att_view.sort_values(by="Timestamp", ascending=False).copy()
        st.markdown(f"<h5>General Attendance Records for: {user_name_for_header_att_view}</h5>", unsafe_allow_html=True)
        columns_to_show_att_view = ["Type", "Timestamp"]
        if 'Latitude' in df_logs_sorted_att_view.columns and 'Longitude' in df_logs_sorted_att_view.columns:
            df_logs_sorted_att_view['Location'] = df_logs_sorted_att_view.apply(
                lambda row_att_view: f"Lat: {row_att_view['Latitude']:.4f}, Lon: {row_att_view['Longitude']:.4f}"
                if pd.notna(row_att_view['Latitude']) and pd.notna(row_att_view['Longitude']) else "Not Recorded", axis=1)
            columns_to_show_att_view.append('Location')
        st.dataframe(df_logs_sorted_att_view[columns_to_show_att_view], use_container_width=True, hide_index=True)

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: View Employee Records</h4>", unsafe_allow_html=True)
        employee_name_list_logs = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
        if not employee_name_list_logs: st.info("No employees to display logs for.")
        else:
            selected_employee_log_admin = st.selectbox("Select Employee:", employee_name_list_logs, key="log_employee_select_admin_viewlogs_final")
            if selected_employee_log_admin:
                emp_activity_log_view = activity_log_df[activity_log_df["Username"] == selected_employee_log_admin]
                display_activity_logs_with_photos(emp_activity_log_view, selected_employee_log_admin)
                st.markdown("<br><hr><br>", unsafe_allow_html=True)
                emp_attendance_log_view = attendance_df[attendance_df["Username"] == selected_employee_log_admin]
                display_attendance_logs_view(emp_attendance_log_view, selected_employee_log_admin)
                st.markdown("---"); st.markdown(f"<h5>Allowances for {selected_employee_log_admin}</h5>", unsafe_allow_html=True)
                emp_allowance_log_view = allowance_df[allowance_df["Username"] == selected_employee_log_admin]
                if not emp_allowance_log_view.empty: st.dataframe(emp_allowance_log_view.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
                else: st.info("No allowance records found")
                st.markdown(f"<h5>Sales Goals for {selected_employee_log_admin}</h5>", unsafe_allow_html=True)
                emp_goals_log_view = goals_df[goals_df["Username"] == selected_employee_log_admin]
                if not emp_goals_log_view.empty: st.dataframe(emp_goals_log_view.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
                else: st.info("No sales goals records found")
                st.markdown(f"<h5>Payment Collection Goals for {selected_employee_log_admin}</h5>", unsafe_allow_html=True)
                emp_payment_goals_log_view = payment_goals_df[payment_goals_df["Username"] == selected_employee_log_admin]
                if not emp_payment_goals_log_view.empty: st.dataframe(emp_payment_goals_log_view.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
                else: st.info("No payment collection goals found")
    else: # Employee view
        st.markdown("<h4>My Records</h4>", unsafe_allow_html=True)
        my_activity_log_view = activity_log_df[activity_log_df["Username"] == current_user["username"]]
        display_activity_logs_with_photos(my_activity_log_view, current_user["username"])
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        my_attendance_log_view = attendance_df[attendance_df["Username"] == current_user["username"]]
        display_attendance_logs_view(my_attendance_log_view, current_user["username"])
        st.markdown("---"); st.markdown("<h5>My Allowances</h5>", unsafe_allow_html=True)
        my_allowance_log_view = allowance_df[allowance_df["Username"] == current_user["username"]]
        if not my_allowance_log_view.empty: st.dataframe(my_allowance_log_view.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
        else: st.info("No allowance records found for you")
        st.markdown("<h5>My Sales Goals</h5>", unsafe_allow_html=True)
        my_goals_log_view = goals_df[goals_df["Username"] == current_user["username"]]
        if not my_goals_log_view.empty: st.dataframe(my_goals_log_view.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
        else: st.info("No sales goals records found for you")
        st.markdown("<h5>My Payment Collection Goals</h5>", unsafe_allow_html=True)
        my_payment_goals_log_view = payment_goals_df[payment_goals_df["Username"] == current_user["username"]]
        if not my_payment_goals_log_view.empty: st.dataframe(my_payment_goals_log_view.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
        else: st.info("No payment collection goals records found for you")
    st.markdown('</div>', unsafe_allow_html=True)
    # --- End of View Logs Page Logic ---

# Previous page logic (elif selected == "View Logs":)
# # Previous page logic ...

elif selected == "Create Order":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🛒 Create New Order</h3>", unsafe_allow_html=True)

    # --- Initialize necessary session state variables for this page ---
    # (Keep this initialization block as it was)
    if "co_order_line_items" not in st.session_state: st.session_state.co_order_line_items = []
    if "co_current_product_id" not in st.session_state: st.session_state.co_current_product_id = None
    if "co_current_quantity" not in st.session_state: st.session_state.co_current_quantity = 1
    if "co_selected_store_id" not in st.session_state: st.session_state.co_selected_store_id = None
    if "co_order_notes" not in st.session_state: st.session_state.co_order_notes = ""
    if "co_order_discount" not in st.session_state: st.session_state.co_order_discount = 0.0
    if "co_order_tax" not in st.session_state: st.session_state.co_order_tax = 0.0


    # --- Load Data for Order Creation ---
    # (Keep this data loading block as it was)
    try:
        stores_df_co = pd.read_csv("agri_stores.csv")
        products_df_co = pd.read_csv("symplanta_products_with_images.csv")
        if stores_df_co.empty: st.warning("`agri_stores.csv` is empty. Store selection affected.", icon="🏬")
        if products_df_co.empty: st.warning("`symplanta_products_with_images.csv` is empty. Product selection affected.", icon="🛍️")
    except FileNotFoundError:
        st.error("Critical Error: Order data files not found. Order creation cannot proceed.")
        st.markdown('</div>', unsafe_allow_html=True); st.stop()
    except pd.errors.EmptyDataError:
        st.error("Critical Error: Order data files are empty. Order creation cannot proceed.")
        st.markdown('</div>', unsafe_allow_html=True); st.stop()
    except Exception as e:
        st.error(f"Error loading order data files: {e}")
        st.markdown('</div>', unsafe_allow_html=True); st.stop()

    # --- Order Header ---
    # (Keep this section as it was)
    st.markdown("<h4>Order Header</h4>", unsafe_allow_html=True)
    col_header1_co, col_header2_co = st.columns(2)
    with col_header1_co:
        order_date_display_co = get_current_time_in_tz().strftime("%Y-%m-%d")
        st.text_input("Order Date", value=order_date_display_co, disabled=True, key="co_order_date_display_vfinal")
        st.text_input("Salesperson", value=current_user["username"], disabled=True, key="co_salesperson_display_vfinal")
    with col_header2_co:
        store_options_co = {"": "Select a store..."} 
        if not stores_df_co.empty:
            for _, row in stores_df_co.iterrows(): store_options_co[row['StoreID']] = f"{row['StoreName']} ({row['StoreID']})"
        st.session_state.co_selected_store_id = st.selectbox(
            "Select Store *", options=list(store_options_co.keys()),
            format_func=lambda x: store_options_co[x],
            index=list(store_options_co.keys()).index(st.session_state.co_selected_store_id) if st.session_state.co_selected_store_id in store_options_co else 0,
            key="co_store_selector_vfinal_2"
        )
    st.markdown("---")
    st.markdown("<h4><span class='material-symbols-outlined' style='vertical-align:middle; font-size:20px;'>playlist_add</span> Add Products to Order</h4>", unsafe_allow_html=True)

    # --- Product Selection and Adding to Order ---
    # (Keep this section as it was, with unique keys)
    if not products_df_co.empty:
        categories_list_co = ["All Categories"] + sorted(products_df_co['Category'].dropna().unique().tolist())
        selected_category_filter_co = st.selectbox("Filter by Product Category", options=categories_list_co, key="co_category_filter_vfinal")
        filtered_products_df_co = products_df_co.copy()
        if selected_category_filter_co != "All Categories": filtered_products_df_co = products_df_co[products_df_co['Category'] == selected_category_filter_co]
        product_variant_options_co = {"": "Choose a product..."}
        if not filtered_products_df_co.empty:
            for _, row in filtered_products_df_co.iterrows(): product_variant_options_co[row['SKU']] = ... # Using SKU as the key # and later: # "ProductVariantID": item_data['SKU'], # Storing SKU as ProductVariantID or add a new SKU field = f"{row['ProductName']} ({row.get('UnitOfMeasure', 'N/A')}) - ₹{pd.to_numeric(row.get('Price'), errors='coerce'):.2f}"
        col_prod_co, col_qty_co, col_add_btn_co = st.columns([3, 1, 1.5])
        with col_prod_co:
            st.session_state.co_current_product_id = st.selectbox(
                "Select Product (Name & Size) *", options=list(product_variant_options_co.keys()),
                format_func=lambda x: product_variant_options_co[x],
                index=list(product_variant_options_co.keys()).index(st.session_state.co_current_product_id) if st.session_state.co_current_product_id in product_variant_options_co else 0,
                key="co_product_selector_vfinal_2"
            )
        with col_qty_co: st.session_state.co_current_quantity = st.number_input("Quantity *", min_value=1, value=st.session_state.co_current_quantity, step=1, key="co_quantity_input_vfinal_2")
        with col_add_btn_co:
            st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
            if st.button("➕ Add to Order", key="co_add_item_button_vfinal_2", type="primary", use_container_width=True, disabled=(not st.session_state.co_current_product_id or st.session_state.co_current_product_id == "")):
                if st.session_state.co_current_product_id and st.session_state.co_current_quantity > 0:
                    product_info_co = products_df_co[products_df_co['ProductVariantID'] == st.session_state.co_current_product_id]
                    if not product_info_co.empty:
                        product_data_co = product_info_co.iloc[0]; unit_price_co = pd.to_numeric(product_data_co.get('UnitPrice'), errors='coerce')
                        if pd.notna(unit_price_co):
                            existing_item_indices = [i for i, item in enumerate(st.session_state.co_order_line_items) if item['ProductVariantID'] == st.session_state.co_current_product_id]
                            if existing_item_indices:
                                idx = existing_item_indices[0]; st.session_state.co_order_line_items[idx]['Quantity'] += st.session_state.co_current_quantity
                                st.session_state.co_order_line_items[idx]['LineTotal'] = st.session_state.co_order_line_items[idx]['Quantity'] * st.session_state.co_order_line_items[idx]['UnitPrice']
                                st.toast(f"Updated quantity for {product_data_co['ProductName']}.", icon="🔄")
                            else:
                                st.session_state.co_order_line_items.append({"ProductVariantID": product_data_co['ProductVariantID'], "SKU": product_data_co.get('SKU', 'N/A'), "ProductName": product_data_co['ProductName'], "Quantity": st.session_state.co_current_quantity, "UnitOfMeasure": product_data_co.get('UnitOfMeasure', 'Unit'), "UnitPrice": unit_price_co, "LineTotal": st.session_state.co_current_quantity * unit_price_co, "ImageURL": product_data_co.get('ImageURL')})
                                st.toast(f"Added {product_data_co['ProductName']} to order.", icon="✅")
                            st.session_state.co_current_quantity = 1; st.rerun()
                        else: st.warning("Selected product has an invalid price.", icon="⚠️")
                    else: st.error("Selected product variant not found.", icon="❌")
                else: st.warning("Please select a product and specify quantity > 0.", icon="⚠️")
    else: st.info("Product catalog is empty. Cannot add products.", icon="ℹ️")

    # --- Display Current Order Items ---
    # (Keep this section as it was)
    if st.session_state.co_order_line_items:
        st.markdown("---"); st.markdown("<h4><span class='material-symbols-outlined' style='vertical-align:middle; font-size:20px;'>receipt_long</span> Current Order Items</h4>", unsafe_allow_html=True)
        for i, item_co_disp in enumerate(st.session_state.co_order_line_items):
            col_img_disp, col_desc_disp, col_qty_disp, col_price_disp, col_total_disp, col_del_disp = st.columns([0.8, 3, 0.7, 1.2, 1.2, 0.5], gap="small")
            with col_img_disp:
                img_url = item_co_disp.get("ImageURL")
                if img_url and isinstance(img_url, str) and img_url.startswith("http"): st.image(img_url, width=50)
                else: st.markdown("<div style='width:50px; height:50px; background-color:#f0f0f0; display:flex; align-items:center; justify-content:center;'><i class='bi bi-card-image' style='font-size:24px; color:#ccc;'></i></div>", unsafe_allow_html=True)
            col_desc_disp.markdown(f"**{item_co_disp['ProductName']}** <small>({item_co_disp.get('SKU', 'No SKU')})</small><br><small>Unit: {item_co_disp.get('UnitOfMeasure', 'N/A')}</small>", unsafe_allow_html=True)
            col_qty_disp.markdown(f"{item_co_disp['Quantity']}"); col_price_disp.markdown(f"₹{item_co_disp['UnitPrice']:.2f}"); col_total_disp.markdown(f"**₹{item_co_disp['LineTotal']:.2f}**")
            if col_del_disp.button("🗑️", key=f"co_delete_item_key_final_v2_{i}", help="Remove item"): st.session_state.co_order_line_items.pop(i); st.rerun()
            if i < len(st.session_state.co_order_line_items) - 1 : st.markdown("<hr style='margin: 0.3rem 0; opacity:0.2;'>", unsafe_allow_html=True)
        st.markdown("---")
        subtotal_co = sum(item['LineTotal'] for item in st.session_state.co_order_line_items)
        col_summary1_co, col_summary2_co = st.columns([2,3])
        with col_summary1_co:
            st.session_state.co_order_discount = st.number_input("Discount (₹)", value=st.session_state.co_order_discount, min_value=0.0, max_value=subtotal_co, step=10.0, key="co_discount_val_final_v2")
            st.session_state.co_order_tax = st.number_input("Tax (₹)", value=st.session_state.co_order_tax, min_value=0.0, step=5.0, key="co_tax_val_final_v2", help="Total tax amount")
        grand_total_co = subtotal_co - st.session_state.co_order_discount + st.session_state.co_order_tax
        with col_summary2_co:
            st.markdown(f"""<div style='text-align:right; padding-top: 10px;'><p style='margin-bottom:2px; font-size:0.9rem;'>Subtotal:   <strong>₹{subtotal_co:,.2f}</strong></p><p style='margin-bottom:2px; font-size:0.9rem; color:var(--danger-color);'>Discount:   - ₹{st.session_state.co_order_discount:,.2f}</p><p style='margin-bottom:2px; font-size:0.9rem;'>Tax:   + ₹{st.session_state.co_order_tax:,.2f}</p><h4 style='margin-top:8px; border-top:1.5px solid var(--kaggle-gray-border); padding-top:8px;'>Grand Total:   ₹{grand_total_co:,.2f}</h4></div>""", unsafe_allow_html=True)
        st.session_state.co_order_notes = st.text_area("Order Notes / Payment Mode / Expected Delivery", value=st.session_state.co_order_notes, key="co_notes_val_final_v2", placeholder="E.g., Payment via UPI, Deliver by Tuesday evening")
        
        # --- Order Submission Logic ---
        if st.button("✅ Submit Order", key="co_submit_order_btn_final_v2", type="primary", use_container_width=True, disabled=(not st.session_state.co_selected_store_id or st.session_state.co_selected_store_id == "")):
            if not st.session_state.co_selected_store_id or st.session_state.co_selected_store_id == "":
                st.error("Store selection is mandatory to submit the order.", icon="🏬")
            elif not st.session_state.co_order_line_items:
                st.error("Cannot submit an empty order. Please add products.", icon="🛒")
            else:
                # Removed: global orders_df, order_summary_df
                # Work with copies and then reassign globals
                temp_orders_df_submit = orders_df.copy()
                temp_order_summary_df_submit = order_summary_df.copy()

                store_name_co_submit = "N/A"
                store_info_submit = stores_df_co[stores_df_co['StoreID'] == st.session_state.co_selected_store_id]
                if not store_info_submit.empty: store_name_co_submit = store_info_submit['StoreName'].iloc[0]
                else: st.error("Selected store details not found. Cannot submit order.", icon="❌"); st.stop()

                def generate_order_id(): return f"ORD-{get_current_time_in_tz().strftime('%Y%m%d%H%M%S')}-{np.random.randint(100,999)}"
                new_order_id = generate_order_id()
                order_date_final = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
                salesperson_final = current_user["username"]

                new_order_items_list = []
                for item_data in st.session_state.co_order_line_items:
                    new_order_items_list.append({
                        "OrderID": new_order_id, "OrderDate": order_date_final, "Salesperson": salesperson_final,
                        "StoreID": st.session_state.co_selected_store_id,
                        "ProductVariantID": item_data['ProductVariantID'], "SKU": item_data.get('SKU', pd.NA),
                        "ProductName": item_data['ProductName'], "Quantity": item_data['Quantity'],
                        "UnitOfMeasure": item_data.get('UnitOfMeasure', pd.NA),
                        "UnitPrice": item_data['UnitPrice'], "LineTotal": item_data['LineTotal']
                    })
                
                new_orders_to_add_df = pd.DataFrame(new_order_items_list, columns=ORDERS_COLUMNS)
                temp_orders_df_submit = pd.concat([temp_orders_df_submit, new_orders_to_add_df], ignore_index=True)

                summary_data_final = {
                    "OrderID": new_order_id, "OrderDate": order_date_final, "Salesperson": salesperson_final,
                    "StoreID": st.session_state.co_selected_store_id, "StoreName": store_name_co_submit,
                    "Subtotal": subtotal_co, "DiscountAmount": st.session_state.co_order_discount,
                    "TaxAmount": st.session_state.co_order_tax, "GrandTotal": grand_total_co,
                    "Notes": st.session_state.co_order_notes.strip(),
                    "PaymentMode": pd.NA, "ExpectedDeliveryDate": pd.NA
                }
                new_summary_to_add_df = pd.DataFrame([summary_data_final], columns=ORDER_SUMMARY_COLUMNS)
                temp_order_summary_df_submit = pd.concat([temp_order_summary_df_submit, new_summary_to_add_df], ignore_index=True)

                try:
                    temp_orders_df_submit.to_csv(ORDERS_FILE, index=False)
                    temp_order_summary_df_submit.to_csv(ORDER_SUMMARY_FILE, index=False)
                    
                    # Update global dataframes AFTER successful save
                    orders_df = temp_orders_df_submit
                    order_summary_df = temp_order_summary_df_submit
                    
                    st.session_state.user_message = f"Order {new_order_id} for '{store_name_co_submit}' submitted successfully!"
                    st.session_state.message_type = "success"
                    
                    # Clear order form state
                    st.session_state.co_order_line_items = []
                    st.session_state.co_current_product_id = None
                    st.session_state.co_current_quantity = 1
                    st.session_state.co_selected_store_id = None
                    st.session_state.co_order_notes = ""
                    st.session_state.co_order_discount = 0.0
                    st.session_state.co_order_tax = 0.0
                    st.rerun()
                except Exception as e_submit:
                    st.session_state.user_message = f"Error submitting order: {e_submit}"
                    st.session_state.message_type = "error"; st.rerun()
    else:
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("Add products to the order to see summary and proceed to submission.", icon="💡")

    st.markdown('</div>', unsafe_allow_html=True)
    # --- End of Create Order Page Logic ---

elif selected == "Home" or selected is None: # Default/Fallback Page
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(f"🏠 Welcome Home, {current_user['username']}!")
    st.write("Select an option from the sidebar to manage your activities.")
    st.markdown('</div>', unsafe_allow_html=True)
