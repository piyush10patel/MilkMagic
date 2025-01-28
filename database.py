import os
from pymongo import MongoClient
from urllib.parse import quote_plus
<<<<<<< Updated upstream
import streamlit as st
from datetime import datetime, date
import pytz
import pymongo
import ssl
from functools import lru_cache
from typing import Dict, List

# Cache the database connection
=======
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
>>>>>>> Stashed changes
@st.cache_resource
def init_connection():
    """Initialize database connection with connection pooling"""
    try:
<<<<<<< Updated upstream
        connection_string = st.secrets["mongo"]["connection_string"]
        
        # Add SSL options directly in the connection string
        if "?" in connection_string:
            connection_string += "&tlsInsecure=true&ssl=true"
        else:
            connection_string += "?tlsInsecure=true&ssl=true"
        
        client = pymongo.MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,
            maxPoolSize=10,
            minPoolSize=5
        )
        
        # Test the connection
        client.admin.command('ping')
=======
        client = MongoClient(
            st.secrets["mongo"]["connection_string"],
            tlsCAFile=certifi.where(),
            maxPoolSize=5,
            minPoolSize=1
        )
>>>>>>> Stashed changes
        return client.milk_collection
    except Exception as e:
        st.error("Database connection failed")
        return None

<<<<<<< Updated upstream
# Cache farmer list for 5 minutes
@st.cache_data(ttl=300)
def get_all_farmers() -> List[Dict]:
    db = init_connection()
    if db is not None:
        try:
            return list(db.farmers.find().sort("name", 1))
        except Exception as e:
            st.error(f"Error fetching farmers: {e}")
    return []

# Cache farmer details for 5 minutes
@st.cache_data(ttl=300)
def get_farmer_details(name: str) -> Dict:
    db = init_connection()
    if db is not None:
        try:
            return db.farmers.find_one({"name": name})
        except Exception as e:
            st.error(f"Error fetching farmer details: {e}")
    return None

# Cache fat rate for 1 hour
@st.cache_data(ttl=3600)
def get_fat_rate() -> float:
    """Get current fat rate from database"""
    db = init_connection()
    if db is not None:
        try:
            rate_setting = db.settings.find_one({"setting_type": "fat_rate"})
            return rate_setting["value"] if rate_setting else 6.5
        except Exception as e:
            st.error(f"Error fetching fat rate: {e}")
            return 6.5
    return 6.5

# Cache farmer entries for 1 minute
@st.cache_data(ttl=60)
def get_farmer_entries(name: str) -> List[Dict]:
    db = init_connection()
    if db is not None:
        try:
            return list(db.milk_entries.find({
                "farmer.name": name
            }).sort("timestamp", -1))
        except Exception as e:
            st.error(f"Error fetching farmer entries: {e}")
    return []

# Cache farmer payments for 1 minute
@st.cache_data(ttl=60)
def get_farmer_payments(farmer_name: str, year: int, month: int) -> List[Dict]:
    db = init_connection()
    if db is not None:
        try:
            return list(db.payments.find({
                "farmer_name": farmer_name,
                "year": year,
                "month": month
            }).sort("payment_date", -1))
        except Exception as e:
            st.error(f"Error fetching payments: {e}")
    return []

# Write operations don't use caching
def save_milk_entry(data: Dict) -> bool:
    db = init_connection()
    if db is not None:
        try:
            collection_date = data["collection"]["date"]
            if isinstance(collection_date, date):
                collection_date = datetime.combine(collection_date, datetime.min.time())
            
            entry = {
                "farmer": data["farmer"],
                "milk": data["milk"],
                "collection": {
                    "date": collection_date,
                    "shift": data["collection"]["shift"]
                },
                "timestamp": datetime.now(pytz.UTC)
            }
            
            db.milk_entries.insert_one(entry)
            # Clear relevant caches
            get_farmer_entries.clear()
=======
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
>>>>>>> Stashed changes
            return True
        except Exception as e:
            st.error(f"Error saving milk entry: {e}")
            return False
    return False

<<<<<<< Updated upstream
def save_farmer(data: Dict) -> bool:
    db = init_connection()
    if db is not None:
        try:
            existing_farmer = db.farmers.find_one({
                "name": data["name"],
                "father_name": data["father_name"]
            })
            
            if existing_farmer:
                st.error("Farmer with this name and father's name already exists!")
                return False
            
            db.farmers.insert_one({
                "name": data["name"],
                "father_name": data["father_name"],
                "village": data["village"],
                "timestamp": datetime.now(pytz.UTC)
            })
            # Clear farmer caches
            get_all_farmers.clear()
            get_farmer_details.clear()
            return True
        except Exception as e:
            st.error(f"Error saving farmer: {e}")
            return False
    return False

def save_payment(data: Dict) -> bool:
    db = init_connection()
    if db is not None:
        try:
            payment_data = {
                "farmer_name": data["farmer_name"],
                "year": data["year"],
                "month": data["month"],
                "amount_paid": data["amount_paid"],
                "payment_date": datetime.now(pytz.UTC),
                "notes": data.get("notes", "")
            }
            db.payments.insert_one(payment_data)
            # Clear payment cache
            get_farmer_payments.clear()
=======
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
>>>>>>> Stashed changes
            return True
        except Exception as e:
            st.error(f"Error saving payment: {e}")
            return False
    return False

<<<<<<< Updated upstream
def get_farmer(phone):
    db = init_connection()
    if db is not None:
        try:
            return db.farmers.find_one({"phone": phone})
        except Exception as e:
            st.error(f"Error fetching farmer: {e}")
    return None

def save_fat_rate(rate: float) -> bool:
=======
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
>>>>>>> Stashed changes
    """Save new fat rate to database"""
    db = init_connection()
    if db is not None:
        try:
<<<<<<< Updated upstream
            # Update if exists, insert if not
            db.settings.update_one(
                {"setting_type": "fat_rate"},
                {"$set": {
                    "value": rate,
                    "updated_at": datetime.now(pytz.UTC)
                }},
                upsert=True
            )
            # Clear cache
            if hasattr(get_fat_rate, 'clear_cache'):
                get_fat_rate.clear_cache()
=======
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
>>>>>>> Stashed changes
            return True
        except Exception as e:
            st.error(f"Error saving fat rate: {e}")
            return False
    return False
<<<<<<< Updated upstream
=======

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
>>>>>>> Stashed changes
