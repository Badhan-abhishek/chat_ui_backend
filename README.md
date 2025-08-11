# Gemini Streaming Chatbot

FastAPI streaming chatbot using Google Gemini.

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

## API

**POST** `/api/v1/chat/stream` - Streaming chat endpoint
```json
{
  "message": "Hello",
  "conversation_history": []
}
```

Response format:
```
{"type": "chunk", "content": "Hello"}
{"type": "chunk", "content": " there!"}
{"type": "complete", "full_response": "Hello there!", "message_count": 2}
```

**GET** `/api/v1/chat/health` - Health check

Visit `http://localhost:8000/docs` for API documentation.