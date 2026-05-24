import streamlit as st
import requests

# === CONFIGURAÇÕES ===
API_URL = "http://localhost:8000"  # Endereço da API (ajuste conforme necessário)
APP_NAME = "smartbuy_advisor"
USER_ID = "user_teste"
SESSION_ID = "sessao_compra"

# === CRIA SESSÃO COM O AGENTE ===
@st.cache_resource
def criar_sessao():
    url = f"{API_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions/{SESSION_ID}"
    response = requests.post(url, json={})
    return response.status_code in [200, 409]

# === ENVIA CONSULTA DE COMPRA ===
def enviar_mensagem(mensagem):
    url = f"{API_URL}/run"
    payload = {
        "appName": APP_NAME,
        "userId": USER_ID,
        "sessionId": SESSION_ID,
        "newMessage": {
            "role": "user",
            "parts": [{"text": mensagem}]
        }
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        eventos = response.json()
        for evento in reversed(eventos):
            parts = evento.get("content", {}).get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"].strip()
        return "⚠️ A resposta não continha texto compreensível."

    return "❌ Erro ao processar a requisição."

# === INTERFACE STREAMLIT ===

st.set_page_config(page_title="🔍 Consultor de Compras Inteligente")
st.title("🛍️ Consultor de Compras com IA")
st.markdown("Este assistente analisa **avaliações, reclamações e opiniões online** sobre produtos ou serviços, e dá uma recomendação de compra.")

# Inicializa ou reutiliza sessão
criar_sessao()

# Campo de entrada
st.header("🔎 Faça sua consulta")
entrada = st.text_input("Digite o nome do produto ou serviço que deseja avaliar:")

if st.button("Analisar Produto"):
    if entrada:
        with st.spinner("🔍 Buscando informações na web..."):
            resposta = enviar_mensagem(entrada)
        st.success("✅ Análise concluída!")
        st.text_area("📄 Relatório de Reputação do Produto", resposta, height=400)
    else:
        st.warning("Por favor, insira o nome do produto ou serviço.")
