from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.tools import rag_retriever
from app.config import settings
from langgraph.prebuilt import create_react_agent
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_agent(user_id=None):
    # LLM
    model = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3
    )

    def rag_retriever_with_user(query: str):
        return rag_retriever.invoke({"query": query, "user_id": user_id})

    tools = [
        Tool(
            name="RAGRetriever",
            func=rag_retriever_with_user,
            description="Retrieve relevant document chunks based on user query."
        )
    ]

    llm_with_tools = model.bind_tools(tools)

    # MongoDB-backed memory
    message_history = MongoDBChatMessageHistory(
        connection_string=settings.MONGO_URI,
        session_id=str(user_id),
        database_name=settings.MONGO_DB,
        collection_name="chat_histories"
    )

    memory = ConversationBufferMemory(
        chat_memory=message_history,
        memory_key="chat_history",
        return_messages=True
    )

    prompt = ChatPromptTemplate.from_messages([
    (
        "system",
            """You are an intelligent, thoughtful AI assistant that can reason step-by-step to provide helpful, accurate answers.

        You have access to external tools, such as a document retriever, which can provide detailed or user-specific information.

        Before responding:
        - **Think carefully and reason step-by-step** about the user's question.
        - **Determine whether you need to use a tool** to retrieve external information (e.g., documents, user-specific context).
        - Use the **RAGRetriever** tool when the question requires up-to-date, factual, or document-based content.
        - If you can answer confidently with your internal knowledge, proceed without tools.
        - Always make your final answer clear, concise, and helpful.

        Your priority is to **think first**, **use tools only when needed**, and **answer with clarity and relevance**."""
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad")
    ])


    # Build agent
    agent = create_tool_calling_agent(llm_with_tools, tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=False, return_intermediate_steps=True)

    return agent_executor
