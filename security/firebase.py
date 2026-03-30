import os

from firebase_admin import credentials, initialize_app


def start_firebase():
    firebase_path = os.getenv("FIREBASE_PATH")
    if not firebase_path:
        raise ValueError("FIREBASE_PATH not set")
    cred = credentials.Certificate(firebase_path)
    initialize_app(cred)
