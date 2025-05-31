# Video Highlight Extractor

AI-powered video processing system with intelligent highlight extraction using LangChain.

## Features

### AI Processing
- **LangChain Integration**: Structured prompts, chains, and output parsing
- **Intelligent Filtering**: Only extracts meaningful highlights (quality threshold)
- **Context-Aware Analysis**: Maintains conversation memory for better continuity
- **Structured Output**: Pydantic models for reliable data extraction

### Performance Optimizations
- **Streamlined Architecture**: Removed unnecessary components
- **Batch Processing**: Efficient database operations and embedding generation
- **Parallel Processing**: Concurrent segment analysis
- **Smart Filtering**: Pre-filters segments before expensive LLM calls

### Data Management
- **PostgreSQL + pgvector**: Efficient vector storage and similarity search
- **Batch Operations**: Improved database performance
- **Comprehensive Logging**: Detailed processing insights
- **Error Resilience**: Graceful failure handling

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

3. **Add videos and run:**
   ```bash
   # Place videos in ./videos/ directory
   python src/demo.py
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

## Technology Stack

### Core Processing
- **Audio**: Faster-Whisper (transcription)
- **Video**: OpenCV, MoviePy
- **AI/LLM**: Google Gemini 1.5 Flash + LangChain

### LangChain Features
- **Structured Prompts**: PromptTemplate for consistent AI interactions
- **Smart Chains**: LLMChain for intelligent processing workflows
- **Output Parsing**: PydanticOutputParser for reliable data extraction
- **Memory Management**: ConversationBufferMemory for context awareness

### Infrastructure
- **Database**: PostgreSQL + pgvector (vector similarity search)
- **ORM**: SQLAlchemy with batch operations
- **Deployment**: Docker + Docker Compose

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

## Smart Filtering Process

### 1. Segment Pre-filtering
- Removes segments < 10 characters or < 2 seconds
- Filters out filler words and noise
- Calculates meaningful content ratio

### 2. LLM Quality Assessment
- Each segment evaluated for significance
- Importance scoring (1-10 scale)
- Category classification (action, dialogue, key_moment, etc.)
- Only highlights scoring ≥6 are saved

### 3. Batch Processing
- Parallel segment analysis (4 workers)
- Batch embedding generation
- Optimized database operations

## Configuration

### Environment Variables
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

### Smart Filtering Settings
```python
# Minimum segment duration (seconds)
MIN_SEGMENT_DURATION = 2.0

# Minimum text length (characters)
MIN_TEXT_LENGTH = 10

# Quality threshold for highlights (1-10)
QUALITY_THRESHOLD = 6

# Maximum filler word ratio
MAX_FILLER_RATIO = 0.7
```

## Example Output

```
Starting Video Highlight Extractor
Initializing database...
Database ready
Processing video 1/1: presentation.mp4

Processing video: presentation.mp4
Found 15 meaningful segments from 23 total
Processing 15 segments with AI filtering...
Progress: 15/15 segments processed (100.0%) - 8 highlights found
Generated 8 quality highlights from 15 segments
Batch saving 8 highlights...
Successfully saved 8 highlights to database

Video processing complete
Video: presentation.mp4
Duration: 180.5s
Highlights found: 8
Processing time: 45.2s
Summary: Professional presentation covering key product features and implementation strategy.

Top highlights:
  1. 00:02:15.50
     The presenter introduces the new product features with enthusiasm.
     Product introduction with key feature overview.

  2. 00:05:42.30
     Detailed explanation of the implementation timeline and resource requirements.
     Implementation strategy and timeline discussion.