from typing import Any
import httpx
import xml.etree.ElementTree as ET
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("arxiv")

# Constants
ARXIV_API_BASE = "http://export.arxiv.org/api/query"
USER_AGENT = "arxiv-search-app/1.0"

async def make_arxiv_request(url: str) -> str | None:
    """Make a request to the arXiv API with proper error handling."""
    headers = {
        "User-Agent": USER_AGENT,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.text
        except Exception:
            return None

def parse_arxiv_response(xml_data: str) -> list[dict[str, Any]]:
    """Parse arXiv API XML response into structured data."""
    if not xml_data:
        return []
    
    root = ET.fromstring(xml_data)
    
    # Define namespaces used in arXiv API
    namespaces = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }
    
    entries = []
    for entry in root.findall('.//atom:entry', namespaces):
        # Extract basic information from each entry
        title = entry.find('atom:title', namespaces).text.strip() if entry.find('atom:title', namespaces) is not None else "No title"
        summary = entry.find('atom:summary', namespaces).text.strip() if entry.find('atom:summary', namespaces) is not None else "No summary"
        
        # Get authors
        authors = []
        for author in entry.findall('.//atom:author/atom:name', namespaces):
            authors.append(author.text.strip())
        
        # Get link to the paper
        link = entry.find('atom:id', namespaces).text if entry.find('atom:id', namespaces) is not None else "No link"
        
        # Get publication date
        published = entry.find('atom:published', namespaces).text if entry.find('atom:published', namespaces) is not None else "Unknown date"
        
        entries.append({
            'title': title,
            'summary': summary,
            'authors': authors,
            'link': link,
            'published': published
        })
    
    return entries

def format_paper(paper: dict) -> str:
    """Format a paper entry into a readable string."""
    authors_str = ", ".join(paper['authors']) if paper['authors'] else "Unknown author"
    
    return f"""
Title: {paper['title']}
Authors: {authors_str}
Published: {paper['published'][:10]}
Link: {paper['link']}
Summary: {paper['summary']}
"""

@mcp.tool()
async def search_arxiv(query: str, max_results: int = 5, start: int = 0) -> str:    
    # Format the query for URL
    formatted_query = query.replace(' ', '+')

    url = f"{ARXIV_API_BASE}?search_query=all:{formatted_query}&start={start}&max_results={max_results}"
    
    xml_data = await make_arxiv_request(url)
    if not xml_data:
        return "Unable to fetch results from arXiv."

    papers = parse_arxiv_response(xml_data)
    
    if not papers:
        return "No papers found matching your query."
    
    paper_texts = [format_paper(paper) for paper in papers]
    return "\n---\n".join(paper_texts)


if __name__ == "__main__":
    mcp.run()
