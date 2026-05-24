import os
import uuid
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import logging

# CONFIGS
FAISS_INDEX_PATH = "./faiss_ti.bin"
CASES_DB_PATH = "./cases_ti.json"
EMBED_MODEL = "all-MiniLM-L6-v2"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

embedder = SentenceTransformer(EMBED_MODEL)

def carregar_casos():
    if os.path.exists(CASES_DB_PATH):
        with open(CASES_DB_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def salvar_casos(casos):
    with open(CASES_DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(casos, f, ensure_ascii=False, indent=2)

def indexar_casos(casos):
    vectors = [embedder.encode(c['problema']) for c in casos]
    dim = len(vectors[0])
    index = faiss.IndexFlatIP(dim)
    vectors = np.array(vectors)
    faiss.normalize_L2(vectors)
    index.add(vectors.astype('float32'))
    faiss.write_index(index, FAISS_INDEX_PATH)
    salvar_casos(casos)
    logger.info(f"✓ Indexados {len(casos)} casos no FAISS!")

def buscar_caso_similar(pergunta, k=1, threshold=0.3):
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(CASES_DB_PATH):
        logger.warning("⚠️  Base de dados não encontrada!")
        return None
    index = faiss.read_index(FAISS_INDEX_PATH)
    casos = carregar_casos()
    if len(casos) == 0:
        logger.warning("⚠️  Nenhum caso na base!")
        return None
    query_vector = embedder.encode(pergunta).reshape(1, -1)
    faiss.normalize_L2(query_vector)
    distances, indices = index.search(query_vector.astype('float32'), min(k, len(casos)))
    if len(indices) > 0 and indices[0][0] != -1:
        idx = indices[0][0]
        similarity = distances[0][0]
        if similarity >= threshold:
            return casos[idx]
    return None

def adicionar_caso(problema, solucao, fonte="usuario"):
    casos = carregar_casos()
    novo_caso = {
        "id": str(uuid.uuid4()),
        "problema": problema,
        "solucao": solucao,
        "fonte": fonte,
        "data_adicao": str(uuid.uuid4())[:8]
    }
    casos.append(novo_caso)
    indexar_casos(casos)
    logger.info(f"✅ Novo caso adicionado na base! Fonte: {fonte}")
