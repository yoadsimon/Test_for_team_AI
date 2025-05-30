#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

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
    mkdir -p videos
    echo "Created videos directory"
    echo "Please add your video files (30sec - 1.5min) to the videos directory"
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
docker compose down -v

# Start the services
echo "Starting services..."
docker compose up -d

# Wait for database to be ready
echo "Waiting for database to be ready..."
until docker compose exec db pg_isready -U postgres; do
    echo "Database is unavailable - sleeping"
    sleep 1
done

# Initialize database
echo "Initializing database..."
docker compose exec app python migrations/migrate.py

echo "Processing videos..."
# Run the app container and wait for it to complete
docker compose up app --exit-code-from app

# The container exit code 0 means success
echo "Video processing completed successfully!"
echo "View results with:"
echo "docker compose exec db psql -U postgres -d video_highlights -c \"SELECT * FROM highlights;\"" 