from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

app = FastAPI()

# Definição do LLM e configuração
def generate_llm_response(prompt):
    url = "http://127.0.0.1:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    data = {
        "model": "deepseek-r1:7b", #deepseek-r1:7b
        "prompt": prompt,
        "stream": False,
        "temperature": 0.4
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Erro ao chamar a API LLaMA: {e}")

class GenerateRequest(BaseModel):
    prompt: str

@app.post("/api/generate")
async def generate_response(request: GenerateRequest):
    """Recebe um prompt e retorna uma resposta gerada pelo LLM remoto."""
    resposta = generate_llm_response(request.prompt)
    return {"resposta": resposta if resposta else "Nenhuma resposta gerada"}