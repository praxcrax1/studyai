# Tool for searching relevant document chunks using Pinecone and user context
from typing import Annotated, Optional
from langchain.tools import tool
from langchain_core.tools import InjectedToolArg
from app.database.pinecone_utils import embeddings, index

@tool
def search_documents(
    query: str,
    user_id: Annotated[str, InjectedToolArg],
    doc_ids: Annotated[Optional[list[str]], InjectedToolArg] = None
) -> str:
    """Retrieve relevant document chunks based on user query."""

    # Embed the user query to a vector
    vector = embeddings.embed_query(query)

    # Build filter for Pinecone query (by user and optional doc_ids)
    filter = {"user_id": user_id}
    if doc_ids:
        filter["doc_id"] = {"$in": doc_ids}

    # Query Pinecone for top matches
    response = index.query(vector=vector, filter=filter, top_k=10, include_metadata=True)
    matches = response.matches or []

    # Combine matching document texts into a single string
    content = "\n\n".join([m.metadata.get("text", "") for m in matches])

    return content
