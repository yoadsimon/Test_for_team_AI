# Interactive Chat Interface

A web interface for asking questions about video highlights, powered by FastAPI and React.

## Features

- React frontend with modern UI
- FastAPI backend
- Semantic search using pgvector
- Real-time responses
- Docker containerization

## Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local backend)
- Node.js 16+ (for local frontend)

## Setup

1. Copy environment files:
   ```bash
   # Backend
   cp backend/.env.example backend/.env
   
   # Frontend
   cp frontend/.env.example frontend/.env
   ```

## Usage

### Using Docker (Recommended)

Start all services:
```bash
docker compose up -d
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Local Development

1. Backend (FastAPI):
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. Frontend (React):
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Project Structure

```
.
├── backend/                # FastAPI backend
│   ├── app/              # Application code
│   │   ├── api/         # API endpoints
│   │   ├── models/      # Database models
│   │   └── services/    # Business logic
│   └── Dockerfile       # Backend container
└── frontend/             # React frontend
    ├── src/             # Source code
    │   ├── components/  # React components
    │   ├── services/    # API services
    │   └── styles/      # CSS styles
    └── Dockerfile       # Frontend container
```

## API Endpoints

### Chat API
- `POST /api/chat/question`
  - Request: `{ "text": "string" }`
  - Response: `[{ "text": "string", "timestamp": float, "similarity_score": float }]`

## Testing

Run backend tests:
```bash
cd backend
pytest
```

Run frontend tests:
```bash
cd frontend
npm test
``` 