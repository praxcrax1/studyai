from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.auth.bearer import JWTBearer
from app.utils.document import upload_pdf_util, url_upload_util
from app.database.mongo import MongoDB
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
        
        result = upload_pdf_util(tmp_path, user_id)
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
        return url_upload_util(url, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def get_documents(user_id: str = Depends(JWTBearer())):
    docs = MongoDB.get_documents(user_id)
    docs = [serialize_doc(doc) for doc in docs] if docs else []
    return docs