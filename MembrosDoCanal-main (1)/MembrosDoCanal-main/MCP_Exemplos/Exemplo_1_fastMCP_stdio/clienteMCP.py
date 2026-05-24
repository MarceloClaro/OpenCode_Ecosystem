import asyncio
from fastmcp import Client

async def main():
    async with Client("servidorMCP.py") as client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")

        result = await client.call_tool("greet", {"name": "Priscilla"})
        print(f"Result: {result.content[0].text}")

asyncio.run(main())
