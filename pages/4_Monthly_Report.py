import streamlit as st
import pandas as pd
from database import get_all_farmers, get_farmer_entries
from datetime import datetime, date
import calendar

def get_month_dates(year, month):
    """Get all dates for the specified month"""
    num_days = calendar.monthrange(year, month)[1]
    return [date(year, month, day) for day in range(1, num_days + 1)]

def create_monthly_report():
    st.title("📊 Monthly Milk Collection Report")
    
    # Date selection
    today = date.today()
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("Year", options=range(today.year-1, today.year+1), index=1)
    with col2:
        selected_month = st.selectbox("Month", options=range(1, 13), index=today.month-1, 
                                    format_func=lambda x: calendar.month_name[x])
    
    st.divider()
    
    # Get all farmers
    farmers = get_all_farmers()
    if not farmers:
        st.warning("No farmers found in the database.")
        return
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create a DataFrame structure
    data = []
    
    # Process each farmer
    for i, farmer in enumerate(farmers):
        status_text.text(f"Processing farmer {i+1}/{len(farmers)}")
        progress_bar.progress((i + 1) / len(farmers))
        
        farmer_name = farmer['name']
        entries = get_farmer_entries(farmer_name)
        
        # Initialize row with farmer details
        row = {
            'Farmer Name': farmer_name,
            'Father Name': farmer['father_name'],
            'Village': farmer['village']
        }
        
        # Get dates for the selected month
        month_dates = get_month_dates(selected_year, selected_month)
        
        # Initialize farmer total
        farmer_total = 0
        
        # Process each date
        for current_date in month_dates:
            # Morning entry
            morning_entry = next((
                entry for entry in entries 
                if isinstance(entry['collection']['date'], datetime) and 
                entry['collection']['date'].date() == current_date or
                isinstance(entry['collection']['date'], date) and 
                entry['collection']['date'] == current_date
                and entry['collection']['shift'] == 'Morning'
            ), None)
            
            # Evening entry
            evening_entry = next((
                entry for entry in entries 
                if isinstance(entry['collection']['date'], datetime) and 
                entry['collection']['date'].date() == current_date or
                isinstance(entry['collection']['date'], date) and 
                entry['collection']['date'] == current_date
                and entry['collection']['shift'] == 'Evening'
            ), None)
            
            # Add to row and update farmer total
            date_str = current_date.strftime('%d-%m')
            morning_qty = morning_entry['milk']['quantity'] if morning_entry else 0
            evening_qty = evening_entry['milk']['quantity'] if evening_entry else 0
            
            row[f'{date_str} (M)'] = f"{morning_qty}L" if morning_qty > 0 else "-"
            row[f'{date_str} (E)'] = f"{evening_qty}L" if evening_qty > 0 else "-"
            
            farmer_total += morning_qty + evening_qty
        
        # Add farmer total to the row
        row['Total'] = f"{farmer_total:.1f}L"
        data.append(row)
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    if not data:
        st.warning("No data found for the selected month.")
        return
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Calculate totals
    df_numeric = df.copy()
    for col in df.columns[3:]:  # Skip farmer details columns
        df_numeric[col] = df[col].apply(lambda x: float(x.replace('L', '')) if x != '-' else 0)
    
    total_row = {'Farmer Name': 'TOTAL', 'Father Name': '', 'Village': ''}
    for col in df_numeric.columns[3:]:
        total = df_numeric[col].sum()
        total_row[col] = f"{total:.1f}L" if total > 0 else "-"
    
    # Add total row to data and recreate DataFrame
    data.append(total_row)
    df = pd.DataFrame(data)
    
    # Style the DataFrame
    def highlight_total_row(row):
        if row['Farmer Name'] == 'TOTAL':
            return ['background-color: #f0f2f6'] * len(row)
        return [''] * len(row)
    
    styled_df = df.style.apply(highlight_total_row, axis=1)
    
    # Display the report
    st.markdown("### Monthly Collection Report")
    
    # Display with horizontal scroll
    st.markdown("""
        <style>
        .stDataFrame {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Display the DataFrame
    st.dataframe(
        styled_df,
        use_container_width=True,
        height=500
    )
    
    # Export functionality
    if st.button("Export to Excel"):
        month_name = calendar.month_name[selected_month]
        filename = f"milk_collection_{month_name}_{selected_year}.xlsx"
        
        # Create Excel file in memory
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Report']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.set_column(idx, idx, max_length + 2)
        
        # Offer download
        with open(filename, 'rb') as f:
            st.download_button(
                label="Download Excel file",
                data=f,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__":
    create_monthly_report()     