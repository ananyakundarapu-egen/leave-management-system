import firebase_admin
from firebase_admin import credentials
import os

if not firebase_admin._apps:
    try:
        if os.path.exists("firebase_key.json"):
            cred = credentials.Certificate("firebase_key.json")
            firebase_admin.initialize_app(cred)
        else:
            firebase_admin.initialize_app()
    except Exception:
        firebase_admin.initialize_app()