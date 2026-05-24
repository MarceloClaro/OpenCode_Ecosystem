# ./adk_agent_samples/mcp_http_agent/agent.py
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

# URL do servidor MCP remoto
REMOTE_MCP_URL = "http://localhost:8001/mcp"

# Configuração opcional de headers (ex: autenticação)
#HEADERS = {"Authorization": "Bearer my-token-123"}

# Criação do agente
root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="remote_mcp_agent",
    instruction="Use as ferramentas disponíveis do servidor MCP remoto para mostra uma mensagem de saudação para um nome de um usuário.",
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=REMOTE_MCP_URL,
                #headers=HEADERS
            ),
            tool_filter=["greet"],  # opcional
        )
    ],
)




