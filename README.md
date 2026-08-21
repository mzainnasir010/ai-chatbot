# 🔮 Echo: AI Chatbot

> A production-ready, full-stack AI chatbot powered by **Google Gemini**, built with **FastAPI**, **LangChain**, and **Streamlit**. Features real-time response streaming, a premium responsive UI, multi-model support, and dark/light themes.

---

## 📋 Table of Contents

- [About the Project](#-about-the-project)
- [Architecture Overview](#-architecture-overview)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Setup: Virtual Environment](#-setup-virtual-environment)
- [Setup: Environment Variables](#-setup-environment-variables)
- [Install Dependencies](#-install-dependencies)
- [Running the App](#-running-the-app)
- [API Reference](#-api-reference)
- [Features](#-features)
- [Customization](#-customization)
- [Notes & Gotchas](#-notes--gotchas)

---

## 🧠 About the Project

**Echo** is an AI chatbot assistant that lets users have natural, streaming conversations powered by Google's Gemini language models. It is split into two independent services:

| Service | Role |
|---|---|
| **Server** (`/server`) | FastAPI backend: handles AI inference, model routing, and streaming |
| **Client** (`/client`) | Streamlit frontend: renders the chat UI, themes, and streams responses |

The client calls the server's REST API and streams the response token-by-token, giving users a real-time typing effect. The project is designed to be easily extensible swap models, add new routes, or restyle the UI without touching the other half.

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────────────────────┐
│                    USER BROWSER                  │
│                  localhost:8501                  │
│              (Streamlit Frontend)                │
└────────────────────┬────────────────────────────┘
                     │  HTTP POST /chat/stream
                     ▼
┌─────────────────────────────────────────────────┐
│               FastAPI Backend                    │
│              localhost:8000                      │
│                                                  │
│   /health       → status check                  │
│   /chat/models  → list available models          │
│   /chat         → single response               │
│   /chat/stream  → streaming response (SSE)       │
└────────────────────┬────────────────────────────┘
                     │  LangChain + Google GenAI
                     ▼
              Google Gemini API
```

---

## 🛠 Tech Stack

### Backend (Server)
| Technology | Purpose |
|---|---|
| **FastAPI** | High-performance async REST API framework |
| **Uvicorn** | ASGI server to run FastAPI |
| **LangChain** | LLM abstraction & chain management |
| **langchain-google-genai** | Google Gemini integration for LangChain |
| **python-dotenv** | Load environment variables from `.env` |

### Frontend (Client)
| Technology | Purpose |
|---|---|
| **Streamlit** | Python-based interactive web UI framework |
| **Requests** | HTTP client to call the FastAPI backend |
| **Pillow (PIL)** | Load logo image for favicon & chat avatars |
| **python-dotenv** | Load `BACKEND_URL` from `.env` |

### AI / Models
| Model | Description |
|---|---|
| `gemini-3.5-flash` | Default: balanced speed & quality ✅ |
| `gemini-3.5-flash-lite` | Fastest, lightest responses |
| `gemini-3.6-flash` | Next-gen flash model |
| `gemini-3.7-flash` | Latest flash model |

---

## 📁 Project Structure

```
AI Chatbot/
├── README.md
├── .gitignore
├── chatbot_venv/              ← shared virtual environment (git-ignored)
│
├── server/                    ← FastAPI Backend
│   ├── .env                   ← secrets (git-ignored)
│   ├── .env.example           ← template for .env
│   ├── requirements.txt
│   ├── get_models.py          ← utility to list available Gemini models
│   └── app/
│       ├── main.py            ← FastAPI app entry point
│       ├── core/
│       │   └── config.py      ← settings & env var loading
│       ├── models/
│       │   └── schemas.py     ← Pydantic request/response models
│       ├── routes/
│       │   └── chat.py        ← /chat endpoints
│       └── services/
│           └── chatbot.py     ← LangChain + Gemini logic
│
└── client/                    ← Streamlit Frontend
    ├── .env                   ← secrets (git-ignored)
    ├── .env.example           ← template for .env
    ├── requirements.txt
    ├── app.py                 ← main Streamlit application
    ├── assets/
    │   └── logo.png           ← chatbot logo
    ├── .streamlit/
    │   └── config.toml        ← Streamlit theme & server config
    └── utils/
        └── api.py             ← HTTP helpers (stream_chat, fetch_models, check_health)
```

---

## ✅ Prerequisites

Make sure you have the following installed before starting:

- **Python 3.10+** : [Download](https://www.python.org/downloads/)
- **pip** : comes with Python
- **Google Gemini API Key** : get one free at [Google AI Studio](https://aistudio.google.com/app/apikey)

---

## 🐍 Setup: Virtual Environment

A single shared virtual environment at the project root is recommended.

```powershell
# Navigate to the project root
cd "AI Chatbot"

# Create the virtual environment
python -m venv chatbot_venv

# Activate it (Windows PowerShell)
.\chatbot_venv\Scripts\Activate.ps1

# Activate it (Windows CMD)
.\chatbot_venv\Scripts\activate.bat

# Activate it (macOS / Linux)
source chatbot_venv/bin/activate
```

> 💡 You'll know it's active when you see `(chatbot_venv)` at the start of your terminal prompt.

To deactivate later:
```powershell
deactivate
```

---

## 🔐 Setup: Environment Variables

Both the server and client need their own `.env` file. Copy the provided `.env.example` in each folder and fill in your values.

### Server : `server/.env`

```powershell
# Copy the template
copy server\.env.example server\.env
```

Then open `server/.env` and fill in:

```env
GOOGLE_API_KEY=your_google_gemini_api_key_here
```

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | ✅ Yes | Your Google Gemini API key from [AI Studio](https://aistudio.google.com/app/apikey) |
| `GEMINI_MODEL` | Optional | Default model ID (defaults to `gemini-3.5-flash`) |
| `ALLOWED_ORIGINS` | Optional | CORS origins (defaults to `http://localhost:8501`) |

> ⚠️ The server will **refuse to start** if `GOOGLE_API_KEY` is missing or empty.

---

### Client : `client/.env`

```powershell
# Copy the template
copy client\.env.example client\.env
```

Then open `client/.env` and fill in:

```env
BACKEND_URL=http://localhost:8000
```

| Variable | Required | Description |
|---|---|---|
| `BACKEND_URL` | ✅ Yes | Full URL of the running FastAPI server |

> 💡 If you deploy the server to the cloud, replace `http://localhost:8000` with your deployment URL (e.g. `https://myapi.onrender.com`).

---

## 📦 Install Dependencies

With the virtual environment **activated**, install dependencies for both services.

### Install Server dependencies
```powershell
pip install -r server\requirements.txt
```

### Install Client dependencies
```powershell
pip install -r client\requirements.txt
```

Or install both at once:
```powershell
pip install -r server\requirements.txt -r client\requirements.txt
```

---

## 🚀 Running the App

You need **two separate terminals** : one for the server and one for the client.

### Terminal 1 : Start the Backend (FastAPI)

```powershell
# Activate venv
.\chatbot_venv\Scripts\Activate.ps1

# Run the FastAPI server
.\chatbot_venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000 --app-dir server
```

The API will be live at:
- **API Base:** `http://localhost:8000`
- **Interactive Docs (Swagger):** `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/health`

---

### Terminal 2 : Start the Frontend (Streamlit)

```powershell
# Activate venv
.\chatbot_venv\Scripts\Activate.ps1

# Run the Streamlit client
.\chatbot_venv\Scripts\python.exe -m streamlit run client\app.py
```

The UI will open automatically at:
- **Chat Interface:** `http://localhost:8501`

> ✅ Make sure the server is running **before** starting the client, or the "Echo Alive" status indicator will show red.

---

## 📡 API Reference

### `GET /health`
Returns the backend status.
```json
{ "status": "ok", "app": "AI Chatbot API", "version": "1.0.0" }
```

### `GET /chat/models`
Returns the list of available Gemini models.
```json
{
  "models": [
    { "id": "gemini-3.5-flash", "label": "Gemini 3.5 Flash (Recommended)" }
  ],
  "default": "gemini-3.5-flash"
}
```

### `POST /chat`
Single (non-streaming) chat response.
```json
// Request
{ "message": "Hello!", "history": [], "model": "gemini-3.5-flash" }

// Response
{ "reply": "Hi there! How can I help you today?" }
```

### `POST /chat/stream`
Streaming chat response (used by the UI). Returns plain text chunks as they are generated.
```json
// Request body (same as /chat)
{ "message": "Explain Python", "history": [], "model": "gemini-3.5-flash" }
// Response: chunked plain/text stream
```

---

## ✨ Features

- 🔮 **Real-time streaming** : responses appear token-by-token as Gemini generates them
- 🎨 **Dark & Light themes** : switchable from the sidebar, applied instantly
- 🤖 **Multi-model support** : switch between Gemini models mid-conversation
- 📊 **Response stats** : each reply shows generation time (seconds) and word count
- ⚡ **Typing indicator** : animated bouncing dots while the model is thinking
- 📱 **Responsive design** : works on desktop, tablet, and mobile
- 🖼️ **Custom branding** : logo used as favicon, sidebar icon, header, and chat avatar
- 🩺 **Health check** : live backend status displayed in the sidebar
- 🗑️ **Clear chat** : reset conversation with one click

---

## 🎨 Customization

### Change the chatbot name
In `client/app.py`, search for `"Echo"` and replace with your preferred name.

### Add a new Gemini model
In `server/app/core/config.py`, add an entry to `AVAILABLE_MODELS`:
```python
{ "id": "gemini-2.0-flash", "label": "Gemini 2.0 Flash" }
```

### Change the logo
Replace `client/assets/logo.png` with your own square PNG image.

### Change themes / colors
In `client/app.py`, edit the `THEMES` dictionary at the top of the file.

---

## 🗒 Notes & Gotchas

- **Never commit `.env` files** : they are git-ignored by default. Always use `.env.example` as reference.
- **Virtual environment** (`chatbot_venv/`) is also git-ignored : each developer creates their own.
- The server must be started **before** the client, otherwise the health check will fail on load.
- If you change the server port from `8000`, update `BACKEND_URL` in `client/.env` accordingly.
- The Streamlit client connects to the backend via `BACKEND_URL` : this makes it trivially deployable to cloud platforms (Render, Railway, Fly.io, etc.) by just updating that one variable.
- `ALLOWED_ORIGINS` in the server `.env` must include your client's URL when deploying to production to avoid CORS errors.

---

## 📄 License

This project was built as part of an internship at **SEKER AI**. All rights reserved.
