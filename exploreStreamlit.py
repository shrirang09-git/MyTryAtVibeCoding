"""PO Twin — Streamlit app for LinkedIn showcase."""

import streamlit as st
from dotenv import load_dotenv

from persona import PERSONA, SAMPLE_QUESTIONS, respond

load_dotenv()

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
    .footer-note { color: #94a3b8; font-size: 0.8rem; margin-top: 2rem; }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — credibility panel for LinkedIn visitors
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown("### About this twin")
    st.markdown(
        f"**{PERSONA['name']}**  \n"
        f"{PERSONA['title']}  \n"
        f"{PERSONA['tagline']}"
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

    use_ai = st.toggle(
        "Use AI (OpenAI)",
        value=bool(__import__("os").getenv("OPENAI_API_KEY")),
        help="Requires OPENAI_API_KEY in secrets. Falls back to knowledge base if off or unavailable.",
    )

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------

col_title, col_status = st.columns([4, 1])
with col_title:
    st.markdown('<p class="main-header">🎯 AI Product Owner Twin</p>', unsafe_allow_html=True)
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
st.markdown("**Try a sample question:**")
sq_cols = st.columns(2)
for i, question in enumerate(SAMPLE_QUESTIONS):
    with sq_cols[i % 2]:
        if st.button(question, key=f"sample_{i}", use_container_width=True):
            st.session_state.pending_prompt = question

st.divider()

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🎯" if message["role"] == "assistant" else None):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("mode"):
            st.caption(f"via {message['mode']} engine")

# Handle sample question click or chat input
prompt = st.session_state.pop("pending_prompt", None) or st.chat_input(
    "Ask about prioritisation, requirements, BSS/OSS, digital twin, Agile..."
)

if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🎯"):
        with st.spinner("Thinking like a PO..."):
            content, mode = respond(prompt, st.session_state.messages, use_ai=use_ai)
        st.markdown(content)
        st.caption(f"via {mode} engine")

    st.session_state.messages.append(
        {"role": "assistant", "content": content, "mode": mode}
    )

# Footer
st.markdown(
    '<p class="footer-note">Built by Shrirang Deshpande · '
    "CSPO · SAFe POPM · Telecom BSS Product Owner · "
    "This twin reflects professional PO thinking — not official employer advice.</p>",
    unsafe_allow_html=True,
)
