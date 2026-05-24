import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
import os

# Inicializar o modelo para gerar vetores
try:
    modelo = SentenceTransformer('BAAI/bge-m3')  # Modelo maior para melhor semântica
except:
    modelo = SentenceTransformer('all-MiniLM-L6-v2')

# Inicializar FAISS
DIMENSAO = 1024
INDEX_PATH = "bancoDeDadosVetorial/faiss_index.bin"
MEMORY_PATH = "bancoDeDadosVetorial/memoria_textos.json"

# Carregar ou criar índice FAISS
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
else:
    index = faiss.IndexFlatL2(DIMENSAO)

# Carregar ou inicializar memória associativa
if os.path.exists(MEMORY_PATH):
    with open(MEMORY_PATH, "r") as f:
        memoria_textos = json.load(f)
else:
    memoria_textos = {}

id_atual = len(memoria_textos)

def store_chunk(texto, fileName):
    """Armazena um texto e seu vetor correspondente no índice FAISS."""
    global id_atual
    vetor = modelo.encode([texto])[0]
    
    # Validação da dimensão do vetor
    assert len(vetor) == DIMENSAO, f"Dimensão do vetor incorreta: {len(vetor)} esperada {DIMENSAO}"

    vetor_np = np.array(vetor, dtype=np.float32).reshape(1, -1)
    index.add(vetor_np)
    memoria_textos[id_atual] = {"texto": texto, "fileName": fileName}
    id_atual += 1

    # Salvar índice e memória após cada adição
    faiss.write_index(index, INDEX_PATH)
    with open(MEMORY_PATH, "w") as f:
        json.dump(memoria_textos, f)


def get_text_and_vector(fileName=None):
    """Recupera textos e vetores do FAISS por nome de arquivo ou todos."""
    documentos = []
    for id, dados in memoria_textos.items():
        try:
            vetor = index.reconstruct(int(id))  # Garante que o ID está no índice
            if fileName is None or dados["fileName"] == fileName:
                documentos.append((id, dados["texto"], vetor))
        except RuntimeError:
            print(f"ID {id} não encontrado no índice FAISS. Ignorando.")
    return documentos


def get_index():
    """Retorna o índice FAISS atual."""
    return index

def get_model():
    """Retorna o modelo de embedding."""
    return modelo