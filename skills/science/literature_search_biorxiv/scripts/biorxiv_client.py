"""bioRxiv/medRxiv API client for OpenCode Ecosystem."""
import sys
import os
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'science_skills_common'))
from http_client import HttpClient


class BiorxivClient:
    """Search bioRxiv and medRxiv preprints by keyword, DOI, or date."""

    def __init__(self):
        self.client = HttpClient(base_url="https://api.biorxiv.org", qps=3.0)

    def search(self, query, limit=10):
        results = []
        try:
            encoded = urllib.parse.quote(query)
            data = self.client.fetch_json(
                f"/details/biorxiv/2020-01-01/2025-12-31/{limit}"
            )
            messages = data.get("messages", [{}])[0]
            if messages.get("status") == "ok":
                all_records = data.get("collection", [])
                query_lower = query.lower()
                for r in all_records:
                    title = r.get("title", "")
                    abstract = r.get("abstract", "")
                    if query_lower in title.lower() or query_lower in abstract.lower():
                        results.append({
                            "doi": r.get("doi"),
                            "title": title,
                            "category": r.get("category", ""),
                            "date": r.get("date", ""),
                            "authors": r.get("authors", ""),
                            "server": r.get("server", "biorxiv"),
                        })
                results = results[:limit]
            else:
                return {"status": "error", "message": "API returned non-ok status", "source": "bioRxiv"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "bioRxiv"}
        return {"status": "ok", "results": results, "source": "bioRxiv"}

    def search_by_doi(self, doi):
        try:
            encoded = urllib.parse.quote(doi.replace("https://doi.org/", ""))
            data = self.client.fetch_json(f"/details/biorxiv/10.1101/{encoded}")
            return {"status": "ok", "results": data.get("collection", []), "source": "bioRxiv"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "bioRxiv"}

    def search_by_date(self, start_date, end_date, limit=25):
        try:
            data = self.client.fetch_json(
                f"/details/biorxiv/{start_date}/{end_date}/{limit}"
            )
            return {"status": "ok",
                    "results": data.get("collection", []),
                    "source": "bioRxiv"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "bioRxiv"}

    @property
    def available(self):
        return True


if __name__ == "__main__":
    c = BiorxivClient()
    print(f"bioRxiv available: {c.available}")
    print(c.search("CRISPR", limit=2))
