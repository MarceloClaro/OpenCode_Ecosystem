import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "skills" / "system" / "pypi-scout"))
from scihub_bridge import SciHubBridge, PaperMetadata

class TestSciHubBridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.bridge = SciHubBridge()
    def test_bridge_initialized(self): self.assertIsNotNone(self.bridge)
    def test_sources_discovered(self): self.assertGreaterEqual(len(self.bridge.available_sources), 1)
    def test_download_dir_exists(self): self.assertTrue(self.bridge.download_dir.exists())
    def test_get_status(self): self.assertIn("total_sources", self.bridge.get_status())
    def test_paper_metadata_dataclass(self):
        p = PaperMetadata(doi="10.1234/t", title="T", authors=["A"], year=2024, source="t")
        self.assertEqual(p.doi, "10.1234/t")
    def test_verify_doi_format(self):
        r = self.bridge.verify_doi("10.1234/fake")
        self.assertIn("valid", r); self.assertIn("sources_checked", r)
    def test_verify_references_batch(self): self.assertEqual(len(self.bridge.verify_references(["10.1/t1","10.1/t2"])), 2)
    def test_hash_file_empty(self): self.assertEqual(self.bridge._hash_file(Path("nonexistent.pdf")), "")
    def test_no_duplicate_sources(self): self.assertEqual(len(self.bridge.available_sources), len(set(self.bridge.available_sources)))
    def test_scihub_domains_https(self):
        for d in self.bridge.SCIHUB_DOMAINS: self.assertTrue(d.startswith("https://"))
