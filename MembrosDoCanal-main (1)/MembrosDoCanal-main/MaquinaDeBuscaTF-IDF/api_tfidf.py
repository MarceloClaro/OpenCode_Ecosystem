import os
import math
from collections import Counter
from fastapi import FastAPI, Query
from pydantic import BaseModel
import pymupdf4llm
from fastapi.staticfiles import StaticFiles

# Função para extrair texto em markdown de um PDF
def get_text_from_pdf(file_path):
    return pymupdf4llm.to_markdown(file_path)

# Função para calcular TF (Term Frequency)
def compute_tf(word_dict, doc):
    tf_dict = {}
    total_words = len(doc)
    for word, count in word_dict.items():
        tf_dict[word] = count / total_words
    return tf_dict

# Função para calcular IDF (Inverse Document Frequency)
def compute_idf(doc_list):
    idf_dict = {}
    total_docs = len(doc_list)
    
    # Contagem de documentos contendo cada palavra
    for doc in doc_list:
        for word in doc:
            if word in idf_dict:
                idf_dict[word] += 1
            else:
                idf_dict[word] = 1
    
    # Calcula IDF para cada palavra
    for word, count in idf_dict.items():
        idf_dict[word] = math.log(total_docs / float(count))
    return idf_dict

# Função para calcular TF-IDF
def compute_tf_idf(tf_bow, idfs):
    tf_idf = {}
    for word, tf_value in tf_bow.items():
        tf_idf[word] = tf_value * idfs.get(word, 0)
    return tf_idf

# Função para calcular similaridade de cosseno
def cosine_similarity(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    dot_product = sum([vec1[word] * vec2[word] for word in intersection])
    
    magnitude1 = math.sqrt(sum([val**2 for val in vec1.values()]))
    magnitude2 = math.sqrt(sum([val**2 for val in vec2.values()]))
    
    if not magnitude1 or not magnitude2:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

# Carregando documentos e pré-processando o corpus
directory_path = "artigos"
corpus = []
file_names = []
for filename in os.listdir(directory_path):
    if filename.endswith(".pdf"):
        file_path = os.path.join(directory_path, filename)
        md_text = get_text_from_pdf(file_path)
        corpus.append(md_text)
        file_names.append(filename)

# Pré-processamento do corpus: tokenização e contagem de palavras
docs = [doc.lower().split() for doc in corpus]
word_dicts = [Counter(doc) for doc in docs]

# Calcula TF para cada documento
tf_docs = [compute_tf(word_dict, doc) for word_dict, doc in zip(word_dicts, docs)]

# Calcula IDF para cada palavra no corpus
idfs = compute_idf(docs)

# Calcula TF-IDF para cada documento
tf_idf_docs = [compute_tf_idf(tf_doc, idfs) for tf_doc in tf_docs]

# Criação da API com FastAPI
app = FastAPI()

# Monta a pasta com os PDFs para servir os arquivos estáticos
app.mount("/files", StaticFiles(directory="artigos"), name="files")

class SearchResponse(BaseModel):
    document: str
    similarity: float

@app.get("/search", response_model=list[SearchResponse])
async def search(keywords: str = Query(..., description="Palavras-chave separadas por espaço")):
    # Processa as palavras-chave fornecidas pelo usuário
    keyword_list = keywords.lower().split()
    keyword_vector = compute_tf_idf(Counter(keyword_list), idfs)

    # Calcula a similaridade de cosseno entre as palavras-chave e cada documento
    similarities = []
    for i, tf_idf_doc in enumerate(tf_idf_docs):
        similarity = cosine_similarity(keyword_vector, tf_idf_doc)
        similarities.append((file_names[i], similarity))

    # Ordena os documentos por similaridade em ordem decrescente
    similarities = sorted(similarities, key=lambda x: x[1], reverse=True)

    # Prepara o resultado para retorno em JSON
    results = [{"document": doc, "similarity": sim} for doc, sim in similarities]

    return results
