# utils/db.py
import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

def _get_config_path():
    # Look for explicit env vars first, then fallback to default file name
    return os.getenv("FIREBASE_CONFIG_PATH") or os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or "firebase_config.json"

def initialize_firebase(config_path: str = None) -> bool:
    """
    Initialize Firebase Admin SDK with a service account JSON.
    Returns True if initialization succeeded (or was already initialized), False otherwise.
    """
    if firebase_admin._apps:
        return True

    try:
        if not config_path:
            config_path = _get_config_path()

        if not os.path.exists(config_path):
            st.error(
                f"Firebase config not found at '{config_path}'.\n"
                "Set FIREBASE_CONFIG_PATH env var to the path of your service account JSON "
                "or place firebase_config.json in the project root."
            )
            return False

        cred = credentials.Certificate(config_path)
        firebase_admin.initialize_app(cred)
        # Optional quick test (non-fatal)
        try:
            firestore.client().collection("connection_test").document("test").set({
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            st.warning(f"Firebase Admin initialized but test write failed: {e}")
        return True
    except Exception as e:
        st.error(f"Failed to initialize Firebase Admin SDK: {e}")
        return False

def get_db():
    """
    Returns a Firestore client or None if initialization failed.
    """
    ok = initialize_firebase()
    if not ok:
        return None
    try:
        return firestore.client()
    except Exception as e:
        st.error(f"Failed to create Firestore client: {e}")
        return None

# Convenience wrappers (optional - you can call these instead of using db directly)
def add_user_to_db(user_id: str, user_data: dict):
    db = get_db()
    if not db:
        raise RuntimeError("Database not initialized")
    db.collection("users").document(user_id).set(user_data, merge=True)

def get_user_from_db(user_id: str):
    db = get_db()
    if not db:
        raise RuntimeError("Database not initialized")
    doc = db.collection("users").document(user_id).get()
    return doc.to_dict() if doc.exists else None
