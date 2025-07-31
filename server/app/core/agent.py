from langchain.agents import AgentExecutor, Tool, create_tool_calling_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.tools import search_documents
from app.config import settings
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_agent(user_id=None, doc_ids=None):
    # LLM
    model = ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3
    )

    def search_documents_user(query: str):
        inputs = {"query": query, "user_id": user_id}
        if doc_ids:
            inputs["doc_ids"] = doc_ids
        return search_documents.invoke(inputs)

    tools = [
        Tool(
            name="search_documents",
            func=search_documents_user,
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
        f"""You are an intelligent, thoughtful AI assistant that can reason step-by-step to provide helpful, accurate answers.

        You have access to external tools, such as a document retriever, which can provide detailed or user-specific information.

        Your decision-making process must follow this logic:
        - **If `doc_ids` are provided**, you must always use the `search_documents` tool to try and answer the question using those specific documents.
        - If `doc_ids` are **not** provided, evaluate whether the question requires external document-based context. Use the tool if it helps improve your answer.
        - If you use the `search_documents` tool but it returns no relevant results, respond with:
        - `"I don't know."` if you truly cannot answer, **or**
        - Use your internal knowledge to give the best possible response, while clearly stating that the documents did not help.
        - If you can answer confidently without using tools, proceed using your internal knowledge.

        Always respond in **Markdown format**:
        - Use clear **titles**, **subtitles**, **bullet points**, and **numbered lists** where helpful.
        - Use **code blocks** for code.
        - Be precise, helpful, and well-organized in all responses.

        Your priority is to **reason step-by-step**, **use tools when needed (especially with doc_ids)**, and **always respond clearly and concisely**.
        """
    ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])


    # Build agent
    agent = create_tool_calling_agent(llm_with_tools, tools, prompt=prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True, return_intermediate_steps=True)

    return agent_executor
