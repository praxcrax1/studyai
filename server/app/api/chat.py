from fastapi import APIRouter, Depends, Body
from server.app.auth.bearer import JWTBearer
from app.services.chat_service import ChatService

router = APIRouter()

@router.post("/query")
async def chat_query(
    query: str = Body(..., embed=True),
    user_id: str = Depends(JWTBearer())
):
    try:
        response = ChatService.process_query(query, user_id)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}
