# Interactive Video Chat

Chat interface for querying video highlights using natural language.

## Features
- Natural language queries
- Semantic search
- React frontend
- FastAPI backend

## Quick Start

1. Start services:
   ```bash
   docker compose up -d
   ```

2. Access:
   - Web UI: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## Chat Architecture

The chat system follows a simple but effective flow:

1. **User Input**: User enters a natural language question in the React frontend (e.g., "is there a man in any of the video?")
2. **Frontend Processing**: React Chat component captures the input and sends a POST request to the backend API
3. **Backend Processing**: 
   - FastAPI receives the question through the `/api/chat/question` endpoint
   - ChatService processes the question by generating embeddings using Google's embedding model
   - Semantic search is performed against the database using pgvector for cosine similarity
   - Relevant highlights are retrieved and ranked by similarity score
4. **Response**: Backend returns a list of relevant video highlights with metadata
5. **Display**: Frontend displays the highlight descriptions with timestamps and similarity scores

## Endpoint Flow

### POST `/api/chat/question`
**Purpose**: Submit a question about video highlights and receive relevant responses

**Request Body**:
```json
{
  "text": "string"
}
```

**Response**:
```json
[
  {
    "id": "integer",
    "description": "string",
    "timestamp": "float",
    "similarity_score": "float"
  }
]
```

**Field Descriptions**:
- `description`: Contains the full description of the highlight (what the UI displays)
- `timestamp`: Video timestamp when the highlight occurs
- `similarity_score`: Relevance score (0-1) for the search query

**Example Usage**:
```bash
curl -X POST "http://localhost:8000/api/chat/question" \
  -H "Content-Type: application/json" \
  -d '{"text": "is there a man in the video?"}'
```

### GET `/health`
**Purpose**: Health check endpoint for monitoring service status

**Response**:
```json
{
  "status": "healthy"
}
```

## Project Structure
```
.
├── frontend/        # React application
│   ├── src/        # Frontend source
│   └── Dockerfile  # Frontend container
└── backend/        # FastAPI service
    ├── app/        # Backend source
    └── Dockerfile  # Backend container
```
