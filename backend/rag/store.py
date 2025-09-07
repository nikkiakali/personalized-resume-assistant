import faiss, json, os, numpy as np
from typing import List, Dict, Any

INDEX_PATH = "data/index.faiss"
META_PATH  = "data/meta.json"

class VectorStore:
    def __init__(self, dim: int):
        self.dim = dim
        self.index = faiss.IndexFlatIP(dim)
        self.meta: list[Dict[str, Any]] = []

        if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            self.meta  = json.load(open(META_PATH))

    def add(self, vectors: np.ndarray, metadatas: List[Dict[str, Any]]):
        assert vectors.shape[1] == self.dim
        self.index.add(vectors.astype(np.float32))
        self.meta.extend(metadatas)
        faiss.write_index(self.index, INDEX_PATH)
        json.dump(self.meta, open(META_PATH, "w"))

    def search(self, query: np.ndarray, k: int = 5):
        D, I = self.index.search(query.astype(np.float32), k)
        hits = []
        for idx, score in zip(I[0], D[0]):
            if idx == -1: continue
            hit = self.meta[idx].copy()
            hit["score"] = float(score)
            hits.append(hit)
        return hits