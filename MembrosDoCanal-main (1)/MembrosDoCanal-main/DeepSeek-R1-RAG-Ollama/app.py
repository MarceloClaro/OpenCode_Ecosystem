import streamlit as st
import requests
import os

CHATBOT_ENDPOINT_URL = "http://127.0.0.1:8001/query" 
UPLOAD_ENDPOINT_URL = "http://127.0.0.1:8002/upsert_documents"
UPLOAD_DIRECTORY = "documentos"

# Garante que o diretório para upload existe
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

def exibir_conversa():
    """
    Percorre st.session_state.messages e exibe cada mensagem 
    (usuário ou assistente) no estilo de chat.
    """
    for role, content in st.session_state.messages:
        st.chat_message(role).write(content)

def enviar_documentos_para_backend():
    """Envia os documentos salvos no diretório 'documentos' para o backend."""
    try:
        payload = {"folder": UPLOAD_DIRECTORY}
        response = requests.post(UPLOAD_ENDPOINT_URL, json=payload)
        if response.status_code == 200:
            st.success("Documentos processados com sucesso!")
        else:
            st.error(f"Erro ao processar documentos: {response.status_code} - {response.json().get('detail', 'Erro desconhecido')}")
    except Exception as e:
        st.error(f"Erro ao se conectar ao servidor: {str(e)}")

def menu_sidebar():
    """Cria o menu na barra lateral para upload de documentos."""
    st.sidebar.header("📄 Upload de Documentos")
    st.sidebar.write("Envie arquivos PDF para serem processados.")
    uploaded_files = st.sidebar.file_uploader(
        "Arraste e solte ou selecione os arquivos PDF",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_path = os.path.join(UPLOAD_DIRECTORY, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.sidebar.success("Arquivos enviados com sucesso!")
        if st.sidebar.button("Processar Documentos"):
            enviar_documentos_para_backend()

def main():
    st.set_page_config(page_title="Assistente DeepSeek-R1", layout="centered")
    st.title("💬 Assistente DeepSeek-R1")
    st.write("🚀 Converse com os seus documentos ou faça upload de novos.")

    # Configura o menu lateral
    menu_sidebar()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Exibe as mensagens do chat que já existem no state
    exibir_conversa()

    st.divider()

    st.header("Conversa com o Assistente")
    if user_input := st.chat_input():
        if user_input.strip():
            st.session_state.messages.append(("Usuário", user_input))
            st.chat_message("user").write(user_input)

            payload = {"question": user_input}
            try:
                response = requests.post(CHATBOT_ENDPOINT_URL, json=payload)
                
                if response.status_code == 200:
                    response_data = response.json()
                    resposta_chatbot = response_data.get("resposta", "")
                    if resposta_chatbot:
                        st.session_state.messages.append(("Chatbot", resposta_chatbot))
                        st.chat_message("assistant").write(resposta_chatbot)
                    else:
                        st.session_state.messages.append(("Chatbot", "Resposta não disponível."))
                        st.chat_message("assistant").write("Resposta não disponível.")
                else:
                    st.session_state.messages.append(("Chatbot", f"Erro: {response.status_code}"))
            except Exception as e:
                st.session_state.messages.append(("Chatbot", f"Exceção: {str(e)}"))

if __name__ == "__main__":
    main()
