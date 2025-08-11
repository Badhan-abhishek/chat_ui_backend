import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage


@dataclass
class CodeFile:
    filename: str
    content: str
    language: str


@dataclass
class CodeGenerationResult:
    files: List[CodeFile]
    description: str


class CodeGenerator:
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=0.3
        )
    
    def is_programming_question(self, message: str) -> bool:
        """Detect if the message is asking for code generation"""
        programming_keywords = [
            'create', 'build', 'make', 'write', 'generate', 'code',
            'html', 'css', 'javascript', 'js', 'python', 'react',
            'component', 'function', 'class', 'button', 'form',
            'website', 'page', 'app', 'application', 'script'
        ]
        
        code_patterns = [
            r'\b(html|css|js|javascript|python|react|vue|angular)\b',
            r'\b(create|build|make|write|generate)\s+(a|an)?\s*(button|form|component|page|website|app)',
            r'\b(show me|give me|can you)\s+(code|example)',
            r'\bfiles?\s+(for|with)',
            r'\b(frontend|backend|full.?stack)\b'
        ]
        
        message_lower = message.lower()
        
        # Check for programming keywords
        keyword_matches = sum(1 for keyword in programming_keywords if keyword in message_lower)
        
        # Check for code patterns
        pattern_matches = sum(1 for pattern in code_patterns if re.search(pattern, message_lower))
        
        # Consider it a programming question if we have multiple indicators
        return keyword_matches >= 2 or pattern_matches >= 1
    
    async def generate_code(self, user_request: str) -> CodeGenerationResult:
        """Generate code files based on user request"""
        
        system_prompt = """You are a code generation assistant. When a user asks for code, you should:

1. Analyze what they're asking for
2. Generate the appropriate code files
3. Return the result in this exact JSON format:

{
  "description": "Brief description of what was created",
  "files": [
    {
      "filename": "index.html",
      "language": "html",
      "content": "<!DOCTYPE html>..."
    },
    {
      "filename": "style.css", 
      "language": "css",
      "content": "body { margin: 0; }"
    },
    {
      "filename": "script.js",
      "language": "javascript", 
      "content": "console.log('Hello');"
    }
  ]
}

Rules:
- Always provide complete, working code
- Use appropriate file extensions
- Include all necessary files (HTML, CSS, JS if it's a web component)
- Keep code clean and well-commented
- Make sure the code actually works together
- For simple requests, you might only need 1-2 files
- For complex requests, break into logical files

Generate code for the following request:"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_request)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            
            # Extract JSON from response
            content = response.content.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result_data = json.loads(json_str)
                
                files = []
                for file_data in result_data.get('files', []):
                    files.append(CodeFile(
                        filename=file_data['filename'],
                        content=file_data['content'],
                        language=file_data['language']
                    ))
                
                return CodeGenerationResult(
                    files=files,
                    description=result_data.get('description', 'Generated code files')
                )
            else:
                # Fallback: treat entire response as a single file
                return CodeGenerationResult(
                    files=[CodeFile(
                        filename="generated_code.txt",
                        content=content,
                        language="text"
                    )],
                    description="Generated code"
                )
                
        except Exception as e:
            # Return error as a text file
            return CodeGenerationResult(
                files=[CodeFile(
                    filename="error.txt",
                    content=f"Error generating code: {str(e)}",
                    language="text"
                )],
                description="Error occurred during code generation"
            )


def create_code_generator(api_key: str, model: str = "gemini-1.5-flash") -> CodeGenerator:
    return CodeGenerator(api_key=api_key, model=model)