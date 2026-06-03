"""Reactome database client for OpenCode Ecosystem."""
import sys
import os
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'science_skills_common'))
from http_client import HttpClient


class ReactomeClient:
    """Search pathways by gene, protein, or pathway name."""

    def __init__(self):
        self.client = HttpClient(base_url="https://reactome.org/ContentService", qps=5.0)

    def search(self, query, limit=10):
        results = []
        try:
            encoded = urllib.parse.quote(query)
            data = self.client.fetch_json(
                f"/search/query?query={encoded}&species=Homo%20sapiens&types=Pathway&pageSize={limit}"
            )
            entries = data.get("results", [])
            results = [{"id": e.get("stId", ""), "name": e.get("name", ""),
                        "species": e.get("species", [""])[0] if e.get("species") else ""}
                       for e in entries]
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "Reactome"}
        return {"status": "ok", "results": results, "source": "Reactome"}

    def search_by_gene(self, gene_symbol):
        try:
            encoded = urllib.parse.quote(gene_symbol)
            data = self.client.fetch_json(
                f"/search/query?query={encoded}&species=Homo%20sapiens&types=Pathway&pageSize=20"
            )
            entries = data.get("results", [])
            return {"status": "ok", "results": [
                {"id": e.get("stId"), "name": e.get("name")} for e in entries
            ], "source": "Reactome"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "Reactome"}

    def get_pathway_details(self, pathway_id):
        try:
            data = self.client.fetch_json(f"/data/query/{pathway_id}")
            return {"status": "ok", "results": data, "source": "Reactome"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "Reactome"}

    @property
    def available(self):
        return True


if __name__ == "__main__":
    c = ReactomeClient()
    print(f"Reactome available: {c.available}")
    print(c.search("apoptosis", limit=2))
