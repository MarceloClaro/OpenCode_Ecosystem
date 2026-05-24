"""Tela de Lint — health check da wiki."""
import streamlit as st
from src import synthesis, storage


SEVERITY_ICON = {"alta": "🔴", "media": "🟡", "baixa": "🟢"}


def render():
    st.header("Health check da wiki")
    st.caption(
        "O lint inspeciona a wiki em busca de páginas órfãs, links quebrados, "
        "estagnação, e sugere próximos passos. Combina dados pré-calculados com análise do LLM."
    )

    if st.button("🔍 Rodar lint", type="primary"):
        with st.spinner("Auditando a wiki (chamada LLM, pode demorar)..."):
            try:
                report = synthesis.run_lint()
                st.session_state["last_lint_report"] = report
            except Exception as e:
                st.error(f"Falha no lint: {e}")
                return

    report = st.session_state.get("last_lint_report")
    if not report:
        st.info("Clique em 'Rodar lint' para gerar um relatório.")
        return

    st.subheader("Resumo")
    st.write(report.get("summary", "(sem resumo)"))

    issues = report.get("issues", [])
    if issues:
        st.subheader(f"Issues encontrados ({len(issues)})")
        for i, issue in enumerate(issues):
            severity = issue.get("severity", "media")
            icon = SEVERITY_ICON.get(severity, "⚪")
            with st.expander(f"{icon} **[{severity.upper()}]** {issue.get('description', '?')}"):
                st.markdown(f"**Tipo:** `{issue.get('type', '?')}`")
                affected = issue.get("affected_pages", [])
                if affected:
                    st.markdown("**Páginas afetadas:**")
                    for p in affected[:10]:
                        st.markdown(f"- `{p}`")
                    if len(affected) > 10:
                        st.caption(f"... e mais {len(affected) - 10}")
                if issue.get("suggested_action"):
                    st.markdown(f"**Ação sugerida:** {issue['suggested_action']}")
    else:
        st.success("✅ Nenhum issue detectado!")

    next_steps = report.get("next_steps", [])
    if next_steps:
        st.subheader("Próximos passos sugeridos")
        for step in next_steps:
            st.markdown(f"- {step}")

    st.divider()
    with st.expander("📜 Histórico recente de operações"):
        log = storage.recent_log(limit=20)
        for entry in log:
            st.markdown(f"- **{entry['timestamp'][:16]}** `{entry['operation']}` — {entry['summary']}")
