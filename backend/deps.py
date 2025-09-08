# backend/deps.py
import os
from typing import List

try:
    # fastembed >= 0.5
    from fastembed import TextEmbedding
except Exception:
    # fallback for older fastembed (<0.5)
    from fastembed.embedding import TextEmbedding  # type: ignore

# 384-dim, small and fast
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "BAAI/bge-small-en-v1.5")
_embedder = TextEmbedding(model_name=EMBED_MODEL_NAME)

def embed_texts(texts: List[str]) -> List[List[float]]:
    # FastEmbed yields numpy arrays; convert to lists
    return [vec.tolist() for vec in _embedder.embed(texts, batch_size=64)]