from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.auth_handler import decode_token

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            try:
                payload = decode_token(credentials.credentials)
                request.state.user_id = payload["sub"]
            except ValueError as e:
                raise HTTPException(status_code=403, detail=str(e))
            return payload["sub"]  # Return the ObjectId, not the token
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code")