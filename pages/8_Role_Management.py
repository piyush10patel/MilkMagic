import streamlit as st
from database import init_connection
from auth_utils import has_permission, can_access_page
import pandas as pd
import bcrypt
import re

# Check access
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login to access this page")
    st.stop()

if not can_access_page('8_Role_Management'):
    st.error("You don't have permission to access this page")
    st.stop()

st.title("Role Management")

# Get database connection
db = init_connection()
if db is None:
    st.error("Database connection failed")
    st.stop()

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Create User", "Manage Roles", "Role Permissions"])

with tab1:
    # User Creation Form
    st.subheader("Create New User")
    with st.form("create_user_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input("Username", 
                help="Username should be at least 4 characters")
            new_password = st.text_input("Password", type="password",
                help="Password should be at least 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
        
        with col2:
            full_name = st.text_input("Full Name")
            st.info("New users are assigned 'user' role by default")
        
        create_submitted = st.form_submit_button("Create User", use_container_width=True)
        
        if create_submitted:
            try:
                # Validate inputs
                if not new_username or len(new_username) < 4:
                    st.error("Username must be at least 4 characters long")
                    st.stop()
                
                if not new_password or len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                    st.stop()
                
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                    st.stop()
                
                if not full_name:
                    st.error("Full name is required")
                    st.stop()
                
                # Check if username already exists
                existing_user = db.users.find_one({"username": new_username})
                if existing_user:
                    st.error("Username already exists")
                    st.stop()
                
                # Create new user with default 'user' role
                hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                new_user = {
                    "username": new_username,
                    "password": hashed_password,
                    "full_name": full_name,
                    "role": "user"  # Default role
                }
                
                result = db.users.insert_one(new_user)
                if result.inserted_id:
                    st.success(f"User {new_username} created successfully with default role 'user'")
                else:
                    st.error("Failed to create user")
                    
            except Exception as e:
                st.error(f"Error creating user: {str(e)}")

with tab2:
    # Role Management Section
    st.subheader("Update User Role")
    
    # Get all users and their current roles
    try:
        users = list(db.users.find({}, {"username": 1, "role": 1, "full_name": 1, "_id": 0}))
        if users:
            # Create DataFrame for user roles
            user_data = []
            for user in users:
                user_data.append({
                    "Username": user['username'],
                    "Full Name": user.get('full_name', 'N/A'),  # Use get() with default value
                    "Current Role": user.get('role', 'user')    # Use get() with default value
                })
            
            st.dataframe(
                pd.DataFrame(user_data),
                column_config={
                    "Username": st.column_config.TextColumn("Username", width="medium"),
                    "Full Name": st.column_config.TextColumn("Full Name", width="medium"),
                    "Current Role": st.column_config.TextColumn("Current Role", width="medium")
                },
                hide_index=True
            )
            
            # Role update form
            with st.form("role_update_form"):
                # Create display names for users
                user_options = [
                    f"{user['username']} ({user.get('full_name', 'N/A')})" 
                    for user in users
                ]
                
                selected_user = st.selectbox(
                    "Select User to Update",
                    options=user_options
                )
                
                # Extract username from selection
                selected_username = selected_user.split(" (")[0] if selected_user else None
                
                # Get current role for selected user
                current_user = next((user for user in users if user['username'] == selected_username), None)
                current_role = current_user.get('role', 'user') if current_user else 'user'
                
                # Role selection
                roles = ["admin", "user", "viewer"]
                new_role = st.selectbox(
                    "Select New Role", 
                    options=roles,
                    index=roles.index(current_role) if current_role in roles else 1
                )
                
                update_submitted = st.form_submit_button("Update Role")
                
                if update_submitted:
                    try:
                        if not selected_username:
                            st.error("Please select a user")
                            st.stop()
                        
                        if current_role == new_role:
                            st.info(f"User {selected_username} already has role {new_role}")
                            st.stop()
                        
                        # Prevent removing last admin
                        if current_role == 'admin':
                            admin_count = sum(1 for user in users if user.get('role') == 'admin')
                            if admin_count <= 1 and new_role != 'admin':
                                st.error("Cannot remove the last admin user")
                                st.stop()
                        
                        # Update role
                        result = db.users.update_one(
                            {"username": selected_username},
                            {"$set": {"role": new_role}}
                        )
                        
                        if result.modified_count > 0:
                            st.success(f"Role updated successfully for {selected_username} to {new_role}")
                            st.rerun()
                        else:
                            st.error("Failed to update role")
                        
                    except Exception as e:
                        st.error(f"Error updating role: {str(e)}")
        else:
            st.info("No users found in the database")
            
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")

with tab3:
    st.subheader("Role Permissions Matrix")
    permissions = {
        'Feature': [
            'Milk Entry',
            'Daily Report',
            'Monthly Report',
            'Farmer Management',
            'Rate Management',
            'User Profile',
            'Settings',
            'Role Management'
        ],
        'Admin': ['✅', '✅', '✅', '✅', '✅', '✅', '✅', '✅'],
        'User': ['✅', '✅', '✅', '❌', '❌', '✅', '❌', '❌'],
        'Viewer': ['❌', '✅', '✅', '❌', '❌', '✅', '❌', '❌']
    }
    
    df = pd.DataFrame(permissions)
    st.dataframe(
        df,
        column_config={
            "Feature": st.column_config.TextColumn("Feature", width="medium"),
            "Admin": st.column_config.TextColumn("Admin", width="small"),
            "User": st.column_config.TextColumn("User", width="small"),
            "Viewer": st.column_config.TextColumn("Viewer", width="small")
        },
        hide_index=True
    )

    # Add role descriptions below the permissions matrix
    st.subheader("Role Descriptions")
    st.markdown("""
    **Admin**
    - Full system access
    - Manage users and roles
    - Configure system settings
    
    **User**
    - Enter milk collections
    - View reports
    - Manage profile
    
    **Viewer**
    - View reports only
    - Read-only access
    """) 