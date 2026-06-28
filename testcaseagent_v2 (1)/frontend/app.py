"""
app.py - Streamlit frontend for Test Case Agent v2.
Features:
- In-memory file handling (no disk session files)
- Min 2 answers before submit is enabled
- Language selector: English / Español / 日本語 / 한국어
- Base64 download buttons (no /download/ endpoint needed)
"""

import json
import base64
import requests
import streamlit as st
from i18n import t, LANG_OPTIONS

st.set_page_config(
    page_title="TestCase Agent",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = "http://localhost:8000"
ALLOWED_TYPES = ["pdf", "xlsx", "xls", "docx"]

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+JP&family=Noto+Sans+KR&display=swap');
html, body, [class*="css"] { font-family: 'Inter','Noto Sans JP','Noto Sans KR',sans-serif; }
.stApp { background: #0f172a; color: #e2e8f0; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { background: #1e293b !important; border-right: 1px solid #334155; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] input { background: #0f172a !important; color: #e2e8f0 !important; border: 1px solid #334155 !important; }
.stTextArea textarea { background: #1e293b !important; color: #e2e8f0 !important; border: 1px solid #334155 !important; font-size: 14px !important; }
.stTextInput input { background: #1e293b !important; color: #e2e8f0 !important; }

.msg-user {
    background: #6366f1; color: white; padding: 12px 16px;
    border-radius: 18px 18px 4px 18px; max-width: 75%;
    margin-left: auto; font-size: 14px; line-height: 1.5;
    box-shadow: 0 2px 8px rgba(99,102,241,0.3); margin-bottom: 12px;
}
.msg-assistant {
    background: #1e293b; color: #e2e8f0; padding: 14px 18px;
    border-radius: 18px 18px 18px 4px; max-width: 85%; font-size: 14px;
    line-height: 1.6; border: 1px solid #334155; margin-bottom: 12px;
}
.msg-assistant strong { color: #a5b4fc; }

.qa-card {
    background: #1e293b; border: 1px solid #334155;
    border-radius: 12px; padding: 16px 18px; margin-bottom: 8px;
}
.qa-badge {
    display: inline-block; background: #312e81; color: #a5b4fc;
    padding: 2px 10px; border-radius: 12px; font-size: 11px;
    font-weight: 600; margin-bottom: 8px;
}
.qa-question { font-size: 15px; font-weight: 600; color: #e2e8f0; margin-bottom: 4px; }
.qa-why { font-size: 12px; color: #64748b; font-style: italic; margin: 0; }
.char-count { font-size: 11px; text-align: right; margin-top: 2px; }

.step-bar { display: flex; gap: 0; margin-bottom: 20px; border-radius: 8px; overflow: hidden; }
.step { flex: 1; padding: 10px; text-align: center; font-size: 12px; font-weight: 600; }
.step-done   { background: #166534; color: #bbf7d0; }
.step-active { background: #4338ca; color: #c7d2fe; }
.step-pending { background: #1e293b; color: #475569; }

.disclaimer {
    background: #1c1917; border: 1px solid #a16207;
    border-radius: 10px; padding: 12px 14px; margin: 10px 0;
    font-size: 12px; color: #fbbf24; line-height: 1.6;
}
.submit-hint { font-size: 12px; color: #64748b; margin-top: 6px; }

.dl-row { display: flex; gap: 12px; margin-top: 14px; flex-wrap: wrap; }
.dl-btn-xlsx {
    display: inline-block; background: linear-gradient(135deg,#16a34a,#15803d);
    color: white !important; padding: 10px 22px; border-radius: 8px;
    text-decoration: none !important; font-weight: 600; font-size: 14px;
    box-shadow: 0 4px 14px rgba(22,163,74,.35);
}
.dl-btn-csv {
    display: inline-block; background: linear-gradient(135deg,#0284c7,#0369a1);
    color: white !important; padding: 10px 22px; border-radius: 8px;
    text-decoration: none !important; font-weight: 600; font-size: 14px;
    box-shadow: 0 4px 14px rgba(2,132,199,.35);
}
</style>
""", unsafe_allow_html=True)


# ── Session state ──────────────────────────────────────────────────────────────
DEFAULTS = {
    "stage": "upload",
    "session_id": None,
    "questions": [],
    "answers": {},
    "messages": [],
    "files_processed": [],
    "result": None,
    "confluence_verified": False,
    "confluence_user": "",
    "api_key": "",
    "pending_files": [],
    "lang": "en",
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

lang = st.session_state.lang


def reset():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()


def add_msg(role, content, extra=None):
    msg = {"role": role, "content": content}
    if extra:
        msg.update(extra)
    st.session_state.messages.append(msg)


def b64_download_link(b64_data: str, filename: str, label: str, btn_class: str) -> str:
    """Create an HTML download link from base64 data."""
    if filename.endswith(".xlsx"):
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        mime = "text/csv"
    href = f"data:{mime};base64,{b64_data}"
    return f'<a href="{href}" download="{filename}" class="{btn_class}">{label}</a>'


def render_messages():
    import re
    for msg in st.session_state.messages:
        content = msg["content"]
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        content = content.replace("\n", "<br>")
        cls = "msg-user" if msg["role"] == "user" else "msg-assistant"
        dl_html = ""
        if msg.get("xlsx_b64") and msg.get("csv_b64"):
            dl_html = f"""<div class="dl-row">
                {b64_download_link(msg['xlsx_b64'], msg['xlsx_filename'], t('dl_xlsx', lang), 'dl-btn-xlsx')}
                {b64_download_link(msg['csv_b64'], msg['csv_filename'], t('dl_csv', lang), 'dl-btn-csv')}
            </div>"""
        st.markdown(f'<div class="{cls}">{content}{dl_html}</div>', unsafe_allow_html=True)


# ── Step bar ───────────────────────────────────────────────────────────────────
stage = st.session_state.stage
stages = ["upload", "questionnaire", "generating", "done"]
labels = [t("step_upload", lang), t("step_qa", lang), t("step_generate", lang), t("step_done", lang)]

cur_idx = stages.index(stage) if stage in stages else 0
bar = '<div class="step-bar">'
for i, label in enumerate(labels):
    cls = "step-done" if i < cur_idx else ("step-active" if i == cur_idx else "step-pending")
    bar += f'<div class="step {cls}">{label}</div>'
bar += "</div>"
st.markdown(bar, unsafe_allow_html=True)
st.markdown(f'<p style="color:#e2e8f0;font-size:22px;font-weight:700;margin-bottom:6px;">{t("app_title", lang)}</p>', unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Language selector
    lang_choice = st.selectbox(
        t("lang_label", lang),
        options=list(LANG_OPTIONS.keys()),
        index=list(LANG_OPTIONS.values()).index(st.session_state.lang),
    )
    new_lang = LANG_OPTIONS[lang_choice]
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        lang = new_lang
        st.rerun()

    st.markdown("---")
    st.markdown(f"### {t('sidebar_openai', lang)}")
    api_key = st.text_input(
        t("api_key_label", lang), type="password",
        placeholder=t("api_key_placeholder", lang),
        value=st.session_state.api_key,
        help=t("api_key_help", lang),
    )
    if api_key:
        st.session_state.api_key = api_key

    st.markdown("---")
    st.markdown(f"### {t('sidebar_confluence', lang)}")

    conf_url = st.text_input(t("conf_url_label", lang), placeholder=t("conf_url_placeholder", lang), key="conf_url")
    conf_key = st.text_input(t("conf_key_label", lang), type="password", key="conf_key")
    conf_uid = st.text_input(t("conf_uid_label", lang), placeholder=t("conf_uid_placeholder", lang), key="conf_uid")
    conf_page = st.text_input(t("conf_page_label", lang), placeholder="123456", key="conf_page")
    conf_space = st.text_input(t("conf_space_label", lang), placeholder="ENG", key="conf_space")

    if conf_url or conf_key or conf_uid:
        st.markdown(f'<div class="disclaimer">{t("conf_disclaimer", lang)}</div>', unsafe_allow_html=True)

    if conf_url and conf_key and conf_uid:
        if st.button(t("verify_btn", lang), use_container_width=True):
            with st.spinner(t("verifying", lang)):
                try:
                    resp = requests.post(
                        f"{BACKEND_URL}/verify-confluence",
                        json={"confluence_url": conf_url, "confluence_api_key": conf_key, "confluence_user_id": conf_uid},
                        timeout=15,
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        st.session_state.confluence_verified = True
                        st.session_state.confluence_user = data["user_display_name"]
                        st.success(f"✅ {data['user_display_name']}")
                    else:
                        st.session_state.confluence_verified = False
                        st.error(f"❌ {resp.json().get('detail','Error')}")
                except Exception as e:
                    st.error(f"❌ {e}")

    if st.session_state.confluence_verified:
        st.success(f"{t('verified_as', lang)} {st.session_state.confluence_user}")

    st.markdown("---")
    st.markdown(f"### {t('sidebar_docs', lang)}")
    uploaded = st.file_uploader(
        "Upload", type=ALLOWED_TYPES, accept_multiple_files=True, label_visibility="collapsed",
    )
    if uploaded:
        existing = {f.name for f in st.session_state.pending_files}
        for f in uploaded:
            if f.name not in existing:
                st.session_state.pending_files.append(f)
                existing.add(f.name)

    if st.session_state.pending_files:
        st.markdown(t("queued_label", lang))
        to_rm = []
        for i, f in enumerate(st.session_state.pending_files):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"`{f.name}`")
            if c2.button("✕", key=f"rm_{i}"):
                to_rm.append(i)
        for i in reversed(to_rm):
            st.session_state.pending_files.pop(i)
        if to_rm:
            st.rerun()

    st.markdown("---")
    if st.button(t("start_over", lang), use_container_width=True):
        reset()


# ══════════════════════════════════════════════════════════════════════════════
# STAGE: upload
# ══════════════════════════════════════════════════════════════════════════════
if stage == "upload":
    if not st.session_state.messages:
        add_msg("assistant", t("welcome_msg", lang))
        st.rerun()

    render_messages()
    st.markdown("---")

    chips = " ".join(
        f'<span style="background:#334155;color:#94a3b8;padding:3px 10px;border-radius:12px;font-size:12px;margin:2px">📎 {f.name}</span>'
        for f in st.session_state.pending_files
    )
    if chips:
        st.markdown(chips, unsafe_allow_html=True)
    else:
        st.markdown(f'<span style="color:#475569;font-size:13px">{t("no_files_queued", lang)}</span>', unsafe_allow_html=True)

    st.markdown("")
    analyse_clicked = st.button(t("analyse_btn", lang), type="primary", use_container_width=False)

    if analyse_clicked:
        if not st.session_state.api_key:
            st.error(t("api_key_error", lang))
            st.stop()
        if not st.session_state.pending_files and not (conf_url and conf_key and conf_uid and (conf_page or conf_space)):
            st.error(t("no_content_error", lang))
            st.stop()

        files_snap = list(st.session_state.pending_files)
        names = [f.name for f in files_snap]
        add_msg("user", f"Analyse: {', '.join(names) if names else 'Confluence content'}")

        with st.spinner(t("analysing_spinner", lang)):
            try:
                form_data = {
                    "openai_api_key": st.session_state.api_key,
                    "confluence_url": conf_url or "",
                    "confluence_api_key": conf_key or "",
                    "confluence_user_id": conf_uid or "",
                    "confluence_page_id": conf_page or "",
                    "confluence_space_key": conf_space or "",
                }
                file_tuples = [("files", (f.name, f.getvalue(), f.type)) for f in files_snap]
                resp = requests.post(
                    f"{BACKEND_URL}/analyze",
                    data=form_data,
                    files=file_tuples if file_tuples else None,
                    timeout=120,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.session_id = data["session_id"]
                    st.session_state.questions = data["questions"]
                    st.session_state.files_processed = data["files_processed"]
                    st.session_state.answers = {}

                    q_count = data["question_count"]
                    file_list = "\n".join(f"- {f}" for f in data["files_processed"])
                    msg = f"✅ Ingested **{len(data['files_processed'])} source(s)**:\n{file_list}\n\n📝 {data['doc_summary']}\n\n"
                    if q_count > 0:
                        msg += f"I found **{q_count} gap(s)**. Please answer the questions below."
                    else:
                        msg += "The spec looks comprehensive — proceeding to generation."
                    add_msg("assistant", msg)
                    st.session_state.pending_files = []
                    st.session_state.stage = "questionnaire"
                    st.rerun()
                else:
                    detail = resp.json().get("detail", resp.text)
                    add_msg("assistant", f"❌ **Error:** {detail}")
                    st.rerun()
            except requests.exceptions.ConnectionError:
                add_msg("assistant", t("conn_error", lang))
                st.rerun()
            except Exception as e:
                add_msg("assistant", f"❌ {e}")
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STAGE: questionnaire
# ══════════════════════════════════════════════════════════════════════════════
elif stage == "questionnaire":
    render_messages()
    questions = st.session_state.questions

    if not questions:
        st.session_state.stage = "generating"
        st.rerun()

    st.markdown("---")
    st.markdown(f'<p style="color:#a5b4fc;font-size:15px;font-weight:600;margin-bottom:14px">{t("qa_prompt", lang)}</p>', unsafe_allow_html=True)

    CAT_COLORS = {
        "Functional": "#312e81", "Edge Case": "#4c1d95", "Integration": "#1e3a5f",
        "Security": "#7f1d1d", "Performance": "#1c4532", "Data Validation": "#713f12",
    }

    for q in questions:
        qid = str(q["id"])
        cat = q.get("category", "Functional")
        badge_bg = CAT_COLORS.get(cat, "#312e81")
        current = st.session_state.answers.get(qid, "")

        st.markdown(f"""
        <div class="qa-card">
            <span class="qa-badge" style="background:{badge_bg}">Q{q['id']} · {cat}</span>
            <p class="qa-question">{q['question']}</p>
            <p class="qa-why">{t('why_matters', lang)} {q.get('why_needed','')}</p>
        </div>""", unsafe_allow_html=True)

        answer = st.text_area(
            f"q_{qid}", value=current, max_chars=1000, height=80,
            placeholder=t("answer_placeholder", lang),
            key=f"ta_{qid}", label_visibility="collapsed",
        )
        st.session_state.answers[qid] = answer
        char_count = len(answer)
        color = "#ef4444" if char_count > 900 else "#64748b"
        st.markdown(f'<p class="char-count" style="color:{color}">{char_count}/1000 {t("char_limit", lang)}</p>', unsafe_allow_html=True)

    st.markdown("---")

    # Count non-empty answers
    answered_count = sum(1 for a in st.session_state.answers.values() if a.strip())
    can_submit = answered_count >= 2

    col1, col2 = st.columns([2, 1])
    with col2:
        if st.button(t("skip_btn", lang), use_container_width=True):
            st.session_state.answers = {}
            add_msg("user", "Skipped Q&A — proceeding to generation.")
            add_msg("assistant", "✅ Skipped. Building knowledge graph now...")
            st.session_state.stage = "generating"
            st.rerun()
    with col1:
        submit = st.button(
            t("submit_btn", lang), type="primary",
            use_container_width=True, disabled=not can_submit,
        )
        if not can_submit:
            st.markdown(f'<p class="submit-hint">{t("submit_hint", lang)}</p>', unsafe_allow_html=True)

    if submit:
        add_msg("user", f"Submitted {answered_count} answer(s).")
        add_msg("assistant", "✅ Got it! Building the knowledge graph and generating test cases now...")
        st.session_state.stage = "generating"
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STAGE: generating
# ══════════════════════════════════════════════════════════════════════════════
elif stage == "generating":
    render_messages()

    with st.spinner(t("generating_spinner", lang)):
        try:
            form_data = {
                "session_id": st.session_state.session_id,
                "answers": json.dumps(st.session_state.answers),
            }
            resp = requests.post(f"{BACKEND_URL}/generate", data=form_data, timeout=300)
            if resp.status_code == 200:
                data = resp.json()
                add_msg("assistant", data["content"], extra={
                    "xlsx_b64": data["xlsx_b64"],
                    "csv_b64": data["csv_b64"],
                    "xlsx_filename": data["xlsx_filename"],
                    "csv_filename": data["csv_filename"],
                })
                st.session_state.result = data
                st.session_state.stage = "done"
                st.rerun()
            else:
                detail = resp.json().get("detail", resp.text)
                add_msg("assistant", f"❌ **Generation failed:** {detail}")
                st.session_state.stage = "upload"
                st.rerun()
        except requests.exceptions.ConnectionError:
            add_msg("assistant", t("conn_error", lang))
            st.session_state.stage = "upload"
            st.rerun()
        except Exception as e:
            add_msg("assistant", f"❌ {e}")
            st.session_state.stage = "upload"
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# STAGE: done
# ══════════════════════════════════════════════════════════════════════════════
elif stage == "done":
    render_messages()

    result = st.session_state.result
    if result:
        stats = result.get("stats", {})
        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric(t("test_cases_metric", lang), stats.get("total", 0))
        c2.metric(t("features_metric", lang), stats.get("features_found", 0))
        c3.metric(t("edge_cases_metric", lang), stats.get("edge_cases_found", 0))
        c4.metric(t("user_roles_metric", lang), stats.get("user_roles_found", 0))

        st.markdown("---")
        st.markdown(f'<p style="color:#a5b4fc;font-weight:600;font-size:14px">{t("download_ready", lang)}</p>', unsafe_allow_html=True)
        dl_html = f"""<div class="dl-row">
            {b64_download_link(result['xlsx_b64'], result['xlsx_filename'], t('dl_xlsx', lang), 'dl-btn-xlsx')}
            {b64_download_link(result['csv_b64'], result['csv_filename'], t('dl_csv', lang), 'dl-btn-csv')}
        </div>"""
        st.markdown(dl_html, unsafe_allow_html=True)
