import os, httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")

async def call_gpt4(prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "system", "content": "You answer strictly from provided context."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=body)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

async def call_claude3(prompt: str) -> str:
    url = "https://api.anthropic.com/v1/messages"
    headers = {"x-api-key": ANTHROPIC_API_KEY, "anthropic-version": "2023-06-01"}
    body = {"model": "claude-3-haiku-20240307", "max_tokens": 800,
            "system": "You answer strictly from provided context.",
            "messages": [{"role": "user", "content": prompt}]}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=body)
        r.raise_for_status()
        return r.json()["content"][0]["text"]

async def call_grok(prompt: str) -> str:
    url = "https://api.x.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
    body = {"model": "grok-beta",
            "messages": [{"role": "system", "content": "You answer strictly from provided context."},
                         {"role": "user", "content": prompt}],
            "temperature": 0.1}
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, headers=headers, json=body)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

MODEL_MAP = {"gpt-4": call_gpt4, "claude-3": call_claude3, "grok": call_grok}