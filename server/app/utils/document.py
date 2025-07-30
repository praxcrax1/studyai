from app.database.mongo import MongoDB
from app.database.pinecone_utils import embeddings, index
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
import uuid
import os
import requests
import tempfile

async def upload_pdf_util(file_path: str, user_id: str) -> dict:
    doc_id = str(uuid.uuid4())
    try:
        # Pinecone pipeline
        vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        loader = PyPDFLoader(file_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = splitter.split_documents(docs)
        # Store the actual text and correct user_id in metadata for each chunk
        for doc in docs:
            doc.metadata["text"] = doc.page_content
            doc.metadata["user_id"] = user_id  # Ensure user_id is present and correct
            doc.metadata["doc_id"] = doc_id
        vector_store.add_documents(docs)
        MongoDB.insert_document({
            "user_id": user_id,
            "doc_id": doc_id,
            "embedding_status": "complete"
        })
        return {"status": "success", "document_id": doc_id}
    except Exception as e:
        MongoDB.insert_document({
            "user_id": user_id,
            "doc_id": doc_id,
            "embedding_status": "failed",
            "error": str(e)
        })
        return {"status": "error", "message": str(e)}

def download_pdf(url: str) -> str:
    response = requests.get(url)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(response.content)
        return tmp_file.name

def url_upload_util(url: str, user_id: str) -> dict:
    file_path = download_pdf(url)
    doc_id = str(uuid.uuid4())
    try:
        # Pinecone pipeline
        vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        loader = PyPDFLoader(file_path)
        pages = []
        for page in loader.load():
            pages.append(page)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        docs = splitter.split_documents(pages)
        # Store the actual text and correct user_id in metadata for each chunk
        for doc in docs:
            doc.metadata["text"] = doc.page_content
            doc.metadata["user_id"] = user_id  # Ensure user_id is present and correct
            doc.metadata["doc_id"] = doc_id
        vector_store.add_documents(docs)
        MongoDB.insert_document({
            "user_id": user_id,
            "doc_id": doc_id,
            "url": url,
            "public_id": None,
            "embedding_status": "complete"
        })
        return {"status": "success", "document_id": doc_id}
    except Exception as e:
        MongoDB.insert_document({
            "user_id": user_id,
            "doc_id": doc_id,
            "url": url,
            "public_id": None,
            "embedding_status": "failed",
            "error": str(e)
        })
        return {"status": "error", "message": str(e)}
    finally:
        os.unlink(file_path)
