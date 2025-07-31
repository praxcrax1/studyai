from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import Tool
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from app.core.tools import rag_retriever
from app.config import settings
from langgraph.prebuilt import create_react_agent
from langchain.tools import tool as lc_tool


def create_agent(user_id=None):

    model = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3
    )
    def rag_retriever_with_user(query: str):
        return rag_retriever.invoke({"query": query, "user_id": user_id})

    wrapped_tool = lc_tool(rag_retriever_with_user, description="Retrieve relevant document chunks based on user query.")
    
    tools = [wrapped_tool]
    llm_with_tools = model.bind_tools(tools)

    agent_executor = create_react_agent(llm_with_tools, tools)

    return agent_executor
