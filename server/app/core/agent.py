from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import Tool
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from app.core.tools import rag_retriever
from app.config import settings

def create_agent(user_id: str, chat_history=None):
    chat_history = chat_history or []

    memory = ConversationBufferWindowMemory(k=10, memory_key="chat_history", return_messages=True)
    for msg in chat_history:
        if isinstance(msg, dict) and "human" in msg and "ai" in msg:
            memory.save_context({"input": msg["human"]}, {"output": msg["ai"]})

    tools = [
        Tool(
            name="KnowledgeRetriever",
            func=lambda q: rag_retriever.invoke({"query": q, "user_id": user_id}),
            description="Search user's uploaded documents"
        ),
    ]

    llm = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        You are an AI assistant that can call tools when necessary. 
        When the user asks about their documents or needs information from their files, call KnowledgeRetriever.
        """),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}")
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=False)
    return executor
