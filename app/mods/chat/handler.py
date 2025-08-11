from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from ...libs.chat import internal_v1
from .gemini_bot import create_gemini_bot
from .code_generator import create_code_generator


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []


class CodeGenerationRequest(BaseModel):
    prompt: str


class CodeFile(BaseModel):
    filename: str
    content: str
    language: str


class CodeGenerationResponse(BaseModel):
    description: str
    files: List[CodeFile]


def _convert_to_langchain_messages(messages: List[ChatMessage]) -> List[BaseMessage]:
    langchain_messages = []
    for msg in messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))
    return langchain_messages


@internal_v1.post("/chat/stream", tags=["chat"])
async def chat_stream(request: ChatRequest):
    try:
        bot = create_gemini_bot()
        langchain_history = _convert_to_langchain_messages(request.conversation_history)
        
        return StreamingResponse(
            bot.stream_chat(user_input=request.message, conversation_history=langchain_history),
            media_type="text/plain"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@internal_v1.post("/chat/generate-code", tags=["chat"])
async def generate_code(request: CodeGenerationRequest):
    """Generate code files based on user prompt"""
    try:
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="GEMINI_API_KEY not configured")
        
        code_generator = create_code_generator(api_key)
        result = await code_generator.generate_code(request.prompt)
        
        return CodeGenerationResponse(
            description=result.description,
            files=[
                CodeFile(
                    filename=file.filename,
                    content=file.content,
                    language=file.language
                )
                for file in result.files
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")


@internal_v1.get("/chat/health", tags=["chat"])
def chat_health():
    return {"status": "healthy", "service": "gemini-chat"}
