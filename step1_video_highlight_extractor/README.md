# Video Highlight Extractor

Extracts highlights from videos using LLM and stores them in PostgreSQL with pgvector.

## Features

- Video processing (.mp4, .mov)
- Visual scene analysis
- Audio transcription
- LLM-based highlight extraction
- PostgreSQL + pgvector storage
- Docker containerization

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Google AI Studio API key

## Setup

1. Copy environment file:
   ```bash
   cp .env.example .env
   ```

2. Add your Google AI Studio API key to `.env`:
   ```
   GOOGLE_AI_STUDIO_API_KEY=your_key_here
   ```

## Usage

### Using Docker (Recommended)

1. Start services:
   ```bash
   docker compose up -d
   ```

2. Run demo:
   ```bash
   ./run_demo.sh
   ```

### Local Development

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Start service:
   ```bash
   python src/main.py
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
├── output/              # Processed outputs
├── migrations/          # Database migrations
├── tests/              # Test files
└── docker-compose.yml  # Docker configuration
```

## Testing

Run tests:
```bash
pytest tests/
```

## API

The service exposes no external API endpoints as it's designed to process videos and store results in the database for use by the chat interface.

## 📊 Database

```sql
CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    duration FLOAT,
    created_at TIMESTAMP
);

CREATE TABLE highlights (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    timestamp FLOAT,
    description TEXT,
    embedding vector(1536),
    summary TEXT
);
```

## What I Could Have Improved:
- Clearer Goal Understanding: Knowing the end use of the highlights would have helped craft more relevant descriptions.

- Better Scene Detection: Using visual and audio cues (e.g., frame changes, volume shifts) to segment scenes more accurately.

- Faster Processing: Parallelizing highlight processing to improve performance.

- Contextual Summarization: Including previous highlight summaries for better continuity and coherence (if relevant to the task goals).