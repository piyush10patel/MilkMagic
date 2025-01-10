import streamlit as st
import pandas as pd
from database import save_farmer, get_all_farmers

# Define the list of villages
VILLAGES = ["Kachhaliya", "Chapda"]

def manage_farmers():
    st.title("👨‍🌾 Farmer Management")
    
    # Add new farmer form
    st.subheader("Add New Farmer")
    with st.form("add_farmer_form"):
        name = st.text_input("Farmer Name")
        father_name = st.text_input("Father's Name")
        village = st.selectbox("Village", options=VILLAGES)
        
        submit = st.form_submit_button("Add Farmer")
        
        if submit:
            if not all([name, father_name, village]):
                st.error("Please fill all fields!")
                return
            
            farmer_data = {
                "name": name,
                "father_name": father_name,
                "village": village
            }
            
            if save_farmer(farmer_data):
                st.success("Farmer added successfully!")
                st.rerun()
    
    # Display existing farmers
    st.subheader("Existing Farmers")
    farmers = get_all_farmers()
    if farmers:
        # Convert MongoDB documents to DataFrame
        df = pd.DataFrame([
            {
                "Name": f["name"],
                "Father's Name": f["father_name"],
                "Village": f["village"]
            } for f in farmers
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No farmers added yet.")

if __name__ == "__main__":
    manage_farmers() 