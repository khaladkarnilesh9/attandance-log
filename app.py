import streamlit as st
import pandas as pd
from datetime import datetime, timezone
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

# --- Bootstrap and Material Icons CDN & Custom CSS ---
# (Keep your existing CSS and CDN links as they are good for styling)
st.markdown("""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
""", unsafe_allow_html=True)

st.markdown("""
<style>
    /* Your existing CSS here, including .material-symbols-outlined and .logout-container .stButton > button */
    /* ... (rest of your CSS) ... */
    /* Ensure .custom-notification style is defined for the message display */
    .custom-notification {
        padding: 0.75rem 1rem;
        border-radius: var(--border-radius);
        margin-bottom: 1rem;
        border: 1px solid transparent;
    }
    .custom-notification.success {
        color: #0f5132;
        background-color: #d1e7dd;
        border-color: #badbcc;
    }
    .custom-notification.error {
        color: #842029;
        background-color: #f8d7da;
        border-color: #f5c2c7;
    }
    .custom-notification.warning {
        color: #664d03;
        background-color: #fff3cd;
        border-color: #ffecb5;
    }
    .custom-notification.info {
        color: #055160;
        background-color: #cff4fc;
        border-color: #b6effb;
    }
</style>
""", unsafe_allow_html=True)


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
    except OSError: pass # Folder already exists or other OS error
if PILLOW_INSTALLED:
    for user_key, user_data in USERS.items():
        img_path = user_data.get("profile_photo")
        if img_path and not os.path.exists(img_path):
            try:
                img = Image.new('RGB', (120, 120), color = (200, 220, 240)); draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", 40)
                except IOError: font = ImageFont.load_default()
                text = user_key[:2].upper()
                # PIL text drawing methods changed over versions
                if hasattr(draw, 'textbbox'): # More modern PIL
                    bbox = draw.textbbox((0,0), text, font=font); text_width, text_height = bbox[2]-bbox[0], bbox[3]-bbox[1]
                    text_x, text_y = (120-text_width)/2, (120-text_height)/2 - bbox[1] # Adjust y based on bbox[1] for better centering
                elif hasattr(draw, 'textsize'): # Older PIL
                    text_width, text_height = draw.textsize(text, font=font); text_x, text_y = (120-text_width)/2, (120-text_height)/2
                else: # Fallback if textsize and textbbox not available
                    text_x, text_y = 30,30 # Approximate center
                draw.text((text_x, text_y), text, fill=(28,78,128), font=font); img.save(img_path)
            except Exception: pass # Ignore if placeholder creation fails


# --- File Paths & Timezone & Directories ---
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"
GOALS_FILE = "goals.csv"
PAYMENT_GOALS_FILE = "payment_goals.csv"
ACTIVITY_LOG_FILE = "activity_log.csv"
ACTIVITY_PHOTOS_DIR = "activity_photos"
ATTENDANCE_PHOTOS_DIR = "attendance_photos" # Not used in current logic, but kept for completeness

for dir_path in [ACTIVITY_PHOTOS_DIR, ATTENDANCE_PHOTOS_DIR]:
    if not os.path.exists(dir_path):
        try: os.makedirs(dir_path)
        except OSError: pass

TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'. Please use a valid IANA timezone.")
    st.stop()

def get_current_time_in_tz():
    return datetime.now(timezone.utc).astimezone(tz)

def get_quarter_str_for_year(year):
    now_month = get_current_time_in_tz().month
    if 1 <= now_month <= 3: return f"{year}-Q1"
    elif 4 <= now_month <= 6: return f"{year}-Q2"
    elif 7 <= now_month <= 9: return f"{year}-Q3"
    else: return f"{year}-Q4"

# --- Load or create data ---
# This function now returns the dataframe and is responsible for initial load
# It will be called once to populate session state
def load_dataframe_from_csv(path, columns):
    if os.path.exists(path):
        try:
            if os.path.getsize(path) > 0:
                df = pd.read_csv(path)
                for col in columns: # Ensure all expected columns exist
                    if col not in df.columns: df[col] = pd.NA
                num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude"]
                for nc in num_cols:
                    if nc in df.columns: df[nc] = pd.to_numeric(df[nc], errors='coerce') # Coerce non-numeric to NaN
                return df
            else: return pd.DataFrame(columns=columns)
        except pd.errors.EmptyDataError: return pd.DataFrame(columns=columns)
        except Exception as e:
            st.error(f"Error loading {path}: {e}. Returning empty DataFrame.");
            return pd.DataFrame(columns=columns)
    else: # File does not exist, create it with headers
        df = pd.DataFrame(columns=columns);
        try: df.to_csv(path, index=False)
        except Exception as e: st.warning(f"Could not create {path}: {e}")
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
PAYMENT_GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]

# --- Session State Initialization ---
# Initialize session state variables for authentication and page navigation
if "user_message" not in st.session_state: st.session_state.user_message = None
if "message_type" not in st.session_state: st.session_state.message_type = None
if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}
if "active_page" not in st.session_state: st.session_state.active_page = "Attendance" # Default page

# Load dataframes into session state only once
if "attendance_df" not in st.session_state:
    st.session_state.attendance_df = load_dataframe_from_csv(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
if "allowance_df" not in st.session_state:
    st.session_state.allowance_df = load_dataframe_from_csv(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
if "goals_df" not in st.session_state:
    st.session_state.goals_df = load_dataframe_from_csv(GOALS_FILE, GOALS_COLUMNS)
if "payment_goals_df" not in st.session_state:
    st.session_state.payment_goals_df = load_dataframe_from_csv(PAYMENT_GOALS_FILE, PAYMENT_GOALS_COLUMNS)
if "activity_log_df" not in st.session_state:
    st.session_state.activity_log_df = load_dataframe_from_csv(ACTIVITY_LOG_FILE, ACTIVITY_LOG_COLUMNS)


# --- Charting Functions ---
def render_goal_chart(df: pd.DataFrame, chart_title: str):
    if df.empty:
        st.warning("No data available to plot."); return
    df_chart = df.copy()
    df_chart[["TargetAmount", "AchievedAmount"]] = df_chart[["TargetAmount", "AchievedAmount"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    df_melted = df_chart.melt(id_vars="MonthYear", value_vars=["TargetAmount", "AchievedAmount"], var_name="Metric", value_name="Amount")
    if df_melted.empty:
        st.warning(f"No data to plot for {chart_title} after processing."); return
    
    fig = px.bar(df_melted, x="MonthYear", y="Amount", color="Metric", barmode="group",
                 labels={"MonthYear": "Quarter", "Amount": "Amount (INR)", "Metric": "Metric"},
                 title=chart_title, color_discrete_map={'TargetAmount': '#3498db', 'AchievedAmount': '#2ecc71'})
    fig.update_layout(height=400, xaxis_title="Quarter", yaxis_title="Amount (INR)", legend_title_text='Metric')
    fig.update_xaxes(type='category')
    st.plotly_chart(fig, use_container_width=True)

def create_donut_chart(progress_percentage, chart_title="Progress", achieved_color='#2ecc71', remaining_color='#f0f0f0', center_text_color=None):
    fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=90); fig.patch.set_alpha(0); ax.patch.set_alpha(0)
    progress_percentage = max(0.0, min(float(progress_percentage), 100.0))
    remaining_percentage = 100.0 - progress_percentage
    if progress_percentage <= 0.01: sizes, slice_colors, actual_progress_display = [100.0], [remaining_color], 0.0
    elif progress_percentage >= 99.99: sizes, slice_colors, actual_progress_display = [100.0], [achieved_color], 100.0
    else: sizes, slice_colors, actual_progress_display = [progress_percentage, remaining_percentage], [achieved_color, remaining_color], progress_percentage
    ax.pie(sizes, colors=slice_colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.4, edgecolor='white'))
    centre_circle = plt.Circle((0,0),0.60,fc='white'); fig.gca().add_artist(centre_circle)
    text_color_to_use = center_text_color if center_text_color else (achieved_color if actual_progress_display > 0 else '#4A4A4A')
    ax.text(0, 0, f"{actual_progress_display:.0f}%", ha='center', va='center', fontsize=12, fontweight='bold', color=text_color_to_use)
    ax.axis('equal'); plt.subplots_adjust(left=0, right=1, top=1, bottom=0); return fig

def create_team_progress_bar_chart(summary_df, title="Team Progress", target_col="Target", achieved_col="Achieved", user_col="Employee"):
    if summary_df.empty: return None
    labels = summary_df[user_col].tolist(); target_amounts = summary_df[target_col].fillna(0).tolist(); achieved_amounts = summary_df[achieved_col].fillna(0).tolist()
    x = np.arange(len(labels)); width = 0.35
    fig, ax = plt.subplots(figsize=(max(6, len(labels) * 0.8), 5), dpi=100)
    rects1 = ax.bar(x - width/2, target_amounts, width, label='Target', color='#3498db', alpha=0.8)
    rects2 = ax.bar(x + width/2, achieved_amounts, width, label='Achieved', color='#2ecc71', alpha=0.8)
    ax.set_ylabel('Amount (INR)', fontsize=10); ax.set_title(title, fontsize=12, fontweight='bold', pad=15)
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9); ax.legend(fontsize=9)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            if height > 0: ax.annotate(f'{height:,.0f}', xy=(rect.get_x() + rect.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=7, color='#333')
    autolabel(rects1); autolabel(rects2); fig.tight_layout(pad=1.5); return fig

# --- Global Message Display Function ---
def display_message():
    if st.session_state.user_message:
        message_type = st.session_state.get("message_type", "info")
        st.markdown(
            f"<div class='custom-notification {message_type}'>{st.session_state.user_message}</div>",
            unsafe_allow_html=True
        )
        # Clear the message after displaying
        st.session_state.user_message = None
        st.session_state.message_type = None

# --- Page Functions ---

def attendance_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True)
    st.info("📍 Location services are currently disabled for attendance. Photos for specific activities can be uploaded from the 'Upload Activity Photo' section.", icon="ℹ️")
    
    st.markdown("---")
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    current_username = st.session_state.auth.get("username")
    
    # Ensure current_username is not None before proceeding
    if current_username is None:
        st.error("User not logged in. Please log in to record attendance.")
        st.markdown('</div></div>', unsafe_allow_html=True)
        return

    common_data = {"Username": current_username, "Latitude": pd.NA, "Longitude": pd.NA}

    def process_general_attendance(attendance_type):
        now_str_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create a dictionary for the new entry, ensuring all ATTENDANCE_COLUMNS are present
        new_entry_data = {col: pd.NA for col in ATTENDANCE_COLUMNS}
        new_entry_data.update({
            "Type": attendance_type,
            "Timestamp": now_str_display,
            "Username": current_username,
            "Latitude": common_data["Latitude"],
            "Longitude": common_data["Longitude"]
        })

        new_entry_df = pd.DataFrame([new_entry_data])
        
        # Concatenate and save directly to session state dataframe
        # Use .copy() to prevent SettingWithCopyWarning if further modifications were made
        st.session_state.attendance_df = pd.concat([st.session_state.attendance_df, new_entry_df], ignore_index=True)
        
        try:
            st.session_state.attendance_df.to_csv(ATTENDANCE_FILE, index=False)
            st.session_state.user_message = f"{attendance_type} recorded at {now_str_display}."
            st.session_state.message_type = "success"
        except Exception as e:
            st.session_state.user_message = f"Error saving attendance: {e}"
            st.session_state.message_type = "error"
        st.rerun() # Rerun to display message and update state

    with col1:
        if st.button("✅ Check In", key="check_in_btn_main_no_photo", use_container_width=True, type="primary"):
            process_general_attendance("Check-In")
    with col2:
        if st.button("🚪 Check Out", key="check_out_btn_main_no_photo", use_container_width=True, type="primary"):
            process_general_attendance("Check-Out")
    st.markdown('</div></div>', unsafe_allow_html=True)

def upload_activity_photo_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📸 Upload Field Activity Photo</h3>", unsafe_allow_html=True)
    current_lat, current_lon = pd.NA, pd.NA # Placeholder, actual location capture not implemented
    
    current_username = st.session_state.auth.get("username")
    if current_username is None:
        st.error("User not logged in. Please log in to upload activity photos.")
        st.markdown('</div>', unsafe_allow_html=True)
        return
        
    with st.form(key="activity_photo_form", clear_on_submit=True):
        st.markdown("<h6>Capture and Describe Your Activity:</h6>", unsafe_allow_html=True)
        activity_description = st.text_area("Brief description of activity/visit:", key="activity_desc_input")
        img_file_buffer_activity = st.camera_input("Take a picture of your activity/visit", key="activity_camera_input")
        submit_activity_photo = st.form_submit_button("⬆️ Upload Photo and Log Activity")
    
    if submit_activity_photo:
        if img_file_buffer_activity is None:
            st.session_state.user_message = "Please take a picture before submitting."
            st.session_state.message_type = "warning"
        elif not activity_description.strip():
            st.session_state.user_message = "Please provide a description for the activity."
            st.session_state.message_type = "warning"
        else:
            now_for_filename = get_current_time_in_tz().strftime("%Y%m%d_%H%M%S")
            now_for_display = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            image_filename_activity = f"{current_username}_activity_{now_for_filename}.jpg"
            image_path_activity = os.path.join(ACTIVITY_PHOTOS_DIR, image_filename_activity)
            try:
                with open(image_path_activity, "wb") as f:
                    f.write(img_file_buffer_activity.getbuffer())
                
                # Create a dictionary for the new entry, ensuring all ACTIVITY_LOG_COLUMNS are present
                new_activity_data = {col: pd.NA for col in ACTIVITY_LOG_COLUMNS}
                new_activity_data.update({
                    "Username": current_username,
                    "Timestamp": now_for_display,
                    "Description": activity_description,
                    "ImageFile": image_filename_activity,
                    "Latitude": current_lat,
                    "Longitude": current_lon
                })
                new_activity_entry_df = pd.DataFrame([new_activity_data])
                
                st.session_state.activity_log_df = pd.concat([st.session_state.activity_log_df, new_activity_entry_df], ignore_index=True)
                st.session_state.activity_log_df.to_csv(ACTIVITY_LOG_FILE, index=False)

                st.session_state.user_message = "Activity photo and log uploaded!"
                st.session_state.message_type = "success"
            except Exception as e:
                st.session_state.user_message = f"Error saving activity: {e}"
                st.session_state.message_type = "error"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def allowance_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    
    current_username = st.session_state.auth.get("username")
    if current_username is None:
        st.error("User not logged in. Please log in to claim allowances.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    a_type = st.radio("Allowance Type", ["Travel", "Dinner", "Medical", "Internet", "Other"],
                      key="allowance_type_radio_main", horizontal=True)
    amount = st.number_input("Enter Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_main")
    reason = st.text_area("Reason for Allowance:", key="allowance_reason_main", placeholder="Please provide a clear justification...")
    
    if st.button("Submit Allowance Request", key="submit_allowance_btn_main", use_container_width=True, type="primary"):
        if a_type and amount > 0 and reason.strip():
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            
            # Create a dictionary for the new entry, ensuring all ALLOWANCE_COLUMNS are present
            new_entry_data = {col: pd.NA for col in ALLOWANCE_COLUMNS}
            new_entry_data.update({
                "Username": current_username, "Type": a_type,
                "Amount": amount, "Reason": reason, "Date": date_str
            })
            new_entry_df = pd.DataFrame([new_entry_data])
            
            st.session_state.allowance_df = pd.concat([st.session_state.allowance_df, new_entry_df], ignore_index=True)
            try:
                st.session_state.allowance_df.to_csv(ALLOWANCE_FILE, index=False)
                st.session_state.user_message = f"Allowance for ₹{amount:.2f} submitted."
                st.session_state.message_type = "success"
            except Exception as e:
                st.session_state.user_message = f"Error submitting allowance: {e}"
                st.session_state.message_type = "error"
            st.rerun()
        else:
            st.session_state.user_message = "Please complete all fields with valid values."
            st.session_state.message_type = "warning"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def goal_tracker_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_GOAL_YEAR = 2025
    current_quarter_for_display = get_quarter_str_for_year(TARGET_GOAL_YEAR)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    
    current_role = st.session_state.auth.get("role")
    current_username = st.session_state.auth.get("username")

    if current_role == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio("Action:", ["View Team Progress", f"Set/Edit Goal for {TARGET_GOAL_YEAR}"],
                                 key="admin_goal_action_radio_2025_q", horizontal=True)
        
        if admin_action == "View Team Progress":
            st.markdown(f"<h5>Team Goal Progress for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            quarterly_goals_df = st.session_state.goals_df[st.session_state.goals_df["MonthYear"] == current_quarter_for_display]
            
            if not quarterly_goals_df.empty:
                # Group by Username and sum TargetAmount and AchievedAmount
                team_summary = quarterly_goals_df.groupby("Username").agg(
                    Target=('TargetAmount', 'sum'),
                    Achieved=('AchievedAmount', 'sum')
                ).reset_index()
                
                # Calculate overall progress for each user
                team_summary['Progress'] = team_summary.apply(
                    lambda row: (row['Achieved'] / row['Target'] * 100) if row['Target'] > 0 else 0, axis=1
                )
                
                st.markdown("<h6>Individual Quarterly Progress:</h6>", unsafe_allow_html=True)
                for index, row in team_summary.iterrows():
                    col1, col2 = st.columns([0.6, 0.4])
                    with col1:
                        st.markdown(f"**{row['Username']}**")
                        st.progress(min(row['Progress'] / 100, 1.0), text=f"Target: ₹{row['Target']:,.0f} | Achieved: ₹{row['Achieved']:,.0f}")
                    with col2:
                        fig = create_donut_chart(row['Progress'], chart_title="", center_text_color="#0d6efd")
                        st.pyplot(fig)
                
                st.markdown("---")
                st.markdown("<h6>Team Performance Summary (Bar Chart):</h6>", unsafe_allow_html=True)
                bar_fig = create_team_progress_bar_chart(team_summary, title=f"Team Goals for {current_quarter_for_display}")
                if bar_fig:
                    st.pyplot(bar_fig)
            else:
                st.info(f"No goals set for the team for {current_quarter_for_display} yet.")
        
        elif admin_action == f"Set/Edit Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set/Edit Goals for Employees ({TARGET_GOAL_YEAR})</h5>", unsafe_allow_html=True)
            
            # Filter users to only include employees, excluding admin
            employee_users = [user for user, data in USERS.items() if data.get('role') == 'employee']
            
            selected_employee = st.selectbox("Select Employee", employee_users, key="goal_employee_select")
            selected_quarter = st.selectbox("Select Quarter", [f"{TARGET_GOAL_YEAR}-Q1", f"{TARGET_GOAL_YEAR}-Q2", f"{TARGET_GOAL_YEAR}-Q3", f"{TARGET_GOAL_YEAR}-Q4"], key="goal_quarter_select")

            current_goal_for_employee_quarter = st.session_state.goals_df[
                (st.session_state.goals_df["Username"] == selected_employee) &
                (st.session_state.goals_df["MonthYear"] == selected_quarter)
            ]
            
            # Pre-fill form if a goal exists
            default_description = ""
            default_target = 0.0
            default_achieved = 0.0
            default_status = "Not Started"

            if not current_goal_for_employee_quarter.empty:
                first_goal = current_goal_for_employee_quarter.iloc[0]
                default_description = first_goal["GoalDescription"] if pd.notna(first_goal["GoalDescription"]) else ""
                default_target = first_goal["TargetAmount"] if pd.notna(first_goal["TargetAmount"]) else 0.0
                default_achieved = first_goal["AchievedAmount"] if pd.notna(first_goal["AchievedAmount"]) else 0.0
                default_status = first_goal["Status"] if pd.notna(first_goal["Status"]) else "Not Started"

            with st.form(key="set_goal_form", clear_on_submit=False):
                goal_description = st.text_area("Goal Description:", value=default_description, key="admin_goal_desc")
                target_amount = st.number_input("Target Amount (INR):", min_value=0.0, value=float(default_target), step=1000.0, format="%.2f", key="admin_target_amount")
                achieved_amount = st.number_input("Achieved Amount (INR):", min_value=0.0, value=float(default_achieved), step=100.0, format="%.2f", key="admin_achieved_amount")
                goal_status = st.selectbox("Status:", status_options, index=status_options.index(default_status) if default_status in status_options else 0, key="admin_goal_status")
                
                submit_goal = st.form_submit_button("Save Goal")
            
            if submit_goal:
                if not goal_description.strip() or target_amount <= 0:
                    st.session_state.user_message = "Please provide a description and a positive target amount."
                    st.session_state.message_type = "warning"
                else:
                    new_goal_data = {
                        "Username": selected_employee,
                        "MonthYear": selected_quarter,
                        "GoalDescription": goal_description,
                        "TargetAmount": target_amount,
                        "AchievedAmount": achieved_amount,
                        "Status": goal_status
                    }
                    
                    if not current_goal_for_employee_quarter.empty:
                        # Update existing entry
                        idx = current_goal_for_employee_quarter.index[0]
                        for col, val in new_goal_data.items():
                            st.session_state.goals_df.loc[idx, col] = val
                        st.session_state.user_message = f"Goal for {selected_employee} in {selected_quarter} updated."
                    else:
                        # Add new entry
                        new_goal_df = pd.DataFrame([new_goal_data], columns=GOALS_COLUMNS)
                        st.session_state.goals_df = pd.concat([st.session_state.goals_df, new_goal_df], ignore_index=True)
                        st.session_state.user_message = f"New goal set for {selected_employee} in {selected_quarter}."
                    
                    try:
                        st.session_state.goals_df.to_csv(GOALS_FILE, index=False)
                        st.session_state.message_type = "success"
                    except Exception as e:
                        st.session_state.user_message = f"Error saving goal: {e}"
                        st.session_state.message_type = "error"
                st.rerun()

    else: # Employee View
        if current_username is None:
            st.error("User not logged in. Please log in to view your goals.")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        st.markdown("<h4>My Sales Goals</h4>", unsafe_allow_html=True)
        user_goals = st.session_state.goals_df[st.session_state.goals_df["Username"] == current_username].copy()
        
        if not user_goals.empty:
            # Display current quarter's goals first
            st.markdown(f"<h5>Your Goals for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            current_quarter_goals = user_goals[user_goals["MonthYear"] == current_quarter_for_display]
            
            if not current_quarter_goals.empty:
                total_target = current_quarter_goals["TargetAmount"].sum()
                total_achieved = current_quarter_goals["AchievedAmount"].sum()
                overall_progress = (total_achieved / total_target * 100) if total_target > 0 else 0

                col_donut, col_summary = st.columns([0.3, 0.7])
                with col_donut:
                    fig = create_donut_chart(overall_progress, chart_title="", center_text_color="#0d6efd")
                    st.pyplot(fig)
                with col_summary:
                    st.markdown(f"""
                        <p style='font-size:1.1rem; font-weight:bold;'>Overall Progress:</p>
                        <p style='margin-bottom:0;'>Target: <span style='font-weight:bold;'>₹{total_target:,.0f}</span></p>
                        <p>Achieved: <span style='font-weight:bold;'>₹{total_achieved:,.0f}</span></p>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("<h6>Individual Goals for the Quarter:</h6>", unsafe_allow_html=True)
                for index, row in current_quarter_goals.iterrows():
                    progress_val = (row['AchievedAmount'] / row['TargetAmount'] * 100) if row['TargetAmount'] > 0 else 0
                    st.markdown(f"**Goal:** {row['GoalDescription']}")
                    st.progress(min(progress_val / 100, 1.0), text=f"Target: ₹{row['TargetAmount']:,.0f} | Achieved: ₹{row['AchievedAmount']:,.0f} | Status: {row['Status']}")
                    st.write("") # Add a little space
            else:
                st.info(f"No goals set for you for {current_quarter_for_display} yet.")
            
            # Display history
            st.markdown("---")
            st.markdown("<h5>Your Historical Goals</h5>", unsafe_allow_html=True)
            historical_goals = user_goals[user_goals["MonthYear"] != current_quarter_for_display].sort_values(by="MonthYear", ascending=False)
            if not historical_goals.empty:
                render_goal_chart(historical_goals, "Your Sales Goal History")
                st.dataframe(historical_goals.style.format({
                    "TargetAmount": "₹{:,.0f}",
                    "AchievedAmount": "₹{:,.0f}"
                }), use_container_width=True, hide_index=True)
            else:
                st.info("No historical goals to display yet.")
        else:
            st.info("No sales goals have been set for you yet. Please contact your administrator.")
    st.markdown('</div>', unsafe_allow_html=True)

# Placeholder for payment goals page - similar structure to sales goals
def payment_goals_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💰 Payment Goal Tracker (2025 - Quarterly)</h3>", unsafe_allow_html=True)
    TARGET_GOAL_YEAR = 2025
    current_quarter_for_display = get_quarter_str_for_year(TARGET_GOAL_YEAR)
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]
    
    current_role = st.session_state.auth.get("role")
    current_username = st.session_state.auth.get("username")

    if current_role == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Payment Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio("Action:", ["View Team Progress", f"Set/Edit Payment Goal for {TARGET_GOAL_YEAR}"],
                                 key="admin_payment_goal_action_radio_2025_q", horizontal=True)
        
        if admin_action == "View Team Progress":
            st.markdown(f"<h5>Team Payment Goal Progress for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            quarterly_payment_goals_df = st.session_state.payment_goals_df[st.session_state.payment_goals_df["MonthYear"] == current_quarter_for_display]
            
            if not quarterly_payment_goals_df.empty:
                team_summary = quarterly_payment_goals_df.groupby("Username").agg(
                    Target=('TargetAmount', 'sum'),
                    Achieved=('AchievedAmount', 'sum')
                ).reset_index()
                
                team_summary['Progress'] = team_summary.apply(
                    lambda row: (row['Achieved'] / row['Target'] * 100) if row['Target'] > 0 else 0, axis=1
                )
                
                st.markdown("<h6>Individual Quarterly Progress:</h6>", unsafe_allow_html=True)
                for index, row in team_summary.iterrows():
                    col1, col2 = st.columns([0.6, 0.4])
                    with col1:
                        st.markdown(f"**{row['Username']}**")
                        st.progress(min(row['Progress'] / 100, 1.0), text=f"Target: ₹{row['Target']:,.0f} | Achieved: ₹{row['Achieved']:,.0f}")
                    with col2:
                        fig = create_donut_chart(row['Progress'], chart_title="", center_text_color="#0d6efd")
                        st.pyplot(fig)
                
                st.markdown("---")
                st.markdown("<h6>Team Performance Summary (Bar Chart):</h6>", unsafe_allow_html=True)
                bar_fig = create_team_progress_bar_chart(team_summary, title=f"Team Payment Goals for {current_quarter_for_display}")
                if bar_fig:
                    st.pyplot(bar_fig)
            else:
                st.info(f"No payment goals set for the team for {current_quarter_for_display} yet.")
        
        elif admin_action == f"Set/Edit Payment Goal for {TARGET_GOAL_YEAR}":
            st.markdown(f"<h5>Set/Edit Payment Goals for Employees ({TARGET_GOAL_YEAR})</h5>", unsafe_allow_html=True)
            
            # Filter users to only include employees, excluding admin
            employee_users = [user for user, data in USERS.items() if data.get('role') == 'employee']

            selected_employee = st.selectbox("Select Employee", employee_users, key="payment_goal_employee_select")
            selected_quarter = st.selectbox("Select Quarter", [f"{TARGET_GOAL_YEAR}-Q1", f"{TARGET_GOAL_YEAR}-Q2", f"{TARGET_GOAL_YEAR}-Q3", f"{TARGET_GOAL_YEAR}-Q4"], key="payment_goal_quarter_select")

            current_goal_for_employee_quarter = st.session_state.payment_goals_df[
                (st.session_state.payment_goals_df["Username"] == selected_employee) &
                (st.session_state.payment_goals_df["MonthYear"] == selected_quarter)
            ]
            
            default_description = ""
            default_target = 0.0
            default_achieved = 0.0
            default_status = "Not Started"

            if not current_goal_for_employee_quarter.empty:
                first_goal = current_goal_for_employee_quarter.iloc[0]
                default_description = first_goal["GoalDescription"] if pd.notna(first_goal["GoalDescription"]) else ""
                default_target = first_goal["TargetAmount"] if pd.notna(first_goal["TargetAmount"]) else 0.0
                default_achieved = first_goal["AchievedAmount"] if pd.notna(first_goal["AchievedAmount"]) else 0.0
                default_status = first_goal["Status"] if pd.notna(first_goal["Status"]) else "Not Started"

            with st.form(key="set_payment_goal_form", clear_on_submit=False):
                goal_description = st.text_area("Payment Goal Description:", value=default_description, key="admin_payment_goal_desc")
                target_amount = st.number_input("Target Amount (INR):", min_value=0.0, value=float(default_target), step=1000.0, format="%.2f", key="admin_payment_target_amount")
                achieved_amount = st.number_input("Achieved Amount (INR):", min_value=0.0, value=float(default_achieved), step=100.0, format="%.2f", key="admin_payment_achieved_amount")
                goal_status = st.selectbox("Status:", status_options, index=status_options.index(default_status) if default_status in status_options else 0, key="admin_payment_goal_status")
                
                submit_goal = st.form_submit_button("Save Payment Goal")
            
            if submit_goal:
                if not goal_description.strip() or target_amount <= 0:
                    st.session_state.user_message = "Please provide a description and a positive target amount."
                    st.session_state.message_type = "warning"
                else:
                    new_goal_data = {
                        "Username": selected_employee,
                        "MonthYear": selected_quarter,
                        "GoalDescription": goal_description,
                        "TargetAmount": target_amount,
                        "AchievedAmount": achieved_amount,
                        "Status": goal_status
                    }
                    
                    if not current_goal_for_employee_quarter.empty:
                        idx = current_goal_for_employee_quarter.index[0]
                        for col, val in new_goal_data.items():
                            st.session_state.payment_goals_df.loc[idx, col] = val
                        st.session_state.user_message = f"Payment goal for {selected_employee} in {selected_quarter} updated."
                    else:
                        new_goal_df = pd.DataFrame([new_goal_data], columns=PAYMENT_GOALS_COLUMNS)
                        st.session_state.payment_goals_df = pd.concat([st.session_state.payment_goals_df, new_goal_df], ignore_index=True)
                        st.session_state.user_message = f"New payment goal set for {selected_employee} in {selected_quarter}."
                    
                    try:
                        st.session_state.payment_goals_df.to_csv(PAYMENT_GOALS_FILE, index=False)
                        st.session_state.message_type = "success"
                    except Exception as e:
                        st.session_state.user_message = f"Error saving payment goal: {e}"
                        st.session_state.message_type = "error"
                st.rerun()

    else: # Employee View
        if current_username is None:
            st.error("User not logged in. Please log in to view your payment goals.")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        st.markdown("<h4>My Payment Goals</h4>", unsafe_allow_html=True)
        user_payment_goals = st.session_state.payment_goals_df[st.session_state.payment_goals_df["Username"] == current_username].copy()
        
        if not user_payment_goals.empty:
            st.markdown(f"<h5>Your Payment Goals for {current_quarter_for_display}</h5>", unsafe_allow_html=True)
            current_quarter_payment_goals = user_payment_goals[user_payment_goals["MonthYear"] == current_quarter_for_display]
            
            if not current_quarter_payment_goals.empty:
                total_target = current_quarter_payment_goals["TargetAmount"].sum()
                total_achieved = current_quarter_payment_goals["AchievedAmount"].sum()
                overall_progress = (total_achieved / total_target * 100) if total_target > 0 else 0

                col_donut, col_summary = st.columns([0.3, 0.7])
                with col_donut:
                    fig = create_donut_chart(overall_progress, chart_title="", center_text_color="#0d6efd")
                    st.pyplot(fig)
                with col_summary:
                    st.markdown(f"""
                        <p style='font-size:1.1rem; font-weight:bold;'>Overall Progress:</p>
                        <p style='margin-bottom:0;'>Target: <span style='font-weight:bold;'>₹{total_target:,.0f}</span></p>
                        <p>Achieved: <span style='font-weight:bold;'>₹{total_achieved:,.0f}</span></p>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
                st.markdown("<h6>Individual Payment Goals for the Quarter:</h6>", unsafe_allow_html=True)
                for index, row in current_quarter_payment_goals.iterrows():
                    progress_val = (row['AchievedAmount'] / row['TargetAmount'] * 100) if row['TargetAmount'] > 0 else 0
                    st.markdown(f"**Goal:** {row['GoalDescription']}")
                    st.progress(min(progress_val / 100, 1.0), text=f"Target: ₹{row['TargetAmount']:,.0f} | Achieved: ₹{row['AchievedAmount']:,.0f} | Status: {row['Status']}")
                    st.write("")
            else:
                st.info(f"No payment goals set for you for {current_quarter_for_display} yet.")
            
            st.markdown("---")
            st.markdown("<h5>Your Historical Payment Goals</h5>", unsafe_allow_html=True)
            historical_payment_goals = user_payment_goals[user_payment_goals["MonthYear"] != current_quarter_for_display].sort_values(by="MonthYear", ascending=False)
            if not historical_payment_goals.empty:
                render_goal_chart(historical_payment_goals, "Your Payment Goal History")
                st.dataframe(historical_payment_goals.style.format({
                    "TargetAmount": "₹{:,.0f}",
                    "AchievedAmount": "₹{:,.0f}"
                }), use_container_width=True, hide_index=True)
            else:
                st.info("No historical payment goals to display yet.")
        else:
            st.info("No payment goals have been set for you yet. Please contact your administrator.")
    st.markdown('</div>', unsafe_allow_html=True)


def activity_log_page():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>📋 Activity Log</h3>", unsafe_allow_html=True)

    current_role = st.session_state.auth.get("role")
    current_username = st.session_state.auth.get("username")

    if current_role == "admin":
        st.markdown("<h4>Admin: View All Employee Activities</h4>", unsafe_allow_html=True)
        # Admin can filter activities by employee
        all_employees = ["All"] + [user for user, data in USERS.items() if data.get('role') == 'employee']
        selected_employee_filter = st.selectbox("Filter by Employee:", all_employees, key="admin_activity_employee_filter")

        display_df = st.session_state.activity_log_df.copy()
        if selected_employee_filter != "All":
            display_df = display_df[display_df["Username"] == selected_employee_filter]

        if not display_df.empty:
            st.dataframe(display_df.drop(columns=["Latitude", "Longitude"], errors='ignore').style.format({
                "Timestamp": lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else ""
            }), use_container_width=True, hide_index=True)
            
            # Optional: Allow viewing images directly in the app for admins
            st.markdown("<h6>Recent Activity Photos:</h6>", unsafe_allow_html=True)
            photos_to_show = display_df.tail(5).sort_values(by="Timestamp", ascending=False)
            if not photos_to_show.empty:
                for idx, row in photos_to_show.iterrows():
                    image_path = os.path.join(ACTIVITY_PHOTOS_DIR, row["ImageFile"])
                    if os.path.exists(image_path):
                        st.image(image_path, caption=f"{row['Username']} - {row['Timestamp']} - {row['Description']}", width=200)
                    else:
                        st.warning(f"Image not found: {row['ImageFile']}")
            else:
                st.info("No recent activity photos to display for this selection.")
        else:
            st.info("No activity logs available for this selection.")

    else: # Employee View
        if current_username is None:
            st.error("User not logged in. Please log in to view your activity log.")
            st.markdown('</div>', unsafe_allow_html=True)
            return

        st.markdown("<h4>My Activities</h4>", unsafe_allow_html=True)
        user_activity_df = st.session_state.activity_log_df[st.session_state.activity_log_df["Username"] == current_username].copy()
        
        if not user_activity_df.empty:
            # Sort by timestamp to show most recent activities first
            user_activity_df_sorted = user_activity_df.sort_values(by="Timestamp", ascending=False)
            
            st.dataframe(user_activity_df_sorted.drop(columns=["Latitude", "Longitude"], errors='ignore').style.format({
                "Timestamp": lambda x: pd.to_datetime(x).strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else ""
            }), use_container_width=True, hide_index=True)

            st.markdown("<h6>Your Recent Activity Photos:</h6>", unsafe_allow_html=True)
            photos_to_show = user_activity_df_sorted.head(5) # Show last 5 photos
            if not photos_to_show.empty:
                for idx, row in photos_to_show.iterrows():
                    image_path = os.path.join(ACTIVITY_PHOTOS_DIR, row["ImageFile"])
                    if os.path.exists(image_path):
                        st.image(image_path, caption=f"{pd.to_datetime(row['Timestamp']).strftime('%Y-%m-%d %H:%M')} - {row['Description']}", width=200)
                    else:
                        st.warning(f"Image not found: {row['ImageFile']}")
            else:
                st.info("No activity photos uploaded yet.")
        else:
            st.info("You have not logged any activities yet.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Authentication & Main App Flow ---

def login_page():
    st.markdown('<div class="d-flex align-items-center justify-content-center" style="min-height: 100vh;">'
                '<div class="card p-4 shadow" style="max-width: 400px; width: 100%;">', unsafe_allow_html=True)
    st.markdown("<h2 class='text-center mb-4'>🔑 Login</h2>", unsafe_allow_html=True)

    username_input = st.text_input("Username:", key="login_username_input")
    password_input = st.text_input("Password:", type="password", key="login_password_input")

    if st.button("Login", key="login_button", use_container_width=True, type="primary"):
        if username_input in USERS and USERS[username_input]["password"] == password_input:
            st.session_state.auth["logged_in"] = True
            st.session_state.auth["username"] = username_input
            st.session_state.auth["role"] = USERS[username_input]["role"]
            st.session_state.user_message = f"Welcome, {username_input}!"
            st.session_state.message_type = "success"
            st.rerun()
        else:
            st.session_state.user_message = "Invalid username or password."
            st.session_state.message_type = "error"
            st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)


def logout():
    st.session_state.auth["logged_in"] = False
    st.session_state.auth["username"] = None
    st.session_state.auth["role"] = None
    st.session_state.active_page = "Attendance" # Reset to default page on logout
    st.session_state.user_message = "You have been logged out."
    st.session_state.message_type = "info"
    st.rerun()

# --- Sidebar Navigation ---
def sidebar_navigation():
    st.sidebar.markdown('<div class="sidebar-content-wrapper">', unsafe_allow_html=True)

    # User Profile Section
    username = st.session_state.auth.get("username", "Guest")
    role = st.session_state.auth.get("role", "")
    position = USERS.get(username, {}).get("position", "")
    profile_photo = USERS.get(username, {}).get("profile_photo", "images/default_user.png")

    st.sidebar.markdown(f"""
        <div class="user-profile-section">
            <img src="{profile_photo}" alt="Profile" class="user-profile-img">
            <p class="welcome-text">Welcome, {username}!</p>
            <p class="user-position">{position}</p>
        </div>
        <div class="divider"></div>
    """, unsafe_allow_html=True)

    # Navigation Links
    nav_items = {
        "Attendance": "✅ Attendance",
        "Upload Activity Photo": "📸 Activity Photo",
        "Claim Allowance": "💼 Allowance",
        "Sales Goals": "🎯 Sales Goals",
        "Payment Goals": "💰 Payment Goals",
        "Activity Log": "📋 Activity Log",
    }

    for page_name, icon_text in nav_items.items():
        # Check roles for specific pages
        if page_name in ["Sales Goals", "Payment Goals", "Activity Log"] and st.session_state.auth["role"] != "admin":
            if st.session_state.auth["role"] == "employee":
                # Employees can only see their own logs/goals, so they see "My ..."
                if page_name == "Sales Goals": icon_text = "🎯 My Sales Goals"
                if page_name == "Payment Goals": icon_text = "💰 My Payment Goals"
                if page_name == "Activity Log": icon_text = "📋 My Activity Log"
            else:
                # If not an employee or admin, hide these pages
                continue
        
        # Determine if the current page is active
        is_active = "active-nav-item" if st.session_state.active_page == page_name else ""
        
        # Use a container with a button inside for better styling control
        st.sidebar.markdown(f"""
            <div class="sidebar-nav-item {is_active}">
                <span class="material-symbols-outlined">{icon_text.split(" ")[0]}</span>
                <span style="flex: 1;">{icon_text[icon_text.find(" "):].strip()}</span>
            </div>
        """, unsafe_allow_html=True)

        # Using a separate button to handle click, making it invisible but clickable
        # This is a common Streamlit pattern when you want custom HTML styling for buttons
        # but still need Streamlit's click detection.
        if st.sidebar.button(" ", key=f"nav_button_{page_name}", use_container_width=True): # Invisible button
            st.session_state.active_page = page_name
            st.rerun()

    # Logout Button
    st.sidebar.markdown('<div class="logout-container">', unsafe_allow_html=True)
    # The original button with HTML label, carefully placed
    if st.sidebar.button(label="<span class='material-symbols-outlined'>logout</span> Logout", key="logout_button_sidebar", use_container_width=True, unsafe_allow_html=True):
        logout()
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

# --- Main App Logic ---
def main():
    display_message() # Display messages at the top of the main content area

    if not st.session_state.auth["logged_in"]:
        login_page()
    else:
        sidebar_navigation()
        st.title(f"Hello, {st.session_state.auth['username']}!")

        # Render the active page
        if st.session_state.active_page == "Attendance":
            attendance_page()
        elif st.session_state.active_page == "Upload Activity Photo":
            upload_activity_photo_page()
        elif st.session_state.active_page == "Claim Allowance":
            allowance_page()
        elif st.session_state.active_page == "Sales Goals":
            goal_tracker_page()
        elif st.session_state.active_page == "Payment Goals":
            payment_goals_page()
        elif st.session_state.active_page == "Activity Log":
            activity_log_page()
        else:
            st.error("Invalid page selected.")

if __name__ == "__main__":
    main()
