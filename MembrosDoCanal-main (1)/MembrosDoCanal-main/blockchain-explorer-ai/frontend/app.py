import streamlit as st
import requests

st.set_page_config(page_title="Explorador Blockchain Inteligente")

st.title("🔍 Explorador Blockchain com IA")
st.markdown("Faça perguntas sobre um endereço Ethereum. Exemplo: *'O que este endereço tem feito recentemente?'*")

address = st.text_input("Endereço Ethereum")
question = st.text_area("Sua pergunta")

if st.button("Analisar"):
    if not address or not question:
        st.warning("Preencha todos os campos.")
    else:
        with st.spinner("Consultando a blockchain e gerando resposta com IA..."):
            response = requests.post(
                "http://localhost:8000/analyze/",
                json={"address": address, "question": question}
            )
            if response.status_code == 200:
                st.success(response.json()["response"])
            else:
                st.error("Erro na análise. Tente novamente.")
