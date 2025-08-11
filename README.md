# Gemini Streaming Chatbot with Code Generation

FastAPI streaming chatbot using Google Gemini with intelligent code generation capabilities.

## Features

- 🤖 **Streaming Chat**: Real-time conversation with Google Gemini AI
- 🔧 **Smart Code Generation**: Automatically detects programming questions and generates code files
- 📁 **Multi-file Support**: Creates complete projects with HTML, CSS, JavaScript, Python, and more
- 🎯 **Tool Calls**: Claude-like interface that returns structured code files
- 🔄 **Conversation History**: Maintains context across messages

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Set environment variable:
```bash
export GEMINI_API_KEY=your_api_key_here
```

3. Run server:
```bash
uv run dev
```

4. Test the code generation feature:
```bash
python test_code_generation.py
```

## API Endpoints

### Streaming Chat with Code Generation

**POST** `/api/v1/chat/stream` - Streaming chat with automatic code generation

```json
{
  "message": "Create a simple HTML button with CSS and JavaScript",
  "conversation_history": []
}
```

Response formats:
```json
// Regular chat chunks
{"type": "chunk", "content": "I'll create that for you..."}

// Code generation tool call
{
  "type": "tool_call",
  "tool_name": "code_generator", 
  "description": "Simple interactive button with HTML, CSS, and JavaScript",
  "files": [
    {
      "filename": "index.html",
      "content": "<!DOCTYPE html>...",
      "language": "html"
    },
    {
      "filename": "style.css", 
      "content": "button { padding: 10px; }",
      "language": "css"
    },
    {
      "filename": "script.js",
      "content": "document.querySelector('button')...",
      "language": "javascript"
    }
  ]
}

// Completion
{"type": "complete", "full_response": "I've generated 3 files for you...", "message_count": 2}
```

### Direct Code Generation

**POST** `/api/v1/chat/generate-code` - Generate code without streaming

```json
{
  "prompt": "Create a React login form component"
}
```

Response:
```json
{
  "description": "React login form with validation",
  "files": [
    {
      "filename": "LoginForm.jsx",
      "content": "import React, { useState } from 'react';...",
      "language": "jsx"
    }
  ]
}
```

### Health Check

**GET** `/api/v1/chat/health` - Service health status

## Code Generation Examples

The system automatically detects programming questions and generates appropriate code files:

- **"Create a simple button"** → HTML, CSS, JS files
- **"Build a React component"** → JSX file with component
- **"Make a Python function"** → Python file with function
- **"Design a login form"** → Complete form with validation

## Frontend Integration

See `frontend_example.js` for a complete example of how to integrate the streaming chat and handle tool calls in your frontend application.

Key features:
- Handle streaming responses
- Process tool calls for code generation
- Display generated files with syntax highlighting
- Copy/download functionality

## Programming Question Detection

The system uses intelligent detection to identify when users are asking for code:

- **Keywords**: create, build, make, write, generate, code, html, css, javascript, python, react
- **Patterns**: "create a button", "build an app", "show me code"
- **Context**: Mentions of programming languages, frameworks, or development concepts

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation with examples and testing interface.