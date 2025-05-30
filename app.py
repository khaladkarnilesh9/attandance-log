import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta, date
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
try:
    tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'. Please correct it.")
    st.stop()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ... (other file paths using BASE_DIR) ...
ATTENDANCE_FILE = os.path.join(BASE_DIR, "attendance.csv")
ALLOWANCE_FILE = os.path.join(BASE_DIR, "allowances.csv")
GOALS_FILE = os.path.join(BASE_DIR, "goals.csv")
PAYMENT_GOALS_FILE = os.path.join(BASE_DIR, "payment_goals.csv")
ACTIVITY_LOG_FILE = os.path.join(BASE_DIR, "activity_log.csv")
ACTIVITY_PHOTOS_DIR = os.path.join(BASE_DIR, "activity_photos")
ORDERS_FILE = os.path.join(BASE_DIR, "orders.csv")
ORDER_SUMMARY_FILE = os.path.join(BASE_DIR, "order_summary.csv")
STORES_FILE = os.path.join(BASE_DIR, "agri_stores.csv")
PRODUCTS_FILE = os.path.join(BASE_DIR, "symplanta_products_with_images.csv")


if not os.path.exists(ACTIVITY_PHOTOS_DIR): os.makedirs(ACTIVITY_PHOTOS_DIR, exist_ok=True)

# --- UTILITY FUNCTIONS ---
def get_quarter_str_for_year(year):
    current_time = get_current_time_in_tz() # Get current time once
    month = current_time.month             # Get month once

    if 1 <= month <= 3:
        return f"{year}-Q1"
    elif 4 <= month <= 6:
        return f"{year}-Q2"
    elif 7 <= month <= 9:
        return f"{year}-Q3"
    else: # This covers months 10, 11, 12
        return f"{year}-Q4"
def load_data(path, columns):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        try:
            df = pd.read_csv(path)
            for col in columns:
                if col not in df.columns: df[col] = pd.NA
            num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude", "UnitPrice", "LineTotal", "Subtotal", "DiscountAmount", "TaxAmount", "GrandTotal"]
            for nc in num_cols:
                if nc in df.columns: df[nc] = pd.to_numeric(df[nc], errors='coerce')
            return df
        except Exception: return pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
        try: df.to_csv(path, index=False)
        except Exception: pass
        return df

# --- Column Definitions ---
ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]
ORDERS_COLUMNS = ["OrderID", "OrderDate", "Salesperson", "StoreID", "ProductVariantID", "SKU", "ProductName", "Quantity", "UnitOfMeasure", "UnitPrice", "LineTotal"]
ORDER_SUMMARY_COLUMNS = ["OrderID", "OrderDate", "Salesperson", "StoreID", "StoreName", "Subtotal", "DiscountAmount", "TaxAmount", "GrandTotal", "Notes", "PaymentMode", "ExpectedDeliveryDate"]
STORES_COLUMNS = ["StoreID", "StoreName"]
PRODUCTS_COLUMNS = ["ProductVariantID", "ProductName", "SKU", "Category", "UnitOfMeasure", "Price", "ImageURL"]

# --- Load Global DataFrames ---
attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
activity_log_df = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS)
orders_df = load_data(ORDERS_FILE, ORDERS_COLUMNS)
order_summary_df = load_data(ORDER_SUMMARY_FILE, ORDER_SUMMARY_COLUMNS)
stores_df = load_data(STORES_FILE, STORES_COLUMNS)
products_df = load_data(PRODUCTS_FILE, PRODUCTS_COLUMNS)

# --- USER AUTHENTICATION & INFO ---
USERS = {
    "Geetali": {"password": "Geetali123", "role": "employee", "position": "Software Engineer", "profile_photo": "images/geetali.png"},
    "Nilesh": {"password": "Nilesh123", "role": "sales_person", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "Vishal": {"password": "Vishal123", "role": "sales_person", "position": "Sales Executive", "profile_photo": "images/vishal.png"},
    "admin": {"password": "admin123", "role": "admin", "position": "System Administrator", "profile_photo": "images/admin.png"}
}
images_dir = os.path.join(BASE_DIR, "images")
if not os.path.exists(images_dir): os.makedirs(images_dir, exist_ok=True)
if PILLOW_INSTALLED: # ... (Pillow image generation logic as before) ...
    for user_key, user_data in USERS.items():
        img_file_name = user_data.get("profile_photo")
        if img_file_name:
            img_path = os.path.join(images_dir, img_file_name)
            if not os.path.exists(img_path):
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

# --- SESSION STATE INITIALIZATION ---
if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}
# Order creation specific session state items
if "co_order_line_items" not in st.session_state: st.session_state.co_order_line_items = []
if "co_current_product_id" not in st.session_state: st.session_state.co_current_product_id = None
if "co_current_quantity" not in st.session_state: st.session_state.co_current_quantity = 1
if "co_selected_store_id" not in st.session_state: st.session_state.co_selected_store_id = None
if "co_order_notes" not in st.session_state: st.session_state.co_order_notes = ""
if "co_order_discount" not in st.session_state: st.session_state.co_order_discount = 0.0
if "co_order_tax" not in st.session_state: st.session_state.co_order_tax = 0.0
if "admin_order_view_selected_order_id" not in st.session_state: st.session_state.admin_order_view_selected_order_id = None


# --- DEFINE BASE MENU OPTIONS GLOBALLY --- <<<< MOVED HERE
APP_MENU_OPTIONS_BASE = ["Attendance", "Upload Activity Photo", "Allowance", "Goal Tracker", "Payment Collection Tracker"]
APP_MENU_ICONS_BASE = ['calendar2-check', 'camera', 'wallet2', 'graph-up', 'cash-stack']

# Initialize active_page; this might be refined after login based on role
if "active_page" not in st.session_state:
    # Default to a generic first page before role-specific menu is built
    st.session_state.active_page = "Home" if "Home" in APP_MENU_OPTIONS_BASE else APP_MENU_OPTIONS_BASE[0]


# --- CSS STYLING ---
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
<style>
    /* ... (Your full CSS block - KEEP AS IS) ... */
    :root {
        --kaggle-blue: #20BEFF; --kaggle-dark-text: #333333; --kaggle-light-bg: #FFFFFF;
        --kaggle-content-bg: #F5F5F5; --kaggle-gray-border: #E0E0E0; --kaggle-hover-bg: #f0f8ff;
        --kaggle-selected-bg: #E6F7FF; --kaggle-selected-text: var(--kaggle-blue);
        --kaggle-icon-color: #555555; --kaggle-icon-selected-color: var(--kaggle-blue);
        --danger-color: #dc3545; --border-color: #ced4da; 
    }
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
    .sidebar-user-info-block img { 
        border-radius: 50%; width: 40px; height: 40px; object-fit: cover; border: 1px solid var(--kaggle-gray-border);
    }
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

# --- PLOTTING FUNCTIONS ---
# ... (Keep your plotting functions as corrected previously) ...
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
    uname = st.text_input("Username", key="login_uname_final_v6") # Unique key
    pwd = st.text_input("Password", type="password", key="login_pwd_final_v6") # Unique key
    if st.button("Login", key="login_button_final_v6", type="primary", use_container_width=True):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = "Login successful!"; st.session_state.message_type = "success"
            
            # Determine dynamic menu options AFTER role is set
            current_role_login = st.session_state.auth.get("role", "")
            dynamic_app_menu_options = APP_MENU_OPTIONS_BASE.copy()
            dynamic_app_menu_icons = APP_MENU_ICONS_BASE.copy()

            # Ensure "Home" is always the first option after login
            if "Home" not in dynamic_app_menu_options:
                dynamic_app_menu_options.insert(0, "Home")
                dynamic_app_menu_icons.insert(0, 'house-door') # Icon for Home

            if current_role_login == 'admin':
                if "Create Order" not in dynamic_app_menu_options: dynamic_app_menu_options.append("Create Order"); dynamic_app_menu_icons.append("cart-plus")
                if "Manage Records" not in dynamic_app_menu_options: dynamic_app_menu_options.append("Manage Records"); dynamic_app_menu_icons.append("gear-fill")
            elif current_role_login == 'sales_person':
                if "Create Order" not in dynamic_app_menu_options: dynamic_app_menu_options.append("Create Order"); dynamic_app_menu_icons.append("cart-plus")
                if "My Records" not in dynamic_app_menu_options: dynamic_app_menu_options.append("My Records"); dynamic_app_menu_icons.append("person-lines-fill")
            else: # Default employee (non-admin, non-sales_person)
                if "My Records" not in dynamic_app_menu_options: dynamic_app_menu_options.append("My Records"); dynamic_app_menu_icons.append("person-lines-fill")
                # Remove "Create Order" if it was in base and this role shouldn't see it
                if "Create Order" in dynamic_app_menu_options:
                    try:
                        idx_co = dynamic_app_menu_options.index("Create Order")
                        dynamic_app_menu_options.pop(idx_co)
                        dynamic_app_menu_icons.pop(idx_co)
                    except ValueError: pass # Should not happen if check is done

            st.session_state.APP_MENU_OPTIONS_FOR_USER = dynamic_app_menu_options
            st.session_state.APP_MENU_ICONS_FOR_USER = dynamic_app_menu_icons
            st.session_state.active_page = dynamic_app_menu_options[0] # Default to first available page
            st.rerun()
        else: st.error("Invalid username or password.")
    st.markdown("</div>", unsafe_allow_html=True); st.stop()

# --- MAIN APPLICATION AFTER LOGIN ---
current_user = st.session_state.auth
message_placeholder_main = st.empty()
if st.session_state.user_message:
    message_placeholder_main.markdown(f"<div class='custom-notification {st.session_state.message_type}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
    st.session_state.user_message = None; st.session_state.message_type = None

# --- SIDEBAR IMPLEMENTATION ---
with st.sidebar:
    st.markdown("""<div class="sidebar-app-header"><h2>TrackSphere</h2><p>Field Activity Tracker</p></div>""", unsafe_allow_html=True)
    current_username_sb = current_user.get('username', 'Guest')
    user_details_sb = USERS.get(current_username_sb, {})
    profile_photo_sb_filename = user_details_sb.get("profile_photo", "") # Filename from USERS dict

    st.markdown('<div class="sidebar-user-info-block">', unsafe_allow_html=True)
    if profile_photo_sb_filename and PILLOW_INSTALLED:
        full_profile_photo_path_sb = os.path.join(BASE_DIR, profile_photo_sb_filename) # Construct full path
        if os.path.exists(full_profile_photo_path_sb):
            st.image(full_profile_photo_path_sb, width=40)
        else: # Fallback if image file not found
            st.markdown(f"""<i class="bi bi-person-circle" style="font-size: 36px; color: var(--kaggle-icon-color); vertical-align:middle;"></i>""", unsafe_allow_html=True)
    else: # Fallback if no photo path or Pillow not installed
        st.markdown(f"""<i class="bi bi-person-circle" style="font-size: 36px; color: var(--kaggle-icon-color); vertical-align:middle;"></i>""", unsafe_allow_html=True)
    
    st.markdown(f"""<div class="user-details-text-block"><div>{current_username_sb}</div><div>{user_details_sb.get('position', 'N/A')}</div></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Use dynamically set menu options from session state, with a fallback to base if not set (e.g. first run after login)
    active_menu_options = st.session_state.get("APP_MENU_OPTIONS_FOR_USER", APP_MENU_OPTIONS_BASE + ["Home"]) # Add Home as a general fallback
    active_menu_icons = st.session_state.get("APP_MENU_ICONS_FOR_USER", APP_MENU_ICONS_BASE + ['house-door'])

    if st.session_state.get('active_page') not in active_menu_options:
        st.session_state.active_page = active_menu_options[0] if active_menu_options else "Home"
    
    try: default_idx = active_menu_options.index(st.session_state.active_page)
    except ValueError: default_idx = 0; st.session_state.active_page = active_menu_options[0] if active_menu_options else "Home"

    selected = option_menu(
        menu_title=None, options=active_menu_options, icons=active_menu_icons, default_index=default_idx,
        orientation="vertical", on_change=lambda key: st.session_state.update(active_page=key),
        key='main_app_option_menu_final_v6', # Incremented key
        styles={
            "container": {"padding": "5px 8px !important", "background-color": "var(--kaggle-light-bg)"},
            "icon": {"color": "var(--kaggle-icon-color)", "font-size": "18px", "margin-right":"10px"},
            "nav-link": {"font-size": "0.9rem", "text-align": "left", "margin": "4px 0px", "padding": "10px 16px", "color": "var(--kaggle-dark-text)", "border-radius": "6px", "--hover-color": "var(--kaggle-hover-bg)"},
            "nav-link-selected": {"background-color": "var(--kaggle-selected-bg)", "color": "var(--kaggle-selected-text)", "font-weight": "500"},
            "nav-link-selected > i.icon": {"color": "var(--kaggle-icon-selected-color) !important"}
        })
    st.markdown('<div class="logout-button-container-main">', unsafe_allow_html=True)
    if st.button("🚪 Logout", key="logout_app_button_key_final_v6", use_container_width=True): # Incremented key
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.session_state.user_message = "Logged out successfully."; st.session_state.message_type = "info"
        st.session_state.active_page = "Home" # Default to home after logout
        st.session_state.APP_MENU_OPTIONS_FOR_USER = ["Home"] + APP_MENU_OPTIONS_BASE # Reset to a basic menu
        st.session_state.APP_MENU_ICONS_FOR_USER = ["house-door"] + APP_MENU_ICONS_BASE
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN CONTENT PAGE ROUTING ---
# (Logic for all pages: Attendance, Upload Activity Photo, Allowance, Goal Tracker, Payment Tracker, View Logs, Create Order, Home)
# This section should contain the full, corrected logic for each page as previously established.

if selected == "Home":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(f"🏠 Welcome Home, {current_user['username']}!")
    st.write("Select an option from the sidebar to manage your activities.")
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Attendance":
    # --- (Copied and adapted Attendance logic) ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled. Photos for specific activities can be uploaded from 'Upload Activity Photo'.", icon="ℹ️")
    st.markdown("---")
    common_data_att = {"Username": current_user["username"], "Latitude": pd.NA, "Longitude": pd.NA}
    col1_att, col2_att = st.columns(2)
    def process_general_attendance(attendance_type):
        temp_attendance_df = attendance_df.copy()
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_data = {"Type": attendance_type, "Timestamp": now_str_display, **common_data_att}
        for col_name in ATTENDANCE_COLUMNS:
            if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
        new_entry = pd.DataFrame([new_entry_data], columns=ATTENDANCE_COLUMNS)
        temp_attendance_df = pd.concat([temp_attendance_df, new_entry], ignore_index=True)
        try:
            temp_attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            globals()['attendance_df'] = temp_attendance_df
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."; st.session_state.message_type = "success"; st.rerun()
        except Exception as e: st.session_state.user_message = f"Error saving attendance: {e}"; st.session_state.message_type = "error"; st.rerun()
    with col1_att:
        if st.button("✅ Check In", key="check_in_btn_att_page_final_v6", use_container_width=True, type="primary"): process_general_attendance("Check-In")
    with col2_att:
        if st.button("🚪 Check Out", key="check_out_btn_att_page_final_v6", use_container_width=True, type="primary"): process_general_attendance("Check-Out")
    st.markdown('</div>', unsafe_allow_html=True)


elif selected == "Upload Activity Photo":
    # --- (Copied and adapted Upload Activity Photo logic) ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat, current_lon = pd.NA, pd.NA
    with st.form(key="activity_photo_form_upload_page_final_v6"):
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description:", key="activity_desc_upload_page_final_v6")
        img_file_buffer_activity = st.camera_input("Take a picture:", key="activity_camera_upload_page_final_v6")
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo & Log")
    if submit_activity_photo:
        if img_file_buffer_activity is None: st.warning("Please take a picture.")
        elif not activity_description.strip(): st.warning("Please provide a description.")
        else:
            temp_activity_log_df = activity_log_df.copy()
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
                temp_activity_log_df = pd.concat([temp_activity_log_df, new_activity_entry], ignore_index=True)
                temp_activity_log_df.to_csv(ACTIVITY_LOG_FILE, index=False)
                globals()['activity_log_df'] = temp_activity_log_df
                st.session_state.user_message = "Activity photo and log uploaded!"; st.session_state.message_type = "success"; st.rerun()
            except Exception as e: st.session_state.user_message = f"Error saving activity: {e}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Allowance":
    # --- (Copied and adapted Allowance logic) ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    a_type = st.radio("Type:", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allowance_type_radio_main_page_final_v6", horizontal=True)
    amount = st.number_input("Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_main_page_final_v6")
    reason = st.text_area("Reason:", key="allowance_reason_main_page_final_v6", placeholder="Please provide a clear justification...")
    if st.button("Submit Allowance Request", key="submit_allowance_btn_main_page_final_v6", use_container_width=True, type="primary"):
        if a_type and amount > 0 and reason.strip():
            temp_allowance_df = allowance_df.copy()
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry_data = {"Username": current_user["username"], "Type": a_type, "Amount": amount, "Reason": reason, "Date": date_str}
            for col_name in ALLOWANCE_COLUMNS:
                if col_name not in new_entry_data: new_entry_data[col_name] = pd.NA
            new_entry = pd.DataFrame([new_entry_data], columns=ALLOWANCE_COLUMNS)
            temp_allowance_df = pd.concat([temp_allowance_df, new_entry], ignore_index=True)
            try:
                temp_allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                globals()['allowance_df'] = temp_allowance_df
                st.session_state.user_message = f"Allowance for ₹{amount:.2f} submitted."; st.session_state.message_type = "success"; st.rerun()
            except Exception as e: st.session_state.user_message = f"Error submitting allowance: {e}"; st.session_state.message_type = "error"; st.rerun()
        else: st.warning("Please complete all fields with valid values.")
    st.markdown('</div>', unsafe_allow_html=True)

elif selected == "Goal Tracker":
    # --- (Copied and adapted Goal Tracker logic) ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_GOAL_YEAR_GT = 2025; current_quarter_for_display_gt = get_quarter_str_for_year(TARGET_GOAL_YEAR_GT)
    status_options_gt_page = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True)
        admin_action_gt_page = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR_GT}"], key="admin_goal_action_radio_gt_page_final_v2", horizontal=True) # Key update
        if admin_action_gt_page == "View Team Progress":
            st.markdown(f"<h5>Team Goal Progress for {current_quarter_for_display_gt}</h5>", unsafe_allow_html=True)
            employee_users_gt_page = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users_gt_page: st.info("No employees found.")
            else:
                summary_list_sales_gt_page = []
                for emp_name_gt_page in employee_users_gt_page:
                    emp_current_goal_gt_page = goals_df[(goals_df["Username"] == emp_name_gt_page) & (goals_df["MonthYear"] == current_quarter_for_display_gt)]
                    target_gt_page, achieved_gt_page, status_val_gt_page = 0.0, 0.0, "Not Set"
                    if not emp_current_goal_gt_page.empty:
                        g_data_gt_page = emp_current_goal_gt_page.iloc[0]
                        target_gt_page = float(pd.to_numeric(g_data_gt_page.get("TargetAmount"), errors='coerce') or 0.0)
                        achieved_gt_page = float(pd.to_numeric(g_data_gt_page.get("AchievedAmount", 0.0), errors='coerce') or 0.0)
                        status_val_gt_page = g_data_gt_page.get("Status", "N/A")
                    summary_list_sales_gt_page.append({"Employee": emp_name_gt_page, "Target": target_gt_page, "Achieved": achieved_gt_page, "Status": status_val_gt_page})
                summary_df_sales_gt_page = pd.DataFrame(summary_list_sales_gt_page)
                if not summary_df_sales_gt_page.empty:
                    st.markdown("<h6>Individual Sales Progress:</h6>", unsafe_allow_html=True);
                    num_cols_display_admin_gt_page = min(3, len(summary_df_sales_gt_page))
                    if num_cols_display_admin_gt_page > 0:
                        cols_sales_admin_gt_page = st.columns(num_cols_display_admin_gt_page)
                        for idx_admin_gt_page, (index_admin_gt_page, row_admin_gt_page) in enumerate(summary_df_sales_gt_page.iterrows()):
                            progress_percent_admin_gt_page = (row_admin_gt_page['Achieved'] / row_admin_gt_page['Target'] * 100) if row_admin_gt_page['Target'] > 0 else 0.0
                            donut_fig_admin_gt_page = create_donut_chart(progress_percent_admin_gt_page, achieved_color='#28a745')
                            with cols_sales_admin_gt_page[idx_admin_gt_page % num_cols_display_admin_gt_page]:
                                st.markdown(f"<div class='employee-progress-item'><h6>{row_admin_gt_page['Employee']}</h6><p>Target: ₹{row_admin_gt_page['Target']:,.0f}<br>Achieved: ₹{row_admin_gt_page['Achieved']:,.0f}</p></div>", unsafe_allow_html=True)
                                st.pyplot(donut_fig_admin_gt_page, use_container_width=True); st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
                    st.markdown("<hr style='margin-top:10px; margin-bottom:25px;'>", unsafe_allow_html=True)
                    st.markdown("<h6>Overall Team Sales Performance:</h6>", unsafe_allow_html=True)
                    team_bar_fig_admin_gt_page = create_team_progress_bar_chart(summary_df_sales_gt_page, title="Team Sales Target vs. Achieved", target_col="Target", achieved_col="Achieved")
                    if team_bar_fig_admin_gt_page: st.pyplot(team_bar_fig_admin_gt_page, use_container_width=True)
                    else: st.info("No sales data to plot team bar chart.")
                else: st.info(f"No sales goals data for {current_quarter_for_display_gt}.")
        elif admin_action_gt_page == f"Set/Edit Goal for {TARGET_GOAL_YEAR_GT}":
            st.markdown(f"<h5>Set or Update Employee Goal ({TARGET_GOAL_YEAR_GT} - Quarterly)</h5>", unsafe_allow_html=True)
            employee_options_admin_form_gt_page = [u for u,d in USERS.items() if d["role"]=="employee"]
            if not employee_options_admin_form_gt_page: st.warning("No employees available.")
            else:
                selected_emp_admin_form_gt_page = st.radio("Select Employee:", employee_options_admin_form_gt_page, key="goal_emp_radio_admin_gt_form_final_page_v2", horizontal=True) # Key update
                quarter_options_admin_form_gt_page = [f"{TARGET_GOAL_YEAR_GT}-Q{i}" for i in range(1,5)]; selected_period_admin_form_gt_page = st.radio("Goal Period:", quarter_options_admin_form_gt_page, key="goal_period_radio_admin_gt_form_final_page_v2", horizontal=True) # Key update
                temp_goals_df_admin_form_page = goals_df.copy()
                existing_g_admin_form_gt_page = temp_goals_df_admin_form_page[(temp_goals_df_admin_form_page["Username"] == selected_emp_admin_form_gt_page) & (temp_goals_df_admin_form_page["MonthYear"] == selected_period_admin_form_gt_page)]
                g_desc_admin_form_page,g_target_admin_form_page,g_achieved_admin_form_page,g_status_admin_form_page = "",0.0,0.0,status_options_gt_page[0]
                if not existing_g_admin_form_gt_page.empty:
                    g_data_admin_form_page=existing_g_admin_form_gt_page.iloc[0]; g_desc_admin_form_page=g_data_admin_form_page.get("GoalDescription",""); g_target_admin_form_page=g_data_admin_form_page.get("TargetAmount",0.0); g_achieved_admin_form_page=g_data_admin_form_page.get("AchievedAmount",0.0); g_status_admin_form_page=g_data_admin_form_page.get("Status",status_options_gt_page[0])
                    st.info(f"Editing goal for {selected_emp_admin_form_gt_page} - {selected_period_admin_form_gt_page}")
                with st.form(key=f"set_goal_form_{selected_emp_admin_form_gt_page}_{selected_period_admin_form_gt_page}_admin_final_gt_form_page_v2"): # Key update
                    new_desc_admin_form_page=st.text_area("Goal Description",value=g_desc_admin_form_page,key=f"desc_gt_final_form_admin_page_v2") # Key update
                    new_target_admin_form_page=st.number_input("Target Sales (INR)",value=float(g_target_admin_form_page),min_value=0.0,step=1000.0,format="%.2f",key=f"target_gt_final_form_admin_page_v2") # Key update
                    new_achieved_admin_form_page=st.number_input("Achieved Sales (INR)",value=float(g_achieved_admin_form_page),min_value=0.0,step=100.0,format="%.2f",key=f"achieved_gt_final_form_admin_page_v2") # Key update
                    new_status_admin_form_page=st.radio("Status:",status_options_gt_page,index=status_options_gt_page.index(g_status_admin_form_page),horizontal=True,key=f"status_gt_final_form_admin_page_v2") # Key update
                    submitted_admin_form_gt_page=st.form_submit_button("Save Goal")
                if submitted_admin_form_gt_page:
                    if not new_desc_admin_form_page.strip(): st.warning("Description required.")
                    elif new_target_admin_form_page <= 0 and new_status_admin_form_page not in ["Cancelled","On Hold","Not Started"]: st.warning("Target > 0 required.")
                    else:
                        editable_goals_df_admin_save_page = goals_df.copy()
                        idx_to_update_admin_save_gt_page = editable_goals_df_admin_save_page[(editable_goals_df_admin_save_page["Username"] == selected_emp_admin_form_gt_page) & (editable_goals_df_admin_save_page["MonthYear"] == selected_period_admin_form_gt_page)].index
                        if not idx_to_update_admin_save_gt_page.empty:
                            editable_goals_df_admin_save_page.loc[idx_to_update_admin_save_gt_page, ["GoalDescription", "TargetAmount", "AchievedAmount", "Status"]] = [new_desc_admin_form_page, new_target_admin_form_page, new_achieved_admin_form_page, new_status_admin_form_page]
                            msg_verb_admin_save_gt_page="updated"
                        else:
                            new_row_df_admin_save_gt_page=pd.DataFrame([{"Username":selected_emp_admin_form_gt_page,"MonthYear":selected_period_admin_form_gt_page,"GoalDescription":new_desc_admin_form_page,"TargetAmount":new_target_admin_form_page,"AchievedAmount":new_achieved_admin_form_page,"Status":new_status_admin_form_page}], columns=GOALS_COLUMNS)
                            editable_goals_df_admin_save_page=pd.concat([editable_goals_df_admin_save_page,new_row_df_admin_save_gt_page],ignore_index=True)
                            msg_verb_admin_save_gt_page="set"
                        try:
                            editable_goals_df_admin_save_page.to_csv(GOALS_FILE,index=False)
                            globals()['goals_df'] = editable_goals_df_admin_save_page
                            st.session_state.user_message=f"Goal for {selected_emp_admin_form_gt_page} ({selected_period_admin_form_gt_page}) {msg_verb_admin_save_gt_page}!"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e: st.session_state.user_message=f"Error saving goal: {e}"; st.session_state.message_type="error"; st.rerun()
    else: # Employee View
        st.markdown("<h4>My Sales Goals (2025 - Quarterly)</h4>", unsafe_allow_html=True)
        my_goals_e_gt_page = goals_df[goals_df["Username"] == current_user["username"]].copy()
        for col_e_gt_page in ["TargetAmount", "AchievedAmount"]: my_goals_e_gt_page[col_e_gt_page] = pd.to_numeric(my_goals_e_gt_page[col_e_gt_page], errors="coerce").fillna(0.0)
        current_g_df_e_gt_page = my_goals_e_gt_page[my_goals_e_gt_page["MonthYear"] == current_quarter_for_display]
        st.markdown(f"<h5>Current Goal Period: {current_quarter_for_display}</h5>", unsafe_allow_html=True)
        if not current_g_df_e_gt_page.empty:
            g_e_gt_page = current_g_df_e_gt_page.iloc[0]; target_amt_e_gt_page = g_e_gt_page["TargetAmount"]; achieved_amt_e_gt_page = g_e_gt_page["AchievedAmount"]
            st.markdown(f"**Description:** {g_e_gt_page.get('GoalDescription', 'N/A')}")
            col_metrics_e_gt_page, col_chart_e_gt_page = st.columns([0.63,0.37])
            with col_metrics_e_gt_page:
                sub_col1_e_gt_page,sub_col2_e_gt_page=st.columns(2); sub_col1_e_gt_page.metric("Target",f"₹{target_amt_e_gt_page:,.0f}"); sub_col2_e_gt_page.metric("Achieved",f"₹{achieved_amt_e_gt_page:,.0f}")
                st.metric("Status",g_e_gt_page.get("Status","In Progress"),label_visibility="labeled")
            with col_chart_e_gt_page:
                progress_percent_e_gt_page=(achieved_amt_e_gt_page/target_amt_e_gt_page*100) if target_amt_e_gt_page > 0 else 0.0
                st.markdown(f"<h6 style='text-align:center;margin-bottom:0px;margin-top:-15px;'>Sales Progress</h6>",unsafe_allow_html=True)
                donut_fig_e_gt_page=create_donut_chart(progress_percent_e_gt_page,"Sales Progress",achieved_color='#28a745'); st.pyplot(donut_fig_e_gt_page,use_container_width=True)
            st.markdown("---")
            with st.form(key=f"update_achievement_{current_user['username']}_{current_quarter_for_display}_final_gt_form_page_v2"): # Key update
                new_val_e_gt_page=st.number_input("Update Achieved Amount (INR):",value=achieved_amt_e_gt_page,min_value=0.0,step=100.0,format="%.2f")
                submitted_ach_e_gt_page=st.form_submit_button("Update Achievement")
            if submitted_ach_e_gt_page:
                editable_goals_df_emp_save_page = goals_df.copy()
                idx_update_emp_save_gt_page = editable_goals_df_emp_save_page[(editable_goals_df_emp_save_page["Username"] == current_user["username"]) & (editable_goals_df_emp_save_page["MonthYear"] == current_quarter_for_display)].index
                if not idx_update_emp_save_gt_page.empty:
                    target_amt_for_status_emp_page = editable_goals_df_emp_save_page.loc[idx_update_emp_save_gt_page[0], "TargetAmount"]
                    editable_goals_df_emp_save_page.loc[idx_update_emp_save_gt_page[0],"AchievedAmount"]=new_val_e_gt_page
                    editable_goals_df_emp_save_page.loc[idx_update_emp_save_gt_page[0],"Status"] = "Achieved" if new_val_e_gt_page >= target_amt_for_status_emp_page and target_amt_for_status_emp_page > 0 else "In Progress"
                    try:
                        editable_goals_df_emp_save_page.to_csv(GOALS_FILE,index=False)
                        globals()['goals_df'] = editable_goals_df_emp_save_page
                        st.session_state.user_message = "Achievement updated!"; st.session_state.message_type = "success"; st.rerun()
                    except Exception as e: st.session_state.user_message = f"Error updating: {e}"; st.session_state.message_type = "error"; st.rerun()
                else: st.session_state.user_message = "Could not find goal to update."; st.session_state.message_type = "error"; st.rerun()
        else: st.info(f"No goal set for {current_quarter_for_display}. Contact admin.")
        st.markdown("---"); st.markdown("<h5>My Past Goals (2025)</h5>", unsafe_allow_html=True)
        past_goals_e_gt_page = my_goals_e_gt_page[(my_goals_e_gt_page["MonthYear"].str.startswith(str(TARGET_GOAL_YEAR))) & (my_goals_e_gt_page["MonthYear"] != current_quarter_for_display)]
        if not past_goals_e_gt_page.empty: render_goal_chart(past_goals_e_gt_page, "Past Sales Goal Performance")
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
        admin_action_payment_pct = st.radio("Action:", ["View Team Progress", f"Set/Edit Collection Target for {TARGET_YEAR_PAYMENT_PCT}"], key="admin_payment_action_admin_set_pct_final_v5", horizontal=True)
        if admin_action_payment_pct == "View Team Progress":
            # ... (Full Admin View Team Progress logic for Payment Collection) ...
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
                            progress_percent_p_pct=(row_p_pct['Achieved']/row_p_pct['Target']*100) if row_p_pct['Target'] > 0 else 0.0
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
                selected_emp_payment_pct=st.radio("Select Employee:",employees_for_payment_goal_pct,key="payment_emp_radio_admin_set_pct_final_v5_form",horizontal=True) # Key update
                quarters_payment_pct=[f"{TARGET_YEAR_PAYMENT_PCT}-Q{i}" for i in range(1,5)]; selected_period_payment_pct=st.radio("Quarter:",quarters_payment_pct,key="payment_period_radio_admin_set_pct_final_v5_form",horizontal=True) # Key update
                temp_payment_goals_df_admin_form_pct = payment_goals_df.copy()
                existing_payment_goal_pct=temp_payment_goals_df_admin_form_pct[(temp_payment_goals_df_admin_form_pct["Username"]==selected_emp_payment_pct)&(temp_payment_goals_df_admin_form_pct["MonthYear"]==selected_period_payment_pct)]
                desc_payment_pct,tgt_payment_val_pct,ach_payment_val_pct,stat_payment_pct = "",0.0,0.0,status_options_payment_pct[0]
                if not existing_payment_goal_pct.empty:
                    g_payment_pct=existing_payment_goal_pct.iloc[0]; desc_payment_pct=g_payment_pct.get("GoalDescription",""); tgt_payment_val_pct=g_payment_pct.get("TargetAmount",0.0)
                    ach_payment_val_pct=g_payment_pct.get("AchievedAmount",0.0); stat_payment_pct=g_payment_pct.get("Status",status_options_payment_pct[0])
                    st.info(f"Editing payment goal for {selected_emp_payment_pct} - {selected_period_payment_pct}")
                with st.form(f"form_payment_{selected_emp_payment_pct}_{selected_period_payment_pct}_admin_pct_final_v6"): # Key update
                    new_desc_payment_pct=st.text_input("Collection Goal Description",value=desc_payment_pct,key=f"desc_pay_pct_admin_final_v4") # Key update
                    new_tgt_payment_pct=st.number_input("Target Collection (INR)",value=float(tgt_payment_val_pct),min_value=0.0,step=1000.0,key=f"target_pay_pct_admin_final_v4") # Key update
                    new_ach_payment_pct=st.number_input("Collected Amount (INR)",value=float(ach_payment_val_pct),min_value=0.0,step=500.0,key=f"achieved_pay_pct_admin_final_v4") # Key update
                    new_status_payment_pct=st.selectbox("Status",status_options_payment_pct,index=status_options_payment_pct.index(stat_payment_pct),key=f"status_pay_pct_admin_final_v4") # Key update
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
                            globals()['payment_goals_df'] = editable_payment_goals_df
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
            with st.form(key=f"update_collection_{current_user['username']}_{current_quarter_display_payment_pct}_final_pct_form_v6"): # Key update
                new_ach_val_payment_e_pct=st.number_input("Update Collected Amount (INR):",value=ach_pay_e_pct,min_value=0.0,step=500.0)
                submit_collection_update_e_pct=st.form_submit_button("Update Collection")
            if submit_collection_update_e_pct:
                editable_payment_goals_df_emp = payment_goals_df.copy()
                idx_pay_e_pct=editable_payment_goals_df_emp[(editable_payment_goals_df_emp["Username"]==current_user["username"])&(editable_payment_goals_df_emp["MonthYear"]==current_quarter_display_payment_pct)].index
                if not idx_pay_e_pct.empty:
                    target_for_status_pct_emp = editable_payment_goals_df_emp.loc[idx_pay_e_pct[0], "TargetAmount"]
                    editable_payment_goals_df_emp.loc[idx_pay_e_pct[0],"AchievedAmount"]=new_ach_val_payment_e_pct
                    editable_payment_goals_df_emp.loc[idx_pay_e_pct[0],"Status"]="Achieved" if new_ach_val_payment_e_pct >= target_for_status_pct_emp and target_for_status_pct_emp > 0 else "In Progress"
                    try:
                        editable_payment_goals_df_emp.to_csv(PAYMENT_GOALS_FILE,index=False)
                        globals()['payment_goals_df'] = editable_payment_goals_df_emp
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
    def display_activity_logs_with_photos_vl(df_logs_display, user_name_for_header_display):
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
    def display_attendance_logs_view_vl(df_logs_att_view, user_name_for_header_att_view):
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
        employee_name_list_logs_vl = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
        if not employee_name_list_logs_vl: st.info("No employees to display logs for.")
        else:
            selected_employee_log_admin_vl = st.selectbox("Select Employee:", employee_name_list_logs_vl, key="log_employee_select_admin_viewlogs_final_v4") # Key update
            if selected_employee_log_admin_vl:
                emp_activity_log_view_vl = activity_log_df[activity_log_df["Username"] == selected_employee_log_admin_vl]
                display_activity_logs_with_photos_vl(emp_activity_log_view_vl, selected_employee_log_admin_vl)
                st.markdown("<br><hr><br>", unsafe_allow_html=True)
                emp_attendance_log_view_vl = attendance_df[attendance_df["Username"] == selected_employee_log_admin_vl]
                display_attendance_logs_view_vl(emp_attendance_log_view_vl, selected_employee_log_admin_vl)
                st.markdown("---"); st.markdown(f"<h5>Allowances for {selected_employee_log_admin_vl}</h5>", unsafe_allow_html=True)
                emp_allowance_log_view_vl = allowance_df[allowance_df["Username"] == selected_employee_log_admin_vl]
                if not emp_allowance_log_view_vl.empty: st.dataframe(emp_allowance_log_view_vl.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
                else: st.info("No allowance records found")
                st.markdown(f"<h5>Sales Goals for {selected_employee_log_admin_vl}</h5>", unsafe_allow_html=True)
                emp_goals_log_view_vl = goals_df[goals_df["Username"] == selected_employee_log_admin_vl]
                if not emp_goals_log_view_vl.empty: st.dataframe(emp_goals_log_view_vl.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
                else: st.info("No sales goals records found")
                st.markdown(f"<h5>Payment Collection Goals for {selected_employee_log_admin_vl}</h5>", unsafe_allow_html=True)
                emp_payment_goals_log_view_vl = payment_goals_df[payment_goals_df["Username"] == selected_employee_log_admin_vl]
                if not emp_payment_goals_log_view_vl.empty: st.dataframe(emp_payment_goals_log_view_vl.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
                else: st.info("No payment collection goals records found")
    else: # Employee view
        st.markdown("<h4>My Records</h4>", unsafe_allow_html=True)
        my_activity_log_view_vl = activity_log_df[activity_log_df["Username"] == current_user["username"]]
        display_activity_logs_with_photos_vl(my_activity_log_view_vl, current_user["username"])
        st.markdown("<br><hr><br>", unsafe_allow_html=True)
        my_attendance_log_view_vl = attendance_df[attendance_df["Username"] == current_user["username"]]
        display_attendance_logs_view_vl(my_attendance_log_view_vl, current_user["username"])
        st.markdown("---"); st.markdown("<h5>My Allowances</h5>", unsafe_allow_html=True)
        my_allowance_log_view_vl = allowance_df[allowance_df["Username"] == current_user["username"]]
        if not my_allowance_log_view_vl.empty: st.dataframe(my_allowance_log_view_vl.sort_values(by="Date", ascending=False).reset_index(drop=True), use_container_width=True)
        else: st.info("No allowance records found for you")
        st.markdown("<h5>My Sales Goals</h5>", unsafe_allow_html=True)
        my_goals_log_view_vl = goals_df[goals_df["Username"] == current_user["username"]]
        if not my_goals_log_view_vl.empty: st.dataframe(my_goals_log_view_vl.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
        else: st.info("No sales goals records found for you")
        st.markdown("<h5>My Payment Collection Goals</h5>", unsafe_allow_html=True)
        my_payment_goals_log_view_vl = payment_goals_df[payment_goals_df["Username"] == current_user["username"]]
        if not my_payment_goals_log_view_vl.empty: st.dataframe(my_payment_goals_log_view_vl.sort_values(by="MonthYear", ascending=False).reset_index(drop=True), use_container_width=True)
        else: st.info("No payment collection goals records found for you")
    st.markdown('</div>', unsafe_allow_html=True)
    # --- End of View Logs Page Logic ---

elif selected == "Create Order":
    # --- Start of Create Order Page Logic ---
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🛒 Create New Order</h3>", unsafe_allow_html=True)
    if stores_df.empty or products_df.empty:
        st.error("Store or Product data is missing. Cannot create order.")
        st.markdown('</div>', unsafe_allow_html=True); st.stop()

    store_name_co = st.selectbox("Select Store", [""] + sorted(stores_df["StoreName"].dropna().astype(str).unique()), key="co_store_final_v5", format_func=lambda x: "Select Store..." if x == "" else x) # Key update
    product_name_co = st.selectbox("Select Product", [""] + sorted(products_df["ProductName"].dropna().astype(str).unique()), key="co_product_final_v5", format_func=lambda x: "Select Product..." if x == "" else x) # Key update
    product_sizes_df_co = pd.DataFrame()
    size_options_co = [""]
    if product_name_co != "":
        product_sizes_df_co = products_df[products_df["ProductName"] == product_name_co]
        if not product_sizes_df_co.empty:
            size_options_co = [""] + sorted(product_sizes_df_co["Size"].dropna().astype(str).unique())
        else: st.info(f"No sizes found for {product_name_co}.")
    size_co = st.selectbox("Select Size", size_options_co, key="co_size_final_v5", format_func=lambda x: "Select Size..." if x == "" else x, disabled=(product_name_co == "" or not size_options_co or len(size_options_co) <= 1)) # Key update
    quantity_co = st.number_input("Enter Quantity", min_value=1, value=1, key="co_quantity_final_v5", disabled=(product_name_co == "" or size_co == "")) # Key update

    if size_co != "" and st.button("Add to Order", key="co_add_btn_final_v5", type="primary", disabled=(product_name_co == "" or size_co == ""), use_container_width=True): # Key update
        selected_product_row_co = product_sizes_df_co[product_sizes_df_co["Size"] == size_co]
        if not selected_product_row_co.empty:
            selected_product_co = selected_product_row_co.iloc[0]
            unit_price_co = pd.to_numeric(selected_product_co.get("Price"), errors='coerce')
            product_variant_id_co = selected_product_co.get("ProductVariantID", selected_product_co.get("SKU", "UnknownID"))
            if pd.notna(unit_price_co):
                item_co = {
                    "Store": store_name_co, "Product": product_name_co, "Size": size_co,
                    "Quantity": quantity_co, "Unit Price": unit_price_co, "Total": unit_price_co * quantity_co,
                    "ProductVariantID": product_variant_id_co, "SKU": selected_product_co.get("SKU", pd.NA),
                    "UnitOfMeasure": selected_product_co_page.get("UnitOfMeasure", pd.NA), "ImageURL": selected_product_co_page.get("ImageURL", pd.NA)
                }
                item_exists_at_index = -1
                for i_co_page, existing_item_co_page in enumerate(st.session_state.co_order_line_items):
                    if existing_item_co_page["ProductVariantID"] == product_variant_id_co and existing_item_co_page["Size"] == size_co : 
                        item_exists_at_index = i_co_page; break
                if item_exists_at_index != -1:
                    st.session_state.co_order_line_items[item_exists_at_index]["Quantity"] += quantity_co
                    st.session_state.co_order_line_items[item_exists_at_index]["Total"] = st.session_state.co_order_line_items[item_exists_at_index]["Quantity"] * st.session_state.co_order_line_items[item_exists_at_index]["Unit Price"]
                    st.success(f"Updated quantity for {product_name_co} ({size_co}).")
                else:
                    st.session_state.co_order_line_items.append(item_co)
                    st.success(f"Added to order: {quantity_co} x {product_name_co} ({size_co})")
                st.rerun()
            else: st.warning(f"Price not available for {product_name_co} ({size_co}).")
        else: st.warning("Selected product size details not found.")

    if st.session_state.co_order_line_items:
        st.subheader("🧾 Order Summary")
        order_summary_df_co_display_page = pd.DataFrame(st.session_state.co_order_line_items)
        order_summary_df_co_display_page["Unit Price"] = pd.to_numeric(order_summary_df_co_display_page["Unit Price"], errors='coerce').fillna(0)
        order_summary_df_co_display_page["Total"] = pd.to_numeric(order_summary_df_co_display_page["Total"], errors='coerce').fillna(0)
        display_df_co_page_final = order_summary_df_co_display_page.copy()
        for col_currency_co_page_final in ["Unit Price", "Total"]: display_df_co_page_final[col_currency_co_page_final] = display_df_co_page_final[col_currency_co_page_final].apply(lambda x: f"₹{x:,.2f}")
        st.dataframe(display_df_co_page_final[["Store", "Product", "Size", "Quantity", "Unit Price", "Total"]], use_container_width=True, hide_index=True)
        grand_total_co_page_final = order_summary_df_co_display_page['Total'].sum()
        st.markdown(f"<h4 style='text-align: right; margin-top: 1rem;'>Grand Total: ₹{grand_total_co_page_final:,.2f}</h4>", unsafe_allow_html=True)
        if st.button("Clear Order", key="co_clear_btn_final_v4"): # Key update
            st.session_state.co_order_line_items = []
            st.info("Order cleared."); st.rerun()
        if st.button("✅ Submit Final Order", key="co_submit_final_order_btn_v3", type="primary", use_container_width=True): # Key update
            if not st.session_state.co_order_line_items: st.error("Cannot submit an empty order.")
            else:
                temp_orders_df_submit_page = orders_df.copy()
                temp_order_summary_df_submit_page = order_summary_df.copy()
                def generate_order_id_co_final_page(): return f"ORD-{get_current_time_in_tz().strftime('%y%m%d%H%M%S')}{np.random.randint(100,999)}"
                new_order_id_co_final_page = generate_order_id_co_final_page()
                order_date_co_final_page = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
                order_items_to_save_final_page = []
                current_subtotal_co_final_page = 0
                for item_final_page in st.session_state.co_order_line_items:
                    current_subtotal_co_final_page += item_final_page["Total"]
                    order_items_to_save_final_page.append({
                        "OrderID": new_order_id_co_final_page, "OrderDate": order_date_co_final_page, "Salesperson": current_user["username"],
                        "StoreID": item_final_page["Store"],
                        "ProductVariantID": item_final_page.get("ProductVariantID", item_final_page.get("SKU")),
                        "SKU": item_final_page.get("SKU", pd.NA), "ProductName": item_final_page["Product"],
                        "Quantity": item_final_page["Quantity"], "UnitOfMeasure": item_final_page.get("UnitOfMeasure", pd.NA),
                        "UnitPrice": item_final_page["Unit Price"], "LineTotal": item_final_page["Total"]
                    })
                new_items_df_co_final_page = pd.DataFrame(order_items_to_save_final_page, columns=ORDERS_COLUMNS)
                temp_orders_df_submit_page = pd.concat([temp_orders_df_submit_page, new_items_df_co_final_page], ignore_index=True)
                order_summary_entry_final_page = {
                    "OrderID": new_order_id_co_final_page, "OrderDate": order_date_co_final_page, "Salesperson": current_user["username"],
                    "StoreID": store_name_co_page, "StoreName": store_name_co_page,
                    "Subtotal": current_subtotal_co_final_page, "DiscountAmount": 0.0, "TaxAmount": 0.0, "GrandTotal": current_subtotal_co_final_page,
                    "Notes": "Order submitted via app", "PaymentMode": pd.NA, "ExpectedDeliveryDate": pd.NA
                }
                new_summary_df_co_final_page = pd.DataFrame([order_summary_entry_final_page], columns=ORDER_SUMMARY_COLUMNS)
                temp_order_summary_df_submit_page = pd.concat([temp_order_summary_df_submit_page, new_summary_df_co_final_page], ignore_index=True)
                try:
                    temp_orders_df_submit_page.to_csv(ORDERS_FILE, index=False)
                    temp_order_summary_df_submit_page.to_csv(ORDER_SUMMARY_FILE, index=False)
                    globals()['orders_df'] = temp_orders_df_submit_page
                    globals()['order_summary_df'] = temp_order_summary_df_submit_page
                    st.session_state.user_message = f"Order {new_order_id_co_final_page} submitted successfully!"
                    st.session_state.message_type = "success"
                    st.session_state.co_order_line_items = []
                    st.rerun()
                except Exception as e: st.session_state.user_message = f"Error submitting order: {e}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    # --- End of Create Order Page Logic ---

# Fallback for Home or undefined selected page
elif selected == "Home" or selected is None:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.header(f"🏠 Welcome Home, {current_user['username']}!")
    st.write("Select an option from the sidebar to manage your activities.")
    st.markdown('</div>', unsafe_allow_html=True)
