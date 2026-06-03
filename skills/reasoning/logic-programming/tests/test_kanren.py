import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from kanren_engine import KanrenEngine


class TestKanrenEngine:
    def setup_method(self):
        self.engine = KanrenEngine()

    def test_available(self):
        assert self.engine.available is True

    def test_assert_fact(self):
        self.engine.assert_fact("parent", "john", "mary")
        assert len(self.engine._facts) > 0
        assert self.engine._facts[0][0] == "parent"

    def test_query_ancestor(self):
        self.engine.assert_fact("parent", "john", "mary")
        self.engine.assert_fact("parent", "mary", "ann")
        result = self.engine.query("ancestor(X, ann)")
        assert result.num_solutions > 0
        assert len(result.solutions) > 0

    def test_explain(self):
        self.engine.assert_fact("parent", "john", "mary")
        self.engine.assert_fact("parent", "mary", "ann")
        explanation = self.engine.explain("ancestor(X, ann)")
        assert isinstance(explanation, str)
        assert "Deduced" in explanation or "deduction" in explanation.lower()

    def test_clear(self):
        self.engine.assert_fact("parent", "john", "mary")
        self.engine.clear()
        assert len(self.engine._facts) == 0
