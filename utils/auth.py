import streamlit as st
import firebase_admin
from firebase_admin import auth, credentials
from firebase_admin import firestore
from firebase_admin.exceptions import FirebaseError
from utils.db import get_db

def initialize_firebase_auth():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase_config.json")
            firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase initialization failed: {e}")
        return False
    return True

def register_user(email, password, user_data):
    if not initialize_firebase_auth():
        return None
        
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=user_data.get('name', '')
        )
        
        # Add additional user data to Firestore
        db = get_db()
        user_data['uid'] = user.uid
        user_data['created_at'] = firestore.SERVER_TIMESTAMP
        
        db.collection('users').document(user.uid).set(user_data)
        return user.uid
        
    except ValueError as e:
        st.error(f"Invalid data: {e}")
    except auth.EmailAlreadyExistsError:
        st.error("Email already exists")
    except FirebaseError as e:
        st.error(f"Firebase error: {e.code} - {e.message}")
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")
    
    return None

def authenticate_user(email, password):
    if not initialize_firebase_auth():
        return None
        
    try:
        # Note: Firebase Admin SDK doesn't have password verification
        # For actual auth, you need Firebase Client SDK or REST API
        user = auth.get_user_by_email(email)
        return user.uid
    except auth.UserNotFoundError:
        st.error("User not found")
    except FirebaseError as e:
        st.error(f"Authentication error: {e.code} - {e.message}")
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
    
    return None