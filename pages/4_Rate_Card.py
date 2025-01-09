import streamlit as st
from database import init_connection
import datetime

st.title("Rate Card Management")

if st.session_state.get('authentication_status'):
    db = init_connection()
    
    # Display current rate card
    st.subheader("Current Rate Card")
    current_rates = db.rate_card.find_one({"active": True})
    
    if current_rates:
        st.json(current_rates['rates'])
    
    # Add new rate card
    st.subheader("Add New Rate Card")
    with st.form("rate_card_form"):
        base_rate = st.number_input("Base Rate per Liter", min_value=0.0, step=0.1)
        fat_multiplier = st.number_input("Fat Rate Multiplier", min_value=0.0, step=0.1)
        snf_multiplier = st.number_input("SNF Rate Multiplier", min_value=0.0, step=0.1)
        
        if st.form_submit_button("Save Rate Card"):
            new_rate_card = {
                "active": True,
                "rates": {
                    "base_rate": base_rate,
                    "fat_multiplier": fat_multiplier,
                    "snf_multiplier": snf_multiplier
                },
                "created_at": datetime.datetime.now(),
                "created_by": st.session_state['username']
            }
            
            # Deactivate old rate card
            db.rate_card.update_many(
                {"active": True},
                {"$set": {"active": False}}
            )
            
            # Save new rate card
            db.rate_card.insert_one(new_rate_card)
            st.success("Rate card updated successfully!")
            st.rerun()
else:
    st.warning("Please login to manage rate card") 