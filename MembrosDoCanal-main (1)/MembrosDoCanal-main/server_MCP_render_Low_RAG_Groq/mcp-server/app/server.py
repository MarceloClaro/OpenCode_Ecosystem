from mcp.server.fastmcp import FastMCP
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os
import httpx
from typing import List

mcp = FastMCP("GroqRAG")

# Inicialização do RAG
model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384
index = faiss.IndexFlatL2(dimension)
corpus_texts: List[str] = []

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # ou "llama3-70b-8192"

async def chat_with_groq(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {"role": "system", "content": "Você é um assistente especializado com acesso a documentos."},
            {"role": "user", "content": prompt}
        ],
        "model": GROQ_MODEL
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]


#@mcp.tool()
@mcp.tool(name='add_knowledge', description="Adiciona texto ao banco de conhecimento.")
async def add_knowledge(text: str) -> str:
    """
    Adiciona texto ao banco de conhecimento.
    """
    embedding = model.encode([text])
    index.add(np.array(embedding).astype("float32"))
    corpus_texts.append(text)
    return "Texto adicionado com sucesso à base de conhecimento."


@mcp.tool(name='ask_rag', description="Pergunta ao banco de conhecimento.")
async def ask_rag(question: str) -> str:
    """
    Responde com base nos textos adicionados.
    """
    if index.ntotal == 0:
        return "Base de conhecimento vazia. Adicione conteúdo com `add_knowledge`."

    question_embedding = model.encode([question])
    distances, indices = index.search(np.array(question_embedding).astype("float32"), k=3)
    retrieved = [corpus_texts[i] for i in indices[0] if i < len(corpus_texts)]

    context = "\n".join(retrieved)
    prompt = f"Com base no seguinte contexto, responda à pergunta:\n\n{context}\n\nPergunta: {question}"

    try:
        return await chat_with_groq(prompt)
    except Exception as e:
        return f"Erro na resposta com a Groq: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="sse")
