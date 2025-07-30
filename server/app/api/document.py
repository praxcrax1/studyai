from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from server.app.auth.bearer import JWTBearer
from app.services.document_service import DocumentService
import tempfile
import os

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: str = Depends(JWTBearer())
):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        result = DocumentService.upload_document(tmp_path, user_id)
        os.unlink(tmp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload_url")
async def upload_from_url(
    url: str,
    user_id: str = Depends(JWTBearer())
):
    try:
        return DocumentService.upload_from_url(url, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents")
async def get_documents(user_id: str = Depends(JWTBearer())):
    return DocumentService.get_documents(user_id)
