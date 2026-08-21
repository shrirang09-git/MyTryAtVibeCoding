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


ASSISTANT_AVATAR = get_avatar()

# ---------------------------------------------------------------------------
# Page config & styling
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Shrirang PO Twin",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .main-header { font-size: 2rem; font-weight: 700; margin-bottom: 0.25rem; }
    .sub-header { color: #64748b; font-size: 1rem; margin-bottom: 1.5rem; }
    .cred-badge {
        display: inline-block; background: #f1f5f9; color: #334155;
        padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.75rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
    }
    .sample-btn { margin-bottom: 0.35rem; }
    div[data-testid="stSidebar"] { background: #f8fafc; }
    div[data-testid="stSidebar"] [data-testid="stImage"] img,
    .header-avatar [data-testid="stImage"] img {
        border-radius: 50%;
        border: 3px solid #e2e8f0;
        object-fit: cover;
    }
    .footer-note { color: #94a3b8; font-size: 0.8rem; margin-top: 2rem; }
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
    for cert in PERSONA["certifications"]:
        st.markdown(f"- {cert}")
    st.divider()
    st.markdown("**Domain focus**")
    for domain in PERSONA["domains"]:
        st.markdown(f"- {domain}")
    st.divider()
    st.markdown("**Operator programmes**")
    for op in PERSONA["operators"]:
        st.markdown(f"- {op}")
    st.divider()
    st.link_button("Connect on LinkedIn", PERSONA["linkedin"], use_container_width=True)
    st.caption(f"📍 {PERSONA['location']}")

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

# Mode switch — pinned at the very top of the main page as two big buttons,
# visible immediately even if the sidebar is collapsed (e.g. embedded/mobile).
if "mode" not in st.session_state:
    st.session_state.mode = "Recruiter Screening"

st.markdown(
    """
<style>
    div[data-testid="stHorizontalBlock"] .stButton button {
        height: 3.2rem;
        font-size: 1.05rem;
        font-weight: 600;
    }
</style>
""",
    unsafe_allow_html=True,
)

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
        "🎯 PO Deep-Dive",
        use_container_width=True,
        type="primary" if st.session_state.mode == "PO Deep-Dive" else "secondary",
    ):
        st.session_state.mode = "PO Deep-Dive"
        st.rerun()

mode = st.session_state.mode
st.divider()

col_av, col_title, col_status = st.columns([1, 4, 1])
with col_av:
    if has_avatar_image():
        with st.container():
            st.markdown('<div class="header-avatar">', unsafe_allow_html=True)
            st.image(ASSISTANT_AVATAR, width=72)
            st.markdown("</div>", unsafe_allow_html=True)
is_screening = mode == "Recruiter Screening"

with col_title:
    if is_screening:
        st.markdown('<p class="main-header">Recruiter Screening Twin</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sub-header">Ask me the questions a recruiter would in a screening call — '
            "background, visa status, notice period, and more.</p>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<p class="main-header">AI Product Owner Twin</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="sub-header">Ask product, BSS, or digital-twin questions — '
            "answered the way a senior Telecom PO would.</p>",
            unsafe_allow_html=True,
        )
with col_status:
    has_key = bool(__import__("os").getenv("OPENAI_API_KEY"))
    if has_key and use_ai:
        st.success("AI mode")
    else:
        st.info("Knowledge mode")

# Sample questions — one-click for LinkedIn demo
active_samples = SCREENING_SAMPLE_QUESTIONS if is_screening else SAMPLE_QUESTIONS
sample_key_prefix = "screening_sample" if is_screening else "po_sample"
st.markdown("**Try a sample question:**")
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
    else "Ask about prioritisation, requirements, BSS/OSS, digital twin, Agile..."
)
prompt = st.session_state.pop("pending_prompt", None) or st.chat_input(chat_placeholder)

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state[messages_key].append({"role": "user", "content": prompt})

    spinner_text = "Thinking about how to answer that..." if is_screening else "Thinking like a PO..."
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

# Footer
st.markdown(
    '<p class="footer-note">Built by Shrirang Deshpande · '
    "CSPO · SAFe POPM · Telecom BSS Product Owner · "
    "This twin reflects professional PO thinking — not official employer advice.</p>",
    unsafe_allow_html=True,
)
