from fastapi import APIRouter, Depends, Body
from app.auth.bearer import JWTBearer
from app.core.agent import create_agent

router = APIRouter()

@router.post("/query")
async def chat_query(
    query: str = Body(..., embed=True),
    user_id: str = Depends(JWTBearer())
):
    try:

        agent = create_agent(user_id=user_id)
        response = agent.invoke({"input": query})

        answer = response.get("output")
        tool_calls = []

        for idx, (action, obs) in enumerate(response.get("intermediate_steps", [])):
            tool_calls.append({"tool": action.tool, "input": action.tool_input})

        return {
            "response": {
                "answer": answer,
                "tool_calls": tool_calls
            }
        }
    except Exception as e:
        return {"error": str(e)}
