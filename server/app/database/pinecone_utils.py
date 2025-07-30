from app.config import settings
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings

pc = Pinecone(
    api_key=settings.PINECONE_API_KEY
)

index = pc.Index(settings.PINECONE_INDEX)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=settings.GEMINI_API_KEY)

def store_vectors(vectors: list):
    index.upsert(vectors=vectors)

def query_vectors(vector: list, filter: dict, k: int=5):
    return index.query(
        vector=vector,
        filter=filter,
        top_k=k,
        include_metadata=True
    )