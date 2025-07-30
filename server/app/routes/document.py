from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.auth.auth_bearer import JWTBearer
from app.utils.file_processor import process_pdf
from app.core.tools import upload_pdf_tool, url_upload_tool
from app.database.mongo_crud import MongoDB
import tempfile
import os
from bson import ObjectId

router = APIRouter()

def serialize_doc(doc):
    doc = dict(doc)
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc

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
        
        result = upload_pdf_tool.invoke({"file_path": tmp_path, "user_id": user_id})
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
        return url_upload_tool.invoke({"url": url, "user_id": user_id})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def get_documents(user_id: str = Depends(JWTBearer())):
    docs = MongoDB.get_documents(user_id)
    docs = [serialize_doc(doc) for doc in docs] if docs else []
    return docs