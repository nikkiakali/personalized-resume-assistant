import os
import shutil
import logging
from typing import List
from pathlib import Path

# Load .env file before any other application imports.
# This is crucial to ensure environment variables are available when other modules are imported.
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

# Your imports
from deps import embed_texts
from rag.store import VectorStore
from rag.ingest import extract_text, chunk, prepare_metadatas
from rag.retrieval import assemble_prompt, as_np
from models.providers import call_grok

app = FastAPI(title="Personalized Resume Assistant API")

# CORS: allow your local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vector store initialization
# Default 384 works for MiniLM (sentence-transformers/all-MiniLM-L6-v2) and bge-small
EMBED_DIM = int(os.getenv("EMBED_DIM", "384"))
STORE = VectorStore(dim=EMBED_DIM)

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.get("/healthz")
async def healthz():
    """Basic health check and embed dim confirmation."""
    return {"status": "ok", "embed_dim": EMBED_DIM}


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """
    Accept a resume/JD file, extract text, chunk, embed, and add to the vector store.
    """
    try:
        path = os.path.join(UPLOAD_DIR, file.filename)
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        text = extract_text(path)
        chunks = chunk(text, max_tokens=400, overlap=60)
        metas = prepare_metadatas(chunks, file.filename)

        vecs = embed_texts([m["text"] for m in metas])
        STORE.add(as_np(vecs), metas)

        return {"chunks": len(chunks), "filename": file.filename}
    except RuntimeError as e:
        # This is often a sign of a dimension mismatch in Faiss
        logger.error(f"Runtime error during ingestion, possibly a dimension mismatch: {e}")
        detail = (
            f"A runtime error occurred. This can happen if the embedding model's "
            f"output dimension does not match the vector store's dimension ({EMBED_DIM}). "
            f"Original error: {e}"
        )
        raise HTTPException(status_code=500, detail=detail)


class ChatRequest(BaseModel):
    query: str
    k: int = 5


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Embed the query, retrieve top-k chunks, assemble a grounded prompt,
    and call the selected model through providers.MODEL_MAP.
    """
    # Embed query
    qvec = np.array([embed_texts([req.query])[0]], dtype="float32")

    # Retrieve top-k supporting chunks
    hits = STORE.search(qvec, k=req.k)

    # Build prompt from retrieved context
    prompt = assemble_prompt(req.query, hits)

    try:
        answer = await call_grok(prompt)
    except ValueError as e:
        # Catches configuration errors from providers, like a missing API key.
        logger.error(f"Configuration error in LLM provider: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Server configuration error for the selected model: {e}"
        )
    except httpx.ConnectError as e:
        logger.error(f"Connection to LLM provider failed: {e}")
        raise HTTPException(
            status_code=503, # Service Unavailable
            detail="Could not connect to the LLM service (e.g., Ollama). Is it running?"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"LLM provider returned an error: {e.response.status_code} - {e.response.text}")
        detail = f"The LLM service returned an error: {e.response.status_code}."
        raise HTTPException(
            status_code=502, # Bad Gateway
            detail=detail
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred during chat generation: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while generating the chat response."
        )

    return {
        "answer": answer,
        "citations": [
            {"filename": h["filename"], "chunk_id": h["chunk_id"], "score": h["score"]}
            for h in hits
        ],
    }