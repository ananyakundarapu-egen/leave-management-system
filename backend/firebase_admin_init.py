import firebase_admin
from firebase_admin import credentials
import os

if not firebase_admin._apps:
    if os.getenv("GOOGLE_CLOUD_RUN"):
        firebase_admin.initialize_app()
    else:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)