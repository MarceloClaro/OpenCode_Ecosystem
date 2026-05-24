import os
import uuid
import time
from datetime import datetime

import streamlit as st
import chromadb
from ollama import Client as OllamaClient

# ============ CONFIG BÁSICA ============
st.set_page_config(page_title="RAG Contínuo • Chroma + Ollama", page_icon="🧠", layout="wide")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
LLM_MODEL = os.environ.get("LLM_MODEL", "llama3.1:8b")
EMB_MODEL = os.environ.get("EMB_MODEL", "bge-m3:latest")
CHROMA_PATH = os.environ.get("CHROMA_PATH", "./chroma_db")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME", "qa_pairs")

# ============ CLIENTES ============
ollama = OllamaClient(host=OLLAMA_HOST)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "cosine"},  # distância cosseno para embeddings
)

# ============ FUNÇÕES UTILITÁRIAS ============
def get_embedding(text: str):
    """
    Usa o Ollama para gerar embeddings com bge-m3:latest.
    """
    res = ollama.embeddings(model=EMB_MODEL, prompt=text)
    return res["embedding"]

def normalize_text(s: str) -> str:
    """Remove espaços extras e normaliza quebras de linha.
    serve para deixar o texto limpo, sem ruído de múltiplos espaços,
    antes de salvar.
    s.strip() → remove espaços extras no começo e fim.
    s.split() → quebra o texto em palavras, ignorando múltiplos espaços/tabs no meio.
    " ".join(...) → junta de novo as palavras com um único espaço entre elas.
    """
    return " ".join(s.strip().split())

def make_doc_text(question: str, answer: str) -> str:
    """
    Formata o texto da Q/A para salvar no campo 'document' do Chroma."""
    return f"Q: {normalize_text(question)}\nA: {normalize_text(answer)}"

def add_qa_to_vectorstore(question: str, answer: str, user_id: str, source: str = "user_seed"):
    """
    Insere um par Q/A com embedding pré-computado.
    """
    text = make_doc_text(question, answer)
    emb = get_embedding(text)
    _id = str(uuid.uuid4())
    from datetime import UTC
    collection.add(
        ids=[_id],
        embeddings=[emb],
        documents=[text],
        metadatas=[{
            "question": question,
            "answer": answer,
            "user_id": user_id,
            "source": source,                 # "user_seed" nos 5 iniciais, "validated" nos 👍
            "created_at": datetime.now(UTC).isoformat()
        }]
    )
    return _id

def count_user_contributions(user_id: str) -> int:
    """
    Conta Q/As do usuário pelo metadado 'user_id'.
    (Chroma não tem count filtrado direto; então fazemos query ampla e filtramos em memória.)
    """
    # Estratégia: recuperar um n_results alto e filtrar por metadado.
    # Para bases grandes, seria melhor manter esse total num banco relacional.
    # Como protótipo, isto é suficiente.
    results = collection.get(include=["metadatas"])
    metas = results.get("metadatas", [])
    if not metas:
        return 0
    return sum(1 for m in metas if m and m.get("user_id") == user_id)

def search_similar(query: str, k: int = 5):
    query_emb = get_embedding(query)
    results = collection.query(query_embeddings=[query_emb], n_results=k, include=["distances", "metadatas", "documents"])
    # Padroniza saída
    out = []
    if results and results.get("ids"):
        for i in range(len(results["ids"][0])):
            out.append({
                "id": results["ids"][0][i],
                "distance": results["distances"][0][i] if results.get("distances") else None,
                "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                "document": results["documents"][0][i] if results.get("documents") else "",
            })
    return out

def build_context_blocks(hits, max_chars: int = 2500):
    """
    Junta QAs similares até atingir um limite de caracteres para passar ao LLM.
    """
    blocks = []
    total = 0
    for h in hits:
        q = h["metadata"].get("question", "")
        a = h["metadata"].get("answer", "")
        text = f"Q: {q}\nA: {a}".strip()
        if total + len(text) > max_chars:
            break
        blocks.append(text)
        total += len(text)
    return "\n\n".join(blocks)

def answer_with_rag(question: str, hits):
    """
    Constrói um prompt com as QAs recuperadas e chama o LLM do Ollama para responder.
    """
    context = build_context_blocks(hits)
    system_msg = (
        "Você é um assistente especializado que responde de forma curta, clara e correta. "
        "Use SOMENTE o contexto fornecido abaixo (Q/A históricas) para fundamentar sua resposta. "
        "Se o contexto não for suficiente, explique a limitação e peça mais detalhes. "
        "Cite quais Q/As inspiraram a resposta, referenciando os IDs quando possível."
    )
    user_msg = (
        f"Pergunta do usuário:\n{question}\n\n"
        f"----- CONTEXTO (Q/As relevantes) -----\n{context}\n\n"
        "Regras:\n"
        "1) Baseie-se no contexto.\n"
        "2) Seja preciso.\n"
        "3) Se faltarem detalhes, diga o que falta.\n"
        "4) Ao final, liste 'Fontes (IDs aproximados)' com os IDs (se disponíveis) ou breve referências.\n"
    )
    resp = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        options={"temperature": 0.2}
    )
    return resp["message"]["content"]

def gated_can_ask(user_id: str, min_seed: int = 5) -> bool:
    return count_user_contributions(user_id) >= min_seed

# ============ UI ============
st.title("🧠 Plataforma de IA para Aprendizagem Colaborativa")
st.caption("cada usuário contribui com perguntas e respostas → a base vai se moldando ao nível da turma., RAG para resposta e aprendizado contínuo com feedback.")

with st.sidebar:
    st.subheader("Configuração")
    user_id = st.text_input("Seu identificador (ex.: email ou apelido)", value="", placeholder="ex: priscilla@example.com")
    st.write("Modelos:")
    st.code(f"LLM_MODEL={LLM_MODEL}\nEMB_MODEL={EMB_MODEL}\nOLLAMA_HOST={OLLAMA_HOST}", language="bash")
    st.write("Banco vetorial:")
    st.code(f"Chroma path: {CHROMA_PATH}\nCollection: {COLLECTION_NAME}", language="bash")

    if user_id:
        total = count_user_contributions(user_id)
        st.info(f"Contribuições suas registradas: **{total}**")

st.divider()

if not user_id:
    st.warning("Informe seu **identificador** na barra lateral para começar.")
    st.stop()

# ============ PASSO 1: Onboarding com 2 QAs ============
MIN_QA = 2
if not gated_can_ask(user_id, min_seed=MIN_QA):
    st.header("👋 Primeiro acesso: cadastre 2 perguntas & respostas do seu tema de expertise")
    st.write("Preencha pelo menos 2 pares Q/A para liberar as perguntas ao assistente. "
             "Capriche na qualidade — isso será usado como base do conhecimento.")

    with st.form("seed_form", clear_on_submit=False):
        cols = st.columns(2)
        qa_rows = []
        for i in range(1, MIN_QA + 1):
            st.markdown(f"**QA {i}**")
            q = st.text_area(f"Pergunta {i}", key=f"seed_q_{i}", height=80)
            a = st.text_area(f"Resposta {i}", key=f"seed_a_{i}", height=100)
            qa_rows.append((q, a))
            st.markdown("---")

        submitted = st.form_submit_button("Salvar QAs iniciais")
        if submitted:
            valid_count = 0
            with st.spinner("Gerando embeddings e salvando no vetor..."):
                for (q, a) in qa_rows:
                    if q and a:
                        try:
                            add_qa_to_vectorstore(q, a, user_id=user_id, source="user_seed")
                            valid_count += 1
                        except Exception as e:
                            st.error(f"Erro ao inserir um QA: {e}")
                            time.sleep(0.2)
            st.success(f"Foram inseridos {valid_count} QAs.")
            st.rerun()

    st.stop()

# ============ PASSO 2: Perguntar ao assistente (RAG) ============
st.header("❓ Pergunte ao Assistente (RAG)")
user_question = st.text_area("Faça sua pergunta:", placeholder="Digite aqui sua pergunta...", height=100)

colA, colB = st.columns([1, 4])
with colA:
    top_k = st.number_input("Top-K documentos", min_value=1, max_value=10, value=5, step=1)
with colB:
    ask = st.button("Responder", type="primary", use_container_width=True)

if ask and user_question.strip():
    with st.spinner("Buscando contexto e gerando resposta..."):
        hits = search_similar(user_question, k=int(top_k))
        st.subheader("🔎 Fontes recuperadas")
        if hits:
            for h in hits:
                st.write(f"- **ID**: `{h['id']}` • **dist**: {round(h['distance'],4) if h['distance'] is not None else '—'} • **autor**: {h['metadata'].get('user_id','?')} • **source**: {h['metadata'].get('source','')}")
                st.caption(f"Q: {h['metadata'].get('question','')}\n\nA: {h['metadata'].get('answer','')}")
        else:
            st.info("Nenhuma fonte encontrada. (A base pode estar vazia.)")

        answer = answer_with_rag(user_question, hits)
        st.subheader("🧩 Resposta do Assistente")
        st.write(answer)

        # ============ PASSO 3: Feedback ============
        fb_cols = st.columns(3)
        with fb_cols[0]:
            good = st.button("👍 Está correta (salvar como novo QA)")
        with fb_cols[1]:
            bad = st.button("👎 Não está correta")
        with fb_cols[2]:
            st.write("")

        if good:
            try:
                add_qa_to_vectorstore(user_question, answer, user_id=user_id, source="validated")
                st.success("Registrado! Essa nova Q/A agora faz parte do conhecimento do assistente.")
            except Exception as e:
                st.error(f"Erro ao salvar Q/A validada: {e}")

        if bad:
            st.info("Ok — não salvaremos essa resposta. (Você pode refinar a pergunta ou contribuir depois.)")

# Rodapé
st.divider()
st.caption("Protótipo educacional • RAG contínuo com feedback humano • ChromaDB + Ollama")
