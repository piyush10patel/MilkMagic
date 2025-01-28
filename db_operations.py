import streamlit as st
from datetime import datetime
from pymongo import MongoClient
from password_utils import hash_password, verify_password
from bson import ObjectId

def init_connection():
    """Initialize database connection to MongoDB Atlas"""
    try:
        # Get MongoDB connection string from secrets
        mongo_uri = st.secrets["mongo"]["connection_string"]
        
        # Connect to MongoDB Atlas
        client = MongoClient(mongo_uri)
        return client.milk_collection
    except Exception as e:
        st.error(f"Could not connect to database: {e}")
        return None

def create_initial_admin():
    """Create initial admin user if no users exist"""
    db = init_connection()
    if db is not None:
        try:
            # Check if users collection exists and has any users
            existing_user = db.users.find_one({"username": "admin"})
            if not existing_user:
                # Create admin user
                hashed_password = hash_password("admin123")
                db.users.insert_one({
                    "username": "admin",
                    "password": hashed_password,
                    "role": "admin",
                    "name": "Administrator",
                    "created_at": datetime.now(),
                    "is_active": True
                })
                st.success("Initial admin user created! Username: admin, Password: admin123")
                return True
        except Exception as e:
            st.error(f"Error creating initial admin: {e}")
    return False

def test_connection():
    """Test database connection and initialize admin if needed"""
    db = init_connection()
    if db is not None:
        st.success("Successfully connected to MongoDB Atlas!")
        create_initial_admin()
    else:
        st.error("Failed to connect to MongoDB Atlas")

def get_user_credentials():
    """Get all usernames and passwords from database"""
    db = init_connection()
    if db is not None:
        try:
            users = list(db.users.find({}, {"username": 1, "role": 1}))
            return users
        except Exception as e:
            st.error(f"Error fetching user credentials: {e}")
            return []
    return []

def authenticate_user(username: str, password: str):
    """Authenticate user credentials"""
    db = init_connection()
    if db is not None:
        try:
            user = db.users.find_one({"username": username})
            if user and verify_password(password, user['password']):
                return user
        except Exception as e:
            st.error(f"Error authenticating user: {e}")
    return None

def save_user_credentials(username: str, password: str, role: str) -> bool:
    """Save new user credentials to database"""
    db = init_connection()
    if db is not None:
        try:
            existing = db.users.find_one({"username": username})
            if existing:
                st.error("Username already exists")
                return False
            
            hashed_password = hash_password(password)
            db.users.insert_one({
                "username": username,
                "password": hashed_password,
                "role": role,
                "created_at": datetime.now(),
                "is_active": True
            })
            return True
        except Exception as e:
            st.error(f"Error saving user credentials: {e}")
            return False
    return False

def get_all_farmers():
    """Get all farmers from database"""
    db = init_connection()
    if db is not None:
        try:
            farmers = list(db.farmers.find({}))
            return farmers
        except Exception as e:
            st.error(f"Error fetching farmers: {e}")
            return []
    return []

def save_farmer(farmer_data: dict) -> bool:
    """Save farmer data to database"""
    db = init_connection()
    if db is not None:
        try:
            result = db.farmers.insert_one(farmer_data)
            return bool(result.inserted_id)
        except Exception as e:
            st.error(f"Error saving farmer: {e}")
            return False
    return False

def update_farmer(farmer_id: str, farmer_data: dict) -> bool:
    db = init_connection()
    if db is not None:
        try:
            result = db.farmers.update_one(
                {"_id": ObjectId(farmer_id)},
                {"$set": farmer_data}
            )
            return result.modified_count > 0
        except Exception as e:
            st.error(f"Error updating farmer: {e}")
            return False
    return False

def delete_farmer(farmer_id: str) -> bool:
    db = init_connection()
    if db is not None:
        try:
            result = db.farmers.delete_one({"_id": ObjectId(farmer_id)})
            return result.deleted_count > 0
        except Exception as e:
            st.error(f"Error deleting farmer: {e}")
            return False
    return False

def save_milk_entry(entry_data: dict) -> bool:
    """Save milk entry to database"""
    db = init_connection()
    if db is not None:
        try:
            result = db.milk_entries.insert_one(entry_data)
            return bool(result.inserted_id)
        except Exception as e:
            st.error(f"Error saving milk entry: {e}")
            return False
    return False

def get_milk_entries(start_date: datetime, end_date: datetime):
    db = init_connection()
    if db is not None:
        try:
            entries = list(db.milk_entries.find({
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }))
            return entries
        except Exception as e:
            st.error(f"Error fetching milk entries: {e}")
            return []
    return []

def get_monthly_report(farmer_name: str, month: int, year: int):
    """Get monthly report with optimized query"""
    db = init_connection()
    if db is not None:
        try:
            # Create index if it doesn't exist
            db.milk_entries.create_index([
                ("farmer.name", 1),
                ("collection.date", 1)
            ])
            
            # Optimized query with projection
            entries = list(db.milk_entries.find(
                {
                    "farmer.name": farmer_name,
                    "$expr": {
                        "$and": [
                            {"$eq": [{"$month": "$collection.date"}, month]},
                            {"$eq": [{"$year": "$collection.date"}, year]}
                        ]
                    }
                },
                {
                    "collection.date": 1,
                    "collection.shift": 1,
                    "milk.quantity": 1,
                    "milk.fat": 1,
                    "milk.total_amount": 1,
                    "_id": 0
                }
            ).hint([("farmer.name", 1), ("collection.date", 1)]))
            
            # Optimized transformation
            return [{
                'date': entry['collection']['date'],
                'shift': entry['collection']['shift'].lower(),
                'liters': entry['milk']['quantity'],
                'fat': entry['milk']['fat'],
                'amount': entry['milk']['total_amount']
            } for entry in entries]
            
        except Exception as e:
            return []
    return []

# Payment functions
def save_payment(payment_data: dict) -> bool:
    db = init_connection()
    if db is not None:
        try:
            result = db.payments.insert_one(payment_data)
            return bool(result.inserted_id)
        except Exception as e:
            st.error(f"Error saving payment: {e}")
            return False
    return False

def get_payments(farmer_id: str, start_date: datetime, end_date: datetime):
    db = init_connection()
    if db is not None:
        try:
            payments = list(db.payments.find({
                "farmer_id": farmer_id,
                "date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }))
            return payments
        except Exception as e:
            st.error(f"Error fetching payments: {e}")
            return []
    return []

def get_payment_details(month: int, year: int):
    db = init_connection()
    if db is not None:
        try:
            details = list(db.payments.find({
                "month": month,
                "year": year
            }))
            return details
        except Exception as e:
            st.error(f"Error fetching payment details: {e}")
            return []
    return []

# Rate functions
def save_rate(rate_data: dict) -> bool:
    db = init_connection()
    if db is not None:
        try:
            result = db.rates.insert_one(rate_data)
            return bool(result.inserted_id)
        except Exception as e:
            st.error(f"Error saving rate: {e}")
            return False
    return False

def get_rates():
    db = init_connection()
    if db is not None:
        try:
            rates = list(db.rates.find().sort("effective_date", -1))
            return rates
        except Exception as e:
            st.error(f"Error fetching rates: {e}")
            return []
    return []

def get_current_rate():
    db = init_connection()
    if db is not None:
        try:
            rate = db.rates.find_one({}, sort=[("effective_date", -1)])
            return rate
        except Exception as e:
            st.error(f"Error fetching current rate: {e}")
            return None
    return None

# Add other necessary database functions here... 