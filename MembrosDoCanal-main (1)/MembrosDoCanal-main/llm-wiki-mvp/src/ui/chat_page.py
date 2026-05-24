"""Tela de Chat com a wiki.

Mantém histórico em st.session_state. Suporta streaming.
"""
import streamlit as st
from src import synthesis


def render():
    st.header("Chat com a wiki")
    st.caption("Faça perguntas. As respostas citam páginas da wiki. Análises substantivas podem ser salvas como sínteses.")

    # Inicializa histórico
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Botão de limpar histórico
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🗑️ Limpar conversa", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    # Renderiza histórico
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input
    if prompt := st.chat_input("Pergunte algo à wiki..."):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            try:
                for chunk in synthesis.answer_query_stream(
                    question=prompt,
                    chat_history=st.session_state.chat_messages[:-1],
                ):
                    full_response += chunk
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"❌ Erro: {e}"
                placeholder.error(full_response)

        st.session_state.chat_messages.append({"role": "assistant", "content": full_response})

        # Oferece salvar como síntese se a resposta for longa
        if len(full_response) > 300 and "sintese" in full_response.lower() or len(full_response) > 800:
            with st.expander("💾 Salvar essa resposta como página de síntese?"):
                title = st.text_input("Título da síntese", key=f"syn_title_{len(st.session_state.chat_messages)}")
                if st.button("Salvar", key=f"syn_save_{len(st.session_state.chat_messages)}"):
                    if title.strip():
                        path = synthesis.save_synthesis(title.strip(), full_response)
                        st.success(f"Salvo em `{path}`")
                    else:
                        st.warning("Digite um título antes de salvar.")
