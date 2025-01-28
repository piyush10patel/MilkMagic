import streamlit as st
<<<<<<< Updated upstream
from database import save_milk_entry, get_farmer_entries, get_fat_rate, get_all_farmers, get_farmer_details
from datetime import datetime, date
import pytz

# Define the constants
VILLAGES = ["Kachhaliya", "Chapda"]
SHIFTS = ["Morning", "Evening"]

def calculate_rate(fat):
    """Calculate rate per liter based on fat percentage"""
    # Get current fat rate from database
    fat_rate = get_fat_rate()
    return fat * fat_rate

def create_milk_entry():
    st.title("🥛 Milk Collection Entry")
    
    # Display current fat rate
    current_fat_rate = get_fat_rate()
    st.info(f"Current rate: ₹{current_fat_rate:.2f} per fat percentage")
    
    # Get all farmers for dropdown
    farmers = get_all_farmers()
    farmer_names = [f["name"] for f in farmers]
    
    # Create two columns for entry and history
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("milk_entry_form"):
            st.subheader("Collection Details")
            col_date, col_shift = st.columns(2)
            with col_date:
                collection_date = st.date_input("Date", value=date.today())
            with col_shift:
                shift = st.selectbox("Shift", options=SHIFTS)
            
            st.divider()
            
            # Farmer details
            selected_name = st.selectbox("Select Farmer", options=farmer_names)
            if selected_name:
                farmer_details = get_farmer_details(selected_name)
                if farmer_details:
                    st.info(f"""
                        Father's Name: {farmer_details['father_name']}
                        Village: {farmer_details['village']}
                    """)
            
            st.divider()
            
            # Milk details
            quantity = st.number_input("Quantity (Liters)", min_value=0.0, step=0.1)
            fat = st.number_input("Fat %", min_value=0.0, max_value=100.0, step=0.1)
            snf = st.number_input("SNF %", min_value=0.0, max_value=100.0, step=0.1)
            
            # Rate calculation
            rate_per_liter = calculate_rate(fat)
            total_amount = rate_per_liter * quantity
            
            # Display calculations
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("Rate Calculation:")
                st.write(f"Fat % × ₹{current_fat_rate:.2f} = ₹{rate_per_liter:.2f}/L")
            with col_b:
                st.write("Total Amount:")
                st.write(f"₹{rate_per_liter:.2f} × {quantity:.1f}L = ₹{total_amount:.2f}")
            
            submit_button = st.form_submit_button("Save Entry")
            
            if submit_button:
                if not all([selected_name, quantity]):
                    st.error("Please fill all required fields!")
                    return
                
                farmer_details = get_farmer_details(selected_name)
                if not farmer_details:
                    st.error("Please select a valid farmer!")
                    return
                
                entry_data = {
                    "farmer": {
                        "name": farmer_details["name"],
                        "father_name": farmer_details["father_name"],
                        "village": farmer_details["village"]
=======
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
>>>>>>> Stashed changes
                    },
                    "milk": {
                        "quantity": quantity,
                        "fat": fat,
                        "snf": snf,
                        "rate_per_liter": rate_per_liter,
                        "total_amount": total_amount
                    },
                    "collection": {
<<<<<<< Updated upstream
                        "date": collection_date,
                        "shift": shift
                    }
                }
                
                if save_milk_entry(entry_data):
                    st.success("Entry saved successfully!")
                    st.rerun()
    
    with col2:
        st.subheader("Recent Entries")
        if selected_name:
            entries = get_farmer_entries(selected_name)
            if entries:
                for entry in entries[:5]:
                    with st.expander(f"Entry: {entry['collection']['date'].strftime('%d-%m-%Y')} ({entry['collection']['shift']})"):
                        st.write(f"Father's Name: {entry['farmer']['father_name']}")
                        st.write(f"Quantity: {entry['milk']['quantity']} L")
                        st.write(f"Fat: {entry['milk']['fat']}%")
                        st.write(f"Rate: ₹{entry['milk']['rate_per_liter']:.2f}/L")
                        st.write(f"Amount: ₹{entry['milk']['total_amount']:.2f}")
            else:
                st.info("No previous entries found for this farmer")

if __name__ == "__main__":
    create_milk_entry()
=======
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
>>>>>>> Stashed changes
