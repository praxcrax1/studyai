from app.config import settings
from pinecone import Pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)

index = pc.Index(settings.PINECONE_INDEX)
embeddings = GoogleGenerativeAIEmbeddings(model=settings.GEMINI_EMBEDDING_MODEL, google_api_key=settings.GEMINI_API_KEY)
