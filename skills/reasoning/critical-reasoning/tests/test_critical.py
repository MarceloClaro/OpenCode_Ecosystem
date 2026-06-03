import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from critical_engine import CriticalEngine, ArgumentAnalysis


class TestCriticalEngine:
    def setup_method(self):
        self.engine = CriticalEngine()

    def test_available(self):
        assert self.engine.available is True

    def test_analyze_returns_analysis(self):
        result = self.engine.analyze("test")
        assert isinstance(result, ArgumentAnalysis)

    def test_detect_fallacy(self):
        result = self.engine.analyze("everyone always knows the answer")
        fallacy_ids = [f["id"] for f in result.fallacies]
        assert "hasty_generalization" in fallacy_ids

    def test_strength_range(self):
        result = self.engine.analyze("simple statement")
        assert 0 <= result.score <= 100

    def test_no_fallacies_clean_text(self):
        result = self.engine.analyze("The sky is blue")
        assert len(result.fallacies) == 0

    def test_compare_arguments(self):
        result = self.engine.compare_arguments(
            "This is a strong argument with clear evidence and sound logic",
            "Everyone always knows this is obviously wrong"
        )
        assert "winner" in result
        assert result["winner"] in ("arg1", "arg2", "tie")
