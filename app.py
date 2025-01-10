import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import datetime

def load_config():
    # Default configuration with hashed password
    config = {
        'credentials': {
            'usernames': {
                'admin': {
                    'email': 'admin@milk.com',
                    'name': 'Admin',
                    'password': '$2b$12$gxCmjvXqyXGFRqHxh0.YvOz7h5wNLZHK9PX6.iRwnZD8eZG0cFn8.'
                }
            }
        },
        'cookie': {
            'expiry_days': 30,
            'key': 'some_signature_key',
            'name': 'milk_magic_cookie'
        }
    }
    
    return config

def main():
    st.set_page_config(
        page_title="Milk Collection",
        page_icon="🥛",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load configuration
    config = load_config()
    
    # Create the authenticator object
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    
    # Show login widget
    name, authentication_status, username = authenticator.login("Login", "main")
    
    if authentication_status == False:
        st.error("Username/password is incorrect")
        return
        
    if authentication_status == None:
        st.warning("Please enter your username and password")
        return
    
    if authentication_status:
        # Rest of your code remains the same...

if __name__ == "__main__":
    main()
