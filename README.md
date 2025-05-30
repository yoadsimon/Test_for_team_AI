# Video Highlight Extraction & Chat System

A two-part system that processes videos to extract highlights and provides a chat interface to query those highlights.

## 🎥 Step 1: Video Processor
Extracts meaningful highlights from videos using AI:
- Processes MP4/MOV videos
- Uses LLM for highlight extraction
- Stores results in PostgreSQL + pgvector

## 💬 Step 2: Chat Interface
Interactive system to query video highlights:
- React frontend
- FastAPI backend
- Natural language queries
- Semantic search

## Project Structure
```
.
├── step1_video_highlight_extractor/  # Video processing service
└── step2_Interactive_Chat/           # Chat interface
```

## Quick Start

1. Set up your environment:
   - Copy `.env.example` to `.env` in both directories:
     ```bash
     cp step1_video_highlight_extractor/.env.example step1_video_highlight_extractor/.env
     cp step2_Interactive_Chat/.env.example step2_Interactive_Chat/.env
     ```
   - Update the `.env` files with your Google AI Studio API key and any other required configurations

2. Run the entire system:
   ```bash
   chmod +x start_all.sh  
   ./start_all.sh        
   ```

The script will:
- Start the video processor (Step 1)
- Process any videos in the `step1_video_highlight_extractor/videos` directory
- Start the chat interface (Step 2)
- Make the web interface available at http://localhost:3000

## Manual Start (Alternative)
If you prefer to start services individually:

1. Start Video Processor:
```bash
cd step1_video_highlight_extractor
docker compose up -d
```

2. Start Chat Interface:
```bash
cd step2_Interactive_Chat
docker compose up -d
```

## Documentation
- [Video Processor Documentation](step1_video_highlight_extractor/README.md)
- [Chat Interface Documentation](step2_Interactive_Chat/README.md)

## Requirements
- Docker & Docker Compose
- Google AI Studio API key