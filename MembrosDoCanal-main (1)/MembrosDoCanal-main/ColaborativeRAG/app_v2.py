import os
import uuid
import hashlib
from datetime import datetime, UTC

import streamlit as st
import chromadb
from ollama import Client as OllamaClient

# ================= CONFIG =================
st.set_page_config(page_title="RAG Contínuo Expandido", page_icon="🧠", layout="wide")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1:8b")
EMB_MODEL = os.environ.get("EMB_MODEL", "bge-m3:latest")
CHROMA_PATH = os.environ.get("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "qa_pairs")

ollama = OllamaClient(host=OLLAMA_HOST)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# coleção principal
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},
)

# coleção de pendentes de revisão
review_collection = chroma_client.get_or_create_collection(
    name="qa_pending_review",
    metadata={"hnsw:space": "cosine"},
)

# ================= FUNÇÕES =================
def get_embedding(text: str):
    res = ollama.embeddings(model=EMB_MODEL, prompt=text)
    return res["embedding"]

def make_doc_text(question: str, answer: str) -> str:
    return f"Q: {question.strip()}\nA: {answer.strip()}"

def compute_hash(question: str, answer: str) -> str:
    return hashlib.sha256((question.strip() + answer.strip()).encode()).hexdigest()

def add_qa_to_vectorstore(question: str, answer: str, user_id: str, topic: str, source="user_seed"):
    text = make_doc_text(question, answer)
    doc_hash = compute_hash(question, answer)

    # evitar duplicados
    results = collection.get(where={"hash": doc_hash})
    if results and results.get("ids"):
        return None  # já existe

    emb = get_embedding(text)
    _id = str(uuid.uuid4())
    collection.add(
        ids=[_id],
        embeddings=[emb],
        documents=[text],
        metadatas=[{
            "question": question,
            "answer": answer,
            "user_id": user_id,
            "topic": topic,
            "hash": doc_hash,
            "source": source,
            "created_at": datetime.now(UTC).isoformat()
        }]
    )
    return _id

def count_user_contributions(user_id: str, topic: str = None):
    results = collection.get(include=["metadatas"])
    metas = results.get("metadatas", [])
    if not metas:
        return 0
    return sum(
        1 for m in metas if m and m.get("user_id") == user_id and (not topic or m.get("topic") == topic)
    )

def search_similar(query: str, topic: str, k: int = 5):
    query_emb = get_embedding(query)
    where = {"topic": topic} if topic else {}
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=k,
        include=["distances","metadatas","documents"],
        where=where
    )
    out = []
    if results and results.get("ids"):
        for i in range(len(results["ids"][0])):
            out.append({
                "id": results["ids"][0][i],
                "distance": results["distances"][0][i],
                "metadata": results["metadatas"][0][i],
                "document": results["documents"][0][i],
            })
    return out

def build_context_blocks(hits, max_chars=2000):
    blocks, total = [], 0
    for h in hits:
        q, a = h["metadata"].get("question",""), h["metadata"].get("answer","")
        text = f"Q: {q}\nA: {a}"
        if total + len(text) > max_chars: break
        blocks.append(text)
        total += len(text)
    return "\n\n".join(blocks)

def answer_with_rag(question: str, hits):
    context = build_context_blocks(hits)
    system_msg = (
        "Você é um assistente especializado. Use SOMENTE o contexto fornecido. "
        "Se não houver base suficiente, diga isso claramente."
    )
    user_msg = f"Pergunta: {question}\n\nContexto:\n{context}"
    resp = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role":"system","content":system_msg},{"role":"user","content":user_msg}],
        options={"temperature":0.2}
    )
    return resp["message"]["content"]

# ================= UI =================
st.sidebar.title("🔧 Configurações")
page = st.sidebar.radio("Navegação", ["Assistente", "Admin"])

user_id = st.sidebar.text_input("Seu ID (email ou apelido)", value="")
topic = st.sidebar.text_input("Tópico/área de expertise", value="Geral")

# ========== PÁGINA: ASSISTENTE ==========
if page == "Assistente":
    st.title("🧠 RAG Contínuo Expandido")
    if not user_id:
        st.warning("Informe seu ID na barra lateral.")
        st.stop()

    MIN_QA = 1
    if count_user_contributions(user_id, topic) < MIN_QA:
        st.header("👋 Primeiro acesso: cadastre 5 QAs")
        with st.form("seed_form"):
            qa_rows = []
            for i in range(1, MIN_QA+1):
                q = st.text_area(f"Pergunta {i}", key=f"q{i}")
                a = st.text_area(f"Resposta {i}", key=f"a{i}")
                qa_rows.append((q,a))
            submitted = st.form_submit_button("Salvar")
            if submitted:
                ok = 0
                for q,a in qa_rows:
                    if q and a:
                        if add_qa_to_vectorstore(q,a,user_id,topic,"user_seed"):
                            ok+=1
                st.success(f"{ok} QAs salvos!")
                st.rerun()
        st.stop()

    st.subheader("❓ Pergunte")
    question = st.text_area("Sua pergunta:")
    if st.button("Responder"):
        hits = search_similar(question, topic, k=5)
        st.write("🔎 Contexto recuperado:")
        for h in hits:
            st.caption(f"Q: {h['metadata']['question']}\nA: {h['metadata']['answer']} (autor: {h['metadata']['user_id']})")
        answer = answer_with_rag(question,hits)
        st.subheader("Resposta")
        st.write(answer)
        col1,col2 = st.columns(2)
        if col1.button("👍 Correto"):
            add_qa_to_vectorstore(question, answer, user_id, topic, source="validated")
            st.success("Adicionado ao banco!")
        if col2.button("👎 Incorreto"):
            _id = str(uuid.uuid4())
            review_collection.add(
                ids=[_id],
                documents=[f"Q: {question}\nA (INCORRETA): {answer}"],
                metadatas=[{
                    "question": question,
                    "answer_incorreta": answer,
                    "user_id": user_id,
                    "topic": topic,
                    "created_at": datetime.now(UTC).isoformat()
                }]
            )
            st.warning("Enviado para a fila de revisão do Admin.")

# ========== PÁGINA: ADMIN ==========
if page == "Admin":
    st.title("📋 Administração / Curadoria")
    results = collection.get(include=["metadatas","documents"])
    metas, docs, ids = results.get("metadatas",[]), results.get("documents",[]), results.get("ids",[])
    st.write(f"Total de itens (base principal): {len(ids)}")

    filtro_user = st.text_input("Filtrar por user_id")
    filtro_topic = st.text_input("Filtrar por tópico")

    for _id,meta,doc in zip(ids,metas,docs):
        if not meta: continue
        if filtro_user and meta.get("user_id")!=filtro_user: continue
        if filtro_topic and meta.get("topic")!=filtro_topic: continue

        with st.expander(f"ID: {_id} | User: {meta.get('user_id')} | Topic: {meta.get('topic')}"):
            st.write(doc)
            st.json(meta)

            with st.form(f"edit_form_{_id}"):
                new_q = st.text_area("Pergunta", value=meta.get("question",""))
                new_a = st.text_area("Resposta", value=meta.get("answer",""))
                new_topic = st.text_input("Tópico", value=meta.get("topic",""))
                edited = st.form_submit_button("💾 Salvar alterações")

                if edited:
                    collection.delete(ids=[_id])
                    add_qa_to_vectorstore(
                        question=new_q,
                        answer=new_a,
                        user_id=meta.get("user_id",""),
                        topic=new_topic,
                        source="edited"
                    )
                    st.success("QA atualizado com sucesso!")
                    st.rerun()

            if st.button(f"🗑️ Remover {_id}"):
                collection.delete(ids=[_id])
                st.warning(f"Removido {_id}")
                st.rerun()

    # ====== FILA DE REVISÃO ======
    st.subheader("📝 Itens pendentes de revisão")
    rev = review_collection.get(include=["metadatas","documents"])
    if not rev["ids"]:
        st.info("Nenhum item pendente.")
    else:
        for _id,meta,doc in zip(rev["ids"],rev["metadatas"],rev["documents"]):
            with st.expander(f"ID: {_id} | User: {meta.get('user_id')} | Topic: {meta.get('topic')}"):
                st.write(doc)
                st.json(meta)

                with st.form(f"review_form_{_id}"):
                    corrected = st.text_area("Resposta corrigida")
                    approve = st.form_submit_button("✅ Aprovar e mover")
                    if approve and corrected.strip():
                        add_qa_to_vectorstore(
                            question=meta.get("question",""),
                            answer=corrected,
                            user_id=meta.get("user_id",""),
                            topic=meta.get("topic",""),
                            source="reviewed"
                        )
                        review_collection.delete(ids=[_id])
                        st.success("QA corrigido e movido para a base principal!")
                        st.rerun()

                if st.button(f"🗑️ Descartar {_id}"):
                    review_collection.delete(ids=[_id])
                    st.warning("Item descartado da revisão.")
                    st.rerun()
