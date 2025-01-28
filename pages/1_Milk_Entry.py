import streamlit as st
from database import get_all_farmers, save_milk_entry
from auth_utils import has_permission, can_access_page
from datetime import datetime, date

# Check access
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login to access this page")
    st.stop()

if not can_access_page('1_Milk_Entry'):
    st.error("You don't have permission to access this page")
    st.stop()

st.title("🥛 Milk Collection Entry")

# Get all farmers for dropdown
farmers = get_all_farmers()
farmer_names = [f"{farmer['name']} - {farmer.get('village', 'N/A')}" for farmer in farmers]

# Form for milk entry
with st.form("milk_entry_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        # Farmer selection
        selected_farmer_full = st.selectbox("Select Farmer", ["Select Farmer"] + farmer_names)
        
        # Date selection (default to today)
        entry_date = st.date_input("Collection Date", date.today())
        
        # Shift selection
        shift = st.selectbox("Shift", ["Morning", "Evening"])
        
    with col2:
        # Milk details
        quantity = st.number_input("Quantity (Liters)", min_value=0.0, step=0.1)
        fat = st.number_input("Fat %", min_value=0.0, max_value=12.0, step=0.1)
        snf = st.number_input("SNF %", min_value=0.0, max_value=12.0, step=0.1)
        
        # Calculate rate based on fat content
        rate_per_liter = 39.0  # Default rate, you can modify this based on your rate card
        total_amount = quantity * rate_per_liter
        
        st.write(f"Rate per liter: ₹{rate_per_liter:.2f}")
        st.write(f"Total Amount: ₹{total_amount:.2f}")
    
    # Submit button
    submitted = st.form_submit_button("Save Entry")
    
    if submitted:
        if selected_farmer_full == "Select Farmer":
            st.error("Please select a farmer")
        elif quantity <= 0:
            st.error("Please enter valid quantity")
        else:
            # Extract farmer name and find farmer details
            farmer_name = selected_farmer_full.split(" - ")[0]
            farmer = next((f for f in farmers if f['name'] == farmer_name), None)
            
            if farmer:
                # Prepare entry data
                entry_data = {
                    "farmer": {
                        "name": farmer['name'],
                        "father_name": farmer.get('father_name', ''),
                        "village": farmer.get('village', '')
                    },
                    "milk": {
                        "quantity": quantity,
                        "fat": fat,
                        "snf": snf,
                        "rate_per_liter": rate_per_liter,
                        "total_amount": total_amount
                    },
                    "collection": {
                        "date": datetime.combine(entry_date, datetime.min.time()),
                        "shift": shift
                    },
                    "timestamp": datetime.now()
                }
                
                # Save to database
                if save_milk_entry(entry_data):
                    st.success(f"Successfully saved milk entry for {farmer['name']}")
                    # Clear form (rerun the app)
                    st.rerun()
                else:
                    st.error("Failed to save milk entry")
            else:
                st.error("Farmer not found")

# Show recent entries
st.markdown("---")
st.header("Recent Entries")

# Add a refresh button
if st.button("🔄 Refresh"):
    st.rerun()

# Display recent entries in a table
# You can add this functionality later when needed
