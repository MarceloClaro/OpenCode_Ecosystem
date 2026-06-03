"""OpenTargets database client for OpenCode Ecosystem."""
import sys
import os
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'science_skills_common'))
from http_client import HttpClient


class OpenTargetsClient:
    """Search target-disease associations by gene or disease."""

    def __init__(self):
        self.client = HttpClient(base_url="https://api.platform.opentargets.org/api/v4", qps=5.0)

    def search(self, query, limit=10):
        results = []
        try:
            encoded = urllib.parse.quote(query)
            data = self.client.fetch_json(
                f"/graphql",
                method="POST",
                json_body={
                    "query": (
                        'query SearchTargets($q: String!, $size: Int!) {'
                        '  search(query: $q, entityNames: ["target"], page: {size: $size}) {'
                        '    hits { id name description }'
                        '  }'
                        '}'
                    ),
                    "variables": {"q": query, "size": limit},
                },
            )
            hits = data.get("data", {}).get("search", {}).get("hits", [])
            results = [{"id": h["id"], "name": h["name"], "description": h.get("description")} for h in hits]
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "OpenTargets"}
        return {"status": "ok", "results": results, "source": "OpenTargets"}

    def search_by_disease(self, disease_name, limit=10):
        try:
            encoded = urllib.parse.quote(disease_name)
            data = self.client.fetch_json(
                f"/graphql",
                method="POST",
                json_body={
                    "query": (
                        'query SearchDisease($q: String!, $size: Int!) {'
                        '  search(query: $q, entityNames: ["disease"], page: {size: $size}) {'
                        '    hits { id name description }'
                        '  }'
                        '}'
                    ),
                    "variables": {"q": disease_name, "size": limit},
                },
            )
            hits = data.get("data", {}).get("search", {}).get("hits", [])
            return {"status": "ok", "results": hits, "source": "OpenTargets"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "OpenTargets"}

    @property
    def available(self):
        return True


if __name__ == "__main__":
    c = OpenTargetsClient()
    print(f"OpenTargets available: {c.available}")
    print(c.search("BRAF", limit=2))
