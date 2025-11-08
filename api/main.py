from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import httpx
import json
from dotenv import load_dotenv
import os
from pydantic import BaseModel

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
MODEL = os.getenv("MODEL")

app = FastAPI()

class Prompt(BaseModel):
    prompt: str

async def stream_ollama(prompt: str):
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream(
            "POST",
            OLLAMA_URL,
            json={"model": MODEL, "prompt": prompt, "stream": True},
        ) as response:
            async for line in response.aiter_lines():
                if line.strip():
                    data = json.loads(line)
                    yield data.get("response", "")
@app.get("/generate")
async def generate(prompt: str):
    return StreamingResponse(stream_ollama(prompt), media_type="text/plain")

@app.post("/generate")
async def generate(data: Prompt):
    return StreamingResponse(stream_ollama(data.prompt), media_type="text/plain")
