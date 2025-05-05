# Test_for_team_AI

---

## 📹 **Step 1: Video Processor with LLM-Based Highlight Extraction**

### 🎯 Task Overview:
Build a **Python-based video processing tool** that extracts descriptive highlights from videos using an **LLM (Large Language Model)**. The processed highlights should be stored in a **PostgreSQL database using pgvector** for similarity-based retrieval.

### ✅ Requirements:

#### Functional Goals:
1. Accept video files as input (e.g., `.mp4`, `.mov`).
2. Automatically extract **visual and audio descriptions** (e.g., scenes, objects, speech-to-text).
3. Use an **LLM** to:
   - Select **important moments** (e.g., explosions, people speaking, vehicle movement).
   - Generate **detailed descriptions** for each moment.
4. Save each highlight to a **PostgreSQL database** with:
   - `timestamp`
   - `description`
   - `video_id`
   - `embedding (pgvector)`
   - `LLM-generated summary`

#### Technical Constraints:
- ✅ Must use **Python**
- ✅ Must use **LMM** Help for chat
- ✅ Must store data in a **PostgreSQL + pgvector** database.
- ✅ Must follow **OOP principles** with good folder structure and separation of concerns (`processors`, `database`, `llm`, etc.).
- ✅ Must include a **Docker setup** for both the Python service and PostgreSQL (with pgvector extension).
- ✅ Must contain a **demo script** showing:
   - Video processing in action
   - Output descriptions being saved to DB

#### Deliverables:
- Python code with OOP structure
- Docker setup (`docker-compose.yml`)
- PostgreSQL schema
- ✅ A very neat and **clear README** 


## Note:
- **The examinee must select the videos. A proper video is between thirty seconds and a minute and a half. The video must be uploaded along with the assignment, At least two videos must be selected.**
- You can use free key  " https://aistudio.google.com/ "
---

## 💬 **Step 2: Interactive Chat About Video Highlights**

### 🎯 Task Overview:
Extend your system to allow users to **chat with a React frontend** and ask questions about the processed video highlights.

### ✅ Requirements:

#### Functional Goals:
1. Build a **Free choice frontend** that allows users to:
   - Enter a question (e.g., *“What happened after the person got out of the car?”*)
   - Select a video from a dropdown
   - See answers pulled **only from the database**
2. Build a **Python backend (FastAPI recommended)** that:
   - Accepts chat questions
   - Uses embeddings or keyword search to match relevant highlights from the DB
   - Responds only with content from the database (no real-time LLM response)
   - Structures responses coherently based on matching highlights

#### Technical Constraints:
- ✅ Frontend in **Free choice**
- ✅ Backend in **Python** (FastAPI preferred)
- ✅ Adheres to **OOP structure** for API, data access layer, and chat logic
- ✅ Uses Docker for both frontend and backend
- ✅ Backend must pull data **only from the database** (LLM is not used in this step)
- ✅ Clean modular architecture and routing in both React and Python
- ✅ Include a **neat README** that explains:
   - How to start each container
   - Chat architecture
   - Endpoint flow

---

## 🧠 **Bonus Task: Neural Network Tic-Tac-Toe Player**

### 🎯 Task Overview:
Implement a simple neural network that learns to play **Tic-Tac-Toe** using self-play or predefined rules. Provide both a **training visualization** and a **game interface**.

### ✅ Requirements:

#### Part 1: Model Training
- Implement a **basic neural network** in PyTorch or TensorFlow.
- Train it to play against:
  - Random moves (Easy)
  - Heuristic opponent (Medium)
  - Itself (Hard)
- Log training process (e.g., win rate, loss, move preference)

#### Part 2: Game Interface
- Display the game board using a simple GUI (Tkinter, PyGame, or web-based)
- Let the user select difficulty (Easy, Medium, Hard)
- Show the model's move in real time

#### Bonus Points:
- Add visual feedback for the training process (matplotlib loss curves, win stats)
- Enable human-vs-AI play mode

