# Video Highlights Chat System - Task Requirements

## Step 2: Interactive Chat About Video Highlights

### Task Overview
Extend the system to allow users to chat with a React frontend and ask questions about the processed video highlights.

### Requirements

#### Functional Goals
1. Build a Free choice frontend that allows users to:
   - Enter a question (e.g., "What happened after the person got out of the car?")
   - See answers pulled only from the database

2. Build a Python backend (FastAPI recommended) that:
   - Accepts chat questions
   - Uses embeddings or keyword search to match relevant highlights from the DB
   - Responds only with content from the database (no real-time LLM response)
   - Structures responses coherently based on matching highlights

#### Technical Constraints
- Frontend in Free choice
- Backend in Python (FastAPI preferred)
- Adheres to OOP structure for API, data access layer, and chat logic
- Uses Docker for both frontend and backend
- Backend must pull data only from the database (LLM is not used in this step)
- Clean modular architecture and routing in both React and Python

#### Documentation Requirements
Include a neat README that explains:
- How to start each container
- Chat architecture
- Endpoint flow 