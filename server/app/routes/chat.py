from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.schemas import ChatRequest, ChatResponse
from app.services.chatbot import get_response, stream_response

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        reply = get_response(req.message, req.history)
        return ChatResponse(reply=reply)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/stream")
def chat_stream(req: ChatRequest):
    try:
        return StreamingResponse(
            stream_response(req.message, req.history),
            media_type="text/plain",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
