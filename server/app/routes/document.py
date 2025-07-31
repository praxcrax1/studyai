from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.auth.bearer import JWTBearer
from app.utils.document import upload_pdf_util, url_upload_util
from app.database.mongo import MongoDB
from urllib.parse import urlparse
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
        
        result = await upload_pdf_util(tmp_path, user_id, file_name=file.filename)
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
        parsed_url = urlparse(url)
        file_name = os.path.basename(parsed_url.path)
        
        if not file_name or not file_name.lower().endswith(".pdf"):
            raise ValueError("URL does not point to a valid PDF file")

        return url_upload_util(url, user_id, file_name=file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents")
async def get_documents(user_id: str = Depends(JWTBearer())):
    docs = MongoDB.get_documents(user_id)
    docs = [serialize_doc(doc) for doc in docs] if docs else []
    return docs