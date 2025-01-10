import os
from pymongo import MongoClient
from urllib.parse import quote_plus
import streamlit as st
from datetime import datetime, date
import pytz
import pymongo
import ssl
from functools import lru_cache
from typing import Dict, List

# Cache the database connection
@st.cache_resource
def init_connection():
    try:
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
        return client.milk_collection
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

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
            return True
        except Exception as e:
            st.error(f"Error saving entry: {e}")
            return False
    return False

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
            return True
        except Exception as e:
            st.error(f"Error saving payment: {e}")
            return False
    return False

def get_farmer(phone):
    db = init_connection()
    if db is not None:
        try:
            return db.farmers.find_one({"phone": phone})
        except Exception as e:
            st.error(f"Error fetching farmer: {e}")
    return None
