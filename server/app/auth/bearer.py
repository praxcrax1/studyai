# JWTBearer class for FastAPI authentication using JWT tokens
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.handler import decode_token

class JWTBearer(HTTPBearer):
    # Override the __call__ method to validate JWT and extract user info
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            try:
                # Decode the JWT token and set user_id in request state
                payload = decode_token(credentials.credentials)
                request.state.user_id = payload["sub"]
            except ValueError as e:
                # Raise HTTP 403 if token is invalid
                raise HTTPException(status_code=403, detail=str(e))
            return payload["sub"]  # Return the user ID (ObjectId)
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code")