"""PubChem database client for OpenCode Ecosystem."""
import sys
import os
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'science_skills_common'))
from http_client import HttpClient


class PubChemClient:
    """Search compounds, substances, and bioactivities by name or CID."""

    def __init__(self):
        self.client = HttpClient(base_url="https://pubchem.ncbi.nlm.nih.gov/rest/pug", qps=5.0)

    def search(self, query, limit=10):
        results = []
        try:
            encoded = urllib.parse.quote(query)
            data = self.client.fetch_json(
                f"/compound/name/{encoded}/property/MolecularFormula,MolecularWeight,CanonicalSMILES/JSON?MaxRecords={limit}"
            )
            props = data.get("PropertyTable", {}).get("Properties", [])
            results = [{"cid": p["CID"], "formula": p.get("MolecularFormula"),
                        "weight": p.get("MolecularWeight"), "smiles": p.get("CanonicalSMILES")}
                       for p in props]
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "PubChem"}
        return {"status": "ok", "results": results, "source": "PubChem"}

    def search_by_cid(self, cid):
        try:
            data = self.client.fetch_json(
                f"/compound/cid/{cid}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IUPACName/JSON"
            )
            props = data.get("PropertyTable", {}).get("Properties", [])
            return {"status": "ok", "results": props, "source": "PubChem"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "PubChem"}

    def search_bioactivities(self, query, limit=10):
        try:
            encoded = urllib.parse.quote(query)
            data = self.client.fetch_json(
                f"/assay/name/{encoded}/JSON?MaxRecords={limit}"
            )
            return {"status": "ok", "results": data, "source": "PubChem"}
        except Exception as e:
            return {"status": "error", "message": str(e), "source": "PubChem"}

    @property
    def available(self):
        return True


if __name__ == "__main__":
    c = PubChemClient()
    print(f"PubChem available: {c.available}")
    print(c.search("aspirin", limit=2))
