from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str
    PINECONE_API_KEY: str
    PINECONE_ENV: str
    PINECONE_INDEX: str
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"  # Default model, can be overridden
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()