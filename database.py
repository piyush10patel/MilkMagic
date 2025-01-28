import os
from pymongo import MongoClient
import streamlit as st
from dotenv import load_dotenv
from urllib.parse import quote_plus
import pymongo
from datetime import datetime, date
from bson import ObjectId
from password_utils import hash_password, verify_password
from db_operations import (
    # Authentication
    init_connection,
    test_connection,
    get_user_credentials,
    authenticate_user,
    save_user_credentials,
    
    # Farmers
    get_all_farmers,
    save_farmer,
    update_farmer,
    delete_farmer,
    
    # Milk Entries
    save_milk_entry,
    get_milk_entries,
    get_monthly_report,
    
    # Payments
    save_payment,
    get_payments,
    get_payment_details,
    
    # Rates
    save_rate,
    get_rates,
    get_current_rate
)
import certifi

load_dotenv()

# Use connection pooling
@st.cache_resource
def init_connection():
    """Initialize database connection with connection pooling"""
    try:
        client = MongoClient(
            st.secrets["mongo"]["connection_string"],
            tlsCAFile=certifi.where(),
            maxPoolSize=5,
            minPoolSize=1
        )
        return client.milk_collection
    except Exception as e:
        st.error("Database connection failed")
        return None

# Cache database queries
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_all_farmers():
    """Get all farmers with caching"""
    db = init_connection()
    if db is not None:
        try:
            return list(db.farmers.find({}, {'name': 1, '_id': 0}))
        except Exception as e:
            return []
    return []

@st.cache_data(ttl=60)  # Cache for 1 minute
def get_rates():
    """Get rates with caching"""
    db = init_connection()
    if db is not None:
        try:
            rates = list(db.rates.find())
            return rates
        except Exception as e:
            return []
    return []

def get_all_farmers():
    """Get all farmers from database"""
    db = init_connection()
    if db is not None:
        try:
            return list(db.farmers.find().sort("name", 1))
        except Exception as e:
            st.error(f"Error fetching farmers: {e}")
            return []
    return []

def delete_farmer(farmer_name: str) -> bool:
    """Delete farmer from database"""
    db = init_connection()
    if db is not None:
        try:
            result = db.farmers.delete_one({"name": farmer_name})
            return result.deleted_count > 0
        except Exception as e:
            st.error(f"Error deleting farmer: {e}")
            return False
    return False

def update_farmer(old_name: str, new_data: dict) -> bool:
    """Update farmer details"""
    db = init_connection()
    if db is not None:
        try:
            # Check if new name already exists (if name is being changed)
            if old_name != new_data['name']:
                existing = db.farmers.find_one({"name": new_data['name']})
                if existing:
                    st.error("Farmer with this name already exists")
                    return False
            
            result = db.farmers.update_one(
                {"name": old_name},
                {"$set": new_data}
            )
            return result.modified_count > 0
        except Exception as e:
            st.error(f"Error updating farmer: {e}")
            return False
    return False

def save_milk_entry(entry_data: dict) -> bool:
    """Save new milk entry to database"""
    db = init_connection()
    if db is not None:
        try:
            # Insert the entry
            db.milk_entries.insert_one(entry_data)
            return True
        except Exception as e:
            st.error(f"Error saving milk entry: {e}")
            return False
    return False

def get_farmer_entries(farmer_name=None):
    """Get milk entries for a specific farmer or all entries"""
    db = init_connection()
    if db is not None:
        try:
            query = {"name": farmer_name} if farmer_name else {}
            return list(db.milk_entries.find(query).sort("entry_date", -1))
        except Exception as e:
            st.error(f"Error fetching entries: {e}")
            return []
    return []

def delete_milk_entry(entry_id) -> bool:
    """Delete milk entry from database"""
    db = init_connection()
    if db is not None:
        try:
            if isinstance(entry_id, str):
                entry_id = ObjectId(entry_id)
            result = db.milk_entries.delete_one({"_id": entry_id})
            return result.deleted_count > 0
        except Exception as e:
            st.error(f"Error deleting entry: {e}")
            return False
    return False

def update_milk_entry(entry_id, new_data: dict) -> bool:
    """Update milk entry details"""
    db = init_connection()
    if db is not None:
        try:
            if isinstance(entry_id, str):
                entry_id = ObjectId(entry_id)
            result = db.milk_entries.update_one(
                {"_id": entry_id},
                {"$set": new_data}
            )
            return result.modified_count > 0
        except Exception as e:
            st.error(f"Error updating entry: {e}")
            return False
    return False

def get_all_villages():
    """Get list of predefined villages"""
    # Predefined list of villages
    VILLAGES = [
        "Select Village",
        "Chapda",
        "Kachhaliya"
    ]
    return VILLAGES

def get_rate_for_fat(fat_content: float) -> float:
    """Get rate for specific fat percentage"""
    db = init_connection()
    if db is not None:
        try:
            # Find exact match first
            rate = db.settings.find_one({
                "setting_type": "fat_rate",
                "value": float(fat_content)
            })
            
            if rate:
                return rate['value']
            
            # If no exact match, get closest lower rate
            lower_rate = db.settings.find({
                "setting_type": "fat_rate",
                "value": {"$lte": float(fat_content)}
            }).sort("value", -1).limit(1)
            
            lower_rate = list(lower_rate)
            if lower_rate:
                return lower_rate[0]['value']
            
            return 0.0
        except Exception as e:
            st.error(f"Error getting rate for fat content: {e}")
            return 0.0
    return 0.0

def save_payment(payment_data: dict) -> bool:
    """Save new payment entry to database"""
    db = init_connection()
    if db is not None:
        try:
            db.payments.insert_one(payment_data)
            return True
        except Exception as e:
            st.error(f"Error saving payment: {e}")
            return False
    return False

def get_farmer_payments(farmer_name: str, month: int = None, year: int = None):
    """Get payments for a specific farmer with optional month/year filter"""
    db = init_connection()
    if db is not None:
        try:
            query = {"farmer_name": farmer_name}
            
            # Add month/year filter if provided
            if month and year:
                query["month"] = month
                query["year"] = year
            
            payments = list(db.payments.find(query).sort("payment_date", -1))
            return payments
        except Exception as e:
            st.error(f"Error fetching payments: {e}")
            return []
    return []

def save_fat_rate(rate_data: dict) -> bool:
    """Save new fat rate to database"""
    db = init_connection()
    if db is not None:
        try:
            # Check if fat rate already exists
            existing = db.settings.find_one({
                "setting_type": "fat_rate",
                "value": rate_data['value']
            })
            
            if existing:
                st.error(f"Fat rate {rate_data['value']}% already exists")
                return False
            
            # Insert new fat rate
            db.settings.insert_one(rate_data)
            return True
        except Exception as e:
            st.error(f"Error saving fat rate: {e}")
            return False
    return False

def get_fat_rates():
    """Get all fat rates from database"""
    db = init_connection()
    if db is not None:
        try:
            rates = list(db.settings.find(
                {"setting_type": "fat_rate"}
            ).sort("value", 1))
            return rates
        except Exception as e:
            st.error(f"Error fetching fat rates: {e}")
            return []
    return []

def delete_fat_rate(rate_id) -> bool:
    """Delete fat rate from database"""
    db = init_connection()
    if db is not None:
        try:
            result = db.settings.delete_one({
                "_id": rate_id,
                "setting_type": "fat_rate"
            })
            return result.deleted_count > 0
        except Exception as e:
            st.error(f"Error deleting fat rate: {e}")
            return False
    return False

def save_user(user_data: dict) -> bool:
    """Save new user to database"""
    db = init_connection()
    if db is not None:
        try:
            # Check if user already exists
            existing = db.users.find_one({"username": user_data['username']})
            if existing:
                st.error("Username already exists")
                return False
            
            # Insert new user
            db.users.insert_one(user_data)
            return True
        except Exception as e:
            st.error(f"Error saving user: {e}")
            return False
    return False

def get_all_users():
    """Get all users from database"""
    db = init_connection()
    if db is not None:
        try:
            return list(db.users.find().sort("username", 1))
        except Exception as e:
            st.error(f"Error fetching users: {e}")
            return []
    return []

def update_user_role(username: str, updated_data: dict) -> bool:
    """Update user role and permissions"""
    db = init_connection()
    if db is not None:
        try:
            result = db.users.update_one(
                {"username": username},
                {"$set": updated_data}
            )
            return result.modified_count > 0
        except Exception as e:
            st.error(f"Error updating user: {e}")
            return False
    return False

def delete_user(username: str) -> bool:
    """Delete user from both collections"""
    db = init_connection()
    if db is not None:
        try:
            # Delete from settings (credentials)
            db.settings.delete_one({
                "setting_type": "user_credentials",
                "username": username
            })
            
            # Delete from users (roles/permissions)
            db.users.delete_one({"username": username})
            return True
        except Exception as e:
            st.error(f"Error deleting user: {e}")
            return False
    return False

def reset_user_password(username: str, new_password: str) -> bool:
    """Reset user's password"""
    db = init_connection()
    if db is not None:
        try:
            hashed_password = hash_password(new_password)
            result = db.settings.update_one(
                {
                    "setting_type": "user_credentials",
                    "username": username
                },
                {
                    "$set": {
                        "password": hashed_password,
                        "password_reset_required": False,
                        "last_password_reset": datetime.now()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            st.error(f"Error resetting password: {e}")
            return False
    return False

def get_monthly_report(farmer_name: str, month: int, year: int):
    """Get monthly report without caching for real-time data"""
    db = init_connection()
    if db is not None:
        try:
            # Create a pipeline for efficient aggregation
            pipeline = [
                {
                    "$match": {
                        "farmer.name": farmer_name,
                        "$expr": {
                            "$and": [
                                {"$eq": [{"$month": "$collection.date"}, month]},
                                {"$eq": [{"$year": "$collection.date"}, year]}
                            ]
                        }
                    }
                },
                {
                    "$project": {
                        "date": "$collection.date",
                        "shift": "$collection.shift",
                        "liters": "$milk.quantity",
                        "fat": "$milk.fat",
                        "amount": "$milk.total_amount",
                        "_id": 0
                    }
                },
                {
                    "$sort": {"date": 1}
                }
            ]
            
            entries = list(db.milk_entries.aggregate(pipeline))
            
            # Transform the data
            return [{
                'date': entry['date'],
                'shift': entry['shift'].lower(),
                'liters': float(entry['liters']),
                'fat': float(entry['fat']),
                'amount': float(entry['amount'])
            } for entry in entries]
            
        except Exception as e:
            print(f"Database error: {str(e)}")  # For debugging
            return []
    return []

# You can add other database operations here

# Export all the functions from db_operations
__all__ = [
    # Authentication
    'init_connection',
    'test_connection',
    'get_user_credentials',
    'authenticate_user',
    'save_user_credentials',
    
    # Farmers
    'get_all_farmers',
    'save_farmer',
    'update_farmer',
    'delete_farmer',
    
    # Milk Entries
    'save_milk_entry',
    'get_milk_entries',
    'get_monthly_report',
    
    # Payments
    'save_payment',
    'get_payments',
    'get_payment_details',
    
    # Rates
    'save_rate',
    'get_rates',
    'get_current_rate'
]
