from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from tools.buscar_clientes_inativos import router as buscar_router
from tools.recomendar_produtos import router as recomendar_router
from tools.gerar_mensagem_personalizada import router as mensagem_router
from tools.enviar_mensagem import router as enviar_router

app = FastAPI()

# Incluir routers
app.include_router(buscar_router)
app.include_router(recomendar_router)
app.include_router(mensagem_router)
app.include_router(enviar_router)

# Montar MCP
mcp = FastApiMCP(app)
mcp.mount()

@app.get("/")
async def root():
    return {"message": "Servidor Assistente de Vendas MCP rodando com sucesso!"}
