from fastapi import FastAPI
from pydantic import BaseModel
import pickle

app = FastAPI()

with open("modelo.pkl", "rb") as f:
    modelo = pickle.load(f)

class Entrada(BaseModel):
    texto: str

@app.post("/predict")
def predict(entrada: Entrada):
    pred = modelo.predict([entrada.texto])[0]
    return {"sentimento": "positivo" if pred == 1 else "negativo"}