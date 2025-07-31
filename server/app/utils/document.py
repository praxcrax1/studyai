from app.database.mongo import db
from app.database.pinecone_utils import embeddings, index
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
import uuid
import os
import asyncio
import httpx
import aiofiles

# Heavy work: parse, chunk, embed & store
def _process_pdf_sync(file_path: str, user_id: str, doc_id: str, file_name: str):
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
            "page": (doc.metadata.get("page") or 0) + 1
        })

    vector_store.add_documents(docs)
    db.documents.update_one(
        {"doc_id": doc_id, "user_id": user_id},
        {"$set": {"embedding_status": "complete"}}
    )

# Async wrapper for background execution
async def process_pdf_background(file_path: str, user_id: str, doc_id: str, file_name: str):
    try:
        await asyncio.to_thread(_process_pdf_sync, file_path, user_id, doc_id, file_name)
    except Exception as e:
        db.documents.update_one(
            {"doc_id": doc_id, "user_id": user_id},
            {"$set": {"embedding_status": "failed", "error": str(e)}}
        )
    finally:
        os.unlink(file_path)

# Async PDF download
async def download_pdf_async(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        tmp_path = f"/tmp/{uuid.uuid4()}.pdf"
        async with aiofiles.open(tmp_path   , "wb") as f:
            await f.write(response.content)
        return tmp_path
    
async def download_and_process(url: str, user_id: str, doc_id: str, file_name: str):
    tmp_path = await download_pdf_async(url)
    await process_pdf_background(tmp_path, user_id, doc_id, file_name)

# Delete from Mongo & Pinecone
async def delete_document_util(doc_id: str, user_id: str) -> dict:
    try:
        result = db.documents.delete_one({"doc_id": doc_id, "user_id": user_id})
        if result.deleted_count == 0:
            return {"success": False, "message": "Document not found or not authorized"}
        vector_store = PineconeVectorStore(index=index, embedding=embeddings)
        await asyncio.to_thread(vector_store.delete, filter={"doc_id": doc_id})
        return {"success": True}
    except Exception as e:
        return {"success": False, "message": str(e)}
