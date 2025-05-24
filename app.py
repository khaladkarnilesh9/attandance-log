import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import os
import pytz
from streamlit_geolocation import streamlit_geolocation

# --- Pillow for placeholder image generation (optional) ---
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_INSTALLED = True
except ImportError:
    PILLOW_INSTALLED = False

# --- CSS ---
html_css = """
<style>
    /* --- General --- */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f0f2f5; /* Light gray background */
        color: #333;
    }
    /* --- Titles & Headers --- */
    h1, h2 { /* Global H1, H2 */
        color: #1c4e80; /* Dark blue for headers */
    }
    .main .block-container > div:first-child > div:first-child > div:first-child > h1 { /* Main page title */
        text-align: center;
        font-size: 2.5em;
        padding-bottom: 20px;
        border-bottom: 2px solid #70a1d7;
        margin-bottom: 30px;
    }
    /* --- Card Styling --- */
    .card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
    }
    .card h3 { /* Page subheader inside card, e.g., "Digital Attendance" */
        margin-top: 0;
        color: #1c4e80;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 10px;
        margin-bottom: 20px;
        font-size: 1.5em;
    }
    .card h4 { /* Section headers inside card, e.g., "Admin: Manage Goals", "My Sales Goals" */
        color: #2070c0;
        margin-top: 25px;
        margin-bottom: 15px;
        font-size: 1.25em;
        padding-bottom: 5px;
        border-bottom: 1px dashed #d0d0d0;
    }
     .card h5 { /* Sub-section headers, e.g., "Team Goal Progress", "Attendance Records:" */
        font-size: 1.1em;
        color: #333;
        margin-top: 20px; /* Increased top margin slightly */
        margin-bottom: 10px;
        font-weight: 600;
    }
    .card h6 { /* Small text headers, e.g., for radio groups, map titles */
        font-size: 0.95em; /* Slightly larger for better readability */
        color: #495057;
        margin-top: 15px; /* Added top margin */
        margin-bottom: 8px;
        font-weight: 500;
    }
    /* --- Login Container --- */
    .login-container { max-width: 450px; margin: 50px auto; }
    .login-container .stButton button { width: 100%; background-color: #2070c0; font-size: 1.1em; }
    .login-container .stButton button:hover { background-color: #1c4e80; }

    /* --- Streamlit Button Styling --- */
    .stButton button {
        background-color: #28a745; color: white; padding: 10px 20px; border: none;
        border-radius: 5px; font-size: 1em; font-weight: bold;
        transition: background-color 0.3s ease, transform 0.1s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1); cursor: pointer;
    }
    .stButton button:hover { background-color: #218838; transform: translateY(-1px); }
    .stButton button:active { transform: translateY(0px); }
    .stButton button[id*="logout_button_sidebar"] { background-color: #dc3545 !important; }
    .stButton button[id*="logout_button_sidebar"]:hover { background-color: #c82333 !important; }

    /* --- Input Fields --- */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        border-radius: 5px !important; border: 1px solid #ced4da !important;
        padding: 10px !important; font-size: 1em;
    }
    .stTextArea textarea { min-height: 100px; }

    /* --- Sidebar --- */
    [data-testid="stSidebar"] { background-color: #1c4e80; padding: 20px !important; }
    [data-testid="stSidebar"] .sidebar-content { padding-top: 20px; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] div, [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ffffff !important; }
    [data-testid="stSidebar"] .stRadio > label { font-size: 1.1em !important; color: #a9d6e5 !important; padding-bottom: 8px; }
    [data-testid="stSidebar"] .stRadio div[aria-checked="true"] > label { color: #ffffff !important; font-weight: bold; }
    .welcome-text { font-size: 1.3em; font-weight: bold; margin-bottom: 25px; text-align: center; color: #ffffff; border-bottom: 1px solid #70a1d7; padding-bottom: 15px;}

    /* --- Dataframe Styling --- */
    .stDataFrame { width: 100%; border: 1px solid #d1d9e1; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.06); margin-bottom: 20px; }
    .stDataFrame table { width: 100%; border-collapse: collapse; }
    .stDataFrame table thead th { background-color: #f0f2f5; color: #1c4e80; font-weight: 600; text-align: left; padding: 12px 15px; border-bottom: 2px solid #c5cdd5; font-size: 0.9em; }
    .stDataFrame table tbody td { padding: 10px 15px; border-bottom: 1px solid #e7eaf0; vertical-align: middle; color: #333; font-size: 0.875em; }
    .stDataFrame table tbody tr:last-child td { border-bottom: none; }
    .stDataFrame table tbody tr:hover { background-color: #e9ecef; }

    /* --- Columns for buttons --- */
    .button-column-container > div[data-testid="stHorizontalBlock"] { gap: 15px; }
    .button-column-container .stButton button { width: 100%; }

    /* --- Page Sub Headers (already covered by .card h3) --- */
    /* .page-subheader { font-size: 1.8em; color: #1c4e80; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #e0e0e0; } */

    /* Horizontal Radio Buttons */
    div[role="radiogroup"] { display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px; }
    div[role="radiogroup"] > label { background-color: #86a7c7; padding: 8px 15px; border-radius: 20px; border: 1px solid #ced4da; cursor: pointer; transition: background-color 0.2s ease, border-color 0.2s ease; font-size: 0.95em; }
    div[role="radiogroup"] > label:hover { background-color: #dde2e6; border-color: #adb5bd; }
    div[role="radiogroup"] div[data-baseweb="radio"][aria-checked="true"] + label { background-color: #2070c0 !important; color: white !important; border-color: #1c4e80 !important; font-weight: 500; }

    /* --- Employee/Record Specific Headers (used in View Logs and Goal Tracker) --- */
    .employee-section-header { /* For Admin view: "Records for: Employee Name" */
        color: #2070c0; margin-top: 30px; border-bottom: 1px solid #e0e0e0; padding-bottom: 5px; font-size: 1.3em;
    }
    .record-type-header { /* For "Attendance Records:", "Allowance Section:" */
        font-size: 1.1em; color: #333; margin-top: 20px; margin-bottom: 10px; font-weight: 600;
    }
    .allowance-summary-header { /* For map titles, "Monthly Allowance Summary" */
        font-size: 1.0em; color: #495057; margin-top: 15px; margin-bottom: 8px; font-weight: 550;
    }
    div[data-testid="stImage"] > img { border-radius: 8px; border: 2px solid #e0e0e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stProgress > div > div { background-color: #2070c0 !important; }
    div[data-testid="stMetricLabel"] { font-size: 0.9em !important; color: #555 !important; }
</style>
"""
st.markdown(html_css, unsafe_allow_html=True)

# --- Credentials & User Info ---
USERS = {
    "Geetali": {"password": "Geetali123", "role": "employee", "position": "Software Engineer", "profile_photo": "images/geetali.png"},
    "Nilesh": {"password": "Nilesh123", "role": "employee", "position": "Sales Executive", "profile_photo": "images/nilesh.png"},
    "admin": {"password": "admin123", "role": "admin", "position": "System Administrator", "profile_photo": "images/admin.png"}
}

# --- Create dummy images folder and placeholder images for testing ---
if not os.path.exists("images"):
    try: os.makedirs("images")
    except OSError: pass

if PILLOW_INSTALLED:
    for user_key, user_data in USERS.items():
        img_path = user_data.get("profile_photo")
        if img_path and not os.path.exists(img_path):
            try:
                img = Image.new('RGB', (120, 120), color = (200, 220, 240))
                draw = ImageDraw.Draw(img)
                try: font = ImageFont.truetype("arial.ttf", 40)
                except IOError: font = ImageFont.load_default(size=40 if hasattr(ImageFont, 'load_default') and 'size' in ImageFont.load_default.__code__.co_varnames else None)


                text = user_key[:2].upper()
                if hasattr(draw, 'textbbox'): # Pillow 9.2.0+
                    bbox = draw.textbbox((0,0), text, font=font)
                    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
                    text_x, text_y = (120 - text_width) / 2, (120 - text_height) / 2 - bbox[1] # bbox[1] is y_offset
                elif hasattr(draw, 'textsize'): # Older Pillow
                    text_width, text_height = draw.textsize(text, font=font)
                    text_x, text_y = (120 - text_width) / 2, (120 - text_height) / 2
                else: # Fallback if textsize and textbbox are missing (very unlikely)
                    text_x, text_y = 30,30
                draw.text((text_x, text_y), text, fill=(28, 78, 128), font=font)
                img.save(img_path)
            except Exception: pass


# --- File Paths ---
ATTENDANCE_FILE = "attendance.csv"
ALLOWANCE_FILE = "allowances.csv"
GOALS_FILE = "goals.csv"

# --- Timezone Configuration ---
TARGET_TIMEZONE = "Asia/Kolkata"
try: tz = pytz.timezone(TARGET_TIMEZONE)
except pytz.exceptions.UnknownTimeZoneError:
    st.error(f"Invalid TARGET_TIMEZONE: '{TARGET_TIMEZONE}'. Use valid Olson name."); st.stop()

def get_current_time_in_tz(): return datetime.now(timezone.utc).astimezone(tz)
def get_current_month_year_str(): return get_current_time_in_tz().strftime("%Y-%m")

# --- Load or create data ---
def load_data(path, columns):
    if os.path.exists(path):
        try:
            if os.path.getsize(path) > 0:
                df = pd.read_csv(path)
                for col in columns:
                    if col not in df.columns: df[col] = pd.NA
                num_cols = ["Amount", "TargetAmount", "AchievedAmount", "Latitude", "Longitude"]
                for nc in num_cols:
                    if nc in columns and nc in df.columns:
                         df[nc] = pd.to_numeric(df[nc], errors='coerce')
                return df
            else: return pd.DataFrame(columns=columns)
        except pd.errors.EmptyDataError: return pd.DataFrame(columns=columns)
        except Exception as e:
            st.error(f"Error loading {path}: {e}. Empty DataFrame returned.")
            return pd.DataFrame(columns=columns)
    else:
        df = pd.DataFrame(columns=columns)
        try: df.to_csv(path, index=False)
        except Exception as e: st.warning(f"Could not create {path}: {e}")
        return df

ATTENDANCE_COLUMNS = ["Username", "Type", "Timestamp", "Latitude", "Longitude"]
ALLOWANCE_COLUMNS = ["Username", "Type", "Amount", "Reason", "Date"]
GOALS_COLUMNS = ["Username", "MonthYear", "GoalDescription", "TargetAmount", "AchievedAmount", "Status"]

attendance_df = load_data(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
allowance_df = load_data(ALLOWANCE_FILE, ALLOWANCE_COLUMNS)
goals_df = load_data(GOALS_FILE, GOALS_COLUMNS)

if "auth" not in st.session_state: st.session_state.auth = {"logged_in": False, "username": None, "role": None}

if not st.session_state.auth["logged_in"]:
    st.title("🙂HR Dashboard Login")
    st.markdown('<div class="login-container card">', unsafe_allow_html=True)
    st.markdown("<h3>🔐 Login</h3>", unsafe_allow_html=True)
    uname = st.text_input("Username", key="login_uname")
    pwd = st.text_input("Password", type="password", key="login_pwd")
    if st.button("Login", key="login_button"):
        user_creds = USERS.get(uname)
        if user_creds and user_creds["password"] == pwd:
            st.session_state.auth = {"logged_in": True, "username": uname, "role": user_creds["role"]}
            st.success("Login successful!"); st.rerun()
        else: st.error("Invalid username or password.")
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

st.title("👨‍💼 HR Dashboard")
current_user = st.session_state.auth

with st.sidebar:
    st.markdown(f"<div class='welcome-text'>👋 Welcome, {current_user['username']}!</div>", unsafe_allow_html=True)
    nav_options = ["📆 Attendance", "🧾 Allowance", "🎯 Goal Tracker", "📊 View Logs"]
    nav = st.radio("Navigation", nav_options, key="sidebar_nav_main") # Unique key
    user_sidebar_info = USERS.get(current_user["username"], {})
    if user_sidebar_info.get("profile_photo") and os.path.exists(user_sidebar_info["profile_photo"]):
        st.image(user_sidebar_info["profile_photo"], width=80, use_column_width='auto')
    st.markdown(f"<p style='text-align:center; font-size:0.9em; color: #e0e0e0;'>{user_sidebar_info.get('position', 'N/A')}</p>", unsafe_allow_html=True)
    st.markdown("---")
    if st.button("🔒 Logout", key="logout_button_sidebar", use_container_width=True):
        st.session_state.auth = {"logged_in": False, "username": None, "role": None}
        st.success("Logged out successfully."); st.rerun()

if nav == "📆 Attendance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🕒 Digital Attendance</h3>", unsafe_allow_html=True) # Using h3 from card styling
    location_data = streamlit_geolocation(key="attendance_page_location_final")
    lat, lon = None, None
    if location_data and 'latitude' in location_data and 'longitude' in location_data:
        lat, lon = location_data['latitude'], location_data['longitude']
        accuracy_str = f"(Accuracy: {location_data.get('accuracy', 0):.0f}m)" if location_data.get('accuracy') else ""
        st.caption(f"📍 Current Location: Lat {lat:.4f}, Lon {lon:.4f} {accuracy_str}")
        st.markdown(f"[View on Google Maps](https://www.google.com/maps?q={lat},{lon})", unsafe_allow_html=True)
    else: st.warning("📍 Location access denied or unavailable. Please allow browser location access.", icon="📡")
    st.markdown("---")
    st.markdown('<div class="button-column-container">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    common_data = {"Username": current_user["username"], "Latitude": lat if lat else pd.NA, "Longitude": lon if lon else pd.NA}
    with col1:
        if st.button("✅ Check In", key="check_in_btn_main", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = pd.DataFrame([{"Type": "Check-In", "Timestamp": now_str, **common_data}], columns=ATTENDANCE_COLUMNS)
            attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
            try: attendance_df.to_csv(ATTENDANCE_FILE, index=False); st.success(f"Checked in at {now_str}."); st.rerun()
            except Exception as e: st.error(f"Error saving: {e}")
    with col2:
        if st.button("🚪 Check Out", key="check_out_btn_main", use_container_width=True):
            now_str = get_current_time_in_tz().strftime("%Y-%m-%d %H:%M:%S")
            new_entry = pd.DataFrame([{"Type": "Check-Out", "Timestamp": now_str, **common_data}], columns=ATTENDANCE_COLUMNS)
            attendance_df = pd.concat([attendance_df, new_entry], ignore_index=True)
            try: attendance_df.to_csv(ATTENDANCE_FILE, index=False); st.success(f"Checked out at {now_str}."); st.rerun()
            except Exception as e: st.error(f"Error saving: {e}")
    st.markdown('</div></div>', unsafe_allow_html=True)

elif nav == "🧾 Allowance":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>💼 Claim Allowance</h3>", unsafe_allow_html=True)
    st.markdown("<h6>Select Allowance Type:</h6>", unsafe_allow_html=True)
    a_type = st.radio("", ["Travel", "Dinner", "Medical", "Internet", "Other"], key="allowance_type_radio_main", horizontal=True, label_visibility='collapsed')
    amount = st.number_input("Enter Amount (INR):", min_value=0.01, step=10.0, format="%.2f", key="allowance_amount_main")
    reason = st.text_area("Reason for Allowance:", key="allowance_reason_main", placeholder="Please provide a clear justification...")
    if st.button("Submit Allowance Request", key="submit_allowance_btn_main", use_container_width=True):
        if a_type and amount > 0 and reason.strip():
            date_str = get_current_time_in_tz().strftime("%Y-%m-%d")
            new_entry_data = {"Username": current_user["username"], "Type": a_type, "Amount": amount, "Reason": reason, "Date": date_str}
            new_entry = pd.DataFrame([new_entry_data], columns=ALLOWANCE_COLUMNS)
            allowance_df = pd.concat([allowance_df, new_entry], ignore_index=True)
            try: allowance_df.to_csv(ALLOWANCE_FILE, index=False); st.success(f"Allowance for ₹{amount:.2f} submitted."); st.rerun()
            except Exception as e: st.error(f"Error saving: {e}")
        else: st.warning("Please complete all fields with valid values.")
    st.markdown('</div>', unsafe_allow_html=True)

elif nav == "🎯 Goal Tracker":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("<h3>🎯 Sales Goal Tracker</h3>", unsafe_allow_html=True)
    # Ensure goals_df is accessible and up-to-date
    # No need for 'global goals_df' if it's loaded at script start and passed around or re-assigned like:
    # goals_df = updated_df
    current_month_year = get_current_month_year_str()
    status_options = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"]

    if current_user["role"] == "admin":
        st.markdown("<h4>Admin: Manage & Track Employee Goals</h4>", unsafe_allow_html=True)
        admin_action = st.radio("Action:", ["View Team Progress", "Set/Edit Employee Goal"], key="admin_goal_action_radio_main", horizontal=True)

        if admin_action == "View Team Progress":
            st.markdown(f"<h5>Team Goal Progress for {current_month_year}</h5>", unsafe_allow_html=True)
            employee_users = [uname for uname, udata in USERS.items() if udata["role"] == "employee"]
            if not employee_users: st.info("No employees found.")
            else:
                summary_data = []
                for emp_name in employee_users:
                    user_info_gt = USERS.get(emp_name, {})
                    emp_current_goal = goals_df[(goals_df["Username"] == emp_name) & (goals_df["MonthYear"] == current_month_year)]
                    target, achieved, prog_val, goal_desc, status = 0.0, 0.0, 0.0, "Not Set", "N/A"
                    if not emp_current_goal.empty:
                        g_data = emp_current_goal.iloc[0]
                        target = pd.to_numeric(g_data.get("TargetAmount"), errors='coerce').fillna(0.0)
                        achieved = pd.to_numeric(g_data.get("AchievedAmount"), errors='coerce').fillna(0.0)
                        if target > 0: prog_val = min(achieved / target, 1.0)
                        goal_desc, status = g_data.get("GoalDescription", "N/A"), g_data.get("Status", "N/A")
                    summary_data.append({
                        "Photo": user_info_gt.get("profile_photo",""), "Employee": emp_name, "Position": user_info_gt.get("position","N/A"),
                        "Goal": goal_desc, "Target": target, "Achieved": achieved, "Progress": prog_val, "Status": status })
                if summary_data:
                    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True, column_config={
                        "Photo": st.column_config.ImageColumn("Pic", width="small"),
                        "Target": st.column_config.NumberColumn("Target (₹)", format="%.0f"),
                        "Achieved": st.column_config.NumberColumn("Achieved (₹)", format="%.0f"),
                        "Progress": st.column_config.ProgressColumn("Progress", format="%.0f%%", min_value=0, max_value=1)})
        elif admin_action == "Set/Edit Employee Goal":
            st.markdown("<h5>Set or Update Employee Goal</h5>", unsafe_allow_html=True)
            sel_emp = st.selectbox("Select Employee:", [u for u, d in USERS.items() if d["role"] == "employee"], key="goal_sel_emp_admin_main")
            year_now = get_current_time_in_tz().year
            months_list = sorted(list(set( [datetime(y,m,1).strftime("%Y-%m") for y in range(year_now-1, year_now+2) for m in range(1,13)] + [current_month_year] )), reverse=True)
            def_m_idx = months_list.index(current_month_year) if current_month_year in months_list else 0
            target_m_y = st.selectbox("Goal Month (YYYY-MM):", months_list, index=def_m_idx, key="goal_month_admin_main")

            existing_g = goals_df[(goals_df["Username"] == sel_emp) & (goals_df["MonthYear"] == target_m_y)]
            g_desc, g_target, g_achieved, g_status = "", 0.0, 0.0, "Not Started"
            if not existing_g.empty:
                g_d = existing_g.iloc[0]
                g_desc, g_target, g_achieved, g_status = g_d.get("GoalDescription",""), pd.to_numeric(g_d.get("TargetAmount"),errors='coerce').fillna(0.0), pd.to_numeric(g_d.get("AchievedAmount"),errors='coerce').fillna(0.0), g_d.get("Status","Not Started")
                st.info(f"Editing existing goal for {sel_emp} for {target_m_y}.")

            with st.form(key=f"set_goal_form_{sel_emp}_{target_m_y}_main"):
                new_g_desc = st.text_area("Goal Description:", value=g_desc)
                new_g_target = st.number_input("Target Sales (INR):", 0.0, value=g_target, step=1000.0, format="%.2f")
                new_g_achieved = st.number_input("Achieved Sales (INR):", 0.0, value=g_achieved, step=100.0, format="%.2f")
                new_g_status = st.selectbox("Status:", status_options, index=status_options.index(g_status) if g_status in status_options else 0)
                submitted = st.form_submit_button("Save Goal")

            if submitted:
                if not new_g_desc.strip(): st.warning("Description needed.")
                elif new_g_target <= 0 and new_g_status not in ["Cancelled", "On Hold", "Not Started"]: st.warning("Target > 0 unless Cancelled/On Hold/Not Started.")
                else:
                    if not existing_g.empty:
                        goals_df.loc[existing_g.index[0]] = [sel_emp, target_m_y, new_g_desc, new_g_target, new_g_achieved, new_g_status]
                        msg="updated"
                    else:
                        new_g_entry = pd.DataFrame([{"Username":sel_emp, "MonthYear":target_m_y, "GoalDescription":new_g_desc, "TargetAmount":new_g_target, "AchievedAmount":new_g_achieved, "Status":new_g_status}], columns=GOALS_COLUMNS)
                        # Need to reassign goals_df if it was empty or to ensure type consistency
                        goals_df = pd.concat([goals_df, new_g_entry], ignore_index=True)
                        msg="set"
                    try: goals_df.to_csv(GOALS_FILE, index=False); st.success(f"Goal for {sel_emp} ({target_m_y}) {msg}!"); st.rerun()
                    except Exception as e: st.error(f"Error saving: {e}")
    else: # Employee View
        st.markdown("<h4>My Sales Goals</h4>", unsafe_allow_html=True)
        my_all_goals = goals_df[goals_df["Username"] == current_user["username"]].copy()
        if not my_all_goals.empty:
            for col_n in ["TargetAmount", "AchievedAmount"]: my_all_goals[col_n] = pd.to_numeric(my_all_goals[col_n], errors='coerce').fillna(0.0)

        current_g = my_all_goals[my_all_goals["MonthYear"] == current_month_year]
        st.markdown(f"<h5>Current Goal: {current_month_year}</h5>", unsafe_allow_html=True)
        if not current_g.empty:
            g_e = current_g.iloc[0]
            target_amt, achieved_amt = g_e.get("TargetAmount",0.0), g_e.get("AchievedAmount",0.0)
            prog_val = min(achieved_amt / target_amt, 1.0) if target_amt > 0 else 0.0
            st.markdown(f"**Description:** {g_e.get('GoalDescription', 'N/A')}")
            c1,c2,c3 = st.columns(3)
            c1.metric("Target Sales", f"₹{target_amt:,.0f}"); c2.metric("Achieved Sales", f"₹{achieved_amt:,.0f}")
            with c3: st.metric("Status", g_e.get('Status','In Progress')); st.progress(prog_val); st.caption(f"{prog_val*100:.1f}% Completed")
            st.markdown("---")
            st.markdown("<h6>Update My Achievement (Current Month)</h6>", unsafe_allow_html=True)
            with st.form(key=f"update_ach_form_{current_user['username']}_main"):
                new_ach_val = st.number_input("My Total Achieved Sales (INR):", 0.0, value=achieved_amt, step=100.0, format="%.2f")
                submit_upd = st.form_submit_button("Update My Achieved Amount")
            if submit_upd:
                idx_to_update = current_g.index[0]
                goals_df.loc[idx_to_update, "AchievedAmount"] = new_ach_val
                goals_df.loc[idx_to_update, "Status"] = "Achieved" if new_ach_val >= target_amt and target_amt > 0 else "In Progress"
                try: goals_df.to_csv(GOALS_FILE, index=False); st.success("Achievement updated!"); st.rerun()
                except Exception as e: st.error(f"Error updating: {e}")
        else: st.info(f"No goal set for you for {current_month_year}. Contact admin.")
        st.markdown("---")
        st.markdown("<h5>My Past Goals History</h5>", unsafe_allow_html=True)
        past_g = my_all_goals[my_all_goals["MonthYear"] != current_month_year].sort_
