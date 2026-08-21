from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chatbot import get_response, stream_response

router = APIRouter(prefix="/chat", tags=["chat"])

@router.get("/models")
def list_models():
    return {"models": settings.AVAILABLE_MODELS, "default": settings.GEMINI_MODEL}

@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        result = get_response(req.message, req.history, req.model)
        return ChatResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/stream")
def chat_stream(req: ChatRequest):
    try:
        return StreamingResponse(
            stream_response(req.message, req.history, req.model),
            media_type="text/plain",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
