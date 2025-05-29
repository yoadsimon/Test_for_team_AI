# 📹 Step 1: Video Processor with LLM-Based Highlight Extraction

## 📁 Structure

```
src/
├── processors/    # Video/audio processing
├── database/     # Database models
├── llm/         # Gemini AI
├── services/    # Business logic
└── utils/       # Helpers
```

## 📝 Setup

1. Copy `.env.example` to `.env`
2. Add your Google AI key (get free key at https://aistudio.google.com/)


## 🚀 Quick Start

1. Add your videos to the `videos/` directory (.mp4 or .mov)
2. Make the script executable:
```bash
chmod +x run_demo.sh
```
3. Run the demo script:
```bash
./run_demo.sh
```

The script will:
- Create `.env` if missing
- Clean up any existing containers
- Start fresh database with pgvector
- Initialize database tables
- Process all videos
- Show how to view results

Note: The database is automatically initialized with required extensions and tables.

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