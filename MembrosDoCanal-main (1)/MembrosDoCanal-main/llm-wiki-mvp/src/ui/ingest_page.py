"""Tela de Upload + Ingestão.

Fluxo:
1. Usuário faz upload (1 ou vários arquivos)
2. Sistema extrai texto e marca como pendente
3. Para cada pendente, usuário pode revisar análise e confirmar ingestão
4. Confirmação aciona a integração na wiki

CORREÇÃO de duplicação:
- Streamlit re-executa o script a cada interação. Mantemos um set em
  st.session_state com hashes dos arquivos já processados para evitar
  ingestão duplicada quando o usuário interage com qualquer botão na tela.
- save_source no storage também detecta duplicata por hash (defesa em profundidade).
"""
import hashlib
import streamlit as st
from src import ingestion, synthesis, storage


def _file_signature(filename: str, content_bytes: bytes) -> str:
    """Assinatura estável: nome + hash do conteúdo."""
    h = hashlib.sha256(content_bytes).hexdigest()[:16]
    return f"{filename}::{h}"


def render():
    st.header("Ingestão de fontes")
    st.caption("Faça upload de PDFs, TXT ou Markdown. Cada arquivo vira uma fonte que pode ser ingerida na wiki.")

    # Set persistente: arquivos já processados nesta sessão
    if "processed_uploads" not in st.session_state:
        st.session_state.processed_uploads = set()

    # ---------- Upload ----------
    uploaded_files = st.file_uploader(
        "Arraste arquivos aqui ou clique para selecionar",
        type=["pdf", "txt", "md"],
        accept_multiple_files=True,
        key="upload_widget",
    )

    if uploaded_files:
        # Filtra: só processa o que ainda não foi processado nesta sessão
        new_files = []
        for uf in uploaded_files:
            content_bytes = uf.getvalue()  # NÃO usa .read() — esse consome o stream
            sig = _file_signature(uf.name, content_bytes)
            if sig not in st.session_state.processed_uploads:
                new_files.append((uf, content_bytes, sig))

        if new_files:
            with st.status(f"Processando {len(new_files)} novo(s) arquivo(s)...", expanded=True) as status:
                for uf, content_bytes, sig in new_files:
                    try:
                        result = ingestion.ingest_upload(uf.name, content_bytes)
                        st.session_state.processed_uploads.add(sig)
                        st.write(f"✅ **{uf.name}** — {result['char_count']} caracteres, source_id `{result['source_id']}`")
                    except Exception as e:
                        st.write(f"❌ **{uf.name}** — erro: {e}")
                status.update(label="Uploads concluídos", state="complete")
        # Se todos os arquivos já foram processados, não faz nada (silencioso).

    st.divider()

    # ---------- Fontes pendentes ----------
    pending = storage.list_sources(only_pending=True)

    if not pending:
        st.info("Nenhuma fonte pendente. Faça upload de algum arquivo acima ou veja as fontes já ingeridas abaixo.")
    else:
        st.subheader(f"Fontes pendentes ({len(pending)})")
        st.caption("Revise cada fonte antes de ingerir.")

        for src in pending:
            with st.expander(f"📄 {src['filename']} — {src['file_format'].upper()} — `{src['id']}`"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.text_area(
                        "Preview do conteúdo extraído",
                        value=src["content_text"][:1500] + ("\n...[truncado]" if len(src["content_text"]) > 1500 else ""),
                        height=150,
                        key=f"preview_{src['id']}",
                        disabled=True,
                    )
                with col2:
                    analyze_key = f"analysis_{src['id']}"
                    if st.button("🔍 Analisar", key=f"btn_analyze_{src['id']}", use_container_width=True):
                        with st.spinner("Analisando com o LLM..."):
                            try:
                                analysis = synthesis.analyze_source(src["id"])
                                st.session_state[analyze_key] = analysis
                            except Exception as e:
                                st.error(f"Falha na análise: {e}")

                    if st.button("🗑️ Descartar fonte", key=f"btn_discard_src_{src['id']}", use_container_width=True):
                        storage.delete_source(src["id"])
                        st.success("Fonte descartada.")
                        st.rerun()

                analysis = st.session_state.get(analyze_key)
                if analysis:
                    st.markdown("---")
                    st.markdown("**Análise da fonte:**")
                    st.markdown(f"- **Tipo:** {analysis.get('source_type', '?')}")
                    st.markdown(f"- **Viés potencial:** {analysis.get('source_bias', '?')}")
                    st.markdown(f"- **Resumo:** {analysis.get('summary', '?')}")
                    st.markdown("**Pontos-chave identificados:**")
                    for pt in analysis.get("key_points", []):
                        st.markdown(f"- {pt}")
                    entities = analysis.get("entities_mentioned", [])
                    if entities:
                        st.markdown(f"**Páginas a criar/atualizar ({len(entities)}):**")
                        for e in entities:
                            tag = "🆕" if e.get("is_new") else "♻️"
                            st.markdown(f"- {tag} `{e.get('category', '?')}/{e.get('name', '?')}`")

                    conflicts = analysis.get("potential_conflicts", [])
                    if conflicts:
                        st.warning(f"⚠️ {len(conflicts)} conflito(s) potencial(is) detectado(s)")
                        for c in conflicts:
                            st.markdown(f"- Conflito com `{c.get('existing_page')}`: {c.get('description')}")

                    commit_done_key = f"committed_{src['id']}"

                    col1, col2 = st.columns(2)
                    with col1:
                        if not st.session_state.get(commit_done_key):
                            if st.button("✅ Confirmar ingestão", key=f"btn_commit_{src['id']}",
                                         use_container_width=True, type="primary"):
                                with st.spinner("Integrando na wiki..."):
                                    try:
                                        report = synthesis.commit_ingestion(src["id"], analysis)
                                        st.session_state[commit_done_key] = True
                                        st.success("Ingestão completa!")
                                        st.json(report)
                                        if analyze_key in st.session_state:
                                            del st.session_state[analyze_key]
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Falha na ingestão: {e}")
                        else:
                            st.success("✅ Já ingerida nesta sessão.")
                    with col2:
                        if st.button("❌ Descartar análise", key=f"btn_discard_{src['id']}",
                                     use_container_width=True):
                            del st.session_state[analyze_key]
                            st.rerun()

    st.divider()

    all_sources = storage.list_sources(only_pending=False)
    ingested = [s for s in all_sources if s["ingested_at"]]
    if ingested:
        with st.expander(f"📚 Fontes já ingeridas ({len(ingested)})", expanded=False):
            for src in ingested:
                st.markdown(
                    f"- **{src['filename']}** — ingerida em {src['ingested_at'][:10]} → "
                    f"[[{src['summary_page']}]]"
                )
