from fastapi import FastAPI
from pydantic import BaseModel
from chatbot import get_respose

app = FastAPI()

class ChatRequest(BaseModel):
    message: str
    history : list = []

@app.post("/chat")
def chat(req: ChatRequest):
    reply = get_respose(req.message, req.history)
    return {"reply": reply}

    