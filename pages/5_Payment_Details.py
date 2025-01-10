import streamlit as st
import pandas as pd
from database import get_all_farmers, get_farmer_entries, get_farmer_payments
from datetime import datetime, date
import calendar

def create_payment_details():
    st.title("💰 Payment Details")
    
    # Get all farmers for dropdown
    farmers = get_all_farmers()
    if not farmers:
        st.warning("No farmers found in the database.")
        return
    
    farmer_names = [f["name"] for f in farmers]
    
    # Selection filters
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_farmer = st.selectbox("Select Farmer", options=farmer_names)
    with col2:
        selected_year = st.selectbox("Year", options=range(2023, date.today().year + 1))
    with col3:
        selected_month = st.selectbox("Month", options=range(1, 13), 
                                    format_func=lambda x: calendar.month_name[x])
    
    if selected_farmer:
        farmer_details = next((f for f in farmers if f["name"] == selected_farmer), None)
        if farmer_details:
            st.info(f"""
                **Farmer Details:**
                - Father's Name: {farmer_details['father_name']}
                - Village: {farmer_details['village']}
            """)
    
    # Get entries for selected farmer and month
    entries = get_farmer_entries(selected_farmer)
    
    # Filter entries for selected month and year
    month_entries = []
    for entry in entries:
        entry_date = entry['collection']['date']
        # Convert datetime to date if needed
        if isinstance(entry_date, datetime):
            entry_date = entry_date.date()
        
        # Check if entry is for selected month and year
        if (entry_date.year == selected_year and 
            entry_date.month == selected_month):
            month_entries.append(entry)
    
    if month_entries:
        # Calculate totals
        total_quantity = sum(entry['milk']['quantity'] for entry in month_entries)
        total_amount = sum(entry['milk']['total_amount'] for entry in month_entries)
        
        # Get payment history
        payments = get_farmer_payments(selected_farmer, selected_year, selected_month)
        total_paid = sum(payment['amount_paid'] for payment in payments)
        balance = total_amount - total_paid
        
        # Display Summary Box
        st.markdown("""
        <style>
        .summary-box {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='summary-box'>", unsafe_allow_html=True)
        st.subheader("Monthly Summary")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Milk Collected", f"{total_quantity:.1f} L")
        with col2:
            st.metric("Total Amount", f"₹{total_amount:.2f}")
        with col3:
            st.metric("Total Paid", f"₹{total_paid:.2f}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display Balance prominently with exact values
        balance_text = f"Balance: ₹{abs(balance):.2f}"
        balance_color = "red" if balance > 0 else "green"
        st.markdown(
            f"<h2 style='text-align: center; color: {balance_color};'>{balance_text}</h2>",
            unsafe_allow_html=True
        )
        
        st.divider()
        
        # Detailed entries
        st.subheader("Collection Details")
        data = []
        for entry in month_entries:
            data.append({
                'Date': entry['collection']['date'].strftime('%d-%m-%Y'),
                'Shift': entry['collection']['shift'],
                'Quantity (L)': f"{entry['milk']['quantity']:.1f}",
                'Fat %': f"{entry['milk']['fat']:.1f}",
                'Rate/L': f"₹{entry['milk']['rate_per_liter']:.2f}",
                'Amount': f"₹{entry['milk']['total_amount']:.2f}"
            })
        
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
        
        # Payment History
        st.subheader("Payment History")
        if payments:
            payment_data = []
            for payment in payments:
                payment_data.append({
                    'Date': payment['payment_date'].strftime('%d-%m-%Y'),
                    'Amount Paid': f"₹{payment['amount_paid']:.2f}",
                    'Notes': payment.get('notes', '-')
                })
            payment_df = pd.DataFrame(payment_data)
            st.dataframe(payment_df, use_container_width=True)
        else:
            st.info("No payments recorded for this month")
        
        # Export option
        if st.button("Export to Excel"):
            filename = f"payment_details_{selected_farmer}_{calendar.month_name[selected_month]}_{selected_year}.xlsx"
            
            # Create Excel writer object
            with pd.ExcelWriter(filename) as writer:
                # Write summary
                summary_df = pd.DataFrame([{
                    'Total Milk': f"{total_quantity:.1f} L",
                    'Total Amount': f"₹{total_amount:.2f}",
                    'Total Paid': f"₹{total_paid:.2f}",
                    'Balance': f"₹{balance:.2f}"
                }])
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
                
                # Write detailed entries
                df.to_excel(writer, sheet_name='Collection Details', index=False)
                
                # Write payment history if exists
                if payments:
                    payment_df.to_excel(writer, sheet_name='Payment History', index=False)
            
            # Create download button
            with open(filename, 'rb') as f:
                st.download_button(
                    label="Download Excel file",
                    data=f,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.info("No entries found for the selected month.")

if __name__ == "__main__":
    create_payment_details() 