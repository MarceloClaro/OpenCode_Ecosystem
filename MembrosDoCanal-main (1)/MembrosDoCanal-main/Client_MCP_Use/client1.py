import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from mcp_use import MCPAgent, MCPClient

async def main():
    # Load environment variables
    load_dotenv()

    # Create configuration dictionary
    config = {
      "mcpServers": {
        "server-arxiv": {
        "command": "python",
        "args": ["C:\\Users\\Fabio\\llm\\Arxiv_MCP\\server\\server_arxiv.py"],
        "env": {
          "API_KEY": "value"
        }
      }
      }
    }

    # Create MCPClient from configuration dictionary
    client = MCPClient.from_dict(config)

    # Create LLM
    llm = ChatOpenAI(model="gpt-4o")

    # Create agent with the client
    agent = MCPAgent(llm=llm, client=client, max_steps=30)

    # Run the query
    result = await agent.run(
        "Busque por artigos sobre a IA e a LLM",
    )
    print(f"\nResult: {result}")

if __name__ == "__main__":
    asyncio.run(main())