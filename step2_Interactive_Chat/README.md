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
