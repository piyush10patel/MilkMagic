import streamlit as st
from database import init_connection
from auth_utils import has_permission, can_access_page
from datetime import datetime
import pytz

# Check access
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login to access this page")
    st.stop()

if not can_access_page('5_Farmer_Management'):
    st.error("You don't have permission to access this page")
    st.stop()

st.title("Farmer Management")

# Initialize database connection
db = init_connection()
if db is None:
    st.error("Database connection failed")
    st.stop()

# Add New Farmer Form
st.subheader("Add New Farmer")
with st.form(key="add_farmer_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Farmer Name")
        father_name = st.text_input("Father's Name")
    
    with col2:
        village = st.text_input("Village")
        phone = st.text_input("Phone Number")
    
    submitted = st.form_submit_button("Add Farmer")
    
    if submitted:
        if name and father_name and village:
            try:
                # Check if farmer already exists
                existing_farmer = db.farmers.find_one({"name": name, "father_name": father_name})
                
                if existing_farmer:
                    st.error(f"Farmer {name} already exists!")
                else:
                    # Add new farmer
                    new_farmer = {
                        "name": name,
                        "father_name": father_name,
                        "village": village,
                        "phone": phone,
                        "created_at": datetime.now(pytz.timezone('Asia/Kolkata'))
                    }
                    
                    result = db.farmers.insert_one(new_farmer)
                    if result.inserted_id:
                        st.success(f"Farmer {name} added successfully!")
                    else:
                        st.error("Failed to add farmer")
                        
            except Exception as e:
                st.error(f"Error adding farmer: {str(e)}")
        else:
            st.error("Please fill in all required fields")

# Display Existing Farmers
st.subheader("Existing Farmers")
try:
    farmers = list(db.farmers.find().sort("name", 1))
    
    if farmers:
        # Create a dataframe for display
        farmer_data = []
        for farmer in farmers:
            farmer_data.append({
                "Name": farmer['name'],
                "Father's Name": farmer['father_name'],
                "Village": farmer['village'],
                "Phone": farmer.get('phone', 'N/A')
            })
            
        # Display as table
        st.dataframe(
            farmer_data,
            column_config={
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Father's Name": st.column_config.TextColumn("Father's Name", width="medium"),
                "Village": st.column_config.TextColumn("Village", width="medium"),
                "Phone": st.column_config.TextColumn("Phone", width="medium")
            },
            hide_index=True
        )
    else:
        st.info("No farmers found in the database")
        
except Exception as e:
    st.error(f"Error loading farmers: {str(e)}") 