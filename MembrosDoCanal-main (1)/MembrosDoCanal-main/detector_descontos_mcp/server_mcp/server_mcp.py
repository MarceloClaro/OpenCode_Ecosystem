from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from tools.avaliar_descontos_tool import router as avaliar_router

app = FastAPI()

app.include_router(avaliar_router)

mcp = FastApiMCP(app)
mcp.mount()

@app.get("/")
async def root():
    return {"message": "Servidor MCP rodando com sucesso!"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)