from fastapi import APIRouter, HTTPException
from app.auth.handler import create_access_token
from app.database.mongo import MongoDB
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
async def register(email: str, password: str):
    if MongoDB.find_user(email):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = pwd_context.hash(password)
    user_id = MongoDB.insert_user({"email": email, "password": hashed})
    return {"access_token": create_access_token(str(user_id))}

@router.post("/login")
async def login(email: str, password: str):
    user = MongoDB.find_user(email)
    if not user or not pwd_context.verify(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token(str(user["_id"]))}