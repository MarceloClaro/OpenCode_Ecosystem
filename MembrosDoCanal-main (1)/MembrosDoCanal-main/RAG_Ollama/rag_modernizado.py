# -*- coding: utf-8 -*-
"""
RAG Pipeline — Versão Corrigida e Modernizada
Usa LCEL (LangChain Expression Language) em vez do RetrievalQA.
"""

import os
import argparse
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


# ============================================
# Configurações centralizadas
# ============================================
PDF_PATH     = "docs/Artigo.pdf"
INDEX_PATH   = "faiss_index"
EMBED_MODEL  = "nomic-embed-text:latest"
LLM_MODEL    = "granite4:latest"
CHUNK_SIZE   = 1000
CHUNK_OVERLAP = 150
TOP_K        = 4
TEMPERATURE  = 0.3

PROMPT_TEMPLATE = """
Você é um assistente especializado. Responda à pergunta com base
EXCLUSIVAMENTE no contexto fornecido abaixo.
Se a informação não estiver no contexto, diga que não encontrou a resposta
no documento — não invente.

Contexto:
{context}

Pergunta: {question}

Resposta:"""


# ============================================
# 1) Carregar o PDF com validação
# ============================================
def load_pdf(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"PDF não encontrado: '{path}'\n"
            "Verifique o caminho e tente novamente."
        )
    loader = PyPDFLoader(path)
    docs = loader.load()
    if not docs:
        raise ValueError(f"O PDF '{path}' não contém páginas legíveis.")
    print(f"✅ PDF carregado: {len(docs)} página(s).")
    return docs


# ============================================
# 2) Split dos documentos em chunks
# ============================================
def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"✅ Chunks gerados: {len(chunks)}")
    return chunks


# ============================================
# 3) Carregar ou criar o índice FAISS
# ============================================
def get_vectorstore(chunks, embeddings):
    if os.path.exists(INDEX_PATH):
        print(f"⚡ Índice FAISS encontrado em '{INDEX_PATH}'. Carregando...")
        vectordb = FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    else:
        print("🔨 Criando índice FAISS (isso pode levar alguns segundos)...")
        vectordb = FAISS.from_documents(chunks, embeddings)
        vectordb.save_local(INDEX_PATH)
        print(f"✅ Índice salvo em '{INDEX_PATH}'.")
    return vectordb


# ============================================
# 4) Construir a chain RAG com LCEL
# Define uma função que recebe o recuperador de chunks (FAISS) e o modelo de linguagem,
# e devolve a chain montada.
# ============================================
def build_chain(retriever, llm):
    # Cria o template do prompt a partir de uma string definida em outro lugar no código. 
    # Esse template tem variáveis como {context} e {question} que serão preenchidas dinamicamente.
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    
    # Função auxiliar que transforma uma lista de documentos recuperados em uma única string formatada
    def format_docs(docs):
        return "\n\n---\n\n".join(
            f"[Página {d.metadata.get('page', '?')}]\n{d.page_content}"
            for d in docs
        )
    # O **LCEL** (LangChain Expression Language) — uma forma de encadear etapas com o operador `|`, como um pipe do Linux.
    # A chain é construída usando LCEL, onde o contexto é gerado a partir do retriever e formatado, e a pergunta é passada diretamente.
    # O resultado do prompt é então processado pelo LLM e formatado como string.
    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

# ============================================
# 5) Exibir fontes usadas na resposta
# ============================================
def show_sources(retriever, query: str):
    source_docs = retriever.invoke(query)
    print("\n==== Fontes Utilizadas ====\n")
    for i, doc in enumerate(source_docs, start=1):
        src  = doc.metadata.get("source", "desconhecido")
        page = doc.metadata.get("page", "N/A")
        snippet = doc.page_content[:120].replace("\n", " ")
        print(f"[{i}] {src}  (página {page})")
        print(f"     \"{snippet}...\"")


# ============================================
# Main
# ============================================
def main():
    parser = argparse.ArgumentParser(description="RAG com LangChain + Ollama")
    parser.add_argument(
        "--pdf", default=PDF_PATH,
        help="Caminho para o PDF (padrão: docs/Artigo.pdf)"
    )
    parser.add_argument(
        "--pergunta", default=None,
        help="Pergunta a ser respondida (se omitida, modo interativo)"
    )
    parser.add_argument(
        "--rebuild-index", action="store_true",
        help="Força a recriação do índice FAISS mesmo se já existir"
    )
    args = parser.parse_args()

    # Força rebuild se solicitado
    if args.rebuild_index and os.path.exists(INDEX_PATH):
        import shutil
        shutil.rmtree(INDEX_PATH)
        print(f"🗑️  Índice '{INDEX_PATH}' removido. Será recriado.")

    # Pipeline
    try:
        docs     = load_pdf(args.pdf)
        chunks   = split_documents(docs)

        embeddings = OllamaEmbeddings(model=EMBED_MODEL)
        vectordb   = get_vectorstore(chunks, embeddings)
        retriever  = vectordb.as_retriever(search_kwargs={"k": TOP_K})

        llm = ChatOllama(model=LLM_MODEL, temperature=TEMPERATURE)
        chain = build_chain(retriever, llm)

    except (FileNotFoundError, ValueError) as e:
        print(f"\n❌ Erro: {e}")
        return

    # Modo interativo ou argumento direto
    if args.pergunta:
        perguntas = [args.pergunta]
    else:
        print("\n💬 Modo interativo. Digite 'sair' para encerrar.\n")
        perguntas = []
        while True:
            q = input("Sua pergunta: ").strip()
            if q.lower() in {"sair", "exit", "quit"}:
                break
            if q:
                perguntas.append(q)
                break  # uma por vez no loop simples

    for pergunta in perguntas:
        print(f"\n{'='*50}")
        print(f"❓ Pergunta: {pergunta}")
        print(f"{'='*50}\n")

        try:
            # O fluxo completo resumido:
            # pergunta → busca chunks → formata contexto → monta prompt → LLM → texto da resposta    
            resposta = chain.invoke(pergunta)
            print("🤖 Resposta:\n")
            print(resposta)
            show_sources(retriever, pergunta)
        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {e}")


if __name__ == "__main__":
    main()
