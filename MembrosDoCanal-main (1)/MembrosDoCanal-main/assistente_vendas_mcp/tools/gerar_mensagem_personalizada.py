from fastapi import APIRouter

router = APIRouter()

@router.get("/gerar_mensagem_personalizada")
async def gerar_mensagem_personalizada(cliente_nome: str, produto: str):
    try:
        mensagem = f"Olá {cliente_nome}, sentimos sua falta! Aproveite nossa oferta especial no {produto}! Volte a comprar com a gente!"
        return {"mensagem": mensagem}
    except Exception as e:
        return {"error": f"Erro ao gerar mensagem personalizada: {str(e)}"}
