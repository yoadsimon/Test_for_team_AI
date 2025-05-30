# 🎥 Video Highlight Extractor

AI-powered video processing system that extracts and stores meaningful highlights.

## ✨ Features
- Processes MP4/MOV videos
- Extracts visual scenes and audio
- Uses LLM for highlight detection
- Stores in PostgreSQL + pgvector

## 🚀 Quick Start

1. Set up environment:
   ```bash
   cp .env.example .env
   # Add your Google AI Studio API key to .env
   ```

2. Start services:
   ```bash
   docker compose up -d
   ```

## 📁 Project Structure
```
.
├── src/              # Source code
│   ├── processors/   # Video/audio processing
│   ├── llm/         # LLM integration
│   ├── database/    # Database models
│   └── services/    # Business logic
├── videos/          # Input videos
└── processed_media/ # Generated files
```

## 💾 Database Schema
```sql
-- Videos table
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    duration FLOAT
);

-- Highlights table
CREATE TABLE highlights (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    timestamp FLOAT,
    description TEXT,
    embedding vector(1536)
);
```

## Project Structure

```
.
├── src/                    # Source code
│   ├── processors/        # Video and audio processing
│   ├── llm/              # LLM integration
│   ├── database/         # Database models and operations
│   └── services/         # Business logic
├── videos/               # Input videos
├── processed_media/              # Processed media files and metadata
├── migrations/          # Database migrations
├── tests/              # Test files
└── docker-compose.yml  # Docker configuration
```

## What I Could Have Improved:
- Clearer Goal Understanding: Knowing the end use of the highlights would have helped craft more relevant descriptions.

- Better Scene Detection: Using visual and audio cues (e.g., frame changes, volume shifts) to segment scenes more accurately.

- Faster Processing: Parallelizing highlight processing to improve performance.

- Contextual Summarization: Including previous highlight summaries for better continuity and coherence (if relevant to the task goals).