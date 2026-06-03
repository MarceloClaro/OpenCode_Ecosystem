import pytest, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from sympy_engine import SymPyEngine


class TestSymPyEngine:
    def setup_method(self):
        self.engine = SymPyEngine()

    def test_available(self):
        assert isinstance(self.engine.available, bool)

    def test_solve_quadratic(self):
        result = self.engine.solve("x**2 - 4 == 0")
        assert -2 in result.solutions
        assert 2 in result.solutions

    def test_simplify(self):
        result = self.engine.simplify("(x+1)*(x-1)")
        assert "x**2 - 1" in result.expression or "x**2-1" in result.expression

    def test_differentiate(self):
        result = self.engine.differentiate("x**3", "x")
        assert "3*x**2" in result.expression

    def test_prove_identity_valid(self):
        result = self.engine.prove_identity("sin(x)**2 + cos(x)**2 = 1")
        assert result.status == "valid"

    def test_integrate(self):
        result = self.engine.integrate("x", "x")
        assert "x**2" in result.expression

    def test_prove_identity_invalid(self):
        result = self.engine.prove_identity("sin(x)**2 + cos(x)**2 = 2")
        assert result.status == "invalid"
