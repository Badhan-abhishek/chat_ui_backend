from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from ...libs.chat import internal_v1
from .gemini_bot import create_gemini_bot
from .code_generator import create_code_generator
from .memory_store import memory_store
from .models import (
    ChatMessage,
    ChatRequest,
    CodeGenerationRequest,
    CodeFile,
    CodeGenerationResponse
)


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
        session_id = request.session_id or memory_store.create_session()
        
        if not request.conversation_history:
            stored_history = memory_store.retrieve(session_id, "conversation_history")
            if stored_history:
                request.conversation_history = stored_history
        
        langchain_history = _convert_to_langchain_messages(request.conversation_history)
        
        updated_history = request.conversation_history + [ChatMessage(role="user", content=request.message)]
        
        bot = create_gemini_bot()
        
        response_content = ""
        async def stream_with_memory():
            nonlocal response_content
            async for chunk in bot.stream_chat(user_input=request.message, conversation_history=langchain_history):
                response_content += chunk
                yield chunk
            
            # Store updated conversation in memory after streaming
            final_history = updated_history + [ChatMessage(role="assistant", content=response_content)]
            memory_store.store(session_id, "conversation_history", final_history, ttl_seconds=3600)
            memory_store.store(session_id, "last_interaction", request.message, ttl_seconds=1800)
        
        return StreamingResponse(
            stream_with_memory(),
            media_type="text/plain",
            headers={"X-Session-ID": session_id}
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


@internal_v1.post("/chat/session", tags=["chat"])
def create_chat_session():
    """Create a new chat session with memory"""
    session_id = memory_store.create_session()
    return {"session_id": session_id, "status": "created"}


@internal_v1.get("/chat/session/{session_id}/history", tags=["chat"])
def get_session_history(session_id: str):
    """Get conversation history for a session"""
    history = memory_store.retrieve(session_id, "conversation_history")
    if history is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return {"session_id": session_id, "history": history}


@internal_v1.delete("/chat/session/{session_id}", tags=["chat"])
def clear_session(session_id: str):
    """Clear all memory for a session"""
    success = memory_store.clear_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "status": "cleared"}


@internal_v1.get("/chat/memory/stats", tags=["chat"])
def get_memory_stats():
    """Get memory store statistics"""
    return memory_store.get_stats()


@internal_v1.post("/chat/memory/cleanup", tags=["chat"])
def cleanup_expired_memory():
    """Clean up expired memory entries"""
    cleaned_count = memory_store.cleanup_expired()
    return {"cleaned_entries": cleaned_count, "status": "completed"}


@internal_v1.get("/chat/health", tags=["chat"])
def chat_health():
    return {"status": "healthy", "service": "gemini-chat"}
