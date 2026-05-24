"""LLM Wiki MVP — aplicação Streamlit single-page com navegação por sidebar.

Como rodar:
    streamlit run app.py

Pré-requisitos:
    - Ollama rodando local (ollama serve)
    - Pelo menos um modelo baixado (ex: ollama pull llama3.1:8b)
"""
import streamlit as st

from src.config import ensure_dirs
from src import storage
from src.ui import (
    ingest_page,
    chat_page,
    browser_page,
    graph_page,
    lint_page,
    settings_page,
)


def main():
    st.set_page_config(
        page_title="LLM Wiki",
        page_icon="📚",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Garante que pastas e DB existem
    ensure_dirs()

    # Limpeza de paths corrompidos (legado de versão anterior com bug Windows).
    # Roda apenas uma vez por sessão.
    if "paths_cleaned" not in st.session_state:
        try:
            result = storage.cleanup_corrupted_paths()
            if result["removed_duplicates"] or result["renamed"] or result["fixed_wikilinks"]:
                st.toast(
                    f"🧹 Limpeza: {result['removed_duplicates']} duplicada(s) removida(s), "
                    f"{result['renamed']} renomeada(s).",
                    icon="✅"
                )
        except Exception:
            pass
        st.session_state["paths_cleaned"] = True

    # Reconciliação leve: só na primeira vez que o app roda numa sessão.
    # E só se o índice estiver vazio mas há .md no disco (caso de import manual).
    if "filesystem_reconciled" not in st.session_state:
        try:
            existing_pages = storage.list_pages()
            if not existing_pages:
                # Índice vazio — vale escanear o disco
                storage.reconcile_filesystem()
        except Exception:
            pass
        st.session_state["filesystem_reconciled"] = True

    # Sidebar: navegação
    st.sidebar.title("📚 LLM Wiki")
    st.sidebar.caption("Alternativa ao RAG tradicional — knowledge base que acumula")

    page = st.sidebar.radio(
        "Navegação",
        options=["Ingestão", "Chat", "Wiki", "Graph", "Lint", "Configurações"],
        label_visibility="collapsed",
    )

    # Stats rápidas no sidebar
    st.sidebar.divider()
    pages_count = len(storage.list_pages())
    sources = storage.list_sources()
    pending = sum(1 for s in sources if not s["ingested_at"])
    ingested = sum(1 for s in sources if s["ingested_at"])

    st.sidebar.metric("Páginas na wiki", pages_count)
    st.sidebar.metric("Fontes ingeridas", ingested)
    if pending:
        st.sidebar.metric("Fontes pendentes", pending)

    st.sidebar.divider()
    st.sidebar.caption("ℹ️ Tudo roda local. Dados em `./data/`.")

    # Roteamento
    if page == "Ingestão":
        ingest_page.render()
    elif page == "Chat":
        chat_page.render()
    elif page == "Wiki":
        browser_page.render()
    elif page == "Graph":
        graph_page.render()
    elif page == "Lint":
        lint_page.render()
    elif page == "Configurações":
        settings_page.render()


if __name__ == "__main__":
    main()
