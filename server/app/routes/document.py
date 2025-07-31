# FastAPI routes for document upload, URL upload, listing, and deletion
from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks
from app.auth.bearer import JWTBearer
from app.utils.document import process_pdf_background, delete_document_util, download_pdf_async
from app.database.mongo import MongoDB
from urllib.parse import urlparse
from fastapi import UploadFile
import aiofiles
import asyncio
import os
import uuid
from bson import ObjectId

router = APIRouter()

def serialize_doc(doc):
    # Convert ObjectId fields to strings for JSON serialization
    doc = dict(doc)
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc

@router.post("/upload")
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(JWTBearer())
):
    # Handle PDF upload, save to temp, and queue background processing
    doc_id = str(uuid.uuid4())
    tmp_path = f"/tmp/{doc_id}.pdf"
    file_name = file.filename or f"upload_{doc_id}.pdf"

    # Stream write file to disk
    async with aiofiles.open(tmp_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            await f.write(chunk)

    MongoDB.insert_document({
        "user_id": user_id,
        "doc_id": doc_id,
        "file_name": file_name,
        "embedding_status": "pending"
    })
    background_tasks.add_task(process_pdf_background, tmp_path, user_id, doc_id, file_name)
    return {"status": "queued", "document_id": doc_id}


@router.post("/upload_url")
async def upload_from_url(
    url: str,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(JWTBearer())
):
    """Queue a PDF document upload from a URL for the authenticated user."""
    try:
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)
        if not file_name or not file_name.lower().endswith(".pdf"):
            raise ValueError("URL does not point to a valid PDF file")
        doc_id = str(uuid.uuid4())

        MongoDB.insert_document({
            "user_id": user_id,
            "doc_id": doc_id,
            "url": url,
            "file_name": file_name,
            "embedding_status": "pending"
        })

        # Sync wrapper for BackgroundTasks to run async download and processing
        def download_and_process():
            # Run async download + processing inside thread-safe loop
            asyncio.run(_download_and_process(url, user_id, doc_id, file_name))
        background_tasks.add_task(download_and_process)

        return {"status": "queued", "document_id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper for background download and processing
async def _download_and_process(url: str, user_id: str, doc_id: str, file_name: str):
    tmp_path = await download_pdf_async(url)
    await process_pdf_background(tmp_path, user_id, doc_id, file_name)

@router.get("/documents")
async def get_documents(user_id: str = Depends(JWTBearer())):
    """Get all documents for the authenticated user."""
    docs = MongoDB.get_documents(user_id)
    return [serialize_doc(doc) for doc in docs] if docs else []

@router.delete("/document/{doc_id}")
async def delete_document(doc_id: str, user_id: str = Depends(JWTBearer())):
    """Delete a document by ID for the authenticated user."""
    try:
        result = await delete_document_util(doc_id, user_id)
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        return {"status": "success", "message": "Document deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
