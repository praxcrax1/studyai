# FastAPI application entry point and router setup
from fastapi import FastAPI
from app.routes import document, chat
from app.auth import router
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# Allow CORS for all origins (customize as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register authentication, document, and chat routers
app.include_router(router.router, prefix="/auth")
app.include_router(document.router, prefix="/documents")
app.include_router(chat.router, prefix="/chat")

# Run the app with Uvicorn if executed directly
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)