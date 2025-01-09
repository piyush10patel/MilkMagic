import streamlit as st
import streamlit_authenticator as stauth
from database import init_connection

st.set_page_config(
    page_title="MilkMagic",
    page_icon="🥛",
    layout="wide"
)

# Initialize connection to database
conn = init_connection()

def main():
    st.title("🥛 MilkMagic")
    st.write("Welcome to MilkMagic - Your Digital Dairy Management System")
    
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None

    if st.session_state['authentication_status'] is None:
        st.warning("Please login or register to continue")
    
    elif st.session_state['authentication_status']:
        st.success(f"Welcome {st.session_state['name']}")
        
if __name__ == "__main__":
    main()
