# -*- coding: utf-8 -*-

# Instale dependências (se estiver no Colab, mantenha os !pip; local use pip normal)
#pip install -U langchain langchain-community faiss-cpu langchain-text-splitters pypdf langchain-ollama

import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA

# --- Ollama (LLM + Embeddings) ---
# OBS: dependendo da versão do LangChain, os imports podem variar.
# Primeiro tenta pelo langchain_community; se não existir, cai para langchain_ollama.
try:
    from langchain_ollama import ChatOllama
    from langchain_ollama import OllamaEmbeddings
except Exception:
    from langchain_ollama import ChatOllama, OllamaEmbeddings

# (Opcional) se o Ollama estiver em outra máquina/porta:
# os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434"

# ============================================
# 1) Carregar o PDF local
# ============================================
pdf_path = "docs/Artigo.pdf"  # ajuste se precisar
loader = PyPDFLoader(pdf_path)
docs = loader.load()
print(f"PDF carregado: {len(docs)} páginas.")

# ============================================
# 2) Split dos documentos em chunks
# ============================================
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=["\n\n", "\n", " ", ""],
)
chunks = splitter.split_documents(docs)
print(f"Chunks gerados: {len(chunks)}")

# ============================================
# 3) Index (vetorização) com embeddings via Ollama
# ============================================
# Modelo de embeddings recomendado no Ollama:
# - nomic-embed-text (leve e bom)
embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")
vectordb = FAISS.from_documents(chunks, embeddings)

retriever = vectordb.as_retriever(search_kwargs={"k": 4})

# ============================================
# 4) LLM (granite4:latest) e chain RAG
# ============================================
llm = ChatOllama(
    model="granite4:latest",
    temperature=0.3,
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type="stuff",
    return_source_documents=True,
)

# ============================================
# 5) Pergunte!
# ============================================
pergunta = "Qual é o modelo de CNN que apresentou o melhor resultado?"
result = qa_chain.invoke({"query": pergunta})

print("\n==== Resposta ====\n")
print(result["result"])

print("\n==== Fontes ====\n")
for i, d in enumerate(result["source_documents"], start=1):
    src = d.metadata.get("source")
    page = d.metadata.get("page", "N/A")
    print(f"[{i}] {src}  (página {page})")