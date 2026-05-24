
import os
import streamlit as st
from utils import setup_qdrant, index_document, search_documents, get_rag_response

# Configuração da página
st.set_page_config(page_title="Assistente de Documentos com IA", layout="wide")

# Diretório para uploads
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Inicializa o Qdrant na primeira execução
setup_qdrant()

# --- Interface do Streamlit ---

st.title("🤖 Assistente de IA para Análise de Documentos")
st.caption("Faça upload de PDFs ou imagens e faça perguntas sobre o conteúdo.")

# --- Sidebar para Upload ---
st.sidebar.header("Upload de Documentos")
uploaded_files = st.sidebar.file_uploader(
    "Escolha os arquivos (PDF, PNG, JPG)", 
    accept_multiple_files=True, 
    type=['pdf', 'png', 'jpg', 'jpeg']
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        # Salva o arquivo no diretório de uploads
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Indexa o documento
        with st.spinner(f'Processando e indexando {uploaded_file.name}...'):
            index_document(file_path, uploaded_file.name)
        st.sidebar.success(f"{uploaded_file.name} processado com sucesso!")

# --- Área de Chat ---
st.header("Faça sua Pergunta")

# Inicializa o histórico do chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens do histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Campo de input para a pergunta do usuário
if prompt := st.chat_input("Qual a sua dúvida?"):
    # Adiciona a mensagem do usuário ao histórico e à tela
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Busca por contexto relevante
    with st.spinner("Buscando informações nos documentos..."):
        context_payloads = search_documents(prompt)
    
    # Gera e exibe a resposta do assistente
    with st.spinner("Gerando a resposta..."):
        response = get_rag_response(prompt, context_payloads)
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Adiciona a resposta do assistente ao histórico
    st.session_state.messages.append({"role": "assistant", "content": response})

