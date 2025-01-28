import streamlit as st
from database import get_all_farmers, get_monthly_report
from auth_utils import has_permission, can_access_page
from datetime import datetime, timedelta
import pandas as pd
import calendar

# Check access
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login to access this page")
    st.stop()

if not can_access_page('3_Monthly_Report'):
    st.error("You don't have permission to access this page")
    st.stop()

st.title("Monthly Report")

# Get all farmers
farmers = get_all_farmers()

if not farmers:
    st.error("No farmers found in the database")
    st.stop()

# Filters in main page
st.subheader("Select Filters")

# Create three columns for filters
col1, col2, col3 = st.columns(3)

with col1:
    # Farmer selection
    farmer_names = [farmer['name'] for farmer in farmers]
    selected_farmer = st.selectbox("Select Farmer", farmer_names)

with col2:
    # Month selection
    months = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    current_month = datetime.now().month
    selected_month = st.selectbox("Select Month", 
        list(months.values()), 
        index=current_month-1
    )

with col3:
    # Year selection
    current_year = datetime.now().year
    selected_year = st.selectbox("Select Year", 
        range(current_year-5, current_year+1), 
        index=5
    )

# Convert month name to number
month_num = list(months.keys())[list(months.values()).index(selected_month)]

# Generate Report button - centered
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    generate_report = st.button("Generate Report", use_container_width=True)

if generate_report:
    with st.spinner('Generating report...'):
        entries = get_monthly_report(selected_farmer, month_num, selected_year)
        
        if entries:
            try:
                # Get number of days in the selected month
                num_days = calendar.monthrange(selected_year, month_num)[1]
                
                # Initialize data dictionary
                data = {
                    'Shift': ['M', 'E']  # Morning and Evening rows
                }
                
                # Initialize totals
                total_liters = 0
                total_fat = 0
                total_amount = 0
                day_counts = 0
                
                # Process each day
                for day in range(1, num_days + 1):
                    date_str = f"{day:02d}"
                    data[date_str] = ['', '']
                    
                    # Find entries for this date
                    day_date = datetime(selected_year, month_num, day).date()
                    for entry in entries:
                        if entry['date'].date() == day_date:
                            shift_idx = 0 if entry['shift'] == 'morning' else 1
                            if entry['liters'] > 0:
                                data[date_str][shift_idx] = f"{entry['liters']:.1f}({entry['fat']:.1f})"
                                total_liters += entry['liters']
                                total_fat += entry['fat']
                                total_amount += entry['amount']
                                day_counts += 1
                
                # Add totals
                avg_fat = total_fat / day_counts if day_counts > 0 else 0
                data['Total'] = [f"{total_liters:.1f}({avg_fat:.1f})", ""]
                
                # Create DataFrame
                df = pd.DataFrame(data)
                
                # Display summary
                st.subheader("Monthly Summary")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Liters", f"{total_liters:.1f} L")
                with col2:
                    st.metric("Average Fat", f"{avg_fat:.1f}%")
                with col3:
                    st.metric("Total Amount", f"₹{total_amount:.0f}")
                
                # Display the table
                st.subheader("Daily Details")
                st.dataframe(
                    df,
                    column_config={
                        "Shift": st.column_config.TextColumn(
                            "Shift",
                            width="small",
                        ),
                        **{
                            str(i): st.column_config.TextColumn(
                                str(i),
                                width="small",
                            ) for i in range(1, num_days + 1)
                        },
                        "Total": st.column_config.TextColumn(
                            "Total",
                            width="medium",
                        )
                    },
                    hide_index=True,
                )
                
                # Download button
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Report",
                    data=csv,
                    file_name=f"milk_report_{selected_farmer}_{selected_month}_{selected_year}.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error("Error generating report. Please try again.")
                
        else:
            st.info(f"No entries found for {selected_farmer} in {selected_month} {selected_year}")

# Add these optimizations at the top of the file
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_month_days(year: int, month: int):
    """Cache calendar calculations"""
    return calendar.monthrange(year, month)[1]

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_date_range(year: int, month: int):
    """Cache date range calculations"""
    num_days = get_month_days(year, month)
    return [datetime(year, month, day) for day in range(1, num_days + 1)] 