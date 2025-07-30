from pymongo import MongoClient
from app.config import settings
from bson import ObjectId

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

class MongoDB:
    @staticmethod
    def insert_user(user_data: dict) -> str:
        return db.users.insert_one(user_data).inserted_id
    
    @staticmethod
    def find_user(email: str) -> dict:
        return db.users.find_one({"email": email})
    
    @staticmethod
    def insert_document(doc_data: dict) -> str:
        return db.documents.insert_one(doc_data).inserted_id
    
    @staticmethod
    def get_documents(user_id: str) -> list:
        # Return all documents for a user_id
        return list(db.documents.find({"user_id": user_id}))
    
    @staticmethod
    def update_chat_history(user_id: str, message: dict):
        db.chat_histories.update_one(
            {"user_id": user_id},
            {"$push": {"messages": message}},
            upsert=True
        )
    
    @staticmethod
    def get_chat_history(user_id: str) -> list:
        history = db.chat_histories.find_one({"user_id": user_id})
        return history["messages"] if history else []