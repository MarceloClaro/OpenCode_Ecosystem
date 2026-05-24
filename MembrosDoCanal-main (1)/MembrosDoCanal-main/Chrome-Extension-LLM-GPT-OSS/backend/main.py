from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os, json
from groq import Groq
from fastapi.middleware.cors import CORSMiddleware

# Carrega variáveis de ambiente
load_dotenv()

app = FastAPI()

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializa cliente Groq
client = Groq()

# Modelo de requisição
class URLCheckRequest(BaseModel):
    url: str

@app.post("/check_url")
async def check_url(request: URLCheckRequest):
    """
    Verifica se uma URL é phishing e retorna o resultado com probabilidade (score de confiança).
    Exemplo: "Yes (92%)" ou "No (8%)"
    """
    prompt = (
        f"Analyze the following URL and determine if it is a phishing website. "
        f"Return ONLY a valid JSON object with these exact fields:\n"
        f'{{"is_phishing": "Yes" or "No", "confidence": <integer from 0 to 100>}}.\n\n'
        f"URL: {request.url}"
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-safeguard-20b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a cybersecurity analyst that detects phishing websites. "
                    "Respond ONLY in JSON format with the keys 'is_phishing' and 'confidence'."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_completion_tokens=8192,
        top_p=1,
        reasoning_effort="medium",
        stream=True,
        stop=None,
    )

    result_text = ""
    for chunk in completion:
        result_text += chunk.choices[0].delta.content or ""

    # Tenta converter o texto para JSON válido
    try:
        data = json.loads(result_text)
        phishing = data.get("is_phishing", "Unknown")
        confidence = data.get("confidence", 0)
        result = f"{phishing} ({confidence}%)"
    except Exception:
        result = f"Unable to parse model response: {result_text}"

    return {"result": result}

