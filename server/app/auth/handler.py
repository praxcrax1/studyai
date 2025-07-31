# JWT token creation and decoding utilities
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.config import settings

# Create a JWT access token for a given user_id
def create_access_token(user_id: str) -> str:
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=settings.EXPIRATION_TIME),
        "iat": datetime.now(timezone.utc),  # Issued at
        "sub": user_id  # Subject (user ID)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

# Decode and validate a JWT token
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        raise ValueError("Token expired")
    except jwt.InvalidTokenError:
        # Token is invalid
        raise ValueError("Invalid token")