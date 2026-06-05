"""
TDD Suite — Motif Discovery Engine (MDE)
Testa grafo, mineracao de motivos, invariantes e classificacao.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest


class TestEcosystemGraph:
    def test_create_graph(self):
        from motif_discovery.engine import EcosystemGraph
        g = EcosystemGraph()
        assert len(g.nodes) == 0
        assert len(g.edges) == 0

    def test_add_nodes_and_edges(self):
        from motif_discovery.engine import EcosystemGraph
        g = EcosystemGraph()
        g.add_node("s1", "skill", "code-review")
        g.add_node("a1", "agent", "reviewer")
        g.add_edge("a1", "s1", "uses")
        assert len(g.nodes) == 2
        assert len(g.edges) == 1

    def test_node_type_distribution(self):
        from motif_discovery.engine import EcosystemGraph
        g = EcosystemGraph()
        for i in range(5):
            g.add_node(f"s{i}", "skill", f"skill-{i}")
        for i in range(3):
            g.add_node(f"a{i}", "agent", f"agent-{i}")
        dist = g.node_type_distribution()
        assert dist["skill"] == 5
        assert dist["agent"] == 3

    def test_edge_type_distribution(self):
        from motif_discovery.engine import EcosystemGraph
        g = EcosystemGraph()
        g.add_node("a", "agent", "a"); g.add_node("s", "skill", "s"); g.add_node("m", "mcp", "m")
        g.add_edge("a", "s", "uses")
        g.add_edge("s", "m", "calls")
        dist = g.edge_type_distribution()
        assert dist["uses"] == 1
        assert dist["calls"] == 1

    def test_export_graphml(self):
        from motif_discovery.engine import EcosystemGraph
        g = EcosystemGraph()
        g.add_node("s1", "skill", "test-skill")
        g.add_node("a1", "agent", "test-agent")
        g.add_edge("a1", "s1", "uses")
        graphml = g.export_graphml()
        assert "test-skill" in graphml
        assert "test-agent" in graphml
        assert "<graphml" in graphml

    def test_from_ecosystem_scan(self):
        from motif_discovery.engine import EcosystemGraph
        with tempfile.TemporaryDirectory() as tmp:
            for d in ["skills", "agents", "core", "nexus"]:
                (Path(tmp) / d).mkdir()
            (Path(tmp) / "skills" / "test-skill").mkdir()
            (Path(tmp) / "skills" / "test-skill" / "SKILL.md").write_text("# Test Skill", encoding="utf-8")
            (Path(tmp) / "agents" / "test-agent.md").write_text("skills: [test-skill]", encoding="utf-8")
            g = EcosystemGraph.from_ecosystem_scan(tmp)
            assert g.node_type_distribution().get("skill", 0) >= 1
            assert g.node_type_distribution().get("agent", 0) >= 1
            assert g.node_type_distribution().get("layer", 0) >= 2


class TestMotifMiner:
    def test_mine_known_motifs(self):
        from motif_discovery.engine import EcosystemGraph, MotifMiner
        g = EcosystemGraph()
        g.add_node("a", "agent", "a"); g.add_node("s", "skill", "s"); g.add_node("m", "mcp", "m")
        g.add_edge("a", "s", "uses")
        g.add_edge("s", "m", "calls")
        miner = MotifMiner(g)
        motifs = miner.mine()
        assert len(motifs) >= 1
        has_pipeline = any(m.motif_id == "MOTIF-001" for m in motifs)
        assert has_pipeline

    def test_discover_novel_motifs(self):
        from motif_discovery.engine import EcosystemGraph, MotifMiner
        g = EcosystemGraph()
        for i in range(5):
            g.add_node(f"a{i}", "agent", f"agent-{i}")
            g.add_node(f"s{i}", "skill", f"skill-{i}")
            g.add_edge(f"a{i}", f"s{i}", "uses")
        miner = MotifMiner(g)
        miner.mine()
        novel = miner.discover_novel_motifs(min_frequency=3)
        assert len(novel) >= 1

    def test_motif_confidence(self):
        from motif_discovery.engine import EcosystemGraph, MotifMiner
        g = EcosystemGraph()
        g.add_node("a", "agent", "a"); g.add_node("s", "skill", "s"); g.add_node("m", "mcp", "m")
        g.add_edge("a", "s", "uses")
        g.add_edge("s", "m", "calls")
        miner = MotifMiner(g)
        motifs = miner.mine()
        pipeline = [m for m in motifs if m.motif_id == "MOTIF-001"]
        if pipeline:
            assert 0 <= pipeline[0].confidence <= 1.0


class TestInvariantExtractor:
    def test_extract_invariants(self):
        from motif_discovery.engine import EcosystemGraph, MotifMiner, InvariantExtractor
        g = EcosystemGraph()
        g.add_node("a", "agent", "a"); g.add_node("s", "skill", "s"); g.add_node("m", "mcp", "m")
        g.add_edge("a", "s", "uses"); g.add_edge("s", "m", "calls")
        miner = MotifMiner(g)
        miner.mine()
        extractor = InvariantExtractor(miner)
        history = [
            {"cycle": 17, "motifs_found": ["MOTIF-001", "MOTIF-003"]},
            {"cycle": 18, "motifs_found": ["MOTIF-001", "MOTIF-003", "MOTIF-007"]},
        ]
        invariants = extractor.extract_invariants(history)
        assert len(invariants) >= 1

    def test_detect_breaking_invariants(self):
        from motif_discovery.engine import EcosystemGraph, MotifMiner, InvariantExtractor
        g = EcosystemGraph()
        miner = MotifMiner(g)
        extractor = InvariantExtractor(miner)
        breaking = extractor.detect_breaking_invariants(
            ["MOTIF-001"],
            {"motifs_found": []}
        )
        assert len(breaking) == 0  # MOTIF-001 nao existia antes


class TestPatternClassifier:
    def test_classify_motifs(self):
        from motif_discovery.engine import PatternClassifier, StructuralMotif
        classifier = PatternClassifier()
        motifs = [
            StructuralMotif("M-1", "Fundacional", "", [], frequency=10, is_invariant=True, cycles_survived=18),
            StructuralMotif("M-2", "Otimizavel", "", [], frequency=8, is_invariant=False, cycles_survived=4),
            StructuralMotif("M-3", "Emergente", "", [], frequency=3, is_invariant=False, cycles_survived=1),
            StructuralMotif("M-4", "Anomalo", "", [], frequency=1, is_invariant=False, cycles_survived=0),
        ]
        classified = classifier.classify(motifs)
        assert len(classified["foundational"]) == 1
        assert len(classified["optimization"]) == 1
        assert len(classified["emergent"]) == 1
        assert len(classified["anomaly"]) == 1

    def test_generate_recommendations(self):
        from motif_discovery.engine import PatternClassifier, StructuralMotif
        classifier = PatternClassifier()
        motifs = [
            StructuralMotif("M-1", "F", "", [], frequency=10, is_invariant=True, cycles_survived=18),
            StructuralMotif("M-2", "O", "", [], frequency=8, is_invariant=False, cycles_survived=4),
        ]
        classified = classifier.classify(motifs)
        recs = classifier.generate_recommendations(classified)
        assert len(recs) >= 2


class TestMotifDiscoveryEngine:
    def test_full_pipeline(self):
        from motif_discovery.engine import MotifDiscoveryEngine
        with tempfile.TemporaryDirectory() as tmp:
            for d in ["skills", "agents", "core", "nexus", "swe-eval-v1"]:
                (Path(tmp) / d).mkdir()
            (Path(tmp) / "skills" / "test-skill").mkdir()
            (Path(tmp) / "skills" / "test-skill" / "SKILL.md").write_text("# Test", encoding="utf-8")
            (Path(tmp) / "agents" / "agent.md").write_text("skills: [test-skill]", encoding="utf-8")

            engine = MotifDiscoveryEngine(tmp)
            report = engine.run()
            assert report.total_nodes >= 2
            assert report.motifs_found >= 1
            assert len(report.recommendations) >= 1
            assert len(report.evolution_directions) >= 1

    def test_report_generation(self):
        from motif_discovery.engine import MotifDiscoveryEngine, generate_motif_report_markdown
        with tempfile.TemporaryDirectory() as tmp:
            for d in ["skills", "agents"]:
                (Path(tmp) / d).mkdir()
            engine = MotifDiscoveryEngine(tmp)
            report = engine.run()
            md = generate_motif_report_markdown(report)
            assert "Motif Discovery Report" in md
            assert str(report.motifs_found) in md


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
