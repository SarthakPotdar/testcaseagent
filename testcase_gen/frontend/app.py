"""
app.py - Streamlit frontend for the Test Case Generator.
"""

import time
import requests
import streamlit as st
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TestGen AI",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = "http://localhost:8000"
ALLOWED_TYPES = ["pdf", "xlsx", "xls", "docx"]

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #0f172a;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #1e293b !important;
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* Hide default Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }

/* Chat messages */
.chat-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
    padding: 0 0 20px 0;
}

.msg-user {
    background: #6366f1;
    color: white;
    padding: 12px 16px;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%;
    align-self: flex-end;
    margin-left: auto;
    font-size: 14px;
    line-height: 1.5;
    box-shadow: 0 2px 8px rgba(99,102,241,0.3);
}

.msg-assistant {
    background: #1e293b;
    color: #e2e8f0;
    padding: 14px 18px;
    border-radius: 18px 18px 18px 4px;
    max-width: 80%;
    font-size: 14px;
    line-height: 1.6;
    border: 1px solid #334155;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}

.msg-assistant strong {
    color: #a5b4fc;
}

.msg-assistant ul {
    padding-left: 18px;
    margin: 8px 0;
}

.msg-assistant li {
    margin: 4px 0;
}

/* File chips */
.file-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #334155;
    color: #94a3b8;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
    margin: 2px;
}

/* Download button */
.download-btn {
    display: inline-block;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white !important;
    padding: 10px 22px;
    border-radius: 8px;
    text-decoration: none !important;
    font-weight: 600;
    font-size: 14px;
    margin-top: 10px;
    transition: opacity 0.2s;
    box-shadow: 0 4px 14px rgba(99,102,241,0.4);
}
.download-btn:hover { opacity: 0.9; }

/* Input area */
.input-area {
    position: sticky;
    bottom: 0;
    background: #0f172a;
    padding: 12px 0 0 0;
    border-top: 1px solid #1e293b;
}

/* Stats card */
.stat-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 12px 16px;
    text-align: center;
}
.stat-num {
    font-size: 26px;
    font-weight: 700;
    color: #a5b4fc;
    display: block;
}
.stat-label {
    font-size: 11px;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Scrollable chat area */
.chat-scroll {
    max-height: 62vh;
    overflow-y: auto;
    padding-right: 4px;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "👋 **Welcome to TestGen AI!**\n\n"
                "I can generate comprehensive test cases from your specification documents.\n\n"
                "**How to get started:**\n"
                "1. Enter your OpenAI API key in the sidebar\n"
                "2. Click the **+** button to attach your spec docs (PDF, XLSX, DOCX)\n"
                "3. Send a message and I'll generate test cases automatically!\n\n"
                "I'll build a knowledge graph from your docs and produce a downloadable Excel report."
            ),
            "files": [],
            "download_url": None,
        }
    ]

if "pending_files" not in st.session_state:
    st.session_state.pending_files = []

if "last_stats" not in st.session_state:
    st.session_state.last_stats = None


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧪 TestGen AI")
    st.markdown("---")

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-...",
        help="Your OpenAI API key. Used only for this session.",
    )

    st.markdown("---")
    st.markdown("### 📁 Attach Documents")
    uploaded = st.file_uploader(
        "Click to upload or drop files",
        type=ALLOWED_TYPES,
        accept_multiple_files=True,
        label_visibility="collapsed",
        key="file_uploader",
    )

    if uploaded:
        new_names = {f.name for f in st.session_state.pending_files}
        for f in uploaded:
            if f.name not in new_names:
                st.session_state.pending_files.append(f)
                new_names.add(f.name)

    if st.session_state.pending_files:
        st.markdown("**Queued files:**")
        to_remove = []
        for i, f in enumerate(st.session_state.pending_files):
            col1, col2 = st.columns([4, 1])
            col1.markdown(f"📎 `{f.name}`")
            if col2.button("✕", key=f"rm_{i}", help="Remove"):
                to_remove.append(i)
        for idx in reversed(to_remove):
            st.session_state.pending_files.pop(idx)
        st.rerun() if to_remove else None

    st.markdown("---")

    if st.session_state.last_stats:
        s = st.session_state.last_stats
        st.markdown("### 📊 Last Run")
        cols = st.columns(2)
        cols[0].metric("Test Cases", s.get("total", 0))
        cols[1].metric("Documents", s.get("documents_processed", 0))
        cols[0].metric("Features", s.get("features_found", 0))
        cols[1].metric("Edge Cases", s.get("edge_cases_found", 0))

    st.markdown("---")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.session_state.last_stats = None
        st.rerun()

    st.markdown(
        '<div style="color:#475569;font-size:11px;margin-top:8px;">Powered by GPT-4o-mini · FastAPI · Streamlit</div>',
        unsafe_allow_html=True
    )


# ── Main chat area ─────────────────────────────────────────────────────────────
st.markdown('<div style="color:#e2e8f0;font-size:22px;font-weight:700;margin-bottom:6px;">💬 TestGen AI Chat</div>', unsafe_allow_html=True)

# Render messages
chat_html = '<div class="chat-container">'
for msg in st.session_state.messages:
    if msg["role"] == "user":
        files_html = ""
        if msg.get("files"):
            files_html = "<br><div style='margin-top:6px'>" + "".join(
                f'<span class="file-chip">📎 {f}</span>' for f in msg["files"]
            ) + "</div>"
        # Convert newlines to <br> for HTML display
        content = msg["content"].replace("\n", "<br>")
        chat_html += f'<div class="msg-user">{content}{files_html}</div>'
    else:
        # Convert markdown-like bold to HTML
        content = msg["content"]
        # Simple markdown → HTML
        import re
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\n- ', '\n• ', content)
        content = content.replace("\n", "<br>")

        download_html = ""
        if msg.get("download_url"):
            url = f"{BACKEND_URL}{msg['download_url']}"
            download_html = f'<br><a href="{url}" class="download-btn" target="_blank">⬇️ Download Excel Report</a>'

        chat_html += f'<div class="msg-assistant">{content}{download_html}</div>'

chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# ── Input area ─────────────────────────────────────────────────────────────────
st.markdown('<div class="input-area">', unsafe_allow_html=True)

# Show pending file chips above input
if st.session_state.pending_files:
    chips = " ".join(
        f'<span class="file-chip">📎 {f.name}</span>'
        for f in st.session_state.pending_files
    )
    st.markdown(
        f'<div style="margin-bottom:6px">{chips}</div>',
        unsafe_allow_html=True
    )

col_msg, col_send = st.columns([6, 1])
with col_msg:
    user_input = st.chat_input(
        placeholder="Describe what you want to test, or just send files…",
    )

st.markdown("</div>", unsafe_allow_html=True)

# ── Handle send ────────────────────────────────────────────────────────────────
if user_input:
    if not api_key:
        st.error("⚠️ Please enter your OpenAI API key in the sidebar.")
        st.stop()

    files_snapshot = list(st.session_state.pending_files)
    file_names = [f.name for f in files_snapshot]

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "files": file_names,
        "download_url": None,
    })

    # Call backend
    with st.spinner("🤖 Analysing documents and generating test cases…"):
        try:
            form_data = {
                "message": user_input,
                "openai_api_key": api_key,
            }
            file_tuples = [
                ("files", (f.name, f.getvalue(), f.type))
                for f in files_snapshot
            ]

            resp = requests.post(
                f"{BACKEND_URL}/chat",
                data=form_data,
                files=file_tuples if file_tuples else None,
                timeout=300,
            )

            if resp.status_code == 200:
                data = resp.json()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": data.get("content", "Done!"),
                    "files": [],
                    "download_url": data.get("download_url"),
                })
                if data.get("stats"):
                    st.session_state.last_stats = data["stats"]
            else:
                detail = resp.json().get("detail", resp.text)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"❌ **Error {resp.status_code}:** {detail}",
                    "files": [],
                    "download_url": None,
                })

        except requests.exceptions.ConnectionError:
            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "❌ **Cannot connect to the backend.**\n\n"
                    "Make sure the FastAPI server is running:\n"
                    "```\ncd backend && uvicorn main:app --reload\n```"
                ),
                "files": [],
                "download_url": None,
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ **Unexpected error:** {str(e)}",
                "files": [],
                "download_url": None,
            })

    # Clear pending files after send
    st.session_state.pending_files = []
    st.rerun()
