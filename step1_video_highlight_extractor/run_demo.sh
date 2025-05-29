#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Parse command line arguments
IS_PROD=false
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --prod) IS_PROD=true ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Set environment-specific variables
if [ "$IS_PROD" = true ]; then
    COMPOSE_FILE="docker-compose.yml"
    DB_NAME="video_highlights"
    SERVICE_NAME="app"
else
    COMPOSE_FILE="docker-compose.dev.yml"
    DB_NAME="video_highlights_test"
    SERVICE_NAME="dev"
fi

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Created .env from .env.example"
        echo "Please edit .env and add your Google AI key"
        exit 1
    else
        echo "Error: .env.example not found"
        exit 1
    fi
fi

# Check if videos directory exists and has videos
if [ ! -d "videos" ]; then
    echo "Error: videos directory not found"
    exit 1
fi

VIDEO_COUNT=$(ls videos/*.{mp4,mov,MOV,MP4} 2>/dev/null | wc -l)
if [ "$VIDEO_COUNT" -eq 0 ]; then
    echo "Error: No videos found in videos directory"
    echo "Please add .mp4 or .mov files to the videos directory"
    exit 1
fi

# Stop any running containers and remove volumes
echo "Cleaning up any existing containers..."
docker compose -f "$COMPOSE_FILE" down -v

# Start the environment
echo "Starting environment ($([ "$IS_PROD" = true ] && echo "production" || echo "development"))..."
docker compose -f "$COMPOSE_FILE" up -d

# Wait for database to be ready
echo "Waiting for database to be ready..."
until docker compose -f "$COMPOSE_FILE" exec db pg_isready -U postgres; do
    echo "Database is unavailable - sleeping"
    sleep 1
done

# Initialize database
echo "Initializing database..."
docker compose -f "$COMPOSE_FILE" exec "$SERVICE_NAME" python migrations/migrate.py

if [ "$IS_PROD" = true ]; then
    echo "Processing videos in production mode..."
    # In production, the app service automatically processes all non-demo videos
    echo "Waiting for video processing to complete..."
    docker compose -f "$COMPOSE_FILE" logs -f "$SERVICE_NAME"
else
    echo "Processing demo video..."
    # In development, process only the demo video
    docker compose -f "$COMPOSE_FILE" exec "$SERVICE_NAME" python src/demo.py --video videos/demo_v2.MOV
fi

echo "Done! View results with:"
echo "docker compose -f $COMPOSE_FILE exec db psql -U postgres -d $DB_NAME -c \"SELECT * FROM highlights;\"" 