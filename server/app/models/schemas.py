from pydantic import BaseModel, Field
from typing import List, Tuple


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: List[Tuple[str, str]] = []
    model: str = "gemini-3.5-flash"


class ChatResponse(BaseModel):
    reply: str
    response_time: float
    word_count: int
