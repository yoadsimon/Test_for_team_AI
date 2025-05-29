#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check dependencies
check_dependencies() {
    local missing_deps=()
    
    # Check for docker
    if ! command -v docker &> /dev/null; then
        missing_deps+=("docker")
    fi
    
    # Check for docker compose
    if ! command -v docker compose &> /dev/null; then
        missing_deps+=("docker compose")
    fi
    
    # Check for curl
    if ! command -v curl &> /dev/null; then
        missing_deps+=("curl")
    fi
    
    # Check for jq
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        echo -e "${RED}[✗] Missing required dependencies:${NC}"
        for dep in "${missing_deps[@]}"; do
            echo "  - $dep"
        done
        exit 1
    fi
    
    echo -e "${GREEN}[✓] All dependencies are installed${NC}"
}

# Function to print colored output
print_status() {
    echo -e "${2}[*] $1${NC}"
}

# Function to print stage
print_stage() {
    local stage=$1
    local stage_name=$2
    echo -e "\n${BLUE}=== Stage: $stage_name ===${NC}"
}

# Function to check if a command succeeded
check_status() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] $1${NC}"
    else
        echo -e "${RED}[✗] $1${NC}"
        exit 1
    fi
}

# Function to wait for a service to be ready
wait_for_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1

    print_status "Waiting for $service to be ready..." "${YELLOW}"
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" > /dev/null; then
            echo -e "${GREEN}[✓] $service is ready!${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo -e "${RED}[✗] $service failed to start within timeout${NC}"
    return 1
}

# Function to test chat functionality
test_chat() {
    local question="What is the last thing shown in the video?"
    print_status "Testing chat functionality with question: '$question'" "${YELLOW}"
    
    # Send question to chat API
    response=$(curl -s -X POST "http://localhost:8000/api/chat/question" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"$question\"}")
    
    # Check if we got a valid response
    if echo "$response" | jq -e . >/dev/null 2>&1; then
        # Check if we got any highlights
        if echo "$response" | jq -e 'length > 0' >/dev/null 2>&1; then
            local count=$(echo "$response" | jq '. | length')
            echo -e "${GREEN}[✓] Chat test passed! Found $count highlights:${NC}"
            echo "$response" | jq -r '.[] | "  - \(.text) (Score: \(.similarity_score))"'
        else
            echo -e "${YELLOW}[!] Chat test passed but no highlights found${NC}"
        fi
    else
        echo -e "${RED}[✗] Chat test failed - Invalid response${NC}"
        echo "Response: $response"
        return 1
    fi
}

# Main test flow
echo -e "\n${YELLOW}=== Starting Video Highlights System Test ===${NC}\n"

# Check dependencies first
print_stage "deps" "Checking Dependencies"
check_dependencies

# Step 1: Check if Docker is running
print_stage "docker" "Checking Docker Status"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}[✗] Docker is not running${NC}"
    exit 1
fi
check_status "Docker is running"

# Step 2: Start Step 1 services (Video Processor)
print_stage "step1" "Starting Step 1 Services"
cd step1_video_highlight_extractor
docker compose up -d
check_status "Step 1 services started"

# Wait for PostgreSQL to be ready
print_stage "postgres" "Waiting for PostgreSQL"
wait_for_service "PostgreSQL" "postgresql://postgres:postgres@localhost:5432/video_highlights_test"

# Step 3: Run video processing demo
print_stage "process" "Running Video Processing"
./run_demo.sh
check_status "Video processing completed"

# Step 4: Start Step 2 services (Chat)
print_stage "step2" "Starting Step 2 Services"
cd ../step2_Interactive_Chat
docker compose up -d
check_status "Step 2 services started"

# Wait for services to be ready
print_stage "wait" "Waiting for Services"
wait_for_service "Backend API" "http://localhost:8000/health"
wait_for_service "Frontend" "http://localhost:3000"

# Step 5: Test chat functionality
print_stage "chat" "Testing Chat Functionality"
test_chat

# Step 6: Cleanup
print_stage "cleanup" "Cleaning Up Services"
docker compose down
cd ../step1_video_highlight_extractor
docker compose down
check_status "Services stopped"

echo -e "\n${GREEN}=== Test Flow Completed ===${NC}\n" 