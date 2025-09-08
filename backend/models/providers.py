# backend/models/providers.py
import httpx
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM = "You are a hiring assistant. Answer ONLY from the provided context."

async def call_grok(prompt: str) -> str:
    """
    Calls the Groq API.
    """
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "llama-3.1-8b-instant",  # A fast, supported model on Groq
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, json=body, headers=headers)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]