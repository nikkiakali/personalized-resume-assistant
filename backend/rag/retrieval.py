from typing import List, Dict
import numpy as np

PROMPT_TEMPLATE = """You are a hiring assistant. Answer the user's question using ONLY the context.
If the answer is not in the context, say you don't have enough information.

Question:
{question}

Context (numbered chunks):
{context}

When possible, cite like [filename#chunk_id].
"""

def format_context(chunks: List[Dict]) -> str:
    lines = []
    for c in chunks:
        lines.append(f"[{c['filename']}#{c['chunk_id']}] {c['text']}")
    return "\n".join(lines)

def assemble_prompt(query: str, chunks: List[Dict]) -> str:
    return PROMPT_TEMPLATE.format(question=query, context=format_context(chunks))

def as_np(vectors: list[list[float]]): return np.array(vectors, dtype="float32")