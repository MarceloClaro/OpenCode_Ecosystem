import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

async def main():
    """Run the example using a configuration file."""
    # Load environment variables
    load_dotenv()

    # Create MCPClient from config file  
    client = MCPClient.from_config_file(
        os.path.join(os.path.dirname(__file__), "rag-mcp.json")
    )

    # Create LLM
    llm = ChatOpenAI(model="gpt-4o")

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    # Run the query
    #result = await agent.run(
    #     "Adicione no banco de conhecimento  o texto: O Fabio Santos gosta de comer pizza de milho.",
    #    max_steps=30,
    #)

    # Run the query
    result = await agent.run(
        "Qual é a idade da Priscila?",
        max_steps=30,
    )

    print(f"\nResult: {result}")

if __name__ == "__main__":
    # Run the appropriate example
    asyncio.run(main())