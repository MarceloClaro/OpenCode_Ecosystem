import streamlit as st
from raglight.rag.simple_rag_api import RAGPipeline
from raglight.models.data_source_model import FolderSource
from raglight.config.settings import Settings
from raglight.config.rag_config import RAGConfig
from raglight.config.vector_store_config import VectorStoreConfig
import os

# Configuração da página
st.set_page_config(page_title="RAGlight - Assistente RAG", layout="wide")
st.title("🧠 Assistente de IA baseado em RAGlight")

# Ativa logs detalhados
Settings.setup_logging()

# Caminhos fixos
KNOWLEDGE_PATH = "./meus_docs"
VECTOR_DB_DIR = "./vetor_db"
COLLECTION_NAME = "base_conhecimento"

# Inicializa estado da sessão
if "pipeline" not in st.session_state:
    st.session_state.pipeline = None
if "indexed" not in st.session_state:
    st.session_state.indexed = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Upload de arquivos
st.sidebar.header("🔧 Configurações")
st.sidebar.subheader("📤 Upload de Documentos")

uploaded_files = st.sidebar.file_uploader(
    "Envie documentos para o RAG (PDF, TXT ou DOCX)", 
    type=["pdf", "txt", "docx"], 
    accept_multiple_files=True
)

if uploaded_files:
    os.makedirs(KNOWLEDGE_PATH, exist_ok=True)
    for uploaded_file in uploaded_files:
        file_path = os.path.join(KNOWLEDGE_PATH, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
    st.sidebar.success(f"✅ {len(uploaded_files)} arquivo(s) salvo(s) em `{KNOWLEDGE_PATH}`")

# Verifica se a pasta de documentos existe
if not os.path.exists(KNOWLEDGE_PATH):
    st.warning(f"⚠️ Pasta de documentos não encontrada: `{KNOWLEDGE_PATH}`. Crie a pasta e adicione arquivos PDF, TXT ou DOCX.")
else:
    st.success(f"✅ Pasta de documentos encontrada: `{KNOWLEDGE_PATH}`")

# Seção de indexação
st.sidebar.subheader("📚 Banco de Conhecimento")

if st.sidebar.button("🔍 Indexar Documentos"):
    with st.spinner("Indexando documentos... Isso pode levar alguns segundos."):

        try:
            # Configuração do banco vetorial
            vector_store_config = VectorStoreConfig(
                embedding_model=Settings.DEFAULT_EMBEDDINGS_MODEL,
                provider=Settings.HUGGINGFACE,
                database=Settings.CHROMA,
                persist_directory=VECTOR_DB_DIR,
                collection_name=COLLECTION_NAME
            )

            # Configuração do RAG
            config = RAGConfig(
                llm="llama3.1:8b",
                provider=Settings.OLLAMA,
                knowledge_base=[FolderSource(path=KNOWLEDGE_PATH)],
                k=5
            )

            # Cria pipeline
            pipeline = RAGPipeline(config, vector_store_config)
            pipeline.build()

            st.session_state.pipeline = pipeline
            st.session_state.indexed = True
            st.sidebar.success("✅ Documentos indexados com sucesso!")
            st.rerun()

        except Exception as e:
            st.sidebar.error(f"❌ Erro ao indexar: {str(e)}")

# Verifica se já foi indexado
if os.path.exists(VECTOR_DB_DIR) and not st.session_state.indexed:
    st.sidebar.info("📁 Banco vetorial encontrado. Clique em 'Indexar' para carregar.")
elif st.session_state.indexed:
    st.sidebar.success("✅ Banco de conhecimento carregado!")

# Exibe histórico de chat
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Entrada do usuário
if st.session_state.indexed:
    if prompt := st.chat_input("Faça uma pergunta sobre os documentos..."):
        # Adiciona pergunta ao chat
        st.chat_message("user").write(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        # Gera resposta
        with st.spinner("Gerando resposta..."):
            try:
                resposta = st.session_state.pipeline.generate(prompt)
                st.chat_message("assistant").write(resposta)
                st.session_state.chat_history.append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.chat_message("assistant").write("❌ Ocorreu um erro ao gerar a resposta.")
                st.session_state.chat_history.append({"role": "assistant", "content": "Erro: " + str(e)})
else:
    st.info("Por favor, clique em 'Indexar Documentos' no painel lateral antes de fazer perguntas.")
