from fastapi import APIRouter, Depends, Body
from app.auth.bearer import JWTBearer
from app.core.agent import create_agent
from app.database.mongo import MongoDB

router = APIRouter()

@router.post("/query")
async def chat_query(
    query: str = Body(..., embed=True),
    user_id: str = Depends(JWTBearer())
):
    try:    
        agent = create_agent(user_id=user_id)

        response = agent.invoke(
            {"input": query}
        )

        for message in response.get("messages", []):
            if hasattr(message, "pretty_print"):
                message.pretty_print()

        return {"response": response}
    except Exception as e:
        return {"error": str(e)}