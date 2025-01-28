import streamlit as st
<<<<<<< Updated upstream
from database import save_fat_rate, get_fat_rate

def manage_rates():
    st.title("💰 Rate Management")
    
    # Get current fat rate
    current_rate = get_fat_rate()
    
    st.subheader("Fat Rate Settings")
    with st.form("fat_rate_form"):
        new_rate = st.number_input(
            "Rate per Fat Percentage (₹)",
            min_value=0.0,
            value=float(current_rate),
            step=0.1,
            help="This rate will be multiplied by the fat percentage to calculate the rate per liter"
        )
        
        # Example calculation
        example_fat = 6.0
        example_rate = example_fat * new_rate
        st.write("Example calculation:")
        st.write(f"For milk with {example_fat}% fat:")
        st.write(f"{example_fat}% × ₹{new_rate:.2f} = ₹{example_rate:.2f} per liter")
        
        submit = st.form_submit_button("Update Rate")
        
        if submit:
            if save_fat_rate(new_rate):
                st.success("Fat rate updated successfully!")
                st.rerun()

if __name__ == "__main__":
    manage_rates() 
=======
from database import save_fat_rate, get_fat_rates, delete_fat_rate
from datetime import datetime
from auth_utils import has_permission, can_access_page

# Check access
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login to access this page")
    st.stop()

if not can_access_page('7_Rate_Management'):
    st.error("You don't have permission to access this page")
    st.stop()

st.title("⚖️ Fat Rate Management")

# Add new fat rate
st.header("Add New Fat Rate")

with st.form("fat_rate_form"):
    fat_value = st.number_input("Fat Percentage", 
                               min_value=3.0, 
                               max_value=12.0, 
                               step=0.1, 
                               format="%.1f")
    
    submitted = st.form_submit_button("Add Fat Rate")
    
    if submitted:
        # Prepare rate data
        rate_data = {
            "setting_type": "fat_rate",
            "value": fat_value,
            "updated_at": datetime.utcnow()
        }
        
        if save_fat_rate(rate_data):
            st.success(f"Successfully added fat rate: {fat_value}%")
            st.rerun()
        else:
            st.error("Failed to add fat rate")

# Display existing fat rates
st.markdown("---")
st.header("Existing Fat Rates")

# Add a refresh button
if st.button("🔄 Refresh"):
    st.rerun()

# Get and display fat rates
fat_rates = get_fat_rates()

if fat_rates:
    # Create a table view
    st.markdown("### Current Fat Rates")
    
    for rate in fat_rates:
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.write(f"**Fat %:** {rate['value']}")
        
        with col2:
            st.write(f"**Updated:** {rate['updated_at'].strftime('%d-%m-%Y %H:%M')}")
        
        with col3:
            if has_permission('delete'):
                if st.button("🗑️ Delete", key=f"del_{rate['_id']}"):
                    if delete_fat_rate(rate['_id']):
                        st.success(f"Deleted fat rate: {rate['value']}%")
                        st.rerun()
                    else:
                        st.error("Failed to delete fat rate")
else:
    st.info("No fat rates found. Add some rates above.")

# Add some helpful information
st.markdown("---")
st.markdown("""
### Notes:
- Fat rates are used to calculate milk prices
- Higher fat percentage typically means higher rate per liter
- Rates should be reviewed and updated periodically
""") 
>>>>>>> Stashed changes
