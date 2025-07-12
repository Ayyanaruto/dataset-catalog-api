from pymongo import MongoClient
from config import Config
import logging

client = None
db = None

def init_db():
    """Initialize MongoDB connection"""
    global client, db
    try:
        client = MongoClient(Config.MONGODB_URI)
        db = client[Config.MONGODB_DB]
        
        client.admin.command('ping')
        logging.info("Successfully connected to MongoDB")
        
        create_indexes()
        
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise

def create_indexes():
    """Create database indexes for better performance"""
    if db is None:
        logging.error("Database not initialized")
        return
        
    try:
        db.datasets.create_index("name")
        db.datasets.create_index("owner")
        db.datasets.create_index("tags")
        db.datasets.create_index("is_deleted")
        
        db.quality_logs.create_index("dataset_id")
        db.quality_logs.create_index("timestamp")
        
        logging.info("Database indexes created successfully")
    except Exception as e:
        logging.error(f"Failed to create indexes: {e}")

def get_db():
    """Get database instance"""
    return db

def close_db():
    """Close database connection"""
    if client:
        client.close()
