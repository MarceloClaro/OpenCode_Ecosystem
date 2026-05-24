"""Tela de Configurações — edita schema e configurações de modelo."""
import streamlit as st
from src import synthesis, llm
from src.config import Config


def render():
    st.header("Configurações")

    tab_schema, tab_model, tab_categorias = st.tabs(["📜 Schema", "🤖 Modelo (Ollama)", "📁 Categorias"])

    with tab_schema:
        _render_schema_tab()

    with tab_model:
        _render_model_tab()

    with tab_categorias:
        _render_categories_tab()


def _render_schema_tab():
    st.subheader("Schema da wiki")
    st.caption(
        "O schema define como o LLM mantém a wiki: princípios, convenções, tom. "
        "Equivalente ao `CLAUDE.md` do padrão original. Edite à medida que descobre o que funciona melhor para seu domínio."
    )

    # Lê o schema atual do disco (source of truth)
    current = synthesis.get_schema()

    # Widget SEM key — assim podemos controlar o valor via 'value=' livremente.
    # Usamos uma chave própria 'pending_schema_reset' para forçar refresh quando necessário.
    if st.session_state.get("pending_schema_reset"):
        # Após reset, current já reflete o default — limpa o flag
        del st.session_state["pending_schema_reset"]

    new_schema = st.text_area(
        "Schema",
        value=current,
        height=600,
    )

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("💾 Salvar", type="primary", use_container_width=True):
            synthesis.save_schema(new_schema)
            st.success("Schema atualizado!")
    with col2:
        if st.button("🔄 Restaurar default", use_container_width=True):
            synthesis.reset_schema()
            # Marca para o próximo rerun pegar o novo valor do disco
            st.session_state["pending_schema_reset"] = True
            st.success("Schema restaurado.")
            st.rerun()


def _render_model_tab():
    st.subheader("Configuração do Ollama")
    cfg = Config.load()

    new_host = st.text_input("Host do Ollama", value=cfg.ollama_host)

    available = llm.list_models()
    if available:
        st.success(f"✅ Conectado. {len(available)} modelo(s) disponível(is) localmente.")
        st.caption(f"Modelos detectados: {', '.join(available)}")

        col1, col2 = st.columns(2)
        with col1:
            new_main = st.selectbox(
                "Modelo principal (síntese, queries)",
                options=available,
                index=available.index(cfg.model_main) if cfg.model_main in available else 0,
            )
        with col2:
            new_light = st.selectbox(
                "Modelo leve (tarefas simples)",
                options=available,
                index=available.index(cfg.model_light) if cfg.model_light in available else 0,
            )
    else:
        st.error(
            "❌ Não foi possível conectar ao Ollama. Verifique se ele está rodando "
            f"em `{cfg.ollama_host}`. Para iniciar: `ollama serve` no terminal."
        )
        new_main = st.text_input("Modelo principal", value=cfg.model_main)
        new_light = st.text_input("Modelo leve", value=cfg.model_light)

    new_temp = st.slider("Temperatura", 0.0, 1.0, value=cfg.temperature, step=0.05)

    new_embedding = st.text_input(
        "Modelo de embeddings (sentence-transformers)",
        value=cfg.embedding_model,
        help="Roda local, separado do Ollama. Default: all-MiniLM-L6-v2 (rápido, multilingual).",
    )

    if st.button("💾 Salvar configuração", type="primary"):
        cfg.ollama_host = new_host
        cfg.model_main = new_main
        cfg.model_light = new_light
        cfg.temperature = new_temp
        cfg.embedding_model = new_embedding
        cfg.save()
        st.success("Configuração salva. Recarregue a página para aplicar.")


def _render_categories_tab():
    st.subheader("Categorias da wiki")
    st.caption("Defina as subpastas em data/wiki/. Reordenar/renomear pode quebrar wikilinks existentes.")

    cfg = Config.load()
    cats_text = st.text_area(
        "Uma categoria por linha",
        value="\n".join(cfg.categories),
        height=200,
    )

    if st.button("💾 Salvar categorias", type="primary"):
        new_cats = [c.strip() for c in cats_text.splitlines() if c.strip()]
        if new_cats:
            cfg.categories = new_cats
            cfg.save()
            from src.config import ensure_dirs
            ensure_dirs()
            st.success(f"Categorias salvas: {new_cats}")
        else:
            st.warning("Pelo menos uma categoria é obrigatória.")

    st.divider()
    st.subheader("Manutenção do índice")
    st.caption(
        "O índice SQLite é construído automaticamente conforme você ingere fontes. "
        "Use estas ações apenas se editar arquivos markdown fora da app ou se algo parecer dessincronizado."
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Reescanear pasta wiki/", help="Indexa arquivos .md no disco que ainda não estão no índice. Não duplica nem sobrescreve páginas existentes."):
            from src import storage
            result = storage.reconcile_filesystem()
            st.success(
                f"Reescaneamento concluído: {result['found']} arquivos encontrados, "
                f"{result['added_to_index']} adicionados ao índice, "
                f"{result['already_indexed']} já indexados."
            )

    with col2:
        if st.button("⚠️ Resetar índice (mantém arquivos)", help="Apaga TODAS as entradas do SQLite. Os arquivos markdown em data/wiki/ não são tocados. Útil se o índice ficar inconsistente."):
            confirm = st.session_state.get("_confirm_reset_index", False)
            if not confirm:
                st.session_state["_confirm_reset_index"] = True
                st.warning("Clique novamente para confirmar.")
            else:
                from src import storage
                with storage.get_conn() as conn:
                    conn.execute("DELETE FROM pages")
                    conn.execute("DELETE FROM wikilinks")
                st.session_state["_confirm_reset_index"] = False
                st.success("Índice resetado. Use 'Reescanear' para recriar a partir do disco.")
