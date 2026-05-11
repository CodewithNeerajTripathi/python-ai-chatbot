import streamlit as st
import os
import json
import datetime
import sqlite3
import pathlib
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="StudyBot AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS  — editorial dark-ink aesthetic
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist+Mono:wght@400;500;600&family=Geist:wght@300;400;500;600&display=swap');

/* ── global reset ── */
html, body, [class*="css"] {
    font-family: 'Geist', sans-serif;
    background-color: #0d0d0f !important;
    color: #e8e6e1 !important;
}

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: #111114 !important;
    border-right: 1px solid #1f1f26 !important;
}
[data-testid="stSidebar"] * { color: #c9c7c2 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    font-family: 'Instrument Serif', serif !important;
    color: #f0ede8 !important;
    font-style: italic;
}
[data-testid="stSidebarContent"] { padding: 1.5rem 1rem !important; }

/* ── main header ── */
h1 {
    font-family: 'Instrument Serif', serif !important;
    font-style: italic;
    font-size: 2.4rem !important;
    color: #f0ede8 !important;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 0 !important;
}
h2, h3, h4 {
    font-family: 'Geist', sans-serif !important;
    color: #e8e6e1 !important;
}

/* ── stat cards ── */
.stat-grid { display: flex; gap: 12px; margin: 0.75rem 0 1rem; }
.stat-card {
    flex: 1;
    background: #111114;
    border: 1px solid #1f1f26;
    border-radius: 10px;
    padding: 14px 16px;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: var(--accent);
}
.stat-card.c1 { --accent: #7c6af7; }
.stat-card.c2 { --accent: #3fba8a; }
.stat-card.c3 { --accent: #e8915a; }
.stat-number {
    font-family: 'Geist Mono', monospace;
    font-size: 1.75rem;
    font-weight: 600;
    color: #f0ede8;
    line-height: 1;
}
.stat-label {
    font-size: 0.72rem;
    color: #6b6965;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 4px;
}

/* ── topic badges ── */
.badge-row { display: flex; flex-wrap: wrap; gap: 5px; margin: 6px 0 10px; }
.badge {
    font-family: 'Geist Mono', monospace;
    font-size: 0.7rem;
    padding: 3px 9px;
    border-radius: 4px;
    border: 1px solid #2a2834;
    background: #16131f;
    color: #9d8fff;
}

/* ── history sidebar items ── */
.hist-item {
    padding: 10px 12px;
    border-radius: 8px;
    border: 1px solid #1f1f26;
    margin-bottom: 6px;
    cursor: pointer;
    transition: background 0.15s;
    background: #0d0d0f;
}
.hist-item:hover { background: #16141a; }
.hist-item.active { border-color: #7c6af7; background: #100f1a; }
.hist-title {
    font-size: 0.82rem;
    font-weight: 500;
    color: #e8e6e1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.hist-meta {
    font-family: 'Geist Mono', monospace;
    font-size: 0.68rem;
    color: #4d4b47;
    margin-top: 2px;
}

/* ── chat messages ── */
[data-testid="stChatMessage"] {
    background: #111114 !important;
    border: 1px solid #1a1a20 !important;
    border-radius: 12px !important;
    margin-bottom: 6px !important;
    padding: 4px 8px !important;
}
[data-testid="stChatMessage"][data-testid*="user"] {
    border-color: #1e1b2e !important;
    background: #0f0d18 !important;
}

/* ── chat input ── */
[data-testid="stChatInput"] {
    background: #111114 !important;
    border: 1px solid #252530 !important;
    border-radius: 12px !important;
    color: #e8e6e1 !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,0.12) !important;
}

/* ── buttons ── */
.stButton > button {
    font-family: 'Geist', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    background: #111114 !important;
    border: 1px solid #252530 !important;
    color: #c9c7c2 !important;
    border-radius: 8px !important;
    transition: all 0.15s !important;
}
.stButton > button:hover {
    background: #1a1820 !important;
    border-color: #7c6af7 !important;
    color: #e8e6e1 !important;
}
.stDownloadButton > button {
    background: #111114 !important;
    border: 1px solid #252530 !important;
    color: #c9c7c2 !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
}
.stDownloadButton > button:hover {
    border-color: #3fba8a !important;
    color: #3fba8a !important;
    background: #0b1510 !important;
}

/* ── select / text input ── */
.stSelectbox [data-baseweb="select"] > div {
    background: #111114 !important;
    border-color: #252530 !important;
    color: #c9c7c2 !important;
}
.stTextInput input {
    background: #111114 !important;
    border-color: #252530 !important;
    color: #e8e6e1 !important;
    border-radius: 8px !important;
}

/* ── summary box ── */
.summary-box {
    background: #0d1117;
    border: 1px solid #1f2937;
    border-left: 3px solid #7c6af7;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    color: #c9c7c2;
    font-size: 0.9rem;
    line-height: 1.7;
    margin: 8px 0;
}

/* ── quick starter buttons ── */
.starter-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }
.starter-btn {
    background: #111114;
    border: 1px solid #1f1f26;
    border-radius: 10px;
    padding: 12px 14px;
    font-size: 0.82rem;
    color: #9d9a95;
    cursor: pointer;
    text-align: left;
    line-height: 1.4;
    transition: all 0.15s;
    font-family: 'Geist', sans-serif;
}
.starter-btn:hover {
    border-color: #7c6af7;
    color: #e8e6e1;
    background: #100f1a;
}

/* ── section labels ── */
.section-label {
    font-family: 'Geist Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #4d4b47;
    margin: 14px 0 6px;
}

/* ── dividers ── */
hr { border-color: #1a1a20 !important; margin: 10px 0 !important; }

/* ── expander ── */
[data-testid="stExpander"] {
    background: #0d0d0f !important;
    border: 1px solid #1a1a20 !important;
    border-radius: 8px !important;
}

/* ── spinner ── */
.stSpinner > div { border-top-color: #7c6af7 !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #2a2834; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #3d3850; }

/* ── empty state illustration ── */
.empty-state {
    text-align: center;
    padding: 2rem 0;
    color: #3d3b38;
}
.empty-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 0.5rem;
    opacity: 0.4;
}
.empty-text {
    font-family: 'Instrument Serif', serif;
    font-style: italic;
    font-size: 1.1rem;
    color: #4d4b47;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# PERSISTENT HISTORY — SQLite
# ─────────────────────────────────────────────
DB_PATH = pathlib.Path("studybot_history.db")

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            model    TEXT,
            topics   TEXT,
            messages TEXT,
            saved_at TEXT
        )
    """)
    con.commit()
    con.close()

def db_save_session(name, model, topics, messages):
    """Insert or replace session by name."""
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cur.execute("SELECT id FROM sessions WHERE name=?", (name,))
    row = cur.fetchone()
    if row:
        cur.execute(
            "UPDATE sessions SET model=?,topics=?,messages=?,saved_at=? WHERE name=?",
            (model, json.dumps(topics), json.dumps(messages), now, name)
        )
    else:
        cur.execute(
            "INSERT INTO sessions (name,model,topics,messages,saved_at) VALUES (?,?,?,?,?)",
            (name, model, json.dumps(topics), json.dumps(messages), now)
        )
    con.commit()
    con.close()

def db_load_all_sessions():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT id,name,model,topics,messages,saved_at FROM sessions ORDER BY id DESC")
    rows = cur.fetchall()
    con.close()
    return rows

def db_delete_session(name):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM sessions WHERE name=?", (name,))
    con.commit()
    con.close()

init_db()

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are an expert Python & AI/ML study tutor. Help students learn clearly and patiently. "
        "Explain concepts step-by-step with simple examples, analogies, and encourage curiosity. "
        "Format code cleanly in markdown code blocks. "
        "If asked something completely unrelated, gently redirect: "
        "'I'm here to help with Python & ML learning — let's stay focused!'"
    )
}

MODELS = {
    "llama-3.1-8b-instant":    "Llama 3.1 8B  · Fast",
    "llama-3.3-70b-versatile": "Llama 3.3 70B · Smart",
    "mixtral-8x7b-32768":      "Mixtral 8x7B  · Balanced",
}

def init_state():
    defaults = {
        "history":        [SYSTEM_PROMPT],
        "session_name":   "New session",
        "message_count":  0,
        "topics_covered": [],
        "show_summary":   False,
        "model":          "llama-3.1-8b-instant",
        "loaded_session_id": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def get_visible_messages():
    return [m for m in st.session_state.history if m["role"] != "system"]

def chat_to_text():
    lines = [f"# {st.session_state.session_name}",
             f"Exported: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]
    for m in get_visible_messages():
        role = "You" if m["role"] == "user" else "StudyBot"
        lines.append(f"**{role}:** {m['content']}\n")
    return "\n".join(lines)

def chat_to_json():
    return json.dumps({
        "session":     st.session_state.session_name,
        "exported_at": datetime.datetime.now().isoformat(),
        "model":       st.session_state.model,
        "topics":      st.session_state.topics_covered,
        "messages":    get_visible_messages()
    }, indent=2)

TOPIC_MAP = {
    "list": "Lists", "dict": "Dictionaries", "loop": "Loops",
    "function": "Functions", "def ": "Functions", "class ": "OOP",
    "import": "Modules", "exception": "Error Handling", "try:": "Error Handling",
    "lambda": "Lambdas", "decorator": "Decorators", "async": "Async/Await",
    "file": "File I/O", "open(": "File I/O", "comprehension": "Comprehensions",
    "generator": "Generators", "regex": "Regex", "pandas": "Pandas",
    "numpy": "NumPy", "pytorch": "PyTorch", "sklearn": "scikit-learn",
    "neural": "Neural Nets", "model": "ML Models", "api": "APIs",
    "flask": "Flask", "django": "Django", "fastapi": "FastAPI",
}

def detect_topic(text: str):
    lower = text.lower()
    for kw, topic in TOPIC_MAP.items():
        if kw in lower and topic not in st.session_state.topics_covered:
            return topic
    return None

def ask_groq(messages):
    try:
        return client.chat.completions.create(
            model=st.session_state.model,
            messages=messages,
            stream=True
        )
    except Exception as e:
        st.error(f"API Error: {e}")
        return None

def generate_summary():
    prompt = list(st.session_state.history) + [{
        "role": "user",
        "content": (
            "In 3–4 bullet points, summarise what topics we covered and what the student learned. "
            "Be concise and encouraging. Use ✓ bullet points."
        )
    }]
    try:
        resp = client.chat.completions.create(
            model=st.session_state.model,
            messages=prompt,
            max_tokens=350
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Could not generate summary: {e}"

def new_session():
    st.session_state.history          = [SYSTEM_PROMPT]
    st.session_state.session_name     = f"Session {datetime.datetime.now().strftime('%d %b %H:%M')}"
    st.session_state.message_count    = 0
    st.session_state.topics_covered   = []
    st.session_state.show_summary     = False
    st.session_state.loaded_session_id = None

def load_db_session(row):
    _, name, model, topics_json, msgs_json, _ = row
    msgs = json.loads(msgs_json)
    topics = json.loads(topics_json)
    # Ensure system prompt at start
    if not msgs or msgs[0].get("role") != "system":
        msgs = [SYSTEM_PROMPT] + msgs
    st.session_state.history          = msgs
    st.session_state.session_name     = name
    st.session_state.model            = model
    st.session_state.topics_covered   = topics
    st.session_state.message_count    = len([m for m in msgs if m["role"] != "system"])
    st.session_state.show_summary     = False
    st.session_state.loaded_session_id = row[0]

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
        <div style="margin-bottom:1.5rem;">
            <div style="font-family:'Instrument Serif',serif;font-style:italic;
                        font-size:1.6rem;color:#f0ede8;line-height:1;">
                StudyBot
            </div>
            <div style="font-family:'Geist Mono',monospace;font-size:0.65rem;
                        color:#4d4b47;letter-spacing:0.1em;text-transform:uppercase;
                        margin-top:2px;">
                Python · AI · ML tutor
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ── Model ───────────────────────────────
    st.markdown('<div class="section-label">Model</div>', unsafe_allow_html=True)
    st.session_state.model = st.selectbox(
        "model",
        options=list(MODELS.keys()),
        format_func=lambda x: MODELS[x],
        index=list(MODELS.keys()).index(st.session_state.model),
        label_visibility="collapsed"
    )

    st.markdown('<div style="margin:12px 0 0;"></div>', unsafe_allow_html=True)

    # ── Session actions ──────────────────────
    st.markdown('<div class="section-label">Session</div>', unsafe_allow_html=True)
    st.session_state.session_name = st.text_input(
        "name", value=st.session_state.session_name, label_visibility="collapsed",
        placeholder="Session name…"
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("💾 Save", use_container_width=True):
            db_save_session(
                st.session_state.session_name,
                st.session_state.model,
                st.session_state.topics_covered,
                st.session_state.history,
            )
            st.toast("Session saved!", icon="✅")
    with col2:
        if st.button("🆕 New", use_container_width=True):
            new_session()
            st.rerun()
    with col3:
        if st.button("✨ Sum", use_container_width=True, help="Generate session summary"):
            if get_visible_messages():
                st.session_state.show_summary = True
            else:
                st.toast("Chat first!", icon="⚠️")

    st.markdown('<div style="margin:4px 0;"></div>', unsafe_allow_html=True)

    # ── Export ──────────────────────────────
    st.markdown('<div class="section-label">Export</div>', unsafe_allow_html=True)
    if get_visible_messages():
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📄 .txt", chat_to_text(),
                file_name=f"{st.session_state.session_name.replace(' ','_')}.txt",
                mime="text/plain", use_container_width=True)
        with c2:
            st.download_button("🗂 .json", chat_to_json(),
                file_name=f"{st.session_state.session_name.replace(' ','_')}.json",
                mime="application/json", use_container_width=True)
    else:
        st.caption("Chat to enable export")

    st.markdown('<hr>', unsafe_allow_html=True)

    # ── Persistent History ───────────────────
    st.markdown('<div class="section-label">History</div>', unsafe_allow_html=True)
    all_sessions = db_load_all_sessions()

    if not all_sessions:
        st.markdown('<div style="font-size:0.78rem;color:#3d3b38;padding:6px 0;">No saved sessions yet.</div>',
                    unsafe_allow_html=True)
    else:
        # Search box
        search_q = st.text_input("search history", placeholder="Search…",
                                  label_visibility="collapsed", key="hist_search")

        for row in all_sessions:
            sid, name, model, topics_json, msgs_json, saved_at = row
            if search_q and search_q.lower() not in name.lower():
                continue
            topics = json.loads(topics_json) if topics_json else []
            msgs   = json.loads(msgs_json)   if msgs_json   else []
            msg_count = len([m for m in msgs if m.get("role") != "system"])
            is_active = (sid == st.session_state.loaded_session_id)

            with st.expander(f"{'▶ ' if is_active else ''}{name}", expanded=False):
                st.caption(f"{saved_at}  ·  {msg_count} messages  ·  {MODELS.get(model,'').split('·')[0].strip()}")
                if topics:
                    badge_html = " ".join([f'<span class="badge">{t}</span>' for t in topics[:6]])
                    st.markdown(f'<div class="badge-row">{badge_html}</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Load", key=f"load_{sid}", use_container_width=True):
                        load_db_session(row)
                        st.rerun()
                with c2:
                    if st.button("Delete", key=f"del_{sid}", use_container_width=True):
                        db_delete_session(name)
                        if is_active:
                            new_session()
                        st.rerun()

    # ── Clear current chat ───────────────────
    st.markdown('<hr>', unsafe_allow_html=True)
    if st.button("🗑️ Clear current chat", use_container_width=True):
        st.session_state.history        = [SYSTEM_PROMPT]
        st.session_state.message_count  = 0
        st.session_state.topics_covered = []
        st.session_state.show_summary   = False
        st.rerun()

# ─────────────────────────────────────────────
# MAIN — Header
# ─────────────────────────────────────────────
col_title, col_model = st.columns([5, 2])
with col_title:
    st.markdown(f"<h1>{st.session_state.session_name}</h1>", unsafe_allow_html=True)
with col_model:
    st.markdown(
        f'<div style="text-align:right;padding-top:14px;font-family:\'Geist Mono\',monospace;'
        f'font-size:0.72rem;color:#4d4b47;">'
        f'{MODELS[st.session_state.model]}</div>',
        unsafe_allow_html=True
    )

# ── Stats bar ────────────────────────────────
msg_count   = len(get_visible_messages())
topic_count = len(st.session_state.topics_covered)
total_saved = len(db_load_all_sessions())

st.markdown(f"""
<div class="stat-grid">
  <div class="stat-card c1">
    <div class="stat-number">{msg_count}</div>
    <div class="stat-label">Messages</div>
  </div>
  <div class="stat-card c2">
    <div class="stat-number">{topic_count}</div>
    <div class="stat-label">Topics</div>
  </div>
  <div class="stat-card c3">
    <div class="stat-number">{total_saved}</div>
    <div class="stat-label">Saved sessions</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Topic badges ──────────────────────────────
if st.session_state.topics_covered:
    badges = " ".join([f'<span class="badge">{t}</span>' for t in st.session_state.topics_covered])
    st.markdown(f'<div class="badge-row">{badges}</div>', unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────────────
# SUMMARY BOX
# ─────────────────────────────────────────────
if st.session_state.show_summary:
    with st.spinner("Generating summary…"):
        summary_text = generate_summary()
    st.markdown(
        f'<div class="summary-box">📋 <strong style="color:#e8e6e1;">Session Summary</strong>'
        f'<br><br>{summary_text}</div>',
        unsafe_allow_html=True
    )
    if st.button("✖ Close"):
        st.session_state.show_summary = False

# ─────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────
for message in get_visible_messages():
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ─────────────────────────────────────────────
# EMPTY STATE + QUICK STARTERS
# ─────────────────────────────────────────────
if not get_visible_messages():
    st.markdown("""
        <div class="empty-state">
            <span class="empty-icon">🎓</span>
            <div class="empty-text">What would you like to learn today?</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="section-label" style="text-align:center;">Quick starters</div>',
                unsafe_allow_html=True)
    prompts = [
        "Explain Python lists vs tuples with examples",
        "How do decorators work in Python?",
        "Walk me through NumPy broadcasting",
        "Explain self-attention in transformers",
        "Show me a full PyTorch training loop",
        "What is gradient descent — visual explanation?",
    ]
    cols = st.columns(3)
    for i, p in enumerate(prompts):
        if cols[i % 3].button(p, use_container_width=True, key=f"starter_{i}"):
            st.session_state._quick_prompt = p
            st.rerun()

# ─────────────────────────────────────────────
# CHAT INPUT
# ─────────────────────────────────────────────
quick = st.session_state.pop("_quick_prompt", None)
user_input = st.chat_input("Ask anything about Python or AI/ML…") or quick

if user_input:
    # Detect topic
    topic = detect_topic(user_input)
    if topic:
        st.session_state.topics_covered.append(topic)

    with st.chat_message("user"):
        st.markdown(user_input)

    st.session_state.history.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply  = ""
        stream = ask_groq(st.session_state.history)
        if stream:
            for chunk in stream:
                delta = chunk.choices[0].delta.content or ""
                full_reply += delta
                placeholder.markdown(full_reply + "▌")
            placeholder.markdown(full_reply)

    if full_reply:
        st.session_state.history.append({"role": "assistant", "content": full_reply})
        st.session_state.message_count += 1
        # Auto-save to DB
        db_save_session(
            st.session_state.session_name,
            st.session_state.model,
            st.session_state.topics_covered,
            st.session_state.history,
        )
        st.rerun()