import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from database import init_connection
import os
from pathlib import Path
import re

st.set_page_config(
    page_title="MilkMagic",
    page_icon="🥛",
    layout="wide"
)

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def load_config():
    config_path = Path(__file__).parent / 'config.yaml'
    if not config_path.exists():
        config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'email': 'admin@milkmagic.com',
                        'name': 'Admin User',
                        'password': stauth.Hasher(['admin123']).generate()[0]
                    }
                }
            }
        }
        with open(config_path, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
    
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def save_config(config):
    config_path = Path(__file__).parent / 'config.yaml'
    with open(config_path, 'w') as file:
        yaml.dump(config, file, default_flow_style=False)

def register_user(config):
    st.subheader("Register New User")
    with st.form("registration_form"):
        username = st.text_input("Username").lower()
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password_repeat = st.text_input("Repeat Password", type="password")
        register_button = st.form_submit_button("Register")

        if register_button:
            if not all([username, name, email, password, password_repeat]):
                st.error("Please fill in all fields")
                return
            
            if not is_valid_email(email):
                st.error("Please enter a valid email address")
                return

            if password != password_repeat:
                st.error("Passwords do not match")
                return
            
            if len(password) < 6:
                st.error("Password must be at least 6 characters long")
                return

            if username in config['credentials']['usernames']:
                st.error("Username already exists")
                return

            try:
                # Create hasher and hash the password
                hasher = stauth.Hasher([password])
                hashed_password = hasher.hash(password)
                
                config['credentials']['usernames'][username] = {
                    'name': name,
                    'email': email,
                    'password': hashed_password
                }
                save_config(config)
                st.success("Registration successful! Please log in.")
                st.rerun()
            except Exception as e:
                st.error(f"Registration error: {e}")
                st.error(f"Password type: {type(password)}")  # Debug info

def main():
    st.title("🥛 MilkMagic")
    
    # Initialize authentication variables
    name = None
    auth_status = None
    username = None
    
    config = load_config()
    authenticator = stauth.Authenticate(
        config['credentials'],
        'milk_magic_cookie',
        'milk_magic_key',
        cookie_expiry_days=30
    )

    # Create tabs for login and registration
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        try:
            # Handle login without unpacking
            auth_result = authenticator.login('main')
            if auth_result:
                if isinstance(auth_result, dict):
                    name = auth_result.get("name")
                    auth_status = auth_result.get("authentication_status")
                    username = auth_result.get("username")
                elif isinstance(auth_result, tuple):
                    name, auth_status, username = auth_result
        except Exception as e:
            st.error(f"Login error: {e}")
    
    with tab2:
        if not auth_status:
            register_user(config)

    if auth_status == False:
        st.error('Username/password is incorrect')
    elif auth_status == None:
        st.warning('Please enter your username and password')
    elif auth_status:
        # Show logout button in sidebar
        with st.sidebar:
            authenticator.logout('Logout', 'main')
            st.write(f"Logged in as: {name}")
        
        st.success(f'Welcome *{name}*')
        st.write("Welcome to MilkMagic - Your Digital Dairy Management System")
        
        # Add your main app content here
        st.header("Dashboard")
        # Add your dashboard components here

if __name__ == "__main__":
    main()
