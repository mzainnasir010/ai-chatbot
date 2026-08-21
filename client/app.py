import time
import streamlit as st
from utils.api import stream_chat, check_health, fetch_models

st.set_page_config(
    page_title="Echo | AI Chatbot",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="auto",
)

# ─── Theme Definitions ────────────────────────────────────────────────────────
THEMES = {
    "Dark": {
        "bg":           "#0A0D14",
        "bg2":          "#111520",
        "bg3":          "#181D2E",
        "text":         "#E2E8F0",
        "text_muted":   "#64748B",
        "accent":       "#0EA5E9",
        "accent2":      "#38BDF8",
        "accent_glow":  "rgba(14,165,233,0.28)",
        "bubble_user":  "#0F1929",
        "bubble_ai":    "#0D1120",
        "border":       "rgba(14,165,233,0.20)",
        "input_bg":     "#111520",
        "gradient":     "linear-gradient(135deg, #0369A1 0%, #0EA5E9 100%)",
        "badge_bg":     "rgba(14,165,233,0.12)",
    },
    "Light": {
        "bg":           "#F1F5F9",
        "bg2":          "#FFFFFF",
        "bg3":          "#E2E8F0",
        "text":         "#0F172A",
        "text_muted":   "#475569",
        "accent":       "#0369A1",
        "accent2":      "#0284C7",
        "accent_glow":  "rgba(3,105,161,0.15)",
        "bubble_user":  "#DBEAFE",
        "bubble_ai":    "#FFFFFF",
        "border":       "rgba(3,105,161,0.18)",
        "input_bg":     "#FFFFFF",
        "gradient":     "linear-gradient(135deg, #0369A1 0%, #0284C7 100%)",
        "badge_bg":     "rgba(3,105,161,0.08)",
    },
}

# ─── Session State Init ───────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "model" not in st.session_state:
    st.session_state.model = "gemini-3.5-flash"
if "models_loaded" not in st.session_state:
    st.session_state.available_models = fetch_models()
    st.session_state.models_loaded = True
if "prev_theme" not in st.session_state:
    st.session_state.prev_theme = st.session_state.theme


# ─── CSS Injection ────────────────────────────────────────────────────────────
def apply_theme(theme_name: str):
    t = THEMES[theme_name]
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

        /* ── Root & Body ── */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}
        .stApp {{
            background-color: {t['bg']};
            color: {t['text']};
        }}

        /* ── Animated gradient background noise ── */
        .stApp::before {{
            content: '';
            position: fixed;
            inset: 0;
            background:
                radial-gradient(ellipse 80% 60% at 20% 10%, {t['accent_glow']} 0%, transparent 60%),
                radial-gradient(ellipse 60% 50% at 80% 90%, {t['accent_glow']} 0%, transparent 60%);
            pointer-events: none;
            z-index: 0;
        }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background: {t['bg2']};
            border-right: 1px solid {t['border']};
            backdrop-filter: blur(20px);
        }}
        section[data-testid="stSidebar"] > div {{
            padding-top: 0 !important;
        }}

        /* ── Sidebar header brand ── */
        .echo-brand {{
            background: {t['gradient']};
            padding: 28px 24px 24px;
            margin: 0 -1rem 0;
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .echo-brand-icon {{
            width: 48px;
            height: 48px;
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            flex-shrink: 0;
        }}
        .echo-brand-text-name {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.3px;
            line-height: 1;
        }}
        .echo-brand-text-sub {{
            font-size: 11px;
            color: rgba(255,255,255,0.75);
            margin-top: 3px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}

        /* ── Status pill ── */
        .status-pill {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 500;
            background: {t['badge_bg']};
            border: 1px solid {t['border']};
            color: {t['text']};
            width: 100%;
            justify-content: center;
            margin: 4px 0;
        }}
        .status-dot {{
            width: 7px;
            height: 7px;
            border-radius: 50%;
            animation: pulse-dot 2s infinite;
        }}
        @keyframes pulse-dot {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.6; transform: scale(0.85); }}
        }}

        /* ── Sidebar section labels ── */
        .sidebar-label {{
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            color: {t['text_muted']};
            margin: 16px 0 8px;
            display: block;
        }}

        /* ── Metric card ── */
        .metric-card {{
            background: {t['bg3']};
            border: 1px solid {t['border']};
            border-radius: 12px;
            padding: 12px 16px;
            text-align: center;
            margin: 8px 0;
        }}
        .metric-card-value {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 28px;
            font-weight: 700;
            background: {t['gradient']};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.1;
        }}
        .metric-card-label {{
            font-size: 11px;
            color: {t['text_muted']};
            margin-top: 2px;
            letter-spacing: 0.3px;
        }}

        /* ── Sidebar Streamlit widgets ── */
        .stSelectbox label,
        .stRadio label {{
            font-size: 12px !important;
            color: {t['text_muted']} !important;
            font-weight: 500 !important;
        }}
        [data-testid="stSelectbox"] > div > div {{
            background-color: {t['bg3']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 10px !important;
            color: {t['text']} !important;
            font-size: 13px !important;
        }}
        [data-testid="stSelectbox"] > div > div:hover {{
            border-color: {t['accent']} !important;
        }}
        [data-testid="stSelectbox"] > div > div > div {{
            color: {t['text']} !important;
        }}

        /* ── Clear button ── */
        .stButton > button {{
            background: {t['gradient']} !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            padding: 10px 18px !important;
            width: 100% !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 4px 15px {t['accent_glow']} !important;
            letter-spacing: 0.2px !important;
        }}
        .stButton > button:hover {{
            opacity: 0.9 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px {t['accent_glow']} !important;
        }}
        .stButton > button:active {{
            transform: translateY(0) !important;
        }}

        /* ── Main header ── */
        .echo-header {{
            padding: 32px 0 20px;
            text-align: center;
            position: relative;
        }}
        .echo-header-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 5px 14px;
            border-radius: 999px;
            background: {t['badge_bg']};
            border: 1px solid {t['border']};
            font-size: 11px;
            font-weight: 600;
            color: {t['accent2']};
            letter-spacing: 0.5px;
            text-transform: uppercase;
            margin-bottom: 14px;
        }}
        .echo-header-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: clamp(30px, 5vw, 48px);
            font-weight: 700;
            background: {t['gradient']};
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.15;
            letter-spacing: -1px;
            margin: 0;
        }}
        .echo-header-sub {{
            font-size: clamp(13px, 2vw, 15px);
            color: {t['text_muted']};
            margin-top: 10px;
            font-weight: 400;
            max-width: 480px;
            margin-left: auto;
            margin-right: auto;
        }}
        .echo-divider {{
            height: 1px;
            background: {t['border']};
            margin: 20px 0;
            border: none;
        }}

        /* ── Chat message bubbles ── */
        [data-testid="stChatMessage"] {{
            background: {t['bubble_ai']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 16px !important;
            padding: 14px 18px !important;
            margin-bottom: 12px !important;
            backdrop-filter: blur(10px);
            transition: border-color 0.2s ease;
            position: relative;
            z-index: 1;
        }}
        [data-testid="stChatMessage"]:hover {{
            border-color: {t['accent']}60 !important;
        }}
        [data-testid="stChatMessage"][data-testid*="user"],
        div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
            background: {t['bubble_user']} !important;
            border-color: {t['accent']}40 !important;
        }}

        /* ── Global text color (critical for light theme) ── */
        html, body, .stApp, .stApp * {{
            color: {t['text']};
        }}
        .stMarkdown, .stMarkdown p, .stMarkdown li,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] div,
        [data-testid="stText"], [data-testid="stCaption"],
        .stTextInput input, .stSelectbox,
        div[class*="css"] p, div[class*="css"] span {{
            color: {t['text']} !important;
        }}
        .stApp label, .stApp .stCaption {{
            color: {t['text_muted']} !important;
        }}

        /* ── Chat message text ── */
        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] span,
        [data-testid="stChatMessage"] div {{
            color: {t['text']} !important;
            font-size: 14.5px !important;
            line-height: 1.7 !important;
        }}
        [data-testid="stChatMessage"] code {{
            background: {t['bg3']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 6px !important;
            padding: 2px 7px !important;
            font-size: 13px !important;
            color: {t['accent2']} !important;
        }}
        [data-testid="stChatMessage"] pre {{
            background: {t['bg3']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 10px !important;
            padding: 14px !important;
        }}

        /* ── Message stats ── */
        .msg-stats {{
            font-size: 11px;
            color: {t['text_muted']};
            margin-top: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 400;
        }}
        .msg-stats-dot {{
            width: 3px;
            height: 3px;
            border-radius: 50%;
            background: {t['text_muted']};
            display: inline-block;
        }}

        /* ── Chat input ── */
        [data-testid="stChatInput"],
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div {{
            background: {t['input_bg']} !important;
            border-radius: 14px !important;
        }}
        [data-testid="stChatInput"] {{
            border: 1px solid {t['border']} !important;
            box-shadow: 0 4px 24px {t['accent_glow']} !important;
        }}
        [data-testid="stChatInput"]:focus-within {{
            border-color: {t['accent']} !important;
            box-shadow: 0 4px 30px {t['accent_glow']} !important;
        }}
        [data-testid="stChatInput"] textarea {{
            color: {t['text']} !important;
            background: {t['input_bg']} !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 14px !important;
            caret-color: {t['accent']} !important;
        }}
        [data-testid="stChatInput"] textarea::placeholder {{
            color: {t['text_muted']} !important;
        }}
        [data-testid="stChatInput"] button {{
            background: {t['gradient']} !important;
            border-radius: 9px !important;
            border: none !important;
        }}

        /* ── Empty state ── */
        .echo-empty {{
            text-align: center;
            padding: 60px 20px;
        }}
        .echo-empty-icon {{
            font-size: 56px;
            margin-bottom: 16px;
            filter: drop-shadow(0 0 20px {t['accent_glow']});
            animation: float 4s ease-in-out infinite;
        }}
        @keyframes float {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
        .echo-empty-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 20px;
            font-weight: 600;
            color: {t['text']};
            margin-bottom: 8px;
        }}
        .echo-empty-sub {{
            font-size: 13px;
            color: {t['text_muted']};
            max-width: 340px;
            margin: 0 auto 28px;
            line-height: 1.6;
        }}

        /* ── Suggestion chips ── */
        .suggestion-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            max-width: 540px;
            margin: 0 auto;
        }}
        .suggestion-chip {{
            padding: 9px 16px;
            border-radius: 999px;
            background: {t['badge_bg']};
            border: 1px solid {t['border']};
            font-size: 12.5px;
            color: {t['text']};
            cursor: default;
            transition: all 0.2s ease;
            font-weight: 450;
        }}
        .suggestion-chip:hover {{
            background: {t['accent']}22;
            border-color: {t['accent']}60;
        }}

        /* ── Divider ── */
        hr {{
            border-color: {t['border']} !important;
        }}

        /* ── Scrollbar ── */
        ::-webkit-scrollbar {{
            width: 5px;
        }}
        ::-webkit-scrollbar-track {{
            background: {t['bg']};
        }}
        ::-webkit-scrollbar-thumb {{
            background: {t['accent']}55;
            border-radius: 999px;
        }}
        ::-webkit-scrollbar-thumb:hover {{
            background: {t['accent']}99;
        }}

        /* ── About box ── */
        .about-box {{
            background: {t['bg3']};
            border: 1px solid {t['border']};
            border-radius: 12px;
            padding: 12px 14px;
            font-size: 12px;
            color: {t['text_muted']};
            line-height: 1.6;
        }}
        .about-box strong {{
            color: {t['accent2']};
        }}

        /* ── Streamlit chrome: hide only the rainbow decoration ── */
        [data-testid="stDecoration"] {{
            display: none !important;
        }}
        /* Make the top toolbar area transparent — keep it in DOM for sidebar toggle */
        header[data-testid="stHeader"] {{
            background: transparent !important;
        }}
        /* Hide the hamburger menu icon only (not the sidebar toggle) */
        #MainMenu {{
            visibility: hidden !important;
        }}
        footer {{
            visibility: hidden !important;
        }}
        /* Style the sidebar collapse/expand arrow button */
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="collapsedControl"] button {{
            background: {t['bg3']} !important;
            border: 1px solid {t['border']} !important;
            border-radius: 8px !important;
            color: {t['text']} !important;
        }}
        [data-testid="stSidebarCollapseButton"] svg,
        [data-testid="collapsedControl"] svg {{
            fill: {t['text']} !important;
        }}

        /* ── Responsive content adjustments ── */
        @media (max-width: 768px) {{
            .echo-header {{
                padding: 16px 0 10px;
            }}
            [data-testid="stChatMessage"] {{
                padding: 10px 14px !important;
                border-radius: 12px !important;
            }}
            [data-testid="stChatMessage"] p {{
                font-size: 13.5px !important;
            }}
            .echo-empty {{
                padding: 32px 12px;
            }}
            .echo-empty-icon {{
                font-size: 40px;
            }}
            .echo-header-title {{
                font-size: 26px !important;
            }}
            .suggestion-grid {{
                gap: 8px;
            }}
        }}
        @media (max-width: 480px) {{
            .suggestion-chip {{
                font-size: 11.5px;
                padding: 7px 12px;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


apply_theme(st.session_state.theme)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand header
    st.markdown(
        """
        <div class="echo-brand">
            <div class="echo-brand-icon">🔮</div>
            <div>
                <div class="echo-brand-text-name">Echo</div>
                <div class="echo-brand-text-sub">AI Assistant</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Status
    status_ok = check_health()
    dot_color = "#10B981" if status_ok else "#EF4444"
    status_text = "Backend Online" if status_ok else "Backend Offline"
    st.markdown(
        f"""
        <div class="status-pill">
            <span class="status-dot" style="background:{dot_color};
                box-shadow: 0 0 6px {dot_color};"></span>
            {status_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # Appearance
    st.markdown('<span class="sidebar-label">Appearance</span>', unsafe_allow_html=True)
    selected_theme = st.selectbox(
        "Theme",
        list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme),
        label_visibility="collapsed",
    )
    # Detect theme change and rerun to apply immediately
    if selected_theme != st.session_state.theme:
        st.session_state.theme = selected_theme
        st.session_state.prev_theme = selected_theme
        st.rerun()

    st.divider()

    # Model
    st.markdown('<span class="sidebar-label">Model</span>', unsafe_allow_html=True)
    model_options = st.session_state.available_models["models"]
    labels = [m["label"] for m in model_options]
    ids = [m["id"] for m in model_options]
    current_index = ids.index(st.session_state.model) if st.session_state.model in ids else 0
    chosen_label = st.selectbox(
        "Chat model",
        labels,
        index=current_index,
        label_visibility="collapsed",
    )
    st.session_state.model = ids[labels.index(chosen_label)]

    st.divider()

    # Conversation stats
    st.markdown('<span class="sidebar-label">Conversation</span>', unsafe_allow_html=True)
    msg_count = len(st.session_state.history)
    ai_count = sum(1 for m in st.session_state.history if m["role"] == "assistant")
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card-value">{msg_count}</div>
            <div class="metric-card-label">Total messages &nbsp;·&nbsp; {ai_count} AI replies</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("✦ Clear Chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    st.divider()

    # About
    st.markdown('<span class="sidebar-label">About</span>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="about-box">
            <strong>Echo</strong> is an AI chatbot powered by
            <strong>Gemini</strong> · built with <strong>FastAPI</strong>,
            <strong>LangChain</strong> &amp; <strong>Streamlit</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

# ─── Main Area ────────────────────────────────────────────────────────────────
# Header
st.markdown(
    """
    <div class="echo-header">
        <div class="echo-header-badge">🔮 &nbsp;Powered by Gemini</div>
        <h1 class="echo-header-title">Echo: Your own AI Assistant</h1>
        <p class="echo-header-sub">Ask anything: responses stream in real-time as they're generated.</p>
    </div>
    <hr class="echo-divider">
    """,
    unsafe_allow_html=True,
)

# ── Chat history ──
if not st.session_state.history:
    st.markdown(
        """
        <div class="echo-empty">
            <div class="echo-empty-icon">🔮</div>
            <div class="echo-empty-title">Start a conversation</div>
            <div class="echo-empty-sub">Type a message below or try one of these to get started.</div>
            <div class="suggestion-grid">
                <div class="suggestion-chip">✨ Explain quantum computing</div>
                <div class="suggestion-chip">💡 Write a Python function</div>
                <div class="suggestion-chip">🌍 Summarize world news</div>
                <div class="suggestion-chip">🎨 Creative writing prompt</div>
                <div class="suggestion-chip">🧮 Solve a math problem</div>
                <div class="suggestion-chip">📝 Draft an email</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    for msg in st.session_state.history:
        avatar = "🧑" if msg["role"] == "user" else "🔮"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("time") is not None:
                st.markdown(
                    f"""<div class='msg-stats'>
                        ⚡ {msg['time']}s
                        <span class='msg-stats-dot'></span>
                        {msg['words']} words
                    </div>""",
                    unsafe_allow_html=True,
                )

# ── Input ──
user_input = st.chat_input("Message Echo...")

if user_input:
    # Clear empty state by adding to history
    st.session_state.history.append({"role": "user", "content": user_input, "time": None, "words": None})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    history_pairs = [(m["role"], m["content"]) for m in st.session_state.history[:-1]]

    with st.chat_message("assistant", avatar="🔮"):
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
            full_reply = f"⚠️ Something went wrong reaching the backend: {exc}"
            placeholder.markdown(full_reply)
        elapsed = round(time.perf_counter() - start, 2)
        word_count = len(full_reply.split())
        stats_placeholder.markdown(
            f"""<div class='msg-stats'>
                ⚡ {elapsed}s
                <span class='msg-stats-dot'></span>
                {word_count} words
            </div>""",
            unsafe_allow_html=True,
        )

    st.session_state.history.append(
        {"role": "assistant", "content": full_reply, "time": elapsed, "words": word_count}
    )
