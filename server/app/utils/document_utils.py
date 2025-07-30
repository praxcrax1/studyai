from app.utils.file_processor import process_pdf, download_pdf
from app.utils.cloudinary import upload_to_cloudinary
from app.database.mongo import MongoDB
from app.database.pinecone_utils import embeddings, store_vectors
import uuid
import os

def upload_pdf_util(file_path: str, user_id: str) -> dict:
    """Upload and process PDF document, handle embedding errors gracefully."""
    chunks = process_pdf(file_path)
    doc_id = str(uuid.uuid4())
    vectors = []

    # Upload to Cloudinary
    public_id = f"user_{user_id}/{os.path.basename(file_path)}"
    cloudinary_res = upload_to_cloudinary(file_path, public_id)

    # Store in MongoDB (initially mark as 'processing')
    MongoDB.insert_document({
        "user_id": user_id,
        "doc_id": doc_id,
        "url": cloudinary_res["secure_url"],
        "public_id": cloudinary_res["public_id"],
        "embedding_status": "processing"
    })

    embedding_error = None
    try:
        # Generate vectors
        for i, chunk in enumerate(chunks):
            vector = embeddings.embed_query(chunk)
            vectors.append((f"{doc_id}_{i}", vector, {
                "text": chunk,
                "user_id": user_id,
                "document_id": doc_id,
                "page": i+1
            }))
        # Store in Pinecone
        store_vectors(vectors)
        # Update status to 'complete'
        if hasattr(MongoDB, 'update_document_status'):
            MongoDB.update_document_status(doc_id, "complete")
    except Exception as e:
        embedding_error = str(e)
        # Update status to 'embedding_failed'
        if hasattr(MongoDB, 'update_document_status'):
            MongoDB.update_document_status(doc_id, "embedding_failed")

    result = {
        "status": "success" if not embedding_error else "partial_success",
        "document_id": doc_id,
        "embedding_error": embedding_error
    }
    return result

def url_upload_util(url: str, user_id: str) -> dict:
    """Download and process PDF from URL"""
    file_path = download_pdf(url)
    result = upload_pdf_util(file_path, user_id)
    os.unlink(file_path)
    return result
