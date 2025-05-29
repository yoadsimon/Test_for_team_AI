#!/bin/bash

# Build and start the frontend and backend services (in the foreground so logs are visible)

echo "Building and starting the frontend and backend services (logs will be shown in the terminal) ..."
docker compose up --build

# (Removed sleep and echo lines since we're running in the foreground) 