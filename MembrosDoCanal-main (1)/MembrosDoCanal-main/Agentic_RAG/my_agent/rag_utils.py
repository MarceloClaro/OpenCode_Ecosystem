from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
import os


# Caminho onde será salvo o índice FAISS
INDEX_PATH = os.path.join(os.path.dirname(__file__), "../vectorstore/faiss_index")


# Cria o índice vetorial a partir dos arquivos .txt na pasta docs/
def create_vectorstore_from_txt(directory="docs"):
    texts = []

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            loader = TextLoader(os.path.join(directory, filename), encoding="utf-8")
            docs = loader.load()
            texts.extend(docs)

    # Divide os textos em pedaços menores
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    split_docs = splitter.split_documents(texts)

    # Usa modelo de embedding local (sem API)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Cria banco vetorial e salva localmente
    db = FAISS.from_documents(split_docs, embeddings)
    db.save_local(INDEX_PATH)

# Carrega o banco vetorial já salvo
def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)

# Consulta o índice FAISS e retorna os k resultados mais relevantes
def query_vectorstore(query: str, k: int = 3) -> str:
    db = load_vectorstore()
    results = db.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in results])
