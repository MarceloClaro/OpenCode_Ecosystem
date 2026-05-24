# Importa a biblioteca Streamlit, usada para criar interfaces web simples em Python.
import streamlit as st

# Importa a biblioteca requests, usada para fazer requisições HTTP.
import requests

# Define constantes com as informações da API e da sessão.
API_URL = "http://localhost:8000"     # URL base da API do agente
APP_NAME = "finance_agent"            # Nome do aplicativo registrado no servidor
USER_ID = "user_finance"              # Identificador do usuário
SESSION_ID = "session_finance"        # Identificador da sessão da conversa

# Cria uma função que inicializa (ou reutiliza) uma sessão com o agente.
# A função é cacheada para evitar chamadas repetidas.
@st.cache_resource
def criar_sessao():
    # Monta a URL para criar a sessão.
    url = f"{API_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions/{SESSION_ID}"
    # Faz uma requisição POST para iniciar a sessão.
    response = requests.post(url, json={})
    # Retorna True se a sessão foi criada (200) ou já existe (409).
    return response.status_code == 200 or response.status_code == 409

# Função para enviar uma mensagem de texto para o agente e obter a resposta.
def enviar_mensagem(mensagem):
    url = f"{API_URL}/run"  # Endpoint da API que executa a interação
    payload = {
        "appName": APP_NAME,
        "userId": USER_ID,
        "sessionId": SESSION_ID,
        "newMessage": {
            "role": "user",  # Indica que a mensagem é do usuário
            "parts": [{"text": mensagem}]  # Corpo da mensagem
        }
    }
    # Envia a mensagem via POST
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        eventos = response.json()  # Resposta do agente em formato JSON
        if eventos and "content" in eventos[0]:
            # Retorna o texto da resposta se presente
            return eventos[0]["content"]["parts"][0]["text"].strip()
    return "Erro: não foi possível obter resposta."  # Mensagem de erro padrão

# Função para enviar um arquivo (CSV) com extrato bancário e obter análise
def enviar_arquivo(file_bytes):
    url = f"{API_URL}/run"
    # Converte os bytes do arquivo para texto
    csv_text = file_bytes.decode('utf-8')
    payload = {
        "appName": APP_NAME,
        "userId": USER_ID,
        "sessionId": SESSION_ID,
        "newMessage": {
            "role": "user",
            "parts": [{"text": csv_text}]  # Envia o conteúdo do CSV como texto
        }
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        eventos = response.json()
        # Percorre a lista de eventos de trás pra frente (resposta mais recente)
        for evento in reversed(eventos):
            if "text" in evento.get("content", {}).get("parts", [{}])[0]:
                return evento["content"]["parts"][0]["text"].strip()
        return "Não foi possível encontrar uma resposta de texto."  # Caso não encontre conteúdo válido
    return "Erro: não foi possível processar o arquivo."  # Erro geral

# Interface Streamlit começa aqui

# Exibe o título principal da aplicação
st.title("💰 Consultor Financeiro Inteligente")

# Cria (ou reutiliza) a sessão no início da execução
criar_sessao()

# Seção de upload de arquivos
st.header("📤 Upload do Extrato Bancário (CSV)")

# Componente para upload de arquivos CSV
uploaded_file = st.file_uploader("Escolha um arquivo CSV", type=["csv"])

# Se um arquivo for carregado:
if uploaded_file is not None:
    file_bytes = uploaded_file.read()  # Lê o conteúdo do arquivo
    st.success("Arquivo carregado!")   # Exibe mensagem de sucesso
    # Se o botão for pressionado, envia o arquivo para análise
    if st.button("Analisar Extrato"):
        resposta = enviar_arquivo(file_bytes)
        # Exibe a resposta da análise em uma área de texto
        st.text_area("Resultado da Análise", resposta, height=300)

# Seção para conversa direta com o agente
st.header("💬 Converse com o Agente")

# Campo para o usuário digitar uma pergunta
mensagem = st.text_input("Digite sua pergunta:")

# Se o botão for pressionado, envia a mensagem para o agente
if st.button("Enviar Pergunta"):
    if mensagem:
        resposta = enviar_mensagem(mensagem)
        # Exibe a resposta do agente
        st.text_area("Resposta do Agente:", resposta, height=300)
