from fastapi import APIRouter, Depends, Body
from app.auth.auth_bearer import JWTBearer
from app.core.agent_setup import create_agent_with_thinking
from app.database.mongo_crud import MongoDB

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
        agent = create_agent_with_thinking(user_id, history)
        
        # Process query
        response = agent.invoke({"input": query})
        
        # Update history
        MongoDB.update_chat_history(user_id, {
            "human": query,
            "ai": response["output"]
        })
        
        return {"response": response["output"]}
    except Exception as e:
        return {"error": str(e)}