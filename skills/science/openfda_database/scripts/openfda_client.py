"""openFDA database client for OpenCode Ecosystem."""
import sys
import os
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'science_skills_common'))
from http_client import HttpClient


class OpenFDAClient:
    """Search FDA adverse events, drug labels, and recalls."""

    def __init__(self):
        self.client = HttpClient(base_url="https://api.fda.gov", qps=5.0)

    def search(self, query, limit=10):
        results = []
        try:
            encoded = urllib.parse.quote(query)
            data = self.client.fetch_json(
                f"/drug/event.json?search=patient.drug.medicinalproduct:{encoded}&limit={limit}"
            )
            results = data.get("results", [])
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "openFDA"}
        return {"status": "ok", "results": results, "source": "openFDA"}

    def search_labels(self, drug_name, limit=10):
        try:
            encoded = urllib.parse.quote(drug_name)
            data = self.client.fetch_json(
                f"/drug/label.json?search=openfda.brand_name:{encoded}&limit={limit}"
            )
            return {"status": "ok", "results": data.get("results", []), "source": "openFDA"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "openFDA"}

    def search_recalls(self, drug_name, limit=10):
        try:
            encoded = urllib.parse.quote(drug_name)
            data = self.client.fetch_json(
                f"/drug/enforcement.json?search=product_description:{encoded}&limit={limit}"
            )
            return {"status": "ok", "results": data.get("results", []), "source": "openFDA"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "openFDA"}

    @property
    def available(self):
        return True


if __name__ == "__main__":
    c = OpenFDAClient()
    print(f"openFDA available: {c.available}")
    print(c.search("aspirin", limit=2))
