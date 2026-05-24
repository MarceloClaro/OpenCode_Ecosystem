import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

async def main():
    """Run the example using a configuration file."""
    # Load environment variables
    load_dotenv()

    config = {
        "mcpServers": {
            "http": {
                "url": "https://mcp-server-rag-groq.onrender.com/sse"
            }
        }
    }

    # Create MCPClient from config file
    client = MCPClient.from_dict(config)

    # Create LLM
    llm = ChatOpenAI(model="gpt-4o")

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    # Run the query
    #result = await agent.run(
    #     "Adicione no banco de conhecimento o seguinte texto: O sabor de pizza que o Fabio Santos gosta de comer é pizza de milho.",
    #    max_steps=30,
    #)

    # Run the query
    result = await agent.run(
        "Qual é o sabor de pizza que o Fabio Santos gosta?",
        max_steps=30,
    )

    print(f"\nResult: {result}")

if __name__ == "__main__":
    # Run the appropriate example
    asyncio.run(main())