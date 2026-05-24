"""Tela de Browser da wiki — navegação por categoria + visualização."""
import streamlit as st
from pathlib import Path
import re
from src import storage
from src.config import Config


def _render_markdown_with_wikilinks(content: str) -> str:
    """Converte [[link]] em links que disparam navegação na wiki."""
    # Para Streamlit, vamos transformar em código inline visível
    # (clicáveis seriam complicados sem URL routing)
    def replace_link(match):
        link = match.group(1).split("|")[0].strip()
        return f"`📎 {link}`"
    return re.sub(r"\[\[([^\]]+)\]\]", replace_link, content)


def render():
    st.header("Wiki")
    st.caption("Navegue pelas páginas geradas pelo LLM. A wiki é organizada por categoria.")

    cfg = Config.load()
    categories = cfg.categories

    # Sidebar de navegação
    col_nav, col_content = st.columns([1, 3])

    with col_nav:
        st.subheader("Categorias")
        all_pages = storage.list_pages()
        if not all_pages:
            st.info("Wiki vazia. Faça upload e ingestão de fontes para começar.")
            return

        # Agrupa por categoria
        by_cat = {}
        for p in all_pages:
            by_cat.setdefault(p["category"], []).append(p)

        # Pega seleção atual
        selected_path = st.session_state.get("browser_selected_path")

        for cat in categories:
            pages_in_cat = by_cat.get(cat, [])
            with st.expander(f"📁 **{cat}** ({len(pages_in_cat)})", expanded=(len(pages_in_cat) > 0 and len(pages_in_cat) < 6)):
                for p in pages_in_cat:
                    if st.button(
                        p["title"],
                        key=f"navlink_{p['path']}",
                        use_container_width=True,
                        type="primary" if p["path"] == selected_path else "secondary",
                    ):
                        st.session_state["browser_selected_path"] = p["path"]
                        st.rerun()

        # Categorias fora das declaradas (caso o LLM crie alguma)
        unknown_cats = set(by_cat.keys()) - set(categories)
        for cat in unknown_cats:
            with st.expander(f"📁 {cat} ({len(by_cat[cat])})"):
                for p in by_cat[cat]:
                    if st.button(p["title"], key=f"navlink_{p['path']}", use_container_width=True):
                        st.session_state["browser_selected_path"] = p["path"]
                        st.rerun()

    with col_content:
        selected_path = st.session_state.get("browser_selected_path")
        if not selected_path:
            st.info("👈 Selecione uma página na barra lateral.")
            # Estatísticas resumo
            st.subheader("Visão geral")
            st.metric("Total de páginas", len(all_pages))
            st.metric("Categorias com conteúdo", len(by_cat))
            return

        page = storage.get_page(selected_path)
        if not page:
            st.error(f"Página não encontrada: `{selected_path}`")
            return

        # Header da página
        st.subheader(page["title"])
        st.caption(f"`{page['path']}` · atualizada {page['updated_at'][:16]} · {page['word_count']} palavras")

        # Botões de ação
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            edit_mode = st.toggle("✏️ Editar", key=f"edit_toggle_{selected_path}")
        with col2:
            if st.button("🗑️ Apagar", key=f"del_{selected_path}"):
                if storage.delete_page(selected_path):
                    storage.log_event("delete", f"Página apagada: {selected_path}")
                    st.session_state["browser_selected_path"] = None
                    st.rerun()

        # Modo edição vs visualização
        if edit_mode:
            new_content = st.text_area(
                "Conteúdo da página (markdown)",
                value=page["content"],
                height=500,
                key=f"editor_{selected_path}",
            )
            if st.button("💾 Salvar mudanças", key=f"save_{selected_path}", type="primary"):
                from src import llm
                try:
                    emb = llm.embed_text(new_content[:2000])
                    storage.save_page(selected_path, new_content, embedding=emb)
                    storage.log_event("edit", f"Página editada manualmente: {selected_path}")
                    st.success("Salvo!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")
        else:
            # Visualização
            st.markdown(_render_markdown_with_wikilinks(page["content"]))

            # Backlinks
            with st.expander("🔗 Páginas que linkam aqui (backlinks)"):
                with storage.get_conn() as conn:
                    rows = conn.execute(
                        "SELECT from_page FROM wikilinks WHERE to_page = ?", (selected_path,)
                    ).fetchall()
                if rows:
                    for r in rows:
                        if st.button(r["from_page"], key=f"backlink_{r['from_page']}_{selected_path}"):
                            st.session_state["browser_selected_path"] = r["from_page"]
                            st.rerun()
                else:
                    st.caption("Nenhuma página aponta para esta.")
