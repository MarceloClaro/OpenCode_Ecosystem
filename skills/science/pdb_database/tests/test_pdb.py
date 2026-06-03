import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from pdb_client import PDBClient


class TestPDB:
    def setup_method(self):
        self.client = PDBClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_search_returns_dict(self):
        result = self.client.search("test", limit=5)
        assert isinstance(result, dict)

    def test_empty_query_handled(self):
        result = self.client.search("", limit=5)
        assert isinstance(result, dict)

    def test_get_structure_returns_dict(self):
        result = self.client.get_structure("4HHB")
        assert isinstance(result, dict)

    def test_search_by_molecule_returns_dict(self):
        result = self.client.search_by_molecule("hemoglobin", limit=5)
        assert isinstance(result, dict)
