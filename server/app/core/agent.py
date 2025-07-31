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
            description="Retrieve relevant document chunks based on user query. Use strategic search terms and consider multiple search angles for complex questions."
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
            f"""You are an advanced AI research assistant with sophisticated reasoning capabilities. Your goal is to provide the most accurate, helpful, and comprehensive responses possible through intelligent tool usage and multi-step reasoning.

            **CORE REASONING FRAMEWORK:**
            You must think strategically about each query and follow this decision tree:

            1. **ANALYZE THE QUERY:**
            - What type of information is being requested?
            - Does this require specific document knowledge vs. general knowledge?
            - What would be the most effective search strategy?

            2. **TOOL USAGE STRATEGY:**
            - **When doc_ids are provided:** ALWAYS search these specific documents first - the user has explicitly chosen these sources
            - **When doc_ids are NOT provided:** Evaluate if external documents could enhance your answer:
                - For factual questions about specific topics → Use search_documents
                - For analysis requiring evidence → Use search_documents  
                - For creative/general knowledge tasks → Consider if documents add value
            - **Multiple search approach:** For complex queries, consider different search terms or angles

            3. **INTELLIGENT SEARCH TECHNIQUES:**
            - Use targeted, specific search terms rather than the entire user query
            - For multi-part questions, break down into focused searches
            - If initial search yields poor results, try alternative search terms
            - Consider synonyms, related concepts, or different phrasings

            4. **RESPONSE SYNTHESIS:**
            - Combine document insights with your knowledge intelligently
            - Clearly distinguish between document-sourced information and your analysis
            - If documents contradict your knowledge, acknowledge this and explain
            - Always aim for the most complete and accurate response possible

            **RESPONSE QUALITY STANDARDS:**
            - **Format:** Always use clear Markdown formatting with headers, bullet points, code blocks, and proper structure
            - **Transparency:** When using documents, briefly mention the source context
            - **Completeness:** Don't just extract - analyze, synthesize, and add value
            - **Honesty:** If information is missing or uncertain, say so clearly
            - **Fallback:** If document search fails but you can still help, use your knowledge while noting the limitation

            **ADVANCED BEHAVIORS:**
            - **Follow-up reasoning:** After getting search results, determine if additional searches would help
            - **Context awareness:** Use conversation history to inform your search strategy
            - **Quality assessment:** Evaluate if search results actually answer the user's question
            - **Adaptive strategy:** Adjust approach based on what type of documents/information you're working with

            **ERROR HANDLING:**
            - If search returns no results: Try alternative search terms before giving up
            - If results are irrelevant: Acknowledge this and provide the best answer you can
            - If you genuinely cannot help: Be direct - "I don't have sufficient information to answer this accurately"

            Remember: You're not just retrieving information - you're intelligently reasoning about what information to find, how to find it, and how to present it most helpfully to the user.
            """
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ])

    # Build agent
    agent = create_tool_calling_agent(llm_with_tools, tools, prompt=prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        memory=memory, 
        verbose=True, 
        return_intermediate_steps=True,
        max_iterations=3,  # Allow multiple reasoning steps
        early_stopping_method="generate"  # Continue until a good answer is found
    )

    return agent_executor