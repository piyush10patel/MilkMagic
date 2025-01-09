import os
import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

def init_connection():
    try:
        # Get credentials from env
        username = os.getenv('MONGODB_USERNAME')
        password = os.getenv('MONGODB_PASSWORD')
        cluster = os.getenv('MONGODB_CLUSTER')
        
        # Escape username and password
        username = quote_plus(username)
        password = quote_plus(password)
        
        # Construct the connection string
        mongodb_uri = f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority"
        
        client = MongoClient(mongodb_uri)
        # Test the connection
        client.admin.command('ping')
        return client.milk_magic
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

def save_milk_entry(data):
    db = init_connection()
    if db:
        try:
            db.milk_entries.insert_one(data)
            return True
        except Exception as e:
            st.error(f"Error saving entry: {e}")
            return False
