import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

def get_respose(user_input: str, chat_history: list):
    messages = [SystemMessage(content = "You are helpful, professional assistant.")]
    for role, text in chat_history:
        if role == "user":
            messages.append(HumanMessage(content=text))
        else:
            messages.append(SystemMessage(content=text))
    messages.append(HumanMessage(content=user_input))
    response = llm.invoke(messages)
    return response.content
