from pydantic import BaseModel
from typing import Optional

class DocumentMetadata(BaseModel):
    source: str
    page: int
    document_id: str

class Document(BaseModel):
    content: str
    metadata: DocumentMetadata