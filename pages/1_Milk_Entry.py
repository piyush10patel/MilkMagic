import streamlit as st
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
                    },
                    "milk": {
                        "quantity": quantity,
                        "fat": fat,
                        "snf": snf,
                        "rate_per_liter": rate_per_liter,
                        "total_amount": total_amount
                    },
                    "collection": {
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
