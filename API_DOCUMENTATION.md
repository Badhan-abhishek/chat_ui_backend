# Gemini Chatbot API - Complete Documentation

## Overview
A streaming chatbot API powered by Google's Gemini AI model with real-time streaming responses, conversation history support, intelligent code generation, and short-term memory management.

## Features
- Real-time streaming chat responses
- Session-based conversation memory
- Automatic code generation for programming questions
- Conversation history persistence
- Memory management and cleanup
- Health monitoring endpoints

## Base URLs
- **Development**: `http://localhost:8000`
- **Production**: Update as needed

## Authentication
No authentication required for current endpoints.

## Rate Limiting
No rate limiting currently implemented.

---

## API Endpoints

### Health Check Endpoints

#### Root Health Check
```http
GET /
```

**Response:**
```json
{
  "message": "Gemini Chatbot is ready"
}
```

#### Chat Service Health Check
```http
GET /api/v1/chat/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "gemini-chat-with-memory"
}
```

---

### Chat Endpoints

#### Stream Chat with Memory
```http
POST /api/v1/chat/stream
```

Send a message to the Gemini AI and receive a streaming response with automatic memory persistence.

**Request Body:**
```json
{
  "message": "Hello, how are you?",
  "conversation_history": [
    {
      "role": "user",
      "content": "Previous message"
    },
    {
      "role": "assistant", 
      "content": "Previous response"
    }
  ],
  "session_id": "optional-session-id"
}
```

**Parameters:**
- `message` (string, required): The user's message (1-10,000 characters)
- `conversation_history` (array, optional): Previous messages in conversation (max 100 items)
- `session_id` (string, optional): Session ID for memory persistence (auto-generated if not provided)

**Response Headers:**
- `X-Session-ID`: The session ID used for memory storage

**Streaming Response Format:**
The response is streamed as newline-delimited JSON objects:

**Chunk Response:**
```json
{"type": "chunk", "content": "partial text here"}
```

**Complete Response:**
```json
{
  "type": "complete", 
  "full_response": "complete response text",
  "message_count": 4
}
```

**Error Response:**
```json
{"type": "error", "content": "error message"}
```

**Tool Call Response (Code Generation):**
```json
{
  "type": "tool_call",
  "tool_name": "code_generator",
  "description": "Simple interactive button with HTML, CSS, and JavaScript",
  "files": [
    {
      "filename": "index.html",
      "content": "<!DOCTYPE html><html>...",
      "language": "html"
    },
    {
      "filename": "style.css",
      "content": "button { padding: 10px; }",
      "language": "css"
    }
  ]
}
```

#### Direct Code Generation
```http
POST /api/v1/chat/generate-code
```

Generate code files directly without streaming.

**Request Body:**
```json
{
  "prompt": "Create a simple button with HTML, CSS, and JavaScript"
}
```

**Response:**
```json
{
  "description": "Simple interactive button with HTML, CSS, and JavaScript",
  "files": [
    {
      "filename": "index.html",
      "language": "html",
      "content": "<!DOCTYPE html><html>..."
    },
    {
      "filename": "style.css",
      "language": "css", 
      "content": "button { padding: 10px; }"
    },
    {
      "filename": "script.js",
      "language": "javascript",
      "content": "document.querySelector('button')..."
    }
  ]
}
```

---

### Memory Management Endpoints

#### Create Chat Session
```http
POST /api/v1/chat/session
```

Create a new chat session with memory.

**Response:**
```json
{
  "session_id": "uuid-string",
  "status": "created"
}
```

#### Get Session History
```http
GET /api/v1/chat/session/{session_id}/history
```

Retrieve conversation history for a session.

**Response:**
```json
{
  "session_id": "uuid-string",
  "history": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hi there!"
    }
  ]
}
```

#### Clear Session Memory
```http
DELETE /api/v1/chat/session/{session_id}
```

Clear all memory for a specific session.

**Response:**
```json
{
  "session_id": "uuid-string",
  "status": "cleared"
}
```

#### Memory Statistics
```http
GET /api/v1/chat/memory/stats
```

Get memory store statistics.

**Response:**
```json
{
  "active_sessions": 5,
  "total_entries": 23,
  "sessions": {
    "session-1": 4,
    "session-2": 6,
    "session-3": 13
  }
}
```

#### Cleanup Expired Memory
```http
POST /api/v1/chat/memory/cleanup
```

Clean up expired memory entries.

**Response:**
```json
{
  "cleaned_entries": 12,
  "status": "completed"
}
```

---

## Data Models

### ChatMessage
```json
{
  "role": "user" | "assistant",
  "content": "string"
}
```

### ChatRequest
```json
{
  "message": "string (1-10000 chars)",
  "conversation_history": "ChatMessage[] (max 100 items)",
  "session_id": "string (optional)"
}
```

### CodeFile
```json
{
  "filename": "string",
  "content": "string", 
  "language": "html|css|javascript|python|typescript|jsx|tsx|json|yaml|markdown|text"
}
```

### CodeGenerationResponse
```json
{
  "description": "string",
  "files": "CodeFile[] (1-10 items)"
}
```

### ErrorResponse
```json
{
  "detail": "string"
}
```

---

## Frontend Integration

### JavaScript/TypeScript Implementation

#### Basic Streaming Chat
```javascript
async function streamChat(message, conversationHistory = [], sessionId = null) {
  const response = await fetch('/api/v1/chat/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      conversation_history: conversationHistory,
      session_id: sessionId
    })
  });

  // Get session ID from response headers
  const responseSessionId = response.headers.get('X-Session-ID');

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\\n').filter(line => line.trim());
    
    for (const line of lines) {
      try {
        const data = JSON.parse(line);
        
        switch (data.type) {
          case 'chunk':
            appendToChat(data.content);
            break;
          case 'tool_call':
            if (data.tool_name === 'code_generator') {
              displayGeneratedCode(data.description, data.files);
            }
            break;
          case 'complete':
            onChatComplete(data.full_response, data.message_count);
            break;
          case 'error':
            onChatError(data.content);
            break;
        }
      } catch (e) {
        console.error('Failed to parse JSON:', line);
      }
    }
  }

  return responseSessionId;
}
```

#### React Hook for Streaming Chat
```typescript
import { useState, useCallback } from 'react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

interface GeneratedFile {
  filename: string;
  content: string;
  language: string;
}

export function useStreamingChat() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [sessionId, setSessionId] = useState<string | null>(null);

  const streamChat = useCallback(async (
    message: string, 
    conversationHistory: ChatMessage[] = []
  ) => {
    setIsStreaming(true);
    setCurrentResponse('');

    try {
      const response = await fetch('/api/v1/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message,
          conversation_history: conversationHistory,
          session_id: sessionId
        })
      });

      // Update session ID from response
      const responseSessionId = response.headers.get('X-Session-ID');
      if (responseSessionId) {
        setSessionId(responseSessionId);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            
            if (data.type === 'chunk') {
              setCurrentResponse(prev => prev + data.content);
            } else if (data.type === 'tool_call') {
              if (data.tool_name === 'code_generator') {
                onCodeGenerated?.(data.description, data.files);
              }
            } else if (data.type === 'complete') {
              setCurrentResponse(data.full_response);
              setIsStreaming(false);
              return data.full_response;
            } else if (data.type === 'error') {
              throw new Error(data.content);
            }
          } catch (e) {
            console.error('Parse error:', e);
          }
        }
      }
    } catch (error) {
      setIsStreaming(false);
      throw error;
    }
  }, [sessionId]);

  const createNewSession = useCallback(async () => {
    const response = await fetch('/api/v1/chat/session', {
      method: 'POST'
    });
    const data = await response.json();
    setSessionId(data.session_id);
    return data.session_id;
  }, []);

  const clearSession = useCallback(async () => {
    if (sessionId) {
      await fetch(`/api/v1/chat/session/${sessionId}`, {
        method: 'DELETE'
      });
      setSessionId(null);
    }
  }, [sessionId]);

  return {
    streamChat,
    isStreaming,
    currentResponse,
    sessionId,
    createNewSession,
    clearSession,
    resetResponse: () => setCurrentResponse('')
  };
}
```

#### Memory Management Functions
```javascript
// Create a new session
async function createSession() {
  const response = await fetch('/api/v1/chat/session', {
    method: 'POST'
  });
  const data = await response.json();
  return data.session_id;
}

// Get session history
async function getSessionHistory(sessionId) {
  const response = await fetch(`/api/v1/chat/session/${sessionId}/history`);
  if (!response.ok) {
    throw new Error('Session not found or expired');
  }
  const data = await response.json();
  return data.history;
}

// Clear session
async function clearSession(sessionId) {
  const response = await fetch(`/api/v1/chat/session/${sessionId}`, {
    method: 'DELETE'
  });
  return response.ok;
}

// Get memory stats
async function getMemoryStats() {
  const response = await fetch('/api/v1/chat/memory/stats');
  return response.json();
}

// Cleanup expired memory
async function cleanupMemory() {
  const response = await fetch('/api/v1/chat/memory/cleanup', {
    method: 'POST'
  });
  return response.json();
}
```

#### Code Generation Display
```javascript
function displayGeneratedCode(description, files) {
  const codeContainer = document.createElement('div');
  codeContainer.className = 'generated-code';
  
  // Add description
  const descriptionEl = document.createElement('h3');
  descriptionEl.textContent = `🔧 ${description}`;
  codeContainer.appendChild(descriptionEl);
  
  // Add each file
  files.forEach(file => {
    const fileContainer = document.createElement('div');
    fileContainer.className = 'code-file';
    
    fileContainer.innerHTML = `
      <div class="file-header">
        <span class="filename">📄 ${file.filename}</span>
        <span class="language">${file.language}</span>
        <button onclick="copyToClipboard('${file.content.replace(/'/g, "\\\\'")}')">Copy</button>
        <button onclick="downloadFile('${file.filename}', '${file.content.replace(/'/g, "\\\\'")}')">Download</button>
      </div>
      <pre><code class="language-${file.language}">${escapeHtml(file.content)}</code></pre>
    `;
    
    codeContainer.appendChild(fileContainer);
  });
  
  document.getElementById('chat-messages').appendChild(codeContainer);
}

function copyToClipboard(content) {
  navigator.clipboard.writeText(content);
}

function downloadFile(filename, content) {
  const blob = new Blob([content], { type: 'text/plain' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
```

---

## Memory System

### How Memory Works
- **Session-based**: Each chat session has isolated memory
- **Automatic TTL**: Entries expire after 1 hour (conversation history) or 30 minutes (interactions)
- **Thread-safe**: Concurrent access is handled safely
- **Auto-cleanup**: Expired entries are automatically removed

### Memory Storage
- **Conversation History**: Full conversation stored per session
- **Last Interaction**: Most recent user message cached
- **Custom Data**: Store any additional session data

### Memory Lifecycle
1. Session created (auto or manual)
2. Data stored with TTL
3. Data retrieved on subsequent requests
4. Expired data automatically cleaned up
5. Empty sessions removed

---

## Code Generation

### Automatic Detection
The system automatically detects programming questions based on:

**Keywords**: create, build, make, write, generate, code, html, css, javascript, python, react, component, function, class, api, database, etc.

**Patterns**: 
- "create a button"
- "build an app" 
- "show me code"
- "write a function"
- "make a component"

**Examples that trigger code generation:**
- "Create a simple HTML button"
- "Build a React component for user login"
- "Make a Python function to calculate fibonacci"
- "Show me a CSS grid layout"
- "Write a REST API endpoint"

### Supported Languages
- HTML, CSS, JavaScript
- Python, TypeScript
- React (JSX/TSX)
- JSON, YAML, Markdown
- And more...

---

## Error Handling

### HTTP Status Codes
- `200`: Success
- `400`: Bad request (validation error)
- `404`: Resource not found (session)
- `500`: Internal server error

### Error Response Format
```json
{
  "detail": "Error message describing the issue"
}
```

### Common Errors
- **Session not found**: Session expired or doesn't exist
- **Validation error**: Invalid request format or parameters
- **API key error**: GEMINI_API_KEY not configured
- **Rate limiting**: Too many requests (if implemented)

---

## Testing Examples

### Health Check
```bash
curl http://localhost:8000/api/v1/chat/health
```

### Simple Chat
```bash
curl -X POST http://localhost:8000/api/v1/chat/stream \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Hello!"}'
```

### Chat with Session
```bash
curl -X POST http://localhost:8000/api/v1/chat/stream \\
  -H "Content-Type: application/json" \\
  -d '{
    "message": "What did we talk about?",
    "session_id": "your-session-id"
  }'
```

### Code Generation
```bash
curl -X POST http://localhost:8000/api/v1/chat/stream \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Create a simple HTML button"}'
```

### Direct Code Generation
```bash
curl -X POST http://localhost:8000/api/v1/chat/generate-code \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Create a Python function to sort a list"}'
```

### Memory Management
```bash
# Create session
curl -X POST http://localhost:8000/api/v1/chat/session

# Get session history
curl http://localhost:8000/api/v1/chat/session/{session_id}/history

# Clear session
curl -X DELETE http://localhost:8000/api/v1/chat/session/{session_id}

# Memory stats
curl http://localhost:8000/api/v1/chat/memory/stats

# Cleanup expired
curl -X POST http://localhost:8000/api/v1/chat/memory/cleanup
```

---

## Environment Setup

### Required Environment Variables
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Optional Configuration
- Memory TTL can be configured in the InMemoryStore constructor
- Default conversation history TTL: 3600 seconds (1 hour)
- Default interaction TTL: 1800 seconds (30 minutes)

---

## Best Practices

### Frontend Development
1. **Handle Connection Errors**: Always wrap streaming calls in try-catch blocks
2. **Manage State**: Track streaming state to prevent multiple concurrent requests
3. **Parse Safely**: Always validate JSON parsing of streaming chunks
4. **User Feedback**: Show loading states during streaming
5. **Session Management**: Store session IDs for memory persistence
6. **Rate Limiting**: Implement client-side rate limiting to prevent spam

### Memory Management
1. **Session Lifecycle**: Create sessions explicitly for better control
2. **Cleanup**: Periodically call cleanup endpoint in production
3. **Monitoring**: Use stats endpoint to monitor memory usage
4. **Error Handling**: Handle session expiration gracefully

### Performance
1. **Connection Reuse**: Reuse HTTP connections when possible
2. **Chunked Processing**: Process streaming chunks incrementally
3. **Memory Monitoring**: Monitor memory usage in production
4. **Cleanup Scheduling**: Schedule regular memory cleanup

---

## OpenAPI Specification

This API follows OpenAPI 3.0.3 specification. The complete schema includes:

- **Info**: API metadata and versioning
- **Servers**: Development and production endpoints  
- **Paths**: All endpoint definitions with parameters and responses
- **Components**: Reusable schemas and models
- **Security**: Authentication schemes (none currently)
- **Tags**: Endpoint categorization

For machine-readable API specification, refer to the generated OpenAPI JSON/YAML files.

---

## Support and Resources

- **Gemini AI Documentation**: https://ai.google.dev/gemini-api
- **API Version**: 1.0.0
- **License**: MIT
- **Contact**: API Support Team

---

*This documentation covers the complete Gemini Chatbot API with memory management, code generation, and streaming capabilities. For additional support or feature requests, please contact the development team.*