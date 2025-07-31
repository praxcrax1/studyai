from langchain.tools import tool
from app.database.pinecone_utils import embeddings, index

@tool
def rag_retriever(query: str, user_id: str, document_ids: list=None) -> str:
    """Retrieve relevant document chunks based on user query"""
    vector = embeddings.embed_query(query)
    filters = {"user_id": user_id}
    if document_ids:
        filters["doc_id"] = {"$in": document_ids}
    results = index.query(
        vector=vector,
        filter=filters,
        top_k=5,
        include_metadata=True
    )
    return "\n\n".join([match.metadata["text"] for match in results.matches])