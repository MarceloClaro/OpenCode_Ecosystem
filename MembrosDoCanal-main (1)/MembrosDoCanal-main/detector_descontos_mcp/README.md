## Detector de Descontos Indevidos - via MCP + LLM Local

### Como executar:
1. Inicie o servidor Ollama com o modelo `gemma3:4b`
```bash
ollama run gemma:3b
```

2. Inicie o servidor FastAPI MCP
```bash
uvicorn server_mcp.main:app --reload --port 8000
```

3. Execute o cliente MCP com mcp-use
```bash
python client_mcp/cliente_mcp_use.py
```
