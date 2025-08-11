from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .libs.chat import internal_v1 as chat_router

app = FastAPI(title="Gemini Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/")
def read_root():
    return {"message": "Gemini Chatbot is ready"}

