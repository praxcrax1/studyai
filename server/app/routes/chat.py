from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse
from app.auth.bearer import JWTBearer
from app.core.agent import create_agent
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.database.mongo import db

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    doc_ids: Optional[List[str]] = None

@router.post("/query")
async def chat_query(
    body: QueryRequest,
    user_id: str = Depends(JWTBearer())
) -> Dict[str, Any]:
    try:
        agent = create_agent(user_id=user_id, doc_ids=body.doc_ids)

        # If agent.invoke is async:
        response = agent.invoke({"input": body.query})

        answer = response.get("output", "")
        intermediate_steps = response.get("intermediate_steps", [])

        tool_calls = []
        for action, _ in intermediate_steps:
            tool_calls.append({
                "tool": getattr(action, "tool", None),
                "input": getattr(action, "tool_input", {})
            })

        return {
            "response": {
                "answer": answer,
                "tool_calls": tool_calls
            }
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.delete("/delete")
async def delete_chat(user_id: str = Depends(JWTBearer())):
    try:
        result = db.chat_histories.delete_many({"SessionId": str(user_id)})
        deleted_count = result.deleted_count
        if deleted_count == 0:
            return {"status": "not_found", "message": "No chat history found for user."}
        return {"status": "success", "message": f"Deleted {deleted_count} chat history records."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/all")
async def get_all_chats(user_id: str = Depends(JWTBearer())):
    """
    Get all chat history records for the authenticated user.
    Returns a list of chat documents.
    """
    try:
        chats = list(db.chat_histories.find({"SessionId": str(user_id)}))
        for chat in chats:
            chat["_id"] = str(chat["_id"])
        return chats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
