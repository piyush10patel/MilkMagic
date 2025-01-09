import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_connection
from datetime import datetime, timedelta

st.title("Reports & Analytics")

if st.session_state.get('authentication_status'):
    db = init_connection()
    
    # Date Filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Fetch Data
    entries = list(db.milk_entries.find({
        "user_id": st.session_state['username'],
        "date": {
            "$gte": start_date.isoformat(),
            "$lte": end_date.isoformat()
        }
    }))
    
    if entries:
        df = pd.DataFrame(entries)
        
        # Summary Statistics
        st.subheader("Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Milk (L)", f"{df['quantity'].sum():.2f}")
        with col2:
            st.metric("Average Fat %", f"{df['fat'].mean():.2f}")
        with col3:
            st.metric("Total Amount (₹)", f"{df['amount'].sum():.2f}")
        
        # Daily Milk Collection Graph
        st.subheader("Daily Milk Collection")
        fig_daily = px.line(df, x="date", y="quantity", 
                           color="shift", title="Daily Milk Collection")
        st.plotly_chart(fig_daily)
        
        # Fat vs SNF Scatter Plot
        st.subheader("Fat vs SNF Analysis")
        fig_scatter = px.scatter(df, x="fat", y="snf", 
                               color="amount", title="Fat vs SNF Distribution")
        st.plotly_chart(fig_scatter)
        
        # Export Data
        st.subheader("Export Data")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download CSV",
            csv,
            "milk_data.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.info("No data available for the selected date range")
else:
    st.warning("Please login to view reports")
