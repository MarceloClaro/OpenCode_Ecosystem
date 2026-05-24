from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

# Define a conexão com o seu servidor MCP local
toolset = MCPToolset(
    connection_params=SseServerParams(
        url="http://127.0.0.1:8001/sse"  # Seu servidor MCP rodando localmente
        # headers={}  # Se você tiver autenticação, adicione aqui
    ),
    tool_filter=["get_crypto_price", "get_crypto_info"]  # opcional, pode omitir se quiser usar todas
)

# Cria o agente
crypto_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="crypto_expert",
    instruction="Ajude o usuário a obter preços e informações sobre criptomoedas.",
    tools=[toolset]
)

root_agent = crypto_agent
# Executa a interação com o agente
if __name__ == "__main__":
    crypto_agent.run_interaction_loop()
