from fastapi import APIRouter
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Exemplos por categoria
EXEMPLOS_INDEVIDOS = [
    "taxa de manutenção", "seguro não solicitado", "tarifa indevida", 
    "mensalidade de serviço não contratado"
]

EXEMPLOS_SUSPEITOS = [
    "débito automático desconhecido", "taxa extra", 
    "serviço identificado como 'outros'", "valor arredondado incomum"
]

EXEMPLOS_VALIDOS = [
    "pagamento de fatura", "saque autorizado", "transferência entre contas", 
    "compra com cartão", "PIX para conhecido"
]

@router.post("/avaliar_descontos")
def avaliar_descontos(texto: str) -> str:
    prompt = f"""
Você é um analista financeiro. Analise o extrato bancário a seguir e classifique cada linha como:
❌ Indevido — se corresponder claramente a exemplos indevidos.
⚠️ Suspeito — se for parecido com exemplos suspeitos ou levantar dúvidas.
✅ Válido — se corresponder aos exemplos válidos.

Use as listas abaixo como referência:

Exemplos de descontos ❌ Indevidos:
{chr(10).join(f"- {ex}" for ex in EXEMPLOS_INDEVIDOS)}

Exemplos de descontos ⚠️ Suspeitos:
{chr(10).join(f"- {ex}" for ex in EXEMPLOS_SUSPEITOS)}

Exemplos de descontos ✅ Válidos:
{chr(10).join(f"- {ex}" for ex in EXEMPLOS_VALIDOS)}

Agora analise o seguinte extrato bancário:

{texto}

Para cada linha, indique a classificação ao lado.
"""

    chat = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=OPENAI_API_KEY
    )
    result = chat([HumanMessage(content=prompt)])

    return result.content if result else "Erro ao analisar texto."


