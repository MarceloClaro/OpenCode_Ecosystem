from fastapi import APIRouter

router = APIRouter()

@router.get("/enviar_mensagem")
async def enviar_mensagem(cliente_id: str, mensagem: str):
    try:
        # Simula envio de mensagem
        return {
            "status": "Mensagem enviada com sucesso",
            "cliente_id": cliente_id,
            "mensagem": mensagem
        }
    except Exception as e:
        return {"error": f"Erro ao enviar mensagem: {str(e)}"}

