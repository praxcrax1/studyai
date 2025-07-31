from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings

def create_access_token(user_id: str) -> str:
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=2),
        "iat": datetime.now(timezone.utc),
        "sub": user_id
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")