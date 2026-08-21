from typing import Generator, List, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.core.config import settings

SYSTEM_PROMPT = "You are a helpful, professional AI assistant. Answer clearly and concisely."

llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    temperature=0.7,
    google_api_key=settings.GOOGLE_API_KEY,
)


def _build_messages(user_input: str, history: List[Tuple[str, str]]):
    messages = [SystemMessage(content=SYSTEM_PROMPT)]
    for role, text in history:
        if role == "user":
            messages.append(HumanMessage(content=text))
        else:
            messages.append(AIMessage(content=text))
    messages.append(HumanMessage(content=user_input))
    return messages


def get_response(user_input: str, history: List[Tuple[str, str]]) -> str:
    messages = _build_messages(user_input, history)
    result = llm.invoke(messages)

    if isinstance(result.content, str):
        return result.content

    return "".join(
        block.get("text", "")
        for block in result.content
        if isinstance(block, dict) and block.get("type") == "text"
    )


def stream_response(
    user_input: str,
    history: List[Tuple[str, str]]
) -> Generator[str, None, None]:

    messages = _build_messages(user_input, history)

    for chunk in llm.stream(messages):
        content = chunk.content

        if isinstance(content, str):
            if content:
                yield content

        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "")
                    if text:
                        yield text