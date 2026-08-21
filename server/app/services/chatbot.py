import time
from typing import Generator, List, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.core.config import settings

SYSTEM_PROMPT = "You are a helpful, professional AI assistant. Answer clearly and concisely."

ALLOWED_MODEL_IDS = {m["id"] for m in settings.AVAILABLE_MODELS}

_llm_cache = {}

def get_llm(model_name: str) -> ChatGoogleGenerativeAI:
    if model_name not in ALLOWED_MODEL_IDS:
        raise ValueError(f"Model '{model_name}' is not in the allowed list")
    if model_name not in _llm_cache:
        _llm_cache[model_name] = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.7,
            google_api_key=settings.GOOGLE_API_KEY,
        )
    return _llm_cache[model_name]    

def _build_messages(user_input: str, history: List[Tuple[str, str]]):
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for role, text in history:
        if role == "user":
            messages.append(HumanMessage(content=text))
        else:
            messages.append(AIMessage(content=text))
    messages.append(HumanMessage(content=user_input))
    return messages


def get_response(user_input: str, history: List[Tuple[str, str]], model_name: str) -> dict:
    llm = get_llm(model_name)
    messages = _build_messages(user_input, history)
    start = time.perf_counter()
    result = llm.invoke(messages)
    elapsed = round(time.perf_counter() - start,2)
    return {
        "reply": result.content,
        "response_time": elapsed,
        "word_count": len(result.content.split()),
    }


def stream_response(
    user_input: str,
    history: List[Tuple[str, str]],
    model_name: str
) -> Generator[str, None, None]:

    llm = get_llm(model_name)
    messages = _build_messages(user_input, history)

    for chunk in llm.stream(messages):
        content = chunk.content

        if not content:
            continue

        if isinstance(content, str):
            yield content

        elif isinstance(content, list):
            for item in content:
                if isinstance(item, str):
                    yield item
                elif isinstance(item, dict):
                    text = item.get("text")
                    if text:
                        yield text