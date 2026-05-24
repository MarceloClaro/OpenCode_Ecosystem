from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import numpy as np
from DataBaseManager import get_text_and_vector, get_index, get_model

app = FastAPI()
base_url = "http://127.0.0.1:8000"  # Servidor remoto para o LLM

class QueryRequest(BaseModel):
    question: str

@app.post("/query")
async def query(request: QueryRequest):
    """Processa uma questão usando FAISS e o LLM remoto."""

    # Recuperar os documentos armazenados no índice FAISS   
    documentos = get_text_and_vector()
    index = get_index()
    modelo = get_model()

    if not documentos:
        raise HTTPException(status_code=404, detail="Nenhum documento encontrado.")
    print(f"{len(documentos)} documentos armazenados no índice FAISS:")

    # Exibir os resultados armazenados
    for doc_id, texto, vetor in documentos:
        print(f"ID: {doc_id}, Texto (50 primeiros caracteres): {texto[:50]}, Dimensão do vetor: {len(vetor)}")

    # Gerar vetor para o texto da consulta
    try:
        vetor_query = modelo.encode([request.question])[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar vetor da consulta: {str(e)}")
    
    vetor_np = np.array(vetor_query, dtype=np.float32).reshape(1, -1)

    # Realizar busca no índice FAISS
    k = min(3, index.ntotal)
    try:
        distancias, indices = index.search(vetor_np, k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao realizar busca no índice FAISS: {str(e)}")

    # Filtrar os resultados válidos
    textos_relevantes = []
    for idx, distancia in zip(indices[0], distancias[0]):
        if 0 <= idx < len(documentos):  # Verifica se o índice está no intervalo de documentos
            if distancia < 40.0:       # Filtra pelas distâncias
                textos_relevantes.append(documentos[idx][1])
            else:
                print(f"Documento {idx} ignorado por distância ({distancia} >= 40.0)")
        else:
            print(f"Índice inválido {idx}, tamanho de documentos: {len(documentos)}")

    if textos_relevantes:
        print("Textos relevantes encontrados:")
        for texto in textos_relevantes:
            print(f"- {texto[:100]}...")
    else:
        print("Nenhum texto relevante encontrado.")
        raise HTTPException(status_code=404, detail="Nenhum texto relevante encontrado.")

    # Construir o contexto para o prompt
    contexto = "\n".join(textos_relevantes)

    # Criar o prompt para o LLM
    prompt = (
        f"Você é o Pesquisador AI, o assistente inteligente do laboratório de pesquisa Genius AI.\n\n"        
        f"Se o usuário lhe enviar uma saudação você deverá responder: Como posso lhe ajudar? .\n\n"
        f"Você também pode responder perguntas sobre os documentos somente tendo como base essas informações fornecidas:\n{contexto}\n\n"
        f"Responda de forma objetiva e clara essa pergunta: {request.question}. Não explique e nem adicione nenhum comentário. "
    )

    # Enviar o prompt para o LLM remoto
    response = requests.post(f"{base_url}/api/generate", json={"prompt": prompt})

    if response.status_code == 200:
        return response.json()
    raise HTTPException(status_code=response.status_code, detail="Erro ao processar a questão.")
