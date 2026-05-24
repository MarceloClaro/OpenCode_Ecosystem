from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .utils import get_transaction_data, ask_openai


app = FastAPI()

# Habilitar CORS para frontend Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str
    address: str

@app.post("/analyze/")
async def analyze(query: Query):
    tx_data = get_transaction_data(query.address)
    answer = ask_openai(query.question, tx_data)
    return {"response": answer}
