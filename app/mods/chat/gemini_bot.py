import os
import json
from typing import Dict, Any, List, AsyncGenerator
from dataclasses import dataclass
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from .code_generator import create_code_generator, CodeGenerator


@dataclass
class GeminiChatBot:
    def __init__(self, model: str = "gemini-1.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=self.api_key,
            temperature=0.7,
            streaming=True
        )
        
        self.code_generator = create_code_generator(self.api_key, model)
    
    async def stream_chat(self, user_input: str, conversation_history: List[BaseMessage] = None) -> AsyncGenerator[str, None]:
        messages = conversation_history or []
        if user_input:
            messages = messages + [HumanMessage(content=user_input)]
        
        try:
            if self.code_generator.is_programming_question(user_input):
                code_result = await self.code_generator.generate_code(user_input)
                
                tool_call_data = {
                    "type": "tool_call",
                    "tool_name": "code_generator",
                    "description": code_result.description,
                    "files": [
                        {
                            "filename": file.filename,
                            "content": file.content,
                            "language": file.language
                        }
                        for file in code_result.files
                    ]
                }
                yield json.dumps(tool_call_data) + "\n"
                
                response_message = f"I've generated {len(code_result.files)} file(s) for you: {code_result.description}"
                yield json.dumps({"type": "chunk", "content": response_message}) + "\n"
                
                updated_messages = messages + [AIMessage(content=response_message)]
                yield json.dumps({"type": "complete", "full_response": response_message, "message_count": len(updated_messages)}) + "\n"
            else:
                full_response = ""
                async for chunk in self.llm.astream(messages):
                    if chunk.content:
                        full_response += chunk.content
                        yield json.dumps({"type": "chunk", "content": chunk.content}) + "\n"
                
                updated_messages = messages + [AIMessage(content=full_response)]
                yield json.dumps({"type": "complete", "full_response": full_response, "message_count": len(updated_messages)}) + "\n"
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            yield json.dumps({"type": "error", "content": error_msg}) + "\n"


def create_gemini_bot(model: str = "gemini-1.5-flash") -> GeminiChatBot:
    return GeminiChatBot(model=model)