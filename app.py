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
    def autolabel(rects_bar_func):
        for rect_bar_f in rects_bar_func:
            height_bar_f = rect_bar_f.get_height()
            if height_bar_f > 0: ax.annotate(f'{height_bar_f:,.0f}', xy=(rect_bar_f.get_x() + rect_bar_f.get_width() / 2, height_bar_f), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=7, color='#202124')
    autolabel(rects1); autolabel(rects2); fig.tight_layout(pad=1.5); return fig

# --- CSS Styling ---
html_css = """
<style>
    /* ... (Your full corrected CSS from the previous response - I'll keep it short here for brevity) ... */
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
    /* ... (The rest of your full CSS continues here) ... */
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
                if hasattr(draw, 'textbbox'):
                    bbox = draw.textbbox((0,0), text, font=font); text_width = bbox[2] - bbox[0]; text_height = bbox[3] - bbox[1]
                    text_x = (120 - text_width) / 2; text_y = (120 - text_height) / 2 - bbox[1]
                elif hasattr(draw, 'textsize'):
                    text_width, text_height = draw.textsize(text, font=font)
                    text_x = (120 - text_width) / 2; text_y = (120 - text_height) / 2
                else: text_x, text_y = 30,30
                draw.text((text_x, text_y), text, fill=(28,78,128), font=font); img.save(img_path)
            except Exception as e_img: st.warning(f"Could not create placeholder image for {user_key}: {e_img}", icon="🖼️")
else:
    pass

# --- File Paths & Timezone & Directories ---
ATTENDANCE_FILE = "attendance.csv"; ALLOWANCE_FILE = "allowances.csv"; GOALS_FILE = "goals.csv"
PAYMENT_GOALS_FILE = "payment_goals.csv"; ACTIVITY_LOG_FILE = "activity_log.csv"
ACTIVITY_PHOTOS_DIR = "activity_photos"
PRODUCTS_FILE = "symplanta_products_with_images.csv"; STORES_FILE = "agri_stores.csv"
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
                num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude", "UnitPrice", "Stock", "Quantity", "LineTotal", "Subtotal", "DiscountAmount", "TaxAmount", "GrandTotal", "Price"]
                for nc in num_cols:
                    if nc in df.columns: df[nc] = pd.to_numeric(df[nc], errors='coerce')
                return df
            else: return pd.DataFrame(columns=columns)
        except pd.errors.EmptyDataError: return pd.DataFrame(columns=columns)
        except Exception as e_load: st.error(f"Error loading {path}: {e_load}.", icon="📄"); return pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns);
        try: df.to_csv(path, index=False)
        except Exception as e_create: st.warning(f"Could not create file {path}: {e_create}", icon="📝")
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]
PRODUCTS_COLUMNS_FROM_CSV = ["Product Name", "Category", "Size", "Price", "Image URL"]
PRODUCTS_COLUMNS_INTERNAL = ["ProductVariantID", "ProductName", "Category", "UnitOfMeasure", "UnitPrice", "ImageURL", "SKU", "Stock", "Description"]
STORES_COLUMNS = ["StoreID", "StoreName", "ContactPerson", "ContactPhone", "Address", "VillageTown", "District", "State", "Pincode", "GSTIN", "StoreType"]
ORDERS_COLUMNS = ["OrderID", "OrderDate", "Salesperson", "StoreID", "ProductVariantID", "SKU", "ProductName", "Quantity", "UnitOfMeasure", "UnitPrice", "LineTotal"]
ORDER_SUMMARY_COLUMNS = ["OrderID", "OrderDate", "Salesperson", "StoreID", "StoreName", "Subtotal", "DiscountAmount", "TaxAmount", "GrandTotal", "Notes", "PaymentMode", "ExpectedDeliveryDate"]

attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS, parse_dates_cols=['Timestamp'])
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS, parse_dates_cols=['Date'])
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)
payment_goals_df = load_data(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
activity_log_df = load_data(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS, parse_dates_cols=['Timestamp'])
raw_products_df = load_data(PRODUCTS_FILE, PRODUCTS_COLUMNS_FROM_CSV)
products_df = pd.DataFrame(columns=PRODUCTS_COLUMNS_INTERNAL)
if not raw_products_df.empty:
    temp_products_list = []
    if 'Price' in raw_products_df.columns and not pd.api.types.is_numeric_dtype(raw_products_df['Price']):
        raw_products_df['Price'] = pd.to_numeric(raw_products_df['Price'], errors='coerce')
    for index, row in raw_products_df.iterrows():
        product_name = str(row.get("Product Name", "")).strip()
        size = str(row.get("Size", "")).strip()
        variant_id = f"{product_name.replace(' ', '_').lower()}_{size.replace(' ', '_').replace('.', '').lower()}_{index}"
        temp_products_list.append({"ProductVariantID": variant_id, "ProductName": product_name, "Category": str(row.get("Category", "Uncategorized")).strip(), "UnitOfMeasure": size, "UnitPrice": row.get("Price", 0.0), "ImageURL": str(row.get("Image URL", "")).strip() if pd.notna(row.get("Image URL")) else None, "SKU": f"SYMP_{index+1:03d}_{size.replace(' ', '').upper()}", "Stock": 100, "Description": f"{product_name} - {size}"})
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

# --- Initialize Session State ---
session_state_defaults = {
    "user_message": None, "message_type": None,
    "auth": {"logged_in": False, "username": None, "role": None},
    "order_line_items": [],
    "co_store_select_v7": None,          # For Create Order: Store selection
    "co_product_name_select_v7": None,  # For Create Order: Product Name selection
    "co_product_size_select_v7": None,    # For Create Order: Size selection
    "co_quantity_input_v7": 1,          # For Create Order: Quantity
    "co_order_notes_v7": "",              # For Create Order: Notes
    "co_order_discount_v7": 0.0,          # For Create Order: Discount
    "co_order_tax_v7": 0.0,               # For Create Order: Tax
    "selected_nav_label": None,         # For Sidebar navigation state
    "admin_order_view_selected_order_id": None # For Admin viewing specific order details
}
for key_ss_init, value_ss_init in session_state_defaults.items():
    if key_ss_init not in st.session_state:
        st.session_state[key_ss_init] = value_ss_init

# --- Login Logic ---
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
    uname = st.text_input("Username", key="login_uname_main_key_v7_final")
    pwd = st.text_input("Password", type="password", key="login_pwd_main_key_v7_final")
    if st.button("Login", key="login_button_main_key_v7_final", type="primary"):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.session_state.user_message = f"Welcome back, {uname}!"; st.session_state.message_type = "success"
            st.session_state.selected_nav_label = None # Reset nav to default for the role
            st.rerun()
        else: st.error("Invalid username or password.")
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

current_user_auth = st.session_state.auth
message_placeholder_main = st.empty() # For messages after login
if "user_message" in st.session_state and st.session_state.user_message:
    message_type_main = st.session_state.get("message_type", "info")
    message_placeholder_main.markdown(f"<div class='custom-notification {message_type_main}'>{st.session_state.user_message}</div>", unsafe_allow_html=True)
    st.session_state.user_message = None; st.session_state.message_type = None

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user_auth['username']}!</div>", unsafe_allow_html=True)
    nav_options_base_icons = { "Dashboard": "<span class='material-symbols-outlined'>dashboard</span> Dashboard", "Attendance": "<span class='material-symbols-outlined'>event_available</span> Attendance", "Upload Activity": "<span class='material-symbols-outlined'>cloud_upload</span> Upload Activity", "Allowance": "<span class='material-symbols-outlined'>receipt_long</span> Allowance Claim",}
    nav_options_sales_person_icons = { "Create Order": "<span class='material-symbols-outlined'>add_shopping_cart</span> Create Order",}
    nav_options_goals_icons = { "Sales Goals": "<span class='material-symbols-outlined'>flag</span> Sales Goals", "Payment Collection": "<span class='material-symbols-outlined'>payments</span> Payment Collection",}
    nav_options_admin_manage_icons = { "Manage Records": "<span class='material-symbols-outlined'>admin_panel_settings</span> Manage Records",}
    nav_options_employee_logs_icons = { "My Records": "<span class='material-symbols-outlined'>article</span> My Records",}
    
    nav_options_with_icons = {} 
    if current_user_auth['role'] == 'admin':
        nav_options_with_icons.update(nav_options_base_icons); nav_options_with_icons.update(nav_options_goals_icons); nav_options_with_icons.update(nav_options_admin_manage_icons)
    elif current_user_auth['role'] == 'sales_person':
        nav_options_with_icons.update(nav_options_base_icons); nav_options_with_icons.update(nav_options_sales_person_icons); nav_options_with_icons.update(nav_options_goals_icons); nav_options_with_icons.update(nav_options_employee_logs_icons)
    elif current_user_auth['role'] == 'employee': 
        nav_options_with_icons.update(nav_options_base_icons); nav_options_with_icons.update(nav_options_employee_logs_icons)
    else: nav_options_with_icons.update(nav_options_base_icons)

    option_labels = list(nav_options_with_icons.values())
    nav = None # Initialize nav
    if not option_labels: st.warning("No navigation options for your role.")
    else:
        current_selected_label = st.session_state.get("selected_nav_label")
        if current_selected_label is None or current_selected_label not in option_labels:
            current_selected_label = option_labels[0]
            st.session_state.selected_nav_label = current_selected_label
        
        current_index = 0
        try:
            current_index = option_labels.index(current_selected_label)
        except ValueError: # If somehow selected_nav_label is invalid
            current_selected_label = option_labels[0]
            st.session_state.selected_nav_label = current_selected_label
            current_index = 0

        st.markdown("<h5 style='margin-top:0; margin-bottom:10px; font-weight:500; color: var(--text-color); padding-left:10px;'>Navigation</h5>", unsafe_allow_html=True)
        selected_nav_html_label = st.radio( "MainNavigationRadioSidebarKey_V7", options=option_labels, index=current_index, label_visibility="collapsed", key="sidebar_nav_radio_final_key_v7") 
        if selected_nav_html_label != st.session_state.selected_nav_label: # Update only if changed
            st.session_state.selected_nav_label = selected_nav_html_label
            # Potentially reset page-specific session state here if needed when nav changes
        
        for key_map, html_label_map in nav_options_with_icons.items():
            if html_label_map == st.session_state.selected_nav_label: nav = key_map; break
    
    user_sidebar_info = USERS.get(current_user_auth["username"], {});
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]): st.image(user_sidebar_info["profile_photo"], width=100)
    elif PILLOW_INSTALLED: st.caption("Profile photo missing.")
    st.markdown( f"<p style='text-align:center; font-size:0.9em; color: var(--text-muted-color);'>{user_sidebar_info.get('position', 'N/A')}</p>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔒 Logout", key="logout_button_sidebar_final_key_v7", use_container_width=True):
        if 'default_session_state' in globals():
            for key_to_reset_logout in default_session_state:
                if key_to_reset_logout == "auth": st.session_state[key_to_reset_logout] = {"logged_in": False, "username": None, "role": None}
                elif key_to_reset_logout in st.session_state: st.session_state[key_to_reset_logout] = default_session_state[key_to_reset_logout]
        else: 
            st.session_state.auth = {"logged_in": False, "username": None, "role": None}
            # Manually list other critical keys if default_session_state is not found
            for key_to_clear in ["order_line_items", "selected_nav_label", "current_product_id_symplanta", "co_product_name_select_v7", "co_product_size_select_v7", "co_quantity_input_v7"]:
                if key_to_clear in st.session_state: del st.session_state[key_to_clear]
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

# --- Main Content Area based on Navigation Selection ---
if nav == "Dashboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>dashboard</span> Dashboard</h3>", unsafe_allow_html=True)
    st.write(f"Welcome to the Dashboard, {current_user_auth['username']}!")
    st.info("Dashboard content will be role-specific and show key metrics and summaries.", icon="📊")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Create Order" and current_user_auth['role'] == 'sales_person':
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>add_shopping_cart</span> Create New Sales Order</h3>", unsafe_allow_html=True)
    
    order_date_display_co = get_current_time_in_tz().strftime("%Y-%m-%d")
    salesperson_name_display_co = current_user_auth["username"]

    st.markdown("<h4>Order Header</h4>", unsafe_allow_html=True)
    col_header1_co, col_header2_co = st.columns(2)
    with col_header1_co:
        st.text_input("Order Date", value=order_date_display_co, disabled=True, key="co_form_date_key_v7")
        st.text_input("Salesperson", value=salesperson_name_display_co, disabled=True, key="co_form_salesperson_key_v7")
    with col_header2_co:
        if stores_df.empty:
            st.warning("No stores in `agri_stores.csv`. Store selection is mandatory.", icon="🏬")
            st.session_state.co_store_select_v7 = None # Use session state key
        else:
            store_options_dict_co = {row['StoreID']: f"{row['StoreName']} ({row['StoreID']})" for index, row in stores_df.iterrows()}
            options_for_sb_co = [None] + list(store_options_dict_co.keys())
            
            # Determine current index for store selectbox
            current_store_val = st.session_state.get("co_store_select_v7", None)
            current_idx_sb_co = 0
            if current_store_val in options_for_sb_co:
                current_idx_sb_co = options_for_sb_co.index(current_store_val)
            else: # If current val not in options (e.g. initially or after filter)
                st.session_state.co_store_select_v7 = None # Reset if invalid

            st.selectbox( # This selectbox writes to st.session_state.co_store_select_v7
                "Select Store *", options=options_for_sb_co,
                format_func=lambda x: "Select a store..." if x is None else store_options_dict_co.get(x, "Unknown Store"),
                key="co_store_select_v7", # Session state key
                index=current_idx_sb_co
            )

    st.markdown("---")
    st.markdown("<h4><span class='material-symbols-outlined'>playlist_add</span> Add Products to Order</h4>", unsafe_allow_html=True)
    
    # Define callback for adding items (must be defined before the button that uses it)
    def add_item_callback_co_v7():
        selected_product_name = st.session_state.get("co_product_name_select_v7")
        selected_size = st.session_state.get("co_product_size_select_v7")
        quantity_to_add = st.session_state.get("co_quantity_input_v7", 0)

        if selected_product_name and selected_size and quantity_to_add > 0:
            selected_variant_df = products_df[
                (products_df["ProductName"] == selected_product_name) &
                (products_df["UnitOfMeasure"] == selected_size)
            ]
            if not selected_variant_df.empty:
                product_info_to_add = selected_variant_df.iloc[0]
                variant_id_to_add = product_info_to_add["ProductVariantID"]
                existing_item_index = next((i for i, item in enumerate(st.session_state.order_line_items) if item['ProductVariantID'] == variant_id_to_add), -1)
                if existing_item_index != -1:
                    st.session_state.order_line_items[existing_item_index]['Quantity'] += quantity_to_add
                    st.session_state.order_line_items[existing_item_index]['LineTotal'] = st.session_state.order_line_items[existing_item_index]['Quantity'] * st.session_state.order_line_items[existing_item_index]['UnitPrice']
                    st.toast(f"Updated quantity for {product_info_to_add['ProductName']} ({product_info_to_add['UnitOfMeasure']}).", icon="🔄")
                else:
                    st.session_state.order_line_items.append({
                        "ProductVariantID": variant_id_to_add, "SKU": product_info_to_add['SKU'],
                        "ProductName": product_info_to_add['ProductName'], "Quantity": quantity_to_add,
                        "UnitOfMeasure": product_info_to_add['UnitOfMeasure'], "UnitPrice": float(product_info_to_add['UnitPrice']),
                        "LineTotal": quantity_to_add * float(product_info_to_add['UnitPrice']), "ImageURL": product_info_to_add['ImageURL']
                    })
                    st.toast(f"Added {product_info_to_add['ProductName']} ({product_info_to_add['UnitOfMeasure']}) to order.", icon="✅")
                st.session_state.co_quantity_input_v7 = 1 # Reset quantity input field
            else: st.error(f"Details not found for {selected_product_name} - {selected_size}.", icon="❌")
        else: st.warning("Please select product name, size, and quantity > 0.", icon="⚠️")

    if products_df.empty: st.error("Product catalog is empty.", icon="🚫")
    else:
        unique_product_names_co = sorted(products_df["ProductName"].dropna().astype(str).unique())
        
        # Product Name Selectbox
        current_product_name_val = st.session_state.get("co_product_name_select_v7")
        options_prod_name = [None] + unique_product_names_co
        index_prod_name = 0 
        if current_product_name_val in options_prod_name: index_prod_name = options_prod_name.index(current_product_name_val)
        
        # This selectbox writes to st.session_state.co_product_name_select_v7 due to its key
        st.selectbox(
            "Select Product Name *", options=options_prod_name,
            format_func=lambda x: "Choose a product name..." if x is None else x,
            key="co_product_name_select_v7", index=index_prod_name,
            on_change=lambda: st.session_state.update({"co_product_size_select_v7": None}) # Reset size if name changes
        )

        # Size Selectbox (dependent on product name)
        selected_size_options_co = []
        if st.session_state.co_product_name_select_v7:
            available_sizes_df_co = products_df[products_df["ProductName"] == st.session_state.co_product_name_select_v7]
            selected_size_options_co = sorted(available_sizes_df_co["UnitOfMeasure"].dropna().astype(str).unique())
        
        current_size_val = st.session_state.get("co_product_size_select_v7")
        options_size = [None] + selected_size_options_co
        index_size = 0
        if current_size_val in options_size: index_size = options_size.index(current_size_val)
        
        st.selectbox(
            f"Select Size for {st.session_state.co_product_name_select_v7 or '...'} *",
            options=options_size,
            format_func=lambda x: "Choose a size..." if x is None else x,
            key="co_product_size_select_v7", index=index_size,
            disabled=not st.session_state.co_product_name_select_v7
        )
        
        st.number_input("Enter Quantity *", min_value=1, value=st.session_state.get("co_quantity_input_v7", 1), step=1, key="co_quantity_input_v7")
        st.button("➕ Add Product to Order", on_click=add_item_callback_co_v7, key="co_add_item_btn_v7")

    if st.session_state.order_line_items:
        st.markdown("---"); st.markdown("<h4><span class='material-symbols-outlined'>receipt_long</span> Current Order Items</h4>", unsafe_allow_html=True)
        for i_item_co_v7, item_data_co_v7 in enumerate(st.session_state.order_line_items):
            item_cols_co_v7 = st.columns([1, 3, 1, 1.5, 1.5, 0.5]) 
            with item_cols_co_v7[0]:
                img_url = item_data_co_v7.get("ImageURL")
                if img_url and isinstance(img_url, str) and img_url.startswith("http"): st.image(img_url, width=50)
                else: st.markdown("<span class='material-symbols-outlined' style='font-size:36px; color: var(--gg-grey-300);'>image_not_supported</span>", unsafe_allow_html=True)
            item_cols_co_v7[1].markdown(f"**{item_data_co_v7['ProductName']}** ({item_data_co_v7['SKU']}) <br><small>{item_data_co_v7['UnitOfMeasure']}</small>", unsafe_allow_html=True)
            item_cols_co_v7[2].markdown(f"{item_data_co_v7['Quantity']}"); item_cols_co_v7[3].markdown(f"₹{item_data_co_v7['UnitPrice']:.2f}"); item_cols_co_v7[4].markdown(f"**₹{item_data_co_v7['LineTotal']:.2f}**")
            if item_cols_co_v7[5].button("➖", key=f"co_delete_item_key_v7_{i_item_co_v7}", help="Remove item"): 
                st.session_state.order_line_items.pop(i_item_co_v7); st.rerun()
            if i_item_co_v7 < len(st.session_state.order_line_items) -1 : st.divider()
        
        subtotal_co_v7 = sum(item['LineTotal'] for item in st.session_state.order_line_items)
        col_summary1_co_v7, col_summary2_co_v7 = st.columns(2)
        with col_summary1_co_v7:
            st.session_state.co_order_discount_v7 = st.number_input("Discount (₹)", value=st.session_state.get("co_order_discount_v7",0.0), min_value=0.0, step=10.0, key="co_order_discount_v7")
            st.session_state.co_order_tax_v7 = st.number_input("Tax (₹)", value=st.session_state.get("co_order_tax_v7",0.0), min_value=0.0, step=5.0, key="co_order_tax_v7", help="Total tax amount")
        grand_total_co_v7 = subtotal_co_v7 - st.session_state.co_order_discount_v7 + st.session_state.co_order_tax_v7
        with col_summary2_co_v7: st.markdown(f"<div style='text-align:right; margin-top:20px;'><p style='margin-bottom:2px;'>Subtotal:  <strong>₹{subtotal_co_v7:,.2f}</strong></p><p style='margin-bottom:2px;color:var(--danger-color);'>Discount:  - ₹{st.session_state.co_order_discount_v7:,.2f}</p><p style='margin-bottom:2px;'>Tax:  + ₹{st.session_state.co_order_tax_v7:,.2f}</p><h4 style='margin-top:5px;border-top:1px solid var(--border-color);padding-top:5px;'>Grand Total:  ₹{grand_total_co_v7:,.2f}</h4></div>", unsafe_allow_html=True)
        st.session_state.co_order_notes_v7 = st.text_area("Order Notes / Payment Mode / Expected Delivery", value=st.session_state.get("co_order_notes_v7",""), key="co_order_notes_v7", placeholder="E.g., UPI, Deliver by Tuesday")
        
        if st.button("✅ Submit Order", key="co_submit_order_btn_key_v7", type="primary", use_container_width=True): 
            final_store_id_co_submit_v7 = st.session_state.co_store_select_v7
            if not final_store_id_co_submit_v7: st.error("Store selection is mandatory.", icon="🏬")
            elif not st.session_state.order_line_items: st.error("Cannot submit an empty order.", icon="🛒")
            else:
                global orders_df, order_summary_df 
                store_name_co_submit_v7 = "N/A"
                store_info_submit_v7 = stores_df[stores_df['StoreID'] == final_store_id_co_submit_v7]
                if not store_info_submit_v7.empty: store_name_co_submit_v7 = store_info_submit_v7['StoreName'].iloc[0]
                else: st.error("Selected store details not found.", icon="❌"); st.stop()
                
                current_subtotal_submit_v7 = sum(item['LineTotal'] for item in st.session_state.order_line_items)
                current_discount_submit_v7 = st.session_state.co_order_discount_v7
                current_tax_submit_v7 = st.session_state.co_order_tax_v7       
                current_grand_total_submit_v7 = current_subtotal_submit_v7 - current_discount_submit_v7 + current_tax_submit_v7
                current_notes_submit_v7 = st.session_state.co_order_notes_v7.strip()
                salesperson_name_submit_v7 = current_user_auth["username"]

                new_order_id_submit_v7 = generate_order_id(); order_date_submit_final_v7 = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
                new_items_list_submit_v7 = [{"OrderID":new_order_id_submit_v7, "OrderDate":order_date_submit_final_v7, "Salesperson":salesperson_name_submit_v7, "StoreID":final_store_id_co_submit_v7, "ProductVariantID":item_v7['ProductVariantID'], "SKU":item_v7['SKU'], "ProductName":item_v7['ProductName'], "Quantity":item_v7['Quantity'], "UnitOfMeasure":item_v7['UnitOfMeasure'], "UnitPrice":item_v7['UnitPrice'], "LineTotal":item_v7['LineTotal']} for item_v7 in st.session_state.order_line_items]
                new_orders_df_submit_v7 = pd.DataFrame(new_items_list_submit_v7, columns=ORDERS_COLUMNS); temp_orders_df_submit_v7 = pd.concat([orders_df, new_orders_df_submit_v7], ignore_index=True)
                summary_data_submit_v7 = {"OrderID":new_order_id_submit_v7, "OrderDate":order_date_submit_final_v7, "Salesperson":salesperson_name_submit_v7, "StoreID":final_store_id_co_submit_v7, "StoreName":store_name_co_submit_v7, "Subtotal":current_subtotal_submit_v7, "DiscountAmount":current_discount_submit_v7, "TaxAmount":current_tax_submit_v7, "GrandTotal":current_grand_total_submit_v7, "Notes":current_notes_submit_v7, "PaymentMode":pd.NA, "ExpectedDeliveryDate":pd.NA}
                new_summary_df_submit_v7 = pd.DataFrame([summary_data_submit_v7], columns=ORDER_SUMMARY_COLUMNS); temp_summary_df_submit_v7 = pd.concat([order_summary_df, new_summary_df_submit_v7], ignore_index=True)
                try:
                    temp_orders_df_submit_v7.to_csv(ORDERS_FILE, index=False); temp_summary_df_submit_v7.to_csv(ORDER_SUMMARY_FILE, index=False)
                    orders_df = temp_orders_df_submit_v7; order_summary_df = temp_summary_df_submit_v7
                    st.session_state.user_message = f"Order {new_order_id_submit_v7} for '{store_name_co_submit_v7}' submitted!"; st.session_state.message_type = "success"
                    # Clear form state by resetting session state variables used by this form
                    st.session_state.order_line_items = []; 
                    st.session_state.co_store_select_v7 = None; 
                    st.session_state.co_product_name_select_v7 = None; 
                    st.session_state.co_product_size_select_v7 = None;
                    st.session_state.co_quantity_input_v7 = 1;
                    st.session_state.co_order_notes_v7 = ""; 
                    st.session_state.co_order_discount_v7 = 0.0; 
                    st.session_state.co_order_tax_v7 = 0.0
                    # Keep these original ones if they are used by other pages, but they should be distinct
                    # st.session_state.current_product_id_symplanta = None; 
                    # st.session_state.current_quantity_order = 1;
                    # st.session_state.order_notes = ""; st.session_state.order_discount = 0.0; st.session_state.order_tax = 0.0
                    st.rerun()
                except Exception as e_co_submit_v7: st.session_state.user_message = f"Error submitting order: {e_co_submit_v7}"; st.session_state.message_type = "error"; st.rerun()
    else: st.markdown("<br>", unsafe_allow_html=True); st.info("Add products to the order to see summary and submit.", icon="💡")
    st.markdown("</div>", unsafe_allow_html=True)

# --- Standard Pages (Attendance, Upload Activity, Allowance) ---
elif nav == "Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>event_available</span> Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services for general attendance are currently illustrative.", icon="ℹ️")
    st.markdown("---"); st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col_att1_std_v7, col_att2_std_v7 = st.columns(2) 
    common_data_att_std_v7 = {"Username": current_user_auth["username"], "Latitude": pd.NA, "Longitude": pd.NA}
    def process_general_attendance_cb_std_v7(attendance_type_param_std_v7): 
        global attendance_df
        now_str_att_std_v7 = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        new_entry_att_std_v7 = {"Type": attendance_type_param_std_v7, "Timestamp": now_str_att_std_v7, **common_data_att_std_v7}
        for col_att_std_v7 in ATTENDANCE_COLUMNS:
            if col_att_std_v7 not in new_entry_att_std_v7: new_entry_att_std_v7[col_att_std_v7] = pd.NA
        new_df_att_std_v7 = pd.DataFrame([new_entry_att_std_v7], columns=ATTENDANCE_COLUMNS)
        temp_df_att_std_v7 = pd.concat([attendance_df, new_df_att_std_v7], ignore_index=True)
        try:
            temp_df_att_std_v7.to_csv(ATTENDANCE_FILE, index=False); attendance_df = temp_df_att_std_v7
            st.session_state.user_message = f"{attendance_type_param_std_v7} recorded."; st.session_state.message_type = "success"; st.rerun()
        except Exception as e_att_std_v7: st.session_state.user_message = f"Error: {e_att_std_v7}"; st.session_state.message_type = "error"; st.rerun()
    with col_att1_std_v7:
        if st.button("✅ Check In", key="att_checkin_btn_v7", use_container_width=True, on_click=process_general_attendance_cb_std_v7, args=("Check-In",)): pass
    with col_att2_std_v7:
        if st.button("🚪 Check Out", key="att_checkout_btn_v7", use_container_width=True, on_click=process_general_attendance_cb_std_v7, args=("Check-Out",)): pass
    st.markdown('</div></div>', unsafe_allow_html=True)


elif nav == "Upload Activity":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>cloud_upload</span> Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    lat_act_std_v7, lon_act_std_v7 = pd.NA, pd.NA 
    with st.form(key="act_photo_form_std_v7"):
        st.markdown("<h6><span class='material-symbols-outlined'>description</span> Describe Activity:</h6>", unsafe_allow_html=True)
        desc_act_std_v7 = st.text_area("Description:", key="act_desc_std_v7", help="E.g., Met Client X, Demoed Product Y.")
        st.markdown("<h6><span class='material-symbols-outlined'>photo_camera</span> Capture Photo:</h6>", unsafe_allow_html=True)
        img_buf_act_std_v7 = st.camera_input("Take picture:", key="act_cam_std_v7", help="Photo provides context.")
        submit_act_std_v7 = st.form_submit_button("⬆️ Upload & Log", type="primary")
    if submit_act_std_v7:
        if img_buf_act_std_v7 is None: st.warning("Please take a picture.", icon="📸")
        elif not desc_act_std_v7.strip(): st.warning("Please provide a description.", icon="✏️")
        else:
            global activity_log_df
            now_fname_act_std_v7 = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S"); now_disp_act_std_v7 = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            img_fname_act_std_v7 = f"{current_user_auth['username']}_activity_{now_fname_act_std_v7}.jpg"; img_path_act_std_v7 = os.path.join(ACTIVITY_PHOTOS_DIR, img_fname_act_std_v7)
            try:
                with open(img_path_act_std_v7, "wb") as f_act_std_v7: f_act_std_v7.write(img_buf_act_std_v7.getbuffer())
                new_data_act_std_v7 = {"Username":current_user_auth["username"], "Timestamp":now_disp_act_std_v7, "Description":desc_act_std_v7, "ImageFile":img_fname_act_std_v7, "Latitude":lat_act_std_v7, "Longitude":lon_act_std_v7}
                for col_act_std_v7 in ACTIVITY_LOG_COLUMNS:
                    if col_act_std_v7 not in new_data_act_std_v7: new_data_act_std_v7[col_act_std_v7] = pd.NA
                new_entry_act_std_v7 = pd.DataFrame([new_data_act_std_v7], columns=ACTIVITY_LOG_COLUMNS)
                temp_df_act_std_v7 = pd.concat([activity_log_df, new_entry_act_std_v7], ignore_index=True)
                temp_df_act_std_v7.to_csv(ACTIVITY_LOG_FILE, index=False); activity_log_df = temp_df_act_std_v7
                st.session_state.user_message = "Activity logged successfully!"; st.session_state.message_type = "success"; st.rerun()
            except Exception as e_act_std_save_v7: st.session_state.user_message = f"Error: {e_act_std_save_v7}"; st.session_state.message_type = "error"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>receipt_long</span> Claim Allowance</h3>", unsafe_allow_html=True)
    st.markdown("<div class='form-field-label'><h6>Select Allowance Type:</h6></div>", unsafe_allow_html=True)
    type_allow_std_v7 = st.radio("AllowTypeRadioStdV7", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allow_type_std_v7", horizontal=True, label_visibility='collapsed')
    amt_allow_std_v7 = st.number_input("Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allow_amt_std_v7")
    reason_allow_std_v7 = st.text_area("Reason:", key="allow_reason_std_v7", placeholder="Justification for claim...")
    if st.button("Submit Claim", key="allow_submit_std_v7", type="primary", use_container_width=True):
        if type_allow_std_v7 and amt_allow_std_v7 > 0 and reason_allow_std_v7.strip():
            global allowance_df
            date_allow_std_v7 = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_data_allow_std_v7 = {"Username":current_user_auth["username"], "Type":type_allow_std_v7, "Amount":amt_allow_std_v7, "Reason":reason_allow_std_v7, "Date":date_allow_std_v7}
            for col_allow_std_v7 in ALLOWANCE_COLUMNS:
                if col_allow_std_v7 not in new_data_allow_std_v7: new_data_allow_std_v7[col_allow_std_v7] = pd.NA
            new_entry_allow_std_v7 = pd.DataFrame([new_data_allow_std_v7], columns=ALLOWANCE_COLUMNS)
            temp_df_allow_std_v7 = pd.concat([allowance_df, new_entry_allow_std_v7], ignore_index=True)
            try:
                temp_df_allow_std_v7.to_csv(ALLOWANCE_FILE, index=False); allowance_df = temp_df_allow_std_v7
                st.session_state.user_message = f"Allowance claim submitted."; st.session_state.message_type = "success"; st.rerun()
            except Exception as e_allow_std_save_v7: st.session_state.user_message = f"Error: {e_allow_std_save_v7}"; st.session_state.message_type = "error"; st.rerun()
        else: st.warning("Please complete all fields for allowance claim.", icon="⚠️")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "Sales Goals":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>flag</span> Sales Goal Tracker (2025)</h3>", unsafe_allow_html=True)
    TARGET_SG_YEAR_V7 = 2025; current_q_sg_v7 = get_quarter_str_for_year(TARGET_SG_YEAR_V7); status_opts_sg_v7 = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    if current_user_auth["role"] == "admin":
        st.markdown("<h4>Admin: Manage Employee Sales Goals</h4>", unsafe_allow_html=True)
        admin_action_sg_v7 = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal"], key="admin_sg_action_v7", horizontal=True)
        if admin_action_sg_v7 == "View Team Progress":
            st.markdown(f"<h5>Team Progress for {current_q_sg_v7}</h5>", unsafe_allow_html=True)
            emp_list_sg_admin_v7 = [u for u,d in USERS.items() if d["role"] in ["employee","sales_person"]]
            if not emp_list_sg_admin_v7: st.info("No employees/salespersons.")
            else:
                summary_data_sg_admin_v7 = []
                for name_sg_v7 in emp_list_sg_admin_v7:
                    goal_data_sg_v7 = goals_df[(goals_df["Username"]==name_sg_v7)&(goals_df["MonthYear"]==current_q_sg_v7)]
                    data_to_append_sg_v7 = {"Employee":name_sg_v7, "TargetAmount":0.0, "AchievedAmount":0.0, "Status":"Not Set"}
                    if not goal_data_sg_v7.empty:
                        data_row_sg_v7 = goal_data_sg_v7.iloc[0]
                        data_to_append_sg_v7["TargetAmount"]=float(pd.to_numeric(data_row_sg_v7.get("TargetAmount"),errors='coerce').fillna(0.0))
                        data_to_append_sg_v7["AchievedAmount"]=float(pd.to_numeric(data_row_sg_v7.get("AchievedAmount"),errors='coerce').fillna(0.0))
                        data_to_append_sg_v7["Status"]=data_row_sg_v7.get("Status","Not Set")
                    summary_data_sg_admin_v7.append(data_to_append_sg_v7)
                summary_df_sg_admin_v7 = pd.DataFrame(summary_data_sg_admin_v7)
                if not summary_df_sg_admin_v7.empty:
                    st.markdown("<h6>Individual Progress:</h6>", unsafe_allow_html=True)
                    cols_sg_admin_v7 = st.columns(min(3, len(summary_df_sg_admin_v7)) if len(summary_df_sg_admin_v7)>0 else 1)
                    for i_sg_admin_v7, row_sg_admin_v7 in summary_df_sg_admin_v7.iterrows():
                        target_sg_admin_val_v7 = float(pd.to_numeric(row_sg_admin_v7.get('TargetAmount'), errors='coerce').fillna(0.0))
                        achieved_sg_admin_val_v7 = float(pd.to_numeric(row_sg_admin_v7.get('AchievedAmount'), errors='coerce').fillna(0.0))
                        prog_sg_admin_v7 = (achieved_sg_admin_val_v7/target_sg_admin_val_v7*100) if target_sg_admin_val_v7>0 else 0
                        donut_sg_admin_v7 = create_donut_chart(prog_sg_admin_v7);
                        with cols_sg_admin_v7[i_sg_admin_v7 % len(cols_sg_admin_v7)]:
                            st.markdown(f"<div class='employee-progress-item'><h6>{row_sg_admin_v7['Employee']}</h6><p>T: ₹{target_sg_admin_val_v7:,.0f} | A: ₹{achieved_sg_admin_val_v7:,.0f}</p></div>", unsafe_allow_html=True)
                            if donut_sg_admin_v7: st.pyplot(donut_sg_admin_v7, use_container_width=True); st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
                    st.markdown("<hr>"); st.markdown("<h6>Overall Team Performance:</h6>", unsafe_allow_html=True)
                    bar_sg_admin_v7 = create_team_progress_bar_chart(summary_df_sg_admin_v7, title="Team Sales: Target vs Achieved", target_col="TargetAmount", achieved_col="AchievedAmount")
                    if bar_sg_admin_v7: st.pyplot(bar_sg_admin_v7, use_container_width=True)
                    else: st.info("No data for team bar chart.")
                else: st.info(f"No sales goals data for {current_q_sg_v7}.")
        else: # Set/Edit Goal
            st.markdown(f"<h5>Set/Update Sales Goal ({TARGET_SG_YEAR_V7} - Quarterly)</h5>", unsafe_allow_html=True)
            emp_opts_sg_set_v7 = [u for u,d in USERS.items() if d["role"] in ["employee","sales_person"]]
            if not emp_opts_sg_set_v7: st.warning("No employees available.")
            else:
                sel_emp_sg_set_v7 = st.radio("Employee:", emp_opts_sg_set_v7, key="sg_set_emp_v7", horizontal=True)
                sel_q_sg_set_v7 = st.radio("Quarter:", [f"{TARGET_SG_YEAR_V7}-Q{i}" for i in range(1,5)], key="sg_set_q_v7", horizontal=True)
                existing_goal_sg_v7 = goals_df[(goals_df["Username"]==sel_emp_sg_set_v7)&(goals_df["MonthYear"]==sel_q_sg_set_v7)]
                desc_sg_v7, tgt_sg_v7, ach_sg_v7, stat_sg_v7 = ("",0.0,0.0,"Not Started")
                if not existing_goal_sg_v7.empty:
                    data_sg_v7 = existing_goal_sg_v7.iloc[0]; desc_sg_v7=data_sg_v7.get("GoalDescription",""); tgt_sg_v7=float(pd.to_numeric(data_sg_v7.get("TargetAmount",0.0),errors='coerce').fillna(0.0)); ach_sg_v7=float(pd.to_numeric(data_sg_v7.get("AchievedAmount",0.0),errors='coerce').fillna(0.0)); stat_sg_v7=data_sg_v7.get("Status","Not Started")
                    st.info(f"Editing goal for {sel_emp_sg_set_v7} - {sel_q_sg_set_v7}")
                with st.form(f"form_sg_set_{sel_emp_sg_set_v7}_{sel_q_sg_set_v7}_v7"):
                    n_desc_v7=st.text_area("Desc:",value=desc_sg_v7, key=f"desc_sg_v7_{sel_emp_sg_set_v7}_{sel_q_sg_set_v7}"); n_tgt_v7=st.number_input("Target:",value=tgt_sg_v7,min_value=0.0,step=1000.0,format="%.2f", key=f"tgt_sg_v7_{sel_emp_sg_set_v7}_{sel_q_sg_set_v7}")
                    n_ach_v7=st.number_input("Achieved:",value=ach_sg_v7,min_value=0.0,step=100.0,format="%.2f", key=f"ach_sg_v7_{sel_emp_sg_set_v7}_{sel_q_sg_set_v7}"); n_stat_v7=st.radio("Status:",status_opts_sg_v7,index=status_opts_sg_v7.index(stat_sg_v7),horizontal=True, key=f"stat_sg_v7_{sel_emp_sg_set_v7}_{sel_q_sg_set_v7}")
                    submit_sg_set_v7=st.form_submit_button("Save Goal", type="primary")
                if submit_sg_set_v7:
                    if not n_desc_v7.strip():st.warning("Desc required."); 
                    elif n_tgt_v7<=0 and n_stat_v7 not in ["Cancelled","On Hold","Not Started"]: st.warning("Target >0 unless status is Cancelled/On Hold/Not Started.")
                    else:
                        global goals_df
                        df_edit_v7=goals_df.copy(); idx_v7=df_edit_v7[(df_edit_v7["Username"]==sel_emp_sg_set_v7)&(df_edit_v7["MonthYear"]==sel_q_sg_set_v7)].index
                        data_save_v7={"Username":sel_emp_sg_set_v7,"MonthYear":sel_q_sg_set_v7,"GoalDescription":n_desc_v7,"TargetAmount":n_tgt_v7,"AchievedAmount":n_ach_v7,"Status":n_stat_v7}
                        for col_check_v7 in GOALS_COLUMNS:
                            if col_check_v7 not in data_save_v7: data_save_v7[col_check_v7]=pd.NA
                        if not idx_v7.empty: df_edit_v7.loc[idx_v7[0]]=pd.Series(data_save_v7); verb_v7="updated"
                        else: df_new_v7=pd.DataFrame([data_save_v7],columns=GOALS_COLUMNS); df_edit_v7=pd.concat([df_edit_v7,df_new_v7],ignore_index=True); verb_v7="set"
                        try: df_edit_v7.to_csv(GOALS_FILE,index=False); goals_df=df_edit_v7; st.session_state.user_message=f"Goal {verb_v7}!"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e_sg_save_v7: st.session_state.user_message=f"Error: {e_sg_save_v7}"; st.session_state.message_type="error"; st.rerun()
    elif current_user_auth["role"] in ["sales_person", "employee"]:
        st.markdown(f"<h4>My Sales Goals ({TARGET_SG_YEAR_V7})</h4>", unsafe_allow_html=True)
        my_goals_sg_v7 = goals_df[goals_df["Username"]==current_user_auth["username"]].copy()
        for col_num_v7 in ["TargetAmount","AchievedAmount"]: my_goals_sg_v7[col_num_v7]=pd.to_numeric(my_goals_sg_v7[col_num_v7],errors="coerce").fillna(0.0)
        current_g_sg_v7 = my_goals_sg_v7[my_goals_sg_v7["MonthYear"]==current_q_sg_v7]
        st.markdown(f"<h5>Current: {current_q_sg_v7}</h5>", unsafe_allow_html=True)
        if not current_g_sg_v7.empty:
            g_data_v7 = current_g_sg_v7.iloc[0]; tgt_v7=g_data_v7["TargetAmount"]; ach_v7=g_data_v7["AchievedAmount"]
            st.markdown(f"**Desc:** {g_data_v7.get('GoalDescription','N/A')}")
            m_cols_v7,c_cols_v7=st.columns([0.6,0.4]);
            with m_cols_v7: s1_v7,s2_v7=st.columns(2);s1_v7.metric("Target",f"₹{tgt_v7:,.0f}");s2_v7.metric("Achieved",f"₹{ach_v7:,.0f}");st.metric("Status",g_data_v7.get("Status","In Progress"),label_visibility="visible")
            with c_cols_v7: prog_v7=(ach_v7/tgt_v7*100)if tgt_v7>0 else 0;st.markdown("<h6 style='text-align:center;margin:0;'>Progress</h6>",unsafe_allow_html=True);d_fig_v7=create_donut_chart(prog_v7);st.pyplot(d_fig_v7,use_container_width=True)
            st.markdown("---")
            if current_user_auth["role"] == "sales_person":
                with st.form(f"form_upd_sg_{current_user_auth['username']}_{current_q_sg_v7}_v7"):
                    n_val_v7=st.number_input("Update Achieved (INR):",value=ach_v7,min_value=0.0,step=100.0,format="%.2f")
                    submit_upd_v7=st.form_submit_button("Update Achievement", type="primary")
                if submit_upd_v7:
                    global goals_df
                    df_edit_u_v7=goals_df.copy();idx_u_v7=df_edit_u_v7[(df_edit_u_v7["Username"]==current_user_auth["username"])&(df_edit_u_v7["MonthYear"]==current_q_sg_v7)].index
                    if not idx_u_v7.empty:
                        df_edit_u_v7.loc[idx_u_v7[0],"AchievedAmount"]=n_val_v7;df_edit_u_v7.loc[idx_u_v7[0],"Status"]="Achieved" if n_val_v7>=tgt_v7 and tgt_v7>0 else "In Progress"
                        try: df_edit_u_v7.to_csv(GOALS_FILE,index=False);goals_df=df_edit_u_v7;st.session_state.user_message="Achievement updated!";st.session_state.message_type="success";st.rerun()
                        except Exception as e_u_save_v7:st.session_state.user_message=f"Error: {e_u_save_v7}";st.session_state.message_type="error";st.rerun()
                    else: st.session_state.user_message="Goal not found.";st.session_state.message_type="error";st.rerun()
        else: st.info(f"No goal for {current_q_sg_v7}. Contact admin.")
        st.markdown(f"---");st.markdown(f"<h5>Past Goals ({TARGET_SG_YEAR_V7})</h5>",unsafe_allow_html=True)
        past_g_sg_v7=my_goals_sg_v7[(my_goals_sg_v7["MonthYear"].str.startswith(str(TARGET_SG_YEAR_V7)))&(my_goals_sg_v7["MonthYear"]!=current_q_sg_v7)]
        if not past_g_sg_v7.empty:render_goal_chart(past_g_sg_v7,"My Past Sales Goals")
        else: st.info(f"No past goals for {TARGET_SG_YEAR_V7}.")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Payment Collection":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>payments</span> Payment Collection Tracker (2025)</h3>", unsafe_allow_html=True)
    TARGET_PAY_YEAR_V7 = 2025; current_q_pay_v7 = get_quarter_str_for_year(TARGET_PAY_YEAR_V7); status_opts_pay_v7 = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    if current_user_auth["role"] == "admin":
        st.markdown("<h4>Admin: Manage Employee Payment Collection Goals</h4>", unsafe_allow_html=True)
        admin_action_pay_v7 = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal"], key="admin_pay_action_v7", horizontal=True)
        if admin_action_pay_v7 == "View Team Progress":
            st.markdown(f"<h5>Team Progress for {current_q_pay_v7}</h5>", unsafe_allow_html=True)
            emp_list_pay_admin_v7 = [u for u,d in USERS.items() if d["role"] in ["employee","sales_person"]]
            if not emp_list_pay_admin_v7: st.info("No employees/salespersons.")
            else:
                summary_data_pay_admin_v7 = []
                for name_pay_v7 in emp_list_pay_admin_v7:
                    goal_data_pay_v7 = payment_goals_df[(payment_goals_df["Username"]==name_pay_v7)&(payment_goals_df["MonthYear"]==current_q_pay_v7)]
                    data_to_append_pay_v7 = {"Employee":name_pay_v7, "TargetAmount":0.0, "AchievedAmount":0.0, "Status":"Not Set"}
                    if not goal_data_pay_v7.empty:
                        data_row_pay_v7 = goal_data_pay_v7.iloc[0]
                        data_to_append_pay_v7["TargetAmount"]=float(pd.to_numeric(data_row_pay_v7.get("TargetAmount"),errors='coerce').fillna(0.0))
                        data_to_append_pay_v7["AchievedAmount"]=float(pd.to_numeric(data_row_pay_v7.get("AchievedAmount"),errors='coerce').fillna(0.0))
                        data_to_append_pay_v7["Status"]=data_row_pay_v7.get("Status","Not Set")
                    summary_data_pay_admin_v7.append(data_to_append_pay_v7)
                summary_df_pay_admin_v7 = pd.DataFrame(summary_data_pay_admin_v7)
                if not summary_df_pay_admin_v7.empty:
                    st.markdown("<h6>Individual Progress:</h6>", unsafe_allow_html=True)
                    cols_pay_admin_v7 = st.columns(min(3, len(summary_df_pay_admin_v7)) if len(summary_df_pay_admin_v7)>0 else 1)
                    for i_pay_admin_v7, row_pay_admin_v7 in summary_df_pay_admin_v7.iterrows():
                        target_pay_admin_val_v7 = float(pd.to_numeric(row_pay_admin_v7.get('TargetAmount'), errors='coerce').fillna(0.0))
                        achieved_pay_admin_val_v7 = float(pd.to_numeric(row_pay_admin_v7.get('AchievedAmount'), errors='coerce').fillna(0.0))
                        prog_pay_admin_v7 = (achieved_pay_admin_val_v7/target_pay_admin_val_v7*100) if target_pay_admin_val_v7>0 else 0
                        donut_pay_admin_v7 = create_donut_chart(prog_pay_admin_v7, achieved_color='#2070c0');
                        with cols_pay_admin_v7[i_pay_admin_v7 % len(cols_pay_admin_v7)]:
                            st.markdown(f"<div class='employee-progress-item'><h6>{row_pay_admin_v7['Employee']}</h6><p>T: ₹{target_pay_admin_val_v7:,.0f} | Coll: ₹{achieved_pay_admin_val_v7:,.0f}</p></div>", unsafe_allow_html=True)
                            if donut_pay_admin_v7: st.pyplot(donut_pay_admin_v7, use_container_width=True); st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
                    st.markdown("<hr>"); st.markdown("<h6>Overall Team Performance:</h6>", unsafe_allow_html=True)
                    bar_pay_admin_v7 = create_team_progress_bar_chart(summary_df_pay_admin_v7, title="Team Collection: Target vs Achieved", target_col="TargetAmount", achieved_col="AchievedAmount")
                    if bar_pay_admin_v7: 
                        for bar_group_pay_v7 in bar_pay_admin_v7.axes[0].containers:
                            if bar_group_pay_v7.get_label()=='Achieved': 
                                for bar_v7 in bar_group_pay_v7: bar_v7.set_color('#2070c0')
                        st.pyplot(bar_pay_admin_v7, use_container_width=True)
                    else: st.info("No data for team bar chart.")
                else: st.info(f"No payment collection goals data for {current_q_pay_v7}.")
        else: # Set/Edit Goal
            st.markdown(f"<h5>Set/Update Collection Goal ({TARGET_PAY_YEAR_V7} - Quarterly)</h5>", unsafe_allow_html=True)
            emp_opts_pay_set_v7 = [u for u,d in USERS.items() if d["role"] in ["employee","sales_person"]]
            if not emp_opts_pay_set_v7: st.warning("No employees available.")
            else:
                sel_emp_pay_set_v7 = st.radio("Employee:", emp_opts_pay_set_v7, key="pay_set_emp_v7", horizontal=True)
                sel_q_pay_set_v7 = st.radio("Quarter:", [f"{TARGET_PAY_YEAR_V7}-Q{i}" for i in range(1,5)], key="pay_set_q_v7", horizontal=True)
                existing_goal_pay_v7 = payment_goals_df[(payment_goals_df["Username"]==sel_emp_pay_set_v7)&(payment_goals_df["MonthYear"]==sel_q_pay_set_v7)]
                desc_pay_v7, tgt_pay_v7, ach_pay_v7, stat_pay_v7 = ("",0.0,0.0,"Not Started")
                if not existing_goal_pay_v7.empty:
                    data_pay_v7 = existing_goal_pay_v7.iloc[0]; desc_pay_v7=data_pay_v7.get("GoalDescription",""); tgt_pay_v7=float(pd.to_numeric(data_pay_v7.get("TargetAmount",0.0),errors='coerce').fillna(0.0)); ach_pay_v7=float(pd.to_numeric(data_pay_v7.get("AchievedAmount",0.0),errors='coerce').fillna(0.0)); stat_pay_v7=data_pay_v7.get("Status","Not Started")
                    st.info(f"Editing goal for {sel_emp_pay_set_v7} - {sel_q_pay_set_v7}")
                with st.form(f"form_pay_set_{sel_emp_pay_set_v7}_{sel_q_pay_set_v7}_v7"):
                    n_desc_pay_v7=st.text_area("Desc:",value=desc_pay_v7, key=f"desc_pay_v7_{sel_emp_pay_set_v7}_{sel_q_pay_set_v7}"); n_tgt_pay_v7=st.number_input("Target:",value=tgt_pay_v7,min_value=0.0,step=1000.0,format="%.2f", key=f"tgt_pay_v7_{sel_emp_pay_set_v7}_{sel_q_pay_set_v7}")
                    n_ach_pay_v7=st.number_input("Achieved:",value=ach_pay_v7,min_value=0.0,step=100.0,format="%.2f", key=f"ach_pay_v7_{sel_emp_pay_set_v7}_{sel_q_pay_set_v7}"); n_stat_pay_v7=st.selectbox("Status:",status_opts_pay_v7,index=status_opts_pay_v7.index(stat_pay_v7), key=f"stat_pay_v7_{sel_emp_pay_set_v7}_{sel_q_pay_set_v7}")
                    submit_pay_set_v7=st.form_submit_button("Save Goal", type="primary")
                if submit_pay_set_v7:
                    if not n_desc_pay_v7.strip():st.warning("Desc required."); 
                    elif n_tgt_pay_v7<=0 and n_stat_pay_v7 not in ["Cancelled","On Hold","Not Started"]: st.warning("Target >0 unless status is Cancelled/On Hold/Not Started.")
                    else:
                        global payment_goals_df
                        df_edit_pay_v7=payment_goals_df.copy(); idx_pay_v7=df_edit_pay_v7[(df_edit_pay_v7["Username"]==sel_emp_pay_set_v7)&(df_edit_pay_v7["MonthYear"]==sel_q_pay_set_v7)].index
                        data_save_pay_v7={"Username":sel_emp_pay_set_v7,"MonthYear":sel_q_pay_set_v7,"GoalDescription":n_desc_pay_v7,"TargetAmount":n_tgt_pay_v7,"AchievedAmount":n_ach_pay_v7,"Status":n_stat_pay_v7}
                        for col_check_pay_v7 in PAYMENT_GOALS_COLUMNS:
                            if col_check_pay_v7 not in data_save_pay_v7: data_save_pay_v7[col_check_pay_v7]=pd.NA
                        if not idx_pay_v7.empty: df_edit_pay_v7.loc[idx_pay_v7[0]]=pd.Series(data_save_pay_v7); verb_pay_v7="updated"
                        else: df_new_pay_v7=pd.DataFrame([data_save_pay_v7],columns=PAYMENT_GOALS_COLUMNS); df_edit_pay_v7=pd.concat([df_edit_pay_v7,df_new_pay_v7],ignore_index=True); verb_pay_v7="set"
                        try: df_edit_pay_v7.to_csv(PAYMENT_GOALS_FILE,index=False); payment_goals_df=df_edit_pay_v7; st.session_state.user_message=f"Payment Goal {verb_pay_v7}!"; st.session_state.message_type="success"; st.rerun()
                        except Exception as e_pay_save_v7: st.session_state.user_message=f"Error: {e_pay_save_v7}"; st.session_state.message_type="error"; st.rerun()
    elif current_user_auth["role"] in ["sales_person", "employee"]:
        st.markdown(f"<h4>My Payment Collection Goals ({TARGET_PAY_YEAR_V7})</h4>", unsafe_allow_html=True)
        my_goals_pay_v7 = payment_goals_df[payment_goals_df["Username"]==current_user_auth["username"]].copy()
        for col_num_pay_v7 in ["TargetAmount","AchievedAmount"]: my_goals_pay_v7[col_num_pay_v7]=pd.to_numeric(my_goals_pay_v7[col_num_pay_v7],errors="coerce").fillna(0.0)
        current_g_pay_v7 = my_goals_pay_v7[my_goals_pay_v7["MonthYear"]==current_q_pay_v7]
        st.markdown(f"<h5>Current: {current_q_pay_v7}</h5>", unsafe_allow_html=True)
        if not current_g_pay_v7.empty:
            g_data_pay_v7 = current_g_pay_v7.iloc[0]; tgt_pay_v7=g_data_pay_v7["TargetAmount"]; ach_pay_v7=g_data_pay_v7["AchievedAmount"]
            st.markdown(f"**Desc:** {g_data_pay_v7.get('GoalDescription','N/A')}")
            m_cols_pay_v7,c_cols_pay_v7=st.columns([0.6,0.4]);
            with m_cols_pay_v7: s1_pay_v7,s2_pay_v7=st.columns(2);s1_pay_v7.metric("Target",f"₹{tgt_pay_v7:,.0f}");s2_pay_v7.metric("Collected",f"₹{ach_pay_v7:,.0f}");st.metric("Status",g_data_pay_v7.get("Status","In Progress"),label_visibility="visible")
            with c_cols_pay_v7: prog_pay_v7=(ach_pay_v7/tgt_pay_v7*100)if tgt_pay_v7>0 else 0;st.markdown("<h6 style='text-align:center;margin:0;'>Progress</h6>",unsafe_allow_html=True);d_fig_pay_v7=create_donut_chart(prog_pay_v7, achieved_color='#2070c0');st.pyplot(d_fig_pay_v7,use_container_width=True)
            st.markdown("---")
            if current_user_auth["role"] == "sales_person":
                with st.form(f"form_upd_pay_{current_user_auth['username']}_{current_q_pay_v7}_v7"):
                    n_val_pay_v7=st.number_input("Update Collected (INR):",value=ach_pay_v7,min_value=0.0,step=100.0,format="%.2f")
                    submit_upd_pay_v7=st.form_submit_button("Update Collection", type="primary")
                if submit_upd_pay_v7:
                    global payment_goals_df
                    df_edit_u_pay_v7=payment_goals_df.copy();idx_u_pay_v7=df_edit_u_pay_v7[(df_edit_u_pay_v7["Username"]==current_user_auth["username"])&(df_edit_u_pay_v7["MonthYear"]==current_q_pay_v7)].index
                    if not idx_u_pay_v7.empty:
                        df_edit_u_pay_v7.loc[idx_u_pay_v7[0],"AchievedAmount"]=n_val_pay_v7;df_edit_u_pay_v7.loc[idx_u_pay_v7[0],"Status"]="Achieved" if n_val_pay_v7>=tgt_pay_v7 and tgt_pay_v7>0 else "In Progress"
                        try: df_edit_u_pay_v7.to_csv(PAYMENT_GOALS_FILE,index=False);payment_goals_df=df_edit_u_pay_v7;st.session_state.user_message="Collection updated!";st.session_state.message_type="success";st.rerun()
                        except Exception as e_u_save_pay_v7:st.session_state.user_message=f"Error: {e_u_save_pay_v7}";st.session_state.message_type="error";st.rerun()
                    else: st.session_state.user_message="Goal not found.";st.session_state.message_type="error";st.rerun()
        else: st.info(f"No collection goal for {current_q_pay_v7}. Contact admin.")
        st.markdown(f"---");st.markdown(f"<h5>Past Collection Goals ({TARGET_PAY_YEAR_V7})</h5>",unsafe_allow_html=True)
        past_g_pay_v7=my_goals_pay_v7[(my_goals_pay_v7["MonthYear"].str.startswith(str(TARGET_PAY_YEAR_V7)))&(my_goals_pay_v7["MonthYear"]!=current_q_pay_v7)]
        if not past_g_pay_v7.empty:render_goal_chart(past_g_pay_v7,"My Past Collection Performance")
        else: st.info(f"No past collection goals for {TARGET_PAY_YEAR_V7}.")
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "Manage Records" and current_user_auth['role'] == 'admin':
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3><span class='material-symbols-outlined'>admin_panel_settings</span> Manage Records</h3>", unsafe_allow_html=True)
    admin_record_view_options_v7 = ["Employee Activity & Logs", "Submitted Sales Orders"] 
    admin_selected_record_view_v7 = st.radio( "Select Record Type:", options=admin_record_view_options_v7, horizontal=True, key="admin_manage_record_type_radio_main_v7")
    st.divider()
    if admin_selected_record_view_v7 == "Employee Activity & Logs":
        st.markdown("<h4>Employee Activity & Other Logs</h4>", unsafe_allow_html=True)
        emp_list_admin_logs_v7 = [name for name, data in USERS.items() if data["role"] != "admin"]
        if not emp_list_admin_logs_v7: st.info("No employees/salespersons found.")
        else:
            sel_emp_admin_logs_v7 = st.selectbox("Select Employee:", [""] + emp_list_admin_logs_v7, key="admin_log_emp_select_v7", format_func=lambda x: "Select an Employee..." if x == "" else x)
            if sel_emp_admin_logs_v7:
                st.markdown(f"<h4 class='employee-section-header'>Records for: {sel_emp_admin_logs_v7}</h4>", unsafe_allow_html=True)
                tab_titles_admin_log_view_v7 = ["Field Activity", "Attendance", "Allowances", "Sales Goals", "Payment Goals"]
                tabs_admin_log_view_v7 = st.tabs([f"<span class='material-symbols-outlined' style='vertical-align:middle; margin-right:5px;'>folder_shared</span> {title}" for title in tab_titles_admin_log_view_v7])
                with tabs_admin_log_view_v7[0]: data_act_v7 = activity_log_df[activity_log_df["Username"] == sel_emp_admin_logs_v7]; display_activity_logs_section(data_act_v7, sel_emp_admin_logs_v7)
                with tabs_admin_log_view_v7[1]: data_att_v7 = attendance_df[attendance_df["Username"] == sel_emp_admin_logs_v7]; display_general_attendance_logs_section(data_att_v7, sel_emp_admin_logs_v7)
                with tabs_admin_log_view_v7[2]:
                    st.markdown(f"<h5>Allowances</h5>", unsafe_allow_html=True); data_allow_v7 = allowance_df[allowance_df["Username"] == sel_emp_admin_logs_v7]
                    if not data_allow_v7.empty: st.dataframe(data_allow_v7.sort_values(by="Date",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
                    else: st.info("No allowance records.")
                with tabs_admin_log_view_v7[3]:
                    st.markdown(f"<h5>Sales Goals</h5>", unsafe_allow_html=True); data_goals_v7 = goals_df[goals_df["Username"] == sel_emp_admin_logs_v7]
                    if not data_goals_v7.empty: st.dataframe(data_goals_v7.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
                    else: st.info("No sales goals.")
                with tabs_admin_log_view_v7[4]:
                    st.markdown(f"<h5>Payment Goals</h5>", unsafe_allow_html=True); data_pay_goals_v7 = payment_goals_df[payment_goals_df["Username"] == sel_emp_admin_logs_v7]
                    if not data_pay_goals_v7.empty: st.dataframe(data_pay_goals_v7.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
                    else: st.info("No payment goals.")
            else: st.info("Select an employee to view records.")
    elif admin_selected_record_view_v7 == "Submitted Sales Orders":
        st.markdown("<h4>Submitted Sales Orders</h4>", unsafe_allow_html=True)
        if order_summary_df.empty: st.info("No orders submitted yet.")
        else:
            summary_disp_admin_orders_v7 = order_summary_df.copy(); summary_disp_admin_orders_v7['OrderDate_dt'] = pd.to_datetime(summary_disp_admin_orders_v7['OrderDate'], errors='coerce'); summary_disp_admin_orders_v7 = summary_disp_admin_orders_v7.sort_values(by="OrderDate_dt", ascending=False)
            st.markdown("<h6>Filter Orders:</h6>", unsafe_allow_html=True); f_cols_admin_ord_v7 = st.columns([1,1,2])
            sales_list_admin_ord_v7 = ["All"] + sorted(summary_disp_admin_orders_v7['Salesperson'].unique().tolist()); sel_sales_admin_ord_v7 = f_cols_admin_ord_v7[0].selectbox("Salesperson", sales_list_admin_ord_v7, key="admin_ord_filt_sales_v7")
            if sel_sales_admin_ord_v7 != "All": summary_disp_admin_orders_v7 = summary_disp_admin_orders_v7[summary_disp_admin_orders_v7['Salesperson'] == sel_sales_admin_ord_v7]
            store_filt_admin_ord_v7 = f_cols_admin_ord_v7[1].text_input("Store Name contains", key="admin_ord_filt_store_v7")
            if store_filt_admin_ord_v7.strip(): summary_disp_admin_orders_v7 = summary_disp_admin_orders_v7[summary_disp_admin_orders_v7['StoreName'].str.contains(store_filt_admin_ord_v7.strip(), case=False, na=False)]
            min_d_admin_v7 = (summary_disp_admin_orders_v7['OrderDate_dt'].min().date() if not summary_disp_admin_orders_v7.empty and pd.notna(summary_disp_admin_orders_v7['OrderDate_dt'].min()) else date.today()-timedelta(days=30))
            max_d_admin_v7 = (summary_disp_admin_orders_v7['OrderDate_dt'].max().date() if not summary_disp_admin_orders_v7.empty and pd.notna(summary_disp_admin_orders_v7['OrderDate_dt'].max()) else date.today())
            date_r_admin_ord_v7 = f_cols_admin_ord_v7[2].date_input("Date Range", value=(min_d_admin_v7,max_d_admin_v7), min_value=min_d_admin_v7, max_value=max_d_admin_v7, key="admin_ord_filt_date_v7")
            if len(date_r_admin_ord_v7)==2: start_d_admin_v7,end_d_admin_v7=date_r_admin_ord_v7; summary_disp_admin_orders_v7=summary_disp_admin_orders_v7[(summary_disp_admin_orders_v7['OrderDate_dt'].dt.date>=start_d_admin_v7)&(summary_disp_admin_orders_v7['OrderDate_dt'].dt.date<=end_d_admin_v7)]
            st.markdown("---")
            if summary_disp_admin_orders_v7.empty: st.info("No orders match filters.")
            else:
                st.markdown(f"<h6>Displaying {len(summary_disp_admin_orders_v7)} Order(s)</h6>", unsafe_allow_html=True)
                cols_summary_show_admin_v7 = ["OrderID", "OrderDate", "Salesperson", "StoreName", "GrandTotal", "Notes"]
                st.dataframe(summary_disp_admin_orders_v7[cols_summary_show_admin_v7].reset_index(drop=True),use_container_width=True,hide_index=True,column_config={"OrderDate":st.column_config.DatetimeColumn("Date",format="YYYY-MM-DD HH:mm"), "GrandTotal":st.column_config.NumberColumn("Total (₹)",format="₹ %.2f")})
                st.markdown("---"); st.markdown("<h6>View Order Details:</h6>", unsafe_allow_html=True)
                opts_ord_id_admin_v7 = [""]+summary_disp_admin_orders_v7["OrderID"].tolist()
                sel_ord_id_admin_details_v7 = st.selectbox("Select OrderID:",opts_ord_id_admin_v7, index=0 if not st.session_state.admin_order_view_selected_order_id else opts_ord_id_admin_v7.index(st.session_state.admin_order_view_selected_order_id) if st.session_state.admin_order_view_selected_order_id in opts_ord_id_admin_v7 else 0, format_func=lambda x: "Select Order ID..." if x=="" else x, key="admin_ord_details_sel_v7")
                st.session_state.admin_order_view_selected_order_id = sel_ord_id_admin_details_v7
                if sel_ord_id_admin_details_v7:
                    items_sel_admin_v7 = orders_df[orders_df['OrderID']==sel_ord_id_admin_details_v7]
                    if items_sel_admin_v7.empty: st.warning(f"No items for OrderID: {sel_ord_id_admin_details_v7}")
                    else:
                        st.markdown(f"<h6>Line Items for Order: {sel_ord_id_admin_details_v7}</h6>",unsafe_allow_html=True)
                        cols_items_show_admin_v7=["ProductName","SKU","Quantity","UnitOfMeasure","UnitPrice","LineTotal"]
                        st.dataframe(items_sel_admin_v7[cols_items_show_admin_v7].reset_index(drop=True),use_container_width=True,hide_index=True,column_config={"UnitPrice":st.column_config.NumberColumn("Price (₹)",format="₹ %.2f"),"LineTotal":st.column_config.NumberColumn("Item Total (₹)",format="₹ %.2f")})
    st.markdown("</div>", unsafe_allow_html=True)

elif nav == "My Records":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f"<h3><span class='material-symbols-outlined'>article</span> My Records</h3>", unsafe_allow_html=True)
    my_username_rec_v7 = current_user_auth["username"] 
    st.markdown(f"<h4 class='employee-section-header'>Activity & Records for: {my_username_rec_v7}</h4>", unsafe_allow_html=True)
    tab_titles_user_rec_page_v7 = ["Field Activity", "Attendance", "Allowances", "Sales Goals", "Payment Goals"]
    if current_user_auth['role'] == 'sales_person': tab_titles_user_rec_page_v7.append("My Submitted Orders")
    tabs_user_rec_page_v7 = st.tabs([f"<span class='material-symbols-outlined' style='vertical-align:middle; margin-right:5px;'>badge</span> {title}" for title in tab_titles_user_rec_page_v7])
    with tabs_user_rec_page_v7[0]: data_act_user_v7 = activity_log_df[activity_log_df["Username"] == my_username_rec_v7]; display_activity_logs_section(data_act_user_v7, "My")
    with tabs_user_rec_page_v7[1]: data_att_user_v7 = attendance_df[attendance_df["Username"] == my_username_rec_v7]; display_general_attendance_logs_section(data_att_user_v7, "My")
    with tabs_user_rec_page_v7[2]:
        st.markdown(f"<h5>My Allowances</h5>", unsafe_allow_html=True); data_allow_user_v7 = allowance_df[allowance_df["Username"] == my_username_rec_v7]
        if not data_allow_user_v7.empty: st.dataframe(data_allow_user_v7.sort_values(by="Date",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
        else: st.info("No allowance records.")
    with tabs_user_rec_page_v7[3]:
        st.markdown(f"<h5>My Sales Goals</h5>", unsafe_allow_html=True); data_goals_user_v7 = goals_df[goals_df["Username"] == my_username_rec_v7]
        if not data_goals_user_v7.empty: st.dataframe(data_goals_user_v7.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
        else: st.info("No sales goals.")
    with tabs_user_rec_page_v7[4]:
        st.markdown(f"<h5>My Payment Goals</h5>", unsafe_allow_html=True); data_pay_goals_user_v7 = payment_goals_df[payment_goals_df["Username"] == my_username_rec_v7]
        if not data_pay_goals_user_v7.empty: st.dataframe(data_pay_goals_user_v7.sort_values(by="MonthYear",ascending=False).reset_index(drop=True),use_container_width=True,hide_index=True)
        else: st.info("No payment goals.")
    if current_user_auth['role'] == 'sales_person' and len(tabs_user_rec_page_v7) > 5:
        with tabs_user_rec_page_v7[5]:
            st.markdown(f"<h5>My Submitted Orders</h5>", unsafe_allow_html=True)
            my_orders_summary_v7 = order_summary_df[order_summary_df["Salesperson"] == my_username_rec_v7].copy()
            if my_orders_summary_v7.empty: st.info("You have not submitted any orders yet.")
            else:
                my_orders_summary_v7['OrderDate_dt'] = pd.to_datetime(my_orders_summary_v7['OrderDate'])
                my_orders_summary_v7 = my_orders_summary_v7.sort_values(by="OrderDate_dt", ascending=False)
                my_order_cols_to_show_v7 = ["OrderID", "OrderDate", "StoreName", "GrandTotal", "Notes"]
                st.dataframe(my_orders_summary_v7[my_order_cols_to_show_v7].reset_index(drop=True), use_container_width=True, hide_index=True,
                               column_config={"OrderDate": st.column_config.DatetimeColumn("Order Date", format="YYYY-MM-DD HH:mm"),
                                              "GrandTotal": st.column_config.NumberColumn("Total (₹)", format="₹ %.2f")})
    st.markdown("</div>", unsafe_allow_html=True)

else: 
    if nav: 
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.error(f"The page '{nav}' is not available for your role or does not exist.", icon="🚨")
        st.markdown("</div>", unsafe_allow_html=True)
