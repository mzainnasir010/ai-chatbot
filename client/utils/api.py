import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")


def stream_chat(message: str, history: list, model: str):
    with requests.post(
        f"{BACKEND_URL}/chat/stream",
        json={"message": message, "history": history, "model": model},
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


def fetch_models() -> dict:
    try:
        resp = requests.get(f"{BACKEND_URL}/chat/models", timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return {"models": [{"id": "gemini-3.5-flash", "label": "Gemini 3.5 Flash"}], "default": "gemini-3.5-flash"}

def check_health() -> bool:
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False
