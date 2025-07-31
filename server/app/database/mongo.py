# MongoDB utility class for user, document, and chat history operations
from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

class MongoDB:
    @staticmethod
    def insert_user(user_data: dict) -> str:
        # Insert a new user document and return its ID
        return db.users.insert_one(user_data).inserted_id
    
    @staticmethod
    def find_user(email: str) -> dict:
        # Find a user by email
        return db.users.find_one({"email": email})
    
    @staticmethod
    def insert_document(doc_data: dict) -> str:
        # Insert a new document and return its ID
        return db.documents.insert_one(doc_data).inserted_id
    
    @staticmethod
    def get_documents(user_id: str) -> list:
        # Get all documents for a user
        return list(db.documents.find({"user_id": user_id}))
    
    @staticmethod
    def update_chat_history(user_id: str, message: dict):
        # Add a message to the user's chat history (upsert)
        db.chat_histories.update_one(
            {"session_id": str(user_id)},
            {"$push": {"messages": message}},
            upsert=True
        )
    
    @staticmethod
    def get_chat_history(user_id: str) -> list:
        # Retrieve the chat history for a user
        history = db.chat_histories.find_one({"session_id": str(user_id)})
        return history["messages"] if history else []
