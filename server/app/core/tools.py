from langchain.tools import tool
from app.database.pinecone_utils import query_vectors, embeddings, store_vectors
from app.utils.file_processor import process_pdf, download_pdf
from app.utils.cloudinary import upload_to_cloudinary
from app.database.mongo import MongoDB
import uuid
import os

@tool
def rag_retriever(query: str, user_id: str, document_ids: list=None) -> str:
    """Retrieve relevant document chunks based on user query"""
    vector = embeddings.embed_query(query)
    filters = {"user_id": user_id}
    if document_ids:
        filters["document_id"] = {"$in": document_ids}
    
    results = query_vectors(vector, filters)
    return "\n\n".join([match.metadata["text"] for match in results.matches])

# Removed upload_pdf_tool and url_upload_tool from here. Use document_utils.py instead.