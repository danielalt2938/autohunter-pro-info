import firebase_admin
from firebase_admin import credentials, firestore
import os

# Initialize Firebase only once
firebase_app = None

def initialize_firestore():
    global firebase_app
    if not firebase_admin._apps:
        key_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'firebase_key.json')
        cred = credentials.Certificate(key_path)
        firebase_app = firebase_admin.initialize_app(cred)
    return firestore.client()

def upload_publication_to_firestore(publication_data):
    db = initialize_firestore()

    publication_id = str(publication_data["publication_info"]["publication_id"])
    collection_name = "facebook"

    doc_ref = db.collection(collection_name).document(publication_id)
    doc_ref.set(publication_data, merge=True)  # Merge updates if the document exists
    print(f"✅ Synced Firestore document: {collection_name}/{publication_id}")
