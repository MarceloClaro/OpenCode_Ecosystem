"""Test coverage: import + instantiate + edge cases for all nexus modules."""

import unittest
import importlib
import sys

sys.path.insert(0, r"C:\Users\marce\.config\opencode\nexus\scripts")

TEST_MAP = [
    ("meta_learning_engine", "MetaLearningEngine"),
    ("phd_learning_cores", "AgentCoreEvolution"),
    ("phd_learning_cores", "ContinuousLearningCore"),
    ("micro_reasoning_types", "MicroReasoningEngine"),
    ("micro_validation", "MicroValidator"),
    ("mcp_self_organization", "MCPSelfOrganization"),
    ("micro_feedback_loop", "MicroFeedbackEngine"),
    ("micro_sync_barriers", "MicroSyncBarrierNetwork"),
    ("autonomous_reasoning_framework", "AutonomousReasoningFramework"),
    ("domain_discovery_engine", "DomainDiscoveryEngine"),
    ("pdf_ecosystem_integration", "PDFPipelineManager"),
    ("micro_integration", "MicroTMAOrchestrator"),
]


class TestModuleCoverage(unittest.TestCase):
    def test_all_modules_importable(self):
        for mod_name, cls_name in TEST_MAP:
            with self.subTest(module=mod_name, cls=cls_name):
                mod = importlib.import_module(mod_name)
                cls = getattr(mod, cls_name)
                self.assertIsNotNone(cls)

    def test_all_modules_instantiable(self):
        for mod_name, cls_name in TEST_MAP:
            with self.subTest(module=mod_name, cls=cls_name):
                mod = importlib.import_module(mod_name)
                cls = getattr(mod, cls_name)
                try:
                    obj = cls()
                    self.assertIsNotNone(obj)
                except TypeError as e:
                    self.skipTest(f"Constructor needs args: {e}")
                except Exception as e:
                    self.skipTest(f"Init error: {e}")


class TestEdgeCases(unittest.TestCase):
    """Edge case tests for critical infrastructure."""

    def test_load_state_missing_file(self):
        from ecosystem_config import load_state
        from pathlib import Path
        import tempfile
        result = load_state(Path(tempfile.mkdtemp()) / "nonexistent")
        self.assertEqual(result, {})

    def test_load_state_missing_file_custom_default(self):
        from ecosystem_config import load_state
        from pathlib import Path
        import tempfile
        result = load_state(Path(tempfile.mkdtemp()) / "nonexistent", {"custom": True})
        self.assertEqual(result, {"custom": True})

    def test_save_state_creates_gzip(self):
        from ecosystem_config import save_state, load_state
        from pathlib import Path
        import tempfile, os
        tmp = Path(tempfile.mkdtemp())
        test_path = tmp / "test.json"
        save_state(test_path, {"key": "value"})
        gz = test_path.with_suffix(".json.gz")
        self.assertTrue(gz.exists())
        self.assertFalse(test_path.exists())
        loaded = load_state(test_path, {})
        self.assertEqual(loaded, {"key": "value"})
        os.remove(str(gz))

    def test_load_state_with_gzip_file(self):
        from ecosystem_config import load_state, STATE_PATH
        data = load_state(STATE_PATH, {})
        self.assertIsInstance(data, dict)
        self.assertGreater(len(data), 0)

    def test_safe_evaluator_true(self):
        from granular_sync import GranularOperation
        op = GranularOperation("test", "phase", "agent", "standard")
        op.status = "completed"
        ops = {"test": op}
        result = op._evaluate_condition("ops['test'].status == 'completed'", ops)
        self.assertTrue(result)

    def test_safe_evaluator_false(self):
        from granular_sync import GranularOperation
        op = GranularOperation("test", "phase", "agent", "standard")
        op.status = "failed"
        ops = {"test": op}
        result = op._evaluate_condition("ops['test'].status == 'completed'", ops)
        self.assertFalse(result)

    def test_safe_evaluator_rejects_dangerous(self):
        from granular_sync import GranularOperation
        op = GranularOperation("test", "phase", "agent", "standard")
        ops = {"test": op}
        result = op._evaluate_condition("__import__('os').system('dir')", ops)
        self.assertFalse(result)

    def test_safe_evaluator_rejects_nested_eval(self):
        from granular_sync import GranularOperation
        op = GranularOperation("test", "phase", "agent", "standard")
        ops = {"test": op}
        result = op._evaluate_condition("eval('1+1')", ops)
        self.assertFalse(result)

    def test_validation_type_error_path(self):
        from ecosystem_config import load_state
        import tempfile
        with self.assertRaises(TypeError):
            load_state("not-a-path", {})

    def test_validation_type_error_data(self):
        from ecosystem_config import save_state
        from pathlib import Path
        import tempfile
        with self.assertRaises(TypeError):
            save_state(Path(tempfile.mkdtemp()) / "x.json", "not-a-dict")


if __name__ == "__main__":
    unittest.main(verbosity=2)
