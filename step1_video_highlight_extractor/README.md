# Video Highlight Extractor

AI-powered video processing system with intelligent highlight extraction using LangChain.


## Architecture

```
INPUT VIDEO
     ↓
Audio Extraction & Transcription (Whisper)
     ↓
Smart Segment Filtering
     ↓
LangChain AI Analysis (Parallel)
     ↓
Quality Highlight Generation
     ↓
Batch Embedding & Storage
```

## Quick Start

1. **Set up environment:**
   ```bash
   cp .env.example .env
   # Add your Google AI Studio API key to .env
   ```

2. **Start services:**
   ```bash
   docker compose up -d
   ```

## Project Structure
```
.
├── src/                    # Source code
│   ├── processors/        # Video/audio processing
│   ├── llm/              # LangChain integration
│   ├── database/         # Database models and batch operations
│   └── services/         # Business logic
├── videos/               # Input videos
├── processed_media/      # Processed files
└── docker-compose.yml    # Docker configuration
```

## Database Schema

```sql
-- Videos table
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    duration FLOAT,
    width INTEGER,
    height INTEGER,
    fps FLOAT,
    summary TEXT,
    created_at TIMESTAMP
);

-- Highlights table with vector embeddings
CREATE TABLE highlights (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    timestamp FLOAT,
    description TEXT,
    summary TEXT,
    embedding vector(768),  -- For similarity search
    created_at TIMESTAMP
);
```

## Environment Variables
```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=video_highlights

# AI
GOOGLE_API_KEY=your_google_ai_studio_key
```
