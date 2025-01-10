import streamlit as st
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