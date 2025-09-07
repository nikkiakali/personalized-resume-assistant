import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env (safe if called multiple times)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "text-embedding-3-small")

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set. Add it to backend/.env")

# OpenAI client will read the key from env automatically
client = OpenAI()

def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Returns embeddings as a list of vectors (lists of floats).
    """
    resp = client.embeddings.create(model=EMBED_MODEL_NAME, input=texts)
    return [d.embedding for d in resp.data]