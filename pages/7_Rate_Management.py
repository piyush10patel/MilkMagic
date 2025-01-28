import streamlit as st
from database import init_connection
from auth_utils import has_permission, can_access_page
from datetime import datetime
import pytz

# Cache database connection
@st.cache_resource
def get_database():
    return init_connection()

# Cache rate query
@st.cache_data(ttl=60)
def get_current_rates(_db):
    try:
        fat_rate = _db.settings.find_one({"setting_type": "fat_rate"})
        snf_rate = _db.settings.find_one({"setting_type": "snf_rate"})
        return {
            "fat_rate": fat_rate.get('value', 0) if fat_rate else 0,
            "snf_rate": snf_rate.get('value', 0) if snf_rate else 0,
            "updated_at": fat_rate.get('updated_at') if fat_rate else None
        }
    except Exception as e:
        st.error(f"Error fetching rates: {str(e)}")
        return None

# Check access
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login to access this page")
    st.stop()

if not can_access_page('7_Rate_Management'):
    st.error("You don't have permission to access this page")
    st.stop()

st.title("Rate Management")

# Get database connection
db = get_database()
if db is None:
    st.error("Database connection failed")
    st.stop()

# Display current rates
current_rates = get_current_rates(db)
if current_rates:
    st.info(f"Current Rates (Last updated: {current_rates['updated_at'].strftime('%d-%m-%Y %H:%M') if current_rates['updated_at'] else 'Never'})")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Fat Rate", f"₹{current_rates['fat_rate']:.2f}")
    with col2:
        st.metric("SNF Rate", f"₹{current_rates['snf_rate']:.2f}")

# Create form for rate entry
with st.form("rate_entry_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    
    with col1:
        new_fat_rate = st.number_input("Fat Rate (₹)", 
            value=float(current_rates['fat_rate']) if current_rates else 0.0,
            min_value=0.0, step=0.1)
    with col2:
        new_snf_rate = st.number_input("SNF Rate (₹)", 
            value=float(current_rates['snf_rate']) if current_rates else 0.0,
            min_value=0.0, step=0.1)
    
    notes = st.text_area("Notes", height=100)
    submitted = st.form_submit_button("Update Rates")
    
    if submitted:
        try:
            if new_fat_rate <= 0 or new_snf_rate <= 0:
                st.error("Please enter valid rates")
                st.stop()
            
            now = datetime.now(pytz.timezone('Asia/Kolkata'))
            
            # Update fat rate
            fat_result = db.settings.update_one(
                {"setting_type": "fat_rate"},
                {
                    "$set": {
                        "value": new_fat_rate,
                        "updated_at": now
                    }
                },
                upsert=True
            )
            
            # Update snf rate
            snf_result = db.settings.update_one(
                {"setting_type": "snf_rate"},
                {
                    "$set": {
                        "value": new_snf_rate,
                        "updated_at": now
                    }
                },
                upsert=True
            )
            
            if fat_result.modified_count > 0 or snf_result.modified_count > 0:
                st.success("Rates updated successfully")
                st.cache_data.clear()
                st.rerun()
            else:
                st.info("No changes were needed")
                
        except Exception as e:
            st.error(f"Error updating rates: {str(e)}")

# Add some helpful information
st.markdown("---")
st.markdown("""
### Notes:
- Fat rates are used to calculate milk prices
- Higher fat percentage typically means higher rate per liter
- Rates should be reviewed and updated periodically
""") 
