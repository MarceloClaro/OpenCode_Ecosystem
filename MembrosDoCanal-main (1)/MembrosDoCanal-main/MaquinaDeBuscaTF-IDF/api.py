from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from embbeding import model, chunked_pdfs
from qdrant_client import QdrantClient
import requests
import json
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Diretório onde os PDFs estão armazenados
pdf_directory = "documentos"  # Coloque o caminho correto para a pasta com os PDFs

# Verifica se o diretório existe e monta como um diretório estático
if os.path.isdir(pdf_directory):
    app.mount("/documentos", StaticFiles(directory=pdf_directory), name="documentos")
else:
    print(f"Diretório {pdf_directory} não encontrado.")


# Estrutura para resposta de busca de documentos
class SearchResponse(BaseModel):
    document: str
    similarity: float

# Configurações do Qdrant
QDRANT_CLOUD_URL = "https://20e89b3a-838b-49ae-aab2-99e82571dbae.us-east4-0.gcp.cloud.qdrant.io:6333"
API_KEY = "Lju12sgNtT32767Z6wpWNwhyINPo8o3doyLDJwdnSGiKdEvQzNWpLA"
client = QdrantClient(url=QDRANT_CLOUD_URL, api_key=API_KEY)

# Endpoint de busca
@app.get("/search", response_model=list[SearchResponse])
async def search(keywords: str = Query(..., description="Palavras-chave para busca")):
    keyword_list = keywords.lower().split()
    keyword_vector = model.encode([" ".join(keyword_list)])[0]

    results = client.search(
        collection_name="papers-test",
        query_vector=keyword_vector,
        limit=10
    )

    if not results:
        raise HTTPException(status_code=404, detail="Nenhum documento encontrado para as palavras-chave fornecidas.")
    
    return [{"document": result.payload["source"], "similarity": result.score} for result in results]

# Endpoint para obter conteúdo de um documento específico
@app.get("/document/{document_name}")
async def get_document_content(document_name: str):
    document_content = [doc['content'] for doc in chunked_pdfs if doc['source'] == document_name]
    if not document_content:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return {"content": " ".join(document_content)}

# Estrutura para solicitação de interação com documento
class InteractionRequest(BaseModel):
    query: str
    document_name: str

# Estrutura para resposta de interação
class InteractionResponse(BaseModel):
    answer: str

@app.post("/interact", response_model=InteractionResponse)
async def interact_with_document(request: InteractionRequest):
    # Busca o conteúdo do documento especificado
    document_content = [doc['content'] for doc in chunked_pdfs if doc['source'] == request.document_name]
    if not document_content:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    
    # Codifica a consulta do usuário para buscar os parágrafos mais relevantes
    query_vector = model.encode([request.query])[0]

    # Realiza uma busca no Qdrant para obter os parágrafos mais similares no documento selecionado
    results = client.search(
        collection_name="papers-test",
        query_vector=query_vector,
        limit=5
    )

    # Concatena os conteúdos dos parágrafos mais relevantes para formar o contexto
    contexto = "\n\n".join(result.payload.get("content", "") for result in results)

    # Monta o prompt para o modelo LLM usando o contexto extraído
    prompt = (
        f"Contexto:\n{contexto}\n\n"
        f"Pergunta: {request.query}\n"
        "Responda de forma clara e detalhada com base nas informações fornecidas. "
        "Caso não tenha a resposta exata, especifique que as informações são insuficientes."
    )

    # Configuração para chamada da API do LLM
    url = "http://127.0.0.1:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "temperature": 0.4
    }

    # Tente conectar ao LLM e obter a resposta
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        answer = response.json().get("response", "").strip()
    except requests.RequestException as e:
        print(f"Erro ao conectar com a API LLM: {e}")
        raise HTTPException(status_code=500, detail="Erro ao conectar com a API LLM.") from e
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar a resposta JSON: {e}")
        raise HTTPException(status_code=500, detail="Erro ao processar a resposta JSON da API LLM.") from e
    except Exception as e:
        print(f"Erro inesperado: {e}")
        raise HTTPException(status_code=500, detail="Erro inesperado ao processar a interação.")

    return {"answer": answer}

