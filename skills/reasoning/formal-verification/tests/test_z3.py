import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from z3_engine import Z3Engine


class TestZ3Engine:
    def setup_method(self):
        self.engine = Z3Engine()

    def test_available(self):
        assert isinstance(self.engine.available, bool)

    def test_prove_valid(self):
        result = self.engine.prove("x > 0 and y > 0", "x + y > 0")
        assert result.status == "valid"

    def test_prove_invalid(self):
        result = self.engine.prove("x > 0", "x < 0")
        assert result.status == "invalid"

    def test_check_sat_solution(self):
        result = self.engine.check_sat(["x + y == 10", "x - y == 2"])
        assert result.status == "sat"

    def test_check_sat_unsat(self):
        result = self.engine.check_sat(["x > 0", "x < 0"])
        assert result.status == "unsat"
