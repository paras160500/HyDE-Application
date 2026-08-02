#==========================================================================================
#                                   Import Statements
#==========================================================================================

import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _clean_html(s: str) -> str:
    """Strip leading whitespace from every line of an HTML block.

    Streamlit's st.markdown() runs content through a Markdown parser before
    honoring unsafe_allow_html=True. Markdown treats any line starting with
    4+ spaces as a code block, and Python's indentation inside triple-quoted
    f-strings introduces exactly that whitespace. Without this, HTML blocks
    randomly render as literal escaped text instead of actual markup.
    """
    return "\n".join(line.strip() for line in s.strip("\n").split("\n"))

#==========================================================================================
#                                   Configuration
#==========================================================================================

BACKEND_URL = os.getenv("BACKEND_URL")

st.set_page_config(
    page_title="HyDE RAG Studio",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

#==========================================================================================
#                                   Global Styling
#==========================================================================================

st.markdown(_clean_html("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root{
  --bg:            #f5f6fb;
  --bg-soft:       #eef0f9;
  --surface:       #ffffff;
  --surface-2:     #fbfbfe;
  --border:        #e6e8f2;
  --border-soft:   #eef0f7;
  --text:          #1c1e2b;
  --text-dim:      #5a5d72;
  --text-mute:     #8b8ea3;
  --indigo:        #6d5ef8;
  --indigo-soft:   #efecff;
  --indigo-dark:   #4c3fd6;
  --emerald:       #10b981;
  --emerald-soft:  #e6fbf3;
  --amber:         #f59e0b;
  --amber-soft:    #fff6e5;
  --rose:          #f43f5e;
  --rose-soft:     #ffeef0;
  --blue:          #3b82f6;
  --blue-soft:     #eaf2ff;
  --shadow-sm:     0 1px 3px rgba(30, 30, 60, 0.06);
  --shadow-md:     0 8px 24px rgba(30, 30, 60, 0.08);
  --shadow-lg:     0 16px 40px rgba(30, 30, 60, 0.12);
  --radius:        18px;
}

html, body, [class*="css"], .stMarkdown, p, span, div {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
code, .doc-id, .mono { font-family: 'JetBrains Mono', monospace !important; }

/* ---------------------------------------------------------------- */
/* base app                                                          */
/* ---------------------------------------------------------------- */
.stApp {
    background:
        radial-gradient(circle at 8% 0%, #eee9ff 0%, transparent 45%),
        radial-gradient(circle at 95% 10%, #e6fbf3 0%, transparent 40%),
        var(--bg);
}
.block-container{
    padding-top: 1.5rem;
    padding-bottom: 4rem;
    max-width: 1180px;
}
section[data-testid="stSidebar"] > div{ padding-top: 0.5rem; }
h1, h2, h3, h4, h5 { color: var(--text) !important; }
p, li, label, span { color: var(--text-dim); }

/* ---------------------------------------------------------------- */
/* animations                                                         */
/* ---------------------------------------------------------------- */
@keyframes fadeSlideUp { from{opacity:0; transform:translateY(14px);} to{opacity:1; transform:translateY(0);} }
@keyframes fadeIn      { from{opacity:0;} to{opacity:1;} }
@keyframes floatY      { 0%,100%{transform:translateY(0px);} 50%{transform:translateY(-6px);} }
@keyframes shimmer     { 0%{background-position:-450px 0;} 100%{background-position:450px 0;} }
@keyframes popIn       { 0%{opacity:0; transform:scale(0.92);} 100%{opacity:1; transform:scale(1);} }
@keyframes underlineGrow { from{width:0;} to{width:46px;} }

/* ---------------------------------------------------------------- */
/* hero                                                                */
/* ---------------------------------------------------------------- */
.hero-wrap{ animation: fadeSlideUp 0.6s ease; margin-bottom: 8px; }
.hero-badge{
    display:inline-flex; align-items:center; gap:6px;
    background: var(--indigo-soft); color: var(--indigo-dark);
    font-size:0.74rem; font-weight:700; letter-spacing:0.04em;
    padding: 5px 14px; border-radius: 999px; text-transform:uppercase;
    margin-bottom: 14px;
}
.hero-title{
    font-size: 2.5rem; font-weight: 800; color: var(--text);
    margin: 0; line-height:1.15; letter-spacing:-0.02em;
}
.hero-title .accent{
    background: linear-gradient(90deg, var(--indigo), #a78bfa 60%, var(--emerald));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.hero-sub{ color: var(--text-mute); font-size: 1.02rem; margin-top:8px; max-width:640px; }

/* ---------------------------------------------------------------- */
/* cards                                                               */
/* ---------------------------------------------------------------- */
.card{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 26px 28px;
    box-shadow: var(--shadow-sm);
    animation: fadeSlideUp 0.5s ease both;
    margin-bottom: 20px;
}
.card:hover{ box-shadow: var(--shadow-md); }

.section-eyebrow{
    display:flex; align-items:center; gap:10px;
    font-size: 0.72rem; font-weight: 800; letter-spacing: 0.09em;
    text-transform: uppercase; color: var(--text-mute);
    margin-bottom: 14px;
}
.section-eyebrow .line{ flex:1; height:1px; background: var(--border); }

/* ---------------------------------------------------------------- */
/* metric tiles                                                       */
/* ---------------------------------------------------------------- */
.metric-tile{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px 18px;
    text-align:center;
    box-shadow: var(--shadow-sm);
    animation: fadeSlideUp 0.55s ease both;
    transition: transform .2s ease, box-shadow .2s ease;
}
.metric-tile:hover{ transform: translateY(-3px); box-shadow: var(--shadow-md); }
.metric-icon{ font-size:1.4rem; margin-bottom:6px; display:inline-block; animation: floatY 3.5s ease-in-out infinite; }
.metric-value{ font-size: 1.7rem; font-weight: 800; color: var(--text); }
.metric-label{ color: var(--text-mute); font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 3px; font-weight:600; }

/* ---------------------------------------------------------------- */
/* answer box                                                         */
/* ---------------------------------------------------------------- */
.answer-box{
    background: linear-gradient(155deg, var(--indigo-soft) 0%, #ffffff 65%);
    border: 1px solid #ded7ff;
    border-radius: 18px;
    padding: 24px 26px;
    margin-bottom: 20px;
    animation: fadeSlideUp 0.5s ease both;
    position: relative;
    overflow:hidden;
}
.answer-box::before{
    content:"";
    position:absolute; top:-40px; right:-40px;
    width:130px; height:130px; border-radius:50%;
    background: radial-gradient(circle, rgba(109,94,248,0.14), transparent 70%);
}
.answer-head{
    display:flex; align-items:center; gap:8px;
    font-weight: 800; color: var(--indigo-dark); font-size: 0.92rem;
    margin-bottom: 10px;
}
.answer-text{ color: var(--text); font-size: 1rem; line-height: 1.7; position:relative; z-index:1; }

/* ---------------------------------------------------------------- */
/* hyde draft box                                                     */
/* ---------------------------------------------------------------- */
.hyde-box{
    background: var(--emerald-soft);
    border: 1px dashed #8fe2c3;
    border-radius: 16px;
    padding: 18px 20px;
    color: #0d6b4c;
    font-size: 0.9rem;
    font-style: italic;
    line-height: 1.6;
    margin-bottom: 18px;
    animation: fadeIn 0.7s ease;
}
.hyde-head{
    font-style: normal; font-weight: 800; text-transform: uppercase;
    letter-spacing: 0.06em; font-size: 0.72rem; color: #0a8f61;
    margin-bottom: 8px; display:flex; align-items:center; gap:6px;
}

/* ---------------------------------------------------------------- */
/* doc cards                                                          */
/* ---------------------------------------------------------------- */
.doc-card{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 14px;
    animation: fadeSlideUp 0.45s ease both;
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    position: relative;
    box-shadow: var(--shadow-sm);
}
.doc-card:hover{ transform: translateY(-2px); box-shadow: var(--shadow-md); border-color:#d9d4ff; }
.doc-card.accent-indigo{ border-left: 4px solid var(--indigo); }
.doc-card.accent-emerald{ border-left: 4px solid var(--emerald); }

.doc-top{ display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; flex-wrap:wrap; gap:8px;}
.doc-id{
    font-size: 0.74rem; font-weight: 700; color: var(--text-mute);
    background: var(--bg-soft); padding: 3px 10px; border-radius: 8px;
}
.doc-score{
    font-size: 0.72rem; font-weight: 800; color: var(--indigo-dark);
    background: var(--indigo-soft); padding: 3px 10px; border-radius: 999px;
}
.doc-text{ color: var(--text); font-size: 0.92rem; line-height: 1.6; margin: 4px 0 10px 0; }

.chip{
    display:inline-block; font-size:0.68rem; font-weight:700;
    padding: 3px 11px; border-radius: 999px; margin-right:6px; margin-top:4px;
    letter-spacing:0.02em;
}
.chip-topic{ background: var(--blue-soft); color: #1d5fd6; }
.chip-source{ background: var(--amber-soft); color: #b4740a; }
.chip-exclusive-h{ background: var(--emerald-soft); color: #0a8f61; }
.chip-exclusive-s{ background: var(--indigo-soft); color: var(--indigo-dark); }

/* ---------------------------------------------------------------- */
/* compare headers                                                    */
/* ---------------------------------------------------------------- */
.method-header{
    display:flex; align-items:center; gap:12px;
    padding: 14px 18px;
    border-radius: 16px;
    margin-bottom: 16px;
    font-weight: 800;
    font-size: 1.15rem;
    animation: popIn 0.4s ease both;
}
.method-header .emoji{ font-size:1.5rem; }
.method-header .sub{ font-size:0.78rem; font-weight:600; opacity:0.85; display:block; margin-top:2px;}
.method-header-standard{
    background: linear-gradient(135deg, var(--indigo-soft), #f5f3ff);
    color: var(--indigo-dark);
    border: 1px solid #ded7ff;
}
.method-header-hyde{
    background: linear-gradient(135deg, var(--emerald-soft), #f2fffb);
    color: #0a8f61;
    border: 1px solid #b9f0d8;
}

.found-tag{
    display:flex; align-items:center; gap:6px;
    font-size: 0.72rem; font-weight: 800; text-transform: uppercase; letter-spacing:0.04em;
    padding: 5px 12px; border-radius: 999px; margin-top:8px; width:fit-content;
}
.found-tag-hyde{ background:#0a8f61; color:white; }
.found-tag-standard{ background: var(--indigo-dark); color:white; }

/* ---------------------------------------------------------------- */
/* status pill / sidebar                                              */
/* ---------------------------------------------------------------- */
section[data-testid="stSidebar"]{
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container{ padding-top: 1.6rem; }

.brand{ display:flex; align-items:center; gap:10px; margin-bottom: 4px; animation: fadeSlideUp 0.5s ease; }
.brand-icon{
    width:40px; height:40px; border-radius:12px;
    background: linear-gradient(135deg, var(--indigo), #a78bfa);
    display:flex; align-items:center; justify-content:center;
    font-size:1.2rem; box-shadow: 0 6px 16px rgba(109,94,248,0.35);
}
.brand-name{ font-weight:800; font-size:1.15rem; color:var(--text); line-height:1.1; }
.brand-tag{ font-size:0.74rem; color:var(--text-mute); font-weight:600; }

.status-pill{
    display:flex; align-items:center; gap:8px;
    padding: 9px 14px; border-radius: 12px;
    font-weight: 700; font-size: 0.82rem;
    animation: fadeIn 0.5s ease;
    border: 1px solid;
}
.status-ok{ background: var(--emerald-soft); color:#0a8f61; border-color:#b9f0d8; }
.status-bad{ background: var(--rose-soft); color:#c81e3f; border-color:#ffd2da; }
.dot{ width:8px; height:8px; border-radius:50%; background:currentColor; animation: floatY 1.4s ease-in-out infinite; }

.side-stat{
    display:flex; justify-content:space-between; align-items:center;
    padding: 8px 0; border-bottom: 1px solid var(--border-soft);
    font-size: 0.82rem;
}
.side-stat:last-child{ border-bottom:none; }
.side-stat .k{ color: var(--text-mute); font-weight:600; }
.side-stat .v{ color: var(--text); font-weight:700; font-family:'JetBrains Mono', monospace; font-size:0.78rem; }

/* nav buttons in sidebar (override the CTA gradient style used elsewhere) */
section[data-testid="stSidebar"] .stButton{ margin-bottom: 2px; }
section[data-testid="stSidebar"] .stButton>button{
    background: transparent !important;
    color: var(--text) !important;
    box-shadow: none !important;
    border: 1px solid transparent !important;
    text-align: left !important;
    justify-content: flex-start !important;
    padding: 11px 14px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    border-radius: 12px !important;
    transform: none !important;
}
section[data-testid="stSidebar"] .stButton>button p{ color: var(--text) !important; text-align:left !important; font-weight:600 !important; }
section[data-testid="stSidebar"] .stButton>button:hover{
    background: var(--bg-soft) !important;
    box-shadow: none !important;
    transform: none !important;
}
section[data-testid="stSidebar"] .stButton>button[kind="primary"]{
    background: var(--indigo-soft) !important;
    border: 1px solid #ded7ff !important;
}
section[data-testid="stSidebar"] .stButton>button[kind="primary"] p{
    color: var(--indigo-dark) !important;
    font-weight: 800 !important;
}

/* ---------------------------------------------------------------- */
/* buttons / inputs                                                    */
/* ---------------------------------------------------------------- */
.stButton>button,
div[data-testid="stFormSubmitButton"]>button,
.stFormSubmitButton>button{
    background: linear-gradient(135deg, var(--indigo), #8a7cfb) !important;
    color: white !important; border: none !important;
    border-radius: 12px !important; padding: 12px 22px !important;
    font-weight: 700 !important; font-size:0.94rem !important;
    box-shadow: 0 6px 18px rgba(109,94,248,0.3) !important;
    transition: transform .15s ease, box-shadow .15s ease;
}
.stButton>button:hover,
div[data-testid="stFormSubmitButton"]>button:hover,
.stFormSubmitButton>button:hover{
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(109,94,248,0.42) !important;
    color:white !important;
}
.stButton>button p,
div[data-testid="stFormSubmitButton"]>button p,
.stFormSubmitButton>button p{ color:white !important; }

/* re-apply the flat nav look inside the sidebar, overriding the CTA gradient above */
section[data-testid="stSidebar"] .stButton>button{
    background: transparent !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton>button:hover{
    background: var(--bg-soft) !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton>button p{ color: var(--text) !important; }
section[data-testid="stSidebar"] .stButton>button[kind="primary"]{
    background: var(--indigo-soft) !important;
}
section[data-testid="stSidebar"] .stButton>button[kind="primary"] p{ color: var(--indigo-dark) !important; }

/* kill any theme-default red/black focus rings on buttons everywhere */
.stButton>button:focus,
.stButton>button:focus-visible,
div[data-testid="stFormSubmitButton"]>button:focus,
div[data-testid="stFormSubmitButton"]>button:focus-visible{
    outline: none !important;
    box-shadow: 0 0 0 3px var(--indigo-soft) !important;
}

.stTextInput input, .stTextArea textarea, .stNumberInput input{
    background: var(--surface-2) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus{
    border-color: var(--indigo) !important;
    box-shadow: 0 0 0 3px var(--indigo-soft) !important;
}
.stSlider [data-baseweb="slider"] div div div{ background: var(--indigo) !important; }

div[data-baseweb="tab-list"]{ gap: 4px; border-bottom: 1px solid var(--border); }
button[data-baseweb="tab"]{
    border-radius: 10px 10px 0 0 !important;
    font-weight: 700 !important;
}

hr{ border-color: var(--border) !important; }

/* native spinner -> indigo, matching theme */
div[data-testid="stSpinner"] > div{ border-top-color: var(--indigo) !important; }
div[data-testid="stSpinner"] p{ color: var(--text-dim) !important; font-weight: 600 !important; }

/* scrollbar */
::-webkit-scrollbar{ width:8px; height:8px; }
::-webkit-scrollbar-thumb{ background: #d6d1fb; border-radius: 8px; }
::-webkit-scrollbar-thumb:hover{ background: var(--indigo); }

/* misc streamlit chrome cleanup */
#MainMenu, footer{ visibility:hidden; }
[data-testid="stDecoration"]{ display:none; }
header[data-testid="stHeader"]{ display:none !important; }
div[data-testid="stToolbar"]{ display:none !important; }
div[data-testid="stStatusWidget"]{ display:none !important; }
.stAppDeployButton{ display:none !important; }

/* neutralize streamlit's default (theme-dependent) input/slider accents */
div[data-baseweb="input"], div[data-baseweb="textarea"], div[data-baseweb="base-input"]{
    border-radius: 12px !important;
    border-color: var(--border) !important;
}
div[data-baseweb="input"]:focus-within,
div[data-baseweb="textarea"]:focus-within,
div[data-baseweb="base-input"]:focus-within{
    border-color: var(--indigo) !important;
    box-shadow: 0 0 0 3px var(--indigo-soft) !important;
}
textarea, input{ outline: none !important; caret-color: var(--indigo) !important; }

/* slider: force indigo instead of the default red accent */
.stSlider [data-baseweb="slider"] > div > div{ background: var(--border) !important; }
.stSlider [data-baseweb="slider"] > div > div > div{ background: var(--indigo) !important; }
.stSlider [role="slider"]{
    background: var(--indigo) !important;
    border-color: var(--indigo) !important;
    box-shadow: 0 0 0 4px var(--indigo-soft) !important;
}
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"]{ color: var(--text-mute) !important; }
div[data-testid="stThumbValue"]{ color: var(--indigo-dark) !important; font-weight: 700 !important; }

/* checkboxes / radios / focus rings app-wide -> indigo, never red/black */
*:focus{ outline-color: var(--indigo) !important; }
::selection{ background: var(--indigo-soft); color: var(--indigo-dark); }

</style>
""").strip(), unsafe_allow_html=True)

#==========================================================================================
#                                   Helper Functions
#==========================================================================================

def api_post(path: str, payload: dict):
    try:
        resp = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=60)
        resp.raise_for_status()
        return resp.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)


def api_get(path: str):
    try:
        resp = requests.get(f"{BACKEND_URL}{path}", timeout=15)
        resp.raise_for_status()
        return resp.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)


def render_doc_card(doc: dict, index: int, accent: str = "indigo", exclusive_tag: str = None):
    doc_id = doc.get("id", "unknown")
    metadata = doc.get("metadata", {}) or {}
    text = metadata.get("text") or doc.get("text") or ""
    score = doc.get("score")
    topic = metadata.get("topic")
    source = metadata.get("source")

    chips = ""
    if topic:
        chips += f'<span class="chip chip-topic">📌 {topic}</span>'
    if source:
        chips += f'<span class="chip chip-source">🗂 {source}</span>'

    score_html = f'<span class="doc-score">⚡ {score:.3f}</span>' if score is not None else ""

    tag_html = ""
    if exclusive_tag == "hyde":
        tag_html = '<div class="found-tag found-tag-hyde">🟢 Only found by HyDE</div>'
    elif exclusive_tag == "standard":
        tag_html = '<div class="found-tag found-tag-standard">🟣 Only found by Standard</div>'

    st.markdown(_clean_html(f"""
    <div class="doc-card accent-{accent}" style="animation-delay:{index * 0.05}s;">
        <div class="doc-top">
            <span class="doc-id">📄 {doc_id}</span>
            {score_html}
        </div>
        <div class="doc-text">{text}</div>
        <div>{chips}</div>
        {tag_html}
    </div>
    """).strip(), unsafe_allow_html=True)


def render_answer(answer: str):
    st.markdown(_clean_html(f"""
    <div class="answer-box">
        <div class="answer-head">✨ Generated Answer</div>
        <div class="answer-text">{answer}</div>
    </div>
    """).strip(), unsafe_allow_html=True)


def render_hyde_box(hdoc: str):
    st.markdown(_clean_html(f"""
    <div class="hyde-box">
        <div class="hyde-head">🪄 Hypothetical Document Used for Embedding</div>
        {hdoc}
    </div>
    """).strip(), unsafe_allow_html=True)


def render_docs_section(title: str, docs: list, icon: str = "📚", accent="indigo", exclusive_ids=None):
    exclusive_ids = exclusive_ids or set()
    st.markdown(_clean_html(f"""
    <div class="section-eyebrow">{icon} {title} · {len(docs)} retrieved<div class="line"></div></div>
    """).strip(), unsafe_allow_html=True)
    if not docs:
        st.info("No documents retrieved.")
        return
    for i, d in enumerate(docs):
        tag = None
        if d.get("id") in exclusive_ids:
            tag = "hyde" if accent == "emerald" else "standard"
        render_doc_card(d, i, accent=accent, exclusive_tag=tag)


def section_eyebrow(text, icon="◆"):
    st.markdown(_clean_html(f"""
    <div class="section-eyebrow">{icon} {text}<div class="line"></div></div>
    """).strip(), unsafe_allow_html=True)

#==========================================================================================
#                                   Sidebar
#==========================================================================================

with st.sidebar:
    st.markdown(_clean_html("""
    <div class="brand">
        <div class="brand-icon">🧬</div>
        <div>
            <div class="brand-name">HyDE RAG</div>
            <div class="brand-tag">Studio Console</div>
        </div>
    </div>
    """).strip(), unsafe_allow_html=True)

    st.write("")

    NAV_ITEMS = [
        ("overview", "🏠  Overview"),
        ("standard", "🎯  Standard Query"),
        ("hyde", "🧪  HyDE Query"),
        ("compare", "⚖️  Compare"),
        ("ingest", "📥  Ingest Data"),
    ]
    if "page" not in st.session_state:
        st.session_state.page = "overview"

    for key, label in NAV_ITEMS:
        is_active = st.session_state.page == key
        if st.button(label, key=f"nav_{key}", use_container_width=True,
                     type="primary" if is_active else "secondary"):
            st.session_state.page = key
            st.rerun()

    page = st.session_state.page

    st.write("")
    st.markdown('<div class="section-eyebrow">Connection<div class="line"></div></div>', unsafe_allow_html=True)

    health_data, health_err = api_get("/health")
    if health_data:
        st.markdown('<div class="status-pill status-ok"><span class="dot"></span> Backend Online</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-pill status-bad"><span class="dot"></span> Backend Offline</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown(_clean_html(f"""
    <div style="background:var(--surface-2); border:1px solid var(--border); border-radius:14px; padding:14px 16px;">
        <div class="side-stat"><span class="k">Endpoint</span></div>
        <div class="mono" style="font-size:0.72rem; color:var(--text-mute); word-break:break-all; margin-bottom:8px;">{BACKEND_URL}</div>
        <div class="side-stat"><span class="k">LLM Model</span><span class="v">{health_data.get('groq_model','—') if health_data else '—'}</span></div>
        <div class="side-stat"><span class="k">Embeddings</span><span class="v">{health_data.get('embedding_model','—') if health_data else '—'}</span></div>
        <div class="side-stat"><span class="k">Vectors</span><span class="v">{health_data.get('total_vectors',0) if health_data else 0}</span></div>
    </div>
    """).strip(), unsafe_allow_html=True)

    if health_err:
        st.caption(f"⚠️ {health_err}")

#==========================================================================================
#                                   Header
#==========================================================================================

st.markdown(_clean_html("""
<div class="hero-wrap">
    <div class="hero-badge">🧬 Retrieval Playground</div>
    <div class="hero-title">HyDE <span class="accent">RAG</span> Studio</div>
    <div class="hero-sub">Explore Standard vs. Hypothetical-Document-Embedding retrieval, side by side — with real answers, real context, and full transparency into what each method finds.</div>
</div>
""").strip(), unsafe_allow_html=True)
st.write("")

#==========================================================================================
#                                   Page: Overview
#==========================================================================================

if page == "overview":
    total_vectors = 0
    if health_data:
        total_vectors = health_data.get("total_vector_count", health_data.get("total_vectors", 0))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(_clean_html(f"""<div class="metric-tile"><div class="metric-icon">🗂️</div>
            <div class="metric-value">{total_vectors}</div>
            <div class="metric-label">Vectors Indexed</div></div>""").strip(), unsafe_allow_html=True)
    with c2:
        st.markdown(_clean_html(f"""<div class="metric-tile"><div class="metric-icon">🧠</div>
            <div class="metric-value" style="font-size:1.05rem;">{health_data.get('groq_model','—') if health_data else '—'}</div>
            <div class="metric-label">LLM Model</div></div>""").strip(), unsafe_allow_html=True)
    with c3:
        st.markdown(_clean_html(f"""<div class="metric-tile"><div class="metric-icon">🧩</div>
            <div class="metric-value" style="font-size:1.05rem;">{health_data.get('embedding_model','—') if health_data else '—'}</div>
            <div class="metric-label">Embedding Model</div></div>""").strip(), unsafe_allow_html=True)

    st.write("")
    st.write("")

    a, b, c = st.columns(3)
    with a:
        st.markdown(_clean_html("""
        <div class="card">
            <div style="font-size:1.6rem; margin-bottom:8px;">🎯</div>
            <div style="font-weight:800; font-size:1.05rem; color:var(--text); margin-bottom:6px;">Standard RAG</div>
            <p style="font-size:0.9rem; line-height:1.6;">Embeds your raw query directly and searches Pinecone for the closest matching passages.</p>
        </div>
        """).strip(), unsafe_allow_html=True)
    with b:
        st.markdown(_clean_html("""
        <div class="card">
            <div style="font-size:1.6rem; margin-bottom:8px;">🧪</div>
            <div style="font-weight:800; font-size:1.05rem; color:var(--text); margin-bottom:6px;">HyDE RAG</div>
            <p style="font-size:0.9rem; line-height:1.6;">Generates a hypothetical answer first, embeds <em>that</em> instead, then searches — often surfacing richer context.</p>
        </div>
        """).strip(), unsafe_allow_html=True)
    with c:
        st.markdown(_clean_html("""
        <div class="card">
            <div style="font-size:1.6rem; margin-bottom:8px;">⚖️</div>
            <div style="font-weight:800; font-size:1.05rem; color:var(--text); margin-bottom:6px;">Compare</div>
            <p style="font-size:0.9rem; line-height:1.6;">Runs both methods together and highlights exactly which documents each one finds that the other misses.</p>
        </div>
        """).strip(), unsafe_allow_html=True)

#==========================================================================================
#                                   Page: Standard Query
#==========================================================================================

elif page == "standard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_eyebrow("Ask something", "🎯")
    query = st.text_area("Ask a question", placeholder="e.g. How does HyDE improve retrieval?", height=90, label_visibility="collapsed")
    col1, col2 = st.columns([1, 1])
    with col1:
        top_k = st.slider("Top K documents", 1, 10, 5)
    with col2:
        namespace = st.text_input("Namespace (optional)", value="", placeholder="default")
    run = st.button("Run Standard Query  →", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if run:
        if not query.strip():
            st.warning("Please enter a query first.")
        else:
            with st.spinner("⏳ Embedding query & searching Pinecone..."):
                data, err = api_post("/query/standard", {"query": query, "top_k": top_k, "namespace": namespace})
            if err:
                st.error(f"Request failed: {err}")
            else:
                render_answer(data.get("answer", ""))
                render_docs_section("Retrieved Documents", data.get("retrieved_docs", []), accent="indigo")

#==========================================================================================
#                                   Page: HyDE Query
#==========================================================================================

elif page == "hyde":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_eyebrow("Ask something", "🧪")
    query = st.text_area("Ask a question", placeholder="e.g. Why do vector databases matter for RAG?", height=90, label_visibility="collapsed")
    col1, col2 = st.columns([1, 1])
    with col1:
        top_k = st.slider("Top K documents", 1, 10, 5)
    with col2:
        namespace = st.text_input("Namespace (optional)", value="", placeholder="default")
    run = st.button("Run HyDE Query  →", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if run:
        if not query.strip():
            st.warning("Please enter a query first.")
        else:
            with st.spinner("⏳ Generating hypothetical document & searching Pinecone..."):
                data, err = api_post("/query/hyde", {"query": query, "top_k": top_k, "namespace": namespace})
            if err:
                st.error(f"Request failed: {err}")
            else:
                render_hyde_box(data.get("hypothetical_doc", ""))
                render_answer(data.get("answer", ""))
                render_docs_section("Retrieved Documents", data.get("retrieved_docs", []), accent="emerald")

#==========================================================================================
#                                   Page: Compare
#==========================================================================================

elif page == "compare":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_eyebrow("Head-to-head comparison", "⚖️")
    query = st.text_area("Ask a question to compare both methods", placeholder="e.g. What is reranking in retrieval?", height=90, label_visibility="collapsed")
    col1, col2 = st.columns([1, 1])
    with col1:
        top_k = st.slider("Top K documents", 1, 10, 5)
    with col2:
        namespace = st.text_input("Namespace (optional)", value="", placeholder="default")
    run = st.button("Compare Standard vs HyDE  →", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if run:
        if not query.strip():
            st.warning("Please enter a query first.")
        else:
            with st.spinner("⏳ Running both retrieval strategies..."):
                data, err = api_post("/query/compare", {"query": query, "top_k": top_k, "namespace": namespace})
            if err:
                st.error(f"Request failed: {err}")
            else:
                analysis = data.get("analysis", {})
                unique_hyde = set(analysis.get("unique_to_hyde", []))
                unique_std = set(analysis.get("unique_to_standard", []))

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown(_clean_html(f"""<div class="metric-tile"><div class="metric-icon">🔗</div>
                        <div class="metric-value">{analysis.get('overlap_count', 0)}</div>
                        <div class="metric-label">Overlapping Docs</div></div>""").strip(), unsafe_allow_html=True)
                with m2:
                    st.markdown(_clean_html(f"""<div class="metric-tile"><div class="metric-icon">🟢</div>
                        <div class="metric-value">{len(unique_hyde)}</div>
                        <div class="metric-label">Unique to HyDE</div></div>""").strip(), unsafe_allow_html=True)
                with m3:
                    st.markdown(_clean_html(f"""<div class="metric-tile"><div class="metric-icon">🟣</div>
                        <div class="metric-value">{len(unique_std)}</div>
                        <div class="metric-label">Unique to Standard</div></div>""").strip(), unsafe_allow_html=True)

                st.write("")
                st.write("")

                std = data.get("standard", {})
                hyde = data.get("hyde", {})

                left, right = st.columns(2, gap="large")

                with left:
                    st.markdown(_clean_html("""
                    <div class="method-header method-header-standard">
                        <span class="emoji">🎯</span>
                        <div>STANDARD RAG<span class="sub">Raw query embedding</span></div>
                    </div>
                    """).strip(), unsafe_allow_html=True)
                    render_answer(std.get("answer", ""))
                    render_docs_section("Retrieved Documents", std.get("retrieved_docs", []), accent="indigo", exclusive_ids=unique_std)

                with right:
                    st.markdown(_clean_html("""
                    <div class="method-header method-header-hyde">
                        <span class="emoji">🧪</span>
                        <div>HYDE RAG<span class="sub">Hypothetical document embedding</span></div>
                    </div>
                    """).strip(), unsafe_allow_html=True)
                    render_hyde_box(hyde.get("hypothetical_doc", ""))
                    render_answer(hyde.get("answer", ""))
                    render_docs_section("Retrieved Documents", hyde.get("retrieved_docs", []), accent="emerald", exclusive_ids=unique_hyde)

#==========================================================================================
#                                   Page: Ingest Data
#==========================================================================================

elif page == "ingest":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    section_eyebrow("Add documents to your batch", "📥")

    if "ingest_batch" not in st.session_state:
        st.session_state.ingest_batch = []

    with st.form("add_doc_form", clear_on_submit=True):
        doc_id = st.text_input("Document ID", placeholder="doc_031")
        doc_text = st.text_area("Document Text", placeholder="Paste the document content here...", height=110)
        c1, c2 = st.columns(2)
        with c1:
            topic = st.text_input("Metadata: topic", placeholder="rag")
        with c2:
            source = st.text_input("Metadata: source", placeholder="overview")
        add_clicked = st.form_submit_button("➕  Add to Batch", use_container_width=True)

    if add_clicked:
        if not doc_id.strip() or not doc_text.strip():
            st.warning("Document ID and text are required.")
        else:
            st.session_state.ingest_batch.append({
                "id": doc_id.strip(),
                "text": doc_text.strip(),
                "metadata": {k: v for k, v in {"topic": topic, "source": source}.items() if v},
            })
            st.success(f"Added '{doc_id}' to batch.")

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.ingest_batch:
        section_eyebrow(f"Pending Batch · {len(st.session_state.ingest_batch)} docs", "🗂️")
        for i, d in enumerate(st.session_state.ingest_batch):
            render_doc_card({"id": d["id"], "metadata": {**d["metadata"], "text": d["text"]}}, i, accent="indigo")

        namespace = st.text_input("Target namespace (optional)", value="", placeholder="default")
        colA, colB = st.columns([1, 1])
        with colA:
            upsert_clicked = st.button("🚀  Upsert Batch to Pinecone", use_container_width=True)
        with colB:
            clear_clicked = st.button("🗑️  Clear Batch", use_container_width=True)

        if clear_clicked:
            st.session_state.ingest_batch = []
            st.rerun()

        if upsert_clicked:
            with st.spinner("⏳ Embedding & upserting documents into Pinecone..."):
                data, err = api_post("/ingest", {"documents": st.session_state.ingest_batch, "namespace": namespace})
            if err:
                st.error(f"Ingest failed: {err}")
            else:
                st.session_state.ingest_batch = []
                st.session_state.ingest_success = f"✅ Upserted {data.get('upserted', 0)} documents into namespace '{data.get('namespace')}'."
                st.rerun()
    else:
        st.info("Your batch is empty — add a document above to get started.")
        if st.session_state.get("ingest_success"):
            st.balloons()
            st.success(st.session_state.pop("ingest_success"))