# backend/models/providers.py
import httpx
import os
import anthropic

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

SYSTEM = "You are a hiring assistant. Answer ONLY from the provided context."

async def call_local_llama(prompt: str) -> str:
    """
    Uses Ollama's chat API so we can set a system message.
    """
    url = f"{OLLAMA_HOST}/api/chat"
    body = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, json=body)
        r.raise_for_status()
        data = r.json()
        # last message content
        return data["message"]["content"]

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
        "model": "llama-3.1-8b-instant", # A fast, supported model on Groq
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

async def call_claude3(prompt: str) -> str:
    """
    Calls the Anthropic API for a Claude 3 model.
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    message = await client.messages.create(
        model="claude-3-haiku-20240307", # Fast and capable model
        max_tokens=1024,
        system=SYSTEM,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text


MODEL_MAP = {
    "local-llama": call_local_llama,
    "grok": call_grok,
    "claude-3": call_claude3,
}