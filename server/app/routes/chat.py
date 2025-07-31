from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse
from app.auth.bearer import JWTBearer
from app.core.agent import create_agent
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

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
