import streamlit as st
from pipeline_cbr import (
    buscar_caso_similar,
    adaptar_solucao,
    buscar_na_web,
    validar_resposta_web,
    adicionar_caso,
    carregar_casos,
)

st.set_page_config(page_title="Suporte Técnico Inteligente", layout="wide")
st.title("💻 Assistente de TI com Aprendizado Contínuo")

st.markdown(
    """
    Informe o problema técnico que você está enfrentando. 
    O sistema busca casos similares na base, adapta a solução e, se necessário, busca informações atualizadas na web com IA! Possui aprendizado contínuo.
    """
)

with st.expander("📊 Estatísticas da Base"):
    casos = carregar_casos()
    if casos:
        total = len(casos)
        fontes = {}
        for caso in casos:
            fonte = caso.get('fonte', 'desconhecida')
            fontes[fonte] = fontes.get(fonte, 0) + 1
        st.write(f"Total de casos: {total}")
        for fonte, count in fontes.items():
            st.write(f"- {fonte}: {count} casos")
    else:
        st.info("Base vazia.")

if "historico" not in st.session_state:
    st.session_state.historico = []

# Interface de consulta
problema = st.text_area(
    "Descreva seu problema técnico:", 
    placeholder="Exemplo: Meu computador liga, mas a tela fica preta.",
    key="input_problema"
)

if st.button("Buscar solução"):
    st.session_state.resposta = {}
    if problema.strip():
        caso_similar = buscar_caso_similar(problema, threshold=0.3)
        st.session_state.resposta["caso_similar"] = caso_similar
        if caso_similar:
            resposta_adaptada = adaptar_solucao(problema, caso_similar)
            st.session_state.resposta["adaptada"] = resposta_adaptada
            st.session_state.resposta["web"] = None
            st.session_state.resposta["fase"] = "adaptada"
        else:
            resposta_web = buscar_na_web(problema)
            if not validar_resposta_web(resposta_web):
                resposta_web = "❌ Solução da web não parece relevante. Consulte um especialista."
            st.session_state.resposta["adaptada"] = None
            st.session_state.resposta["web"] = resposta_web
            st.session_state.resposta["fase"] = "web"

# Mostra o resultado conforme o estado
if "resposta" in st.session_state and st.session_state.resposta:
    resposta = st.session_state.resposta
    caso_similar = resposta.get("caso_similar")
    resposta_adaptada = resposta.get("adaptada")
    resposta_web = resposta.get("web")
    fase = resposta.get("fase")

    if fase == "adaptada" and caso_similar:
        st.success("✅ Caso similar encontrado na base!")
        with st.expander("🔎 Caso usado como referência"):
            st.write(f"**Problema:** {caso_similar['problema']}")
            st.write(f"**Solução:** {caso_similar['solucao']}")
        st.markdown("### 🛠️ Solução Técnica Adaptada")
        st.write(resposta_adaptada)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Resolvido!", key="resolvido"):
                adicionar_caso(problema, resposta_adaptada, fonte="CBR")
                st.success("Caso registrado como resolvido!")
                st.session_state.resposta = {}
        with col2:
            if st.button("❌ Não resolveu, buscar na web", key="web"):
                resposta_web = buscar_na_web(problema)
                if not validar_resposta_web(resposta_web):
                    resposta_web = "❌ Solução da web não parece relevante. Consulte um especialista."
                st.session_state.resposta["web"] = resposta_web
                st.session_state.resposta["fase"] = "web"
                st.rerun()


    if fase == "web" and resposta_web:
        st.markdown("### 🌐 Solução encontrada na web")
        st.write(resposta_web)
        if st.button("👍 Solução da web resolveu", key="web_resolvido"):
            adicionar_caso(problema, resposta_web, fonte="web")
            st.success("Caso da web registrado na base!")
            st.session_state.resposta = {}

st.markdown("---")
st.caption("Desenvolvido com Raciocínio Baseado em Casos + IA Generativa (CBR+LLM).")
