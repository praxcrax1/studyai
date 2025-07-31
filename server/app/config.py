from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str
    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX: str
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-pro" 
    GEMINI_EMBEDDING_MODEL: str = "models/embedding-001"
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"

settings = Settings()