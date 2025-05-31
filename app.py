import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, session, send_from_directory, redirect, url_for
from functools import wraps

app = Flask(__name__, static_folder='.') # Serve files from current directory
app.secret_key = 'supersecretkey_for_employee_portal_app' # Replace with a strong, random key in production

# --- Data Storage Paths ---
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ATTENDANCE_FILE = os.path.join(DATA_DIR, 'attendance.json')
TASKS_FILE = os.path.join(DATA_DIR, 'tasks.json')
SALES_FILE = os.path.join(DATA_DIR, 'sales.json')
EXPENSES_FILE = os.path.join(DATA_DIR, 'expenses.json')
GOALS_FILE = os.path.join(DATA_DIR, 'goals.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')
CUSTOMERS_FILE = os.path.join(DATA_DIR, 'customers.json')
LEADS_FILE = os.path.join(DATA_DIR, 'leads.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# --- Global variable for USERS_DATA ---
USERS_DATA = {}

# --- Utility Functions for JSON Data Persistence ---

def load_json_data(filepath, default_value=None):
    """Loads JSON data from a file. If file doesn't exist, returns default_value."""
    if not os.path.exists(filepath):
        return default_value if default_value is not None else []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: Could not decode JSON from {filepath}. Returning default value.")
        return default_value if default_value is not None else []
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return default_value if default_value is not None else []

def save_json_data(filepath, data):
    """Saves data to a JSON file."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving {filepath}: {e}")

# --- Dummy Data Initialization ---
def initialize_dummy_data():
    """Initializes dummy data if data files are empty."""
    global USERS_DATA  # Must be first statement in function
    
    # Initialize Users
    default_users = {
        "Geetali": {"password": "password", "role": "employee", "position": "Software Engineer", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=GE", "email": "geetali@example.com"},
        "Nilesh": {"password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=NI", "email": "nilesh@example.com"},
        "Vishal": {"password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=VI", "email": "vishal@example.com"},
        "Santosh": {"password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=SA", "email": "santosh@example.com"},
        "Deepak": {"password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=DE", "email": "deepak@example.com"},
        "Rahul": {"password": "password", "role": "employee", "position": "Sales Executive", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=RA", "email": "rahul@example.com"},
        "admin": {"password": "password", "role": "admin", "position": "System Administrator", "profile_photo": "https://placehold.co/150x150/2c2e30/8ab4f8?text=AD", "email": "admin@example.com"}
    }
    
    USERS_DATA = load_json_data(USERS_FILE, default_value={})
    if not USERS_DATA: # If users.json is empty or doesn't exist
        USERS_DATA = default_users
        save_json_data(USERS_FILE, USERS_DATA)
        print("Initialized default user data.")

    # Initialize other data types if their files are empty
    if not load_json_data(ATTENDANCE_FILE): save_json_data(ATTENDANCE_FILE, [])
    if not load_json_data(TASKS_FILE): save_json_data(TASKS_FILE, [])
    if not load_json_data(SALES_FILE): save_json_data(SALES_FILE, [])
    if not load_json_data(EXPENSES_FILE): save_json_data(EXPENSES_FILE, [])
    if not load_json_data(GOALS_FILE): save_json_data(GOALS_FILE, [])
    if not load_json_data(ORDERS_FILE): save_json_data(ORDERS_FILE, [])
    if not load_json_data(CUSTOMERS_FILE): 
        save_json_data(CUSTOMERS_FILE, [
            {"id": "cust1", "name": "AgriCorp Solutions", "email": "contact@agricorp.com", "phone": "9876543210", "address": "123 Farm Rd, Rural City", "type": "Company", "notes": "Key client for fertilizers.", "addedBy": "admin", "addedDate": "2024-01-15", "createdAt": "2024-01-15 10:00:00"},
            {"id": "cust2", "name": "Priya Sharma", "email": "priya.s@example.com", "phone": "9988776655", "address": "Flat 4B, Green Apartments", "type": "Individual", "notes": "Interested in organic pesticides.", "addedBy": "Nilesh", "addedDate": "2024-02-01", "createdAt": "2024-02-01 11:30:00"},
            {"id": "cust3", "name": "Harvest Innovations", "email": "info@harvestinnov.com", "phone": "9123456789", "address": "789 Tech Park, Metro City", "type": "Company", "notes": "New potential for irrigation systems.", "addedBy": "Vishal", "addedDate": "2024-03-10", "createdAt": "2024-03-10 14:00:00"}
        ])
    if not load_json_data(LEADS_FILE): 
        save_json_data(LEADS_FILE, [
            {"id": "lead1", "name": "Future Farms Ltd.", "email": "sales@futurefarms.in", "phone": "8765432109", "source": "Website Inquiry", "status": "New", "assignedTo": "Nilesh", "notes": "Looking for bulk seeds.", "addedDate": "2024-04-05", "createdAt": "2024-04-05 09:00:00"},
            {"id": "lead2", "name": "Kisan Agro", "email": "kisan.agro@mail.com", "phone": "7654321098", "source": "Referral", "status": "Contacted", "assignedTo": "Vishal", "notes": "Follow-up on NPK liquid fertilizer.", "addedDate": "2024-04-12", "createdAt": "2024-04-12 10:15:00"},
            {"id": "lead3", "name": "Green Earth Co.", "email": "green.earth@co.in", "phone": "6543210987", "source": "Cold Call", "status": "Qualified", "assignedTo": "Nilesh", "notes": "Ready for product demo next week.", "addedDate": "2024-04-20", "createdAt": "2024-04-20 13:45:00"}
        ])

# Call initialization on app startup
with app.app_context():
    initialize_dummy_data()

# --- Authentication Decorator ---
def login_required(f):
    """Decorator to protect routes that require user to be logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({"message": "Unauthorized. Please log in."}), 401
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@app.route('/')
def index():
    """Serves the main HTML file."""
    return send_from_directory('.', 'index.html')

@app.route('/api/login', methods=['POST'])
def login():
    """Handles user login."""
    data = request.get_json()
    username_input = data.get('username')
    password_input = data.get('password')

    # Case-insensitive username lookup
    found_username = next((u for u in USERS_DATA if u.lower() == username_input.lower()), None)

    if found_username and USERS_DATA[found_username]['password'] == password_input:
        session['username'] = found_username
        session['role'] = USERS_DATA[found_username]['role']
        return jsonify({
            "message": "Login successful!",
            "currentUser": found_username,
            "currentRole": USERS_DATA[found_username]['role'],
            "profile_photo": USERS_DATA[found_username]['profile_photo'],
            "position": USERS_DATA[found_username]['position']
        }), 200
    else:
        return jsonify({"message": "Invalid username or password."}), 401

@app.route('/api/register', methods=['POST'])
def register():
    """Handles new user registration."""
    global USERS_DATA  # Must be first statement in function
    
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'employee') # Default role is employee

    if not username or not email or not password:
        return jsonify({"message": "All fields are required."}), 400

    # Check if username or email already exists (case-insensitive for username)
    if any(u.lower() == username.lower() for u in USERS_DATA):
        return jsonify({"message": "Username already exists. Please choose a different one."}), 409
    if any(user_data.get('email') == email for user_data in USERS_DATA.values()):
        return jsonify({"message": "Email already registered. Please use a different one."}), 409

    # Add new user
    USERS_DATA[username] = {
        "password": password,
        "role": role,
        "position": "System Administrator" if role == 'admin' else "Employee",
        "profile_photo": f"https://placehold.co/150x150/2c2e30/8ab4f8?text={username[:2].upper()}",
        "email": email
    }
    save_json_data(USERS_FILE, USERS_DATA)
    return jsonify({"message": "Registration successful! Please login."}), 201

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Handles user logout."""
    session.pop('username', None)
    session.pop('role', None)
    return jsonify({"message": "Logged out successfully!"}), 200

@app.route('/api/current_user', methods=['GET'])
def get_current_user():
    """Returns current user details if logged in."""
    if 'username' in session:
        username = session['username']
        user_info = USERS_DATA.get(username)
        if user_info:
            return jsonify({
                "username": username,
                "role": user_info['role'],
                "position": user_info['position'],
                "profile_photo": user_info['profile_photo']
            }), 200
    return jsonify({"username": None, "role": None}), 200 # Not logged in

@app.route('/api/data/<key>', methods=['GET', 'POST', 'DELETE'])
@login_required
def handle_data(key):
    """
    Generic API endpoint for managing different data types.
    GET: Retrieve data
    POST: Save/Update data (expects full list or object)
    DELETE: Delete an item by ID (expects {'id': 'item_id'})
    """
    global USERS_DATA  # Must be first statement in function if modifying USERS_DATA
    
    filepath_map = {
        'users': USERS_FILE,
        'attendance': ATTENDANCE_FILE,
        'tasks': TASKS_FILE,
        'salesData': SALES_FILE,
        'expenses': EXPENSES_FILE,
        'goals': GOALS_FILE,
        'orders': ORDERS_FILE,
        'customers': CUSTOMERS_FILE,
        'leads': LEADS_FILE
    }
    filepath = filepath_map.get(key)

    if not filepath:
        return jsonify({"message": "Invalid data key."}), 400

    if request.method == 'GET':
        data = load_json_data(filepath)
        # Special handling for users: return as list of user objects, not dict
        if key == 'users':
            return jsonify([{'username': u, **v} for u, v in data.items()]), 200
        return jsonify(data), 200

    elif request.method == 'POST':
        try:
            new_data = request.get_json()
            # Special handling for users: expect a dict, not a list
            if key == 'users':
                if not isinstance(new_data, dict):
                    return jsonify({"message": "Expected a dictionary for users data."}), 400
                save_json_data(filepath, new_data)
                USERS_DATA = new_data
            else:
                if not isinstance(new_data, list):
                    return jsonify({"message": f"Expected a list for {key} data."}), 400
                save_json_data(filepath, new_data)
            return jsonify({"message": f"{key} data updated successfully."}), 200
        except Exception as e:
            return jsonify({"message": f"Error updating {key} data: {str(e)}"}), 400
    
    elif request.method == 'DELETE':
        try:
            item_id = request.get_json().get('id')
            if not item_id:
                return jsonify({"message": "Item ID is required for deletion."}), 400
            
            data = load_json_data(filepath)
            if isinstance(data, list):
                original_len = len(data)
                data = [item for item in data if item.get('id') != item_id]
                if len(data) == original_len:
                    return jsonify({"message": f"Item with ID {item_id} not found."}), 404
            elif isinstance(data, dict) and key == 'users':
                if item_id in data:
                    del data[item_id]
                    USERS_DATA = data
                else:
                    return jsonify({"message": f"User with username {item_id} not found."}), 404
            else:
                return jsonify({"message": f"Deletion not supported for data type {key}."}), 400

            save_json_data(filepath, data)
            return jsonify({"message": f"Item {item_id} deleted successfully from {key}."}), 200
        except Exception as e:
            return jsonify({"message": f"Error deleting item from {key} data: {str(e)}"}), 400

# --- Run the Flask app ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
