from fastapi import FastAPI
from app.routes import document, chat
from app.auth import auth_router
from app.database.mongo_crud import MongoDB
import uvicorn

app = FastAPI()

app.include_router(auth_router.router, prefix="/auth")
app.include_router(document.router, prefix="/documents")
app.include_router(chat.router, prefix="/chat")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)