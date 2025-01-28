import streamlit as st
from db_operations import authenticate_user, get_user_credentials
from typing import Optional
from database import init_connection

# Define user roles and passwords
USERS = {
    'admin': {
        'password': 'admin123',
        'role': 'admin',
        'name': 'Admin User'
    },
    'operator': {
        'password': 'operator123',
        'role': 'operator',
        'name': 'Operator User'
    }
}

# Define role-based access with correct page names
ROLE_ACCESS = {
    'admin': {
        'pages': ['1_Milk_Entry', '3_Monthly_Report', 
                 '4_Payment_Details', '5_Farmer_Management', 
                 '6_Payment_Entry', '7_Rate_Management',
                 '8_Role_Management'],
        'permissions': ['create', 'read', 'update', 'delete']
    },
    'operator': {
        'pages': ['1_Milk_Entry', '3_Monthly_Report'],
        'permissions': ['create', 'read', 'update']
    }
}

# Role templates - Updated with correct page names
ROLE_TEMPLATES = {
    "admin": {
        "pages": ['Milk_Entry', 'Monthly_Report', 
                 'Payment_Details', 'Farmer_Management', 
                 'Payment_Entry', 'Rate_Management',
                 'Role_Management'],
        "permissions": ['create', 'read', 'update', 'delete']
    },
    "operator": {
        "pages": ['Milk_Entry', 'Monthly_Report'],
        "permissions": ['create', 'read', 'update']
    },
    "accountant": {
        "pages": ['Monthly_Report', 'Payment_Details', 'Payment_Entry'],
        "permissions": ['create', 'read', 'update']
    },
    "viewer": {
        "pages": ['Milk_Entry', 'Monthly_Report', 'Payment_Details'],
        "permissions": ['read']
    }
}

def init_session_state():
    """Initialize session state variables"""
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'role' not in st.session_state:
        st.session_state.role = None
    if 'name' not in st.session_state:
        st.session_state.name = None
    if 'permissions' not in st.session_state:
        st.session_state.permissions = []
    if 'login_status' not in st.session_state:
        st.session_state.login_status = False
    if 'accessible_pages' not in st.session_state:
        st.session_state.accessible_pages = []

def check_password():
    """Returns `True` if the user had a correct password."""
    if st.session_state.get("authenticated"):
        return True

    # Initialize session state
    if "login_form_submitted" not in st.session_state:
        st.session_state.login_form_submitted = False

    # Login form
    with st.form("Credentials"):
        input_username = st.text_input("Username", key="input_username")
        input_password = st.text_input("Password", type="password", key="input_password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button("Log in")
        with col2:
            if st.form_submit_button("Reset Password"):
                handle_password_reset()
                return False

        if submitted:
            st.session_state.login_form_submitted = True
            st.session_state.last_username = input_username
            st.session_state.last_password = input_password

    # Handle login logic
    if st.session_state.login_form_submitted:
        username = st.session_state.last_username
        password = st.session_state.last_password
        
        if not username or not password:
            st.error("Please enter both username and password")
            st.session_state.login_form_submitted = False
            return False
        
        user = authenticate_user(username, password)
        if user:
            # Set all necessary session state variables
            st.session_state.authenticated = True
            st.session_state.current_user = username
            st.session_state.role = user.get('role', 'viewer')
            st.session_state.user_id = str(user.get('_id'))
            
            # Debug information
            st.sidebar.write("Login Success:")
            st.sidebar.write(f"Username: {username}")
            st.sidebar.write(f"Role: {st.session_state.role}")
            
            return True
        else:
            st.error("😕 Invalid username or password")
            st.session_state.login_form_submitted = False
            return False

    return False

def handle_password_reset():
    """Handle password reset request"""
    st.session_state['password_reset'] = True
    st.info("Please contact your administrator for password reset.")

def check_user_access(username, page):
    """Check if user has access to the current page"""
    if username not in USERS:
        return False
        
    user_role = USERS[username]['role']
    return page in ROLE_ACCESS[user_role]['pages']

def has_permission(required_role: str) -> bool:
    """Check if current user has the required role"""
    if not st.session_state.authenticated:
        return False
    return st.session_state.get('role', '') == required_role

def can_access_page(page_id: str) -> bool:
    """Check if current user can access the page"""
    if not st.session_state.authenticated:
        return False
    user_role = st.session_state.get('role', '')
    
    # Define page access rules
    admin_pages = ['5_Farmer_Management', '7_Rate_Management', '8_Role_Management','6_Payment_Entry', '4_Payment_Details']
    user_pages = ['1_Milk_Entry', '3_Monthly_Report' ]
    viewer_pages = ['3_Monthly_Report', '4_Payment_Details']
    
    if user_role == 'admin':
        return True
    elif user_role == 'user':
        return page_id in user_pages
    elif user_role == 'viewer':
        return page_id in viewer_pages
    return False

# Add logout functionality
def logout():
    """Clear the session state and log out the user"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun() 