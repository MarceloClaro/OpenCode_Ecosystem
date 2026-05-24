import os  # Importa o módulo para lidar com operações do sistema operacional
import streamlit as st  # Importa o Streamlit para criar a interface do aplicativo
from langchain_groq import ChatGroq  # Importa a classe ChatGroq do pacote langchain_groq
from langchain_community.document_loaders import WebBaseLoader  # Importa WebBaseLoader para carregar documentos da web
from langchain_community.embeddings import OllamaEmbeddings  # Importa OllamaEmbeddings para criar embeddings
from langchain_community.vectorstores import FAISS  # Importa FAISS para armazenar vetores
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Importa RecursiveCharacterTextSplitter para dividir texto
from langchain.chains.combine_documents import create_stuff_documents_chain  # Importa create_stuff_documents_chain para criar corrente de documentos
from langchain_core.prompts import ChatPromptTemplate  # Importa ChatPromptTemplate para criar prompt de chat
from langchain.chains import create_retrieval_chain  # Importa create_retrieval_chain para criar corrente de recuperação
import time  # Importa o módulo time para medir o tempo de resposta
from dotenv import load_dotenv  # Importa load_dotenv para carregar variáveis de ambiente

load_dotenv()  # Carrega as variáveis de ambiente do arquivo .env

groq_api_key = os.environ['GROQ_API_KEY']  # Obtém a chave da API do ambiente

st.title("RAG com páginas web")  # Define o título do aplicativo Streamlit

document_url = st.text_input("Forneça a URL da página aqui")  # Solicita a URL da página web ao usuário

if document_url:  # Verifica se o usuário inseriu uma URL de página web

    if "vector" not in st.session_state:  # Verifica se o vetor não está armazenado na sessão do Streamlit

        # Cria e armazena objetos relacionados ao processamento da página web e criação de embeddings
        st.session_state.embeddings = OllamaEmbeddings()  # Cria um objeto de embeddings
        st.session_state.loader = WebBaseLoader(document_url)  # Cria um objeto loader para carregar a página web
        st.session_state.docs = st.session_state.loader.load()  # Carrega os documentos da web
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)  # Define o splitter de texto
        st.session_state.documents = st.session_state.text_splitter.split_documents(st.session_state.docs)  # Divide os documentos
        st.session_state.vector = FAISS.from_documents(st.session_state.documents, st.session_state.embeddings)  # Cria um vetor de embeddings

    # Cria um objeto ChatGroq para interagir com o serviço Groq
    llm = ChatGroq(
                groq_api_key=groq_api_key, 
                model_name='mixtral-8x7b-32768'
        )

    # Cria um prompt de modelo de chat com contexto e pergunta
    prompt = ChatPromptTemplate.from_template("""
    Escreva somente em português a resposta da questão a seguir com base apenas no contexto fornecido. Pense passo a passo antes de fornecer uma resposta detalhada. 
    <context>
    {context}
    </context>

    Question: {input}""")

    # Cria correntes de processamento de documentos e recuperação combinadas
    document_chain = create_stuff_documents_chain(llm, prompt)
    retriever = st.session_state.vector.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    prompt = st.text_input("Digite a sua pergunta aqui")  # Solicita que o usuário insira uma pergunta

    if prompt:  # Verifica se o usuário inseriu uma pergunta

        start = time.process_time()  # Inicia a contagem do tempo de resposta
        response = retrieval_chain.invoke({"input": prompt})  # Invoca a cadeia de recuperação para obter a resposta à pergunta
        print(f"Response time: {time.process_time() - start}")  # Imprime o tempo de resposta

        st.write(response["answer"])  # Exibe a resposta obtida

        # Expande um expander para mostrar os documentos semelhantes
        with st.expander("Busca documentos similares"):
            for i, doc in enumerate(response["context"]):
                st.write(doc.page_content)  # Exibe o conteúdo do documento
                st.write("--------------------------------")  # Imprime uma linha para separar os documentos

