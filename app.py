import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz # For time zone awareness

# --- Configuration (Adjust as needed) ---
ACTIVITY_PHOTOS_DIR = "activity_photos"
ACTIVITY_LOG_FILE = "activity_log.csv"
ACTIVITY_LOG_COLUMNS = ["Username", "Timestamp", "Description", "ImageFile", "Latitude", "Longitude"]

# Ensure the directory exists
os.makedirs(ACTIVITY_PHOTOS_DIR, exist_ok=True)

# Initialize session_state variables
if "activity_log_df" not in st.session_state:
    if os.path.exists(ACTIVITY_LOG_FILE):
        st.session_state.activity_log_df = pd.read_csv(ACTIVITY_LOG_FILE)
    else:
        st.session_state.activity_log_df = pd.DataFrame(columns=ACTIVITY_LOG_COLUMNS)

# Initialize authentication state (moved here for clarity)
if "auth" not in st.session_state:
    st.session_state.auth = {"logged_in": False, "username": None, "role": None}
    # Set default values for messages
    st.session_state.user_message = ""
    st.session_state.message_type = ""

# --- IMPORTANT: Initialize active_page here ---
if "active_page" not in st.session_state:
    st.session_state.active_page = "login" # Or whatever your default landing page is

# --- Mock USERS and authentication state for testing (consider removing in production) ---
USERS = {
    "testuser": {
        "position": "Sales Executive",
        "profile_photo": "https://via.placeholder.com/150/007bff/FFFFFF?text=TU" # Placeholder image
    },
    "admin": {
        "position": "System Administrator",
        "profile_photo": "https://via.placeholder.com/150/f39c12/FFFFFF?text=AD" # Placeholder image
    }
}

# --- Utility Functions (Place these outside of page functions) ---
def get_current_time_in_tz():
    india_tz = pytz.timezone('Asia/Kolkata')
    return datetime.now(india_tz)

def display_message():
    if "user_message" in st.session_state and st.session_state.user_message:
        if st.session_state.message_type == "success":
            st.success(st.session_state.user_message)
        elif st.session_state.message_type == "error":
            st.error(st.session_state.user_message)
        elif st.session_state.message_type == "warning":
            st.warning(st.session_state.user_message)
        elif st.session_state.message_type == "info":
            st.info(st.session_state.user_message)
        # Clear the message after displaying
        st.session_state.user_message = ""
        st.session_state.message_type = ""

def login_page():
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            # Simple mock authentication
            if username in USERS and password == "password": # Use a real password check in production
                st.session_state.auth["logged_in"] = True
                st.session_state.auth["username"] = username
                st.session_state.auth["role"] = "admin" if username == "admin" else "employee"
                st.session_state.active_page = "Attendance" # Set default page after login
                st.rerun()
            else:
                st.session_state.user_message = "Invalid username or password"
                st.session_state.message_type = "error"
                st.rerun()

def logout():
    st.session_state.auth["logged_in"] = False
    st.session_state.auth["username"] = None
    st.session_state.auth["role"] = None
    st.session_state.active_page = "login" # Redirect to login page
    st.rerun()

# --- Page Functions ---
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


# Place this at the very top of your app.py, before any other Streamlit calls
st.set_page_config(layout="wide") # Good for dashboards
st.markdown("""
<style>
    /* Global Styles & Resets */
    html, body {
        height: 100%;
        margin: 0;
        padding: 0;
        font-family: 'Roboto', sans-serif; /* Apply Roboto font globally */
        color: #333333; /* Default text color */
    }

    [data-testid="stAppViewContainer"] {
        background-color: #f0f2f6; /* Light gray background for the entire app */
    }

    /* Hide Streamlit's default header, footer, and toolbar */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    div[data-testid="stToolbar"] {
        visibility: hidden;
        height: 0%;
        position: fixed; /* Completely hide it */
    }

    /* Input Fields (Text, Number, Text Area, Selectbox) - Enhanced Styling */
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    div[data-baseweb="select"] input { /* Target selectbox input */
        background-color: white;
        color: #335677; /* Darker text for input values */
        border: 1px solid #ced4da; /* A slightly darker border color */
        border-radius: 8px; /* Slightly more rounded corners */
        padding: 10px 15px; /* More padding */
        font-size: 1rem; /* Standard font size */
        transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        box-shadow: none; /* Remove any default shadow */
    }

    /* Placeholder color */
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder,
    .stNumberInput input::placeholder {
        color: #6c757d !important; /* Slightly darker grey for placeholder */
        opacity: 1; /* Ensure full visibility */
    }

    /* Focus styles for inputs */
    .stTextInput input:focus,
    .stTextArea textarea:focus,
    .stNumberInput input:focus {
        border-color: #007bff; /* Primary blue on focus */
        box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25); /* Subtle glow */
        outline: none; /* Remove default outline */
    }
    /* Selectbox focus (it's a bit different because of BaseWeb) */
    div[data-baseweb="select"] div[role="button"]:focus-within {
        border-color: #007bff;
        box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
        outline: none;
    }

    /* Sidebar Styling (Navigation Bar Look & Feel) */
    [data-testid="stSidebar"] {
        background-color: #2c3e50; /* Darker blue-grey for sidebar background */
        padding-top: 1rem;
        box-shadow: 2px 0 10px rgba(0,0,0,0.2); /* More prominent shadow */
    }
    [data-testid="stSidebarContent"] {
        display: flex;
        flex-direction: column;
        height: 100%; /* Make sidebar content fill height */
        padding: 0; /* Remove default sidebar padding */
    }

    /* User Profile Section in Sidebar */
    .user-profile-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 1.5rem 1rem;
        margin-bottom: 1.5rem;
        text-align: center;
        background-color: #34495e; /* Slightly lighter than sidebar background */
        border-radius: 10px; /* Rounded corners for the profile box */
        margin: 1rem;
    }
    .user-profile-img {
        width: 90px; /* Slightly larger image */
        height: 90px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 0.75rem;
        border: 3px solid #f39c12; /* Accent border color */
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .welcome-text {
        font-weight: 600;
        color: white; /* White text for welcome */
        margin-bottom: 0.25rem;
        font-size: 1.2rem;
    }
    .user-position {
        font-size: 0.9rem;
        color: #bdc3c7; /* Lighter grey for position */
    }
    .divider {
        border-top: 1px solid #4a627a; /* Lighter divider for contrast */
        margin: 0.5rem 0 1.5rem 0;
    }

    /* Navigation Items (Sidebar Buttons) - Enhanced Styles */
    .sidebar-nav-item {
        display: flex;
        align-items: center;
        padding: 0.85rem 1.2rem; /* More padding for a bolder look */
        margin: 0.25rem 0.75rem; /* Space between items */
        border-radius: 8px;
        color: #ecf0f1; /* Light text color for inactive items */
        font-size: 1.05rem; /* Slightly larger font */
        font-weight: 500;
        transition: background-color 0.2s, color 0.2s, transform 0.1s;
        position: relative; /* Crucial for positioning the invisible button */
        overflow: hidden; /* Hide any overflow */
    }
    .sidebar-nav-item:hover {
        background-color: #3498db; /* Primary blue on hover */
        color: white;
        transform: translateX(5px); /* Slight slide effect on hover */
    }
    .sidebar-nav-item.active-nav-item {
        background-color: #007bff; /* Primary blue for active */
        color: white;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3); /* More pronounced shadow */
        transform: translateX(0); /* Ensure no slide for active */
    }
    .sidebar-nav-item .material-symbols-outlined {
        margin-right: 0.8rem; /* More space for icon */
        font-size: 1.6rem; /* Slightly larger icon */
        width: 28px; height: 28px; /* Fixed size for icons */
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: #ecf0f1; /* Icon color for inactive */
    }
    .sidebar-nav-item.active-nav-item .material-symbols-outlined {
        color: white; /* Icon color for active */
    }

    /* !!! CRUCIAL FIX FOR DUPLICATE LABELS !!! */
    /* Target the Streamlit button that appears directly after .sidebar-nav-item */
    /* This targets the button (and its internal content div) */
    .sidebar-nav-item + div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button {
        /* Make the actual button element completely transparent and cover the custom div */
        background-color: transparent !important;
        border: none !important;
        color: transparent !important; /* Hide text color of the button */
        opacity: 0; /* Make the button itself transparent */
        position: absolute !important; /* Position it over the custom div */
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 10; /* Ensure it's on top for clicks */
        cursor: pointer; /* Keep cursor pointer to indicate interactivity */
        pointer-events: all !important; /* Ensure clicks pass through */
    }

    /* Explicitly hide the content div inside the Streamlit button */
    .sidebar-nav-item + div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button > div[data-testid="baseButton-children"] {
        opacity: 0 !important; /* Hide the default button label text */
        visibility: hidden !important; /* Ensure it's fully hidden */
        /* Also make sure it doesn't take up any space */
        width: 0 !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* Make sure hover on the invisible button doesn't reveal anything */
    .sidebar-nav-item + div[data-testid="stVerticalBlock"] > div[data-testid="stButton"] > button:hover {
        background-color: transparent !important; /* Keep background transparent on hover */
        border: none !important; /* No border on hover */
    }

    /* Logout button specific styling (push to bottom) */
    .logout-container {
        margin-top: auto; /* Pushes logout button to the very bottom of the sidebar */
        padding: 1rem;
        border-top: 1px solid #4a627a; /* Divider line */
        background-color: #2c3e50; /* Match sidebar background */
    }
    .logout-container .stButton > button {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #e74c3c; /* Red for logout */
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: background-color 0.2s, transform 0.1s;
        width: 100%; /* Make button full width */
        /* Override the general invisible button styles for logout */
        opacity: 1 !important; /* Make logout button visible */
        position: static !important; /* Remove absolute positioning */
        height: auto !important;
        z-index: auto !important;
        pointer-events: all !important; /* Ensure clicks pass through */
    }
    .logout-container .stButton > button:hover {
        background-color: #c0392b; /* Darker red on hover */
        transform: translateY(-2px);
    }
    .logout-container .stButton > button:active {
        background-color: #a53026;
        transform: translateY(0);
    }
    .logout-container .stButton > button .material-symbols-outlined {
        margin-right: 0.5rem;
        font-size: 1.5rem;
    }

    /* Main Content Area Styling */
    .main-content-area {
        padding: 1.5rem 2rem;
        gap: 1.5rem; /* Space between content blocks */
    }
    /* Ensure Streamlit's main block takes up correct padding */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        padding: 0; /* Remove default padding from inner vertical blocks */
    }

    .card {
        background-color: white;
        border-radius: 12px;
        padding: 2.5rem; /* More padding inside cards */
        box-shadow: 0 6px 20px rgba(0,0,0,0.1); /* Stronger, softer shadow */
        margin-bottom: 1.5rem;
    }
    .card h3, .card h4, .card h5 {
        color: #2c3e50; /* Darker color for headings */
        margin-bottom: 1.5rem;
        font-weight: 700; /* Bolder headings */
    }
    /* General Streamlit button styling for content area buttons */
    /* This overrides the invisible button style for regular page buttons */
    .stButton > button:not(.logout-container .stButton > button):not([data-testid^="stSidebar"]) { /* Target buttons NOT in sidebar and not logout */
        border-radius: 8px;
        font-weight: 600; /* Bolder button text */
        padding: 0.8rem 1.5rem; /* More padding for buttons */
        min-height: 45px; /* Ensure minimum height */
        transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.1s ease;
        opacity: 1 !important; /* Ensure visibility for content area buttons */
        position: static !important; /* Reset positioning */
        top: auto !important;
        left: auto !important;
        width: auto !important;
        height: auto !important;
        z-index: auto !important;
        color: inherit !important; /* Reset text color */
        background-color: inherit !important; /* Reset background color */
    }

    .stButton > button.primary {
        background-color: #007bff;
        color: white;
        border: none;
    }
    .stButton > button.primary:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
    }
    .stButton > button[data-testid="baseButton-secondary"] {
        background-color: #e9ecef; /* Lighter background for secondary */
        color: #4a4a4a;
        border: 1px solid #ced4da;
    }
    .stButton > button[data-testid="baseButton-secondary"]:hover {
        background-color: #d8dee2;
        transform: translateY(-2px);
    }

    .custom-notification {
        padding: 1rem 1.25rem; /* More padding */
        border-radius: 8px; /* Consistent border radius */
        margin-bottom: 1.5rem; /* More space below notification */
        border: 1px solid transparent;
        font-size: 1rem; /* Clearer font size */
        font-weight: 500;
    }
    .custom-notification.success {
        color: #0f5132; background-color: #d1e7dd; border-color: #badbcc;
    }
    .custom-notification.error {
        color: #842029; background-color: #f8d7da; border-color: #f5c2c7;
    }
    .custom-notification.warning {
        color: #664d03; background-color: #fff3cd; border-color: #ffecb5;
    }
    .custom-notification.info {
        color: #055160; background-color: #cff4fc; border-color: #b6effb;
    }

    .button-column-container {
        display: flex;
        gap: 1rem; /* Space between the check-in/out buttons */
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .stColumn {
        display: flex;
        flex-direction: column;
        flex-grow: 1; /* Make columns grow evenly */
    }
    .stColumn > .stButton {
        flex-grow: 1; /* Make buttons fill available column width */
        width: 100%; /* Ensure button takes full width within its column */
    }
    .stDateInput, .stNumberInput, .stTextInput, .stTextArea, .stSelectbox, .stRadio {
        margin-bottom: 1.25rem; /* Consistent spacing for form elements */
    }
    .stForm > div > div {
        gap: 1.25rem; /* Adjust gap for form elements */
    }

    /* Adjust progress bar colors */
    .stProgress > div > div {
        background-color: #e9ecef; /* Lighter background for empty progress bar */
        border-radius: 5px;
    }
    .stProgress > div > div > div {
        background-color: #28a745; /* Green for progress fill */
        border-radius: 5px;
    }

    /* Style for Plotly charts */
    .stPlotlyChart {
        border-radius: 12px;
        overflow: hidden; /* Ensure chart elements respect border-radius */
        box-shadow: 0 4px 15px rgba(0,0,0,0.08); /* Consistent shadow */
    }

    /* Streamlit labels */
    div[data-testid="stWidgetLabel"] > p {
        font-weight: 500;
        color: #555555;
        margin-bottom: 0.5rem;
    }
    /* Specific targeting for radio/checkbox labels if needed */
    .stRadio > label, .stCheckbox > label {
        font-weight: 500;
        color: #555555;
    }
    
    /* Small adjustments for layout */
    div[data-testid="stVerticalBlock"] > div:not(:last-child) {
        margin-bottom: 1.5rem; /* Add space between vertical blocks for better readability */
    }
    
</style>
""", unsafe_allow_html=True)


# --- Main Application Flow ---
if not st.session_state.auth["logged_in"]:
    login_page() # Assuming you have a login_page() function
else:
    with st.sidebar:
        # Profile Section
        current_username = st.session_state.auth["username"]
        current_role = st.session_state.auth["role"]
        current_position = USERS[current_username]["position"]
        profile_photo_path = USERS[current_username]["profile_photo"]

        st.markdown(f"""
            <div class="user-profile-section">
                <img src="{profile_photo_path}" class="user-profile-img">
                <div class="welcome-text">Welcome, {current_username}!</div>
                <div class="user-position">{current_position}</div>
            </div>
            <div class="divider"></div>
        """, unsafe_allow_html=True)

        # Navigation Menu
        nav_items_employee = [
            ("Attendance", "event_available"),
            ("Upload Activity Photo", "upload_file"), # This is the page we're integrating
            ("Claim Allowance", "payments"),
            ("Sales Goal Tracker", "track_changes"),
            ("Payment Goal Tracker", "paid"),
            ("Activity Log", "list_alt"),
        ]
        nav_items_admin = nav_items_employee # Or add admin-specific pages

        nav_items = nav_items_admin if current_role == "admin" else nav_items_employee

        for page_name, icon_name in nav_items:
            is_active = "active-nav-item" if st.session_state.active_page == page_name else ""
            
            # The visual part of the button
            st.markdown(f"""
                <div class="sidebar-nav-item {is_active}">
                    <span class="material-symbols-outlined">{icon_name}</span> {page_name}
                </div>
            """, unsafe_allow_html=True)
            
            # The functional (invisible) button for navigation
            if st.button(page_name, key=f"nav_btn_{page_name}", use_container_width=True):
                st.session_state.active_page = page_name
                st.rerun()

        # Logout Button
        st.markdown('<div class="logout-container">', unsafe_allow_html=True)
        logout_label = '<span class="material-symbols-outlined">logout</span> Logout'
        if st.button(logout_label, key="logout_btn", use_container_width=True, unsafe_allow_html=True):
            # Assuming you have a logout() function
            def logout():
                st.session_state.auth["logged_in"] = False
                st.session_state.auth["username"] = None
                st.session_state.auth["role"] = None
                st.session_state.active_page = "login" # Redirect to login page
                st.rerun()
            logout()
        st.markdown('</div>', unsafe_allow_html=True)

    # Main Content Area
    st.markdown('<div class="main-content-area">', unsafe_allow_html=True)
    display_message() # Display messages at the top of the content area

    # Render content based on active page
    if st.session_state.active_page == "Attendance":
        # attendance_page() # Call your attendance page function
        st.write("Attendance Page Content Here")
    elif st.session_state.active_page == "Upload Activity Photo":
        upload_activity_photo_page() # <--- This is where your code integrates
    elif st.session_state.active_page == "Claim Allowance":
        # allowance_page() # Call your allowance page function
        st.write("Claim Allowance Page Content Here")
    elif st.session_state.active_page == "Sales Goal Tracker":
        # goal_tracker_page() # Call your sales goal tracker function
        st.write("Sales Goal Tracker Page Content Here")
    elif st.session_state.active_page == "Payment Goal Tracker":
        # payment_goals_page() # Call your payment goal tracker function
        st.write("Payment Goal Tracker Page Content Here")
    elif st.session_state.active_page == "Activity Log":
        # activity_log_page() # Call your activity log page function
        st.write("Activity Log Page Content Here")
    
    st.markdown('</div>', unsafe_allow_html=True)
