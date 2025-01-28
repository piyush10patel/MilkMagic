import streamlit as st
<<<<<<< Updated upstream
from database import get_all_farmers, get_farmer_entries, save_payment, get_farmer_payments
from datetime import datetime, date
import calendar

def create_payment_entry():
    st.title("💸 Payment Entry")
    
    # Get all farmers for dropdown
    farmers = get_all_farmers()
    if not farmers:
        st.warning("No farmers found in the database.")
        return
    
    farmer_names = [f["name"] for f in farmers]
    
    with st.form("payment_entry_form"):
        selected_farmer = st.selectbox("Select Farmer", options=farmer_names)
        
        col1, col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox("Year", options=range(2023, date.today().year + 1))
        with col2:
            selected_month = st.selectbox("Month", options=range(1, 13), 
                                        format_func=lambda x: calendar.month_name[x])
        
        # Show current balance if available
        if selected_farmer:
            entries = get_farmer_entries(selected_farmer)
            month_entries = [
                entry for entry in entries
                if isinstance(entry['collection']['date'], datetime) and
                entry['collection']['date'].year == selected_year and
                entry['collection']['date'].month == selected_month
            ]
            
            if month_entries:
                total_amount = sum(entry['milk']['total_amount'] for entry in month_entries)
                payments = get_farmer_payments(selected_farmer, selected_year, selected_month)
                total_paid = sum(payment['amount_paid'] for payment in payments)
                balance = total_amount - total_paid
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Amount", f"₹{total_amount:.2f}")
                with col2:
                    st.metric("Already Paid", f"₹{total_paid:.2f}")
                with col3:
                    st.metric("Balance", f"₹{balance:.2f}")
        
        amount = st.number_input("Payment Amount (₹)", min_value=0.0, step=100.0)
        notes = st.text_area("Notes (Optional)")
        
        submit = st.form_submit_button("Save Payment")
        
        if submit:
            if not all([selected_farmer, amount]):
                st.error("Please fill all required fields!")
                return
            
            payment_data = {
                "farmer_name": selected_farmer,
                "year": selected_year,
                "month": selected_month,
                "amount_paid": amount,
                "notes": notes
            }
            
            if save_payment(payment_data):
                st.success("Payment saved successfully!")
                st.rerun()
    
    # Show payment history
    if selected_farmer:
        st.subheader("Payment History")
        payments = get_farmer_payments(selected_farmer, selected_year, selected_month)
        if payments:
            for payment in payments:
                with st.expander(f"Payment on {payment['payment_date'].strftime('%d-%m-%Y %H:%M')}"):
                    st.write(f"Amount: ₹{payment['amount_paid']:.2f}")
                    if payment.get('notes'):
                        st.write(f"Notes: {payment['notes']}")
        else:
            st.info("No payment history found for this month.")

if __name__ == "__main__":
    create_payment_entry() 
=======
from database import get_all_farmers, save_payment, get_monthly_report, get_farmer_payments
from datetime import datetime
from auth_utils import has_permission, can_access_page

# Check access
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login to access this page")
    st.stop()

if not can_access_page('6_Payment_Entry'):
    st.error("You don't have permission to access this page")
    st.stop()

st.title("💰 Payment Entry")

# Get all farmers for dropdown
farmers = get_all_farmers()
farmer_names = [f"{farmer['name']} - {farmer.get('village', 'N/A')}" for farmer in farmers]

# Payment Entry Form
st.header("New Payment Entry")

with st.form("payment_entry_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        selected_farmer_full = st.selectbox("Select Farmer", ["Select Farmer"] + farmer_names)
        payment_amount = st.number_input("Amount Paid (₹)", min_value=0.0, step=100.0)
        payment_notes = st.text_input("Payment Notes (e.g., cash, cheque, etc.)")
    
    with col2:
        current_year = datetime.now().year
        payment_year = st.selectbox("Year", range(current_year-1, current_year+2))
        payment_month = st.selectbox("Month", range(1, 13), format_func=lambda x: datetime(2000, x, 1).strftime('%B'))
        
    submitted = st.form_submit_button("Save Payment")
    
    if submitted:
        if selected_farmer_full == "Select Farmer":
            st.error("Please select a farmer")
        elif payment_amount <= 0:
            st.error("Please enter valid payment amount")
        else:
            # Extract farmer name
            farmer_name = selected_farmer_full.split(" - ")[0]
            
            # Prepare payment data
            payment_data = {
                "farmer_name": farmer_name,
                "year": payment_year,
                "month": payment_month,
                "amount_paid": payment_amount,
                "payment_date": datetime.now(),
                "notes": payment_notes
            }
            
            # Save to database
            if save_payment(payment_data):
                st.success(f"Successfully saved payment for {farmer_name}")
                st.rerun()
            else:
                st.error("Failed to save payment")

# Payment Summary Section
st.markdown("---")
st.header("Payment Summary")

# Farmer selection for summary
selected_farmer_summary = st.selectbox(
    "Select Farmer for Summary",
    ["Select Farmer"] + [f['name'] for f in farmers],
    key="summary_farmer"
)

if selected_farmer_summary != "Select Farmer":
    col1, col2 = st.columns(2)
    
    with col1:
        summary_year = st.selectbox("Select Year", range(current_year-1, current_year+2), key="summary_year")
    with col2:
        summary_month = st.selectbox("Select Month", range(1, 13), 
                                   format_func=lambda x: datetime(2000, x, 1).strftime('%B'),
                                   key="summary_month")
    
    # Get milk collection data
    milk_entries = get_monthly_report(selected_farmer_summary, summary_month, summary_year)
    total_milk_amount = sum(entry['milk']['total_amount'] for entry in milk_entries)
    
    # Get payment data
    payments = get_farmer_payments(selected_farmer_summary, summary_month, summary_year)
    total_paid = sum(payment['amount_paid'] for payment in payments)
    
    # Display summary
    st.markdown("### Monthly Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Milk Amount", f"₹{total_milk_amount:.2f}")
    with col2:
        st.metric("Total Paid", f"₹{total_paid:.2f}")
    with col3:
        balance = total_milk_amount - total_paid
        st.metric("Balance", f"₹{balance:.2f}")
    
    # Show payment history
    if payments:
        st.markdown("### Payment History")
        for payment in payments:
            with st.expander(f"Payment on {payment['payment_date'].strftime('%d %B %Y')}"):
                st.write(f"Amount: ₹{payment['amount_paid']:.2f}")
                st.write(f"Notes: {payment['notes']}")
    else:
        st.info("No payments found for selected month") 
>>>>>>> Stashed changes
