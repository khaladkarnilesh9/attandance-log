<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Employee Portal - AI Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet">
    
    <style>
        /* Define Google AI Dashboard inspired color palette using CSS variables */
        :root {
            --primary-bg: #202124; /* Dark background */
            --secondary-bg: #2c2e30; /* Slightly lighter dark for cards/sidebar */
            --text-color: #e8eaed; /* Light text */
            --accent-blue: #8ab4f8; /* Google blue accent */
            --border-color: #3c4043; /* Subtle border for cards/inputs */
            --shadow-color: rgba(0, 0, 0, 0.4); /* Dark shadow */
            --success-color: #2ecc71; /* Green for success */
            --error-color: #e74c3c; /* Red for error */
            --warning-color: #f39c12; /* Orange for warning */
            --info-color: #3498db; /* Blue for info */
        }

        /* Global Styles & Resets */
        body {
            font-family: 'Inter', sans-serif; /* Apply Inter font globally */
            background-color: var(--primary-bg); /* Main app background */
            color: var(--text-color); /* Default text color */
            margin: 0;
            padding: 0;
            height: 100vh; /* Full viewport height */
            display: flex;
            flex-direction: column;
            overflow: hidden; /* Prevent body scroll, let inner divs scroll */
        }

        #app {
            display: flex;
            flex-grow: 1; /* Allow app to fill remaining space */
            overflow: hidden; /* Hide overflow from children */
        }

        /* Login Section Specific Styles */
        #login-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            background-color: var(--primary-bg);
        }
        .login-card {
            background-color: var(--secondary-bg);
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 6px 20px var(--shadow-color);
            border: 1px solid var(--border-color);
            width: 100%;
            max-width: 400px;
        }

        /* Dashboard Layout */
        #dashboard-section {
            display: flex;
            flex-grow: 1;
            overflow: hidden; /* Ensure sidebar and main content handle their own scroll */
        }

        /* Sidebar Styling */
        #sidebar {
            background-color: var(--secondary-bg);
            width: 280px; /* Fixed width for sidebar */
            flex-shrink: 0; /* Prevent sidebar from shrinking */
            padding-top: 1rem;
            box-shadow: 2px 0 10px var(--shadow-color);
            display: flex;
            flex-direction: column;
            overflow-y: auto; /* Allow sidebar content to scroll */
            border-right: 1px solid var(--border-color); /* Separator */
        }

        .user-profile-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 1.5rem 1rem;
            margin-bottom: 1.5rem;
            text-align: center;
            background-color: var(--primary-bg);
            border-radius: 10px;
            margin: 1rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .user-profile-img {
            width: 90px;
            height: 90px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 0.75rem;
            border: 3px solid var(--accent-blue);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .welcome-text {
            font-weight: 600;
            color: var(--text-color);
            margin-bottom: 0.25rem;
            font-size: 1.2rem;
        }
        .user-position {
            font-size: 0.9rem;
            color: #bdc3c7;
        }
        .divider {
            border-top: 1px solid var(--border-color);
            margin: 0.5rem 0 1.5rem 0;
        }

        /* Sidebar Navigation Items */
        .sidebar-nav-item {
            display: flex;
            align-items: center;
            padding: 0.85rem 1.2rem;
            margin: 0.25rem 0.75rem;
            border-radius: 8px;
            font-size: 1.05rem;
            font-weight: 500;
            transition: background-color 0.2s, color 0.2s, transform 0.1s;
            cursor: pointer;
            color: var(--text-color); /* Default text color */
            background-color: transparent;
        }
        .sidebar-nav-item:hover {
            background-color: var(--primary-bg);
            color: var(--accent-blue);
            transform: translateX(5px);
        }
        .sidebar-nav-item.active {
            background-color: var(--primary-bg);
            color: var(--accent-blue);
            box-shadow: 0 4px 12px rgba(138, 180, 248, 0.1);
            transform: translateX(0);
        }
        .sidebar-nav-item .material-symbols-outlined {
            margin-right: 0.8rem;
            font-size: 1.6rem;
            width: 28px; height: 28px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: inherit;
        }

        /* Logout button specific styling */
        .logout-container {
            margin-top: auto; /* Pushes logout button to the very bottom */
            padding: 1rem;
            border-top: 1px solid var(--border-color);
            background-color: var(--secondary-bg);
        }
        .logout-container button {
            background-color: var(--error-color);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            transition: background-color 0.2s, transform 0.1s;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .logout-container button:hover {
            background-color: #c0392b;
            transform: translateY(-2px);
        }
        .logout-container button .material-symbols-outlined {
            margin-right: 0.5rem;
            font-size: 1.5rem;
        }


        /* Main Content Area Styling */
        #main-content {
            flex-grow: 1;
            padding: 1.5rem 2rem;
            overflow-y: auto; /* Allow main content to scroll */
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        .card {
            background-color: var(--secondary-bg);
            border-radius: 12px;
            padding: 2.5rem;
            box-shadow: 0 6px 20px var(--shadow-color);
            margin-bottom: 1.5rem;
            border: 1px solid var(--border-color);
        }
        .card h3, .card h4, .card h5 {
            color: var(--accent-blue);
            margin-bottom: 1.5rem;
            font-weight: 700;
        }

        /* Form Elements */
        input[type="text"],
        input[type="password"],
        input[type="number"],
        textarea,
        select {
            background-color: var(--primary-bg);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 1rem;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
            box-shadow: none;
            width: 100%;
            box-sizing: border-box; /* Include padding in width */
        }
        input::placeholder, textarea::placeholder {
            color: #888;
            opacity: 1;
        }
        input:focus, textarea:focus, select:focus {
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 0.2rem rgba(138, 180, 248, 0.25);
            outline: none;
        }

        /* Buttons */
        button {
            background-color: var(--accent-blue);
            color: white;
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s, transform 0.1s;
        }
        button:hover {
            background-color: #6a9df8;
            transform: translateY(-2px);
        }
        button:active {
            background-color: #538ef0;
            transform: translateY(0);
        }
        button.secondary {
            background-color: var(--secondary-bg);
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }
        button.secondary:hover {
            background-color: var(--primary-bg);
            transform: translateY(-2px);
        }

        /* Custom Notifications */
        .notification {
            padding: 1rem 1.25rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
            border: 1px solid transparent;
            font-size: 1rem;
            font-weight: 500;
            display: none; /* Hidden by default */
        }
        .notification.show {
            display: block;
        }
        .notification.success {
            color: #b8e0d4; background-color: #1a4f32; border-color: #2e6b4e;
        }
        .notification.error {
            color: #f5c2c7; background-color: #6b1d24; border-color: #842029;
        }
        .notification.warning {
            color: #ffeeba; background-color: #664d03; border-color: #997300;
        }
        .notification.info {
            color: #b6effb; background-color: #055160; border-color: #076d7e;
        }

        /* Table Styling */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1.5rem;
        }
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        th {
            background-color: var(--primary-bg);
            font-weight: 600;
            color: var(--accent-blue);
        }
        tr:hover {
            background-color: rgba(138, 180, 248, 0.05);
        }

        /* Image preview for camera input */
        #camera-preview {
            width: 100%;
            max-width: 320px; /* Standard webcam width */
            height: auto;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin-top: 1rem;
            background-color: #000;
            display: block;
        }
        #camera-feed {
            width: 100%;
            height: auto;
            border-radius: 8px;
            display: block;
        }
        #camera-canvas {
            display: none; /* Hidden, used for capturing image */
        }

        /* Responsive adjustments */
        @media (max-width: 768px) {
            #sidebar {
                width: 200px;
            }
            #main-content {
                padding: 1rem;
            }
            .card {
                padding: 1.5rem;
            }
            .sidebar-nav-item {
                font-size: 0.95rem;
                padding: 0.75rem 1rem;
            }
            .sidebar-nav-item .material-symbols-outlined {
                font-size: 1.4rem;
                margin-right: 0.6rem;
            }
        }

        @media (max-width: 640px) {
            #app {
                flex-direction: column; /* Stack sidebar and main content */
            }
            #sidebar {
                width: 100%;
                height: auto; /* Allow sidebar to collapse vertically */
                max-height: 200px; /* Limit height on small screens */
                overflow-y: auto;
                border-right: none;
                border-bottom: 1px solid var(--border-color);
            }
            .user-profile-section {
                flex-direction: row;
                justify-content: center;
                gap: 1rem;
                margin: 0.5rem;
                padding: 1rem;
            }
            .user-profile-img {
                width: 60px;
                height: 60px;
                margin-bottom: 0;
            }
            .welcome-text, .user-position {
                text-align: left;
            }
            .divider {
                display: none; /* Hide divider on small screens */
            }
            .sidebar-nav-item {
                margin: 0.2rem 0.5rem;
                width: calc(100% - 1rem);
            }
            .logout-container {
                margin-top: 0;
                padding: 0.5rem;
                border-top: none;
            }
            .logout-container button {
                padding: 0.6rem 1rem;
            }
            #main-content {
                padding: 1rem 0.75rem;
            }
            .login-card {
                padding: 1.5rem;
            }
        }
    </style>
</head>
<body class="antialiased">
    <div id="app" class="flex-grow">
        <section id="login-section" class="flex flex-col items-center justify-center h-screen bg-primary-bg">
            <div class="login-card">
                <h2 class="text-center text-accent-blue text-2xl font-bold mb-4">Employee Portal Login</h2>
                <p class="text-center text-text-color mb-6">Enter your credentials to access the dashboard.</p>
                <form id="login-form" class="space-y-4">
                    <div>
                        <label for="username" class="block text-sm font-medium text-text-color mb-1">Username:</label>
                        <input type="text" id="username" name="username" placeholder="Enter your username" class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                    </div>
                    <div>
                        <label for="password" class="block text-sm font-medium text-text-color mb-1">Password:</label>
                        <input type="password" id="password" name="password" placeholder="Enter your password" class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                    </div>
                    <button type="submit" class="w-full bg-accent-blue text-white py-2 rounded-lg font-semibold hover:bg-blue-600 transition duration-200">Login</button>
                </form>
                <div id="login-message" class="notification mt-4"></div>
            </div>
        </section>

        <section id="dashboard-section" class="hidden flex-grow">
            <aside id="sidebar" class="bg-secondary-bg w-72 flex-shrink-0 p-4 shadow-lg flex flex-col overflow-y-auto">
                <div class="user-profile-section">
                    <img id="profile-img" src="" alt="Profile" class="user-profile-img">
                    <div id="welcome-text" class="welcome-text"></div>
                    <div id="user-position" class="user-position"></div>
                </div>
                <div class="divider"></div>
                <nav id="sidebar-nav" class="flex-grow">
                    </nav>
                <div class="logout-container">
                    <button id="logout-btn" class="w-full bg-red-600 text-white py-2 rounded-lg font-semibold hover:bg-red-700 transition duration-200">
                        <span class="material-symbols-outlined">logout</span> Logout
                    </button>
                </div>
            </aside>

            <main id="main-content" class="flex-grow p-6 overflow-y-auto">
                <div id="main-notification" class="notification"></div>
                </main>
        </section>
    </div>

    <script>
        // --- Constants and Global Variables ---
        const USERS = {
            "Geetali": { "password": "password", "role": "employee", "position": "Software Engineer", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=GE" },
            "Nilesh": { "password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=NI" },
            "Vishal": { "password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=VI" },
            "Santosh": { "password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=SA" },
            "Deepak": { "password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=DE" },
            "Rahul": { "password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=RA" },
            "admin": { "password": "password", "role": "admin", "position": "System Administrator", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=AD" }
        };

        const LOCAL_STORAGE_PREFIX = "employee_portal_";
        const TARGET_TIMEZONE = "Asia/Kolkata"; // Used for display, actual JS dates are UTC-based

        // DOM Elements
        const loginSection = document.getElementById('login-section');
        const dashboardSection = document.getElementById('dashboard-section');
        const loginForm = document.getElementById('login-form');
        const loginMessage = document.getElementById('login-message');
        const logoutBtn = document.getElementById('logout-btn');
        const sidebarNav = document.getElementById('sidebar-nav');
        const mainContent = document.getElementById('main-content');
        const mainNotification = document.getElementById('main-notification');
        const profileImg = document.getElementById('profile-img');
        const welcomeText = document.getElementById('welcome-text');
        const userPosition = document.getElementById('user-position');

        let currentUser = null;
        let currentRole = null;
        let activePage = 'Attendance'; // Default page after login

        // --- Utility Functions ---

        function getLocalStorageKey(key) {
            return `${LOCAL_STORAGE_PREFIX}${key}`;
        }

        function saveData(key, data) {
            try {
                localStorage.setItem(getLocalStorageKey(key), JSON.stringify(data));
            } catch (e) {
                console.error("Error saving data to localStorage:", e);
                displayMessage("Error saving data. Storage might be full.", "error");
            }
        }

        function loadData(key, defaultValue = []) {
            try {
                const data = localStorage.getItem(getLocalStorageKey(key));
                return data ? JSON.parse(data) : defaultValue;
            } catch (e) {
                console.error("Error loading data from localStorage:", e);
                displayMessage("Error loading data. Data might be corrupted.", "error");
                return defaultValue;
            }
        }

        function getTimestamp(date = new Date()) {
            const options = {
                year: 'numeric', month: '2-digit', day: '2-digit',
                hour: '2-digit', minute: '2-digit', second: '2-digit',
                hour12: false, timeZone: TARGET_TIMEZONE
            };
            return new Intl.DateTimeFormat('en-CA', options).format(date).replace(/,/, ''); // Format YYYY-MM-DD HH:MM:SS
        }

        function getQuarter(year, month) {
            if (month >= 1 && month <= 3) return `${year}-Q1`;
            if (month >= 4 && month <= 6) return `${year}-Q2`;
            if (month >= 7 && month <= 9) return `${year}-Q3`;
            if (month >= 10 && month <= 12) return `${year}-Q4`;
            return null;
        }

        function displayMessage(message, type = "info", targetElement = mainNotification) {
            targetElement.textContent = message;
            targetElement.className = `notification show ${type}`;
            setTimeout(() => {
                targetElement.classList.remove('show');
            }, 5000); // Hide after 5 seconds
        }

        // --- Authentication ---

        function login(username, password) {
            if (USERS[username] && USERS[username].password === password) {
                currentUser = username;
                currentRole = USERS[username].role;
                saveData("loggedInUser", { username: currentUser, role: currentRole });
                displayMessage("Login successful! Welcome.", "success", loginMessage);
                initDashboard();
            } else {
                displayMessage("Invalid username or password. Please try again.", "error", loginMessage);
            }
        }

        function logout() {
            localStorage.removeItem(getLocalStorageKey("loggedInUser"));
            currentUser = null;
            currentRole = null;
            loginSection.classList.remove('hidden');
            dashboardSection.classList.add('hidden');
            displayMessage("You have been logged out.", "info", loginMessage);
            // Clear main content to prevent stale data
            mainContent.innerHTML = ''; 
        }

        // --- Dashboard Initialization & Navigation ---

        function initDashboard() {
            const loggedInUser = loadData("loggedInUser", null);
            if (loggedInUser) {
                currentUser = loggedInUser.username;
                currentRole = loggedInUser.role;
                
                // Update profile section
                profileImg.src = USERS[currentUser].profile_photo;
                welcomeText.textContent = `Welcome, ${currentUser}!`;
                userPosition.textContent = USERS[currentUser].position;

                loginSection.classList.add('hidden');
                dashboardSection.classList.remove('hidden');
                renderSidebar();
                navigateTo(activePage); // Load the default active page
            } else {
                loginSection.classList.remove('hidden');
                dashboardSection.classList.add('hidden');
            }
        }

        function renderSidebar() {
            sidebarNav.innerHTML = ''; // Clear existing items

            const navItemsEmployee = [
                { name: "Attendance", icon: "event_available" },
                { name: "Upload Activity Photo", icon: "upload_file" },
                { name: "Claim Allowance", icon: "payments" },
                { name: "Sales Goal Tracker", icon: "track_changes" },
                { name: "Payment Goal Tracker", icon: "paid" },
                { name: "Activity Log", icon: "list_alt" },
            ];
            const navItemsAdmin = navItemsEmployee; // For this app, admin has same pages

            const navItems = currentRole === "admin" ? navItemsAdmin : navItemsEmployee;

            navItems.forEach(item => {
                const navDiv = document.createElement('div');
                navDiv.className = `sidebar-nav-item ${activePage === item.name ? 'active' : ''}`;
                navDiv.innerHTML = `<span class="material-symbols-outlined">${item.icon}</span> ${item.name}`;
                navDiv.dataset.page = item.name; // Store page name in data attribute

                navDiv.addEventListener('click', () => navigateTo(item.name));
                sidebarNav.appendChild(navDiv);
            });
        }

        function navigateTo(pageName) {
            activePage = pageName;
            renderSidebar(); // Re-render sidebar to update active state
            renderPageContent(pageName);
        }

        // --- Page Content Rendering Functions ---

        function renderPageContent(pageName) {
            mainContent.innerHTML = ''; // Clear previous content
            mainContent.scrollTop = 0; // Scroll to top

            let pageHtml = '';
            switch (pageName) {
                case "Attendance":
                    pageHtml = `
                        <div class="card">
                            <h3 class="text-accent-blue text-xl font-bold mb-4">🕒 Digital Attendance</h3>
                            <p class="text-info mb-4">📍 Location services are currently disabled for attendance. Photos for specific activities can be uploaded from the 'Upload Activity Photo' section.</p>
                            <div class="flex space-x-4 mt-6">
                                <button id="check-in-btn" class="flex-1 bg-accent-blue hover:bg-blue-600 text-white py-2 rounded-lg font-semibold">✅ Check In</button>
                                <button id="check-out-btn" class="flex-1 bg-accent-blue hover:bg-blue-600 text-white py-2 rounded-lg font-semibold">🚪 Check Out</button>
                            </div>
                        </div>
                        <div class="card">
                            <h4 class="text-accent-blue text-lg font-bold mb-4">Attendance History</h4>
                            <div id="attendance-history-table"></div>
                        </div>
                    `;
                    mainContent.innerHTML = pageHtml;
                    document.getElementById('check-in-btn').addEventListener('click', () => processAttendance("Check-In"));
                    document.getElementById('check-out-btn').addEventListener('click', () => processAttendance("Check-Out"));
                    renderAttendanceHistoryTable();
                    break;

                case "Upload Activity Photo":
                    pageHtml = `
                        <div class="card">
                            <h3 class="text-accent-blue text-xl font-bold mb-4">📸 Upload Field Activity Photo</h3>
                            <form id="activity-photo-form" class="space-y-4">
                                <div>
                                    <label for="activity-description" class="block text-sm font-medium text-text-color mb-1">Brief description of activity/visit:</label>
                                    <textarea id="activity-description" name="activity-description" rows="3" placeholder="Please provide a clear description..." class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue"></textarea>
                                </div>
                                <div class="flex flex-col items-center">
                                    <label class="block text-sm font-medium text-text-color mb-2">Take a picture of your activity/visit:</label>
                                    <video id="camera-feed" class="rounded-lg border border-border-color mb-2" autoplay></video>
                                    <canvas id="camera-canvas" class="hidden"></canvas>
                                    <button type="button" id="take-photo-btn" class="bg-gray-700 text-white py-2 px-4 rounded-lg font-semibold hover:bg-gray-600 transition duration-200">Take Photo</button>
                                    <img id="camera-preview" class="hidden mt-4" alt="Captured Photo">
                                </div>
                                <button type="submit" class="w-full bg-accent-blue text-white py-2 rounded-lg font-semibold hover:bg-blue-600 transition duration-200">⬆️ Upload Photo and Log Activity</button>
                            </form>
                        </div>
                    `;
                    mainContent.innerHTML = pageHtml;
                    initCamera();
                    document.getElementById('activity-photo-form').addEventListener('submit', processActivityPhoto);
                    break;

                case "Claim Allowance":
                    pageHtml = `
                        <div class="card">
                            <h3 class="text-accent-blue text-xl font-bold mb-4">💼 Claim Allowance</h3>
                            <form id="allowance-form" class="space-y-4">
                                <div>
                                    <label class="block text-sm font-medium text-text-color mb-1">Allowance Type:</label>
                                    <div class="flex flex-wrap gap-4">
                                        <label class="inline-flex items-center"><input type="radio" name="allowance-type" value="Travel" class="form-radio text-accent-blue"> <span class="ml-2">Travel</span></label>
                                        <label class="inline-flex items-center"><input type="radio" name="allowance-type" value="Dinner" class="form-radio text-accent-blue"> <span class="ml-2">Dinner</span></label>
                                        <label class="inline-flex items-center"><input type="radio" name="allowance-type" value="Medical" class="form-radio text-accent-blue"> <span class="ml-2">Medical</span></label>
                                        <label class="inline-flex items-center"><input type="radio" name="allowance-type" value="Internet" class="form-radio text-accent-blue"> <span class="ml-2">Internet</span></label>
                                        <label class="inline-flex items-center"><input type="radio" name="allowance-type" value="Other" class="form-radio text-accent-blue"> <span class="ml-2">Other</span></label>
                                    </div>
                                </div>
                                <div>
                                    <label for="allowance-amount" class="block text-sm font-medium text-text-color mb-1">Enter Amount (INR):</label>
                                    <input type="number" id="allowance-amount" name="allowance-amount" min="0.01" step="10.0" placeholder="e.g., 500.00" class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                                </div>
                                <div>
                                    <label for="allowance-reason" class="block text-sm font-medium text-text-color mb-1">Reason for Allowance:</label>
                                    <textarea id="allowance-reason" name="allowance-reason" rows="3" placeholder="Please provide a clear justification..." class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue"></textarea>
                                </div>
                                <button type="submit" class="w-full bg-accent-blue text-white py-2 rounded-lg font-semibold hover:bg-blue-600 transition duration-200">Submit Allowance Request</button>
                            </form>
                        </div>
                        <div class="card">
                            <h4 class="text-accent-blue text-lg font-bold mb-4">Allowance History</h4>
                            <div id="allowance-history-table"></div>
                        </div>
                    `;
                    mainContent.innerHTML = pageHtml;
                    document.getElementById('allowance-form').addEventListener('submit', processAllowance);
                    renderAllowanceHistoryTable();
                    break;

                case "Sales Goal Tracker":
                    renderGoalTrackerPage("Sales");
                    break;

                case "Payment Goal Tracker":
                    renderGoalTrackerPage("Payment");
                    break;

                case "Activity Log":
                    pageHtml = `
                        <div class="card">
                            <h3 class="text-accent-blue text-xl font-bold mb-4">📋 Activity Log</h3>
                            <div id="activity-log-filters" class="mb-4">
                                </div>
                            <div id="activity-log-list"></div>
                        </div>
                    `;
                    mainContent.innerHTML = pageHtml;
                    renderActivityLog();
                    break;

                default:
                    mainContent.innerHTML = `<div class="card"><h3 class="text-accent-blue text-xl font-bold">Welcome!</h3><p>Select a page from the sidebar.</p></div>`;
                    break;
            }
        }

        // --- Page Logic Functions ---

        // Attendance
        function processAttendance(type) {
            const timestamp = getTimestamp();
            const attendanceData = loadData("attendance", []);
            attendanceData.push({
                username: currentUser,
                type: type,
                timestamp: timestamp,
                latitude: "N/A", // Location services not implemented
                longitude: "N/A"
            });
            saveData("attendance", attendanceData);
            displayMessage(`${type} recorded at ${timestamp}.`, "success");
            renderAttendanceHistoryTable();
        }

        function renderAttendanceHistoryTable() {
            const attendanceData = loadData("attendance", []);
            const filteredData = attendanceData.filter(entry => entry.username === currentUser);
            
            let tableHtml = `<table class="min-w-full"><thead><tr><th>Type</th><th>Timestamp</th><th>Location</th></tr></thead><tbody>`;
            if (filteredData.length === 0) {
                tableHtml += `<tr><td colspan="3" class="text-center text-gray-500">No attendance records found.</td></tr>`;
            } else {
                filteredData.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)); // Sort by latest
                filteredData.forEach(entry => {
                    tableHtml += `
                        <tr>
                            <td>${entry.type}</td>
                            <td>${entry.timestamp}</td>
                            <td>${entry.latitude}, ${entry.longitude}</td>
                        </tr>
                    `;
                });
            }
            tableHtml += `</tbody></table>`;
            document.getElementById('attendance-history-table').innerHTML = tableHtml;
        }

        // Activity Photo
        let cameraStream = null;
        let photoDataURL = null;

        async function initCamera() {
            const video = document.getElementById('camera-feed');
            const takePhotoBtn = document.getElementById('take-photo-btn');
            const previewImg = document.getElementById('camera-preview');
            const canvas = document.getElementById('camera-canvas');
            const ctx = canvas.getContext('2d');

            // Stop any existing stream
            if (cameraStream) {
                cameraStream.getTracks().forEach(track => track.stop());
            }

            try {
                cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = cameraStream;
                video.classList.remove('hidden');
                takePhotoBtn.classList.remove('hidden');
                previewImg.classList.add('hidden'); // Hide preview until photo is taken
                photoDataURL = null; // Reset photo data
            } catch (err) {
                console.error("Error accessing camera: ", err);
                displayMessage("Could not access camera. Please ensure it's connected and permissions are granted.", "error");
                video.classList.add('hidden');
                takePhotoBtn.classList.add('hidden');
            }

            takePhotoBtn.onclick = () => {
                if (!video.srcObject) {
                    displayMessage("Camera not active.", "warning");
                    return;
                }
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                photoDataURL = canvas.toDataURL('image/jpeg', 0.8); // Get Base64 image
                previewImg.src = photoDataURL;
                previewImg.classList.remove('hidden');
                video.classList.add('hidden'); // Hide video feed after photo
                takePhotoBtn.textContent = "Retake Photo"; // Change button text
            };
        }

        function stopCamera() {
            if (cameraStream) {
                cameraStream.getTracks().forEach(track => track.stop());
                cameraStream = null;
            }
        }

        function processActivityPhoto(event) {
            event.preventDefault();
            const description = document.getElementById('activity-description').value.trim();

            if (!photoDataURL) {
                displayMessage("Please take a picture before submitting.", "warning");
                return;
            }
            if (!description) {
                displayMessage("Please provide a description for the activity.", "warning");
                return;
            }

            const timestamp = getTimestamp();
            const activityLog = loadData("activityLog", []);
            activityLog.push({
                username: currentUser,
                timestamp: timestamp,
                description: description,
                image: photoDataURL, // Store Base64 image
                latitude: "N/A",
                longitude: "N/A"
            });
            saveData("activityLog", activityLog);
            displayMessage("Activity photo and log uploaded!", "success");

            // Reset form and camera
            document.getElementById('activity-photo-form').reset();
            document.getElementById('camera-preview').classList.add('hidden');
            document.getElementById('camera-feed').classList.remove('hidden');
            document.getElementById('take-photo-btn').textContent = "Take Photo";
            photoDataURL = null;
            // No need to stop camera, it's already hidden, user might want to take another
        }

        // Allowance
        function processAllowance(event) {
            event.preventDefault();
            const type = document.querySelector('input[name="allowance-type"]:checked')?.value;
            const amount = parseFloat(document.getElementById('allowance-amount').value);
            const reason = document.getElementById('allowance-reason').value.trim();

            if (!type || isNaN(amount) || amount <= 0 || !reason) {
                displayMessage("Please complete all fields with valid values.", "warning");
                return;
            }

            const allowanceData = loadData("allowances", []);
            allowanceData.push({
                username: currentUser,
                type: type,
                amount: amount,
                reason: reason,
                date: getTimestamp().split(' ')[0] // Just date part
            });
            saveData("allowances", allowanceData);
            displayMessage(`Allowance for ₹${amount.toFixed(2)} submitted.`, "success");
            document.getElementById('allowance-form').reset();
            renderAllowanceHistoryTable();
        }

        function renderAllowanceHistoryTable() {
            const allowanceData = loadData("allowances", []);
            const filteredData = allowanceData.filter(entry => entry.username === currentUser);

            let tableHtml = `<table class="min-w-full"><thead><tr><th>Date</th><th>Type</th><th>Amount</th><th>Reason</th></tr></thead><tbody>`;
            if (filteredData.length === 0) {
                tableHtml += `<tr><td colspan="4" class="text-center text-gray-500">No allowance requests found.</td></tr>`;
            } else {
                filteredData.sort((a, b) => new Date(b.date) - new Date(a.date));
                filteredData.forEach(entry => {
                    tableHtml += `
                        <tr>
                            <td>${entry.date}</td>
                            <td>${entry.type}</td>
                            <td>₹${entry.amount.toFixed(2)}</td>
                            <td>${entry.reason}</td>
                        </tr>
                    `;
                });
            }
            tableHtml += `</tbody></table>`;
            document.getElementById('allowance-history-table').innerHTML = tableHtml;
        }

        // Goal Tracker (Sales & Payment)
        function renderGoalTrackerPage(goalType) {
            const goalsKey = goalType === "Sales" ? "salesGoals" : "paymentGoals";
            const goalsData = loadData(goalsKey, []);
            const currentYear = new Date().getFullYear();
            const currentMonth = new Date().getMonth() + 1; // 1-indexed
            const currentQuarter = getQuarter(currentYear, currentMonth);
            const statusOptions = ["Not Started", "In Progress", "Achieved", "On Hold", "Cancelled"];

            let pageHtml = `<div class="card"><h3 class="text-accent-blue text-xl font-bold mb-4">🎯 ${goalType} Goal Tracker (${currentYear} - Quarterly)</h3>`;

            if (currentRole === "admin") {
                pageHtml += `
                    <h4 class="text-accent-blue text-lg font-bold mb-4">Admin: Manage & Track Employee ${goalType} Goals</h4>
                    <div class="mb-4">
                        <button id="view-team-progress-btn" class="mr-4 px-4 py-2 rounded-lg font-semibold">View Team Progress</button>
                        <button id="set-edit-goal-btn" class="px-4 py-2 rounded-lg font-semibold">Set/Edit Goal</button>
                    </div>
                    <div id="admin-goal-content"></div>
                `;
            } else {
                pageHtml += `
                    <h4 class="text-accent-blue text-lg font-bold mb-4">My ${goalType} Goals for ${currentYear}</h4>
                    <div id="my-goal-content"></div>
                `;
            }
            pageHtml += `</div>`;
            mainContent.innerHTML = pageHtml;

            if (currentRole === "admin") {
                const viewTeamBtn = document.getElementById('view-team-progress-btn');
                const setEditBtn = document.getElementById('set-edit-goal-btn');
                const adminGoalContent = document.getElementById('admin-goal-content');

                let currentAdminAction = "view"; // Default to view team progress

                const updateAdminGoalContent = () => {
                    if (currentAdminAction === "view") {
                        viewTeamBtn.classList.add('bg-accent-blue', 'text-white');
                        setEditBtn.classList.remove('bg-accent-blue', 'text-white');
                        renderAdminViewTeamProgress(goalsKey, adminGoalContent, currentQuarter, goalType);
                    } else {
                        setEditBtn.classList.add('bg-accent-blue', 'text-white');
                        viewTeamBtn.classList.remove('bg-accent-blue', 'text-white');
                        renderAdminSetEditGoal(goalsKey, adminGoalContent, currentQuarter, statusOptions, goalType);
                    }
                };

                viewTeamBtn.addEventListener('click', () => { currentAdminAction = "view"; updateAdminGoalContent(); });
                setEditBtn.addEventListener('click', () => { currentAdminAction = "set-edit"; updateAdminGoalContent(); });
                
                updateAdminGoalContent(); // Initial render
            } else {
                renderEmployeeGoalView(goalsKey, document.getElementById('my-goal-content'), currentQuarter, statusOptions, goalType);
            }
        }

        function renderAdminViewTeamProgress(goalsKey, container, currentQuarter, goalType) {
            container.innerHTML = `<h5 class="text-accent-blue text-md font-bold mb-4">Team ${goalType} Goal Progress for ${currentQuarter}</h5>`;
            const quarterlyGoals = loadData(goalsKey, []).filter(g => g.monthYear === currentQuarter);

            if (quarterlyGoals.length === 0) {
                container.innerHTML += `<p class="text-gray-500">No ${goalType.toLowerCase()} goals set for ${currentQuarter} yet.</p>`;
                return;
            }

            const teamSummary = {};
            quarterlyGoals.forEach(goal => {
                if (!teamSummary[goal.username]) {
                    teamSummary[goal.username] = { target: 0, achieved: 0 };
                }
                teamSummary[goal.username].target += parseFloat(goal.targetAmount || 0);
                teamSummary[goal.username].achieved += parseFloat(goal.achievedAmount || 0);
            });

            let summaryHtml = `<h6 class="text-text-color font-semibold mb-2">Individual Quarterly Progress:</h6>`;
            Object.keys(teamSummary).forEach(username => {
                const data = teamSummary[username];
                const progress = data.target > 0 ? (data.achieved / data.target) * 100 : 0;
                summaryHtml += `
                    <div class="mb-4 p-3 bg-primary-bg rounded-lg border border-border-color">
                        <p class="font-bold">${username}</p>
                        <div class="w-full bg-border-color rounded-full h-2.5 mb-1">
                            <div class="bg-success-color h-2.5 rounded-full" style="width: ${Math.min(progress, 100)}%"></div>
                        </div>
                        <p class="text-sm text-gray-400">Target: ₹${data.target.toLocaleString()} | Achieved: ₹${data.achieved.toLocaleString()}</p>
                    </div>
                `;
            });
            container.innerHTML += summaryHtml;

            // Detailed goals table
            let tableHtml = `<h5 class="text-accent-blue text-md font-bold mt-6 mb-4">Detailed Quarterly ${goalType} Goals:</h5>`;
            tableHtml += `<table class="min-w-full"><thead><tr><th>Employee</th><th>Description</th><th>Target</th><th>Achieved</th><th>Status</th></tr></thead><tbody>`;
            quarterlyGoals.sort((a, b) => a.username.localeCompare(b.username));
            quarterlyGoals.forEach(goal => {
                tableHtml += `
                    <tr>
                        <td>${goal.username}</td>
                        <td>${goal.goalDescription}</td>
                        <td>₹${parseFloat(goal.targetAmount || 0).toLocaleString()}</td>
                        <td>₹${parseFloat(goal.achievedAmount || 0).toLocaleString()}</td>
                        <td>${goal.status}</td>
                    </tr>
                `;
            });
            tableHtml += `</tbody></table>`;
            container.innerHTML += tableHtml;
        }

        function renderAdminSetEditGoal(goalsKey, container, currentQuarter, statusOptions, goalType) {
            const allUsers = Object.keys(USERS).filter(u => USERS[u].role === "employee");
            container.innerHTML = `
                <h5 class="text-accent-blue text-md font-bold mb-4">Set or Update Quarterly ${goalType} Goals for ${currentQuarter}</h5>
                <form id="set-goal-form" class="space-y-4">
                    <div>
                        <label for="target-user" class="block text-sm font-medium text-text-color mb-1">Select Employee:</label>
                        <select id="target-user" name="target-user" class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                            ${allUsers.map(u => `<option value="${u}">${u}</option>`).join('')}
                        </select>
                    </div>
                    <div>
                        <label for="goal-description" class="block text-sm font-medium text-text-color mb-1">Goal Description:</label>
                        <textarea id="goal-description" name="goal-description" rows="2" placeholder="e.g., Achieve X sales, Y client meetings" class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue"></textarea>
                    </div>
                    <div>
                        <label for="target-amount" class="block text-sm font-medium text-text-color mb-1">Target Amount (INR):</label>
                        <input type="number" id="target-amount" name="target-amount" min="0.0" step="1000.0" value="0.00" class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                    </div>
                    <div>
                        <label for="achieved-amount" class="block text-sm font-medium text-text-color mb-1">Achieved Amount (INR):</label>
                        <input type="number" id="achieved-amount" name="achieved-amount" min="0.0" step="100.0" value="0.00" class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                    </div>
                    <div>
                        <label for="goal-status" class="block text-sm font-medium text-text-color mb-1">Status:</label>
                        <select id="goal-status" name="goal-status" class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                            ${statusOptions.map(s => `<option value="${s}">${s}</option>`).join('')}
                        </select>
                    </div>
                    <button type="submit" class="w-full bg-accent-blue text-white py-2 rounded-lg font-semibold hover:bg-blue-600 transition duration-200">💾 Save ${goalType} Goal</button>
                </form>
            `;

            const form = document.getElementById('set-goal-form');
            const targetUserSelect = document.getElementById('target-user');
            const goalDescriptionInput = document.getElementById('goal-description');
            const targetAmountInput = document.getElementById('target-amount');
            const achievedAmountInput = document.getElementById('achieved-amount');
            const goalStatusSelect = document.getElementById('goal-status');

            // Populate form if a goal is selected (for editing)
            const populateFormForEdit = () => {
                const selectedUser = targetUserSelect.value;
                const selectedDesc = goalDescriptionInput.value; // This will be empty on initial load

                const goals = loadData(goalsKey, []);
                const existingGoal = goals.find(g => 
                    g.username === selectedUser && 
                    g.monthYear === currentQuarter && 
                    g.goalDescription === selectedDesc
                );

                if (existingGoal) {
                    targetAmountInput.value = parseFloat(existingGoal.targetAmount || 0).toFixed(2);
                    achievedAmountInput.value = parseFloat(existingGoal.achievedAmount || 0).toFixed(2);
                    goalStatusSelect.value = existingGoal.status;
                } else {
                    // Reset if no matching goal found for current description
                    targetAmountInput.value = "0.00";
                    achievedAmountInput.value = "0.00";
                    goalStatusSelect.value = "Not Started";
                }
            };
            
            // Event listener for description change (to load existing goal)
            goalDescriptionInput.addEventListener('change', populateFormForEdit);
            targetUserSelect.addEventListener('change', populateFormForEdit); // Also update if user changes

            form.addEventListener('submit', (event) => {
                event.preventDefault();
                const username = targetUserSelect.value;
                const description = goalDescriptionInput.value.trim();
                const target = parseFloat(targetAmountInput.value);
                const achieved = parseFloat(achievedAmountInput.value);
                const status = goalStatusSelect.value;

                if (!username || !description || isNaN(target) || target < 0 || isNaN(achieved) || achieved < 0 || !status) {
                    displayMessage("Please fill all goal fields with valid values.", "warning", mainNotification);
                    return;
                }

                let goals = loadData(goalsKey, []);
                const existingIndex = goals.findIndex(g => 
                    g.username === username && 
                    g.monthYear === currentQuarter && 
                    g.goalDescription === description
                );

                const newGoal = {
                    username: username,
                    monthYear: currentQuarter,
                    goalDescription: description,
                    targetAmount: target,
                    achievedAmount: achieved,
                    status: status
                };

                if (existingIndex > -1) {
                    goals[existingIndex] = newGoal;
                    displayMessage(`${goalType} goal for ${username} updated for ${currentQuarter}.`, "info", mainNotification);
                } else {
                    goals.push(newGoal);
                    displayMessage(`New ${goalType} goal added for ${username} for ${currentQuarter}.`, "success", mainNotification);
                }
                saveData(goalsKey, goals);
                form.reset(); // Clear form after submission
                populateFormForEdit(); // Reset form values after submission
            });
        }

        function renderEmployeeGoalView(goalsKey, container, currentQuarter, statusOptions, goalType) {
            const myGoals = loadData(goalsKey, []).filter(g => g.username === currentUser);

            if (myGoals.length === 0) {
                container.innerHTML = `<p class="text-gray-500">You currently have no ${goalType.toLowerCase()} goals assigned.</p>`;
                return;
            }

            const totalTarget = myGoals.reduce((sum, g) => sum + parseFloat(g.targetAmount || 0), 0);
            const totalAchieved = myGoals.reduce((sum, g) => sum + parseFloat(g.achievedAmount || 0), 0);
            const overallProgress = totalTarget > 0 ? (totalAchieved / totalTarget) * 100 : 0;

            container.innerHTML = `
                <h5 class="text-accent-blue text-md font-bold mb-4">Overall Progress:</h5>
                <div class="flex items-center mb-4 p-3 bg-primary-bg rounded-lg border border-border-color">
                    <div class="w-full bg-border-color rounded-full h-3.5 mr-4">
                        <div class="bg-success-color h-3.5 rounded-full" style="width: ${Math.min(overallProgress, 100)}%"></div>
                    </div>
                    <p class="font-bold text-lg">${overallProgress.toFixed(1)}%</p>
                </div>
                <p class="text-sm text-gray-400 mb-6">Target: ₹${totalTarget.toLocaleString()} | Achieved: ₹${totalAchieved.toLocaleString()}</p>

                <h5 class="text-accent-blue text-md font-bold mb-4">My Quarterly ${goalType} Goals for ${currentQuarter}:</h5>
                <div id="quarterly-goals-table"></div>

                <h5 class="text-accent-blue text-md font-bold mt-6 mb-4">Update Goal Progress:</h5>
                <form id="update-my-goal-form" class="space-y-4">
                    <div>
                        <label for="selected-goal-desc" class="block text-sm font-medium text-text-color mb-1">Select Goal to Update:</label>
                        <select id="selected-goal-desc" name="selected-goal-desc" class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                            ${myGoals.filter(g => g.monthYear === currentQuarter).map(g => `<option value="${g.goalDescription}">${g.goalDescription}</option>`).join('')}
                        </select>
                    </div>
                    <div>
                        <label for="updated-achieved-amount" class="block text-sm font-medium text-text-color mb-1">New Achieved Amount (INR):</label>
                        <input type="number" id="updated-achieved-amount" name="updated-achieved-amount" min="0.0" step="100.0" class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                    </div>
                    <div>
                        <label for="updated-status" class="block text-sm font-medium text-text-color mb-1">New Status:</label>
                        <select id="updated-status" name="updated-status" class="w-full bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                            ${statusOptions.map(s => `<option value="${s}">${s}</option>`).join('')}
                        </select>
                    </div>
                    <button type="submit" class="w-full bg-accent-blue text-white py-2 rounded-lg font-semibold hover:bg-blue-600 transition duration-200">🔄 Update My ${goalType} Goal</button>
                </form>
            `;

            const quarterlyGoalsTableDiv = document.getElementById('quarterly-goals-table');
            const updateForm = document.getElementById('update-my-goal-form');
            const selectedGoalDescSelect = document.getElementById('selected-goal-desc');
            const updatedAchievedAmountInput = document.getElementById('updated-achieved-amount');
            const updatedStatusSelect = document.getElementById('updated-status');

            const renderQuarterlyGoalsTable = () => {
                const quarterlyMyGoals = myGoals.filter(g => g.monthYear === currentQuarter);
                let tableHtml = `<table class="min-w-full"><thead><tr><th>Description</th><th>Target</th><th>Achieved</th><th>Status</th></tr></thead><tbody>`;
                if (quarterlyMyGoals.length === 0) {
                    tableHtml += `<tr><td colspan="4" class="text-center text-gray-500">No ${goalType.toLowerCase()} goals assigned for this quarter.</td></tr>`;
                } else {
                    quarterlyMyGoals.forEach(goal => {
                        tableHtml += `
                            <tr>
                                <td>${goal.goalDescription}</td>
                                <td>₹${parseFloat(goal.targetAmount || 0).toLocaleString()}</td>
                                <td>₹${parseFloat(goal.achievedAmount || 0).toLocaleString()}</td>
                                <td>${goal.status}</td>
                            </tr>
                        `;
                    });
                }
                tableHtml += `</tbody></table>`;
                quarterlyGoalsTableDiv.innerHTML = tableHtml;
            };

            const populateUpdateForm = () => {
                const selectedDesc = selectedGoalDescSelect.value;
                const goalToUpdate = myGoals.find(g => g.goalDescription === selectedDesc && g.monthYear === currentQuarter);
                if (goalToUpdate) {
                    updatedAchievedAmountInput.value = parseFloat(goalToUpdate.achievedAmount || 0).toFixed(2);
                    updatedStatusSelect.value = goalToUpdate.status;
                }
            };

            selectedGoalDescSelect.addEventListener('change', populateUpdateForm);
            updateForm.addEventListener('submit', (event) => {
                event.preventDefault();
                const selectedDesc = selectedGoalDescSelect.value;
                const newAchievedAmount = parseFloat(updatedAchievedAmountInput.value);
                const newStatus = updatedStatusSelect.value;

                if (!selectedDesc || isNaN(newAchievedAmount) || newAchievedAmount < 0 || !newStatus) {
                    displayMessage("Please select a goal and provide valid update values.", "warning", mainNotification);
                    return;
                }

                let goals = loadData(goalsKey, []);
                const goalIndex = goals.findIndex(g => 
                    g.username === currentUser && 
                    g.monthYear === currentQuarter && 
                    g.goalDescription === selectedDesc
                );

                if (goalIndex > -1) {
                    goals[goalIndex].achievedAmount = newAchievedAmount;
                    goals[goalIndex].status = newStatus;
                    saveData(goalsKey, goals);
                    displayMessage(`${goalType} goal "${selectedDesc}" updated successfully.`, "success", mainNotification);
                    renderEmployeeGoalView(goalsKey, container, currentQuarter, statusOptions, goalType); // Re-render page
                } else {
                    displayMessage("Selected goal not found for update.", "error", mainNotification);
                }
            });

            renderQuarterlyGoalsTable();
            populateUpdateForm(); // Initial population
        }

        // Activity Log
        function renderActivityLog() {
            const activityLog = loadData("activityLog", []);
            let filteredActivities = activityLog;

            const activityLogFiltersDiv = document.getElementById('activity-log-filters');
            const activityLogListDiv = document.getElementById('activity-log-list');

            if (currentRole === "admin") {
                const allUsers = ["All", ...Object.keys(USERS).filter(u => USERS[u].role === "employee")];
                activityLogFiltersDiv.innerHTML = `
                    <div class="flex flex-wrap gap-4 items-end">
                        <div>
                            <label for="log-user-filter" class="block text-sm font-medium text-text-color mb-1">Filter by Employee:</label>
                            <select id="log-user-filter" class="w-48 bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                                ${allUsers.map(u => `<option value="${u}">${u}</option>`).join('')}
                            </select>
                        </div>
                        <div>
                            <label for="log-start-date" class="block text-sm font-medium text-text-color mb-1">Start Date:</label>
                            <input type="date" id="log-start-date" class="w-48 bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                        </div>
                        <div>
                            <label for="log-end-date" class="block text-sm font-medium text-text-color mb-1">End Date:</label>
                            <input type="date" id="log-end-date" class="w-48 bg-primary-bg text-text-color border border-border-color rounded-lg px-4 py-2 focus:ring-accent-blue focus:border-accent-blue">
                        </div>
                        <button id="apply-log-filters" class="bg-accent-blue text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-600 transition duration-200">Apply Filters</button>
                    </div>
                `;

                const applyFilters = () => {
                    const selectedUser = document.getElementById('log-user-filter').value;
                    const startDate = document.getElementById('log-start-date').value;
                    const endDate = document.getElementById('log-end-date').value;

                    filteredActivities = activityLog;
                    if (selectedUser !== "All") {
                        filteredActivities = filteredActivities.filter(a => a.username === selectedUser);
                    }
                    if (startDate) {
                        filteredActivities = filteredActivities.filter(a => new Date(a.timestamp.split(' ')[0]) >= new Date(startDate));
                    }
                    if (endDate) {
                        filteredActivities = filteredActivities.filter(a => new Date(a.timestamp.split(' ')[0]) <= new Date(endDate));
                    }
                    displayActivities(filteredActivities);
                };

                document.getElementById('apply-log-filters').addEventListener('click', applyFilters);
                applyFilters(); // Initial filter application
            } else {
                filteredActivities = activityLog.filter(a => a.username === currentUser);
                displayActivities(filteredActivities);
            }

            function displayActivities(activities) {
                activityLogListDiv.innerHTML = ''; // Clear previous list
                if (activities.length === 0) {
                    activityLogListDiv.innerHTML = `<p class="text-gray-500">No activities to display for the selected filters.</p>`;
                    return;
                }
                
                activities.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp)); // Sort by latest

                activities.forEach(activity => {
                    const activityCard = document.createElement('div');
                    activityCard.className = 'card p-4 mb-4';
                    activityCard.innerHTML = `
                        <p class="font-bold">Employee: <span class="text-accent-blue">${activity.username}</span> | Timestamp: ${activity.timestamp}</p>
                        <p class="mt-2 text-text-color">Description: ${activity.description}</p>
                        ${activity.image ? `<img src="${activity.image}" alt="Activity Photo" class="mt-4 rounded-lg max-w-xs w-full border border-border-color">` : '<p class="text-gray-500 mt-4">No photo uploaded.</p>'}
                    `;
                    activityLogListDiv.appendChild(activityCard);
                });
            }
        }


        // --- Event Listeners and Initial App Load ---

        loginForm.addEventListener('submit', (event) => {
            event.preventDefault();
            const username = event.target.username.value.trim();
            const password = event.target.password.value.trim();
            login(username, password);
        });

        logoutBtn.addEventListener('click', logout);

        // Initialize the app on page load
        document.addEventListener('DOMContentLoaded', initDashboard);

        // Stop camera stream when navigating away from photo page or before closing app
        window.addEventListener('beforeunload', stopCamera);
        // Also stop camera when navigating to a different page within the app
        mainContent.addEventListener('DOMNodeRemoved', (event) => {
            if (event.target.id === 'activity-photo-form') { // Check if the activity photo form is being removed
                stopCamera();
            }
        });

    </script>
</body>
</html>
