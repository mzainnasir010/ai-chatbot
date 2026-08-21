import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")
    APP_NAME: str = "AI Chatbot API"
    APP_VERSION: str = "1.0.0"

    AVAILABLE_MODELS: list = [
        {"id": "gemini-3.5-flash", "label": "Gemini 3.5 Flash(Recommended)"},
        {"id": "gemini-3.5-flash-lite", "label": "Gemini 3.5 Flash Lite (fastest, lighter answers)"},
        {"id": "gemini-3.6-flash", "label": "Gemini 3.6 Flash"},
        {"id": "gemini-3.7-flash", "label": "Gemini 3.7 Flash"},
    ]

settings = Settings()

if not settings.GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is missing. Set it in your .env file.")
