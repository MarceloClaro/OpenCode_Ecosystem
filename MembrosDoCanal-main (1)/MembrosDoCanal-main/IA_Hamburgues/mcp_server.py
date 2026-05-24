from fastmcp import FastMCP
from typing import List
from pydantic import BaseModel
import stripe
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração da chave Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# MODELS
class Produto(BaseModel):
    id: str
    nome: str
    descricao: str
    preco: float

class PedidoItem(BaseModel):
    produto_id: str
    quantidade: int

class PedidoRequest(BaseModel):
    itens: List[PedidoItem]
    cliente_email: str

# Banco de dados fictício de produtos
PRODUTOS_DB = {
    "h1": Produto(id="h1", nome="Cheeseburger", descricao="Hambúrguer com queijo", preco=15.90),
    "h2": Produto(id="h2", nome="Bacon Burger", descricao="Hambúrguer com bacon crocante", preco=18.50),
    "b1": Produto(id="b1", nome="Coca-Cola", descricao="Refrigerante 350ml", preco=6.00),
    "b2": Produto(id="b2", nome="Suco de Laranja", descricao="Suco natural", preco=8.00),
}

def calcular_total(itens: List[PedidoItem]) -> float:
    total = 0
    for item in itens:
        produto = PRODUTOS_DB.get(item.produto_id)
        if produto:
            total += produto.preco * item.quantidade
    return total

def processar_pagamento(total: float, email: str) -> dict:
    try:
        product = stripe.Product.create(
            name="Pedido Hamburgueria",
            description=f"Pedido realizado por {email}"
        )
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(total * 100),  # Stripe usa centavos
            currency="brl"
        )
        payment_link = stripe.PaymentLink.create(
            line_items=[{"price": price.id, "quantity": 1}],
            after_completion={
                "type": "redirect",
                "redirect": {"url": "http://localhost:8501"}
            }
        )
        print("PAYMENT LINK GERADO:", payment_link.url)  # Debug para garantir que gerou
        return {
            "status": "pendente",
            "payment_url": payment_link.url,
            "valor": total
        }
    except Exception as e:
        print("ERRO STRIPE:", e)
        return {
            "status": "erro",
            "erro": str(e)
        }

# FastMCP server com instrução para retornar JSON puro
mcp = FastMCP(name="HamburgueriaMCP", instructions="Você é um assistente de hamburgueria.")

@mcp.tool
def listar_hamburgueres() -> List[Produto]:
    """Lista os hambúrgueres disponíveis"""
    return [p for p in PRODUTOS_DB.values() if p.id.startswith("h")]

@mcp.tool
def listar_bebidas() -> List[Produto]:
    """Lista as bebidas disponíveis"""
    return [p for p in PRODUTOS_DB.values() if p.id.startswith("b")]

@mcp.tool
def fazer_pedido(pedido: PedidoRequest) -> dict:
    """Realiza um pedido com base nos itens e email do cliente"""
    total = calcular_total(pedido.itens)
    pagamento = processar_pagamento(total, pedido.cliente_email)
    return {
        "total": total,
        "pagamento": pagamento,
        "itens": pedido.itens
    }

if __name__ == "__main__":
    mcp.run(transport="sse", host="127.0.0.1", port=8000)
