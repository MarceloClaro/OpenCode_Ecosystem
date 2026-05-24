from fastapi import FastAPI
import sqlite3
from typing import List
from pydantic import BaseModel

app = FastAPI()

class Produto(BaseModel):
    id: int
    nome: str
    categoria: str
    preco: float
    quantidade: int

def get_produtos():
    conn = sqlite3.connect('produtos.db')
    c = conn.cursor()
    c.execute('SELECT * FROM produtos')
    produtos = c.fetchall()
    conn.close()
    return produtos

@app.get("/produtos", response_model=List[Produto])
def list_produtos():
    produtos = get_produtos()
    return [Produto(id=row[0], nome=row[1], categoria=row[2], preco=row[3], quantidade=row[4]) for row in produtos]

@app.get("/")
def greet_json():
    return {"Hello": "World!"}
