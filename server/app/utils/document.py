# Utilities for uploading, indexing, and deleting PDF documents
from app.database.mongo import MongoDB
from app.database.pinecone_utils import embeddings, index
from langchain_community.document_loaders import PyPDFLoader
from app.database.mongo import db
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
import uuid
import os
import requests
import tempfile

# Upload a PDF file, split, embed, and index it, then log in MongoDB
async def upload_pdf_util(file_path: str, user_id: str, file_name: str) -> dict:
    doc_id = str(uuid.uuid4())
    try:
        # Pinecone setup
        vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        # Split into chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents(docs)

        # Add proper metadata to each chunk
        for doc in docs:
            doc.metadata.update({
                "text": doc.page_content,
                "user_id": user_id,
                "doc_id": doc_id,
                "source": file_name,
                "page": doc.metadata.get("page", None) + 1
            })

        # Upsert into Pinecone
        vector_store.add_documents(docs)

        # Log in MongoDB
        MongoDB.insert_document({
            "user_id": user_id,
            "doc_id": doc_id,
            "file_name": file_name,
            "embedding_status": "complete"
        })

        return {"status": "success", "document_id": doc_id}

    except Exception as e:
        # Log failure in MongoDB
        MongoDB.insert_document({
            "user_id": user_id,
            "doc_id": doc_id,
            "file_name": file_name,
            "embedding_status": "failed",
            "error": str(e)
        })
        return {"status": "error", "message": str(e)}

# Download a PDF from a URL and save to a temp file
def download_pdf(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        return tmp_file.name

# Upload a PDF from a URL, split, embed, and index it, then log in MongoDB
def url_upload_util(url: str, user_id: str, file_name: str) -> dict:
    file_path = download_pdf(url)
    doc_id = str(uuid.uuid4())
    try:
        vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        loader = PyPDFLoader(file_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents(docs)

        for doc in docs:
            doc.metadata.update({
                "text": doc.page_content,
                "user_id": user_id,
                "doc_id": doc_id,
                "source": file_name,
                "page": doc.metadata.get("page", None)
            })

        vector_store.add_documents(docs)

        MongoDB.insert_document({
            "user_id": user_id,
            "doc_id": doc_id,
            "url": url,
            "file_name": file_name,
            "embedding_status": "complete"
        })
        return {"status": "success", "document_id": doc_id}

    except Exception as e:
        # Log failure in MongoDB
        MongoDB.insert_document({
            "user_id": user_id,
            "doc_id": doc_id,
            "url": url,
            "file_name": file_name,
            "embedding_status": "failed",
            "error": str(e)
        })
        return {"status": "error", "message": str(e)}
    finally:
        os.unlink(file_path)

# Delete a document from MongoDB and Pinecone
async def delete_document_util(doc_id: str, user_id: str) -> dict:
    try:
        # Remove from MongoDB
        result = db.documents.delete_one({"doc_id": doc_id, "user_id": user_id})
        if result.deleted_count == 0:
            return {"success": False, "message": "Document not found or not authorized"}

        # Remove from Pinecone
        vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        vector_store.delete(filter={"doc_id": doc_id})
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}
