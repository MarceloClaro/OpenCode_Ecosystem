import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from analyze_plddt import _analyze_entry
from analyze_pae import find_sub_domains, merge_global_domains


class TestAnalyzePlddt:
    def setup_method(self):
        self.sample_entry = {
            "uniprotAccession": "P04637",
            "globalMetricValue": 0.85,
            "fractionPlddtVeryLow": 0.02,
            "fractionPlddtLow": 0.08,
            "fractionPlddtConfident": 0.40,
            "fractionPlddtVeryHigh": 0.50,
        }

    def test_analyze_entry_returns_dict(self):
        result = _analyze_entry(self.sample_entry)
        assert isinstance(result, dict)
        assert result["uniprot_id"] == "P04637"
        assert result["global_plddt"] == 0.85

    def test_analyze_entry_has_fractions(self):
        result = _analyze_entry(self.sample_entry)
        assert "fractions" in result
        frac = result["fractions"]
        assert frac["very_low"] == 0.02
        assert frac["confident"] == 0.40
        assert frac["very_high"] == 0.50

    def test_analyze_entry_has_conclusion(self):
        result = _analyze_entry(self.sample_entry)
        assert "conclusion" in result
        assert isinstance(result["conclusion"], str)
        assert len(result["conclusion"]) > 0


class TestAnalyzePae:
    def setup_method(self):
        self.small_matrix = [
            [0.0, 2.0, 3.0, 25.0],
            [2.0, 0.0, 2.0, 25.0],
            [3.0, 2.0, 0.0, 25.0],
            [25.0, 25.0, 25.0, 0.0],
        ]

    def test_find_sub_domains_returns_list(self):
        domains = find_sub_domains(self.small_matrix)
        assert isinstance(domains, list)

    def test_merge_global_domains_returns_list(self):
        sub = find_sub_domains(self.small_matrix)
        merged = merge_global_domains(sub, self.small_matrix)
        assert isinstance(merged, list)
