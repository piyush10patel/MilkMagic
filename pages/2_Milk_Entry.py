import streamlit as st
from database import save_milk_entry
import datetime

st.title("Milk Entry")

if st.session_state.get('authentication_status'):
    with st.form("milk_entry_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", datetime.date.today())
            shift = st.selectbox("Shift", ["Morning", "Evening"])
            quantity = st.number_input("Quantity (Liters)", min_value=0.0, step=0.1)
            
        with col2:
            fat = st.number_input("Fat %", min_value=0.0, max_value=100.0, step=0.1)
            snf = st.number_input("SNF %", min_value=0.0, max_value=100.0, step=0.1)
            clr = st.number_input("CLR", min_value=0.0, step=0.1)
        
        if st.form_submit_button("Submit"):
            # Calculate amount (you can modify the formula as per your requirements)
            amount = quantity * (fat * 0.8 + snf * 0.2) * 10
            
            entry_data = {
                "user_id": st.session_state['username'],
                "date": date.isoformat(),
                "shift": shift,
                "quantity": quantity,
                "fat": fat,
                "snf": snf,
                "clr": clr,
                "amount": round(amount, 2),
                "created_at": datetime.datetime.now()
            }
            
            if save_milk_entry(entry_data):
                st.success("Entry saved successfully!")
else:
    st.warning("Please login to enter milk data")
