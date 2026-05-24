import os
import io
import base64
import concurrent.futures
from typing import List

import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import sqlite3
import sqlite_vec
from sqlite_vec import serialize_float32
import ollama
import fitz  # PyMuPDF

from markitdown import MarkItDown
from ollama_adapter import OllamaAdapterMarkItDown


# ===============================
# 🔧 Configuração inicial / .env
# ===============================
load_dotenv()

DB_FILE = os.getenv("RAG_DB_FILE", "rag_ui.db")
EMBED_MODEL = os.getenv("EMBED_MODEL", "embeddinggemma:latest")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3.1:8b")
VLM_MODEL = os.getenv("VLM_MODEL", "qwen2.5vl:7b")

EMBED_DIM = int(os.getenv("EMBED_DIM", "768"))
TOP_K = int(os.getenv("TOP_K", "3"))

VLM_TIMEOUT = int(os.getenv("VLM_TIMEOUT", "300"))          # s
VLM_MAX_IMG_SIZE = int(os.getenv("VLM_MAX_IMG_SIZE", "1280"))  # px lado maior

# ===============================
# 🧠 Clientes (VLM + MarkItDown)
# ===============================
ollama_vlm_client = OllamaAdapterMarkItDown(
    model_name=VLM_MODEL,
    connect_timeout=5.0,
    read_timeout=VLM_TIMEOUT,
    max_side=VLM_MAX_IMG_SIZE,
)

markit = MarkItDown(
    llm_client=ollama_vlm_client,
    llm_model=VLM_MODEL,
    llm_prompt="Em 3 parágrafos descreva a imagem detalhadamente em pt-br",
    timeout=VLM_TIMEOUT,
)

# ===============================
# 🗄️ Banco de dados (SQLite + sqlite-vec)
# ===============================
def get_db_connection():
    db = sqlite3.connect(DB_FILE)
    db.enable_load_extension(True)
    sqlite_vec.load(db)
    db.enable_load_extension(False)
    db.execute(
        f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_docs
        USING vec0(embedding float[{EMBED_DIM}], content TEXT, source TEXT)
        """
    )
    db.commit()
    return db

def add_texts(db: sqlite3.Connection, texts: List[str], source="manual") -> int:
    """Gera embeddings e adiciona novos textos ao banco."""
    if not texts:
        return 0
    resp = ollama.embed(model=EMBED_MODEL, input=texts)
    embeddings = resp["embeddings"] if isinstance(resp, dict) else resp.embeddings
    with db:
        for text, emb in zip(texts, embeddings):
            db.execute(
                "INSERT INTO vec_docs(embedding, content, source) VALUES (?, ?, ?)",
                (serialize_float32(emb), text, source),
            )
    return len(texts)

def retrieve_context(db: sqlite3.Connection, query: str, k: int = TOP_K) -> List[str]:
    """Busca vetorial dos k documentos mais relevantes."""
    q_emb = ollama.embed(model=EMBED_MODEL, input=query)
    q_vec = (q_emb["embeddings"][0] if isinstance(q_emb, dict) else q_emb.embeddings[0])
    rows = db.execute(
        """
        SELECT content, distance
        FROM vec_docs
        WHERE embedding MATCH ?
        AND k = ?
        ORDER BY distance
        """,
        [serialize_float32(q_vec), k],
    ).fetchall()
    return [r[0] for r in rows]

def generate_answer(query: str, context_list: List[str]) -> str:
    """Gera resposta usando o LLM com base no contexto recuperado."""
    context_text = "\n".join(f"- {c}" for c in context_list)
    prompt = f"""
Você é um assistente de RAG (Retrieval-Augmented Generation).
Responda com base exclusivamente no contexto abaixo. Se não houver dados suficientes, diga isso claramente.

Contexto:
{context_text}

Pergunta: {query}

Responda de forma objetiva.
"""
    response = ollama.chat(model=LLM_MODEL, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"]

# ===============================
# 🧩 Conversões (MarkItDown + VLM)
# ===============================
def convert_image_to_markdown(image_bytes: bytes, mime: str) -> str:
    """
    Converte imagem → Markdown (thread separada) com compressão e timeout configuráveis.
    """
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail((VLM_MAX_IMG_SIZE, VLM_MAX_IMG_SIZE))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    data_url = f"data:{mime};base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(markit.convert, data_url)
        result = future.result(timeout=VLM_TIMEOUT)
    return result.text_content

def convert_pdf_to_markdown(pdf_bytes: bytes, dpi: int = 300) -> str:
    """
    Extrai texto de PDF:
    - Se tiver texto embutido, usa-o.
    - Se a página for escaneada (quase sem texto), renderiza como imagem e usa MarkItDown (VLM).
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_text_parts = []

    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if len(text) > 50:
            all_text_parts.append(f"\n--- Página {i+1} ---\n{text}\n")
        else:
            pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            data_url = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(markit.convert, data_url)
                result = future.result(timeout=VLM_TIMEOUT)
            all_text_parts.append(f"\n--- Página {i+1} (Markdown) ---\n{result.text_content}\n")

    return "".join(all_text_parts).strip()


# ===============================
# 🖥️ Streamlit UI
# ===============================
st.set_page_config(page_title="🧠 RAG Multimodal", layout="wide")
st.title("🧠 RAG Multimodal")
st.caption("Indexe textos, imagens (convertidas para Markdown via VLM) e PDFs; faça perguntas contextualizadas.")

db = get_db_connection()
tab_ingest, tab_query = st.tabs(["📚 Adicionar Conhecimento", "❓ Fazer Perguntas"])

# -------------------------------
# 📚 Ingestão (texto, imagem, PDF)
# -------------------------------
with tab_ingest:
    st.subheader("Adicionar Texto Manualmente")
    text_input = st.text_area("Digite ou cole texto (vários parágrafos):", height=160, placeholder="Cole seu conteúdo aqui...")
    if st.button("➕ Indexar texto"):
        if text_input.strip():
            count = add_texts(db, [text_input.strip()], source="texto_manual")
            st.success(f"✅ {count} texto(s) indexado(s)!")
        else:
            st.warning("Informe um texto para indexação.")

    st.markdown("---")
    st.subheader("Adicionar Imagem (convertida em Markdown via VLM)")
    img_file = st.file_uploader("Envie uma imagem (PNG/JPG/JPEG)", type=["png", "jpg", "jpeg"], key="img_upload")
    if img_file is not None:
        st.image(img_file, caption="Pré-visualização", use_container_width=True)
    if st.button("🖼️ Converter imagem e indexar"):
        if img_file is None:
            st.warning("Envie uma imagem primeiro.")
        else:
            try:
                with st.spinner("🧠 Processando imagem com VLM..."):
                    md_text = convert_image_to_markdown(img_file.read(), img_file.type)
                st.markdown("### 📝 Markdown extraído da imagem")
                st.markdown(md_text)
                add_texts(db, [md_text], source=f"imagem:{img_file.name}")
                st.success("✅ Imagem convertida e conteúdo indexado!")
            except concurrent.futures.TimeoutError:
                st.error(f"⏱️ Tempo limite de {VLM_TIMEOUT}s excedido durante a conversão da imagem.")
            except Exception as e:
                st.error(f"❌ Erro ao processar a imagem: {e}")

    st.markdown("---")
    st.subheader("Adicionar PDF (texto embutido ou escaneado via VLM)")
    pdf_file = st.file_uploader("Envie um PDF", type=["pdf"], key="pdf_upload")
    if st.button("📄 Processar PDF e indexar"):
        if pdf_file is None:
            st.warning("Envie um PDF primeiro.")
        else:
            try:
                with st.spinner("🧠 Processando PDF..."):
                    pdf_bytes = pdf_file.read()
                    md_text = convert_pdf_to_markdown(pdf_bytes, dpi=300)
                if not md_text.strip():
                    st.warning("⚠️ Não foi possível extrair conteúdo desse PDF.")
                else:
                    st.markdown("### 📝 Texto extraído do PDF")
                    st.markdown(md_text[:4000] + ("...\n\n*(trecho)*" if len(md_text) > 4000 else ""))
                    add_texts(db, [md_text], source=f"pdf:{pdf_file.name}")
                    st.success("✅ PDF processado e conteúdo indexado!")
            except concurrent.futures.TimeoutError:
                st.error(f"⏱️ Tempo limite de {VLM_TIMEOUT}s excedido durante a conversão do PDF.")
            except Exception as e:
                st.error(f"❌ Erro ao processar o PDF: {e}")

# -------------------------------
# ❓ Consulta (RAG)
# -------------------------------
with tab_query:
    st.subheader("Consultar base de conhecimento")
    query = st.text_input("Digite sua pergunta:", placeholder="Ex.: O que diz o documento sobre X?")
    topk = st.slider("Quantidade de trechos (k)", 1, 10, TOP_K)
    if st.button("🔎 Buscar & Responder"):
        if not query.strip():
            st.warning("Digite uma pergunta.")
        else:
            with st.spinner("🔍 Recuperando contexto relevante..."):
                context = retrieve_context(db, query, k=topk)

            if not context:
                st.warning("Nenhum contexto encontrado no banco de dados.")
            else:
                st.markdown("### 📄 Contexto Recuperado")
                for i, c in enumerate(context, 1):
                    with st.expander(f"Trecho {i}"):
                        st.write(c)

                with st.spinner(f"💬 Gerando resposta com {LLM_MODEL}..."):
                    answer = generate_answer(query, context)

                st.markdown("### 🤖 Resposta")
                st.write(answer)

# Observação: o Streamlit gerencia o ciclo da conexão do SQLite.
# Se preferir, feche a conexão manualmente ao sair.
# db.close()
