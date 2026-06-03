"""arXiv API client for OpenCode Ecosystem."""
import sys
import os
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'science_skills_common'))
from http_client import HttpClient

ARXIV_NS = {"atom": "http://www.w3.org/2005/Atom"}
ARXIV_OPENSEARCH = {"opensearch": "http://a9.com/-/spec/opensearch/1.1/"}


class ArxivClient:
    """Search arXiv preprints by keyword, author, or category."""

    def __init__(self):
        self.client = HttpClient(base_url="http://export.arxiv.org/api", qps=1.0)

    def search(self, query, limit=10):
        results = []
        try:
            encoded = urllib.parse.quote(query)
            resp = self.client.fetch(
                f"/query?search_query=all:{encoded}&start=0&max_results={limit}"
            )
            root = ET.fromstring(resp.text)
            for entry in root.findall("atom:entry", ARXIV_NS):
                results.append({
                    "id": self._text(entry, "atom:id"),
                    "title": self._text(entry, "atom:title"),
                    "summary": self._text(entry, "atom:summary"),
                    "published": self._text(entry, "atom:published"),
                    "authors": [a.find("atom:name", ARXIV_NS).text
                                for a in entry.findall("atom:author", ARXIV_NS)],
                    "category": self._attrib(entry, "atom:category", "term"),
                })
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "arXiv"}
        return {"status": "ok", "results": results, "source": "arXiv"}

    def search_by_author(self, author, limit=10):
        try:
            encoded = urllib.parse.quote(author)
            resp = self.client.fetch(
                f"/query?search_query=au:{encoded}&start=0&max_results={limit}"
            )
            root = ET.fromstring(resp.text)
            results = [{"title": self._text(e, "atom:title"),
                        "published": self._text(e, "atom:published")}
                       for e in root.findall("atom:entry", ARXIV_NS)]
            return {"status": "ok", "results": results, "source": "arXiv"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "arXiv"}

    def search_by_category(self, category, limit=10):
        try:
            encoded = urllib.parse.quote(category)
            resp = self.client.fetch(
                f"/query?search_query=cat:{encoded}&start=0&max_results={limit}&sortBy=submittedDate&sortOrder=descending"
            )
            root = ET.fromstring(resp.text)
            results = [{"id": self._text(e, "atom:id"),
                        "title": self._text(e, "atom:title")}
                       for e in root.findall("atom:entry", ARXIV_NS)]
            return {"status": "ok", "results": results, "source": "arXiv"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "arXiv"}

    def _text(self, element, tag):
        child = element.find(tag, ARXIV_NS)
        return child.text.strip() if child is not None and child.text else ""

    def _attrib(self, element, tag, attr):
        child = element.find(tag, ARXIV_NS)
        return child.attrib.get(attr, "") if child is not None else ""

    @property
    def available(self):
        return True


if __name__ == "__main__":
    c = ArxivClient()
    print(f"arXiv available: {c.available}")
    print(c.search("machine learning", limit=2))
