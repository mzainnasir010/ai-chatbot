import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0.7,
    google_api_key=os.getenv("GOOGLE_API_KEY")
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
