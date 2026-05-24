import asyncio
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

async def main():
    """Rodar o cliente MCP conectado ao seu assistente de vendas.""" 
    # Configuração do servidor MCP local
    config = {
        "mcpServers": {
            "http": {
                "url": "http://localhost:8000/mcp"  # Seu servidor FastAPI-MCP
            }
        }
    }

    # Criar cliente MCP
    client = MCPClient.from_dict(config)

      
    llm = ChatOpenAI(model="gpt-4o", api_key="")
    
    # Criar agente MCP
    agent = MCPAgent(
        llm=llm,
        client=client,
        max_steps=30
    )

    # Rodar a consulta
    user_input = input("Digite seu comando de vendas: ")
    result = await agent.run(
        user_input,
        max_steps=30,
    )

    print(f"\n✅ Resultado final:\n{result}")

if __name__ == "__main__":
    asyncio.run(main())

