"""STRING database client for OpenCode Ecosystem."""
import sys
import os
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'science_skills_common'))
from http_client import HttpClient


class StringClient:
    """Search protein-protein interactions by gene/protein identifier."""

    def __init__(self):
        self.client = HttpClient(base_url="https://string-db.org/api", qps=5.0)

    def search(self, query, limit=10):
        results = []
        try:
            encoded = urllib.parse.quote(query)
            data = self.client.fetch_json(
                f"/json/network?identifiers={encoded}&species=9606&limit={limit}"
            )
            for node in data:
                results.append({
                    "stringId": node.get("stringId_A"),
                    "partner": node.get("stringId_B"),
                    "score": node.get("score"),
                    "preferredName_A": node.get("preferredName_A"),
                    "preferredName_B": node.get("preferredName_B"),
                })
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "STRING"}
        return {"status": "ok", "results": results, "source": "STRING"}

    def search_interactions(self, gene_symbol, limit=50):
        try:
            encoded = urllib.parse.quote(gene_symbol)
            data = self.client.fetch_json(
                f"/json/interaction_partners?identifiers={encoded}&species=9606&limit={limit}"
            )
            results = [{"name": d.get("preferredName_B"), "score": d.get("score")} for d in data]
            return {"status": "ok", "results": results, "source": "STRING"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "STRING"}

    @property
    def available(self):
        return True


if __name__ == "__main__":
    c = StringClient()
    print(f"STRING available: {c.available}")
    print(c.search("TP53", limit=3))
