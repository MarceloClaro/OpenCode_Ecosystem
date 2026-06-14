# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "mcp",
#   "rich",
#   "ollama",
# ]
# ///
"""
MCP stdio server exposing Ollama web_search and web_fetch as tools.

Environment:
- OLLAMA_API_KEY (required): if set, will be used as Authorization header.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any, Dict

from ollama import Client

try:
  from mcp.server.fastmcp import FastMCP  # type: ignore
  _FASTMCP_AVAILABLE = True
except Exception:
  _FASTMCP_AVAILABLE = False

if not _FASTMCP_AVAILABLE:
  from mcp.server import Server  # type: ignore
  from mcp.server.stdio import stdio_server  # type: ignore

OLLAMA_API_KEY = os.environ.get("OLLAMA_API_KEY", "")
client = Client(
  host="https://ollama.com",
  headers={"Authorization": f"Bearer {OLLAMA_API_KEY}"} if OLLAMA_API_KEY else {},
)


def _web_search_impl(query: str, max_results: int = 3) -> Dict[str, Any]:
  res = client.web_search(query=query, max_results=max_results)
  return res.model_dump()


def _web_fetch_impl(url: str) -> Dict[str, Any]:
  res = client.web_fetch(url=url)
  return res.model_dump()


if _FASTMCP_AVAILABLE:
  mcp = FastMCP("ollama-web")

  @mcp.tool()
  def web_search(query: str, max_results: int = 3) -> Dict[str, Any]:
    """Search the web for a query and return relevant results."""
    return _web_search_impl(query, max_results)

  @mcp.tool()
  def web_fetch(url: str) -> Dict[str, Any]:
    """Fetch a web page by URL and return its content."""
    return _web_fetch_impl(url)

  if __name__ == "__main__":
    mcp.run()

else:
  from mcp.types import Tool, TextContent  # type: ignore

  server = Server("ollama-web")

  @server.list_tools()
  async def list_tools():
    return [
      Tool(
        name="web_search",
        description="Search the web for a query and return relevant results.",
        inputSchema={
          "type": "object",
          "properties": {
            "query": {"type": "string", "description": "The search query"},
            "max_results": {"type": "integer", "description": "Max results (default 3, max 10)", "default": 3},
          },
          "required": ["query"],
        },
      ),
      Tool(
        name="web_fetch",
        description="Fetch a web page by URL and return its content.",
        inputSchema={
          "type": "object",
          "properties": {
            "url": {"type": "string", "description": "The URL to fetch"},
          },
          "required": ["url"],
        },
      ),
    ]

  @server.call_tool()
  async def call_tool(name: str, arguments: Dict[str, Any]):
    if name == "web_search":
      result = _web_search_impl(**arguments)
    elif name == "web_fetch":
      result = _web_fetch_impl(**arguments)
    else:
      raise ValueError(f"Unknown tool: {name}")
    return [TextContent(type="text", text=str(result))]

  async def main():
    async with stdio_server() as (read_stream, write_stream):
      await server.run(read_stream, write_stream, server.create_initialization_options())

  if __name__ == "__main__":
    asyncio.run(main())
