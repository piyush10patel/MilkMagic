import streamlit as st
from database import init_connection
from auth_utils import has_permission, can_access_page
from datetime import datetime
import pytz
import pandas as pd

# Cache database connection
@st.cache_resource
def get_database():
    return init_connection()

# Cache farmer list
@st.cache_data(ttl=300)
def get_farmers(_db):
    return list(_db.farmers.find({}, {"name": 1, "father_name": 1, "_id": 0}))

# Cache recent payments
@st.cache_data(ttl=60)
def get_recent_payments(_db):
    try:
        payments = list(_db.payments.find().sort("payment_date", -1).limit(10))
        return payments
    except Exception as e:
        st.error(f"Error fetching payments: {str(e)}")
        return []

# Get total payments for farmer
def get_farmer_total(_db, farmer_name, year, month):
    try:
        total = _db.payments.aggregate([
            {
                "$match": {
                    "farmer_name": farmer_name,
                    "year": year,
                    "month": month
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$amount_paid"}
                }
            }
        ])
        result = list(total)
        return result[0]['total'] if result else 0
    except Exception as e:
        st.error(f"Error calculating total: {str(e)}")
        return 0

# Check access
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login to access this page")
    st.stop()

if not can_access_page('6_Payment_Entry'):
    st.error("You don't have permission to access this page")
    st.stop()

st.title("Payment Entry")

# Get database connection
db = get_database()
if db is None:
    st.error("Database connection failed")
    st.stop()

# Create form for payment entry
with st.form("payment_entry_form", clear_on_submit=True):
    farmers = get_farmers(db)
    farmer_options = [f"{farmer['name']} ({farmer['father_name']})" for farmer in farmers]
    
    selected_farmer = st.selectbox("Select Farmer", options=farmer_options)
    amount = st.number_input("Payment Amount (₹)", min_value=0.0, step=100.0)
    payment_date = st.date_input("Payment Date")
    notes = st.text_area("Notes", height=100)
    
    submitted = st.form_submit_button("Submit Payment")
    
    if submitted:
        try:
            if not selected_farmer or amount <= 0:
                st.error("Please fill all required fields")
                st.stop()
            
            farmer_name = selected_farmer.split(" (")[0]
            
            payment = {
                "farmer_name": farmer_name,
                "year": payment_date.year,
                "month": payment_date.month,
                "amount_paid": float(amount),
                "payment_date": datetime.combine(payment_date, datetime.min.time()),
                "notes": notes
            }
            
            result = db.payments.insert_one(payment)
            if result.inserted_id:
                st.success(f"Payment of ₹{amount:.2f} recorded for {farmer_name}")
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("Failed to record payment")
                
        except Exception as e:
            st.error(f"Error recording payment: {str(e)}")

# Display recent payments
st.subheader("Recent Payments")
try:
    recent_payments = get_recent_payments(db)
    
    if recent_payments:
        # Convert to DataFrame for better display
        df = pd.DataFrame(recent_payments)
        
        # Format the data
        df['Date'] = pd.to_datetime(df['payment_date']).dt.strftime('%d-%m-%Y')
        df['Farmer'] = df['farmer_name']
        df['Amount'] = df['amount_paid'].apply(lambda x: f"₹{float(x):,.2f}")
        df['Month/Year'] = df.apply(lambda x: f"{x['month']}/{x['year']}", axis=1)
        df['Notes'] = df['notes'].fillna('-')
        
        # Display as table
        st.dataframe(
            df[['Date', 'Farmer', 'Amount', 'Month/Year', 'Notes']],
            hide_index=True,
            use_container_width=True,
            column_config={
                'Date': st.column_config.TextColumn('Date', width='medium'),
                'Farmer': st.column_config.TextColumn('Farmer', width='medium'),
                'Amount': st.column_config.TextColumn('Amount', width='medium'),
                'Month/Year': st.column_config.TextColumn('Month/Year', width='medium'),
                'Notes': st.column_config.TextColumn('Notes', width='large')
            }
        )
        
        # Show total payments
        total_amount = df['amount_paid'].sum()
        st.metric("Total Payments", f"₹{total_amount:,.2f}")
        
    else:
        st.info("No recent payments found")
        
except Exception as e:
    st.error(f"Error loading payment history: {str(e)}") 
