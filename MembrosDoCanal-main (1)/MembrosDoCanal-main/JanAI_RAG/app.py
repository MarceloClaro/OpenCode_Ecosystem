# Importa o framework de interface de usuário para apps web
import streamlit as st

# Importa o vetor store Qdrant da comunidade LangChain (armazenamento vetorial)
from langchain_community.vectorstores import Qdrant

# Importa a classe para geração de embeddings do modelo HuggingFace
from langchain_community.embeddings import HuggingFaceEmbeddings

# Importa o divisor de texto baseado em tamanho de caractere
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Importa o carregador de documentos PDF
from langchain_community.document_loaders import PyPDFLoader

# Bibliotecas padrão para manipulação de arquivos temporários e sistema de arquivos
import tempfile
import os

# Biblioteca para fazer requisições HTTP (usada para chamar a API do modelo Jan)
import requests


def get_vector_store(uploaded_files):
    # Se nenhum arquivo foi enviado, retorna None
    if not uploaded_files:
        return None

    # Inicializa o divisor de texto com chunks de 1000 caracteres e sobreposição de 100
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = []  # Lista para armazenar todos os documentos processados

    for uploaded_file in uploaded_files:
        # Cria um arquivo temporário para salvar o PDF carregado
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())  # Escreve o conteúdo do PDF no arquivo temporário
            tmp_path = tmp_file.name  # Salva o caminho do arquivo

        # Carrega e divide o PDF em chunks usando LangChain
        loader = PyPDFLoader(tmp_path)
        docs.extend(loader.load_and_split(text_splitter=text_splitter))

        # Remove o arquivo temporário após o uso
        os.remove(tmp_path)

    # Gera embeddings usando um modelo leve da HuggingFace
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Cria o vetor store em memória usando Qdrant
    vector_store = Qdrant.from_documents(
        docs,
        embeddings,
        location=":memory:",  # Banco em memória (não persistente)
        collection_name="my_documents"
    )
    return vector_store  # Retorna o banco vetorial com os documentos indexados


def call_jan_api(prompt, api_key):
    url = "http://127.0.0.1:1337/v1/chat/completions"  # Endpoint local da API Jan
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"  # Chave de autenticação para a API
    }
    data = {
        "model": "gemma3:1b",  # Nome do modelo usado
        "messages": [{"role": "user", "content": prompt}],  # Envia o prompt do usuário
        "temperature": 0.3,     # Controla a aleatoriedade das respostas
        "top_p": 0.95,          # Controle de diversidade (top-p sampling)
        "max_tokens": 1024      # Número máximo de tokens na resposta
    }

    # Faz a requisição POST e levanta erro se falhar
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()

    # Extrai e retorna o conteúdo da resposta
    return response.json()['choices'][0]['message']['content']

def build_prompt(context, question):
    # Constrói um prompt bem estruturado para o modelo, com o contexto e a pergunta
    return f"""Você é um assistente inteligente. Responda à pergunta com base somente nas informações abaixo.

Contexto:
{context}

Pergunta: {question}

Resposta clara, objetiva e precisa:"""

def main():
    # Configura o título e o ícone da aba do Streamlit
    st.set_page_config(page_title="JanAI RAG", page_icon="🤖")
    st.title("Converse com seus Documentos")  # Título da interface

    # Sidebar para upload de arquivos e chave da API
    with st.sidebar:
        st.header("Configurações")
        uploaded_files = st.file_uploader("Carregar PDFs", type=['pdf'], accept_multiple_files=True)
        api_key = st.text_input("Chave da API Jan", type="password", value="teste")

    # Processa os PDFs enviados e cria o vetor store
    vector_store = get_vector_store(uploaded_files)

    # Inicializa o estado da conversa se ainda não estiver criado
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostra todas as mensagens anteriores (histórico do chat)
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Se o usuário enviar uma nova mensagem:
    if user_input := st.chat_input("Pergunte algo sobre seus documentos"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            if not vector_store:
                response = "Por favor, carregue documentos antes de perguntar."
            else:
                # Cria um retriever com até 5 documentos relevantes
                retriever = vector_store.as_retriever(search_kwargs={"k": 5})
                context_docs = retriever.get_relevant_documents(user_input)
                # Junta os textos dos documentos em um único contexto
                context = "\n\n".join(doc.page_content for doc in context_docs)

                if not context.strip():
                    response = "Não encontrei informações relevantes nos documentos para responder sua pergunta."
                else:
                    # Constrói o prompt com o contexto + pergunta
                    final_prompt = build_prompt(context, user_input)
                    try:
                        # Chama a API Jan para obter a resposta
                        response = call_jan_api(final_prompt, api_key)
                    except Exception as e:
                        response = f"Erro ao chamar API Jan: {e}"

            # Exibe a resposta e salva no histórico
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


# Executa a função main() se este script for executado diretamente
if __name__ == "__main__":
    main()

