"""
Pydantic models for chat API
"""
from pydantic import BaseModel
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    session_id: Optional[str] = None


class CodeGenerationRequest(BaseModel):
    prompt: str


class CodeFile(BaseModel):
    filename: str
    content: str
    language: str


class CodeGenerationResponse(BaseModel):
    description: str
    files: List[CodeFile]