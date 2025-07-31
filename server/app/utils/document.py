from app.database.mongo import MongoDB
from app.database.pinecone_utils import embeddings, index
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
import uuid
import os
import requests
import tempfile

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

        # Add proper metadata
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
        MongoDB.insert_document({
            "user_id": user_id,
            "doc_id": doc_id,
            "file_name": file_name,
            "embedding_status": "failed",
            "error": str(e)
        })
        return {"status": "error", "message": str(e)}


def download_pdf(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        return tmp_file.name


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
