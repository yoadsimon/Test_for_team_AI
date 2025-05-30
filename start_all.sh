#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Make scripts executable
chmod +x step1_video_highlight_extractor/run_step1.sh
chmod +x step2_Interactive_Chat/run_step2.sh

echo "🧹 Stopping any existing Step 2 services..."
cd step2_Interactive_Chat
docker compose down 2>/dev/null || true
cd ..

echo "🎬 Starting Step 1: Video Highlight Extractor..."
cd step1_video_highlight_extractor
./run_step1.sh
if [ $? -ne 0 ]; then
    echo "❌ Step 1 setup needs attention. Please check the messages above."
    exit 1
fi
cd ..

echo "💬 Starting Step 2: Interactive Chat..."
cd step2_Interactive_Chat
./run_step2.sh
if [ $? -ne 0 ]; then
    echo "❌ Step 2 setup needs attention. Please check the messages above."
    exit 1
fi

echo "✨ All services are running!"
echo "📊 Step 1: Video processing is running in the background"
echo "🌐 Step 2: Web interface is available at http://localhost:3000" 