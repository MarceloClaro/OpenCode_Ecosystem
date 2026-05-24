from fastapi import APIRouter
import random

router = APIRouter()

@router.get("/recomendar_produtos")
async def recomendar_produtos(cliente_id: str):
    try:
        produtos = ["Smartphone", "Notebook", "Fone de Ouvido", "Relógio Inteligente", "Tablet"]
        recomendados = random.sample(produtos, 2)
        return {"cliente_id": cliente_id, "recomendados": recomendados}
    except Exception as e:
        return {"error": f"Erro ao recomendar produtos: {str(e)}"}
