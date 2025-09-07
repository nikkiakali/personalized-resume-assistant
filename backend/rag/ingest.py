from typing import List, Dict
from pypdf import PdfReader
import docx2txt, os, re

def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def extract_text(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".pdf":
        reader = PdfReader(filepath)
        return _clean(" ".join(page.extract_text() or "" for page in reader.pages))
    if ext in [".docx", ".doc"]:
        return _clean(docx2txt.process(filepath) or "")
    if ext in [".txt", ".md"]:
        return _clean(open(filepath, "r", encoding="utf-8", errors="ignore").read())
    raise ValueError(f"Unsupported file: {ext}")

def chunk(text: str, max_tokens: int = 500, overlap: int = 80) -> List[str]:
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + max_tokens, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words): break
        start = end - overlap
    return chunks

def prepare_metadatas(chunks: List[str], filename: str) -> List[Dict]:
    metas = []
    for i, c in enumerate(chunks):
        metas.append({"filename": filename, "chunk_id": i, "text": c})
    return metas