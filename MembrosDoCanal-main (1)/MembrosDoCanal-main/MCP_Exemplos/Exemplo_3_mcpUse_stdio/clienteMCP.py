import asyncio
from mcp_use import MCPClient

async def main():
    config = {
        "mcpServers": {
            "mcp_use_exemplo": {
            "command": "python",
            "args": [
                "servidorMCP.py"
            ]
            }
        }
    }

    client = MCPClient.from_dict(config)

    await client.create_all_sessions()

    session = client.get_session("mcp_use_exemplo")
    
    result = await session.call_tool("greet", {"name": "Priscilla"})    

    print(f"Result: {result.content[0].text}")

    await client.close_all_sessions()

asyncio.run(main())