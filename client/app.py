import streamlit as st
from utils.api import stream_chat, check_health

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="font-size:32px;">✨</div>
            <div>
                <div style="font-size:20px;font-weight:700;">Echo</div>
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
    st.markdown(
        f"<span style='color:{status_color};'>●</span> {status_label}",
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption("Conversation")
    st.metric("Messages", len(st.session_state.history))

    if st.button("Clear chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.divider()
    st.caption("About")
    st.write("Echo is a demo chatbot built with FastAPI, LangChain, Gemini, and Streamlit.")

st.markdown("### Echo, your AI Assistant")
st.caption("Ask anything. Responses stream in as they are generated.")

for role, text in st.session_state.history:
    avatar = "🧑" if role == "user" else "✨"
    with st.chat_message(role, avatar=avatar):
        st.markdown(text)

user_input = st.chat_input("Message Echo...")

if user_input:
    st.session_state.history.append(("user", user_input))
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="✨"):
        placeholder = st.empty()
        full_reply = ""
        try:
            for chunk in stream_chat(user_input, st.session_state.history[:-1]):
                full_reply += chunk
                placeholder.markdown(full_reply + "▌")
            placeholder.markdown(full_reply)
        except Exception as exc:
            full_reply = f"Something went wrong reaching the backend: {exc}"
            placeholder.markdown(full_reply)

    st.session_state.history.append(("assistant", full_reply))
