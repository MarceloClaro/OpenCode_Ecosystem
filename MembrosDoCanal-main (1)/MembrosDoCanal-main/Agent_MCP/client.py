# Create server parameters for stdio connection
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# Configurando o modelo com os parâmetros corretos
model = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    api_key=" "  # Substitua com sua chave API
)

server_params = StdioServerParameters(
    command="python",
    # Make sure to update to the full absolute path to your math_server.py file
    args=["server.py"],
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # Get tools
            tools = await load_mcp_tools(session) 
            
            # Mostrar as ferramentas disponíveis
            print("\nFerramentas disponíveis no MCP Server:")
            for i, tool in enumerate(tools, 1):
                print(f"{i}. {tool.name}: {tool.description}")
            print("\n" + "="*50 + "\n")
            
            # Create and run the agent
            agent = create_react_agent(model, tools)
            
            # Criando a mensagem de entrada
            question = "what's (3 + 5) x 12?"
            
            # Executando o agente com o contexto correto
            agent_response = await agent.ainvoke({"messages": [{"role": "user", "content": question}]})
            
            # Extrair a resposta final do agente
            messages = agent_response['messages']
            final_message = messages[-1]  # Pega a última mensagem
            final_content = final_message.content if hasattr(final_message, 'content') else "Não foi possível obter uma resposta clara"
            
            # Imprimindo a resposta
            print(f"\nPergunta: {question}")
            print(f"Resposta: {final_content}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())