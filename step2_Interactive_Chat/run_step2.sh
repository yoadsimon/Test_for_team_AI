#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if .env exists for backend
if [ ! -f backend/.env ]; then
    if [ -f backend/.env.example ]; then
        cp backend/.env.example backend/.env
        echo "Created backend/.env from .env.example"
        echo "Please configure your environment variables in backend/.env"
        exit 1
    else
        echo "Error: backend/.env.example not found"
        exit 1
    fi
fi

# Check if Step 1 database is running in the video-network
echo "Checking if Step 1 database is available..."
if ! docker network inspect video-network >/dev/null 2>&1; then
    echo "⚠️  Video network not found. Starting Step 1 first..."
    cd ../step1_video_highlight_extractor
    docker compose up db -d
    cd ../step2_Interactive_Chat
    echo "✅ Step 1 database started"
fi

# Stop any running Step 2 containers
echo "Cleaning up any existing containers..."
docker compose down

# Start the services
echo "Starting services..."
docker compose up -d

# Wait for database to be ready (connect via the shared network)
echo "Waiting for database to be ready..."
until docker compose exec backend python -c "
import psycopg2
try:
    conn = psycopg2.connect(host='db', port=5432, user='postgres', password='postgres', dbname='video_highlights')
    conn.close()
    print('Database ready')
except:
    exit(1)
" 2>/dev/null; do
    echo "Database is unavailable - sleeping"
    sleep 2
done

echo "✅ Database is ready!"

echo "🚀 Step 2 services are starting up!"
echo "⏳ Waiting for all services to be ready..."
sleep 5
echo "✨ You can now open http://localhost:3000 in your browser"
echo "📝 The API is available at http://localhost:8000" 