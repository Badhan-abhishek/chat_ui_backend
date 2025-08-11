# Gemini Streaming Chatbot with Code Generation

FastAPI streaming chatbot using Google Gemini with intelligent code generation capabilities and session-based memory.

## Features

- 🤖 **Streaming Chat**: Real-time conversation with Google Gemini AI.
- 🔧 **Smart Code Generation**: Automatically detects programming questions and generates code files.
- 📁 **Multi-file Support**: Creates complete projects with HTML, CSS, JavaScript, Python, and more.
- 🔄 **Conversation History**: Maintains context across messages using session-based memory.
- 🛠️ **Session Management**: Endpoints to create, retrieve, and clear chat sessions.

## Setup

1.  **Install Dependencies**:
    ```bash
    uv sync
    ```

2. **Source uv env**:
   ```bash
   source .venv/bin/activate
   ```

3.  **Set Environment Variable**:
    Create a `.env` file in the root directory and add your Gemini API key:
    ```
    GEMINI_API_KEY=your_api_key_here
    ```

4.  **Run Server**:
    ```bash
    uvicorn app.app:app --reload --port 8000
    ```
    The API will be available at `http://localhost:8000`.

## API Endpoints

### Streaming Chat

**POST** `/api/v1/chat/stream`

Streams a chat response from the Gemini AI. It maintains conversation history automatically.

- **Request Body**:
  ```json
  {
    "message": "Hello, how are you?",
    "session_id": "optional-session-id"
  }
  ```
- **Response**: A streaming response of plain text chunks. The `X-Session-ID` header in the response contains the session ID.

### Code Generation

**POST** `/api/v1/chat/generate-code`

Generates code files based on a user prompt.

- **Request Body**:
  ```json
  {
    "prompt": "Create a React login form component"
  }
  ```
- **Response**:
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

### Session Management

**POST** `/api/v1/chat/session`

Creates a new chat session.

- **Response**:
  ```json
  {
    "session_id": "new-session-id",
    "status": "created"
  }
  ```

**GET** `/api/v1/chat/session/{session_id}/history`

Retrieves the conversation history for a given session.

**DELETE** `/api/v1/chat/session/{session_id}`

Clears the memory for a given session.

### Health & Memory

**GET** `/api/v1/chat/health`

Returns the health status of the chat service.

**GET** `/api/v1/chat/memory/stats`

Returns statistics about the memory store.

**POST** `/api/v1/chat/memory/cleanup`

Cleans up expired memory entries.

## Interactive API Documentation

For a detailed, interactive API documentation, visit `http://localhost:8000/docs` after starting the server.
