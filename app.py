import streamlit as st
from auth_utils import check_password

# Set page config
st.set_page_config(
    page_title="Milk Collection System",
    page_icon="🥛",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .css-1d391kg {
        padding-top: 1rem;
    }
    .login-container {
        max-width: 400px;
        margin: auto;
        padding: 20px;
    }
    .stAlert {
        padding: 10px;
        margin-top: 1rem;
    }
    .logout-btn {
        position: absolute;
        top: 1rem;
        right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Logout function
def logout():
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.role = None
    st.rerun()

# Add logout button if user is authenticated
if 'authenticated' in st.session_state and st.session_state.authenticated:
    # Place logout button in top right corner
    with st.container():
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Logout", type="primary", key="logout_btn"):
            logout()
        st.markdown('</div>', unsafe_allow_html=True)

# Center the title and content
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.title("🥛 Milk Collection System")
    
    # Main content
    if check_password():
        # Welcome message
        st.markdown("""
        ### Welcome to the Milk Collection Management System
        
        Please use the sidebar to navigate through different sections:
        
        - **Milk Entry**: Record daily milk collections
        - **Monthly Report**: View and analyze monthly collection data
        - **Payment Details**: Track farmer payments
        - **Farmer Management**: Manage farmer information
        - **Payment Entry**: Record payments to farmers
        - **Rate Management**: Manage fat rates
        
        For any issues or support, please contact the administrator.
        """)

# Note: The check_password() function from auth_utils.py handles the login form
# and session management in the sidebar 