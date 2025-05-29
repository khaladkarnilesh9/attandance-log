import streamlit as st
from streamlit_option_menu import option_menu

# CSS styling for Kaggle-like interface
st.markdown("""
<style>
    /* Main styling */
    :root {
        --kaggle-blue: #20BEFF;
        --kaggle-dark: #1C1C1C;
        --kaggle-light: #F5F5F5;
        --kaggle-gray: #E0E0E0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid var(--kaggle-gray) !important;
    }
    
    .sidebar-icon {
        font-size: 20px;
        margin-right: 10px;
        color: #666;
    }
    
    .sidebar-item {
        padding: 8px 16px;
        border-radius: 4px;
        margin: 4px 0;
        display: flex;
        align-items: center;
    }
    
    .sidebar-item:hover {
        background-color: var(--kaggle-light);
    }
    
    .sidebar-item.active {
        background-color: #E6F7FF;
        color: var(--kaggle-blue);
        font-weight: 500;
    }
    
    .sidebar-item.active .sidebar-icon {
        color: var(--kaggle-blue);
    }
    
    /* Main content styling */
    .dataset-card {
        border: 1px solid var(--kaggle-gray);
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 16px;
    }
    
    .dataset-title {
        color: var(--kaggle-blue);
        font-size: 18px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation with icons
with st.sidebar:
    st.markdown("""
    <div style="padding: 16px 0 24px 16px; border-bottom: 1px solid #E0E0E0; margin-bottom: 16px;">
        <h2 style="color: var(--kaggle-blue); margin: 0;">Trackspere</h2>
        <p style="color: #666; margin: 4px 0 0 0;">Track your Buissness</p>
    </div>
    """, unsafe_allow_html=True)    
    
    nav_options = [
        "Attendance",
        "Upload Activity Photo",
        "Allowance",
        "Goal Tracker",
        "Payment Collection Tracker",
        "View Logs",
        "Create Order"
    ]
    
    selected = option_menu(    
        None,
        ["Home", "Attendance", "Upload Activity Photo", "Goal Tracker", "Payment Collection Tracker","View Logs","Create Order"],
        icons=['house','calender','photo', 'database', 'book', 'fingureprint', 'doller'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important"},
            "nav-link": {
                "font-size": "14px",
                "text-align": "left",
                "margin": "4px 0",
                "border-radius": "4px",
                "padding": "8px 16px",
            },
            "nav-link-selected": {
                "background-color": "#E6F7FF",
                "color": "#20BEFF",
                "font-weight": "500",
            },
            "icon": {
                "font-size": "18px",
                "margin-right": "10px",
                "color": "#666",
            },
        }
    )

# Main content
st.title("Datasets Dashboard")

# Sample dataset cards
datasets = [
    {
        "title": "Titanic - Machine Learning from Disaster",
        "description": "The sinking of the Titanic is one of the most infamous shipwrecks in history.",
        "size": "70KB",
        "downloads": "1.2M",
        "likes": "12K"
    },
    {
        "title": "Iris Species",
        "description": "This is perhaps the best known database to be found in pattern recognition literature.",
        "size": "4KB",
        "downloads": "850K",
        "likes": "8.5K"
    },
    {
        "title": "House Prices - Advanced Regression Techniques",
        "description": "Predict sales prices and practice feature engineering, RFs, and gradient boosting.",
        "size": "350KB",
        "downloads": "950K",
        "likes": "9.2K"
    }
]

for dataset in datasets:
    st.markdown(f"""
    <div class="dataset-card">
        <div class="dataset-title">{dataset['title']}</div>
        <p style="color: #666; margin: 8px 0;">{dataset['description']}</p>
        <div style="display: flex; gap: 16px; color: #666; font-size: 14px;">
            <span>📦 {dataset['size']}</span>
            <span>⬇️ {dataset['downloads']}</span>
            <span>❤️ {dataset['likes']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Search and filter section
st.sidebar.markdown("""
<div style="padding: 16px 0; border-top: 1px solid #E0E0E0; margin-top: 16px;">
    <h3 style="font-size: 16px; margin-bottom: 8px;">Filters</h3>
    <div style="margin-bottom: 12px;">
        <label style="display: block; font-size: 14px; margin-bottom: 4px; color: #666;">File types</label>
        <select style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #E0E0E0;">
            <option>All</option>
            <option>CSV</option>
            <option>JSON</option>
            <option>SQL</option>
        </select>
    </div>
    <div style="margin-bottom: 12px;">
        <label style="display: block; font-size: 14px; margin-bottom: 4px; color: #666;">License</label>
        <select style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #E0E0E0;">
            <option>Any</option>
            <option>CC0</option>
            <option>CC BY-SA</option>
            <option>GPL</option>
        </select>
    </div>
</div>
""", unsafe_allow_html=True)
