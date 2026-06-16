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
import urllib.request
import urllib.parse
import re
import json
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


def _fallback_web_search(query: str, max_results: int = 3) -> Dict[str, Any]:
    """Fallback using DuckDuckGo HTML search + Wikipedia search if blocked."""
    results = []
    
    # 1. Try DuckDuckGo
    try:
        encoded_term = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_term}"
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=6) as response:
            html = response.read().decode("utf-8", errors="ignore")
            
            blocks = re.split(r'<div class="web-result', html)
            if len(blocks) > 1:
                for block in blocks[1:max_results + 1]:
                    url_match = re.search(r'href="([^"]+)"', block)
                    title_match = re.search(r'class="result__a"[^>]*>(.*?)</a>', block, re.DOTALL)
                    snippet_match = re.search(r'<a class="result__snippet"[^>]*>(.*?)</a>', block, re.DOTALL)
                    
                    if url_match and title_match:
                        url_val = url_match.group(1)
                        if "uddg=" in url_val:
                            try:
                                url_val = urllib.parse.unquote(url_val.split("uddg=")[1].split("&")[0])
                            except Exception:
                                pass
                        title_val = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
                        snippet_val = ""
                        if snippet_match:
                            snippet_val = re.sub(r'<[^>]+>', '', snippet_match.group(1)).strip()
                        
                        results.append({
                            "title": title_val,
                            "url": url_val,
                            "content": snippet_val
                        })
            
            if not results:
                snippets = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
                urls = re.findall(r'<a class="result__url"[^>]*href="([^"]+)"', html)
                titles = re.findall(r'<a class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL)
                
                for idx in range(min(len(snippets), len(urls), len(titles), max_results)):
                    url_val = urls[idx]
                    if "uddg=" in url_val:
                        try:
                            url_val = urllib.parse.unquote(url_val.split("uddg=")[1].split("&")[0])
                        except Exception:
                            pass
                    results.append({
                        "title": re.sub(r'<[^>]+>', '', titles[idx]).strip(),
                        "url": url_val,
                        "content": re.sub(r'<[^>]+>', '', snippets[idx]).strip()
                    })
    except Exception as e:
        print(f"Fallback DuckDuckGo search error: {e}")
        
    # 2. Try Wikipedia (Portuguese and English) if DuckDuckGo failed/was blocked
    if not results:
        print("DuckDuckGo returned no results (possibly blocked). Trying Wikipedia fallback...")
        for lang in ["pt", "en"]:
            if len(results) >= max_results:
                break
            try:
                encoded_term = urllib.parse.quote_plus(query)
                wiki_url = f"https://{lang}.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={encoded_term}"
                req = urllib.request.Request(wiki_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=4) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    search_results = data.get("query", {}).get("search", [])
                    for item in search_results[:max_results - len(results)]:
                        title_val = item["title"]
                        snippet_val = re.sub(r'<[^>]+>', '', item["snippet"]).strip()
                        page_url = f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(title_val)}"
                        results.append({
                            "title": f"Wikipedia ({lang.upper()}) - {title_val}",
                            "url": page_url,
                            "content": snippet_val
                        })
            except Exception as e:
                print(f"Wikipedia {lang} fallback error: {e}")
                
    return {"results": results}



def _fallback_web_fetch(url: str) -> Dict[str, Any]:
    """Fallback fetch scraping raw HTML and extracting text."""
    try:
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")
            
            title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else url
            
            html_clean = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html_clean = re.sub(r'<style.*?>.*?</style>', '', html_clean, flags=re.DOTALL | re.IGNORECASE)
            
            links = []
            link_matches = re.findall(r'href="https?://[^"]+"', html_clean, re.IGNORECASE)
            for lm in link_matches[:20]:
                links.append(lm[6:-1])
            
            text = re.sub(r'<[^>]+>', ' ', html_clean)
            text = re.sub(r'\s+', ' ', text).strip()
            
            return {
                "title": title,
                "content": text[:15000],
                "links": list(set(links))
            }
    except Exception as e:
        return {
            "title": f"Failed to fetch {url}",
            "content": f"Error loading URL: {str(e)}",
            "links": []
        }


def _web_search_impl(query: str, max_results: int = 3) -> Dict[str, Any]:
  try:
    res = client.web_search(query=query, max_results=max_results)
    return res.model_dump()
  except Exception as e:
    print(f"Ollama web_search error, falling back: {e}")
    return _fallback_web_search(query, max_results)


def _web_fetch_impl(url: str) -> Dict[str, Any]:
  try:
    res = client.web_fetch(url=url)
    return res.model_dump()
  except Exception as e:
    print(f"Ollama web_fetch error, falling back: {e}")
    return _fallback_web_fetch(url)


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
