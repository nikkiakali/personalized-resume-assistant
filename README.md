# AI Resume Assistant ✨

Upload your resume + a job description → get **AI-powered, personalized feedback** on how well they align.  
This project implements a modern **Retrieval-Augmented Generation (RAG)** pipeline to highlight skills, detect gaps, and suggest improvements for job seekers.

- 🚀 Built with **FastAPI + React**
- ⚡ Powered by **Groq Llama 3.1 8B** with automatic **Google Gemini fallback**
- 📄 Supports **PDF, DOCX, TXT, and Markdown**
- 🔍 Uses **FAISS vector search** + **fastembed** for high-performance retrieval


## Features
- **Flexible Document Ingestion**: Upload resumes, job descriptions, or related docs (PDF, DOCX, TXT, MD)
- **End-to-End RAG Pipeline**: Text extraction → chunking → embedding → storage → retrieval → generation
- **High-Performance Embeddings**: Default model `BAAI/bge-small-en-v1.5` via `fastembed`
- **Vector Search**: FAISS in-memory similarity search with disk persistence
- **Dual LLM Strategy**: Groq for ultra-fast inference, Gemini fallback for resilience
- **Async API**: Modern FastAPI backend with async-first design
- **Simple REST Endpoints**: Easy to ingest documents and query them

## 🛠 Tech Stack
![Python](https://img.shields.io/badge/python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-async-green)
![React](https://img.shields.io/badge/React-18-blue)
![FAISS](https://img.shields.io/badge/FAISS-vector%20search-orange)
![Groq](https://img.shields.io/badge/Groq-LLM-red)
![Gemini](https://img.shields.io/badge/Gemini-fallback-yellow)
  
## Getting Started

### Prerequisites

- Python 3.9+
- Node.js + npm
- API keys for **Groq** + **Google Gemini**

### Installation

```bash
# Clone the repo
git clone https://github.com/nikkiakali/resume-assistant.git
cd resume-assistant

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

## Configuration

Create a .env file inside backend/:
```
GROQ_API_KEY="gsk_your_key"
GOOGLE_API_KEY="AIza_your_key"
EMBED_MODEL_NAME="BAAI/bge-small-en-v1.5"
EMBED_DIM="384"
```

### Run the app

```bash
# From the project root
source backend/venv/bin/activate
cd frontend
npm run all
```
The app will open at: http://localhost:5173

## API Endpoints

#### Health Check

- **Endpoint**: `GET /healthz`
- **Description**: A simple health check to confirm the server is running and to see the configured embedding dimension.
- **Response**:
  ```json
  {
    "status": "ok",
    "embed_dim": 384
  }
  ```

### Ingest a Document

- **Endpoint**: `POST /ingest`
- **Description**: Upload a document (`.pdf`, `.docx`, `.txt`, `.md`) to be processed and added to the vector store.
- **Example**:
  ```bash
  curl -X POST \
    -F "file=@/path/to/your/resume.pdf" \
    http://127.0.0.1:8000/ingest
  ```

### Chat with Documents

- **Endpoint**: `POST /chat`
- **Description**: Ask a question about the ingested documents. The API will retrieve relevant context and generate an answer.
- **Body**:
  - `query` (str): The question you want to ask.
  - `k` (int, optional, default: 10): The number of document chunks to retrieve as context.
- **Example**:
  ```bash
  curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"query": "What are my top 3 skills relevant for a Python developer role?", "k": 5}' \
    http://127.0.0.1:8000/chat
  ```

## Architecture
The system follows a Retrieval-Augmented Generation workflow:

1. Ingest:
   Upload doc → extract text → chunk → embed → store in FAISS
2. Query:
   Embed query → retrieve top-k chunks → assemble context → send to LLM
3. Answer:
   LLM (Groq primary, Gemini fallback) → context-aware response


## Project Structure

```
resume-assistant/
├── backend/
│   ├── data/                  # Stores persisted data (index, metadata, uploads)
│   │   ├── uploads/
│   │   ├── index.faiss        # FAISS vector index
│   │   └── meta.json          # Metadata for vectors
│   ├── models/
│   │   └── providers.py       # Logic for calling LLM APIs (Groq, Gemini)
│   ├── rag/
│   │   ├── ingest.py          # Document parsing and chunking
│   │   ├── retrieval.py       # Prompt assembly logic
│   │   └── store.py           # FAISS VectorStore implementation
│   ├── app.py                 # Main FastAPI application, endpoints
│   ├── deps.py                # Embedding model loader
│   ├── .env                   # (You create this) API keys and config
│   └── requirements.txt       # (You create this) Python dependencies
└── README.md                  # This file
```

## What’s Next
- Add match scoring dashboard (% resume–JD alignment)
- Multi-resume + multi-role comparisons
- Integration with Job Tracker Chrome Extension

## About
Built by [Natasha Akali](https://github.com/nikkiakali) — turning ideas into products that help people.

---

## Advanced Configuration ⚙️

### Changing the Embedding Model

You can swap the embedding model by editing your .env:
- EMBED_MODEL_NAME: Any model supported by fastembed
- EMBED_DIM: Must match the output dimension of the chosen model

**Important**: If you change the embedding model, delete the backend/data directory to clear the old vector store. Re-ingest documents after restart.

### Provider Logic

- Primary: Groq Llama 3.1 8B
- Fallback: Google Gemini (auto failover on 429s, missing keys, or errors)
- Logic implemented in backend/app.py under the /chat endpoint

### Data Persistence

- Vector index saved in backend/data/index.faiss
- Metadata in backend/data/meta.json
- Uploaded docs in backend/data/uploads/
- To reset, delete the backend/data folder and restart
