# -*- coding: utf-8 -*-
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from evolution_loop import EvolutionLoopRunner, EvolutionCycle, FeedbackLoopEngine
from pdf_ecosystem_integration import PDFPipelineManager, PDFKnowledgeExtractor

class TestEvolutionLoop(unittest.TestCase):
    def test_cycle_creation(self):
        cycle = EvolutionCycle(
            cycle_id="TEST-001",
            timestamp="2026-05-07T12:00:00",
            phase="detect",
            health_before=0.85,
            health_after=0.85
        )
        self.assertEqual(cycle.cycle_id, "TEST-001")

    def test_full_cycle_execution(self):
        runner = EvolutionLoopRunner()
        result = runner.run_cycle()
        self.assertIsNotNone(result.cycle_id)
        self.assertGreater(result.duration_ms, 0)

class TestPDFPipeline(unittest.TestCase):
    def test_pipeline_manager_init(self):
        mgr = PDFPipelineManager()
        self.assertEqual(len(mgr.watch_dirs), 3)

    def test_pdf_scan(self):
        mgr = PDFPipelineManager()
        results = mgr.scan_for_pdfs()
        self.assertIsInstance(results, list)

if __name__ == "__main__":
    unittest.main()
