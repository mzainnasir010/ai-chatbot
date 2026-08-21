import time
import streamlit as st
from utils.api import stream_chat, check_health, fetch_models

st.set_page_config(
    page_title="Aria | AI Chatbot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

THEMES = {
    "Dark": {
        "bg": "#0F1117",
        "bg2": "#1A1D27",
        "text": "#F2F2F2",
        "accent": "#6C5CE7",
        "bubble_user": "#1F2333",
        "bubble_ai": "#171A24",
    },
    "Light": {
        "bg": "#FFFFFF",
        "bg2": "#F5F5F7",
        "text": "#1A1A1A",
        "accent": "#6C5CE7",
        "bubble_user": "#EFEFF5",
        "bubble_ai": "#FAFAFA",
    },
    "Midnight Blue": {
        "bg": "#0A0E1A",
        "bg2": "#131A2C",
        "text": "#E6EAF5",
        "accent": "#3B82F6",
        "bubble_user": "#182238",
        "bubble_ai": "#101627",
    },
    "Forest": {
        "bg": "#0D1512",
        "bg2": "#16241E",
        "text": "#E8F2EC",
        "accent": "#34D399",
        "bubble_user": "#17281F",
        "bubble_ai": "#101B16",
    },
}

if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: role, content, time, words
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
if "model" not in st.session_state:
    st.session_state.model = "gemini-3.5-flash"
if "models_loaded" not in st.session_state:
    st.session_state.available_models = fetch_models()
    st.session_state.models_loaded = True


def apply_theme(theme_name: str):
    t = THEMES[theme_name]
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {t['bg']};
            color: {t['text']};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {t['bg2']};
        }}
        [data-testid="stChatMessage"] {{
            background-color: {t['bubble_ai']};
            border-radius: 12px;
            padding: 4px 8px;
        }}
        .stChatInput {{
            background-color: {t['bg2']};
        }}
        .stButton button {{
            background-color: {t['accent']};
            color: white;
            border: none;
        }}
        .msg-stats {{
            font-size: 11px;
            opacity: 0.55;
            margin-top: -6px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_theme(st.session_state.theme)

with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="font-size:32px;">✨</div>
            <div>
                <div style="font-size:20px;font-weight:700;">Aria</div>
                <div style="font-size:12px;opacity:0.6;">AI Assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    status_ok = check_health()
    status_label = "Backend online" if status_ok else "Backend unreachable"
    status_color = "#2ECC71" if status_ok else "#E74C3C"
    st.markdown(f"<span style='color:{status_color};'>●</span> {status_label}", unsafe_allow_html=True)

    st.divider()
    st.caption("Appearance")
    st.session_state.theme = st.selectbox("Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.theme))

    st.divider()
    st.caption("Model")
    model_options = st.session_state.available_models["models"]
    labels = [m["label"] for m in model_options]
    ids = [m["id"] for m in model_options]
    current_index = ids.index(st.session_state.model) if st.session_state.model in ids else 0
    chosen_label = st.selectbox("Chat model", labels, index=current_index)
    st.session_state.model = ids[labels.index(chosen_label)]

    st.divider()
    st.caption("Conversation")
    st.metric("Messages", len(st.session_state.history))

    if st.button("Clear chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.divider()
    st.caption("About")
    st.write("Aria is a demo chatbot built with FastAPI, LangChain, Gemini, and Streamlit.")

st.markdown("### Aria, your AI Assistant")
st.caption("Ask anything. Responses stream in as they are generated.")

for msg in st.session_state.history:
    avatar = "🧑" if msg["role"] == "user" else "✨"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("time") is not None:
            st.markdown(
                f"<div class='msg-stats'>{msg['time']}s · {msg['words']} words</div>",
                unsafe_allow_html=True,
            )

user_input = st.chat_input("Message Aria...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input, "time": None, "words": None})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    history_pairs = [(m["role"], m["content"]) for m in st.session_state.history[:-1]]

    with st.chat_message("assistant", avatar="✨"):
        placeholder = st.empty()
        stats_placeholder = st.empty()
        full_reply = ""
        start = time.perf_counter()
        try:
            for chunk in stream_chat(user_input, history_pairs, st.session_state.model):
                full_reply += chunk
                placeholder.markdown(full_reply + "▌")
            placeholder.markdown(full_reply)
        except Exception as exc:
            full_reply = f"Something went wrong reaching the backend: {exc}"
            placeholder.markdown(full_reply)
        elapsed = round(time.perf_counter() - start, 2)
        word_count = len(full_reply.split())
        stats_placeholder.markdown(
            f"<div class='msg-stats'>{elapsed}s · {word_count} words</div>",
            unsafe_allow_html=True,
        )

    st.session_state.history.append(
        {"role": "assistant", "content": full_reply, "time": elapsed, "words": word_count}
    )
