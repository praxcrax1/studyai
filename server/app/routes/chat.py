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
        # Retrieve chat history
        history = MongoDB.get_chat_history(user_id)

        # Create agent with memory
        agent = create_agent(user_id, history)

        # Process query
        response = agent.invoke({"input": query})

        # Update history
        MongoDB.update_chat_history(user_id, {
            "human": query,
            "ai": response.get("output", "")
        })

        return {"response": response.get("output", "")}
    except Exception as e:
        return {"error": str(e)}