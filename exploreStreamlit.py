"""PO Twin — Streamlit app for LinkedIn showcase."""

from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from persona import (
    PERSONA,
    SAMPLE_QUESTIONS,
    SCREENING_SAMPLE_QUESTIONS,
    respond,
    respond_screening,
)

load_dotenv()

# Avatar — kept here so cloud deploy never depends on persona.py exports
_APP_ROOT = Path(__file__).resolve().parent
_AVATAR_CANDIDATES = (
    _APP_ROOT / "assets" / "avatar.jpg",
    _APP_ROOT / "assets" / "avatar.png",
    _APP_ROOT / "assets" / "avatar.jpeg",
    _APP_ROOT / "assets" / "avatar.webp",
)
AVATAR_FALLBACK = "🎯"


def get_avatar() -> str:
    for path in _AVATAR_CANDIDATES:
        if path.is_file():
            return str(path)
    return AVATAR_FALLBACK


def has_avatar_image() -> bool:
    return get_avatar() != AVATAR_FALLBACK


def badge_row(items: list[str]) -> str:
    """Render a list of strings as pill badges (reuses .cred-badge style)."""
    return " ".join(f'<span class="cred-badge">{item}</span>' for item in items)


ASSISTANT_AVATAR = get_avatar()

# ---------------------------------------------------------------------------
# Page config & styling
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Shrirang AI PM Twin",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    :root {
        --accent: #475569;
        --accent-dark: #0f172a;
        --accent-light: #f1f5f9;
        --slate: #64748b;
        --slate-light: #94a3b8;
        --border: #e2e8f0;
        --radius-lg: 18px;
        --radius-md: 12px;
        --shadow-sm: 0 1px 3px rgba(15, 23, 42, 0.06);
        --shadow-md: 0 8px 24px rgba(15, 23, 42, 0.08);
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* ---- Header ---- */
    .main-header {
        font-size: 2rem; font-weight: 800; margin-bottom: 0.2rem;
        color: var(--accent-dark); letter-spacing: -0.02em;
    }
    .sub-header { color: var(--slate); font-size: 1rem; margin-bottom: 0; }

    .st-key-header_card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: var(--radius-lg) !important;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border) !important;
        padding: 0.25rem 0.5rem;
    }

    /* ---- Mode switch ---- */
    .st-key-mode_switch .stButton button {
        height: 3.3rem;
        border-radius: 999px;
        font-size: 1.02rem;
        font-weight: 700;
        border: 1.5px solid var(--border);
        transition: all 0.15s ease;
    }
    .st-key-mode_switch .stButton button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%);
        border: none;
        box-shadow: var(--shadow-sm);
    }
    .st-key-mode_switch .stButton button:hover { transform: translateY(-1px); box-shadow: var(--shadow-sm); }

    /* ---- Sample question chips ---- */
    .sample-eyebrow {
        text-transform: uppercase; letter-spacing: 0.08em; font-size: 0.72rem;
        font-weight: 700; color: var(--slate-light); margin-bottom: 0.5rem;
    }
    .st-key-sample_questions .stButton button {
        border-radius: var(--radius-md);
        border: 1.5px solid #cbd5e1;
        background: #ffffff;
        font-weight: 500;
        color: #334155;
        text-align: left;
        justify-content: flex-start;
        padding: 0.6rem 1rem;
        transition: all 0.15s ease;
    }
    .st-key-sample_questions .stButton button:hover {
        border-color: var(--accent);
        background: var(--accent-light);
        color: var(--accent-dark);
    }

    /* ---- Status pill (AI mode / Knowledge mode) ---- */
    [data-testid="stAlert"] {
        border-radius: 999px !important;
        padding: 0.35rem 0.9rem !important;
        font-size: 0.82rem !important;
        width: fit-content;
        margin-left: auto;
        box-shadow: none !important;
    }

    /* ---- Chat bubbles ---- */
    [data-testid="stChatMessage"] {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.75rem;
        box-shadow: var(--shadow-sm);
    }
    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
        background: var(--accent-light);
        border-color: #e2e8f0;
    }

    /* ---- Chat input bar ---- */
    [data-testid="stBottom"] { background: #ffffff !important; }
    [data-testid="stBottom"] > div {
        background: #ffffff !important;
        border-top: 1px solid var(--border);
    }
    [data-testid="stChatInput"] {
        background: #ffffff !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 999px !important;
        box-shadow: var(--shadow-sm);
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(71, 85, 105, 0.15);
    }
    [data-testid="stChatInput"] * { background: transparent !important; }
    /* Suppress the browser's own focus outline on the inner textarea/wrapper —
       it was drawing a second, sharp-cornered rectangle on top of the custom
       pill border + glow above, giving a 'boxes overlapping' look. */
    [data-testid="stChatInput"] *,
    [data-testid="stChatInput"] *:focus,
    [data-testid="stChatInput"] *:focus-visible {
        outline: none !important;
        box-shadow: none !important;
        border-color: transparent !important;
    }
    [data-testid="stChatInput"] textarea { color: #1e293b !important; }
    [data-testid="stChatInput"] textarea::placeholder { color: var(--slate-light) !important; }
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%) !important;
        border-radius: 999px !important;
        border: none !important;
        box-shadow: var(--shadow-sm);
        transition: transform 0.15s ease;
    }
    [data-testid="stChatInput"] button:hover { transform: scale(1.08); }
    [data-testid="stChatInput"] button svg { fill: #ffffff !important; }

    /* ---- Credential badges (neutral gray-on-white, used in the sidebar) ---- */
    .cred-badge {
        display: inline-block; background: #f1f5f9; color: #1e293b;
        padding: 0.25rem 0.7rem; border-radius: 999px; font-size: 0.78rem;
        margin: 0.15rem 0.3rem 0.15rem 0; font-weight: 500; border: 1px solid var(--border);
    }

    /* ---- Dividers ---- */
    hr { border: none; height: 1px; background: var(--border); margin: 1.4rem 0; }

    /* ---- Sidebar: white background, near-black text ---- */
    /* Note: Streamlit renders the sidebar as a <section>, not a <div> —
       an earlier `div[data-testid="stSidebar"]` selector never matched. */
    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] * { color: #0f172a; }
    [data-testid="stSidebar"] h3 { color: #0f172a; font-weight: 700; }
    [data-testid="stSidebar"] strong { color: #0f172a; }
    [data-testid="stSidebar"] hr { background: var(--border); margin: 1.1rem 0; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: var(--slate) !important; }
    [data-testid="stSidebar"] .stToggle label p { color: #0f172a !important; }
    /* Contact buttons. The `a *` selector (not just `a`) is needed to
       out-specificity the sidebar-wide `[data-testid="stSidebar"] * {
       color: #0f172a }` rule above, which otherwise wins on the button's
       inner text node. */
    .st-key-calendly_btn a {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-dark) 100%) !important;
        border: none !important;
        color: #ffffff !important;
        font-weight: 700;
        box-shadow: var(--shadow-sm);
    }
    .st-key-calendly_btn a * { color: #ffffff !important; }
    .st-key-calendly_btn a:hover { opacity: 0.92; }
    .st-key-linkedin_btn a {
        background: #0a66c2 !important;
        border-color: #0a66c2 !important;
        color: #ffffff !important;
        font-weight: 600;
    }
    .st-key-linkedin_btn a * { color: #ffffff !important; }
    .st-key-linkedin_btn a:hover {
        background: #004182 !important;
        border-color: #004182 !important;
    }
    .st-key-email_btn a {
        background: #ffffff !important;
        border: 1.5px solid var(--border) !important;
        color: #0f172a !important;
        font-weight: 600;
    }
    .st-key-email_btn a * { color: #0f172a !important; }
    .st-key-email_btn a:hover {
        border-color: var(--accent) !important;
        background: var(--accent-light) !important;
    }

    [data-testid="stSidebar"] [data-testid="stImage"] img,
    .header-avatar [data-testid="stImage"] img {
        border-radius: 50%;
        border: 3px solid var(--accent);
        object-fit: cover;
        box-shadow: 0 0 0 4px rgba(71, 85, 105, 0.12);
    }

    /* ---- Footer (lives at the bottom of the sidebar — see note below) ---- */
    .footer-note { color: var(--slate-light); font-size: 0.78rem; margin-top: 1rem; line-height: 1.5; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — credibility panel for LinkedIn visitors
# ---------------------------------------------------------------------------

with st.sidebar:
    if has_avatar_image():
        st.image(ASSISTANT_AVATAR, width=140)
    else:
        st.markdown(
            f"<p style='text-align:center;font-size:3rem;margin:0.5rem 0'>{ASSISTANT_AVATAR}</p>",
            unsafe_allow_html=True,
        )
        st.caption("Add `assets/avatar.jpg` for your photo")
    st.markdown("### Meet My Digital Twin")
    st.markdown(
        f"**{PERSONA['name']}**  \n"
        f"{PERSONA['title']}  \n"
        f"{PERSONA['tagline']}"
    )

    use_ai = st.toggle(
        "Use AI (OpenAI)",
        value=bool(__import__("os").getenv("OPENAI_API_KEY")),
        help="Requires OPENAI_API_KEY in secrets. Falls back to knowledge base if off or unavailable.",
    )

    st.divider()
    st.markdown("**Certifications**")
    st.markdown(badge_row(PERSONA["certifications"]), unsafe_allow_html=True)
    st.divider()
    st.markdown("**Domain focus**")
    st.markdown(badge_row(PERSONA["domains"]), unsafe_allow_html=True)
    st.divider()
    st.markdown("**Operator programmes**")
    st.markdown(badge_row(PERSONA["operators"]), unsafe_allow_html=True)
    st.divider()
    st.link_button(
        "📅 Schedule a Call", PERSONA["calendly"], use_container_width=True, key="calendly_btn"
    )
    st.link_button(
        "Connect on LinkedIn", PERSONA["linkedin"], use_container_width=True, key="linkedin_btn"
    )
    st.link_button(
        "✉️ Email Me", f"mailto:{PERSONA['email']}", use_container_width=True, key="email_btn"
    )
    st.caption(f"📍 {PERSONA['location']}")
    st.divider()
    st.markdown(
        '<p class="footer-note">Built by Shrirang Deshpande · '
        "CSPO · SAFe POPM · Telecom BSS AI Product Manager · "
        "This twin reflects professional PM thinking — not official employer advice.</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

# Mode switch — pinned at the very top of the main page as two big buttons,
# visible immediately even if the sidebar is collapsed (e.g. embedded/mobile).
if "mode" not in st.session_state:
    st.session_state.mode = "Recruiter Screening"

with st.container(key="mode_switch"):
    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        if st.button(
            "🎙️ Recruiter Screening",
            use_container_width=True,
            type="primary" if st.session_state.mode == "Recruiter Screening" else "secondary",
        ):
            st.session_state.mode = "Recruiter Screening"
            st.rerun()
    with mode_col2:
        if st.button(
            "🎯 AI PM Deep-Dive",
            use_container_width=True,
            type="primary" if st.session_state.mode == "AI PM Deep-Dive" else "secondary",
        ):
            st.session_state.mode = "AI PM Deep-Dive"
            st.rerun()

mode = st.session_state.mode
is_screening = mode == "Recruiter Screening"

st.write("")

with st.container(border=True, key="header_card"):
    col_av, col_title, col_status = st.columns([1, 4, 1])
    with col_av:
        if has_avatar_image():
            with st.container():
                st.markdown('<div class="header-avatar">', unsafe_allow_html=True)
                st.image(ASSISTANT_AVATAR, width=72)
                st.markdown("</div>", unsafe_allow_html=True)

    with col_title:
        if is_screening:
            st.markdown('<p class="main-header">Recruiter Screening Twin</p>', unsafe_allow_html=True)
            st.markdown(
                '<p class="sub-header">Ask me the questions a recruiter would in a screening call — '
                "background, visa status, notice period, and more.</p>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<p class="main-header">AI Product Manager Twin</p>', unsafe_allow_html=True)
            st.markdown(
                '<p class="sub-header">Ask about roadmapping, prioritisation, PRDs, metrics, or AI in '
                "product management — answered the way an AI-driven Telecom PM would.</p>",
                unsafe_allow_html=True,
            )
    with col_status:
        has_key = bool(__import__("os").getenv("OPENAI_API_KEY"))
        if has_key and use_ai:
            st.success("AI mode")
        else:
            st.info("Knowledge mode")

st.write("")

# Sample questions — one-click for LinkedIn demo
active_samples = SCREENING_SAMPLE_QUESTIONS if is_screening else SAMPLE_QUESTIONS
sample_key_prefix = "screening_sample" if is_screening else "po_sample"
with st.container(key="sample_questions"):
    st.markdown('<p class="sample-eyebrow">Try a sample question</p>', unsafe_allow_html=True)
    sq_cols = st.columns(2)
    for i, question in enumerate(active_samples):
        with sq_cols[i % 2]:
            if st.button(question, key=f"{sample_key_prefix}_{i}", use_container_width=True):
                st.session_state.pending_prompt = question

st.divider()

# Chat history — kept separate per mode so switching doesn't mix contexts
messages_key = "screening_messages" if is_screening else "po_messages"
if messages_key not in st.session_state:
    st.session_state[messages_key] = []

for message in st.session_state[messages_key]:
    with st.chat_message(
        message["role"],
        avatar=ASSISTANT_AVATAR if message["role"] == "assistant" else None,
    ):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("mode"):
            st.caption(f"via {message['mode']} engine")

# Handle sample question click or chat input
chat_placeholder = (
    "Ask about background, visa status, why you're leaving, notice period..."
    if is_screening
    else "Ask about roadmapping, prioritisation, PRDs, metrics, AI in product management..."
)
# st.chat_input() must be called unconditionally on every run, or the widget
# vanishes for the rest of the session — see project notes on this gotcha.
chat_prompt = st.chat_input(chat_placeholder)
pending_prompt = st.session_state.pop("pending_prompt", None)
prompt = pending_prompt or chat_prompt

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state[messages_key].append({"role": "user", "content": prompt})

    spinner_text = "Thinking about how to answer that..." if is_screening else "Thinking like a PM..."
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        with st.spinner(spinner_text):
            if is_screening:
                content, resp_mode = respond_screening(
                    prompt, st.session_state[messages_key], use_ai=use_ai
                )
            else:
                content, resp_mode = respond(
                    prompt, st.session_state[messages_key], use_ai=use_ai
                )
        st.markdown(content)
        st.caption(f"via {resp_mode} engine")

    st.session_state[messages_key].append(
        {"role": "assistant", "content": content, "mode": resp_mode}
    )
