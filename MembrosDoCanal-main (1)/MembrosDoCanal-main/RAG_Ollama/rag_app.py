# -*- coding: utf-8 -*-
"""
RAG Frontend — Streamlit
Estética: dark editorial, tipografia forte, interface refinada tipo "research terminal"
"""

import os
import time
import streamlit as st

# ── Page config (MUST be first Streamlit call) ───────────────────────────────
st.set_page_config(
    page_title="RAG · Consultor de Documentos",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0c0d0f !important;
    color: #e8e3d8 !important;
    font-family: 'Lora', Georgia, serif !important;
}

[data-testid="stSidebar"] {
    background: #111316 !important;
    border-right: 1px solid #1e2128 !important;
}

[data-testid="stSidebar"] > div { padding: 2rem 1.4rem !important; }

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding: 2.5rem 3rem 4rem !important; max-width: 900px !important; }

/* ── Typography ── */
h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; letter-spacing: -0.02em; }

/* ── Hero header ── */
.hero {
    display: flex;
    align-items: baseline;
    gap: 1rem;
    margin-bottom: 0.25rem;
}
.hero-glyph {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    color: #c8a96e;
    line-height: 1;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #e8e3d8;
    line-height: 1;
}
.hero-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #4a5060;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, #c8a96e 0%, #1e2128 60%);
    margin: 1.8rem 0;
}

/* ── Sidebar labels ── */
.sidebar-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #4a5060;
    margin-bottom: 0.4rem;
}

/* ── Status badge ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.3rem 0.7rem;
    border-radius: 2px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.status-ready   { background: #0f2318; border: 1px solid #1f5c38; color: #4caf7d; }
.status-waiting { background: #1e1506; border: 1px solid #4a3200; color: #c8a96e; }
.status-error   { background: #1e0a0a; border: 1px solid #5c1f1f; color: #e05c5c; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

/* ── Answer card ── */
.answer-card {
    background: #111316;
    border: 1px solid #1e2128;
    border-left: 3px solid #c8a96e;
    border-radius: 2px;
    padding: 1.6rem 1.8rem;
    margin: 1.5rem 0;
    font-family: 'Lora', Georgia, serif;
    font-size: 1.0rem;
    line-height: 1.8;
    color: #d4cfc5;
    white-space: pre-wrap;
}

/* ── Source card ── */
.source-card {
    background: #0e1014;
    border: 1px solid #1a1d24;
    border-radius: 2px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.6rem;
    display: flex;
    align-items: flex-start;
    gap: 0.9rem;
}
.source-index {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    color: #c8a96e;
    background: #1a1506;
    border: 1px solid #3a2d0a;
    padding: 0.2rem 0.45rem;
    border-radius: 2px;
    flex-shrink: 0;
    margin-top: 2px;
}
.source-info { flex: 1; }
.source-file {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #8a9ab0;
    margin-bottom: 0.2rem;
}
.source-page {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #3a4050;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.source-excerpt {
    font-family: 'Lora', serif;
    font-size: 0.78rem;
    font-style: italic;
    color: #555c6a;
    margin-top: 0.4rem;
    line-height: 1.5;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

/* ── Question display ── */
.question-display {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: #c8a96e;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1e2128;
    margin-bottom: 0.5rem;
}

/* ── Section label ── */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #3a4050;
    margin-bottom: 0.7rem;
}

/* ── History item ── */
.history-item {
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.4rem;
    background: #0e1014;
    border: 1px solid #191c22;
    border-radius: 2px;
    cursor: pointer;
    transition: border-color 0.15s;
}
.history-item:hover { border-color: #c8a96e55; }
.history-q {
    font-family: 'Lora', serif;
    font-size: 0.82rem;
    color: #8a9ab0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.history-meta {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #2e3340;
    margin-top: 0.25rem;
}

/* ── Streamlit widget overrides ── */
[data-testid="stFileUploader"] {
    background: #0e1014 !important;
    border: 1px dashed #2a2e38 !important;
    border-radius: 2px !important;
    padding: 0.5rem !important;
}
[data-testid="stFileUploader"]:hover { border-color: #c8a96e55 !important; }

.stTextArea textarea {
    background: #0e1014 !important;
    border: 1px solid #1e2128 !important;
    border-radius: 2px !important;
    color: #e8e3d8 !important;
    font-family: 'Lora', serif !important;
    font-size: 0.95rem !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: #c8a96e !important;
    box-shadow: 0 0 0 1px #c8a96e33 !important;
}

.stButton button {
    background: #c8a96e !important;
    color: #0c0d0f !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.55rem 1.4rem !important;
    transition: opacity 0.15s !important;
}
.stButton button:hover { opacity: 0.85 !important; }

[data-testid="stSelectbox"] > div > div {
    background: #0e1014 !important;
    border: 1px solid #1e2128 !important;
    color: #e8e3d8 !important;
    border-radius: 2px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}
[data-testid="stSlider"] .stSlider { color: #c8a96e !important; }

.stSpinner > div { border-top-color: #c8a96e !important; }

/* ── Metric boxes ── */
.metric-row { display: flex; gap: 1rem; margin: 1rem 0; }
.metric-box {
    flex: 1;
    background: #0e1014;
    border: 1px solid #1a1d24;
    padding: 0.8rem 1rem;
    border-radius: 2px;
}
.metric-val {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #c8a96e;
}
.metric-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #3a4050;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.1rem;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0c0d0f; }
::-webkit-scrollbar-thumb { background: #2a2e38; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #c8a96e55; }
</style>
""", unsafe_allow_html=True)


# ── Lazy imports (compatível com langchain_classic) ───────────────────────────
@st.cache_resource(show_spinner=False)
def load_deps():
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain_classic.chains import RetrievalQA
    from langchain_ollama import ChatOllama, OllamaEmbeddings
    return PyPDFLoader, RecursiveCharacterTextSplitter, FAISS, RetrievalQA, ChatOllama, OllamaEmbeddings


# ── Session state ─────────────────────────────────────────────────────────────
if "history"    not in st.session_state: st.session_state.history    = []
if "vectordb"   not in st.session_state: st.session_state.vectordb   = None
if "qa_chain"   not in st.session_state: st.session_state.qa_chain   = None
if "pdf_name"   not in st.session_state: st.session_state.pdf_name   = None
if "n_chunks"   not in st.session_state: st.session_state.n_chunks   = 0
if "n_pages"    not in st.session_state: st.session_state.n_pages    = 0


# ═════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="hero-glyph">◈</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:Syne,sans-serif;font-weight:700;font-size:1.1rem;color:#e8e3d8;margin-bottom:0.1rem;">RAG Terminal</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#2e3340;letter-spacing:0.14em;text-transform:uppercase;margin-bottom:2rem;">Retrieval-Augmented Generation</div>', unsafe_allow_html=True)

    # ── PDF Upload ──
    st.markdown('<div class="sidebar-label">Documento PDF</div>', unsafe_allow_html=True)
    uploaded_pdf = st.file_uploader("Documento PDF", type=["pdf"], label_visibility="hidden")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Model settings ──
    st.markdown('<div class="sidebar-label">Modelo LLM</div>', unsafe_allow_html=True)
    llm_model = st.text_input("Modelo LLM", value="granite4:latest", label_visibility="hidden",
                               placeholder="ex: granite4:latest, llama3:latest")

    st.markdown('<div class="sidebar-label" style="margin-top:0.8rem;">Embeddings</div>', unsafe_allow_html=True)
    emb_model = st.text_input("Embeddings", value="nomic-embed-text:latest", label_visibility="hidden",
                               placeholder="ex: nomic-embed-text:latest")

    st.markdown('<div class="sidebar-label" style="margin-top:0.8rem;">Temperatura</div>', unsafe_allow_html=True)
    temperature = st.slider("Temperatura", 0.0, 1.0, 0.3, 0.05, label_visibility="hidden")

    st.markdown('<div class="sidebar-label" style="margin-top:0.8rem;">Chunks recuperados (k)</div>', unsafe_allow_html=True)
    k_docs = st.slider("Chunks recuperados (k)", 1, 10, 4, 1, label_visibility="hidden")

    st.markdown('<div class="sidebar-label" style="margin-top:0.8rem;">Chunk size</div>', unsafe_allow_html=True)
    chunk_size = st.slider("Chunk size", 200, 2000, 1000, 100, label_visibility="hidden")

    st.markdown('<div class="sidebar-label" style="margin-top:0.8rem;">Chunk overlap</div>', unsafe_allow_html=True)
    chunk_overlap = st.slider("Chunk overlap", 0, 400, 150, 25, label_visibility="hidden")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    # ── Build index button ──
    build_btn = st.button("⬡  Indexar Documento", use_container_width=True)

    # ── Status ──
    if st.session_state.vectordb:
        st.markdown(f'<div class="status-badge status-ready"><span class="dot"></span>Índice pronto — {st.session_state.pdf_name}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-waiting"><span class="dot"></span>Aguardando documento</div>', unsafe_allow_html=True)

    # ── Clear history ──
    if st.session_state.history:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        if st.button("✕  Limpar histórico", use_container_width=True):
            st.session_state.history = []
            st.rerun()


# ═════════════════════════════════════════════════════════════════════════════
# BUILD INDEX
# ═════════════════════════════════════════════════════════════════════════════
if build_btn:
    if not uploaded_pdf:
        st.error("Nenhum PDF carregado. Faça upload na barra lateral.")
    else:
        try:
            PyPDFLoader, RecursiveCharacterTextSplitter, FAISS, RetrievalQA, ChatOllama, OllamaEmbeddings = load_deps()

            with st.spinner("Processando documento…"):
                tmp_path = f"/tmp/{uploaded_pdf.name}"
                with open(tmp_path, "wb") as f:
                    f.write(uploaded_pdf.read())

                loader = PyPDFLoader(tmp_path)
                docs   = loader.load()

                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    separators=["\n\n", "\n", " ", ""],
                )
                chunks = splitter.split_documents(docs)

            with st.spinner("Gerando embeddings…"):
                embeddings = OllamaEmbeddings(model=emb_model)
                vectordb   = FAISS.from_documents(chunks, embeddings)
                retriever  = vectordb.as_retriever(search_kwargs={"k": k_docs})

            with st.spinner("Carregando LLM…"):
                llm = ChatOllama(model=llm_model, temperature=temperature)
                qa_chain = RetrievalQA.from_chain_type(
                    llm=llm,
                    retriever=retriever,
                    chain_type="stuff",
                    return_source_documents=True,
                )

            st.session_state.vectordb  = vectordb
            st.session_state.qa_chain  = qa_chain
            st.session_state.pdf_name  = uploaded_pdf.name
            st.session_state.n_chunks  = len(chunks)
            st.session_state.n_pages   = len(docs)
            st.success(f"Documento indexado com sucesso! {len(docs)} páginas · {len(chunks)} chunks")
            st.rerun()

        except Exception as e:
            st.markdown(f'<div class="status-badge status-error"><span class="dot"></span>Erro: {e}</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# MAIN PANEL
# ═════════════════════════════════════════════════════════════════════════════

# ── Hero ──
st.markdown("""
<div class="hero">
    <span class="hero-glyph">◈</span>
    <span class="hero-title">Consultor de Documentos</span>
</div>
<div class="hero-sub">Retrieval-Augmented Generation · Ollama · FAISS</div>
""", unsafe_allow_html=True)

# ── Metrics (when indexed) ──
if st.session_state.vectordb:
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box">
            <div class="metric-val">{st.session_state.n_pages}</div>
            <div class="metric-lbl">Páginas</div>
        </div>
        <div class="metric-box">
            <div class="metric-val">{st.session_state.n_chunks}</div>
            <div class="metric-lbl">Chunks</div>
        </div>
        <div class="metric-box">
            <div class="metric-val">{len(st.session_state.history)}</div>
            <div class="metric-lbl">Consultas</div>
        </div>
        <div class="metric-box">
            <div class="metric-val">{k_docs}</div>
            <div class="metric-lbl">k retrieval</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Query input ──
st.markdown('<div class="section-label">Nova consulta</div>', unsafe_allow_html=True)
query = st.text_area(
    "Pergunta",
    placeholder="Faça uma pergunta sobre o documento indexado…",
    height=100,
    label_visibility="hidden",
    key="query_input",
)

col1, col2 = st.columns([1, 5])
with col1:
    ask_btn = st.button("Enviar →", use_container_width=True)

# ── Process query ──
if ask_btn and query.strip():
    if not st.session_state.qa_chain:
        st.markdown('<div class="status-badge status-error"><span class="dot"></span>Nenhum documento indexado. Use a barra lateral.</div>', unsafe_allow_html=True)
    else:
        with st.spinner("Consultando…"):
            t0 = time.time()
            result = st.session_state.qa_chain.invoke({"query": query.strip()})
            elapsed = time.time() - t0

        entry = {
            "question": query.strip(),
            "answer":   result["result"],
            "sources":  result.get("source_documents", []),
            "elapsed":  elapsed,
        }
        st.session_state.history.insert(0, entry)
        st.rerun()

elif ask_btn and not query.strip():
    st.warning("Digite uma pergunta antes de enviar.")

# ── Display history ──
if st.session_state.history:
    for idx, entry in enumerate(st.session_state.history):
        # Question
        st.markdown(f'<div class="question-display">❝ {entry["question"]} ❞</div>', unsafe_allow_html=True)

        # Timing badge
        st.markdown(
            f'<div style="font-family:JetBrains Mono,monospace;font-size:0.62rem;color:#3a4050;margin-bottom:0.6rem;">'
            f'tempo de resposta — {entry["elapsed"]:.2f}s</div>',
            unsafe_allow_html=True,
        )

        # Answer
        st.markdown(f'<div class="answer-card">{entry["answer"]}</div>', unsafe_allow_html=True)

        # Sources
        if entry["sources"]:
            st.markdown('<div class="section-label" style="margin-top:1rem;">Fontes recuperadas</div>', unsafe_allow_html=True)
            for i, doc in enumerate(entry["sources"], start=1):
                src   = doc.metadata.get("source", "—")
                page  = doc.metadata.get("page", "N/A")
                fname = os.path.basename(src) if src != "—" else "—"
                excerpt = doc.page_content[:180].replace("\n", " ").strip()
                st.markdown(f"""
                <div class="source-card">
                    <span class="source-index">#{i:02d}</span>
                    <div class="source-info">
                        <div class="source-file">{fname}</div>
                        <div class="source-page">página {page}</div>
                        <div class="source-excerpt">{excerpt}…</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if idx < len(st.session_state.history) - 1:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

else:
    # Empty state
    st.markdown("""
    <div style="text-align:center;padding:4rem 2rem;color:#2a2e38;">
        <div style="font-size:3rem;margin-bottom:1rem;">◈</div>
        <div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:600;color:#3a4050;margin-bottom:0.5rem;">
            Nenhuma consulta ainda
        </div>
        <div style="font-family:JetBrains Mono,monospace;font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;color:#2a2e38;">
            Carregue um PDF · indexe · pergunte
        </div>
    </div>
    """, unsafe_allow_html=True)
