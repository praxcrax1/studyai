# Pydantic models for user data
from pydantic import BaseModel

class User(BaseModel):
    email: str  # User's email address
    password: str  # User's password (hashed in DB)

class UserInDB(User):
    id: str  # User's unique ID in the database