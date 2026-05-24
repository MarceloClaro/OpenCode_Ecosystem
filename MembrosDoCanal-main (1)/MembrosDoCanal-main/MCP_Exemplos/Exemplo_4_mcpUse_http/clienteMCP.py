import asyncio
from mcp_use import MCPClient

async def main():

    config = {
    "mcpServers": {
        "meuServidor": {
            "transport": "http",
            "url": "http://127.0.0.1:8000/mcp",
        }
    }
}
    # Create MCPClient from config file
    client = MCPClient.from_dict(config)

    try:
        # Create and initialize sessions for configured servers
        await client.create_all_sessions()

        # Retrieve the session for the "exemplo" server (match the server name key in the config)
        session = client.get_session("meuServidor")

        # List available tools
        tools = await session.list_tools()
        tool_names = [t.name for t in tools]
        print(f"Available tools: {tool_names}")

        result_tool_add = await session.call_tool(name="greet", arguments={"name": "Priscilla"})

        # Handle and print the result
        if getattr(result_tool_add, "isError", False):
            print(f"Error: {result_tool_add.content}")
        else:
            print(f"Tool result: {result_tool_add.content}")
            print(f"Text result: {result_tool_add.content[0].text}")

    finally:
        # Ensure we clean up resources properly
        await client.close_all_sessions()
    

asyncio.run(main())

