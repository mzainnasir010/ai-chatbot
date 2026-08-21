import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")


def stream_chat(message: str, history: list):
    with requests.post(
        f"{BACKEND_URL}/chat/stream",
        json={"message": message, "history": history},
        stream=True,
        timeout=60,
    ) as response:
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


def check_health() -> bool:
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return resp.status_code == 200
    except requests.RequestException:
        return False
