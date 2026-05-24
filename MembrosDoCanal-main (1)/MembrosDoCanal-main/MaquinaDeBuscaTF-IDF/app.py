import streamlit as st
import requests
from urllib.parse import quote
import os

# Configurações de URL
API_URL_SEARCH = "http://127.0.0.1:8000/search"
API_URL_INTERACT = "http://127.0.0.1:8000/interact"
PDF_BASE_URL = "http://localhost:8000/documentos/"  # URL base para acessar os PDFs

# Inicializa o estado da sessão para busca e seleção
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "selected_document" not in st.session_state:
    st.session_state.selected_document = None

# Interface de busca
st.title("Interaja com Documentos")
keywords = st.text_input("Digite as palavras-chave para buscar documentos relacionados")

# Realiza a busca ao clicar no botão
if st.button("Buscar"):
    response = requests.get(API_URL_SEARCH, params={"keywords": keywords})
    if response.status_code == 200:
        st.session_state.search_results = response.json()
        st.session_state.selected_document = None  # Limpa a seleção anterior, se houver
    else:
        st.error("Erro ao buscar documentos. Verifique a conexão com a API.")

# Exibe os resultados da busca, se disponíveis
if st.session_state.search_results:
    unique_documents = {}
    for doc in st.session_state.search_results:
        doc_name = doc['document']
        if doc_name not in unique_documents or doc['similarity'] > unique_documents[doc_name]['similarity']:
            unique_documents[doc_name] = doc
    filtered_results = list(unique_documents.values())
    
    st.write("## Documentos recomendados:")
    for i, doc in enumerate(filtered_results):
        truncated_doc_name = doc['document'][:30] + "..." if len(doc['document']) > 30 else doc['document']
        pdf_link = f"{PDF_BASE_URL}{quote(os.path.basename(doc['document']))}"  # Link apenas para o nome do arquivo PDF
        
        with st.expander(f"{truncated_doc_name} - Similaridade: {doc['similarity']:.4f}"):
            # Link para download do PDF
            st.markdown(f"**Documento completo:** [Baixar {doc['document']}]({pdf_link})", unsafe_allow_html=True)
            if st.button(f"Selecionar {doc['document']} para conversar", key=f"select_{i}"):
                # Armazena o documento selecionado no estado da sessão
                st.session_state.selected_document = doc['document']

# Se um documento estiver selecionado, exibe a interface de interação
if st.session_state.selected_document:
    st.write(f"**Documento Selecionado:** {st.session_state.selected_document}")
    query = st.text_input("Faça uma pergunta sobre o documento selecionado")
    if st.button("Enviar Pergunta"):
        response = requests.post(API_URL_INTERACT, json={
            "query": query,
            "document_name": st.session_state.selected_document
        })
        if response.status_code == 200:
            answer = response.json().get("answer", "Erro ao obter resposta.")
            st.write("### Resposta:")
            st.write(answer)
        else:
            st.write("Erro ao processar a pergunta. Tente novamente.")
            st.write(f"Detalhes do erro: {response.text}")  # Mostra a resposta de erro para depuração
