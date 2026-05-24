import asyncio
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

async def main():
    # Create configuration dictionary
    config = {
        "mcpServers": {
            "http": {
                "url": "http://127.0.0.1:8000/sse"
            }
        }
    }

    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(config)
    
    llm = ChatOpenAI(
         model="gpt-4o",
         api_key=OPENAI_KEY
            
      )

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    # Run the query
    result = await agent.run(
    "Quero fazer um pedido de um Cheeseburger e uma Coca-Cola, meu email é teste@teste.com."
    )

    print(f"\nResult: {result}")

    # Busca e exibe o link de pagamento
    pagamento = None
    if isinstance(result, dict):
        pagamento = result.get("pagamento")
    elif isinstance(result, str):
        # Caso o resultado venha em string (ajuste se necessário)
        import json
        try:
            result_json = json.loads(result)
            pagamento = result_json.get("pagamento")
        except Exception:
            pass

    if pagamento and "payment_url" in pagamento:
        print("\nPague seu pedido usando o link Stripe:")
        print(pagamento["payment_url"])
    else:
        print("\nNenhum link de pagamento retornado.")

if __name__ == "__main__":
    asyncio.run(main())
