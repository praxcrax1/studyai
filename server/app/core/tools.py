from langchain.tools import tool
from app.database.pinecone_utils import embeddings, index
from typing import Annotated
from langchain_core.tools import tool, InjectedToolArg

@tool(response_format="content_and_artifact")
def rag_retriever(query: str, user_id: Annotated[str, InjectedToolArg]) -> tuple[str, list[dict]]:
    """Retrieve relevant document chunks based on user query."""
    # Embed query
    vector = embeddings.embed_query(query)

    # Query Pinecone
    response = index.query(vector=vector, filter={"user_id": user_id}, top_k=5, include_metadata=True)

    matches = response.matches or []


    content = "\n\n".join([m.metadata.get("text", "") for m in matches])
    artifact = [
        {
            "page": m.metadata.get("page_label"),
            "source": m.metadata.get("source", ""),
            "doc_id": m.metadata.get("doc_id", ""),
            "user_id": m.metadata.get("user_id", ""),
        }
        for m in matches
    ]

    return content, artifact
