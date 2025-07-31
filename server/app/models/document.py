# Pydantic models for document data and metadata
from pydantic import BaseModel

class DocumentMetadata(BaseModel):
    source: str  # Source of the document
    page: int  # Page number in the document
    document_id: str  # Unique document identifier

class Document(BaseModel):
    content: str  # Text content of the document
    metadata: DocumentMetadata  # Associated metadata