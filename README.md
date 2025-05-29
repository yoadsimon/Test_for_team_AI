# Video Highlights System

A two-step system for processing videos and enabling interactive chat about their highlights.

## Overview

This project consists of two main components:

1. **Video Processor (Step 1)**: Processes videos to extract highlights using LLM
2. **Interactive Chat (Step 2)**: Allows users to ask questions about video highlights

## Architecture

```
.
├── step1_video_highlight_extractor/    # Video processing service
│   ├── src/                           # Python source code
│   │   ├── processors/                # Video and audio processing
│   │   ├── llm/                       # LLM integration
│   │   ├── database/                  # Database models and operations
│   │   └── services/                  # Business logic
│   ├── videos/                        # Input videos
│   ├── output/                        # Processed outputs
│   └── docker-compose.yml            # Docker setup
│
└── step2_Interactive_Chat/            # Chat interface
    ├── backend/                       # FastAPI backend
    │   ├── app/                      # Application code
    │   │   ├── api/                  # API endpoints
    │   │   ├── models/               # Database models
    │   │   └── services/             # Business logic
    │   └── Dockerfile               # Backend container
    └── frontend/                      # React frontend
        ├── src/                      # Source code
        └── Dockerfile               # Frontend container
```

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Node.js 16+ (for local frontend development)
- Google AI Studio API key

## Quick Start

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd video-highlights-system
   ```

2. Set up environment variables:
   ```bash
   # Step 1
   cp step1_video_highlight_extractor/.env.example step1_video_highlight_extractor/.env
   # Edit .env and add your Google AI Studio API key
   
   # Step 2
   cp step2_Interactive_Chat/backend/.env.example step2_Interactive_Chat/backend/.env
   ```

3. Run the test script to verify everything works:
   ```bash
   ./test_flow.sh
   ```

## Step 1: Video Processor

Processes videos to extract highlights using LLM and stores them in PostgreSQL.

### Features
- Video file processing (.mp4, .mov)
- Visual and audio analysis
- LLM-based highlight extraction
- PostgreSQL + pgvector storage

### Running Step 1
```bash
cd step1_video_highlight_extractor
docker compose up -d
./run_demo.sh
```

## Step 2: Interactive Chat

Provides a web interface for asking questions about video highlights.

### Features
- React frontend
- FastAPI backend
- Semantic search using embeddings
- Real-time responses

### Running Step 2
```bash
cd step2_Interactive_Chat
docker compose up -d
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Endpoints

### Chat API
- `POST /api/chat/question`
  - Request: `{ "text": "string" }`
  - Response: `[{ "text": "string", "timestamp": float, "similarity_score": float }]`

## Development

### Local Development
1. Backend (FastAPI):
   ```bash
   cd step2_Interactive_Chat/backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. Frontend (React):
   ```bash
   cd step2_Interactive_Chat/frontend
   npm install
   npm start
   ```

### Testing
Run the test script to verify the entire system:
```bash
./test_flow.sh
```

## License

MIT License

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request 