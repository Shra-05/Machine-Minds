import os
from pymongo import MongoClient

# MongoDB Configuration
MONGODB_LOCAL = "mongodb://localhost:27017"
MONGODB_ATLAS = os.getenv("MONGODB_URL", "mongodb://localhost:27017")

# Use local MongoDB for now
MONGODB_URL = MONGODB_LOCAL
DB_NAME = "machine_minds_sih"
COLLECTION_EMAILS = "extracted_emails"
COLLECTION_IOCS = "iocs"

# Database Connection
def get_db_connection():
    """Connect to MongoDB"""
    try:
        client = MongoClient(MONGODB_URL, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Test connection
        db = client[DB_NAME]
        print(f"? Connected to MongoDB: {DB_NAME}")
        return db
    except Exception as e:
        print(f"? MongoDB connection failed: {e}")
        print(f"  Make sure MongoDB is running: mongod")
        raise

# FastAPI Configuration
FASTAPI_HOST = "0.0.0.0"
FASTAPI_PORT = 8000
FASTAPI_RELOAD = True

# Dataset paths
DATASET_DIR = r"C:\Users\HP\Downloads\archive (3)"

# Batch processing
BATCH_SIZE = 100
MAX_WORKERS = 4
