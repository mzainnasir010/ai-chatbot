from pydantic import BaseModel, Field
from typing import List, Tuple


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: List[Tuple[str, str]] = []


class ChatResponse(BaseModel):
    reply: str
