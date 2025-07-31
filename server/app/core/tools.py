from langchain.tools import tool
from app.database.pinecone_utils import embeddings, index
from typing import Annotated
from langchain_core.tools import tool, InjectedToolArg

@tool
def rag_retriever(query: str, user_id: Annotated[str, InjectedToolArg]) -> str:
    """Retrieve relevant document chunks based on user query."""
    vector = embeddings.embed_query(query)
    filters = {"user_id": user_id}
    results = index.query(vector=vector, filter=filters, top_k=5, include_metadata=True)
    return "\n\n".join([m.metadata["text"] for m in results.matches])