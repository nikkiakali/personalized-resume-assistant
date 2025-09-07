import os
import shutil
from dotenv import load_dotenv

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

from deps import embed_texts
from rag.store import VectorStore
from rag.ingest import extract_text, chunk, prepare_metadatas
from rag.retrieval import assemble_prompt, as_np
from models.providers import MODEL_MAP

# Load .env once at startup
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

EMBED_DIM = int(os.getenv("EMBED_DIM", "1536"))  # text-embedding-3-small is 1536-d
STORE = VectorStore(dim=EMBED_DIM)

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    path = os.path.join(UPLOAD_DIR, file.filename)
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    text = extract_text(path)
    chunks = chunk(text, max_tokens=400, overlap=60)
    metas = prepare_metadatas(chunks, file.filename)

    vecs = embed_texts([m["text"] for m in metas])
    STORE.add(as_np(vecs), metas)

    return {"chunks": len(chunks), "filename": file.filename}

class ChatRequest(BaseModel):
    query: str
    model: str = "gpt-4"
    k: int = 5

@app.post("/chat")
async def chat(req: ChatRequest):
    qvec = np.array([embed_texts([req.query])[0]], dtype="float32")
    hits = STORE.search(qvec, k=req.k)
    prompt = assemble_prompt(req.query, hits)

    llm_fn = MODEL_MAP.get(req.model, MODEL_MAP["gpt-4"])
    answer = await llm_fn(prompt)

    return {
        "answer": answer,
        "citations": [
            {"filename": h["filename"], "chunk_id": h["chunk_id"], "score": h["score"]}
            for h in hits
        ],
    }