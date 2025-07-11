import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv
import os
import json


def initialize_firebase():
    load_dotenv()

    firebase_json = os.getenv("FIREBASE_CREDENTIALS")
    storage_bucket = os.getenv("FIREBASE_STORAGE_BUCKET")

    if not firebase_json:
        raise ValueError("FIREBASE_CREDENTIALS is not set or is empty.")

    if not storage_bucket:
        raise ValueError("FIREBASE_STORAGE_BUCKET is not set or is empty.")

    try:
        firebase_dict = json.loads(firebase_json)
    except json.JSONDecodeError:
        raise ValueError("FIREBASE_CREDENTIALS is not valid JSON.")

    if not firebase_admin._apps:
        cred = credentials.Certificate(firebase_dict)
        firebase_admin.initialize_app(cred, {"storageBucket": storage_bucket})
