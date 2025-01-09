import streamlit as st
import streamlit_authenticator as stauth
from database import init_connection
import datetime

st.title("Registration")

def register_user():
    with st.form("registration_form"):
        username = st.text_input("Username")
        name = st.text_input("Full Name")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.form_submit_button("Register"):
            if password == confirm_password:
                db = init_connection()
                hashed_password = stauth.Hasher([password]).generate()[0]
                
                user_data = {
                    "username": username,
                    "name": name,
                    "password": hashed_password,
                    "created_at": datetime.datetime.now()
                }
                
                try:
                    db.users.insert_one(user_data)
                    st.success("Registration successful! Please login.")
                except Exception as e:
                    st.error(f"Registration failed: {e}")
            else:
                st.error("Passwords do not match!")

register_user()
