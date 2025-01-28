import streamlit as st
from database import get_payment_details
from auth_utils import has_permission, can_access_page

# Check access
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login to access this page")
    st.stop()

if not can_access_page('4_Payment_Details'):
    st.error("You don't have permission to access this page")
    st.stop()

# Rest of your Payment Details page code... 