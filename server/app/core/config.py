import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501").split(",")
    APP_NAME: str = "AI Chatbot API"
    APP_VERSION: str = "1.0.0"


settings = Settings()

if not settings.GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY is missing. Set it in your .env file.")
