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
        # Show logout button in sidebar
        with st.sidebar:
            authenticator.logout("Logout", "sidebar")
            st.write(f'Welcome *{name}*')
        
        # Main content
        st.title("🥛 Milk Collection Management")
        
        # Today's stats
        st.markdown("### Today's Collection")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="Total Milk Collected",
                value="125 L",
                delta="15 L"
            )
            
        with col2:
            st.metric(
                label="Average Fat",
                value="6.5%",
                delta="0.2%"
            )
            
        with col3:
            st.metric(
                label="Total Amount",
                value="₹4,375",
                delta="₹525"
            )
        
        # Recent activity
        st.markdown("### Recent Activity")
        
        activity_data = [
            {"time": datetime.datetime.now().strftime("%H:%M"), "action": "Evening collection recorded for Farmer A"},
            {"time": (datetime.datetime.now() - datetime.timedelta(hours=1)).strftime("%H:%M"), 
             "action": "Payment of ₹2,500 made to Farmer B"},
            {"time": (datetime.datetime.now() - datetime.timedelta(hours=2)).strftime("%H:%M"), 
             "action": "Morning collection recorded for Farmer C"}
        ]
        
        for activity in activity_data:
            st.text(f"{activity['time']} - {activity['action']}")

if __name__ == "__main__":
    main()
