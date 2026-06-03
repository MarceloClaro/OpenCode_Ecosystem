"""Symbolic Mathematics Engine — SymPy wrapper for OpenCode Ecosystem.

Provides symbolic computation: algebra, calculus, logic, matrices,
equation solving, and LaTeX integration.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
import time


@dataclass
class SymbolicResult:
    status: str
    expression: str = ""
    solutions: List[Any] = field(default_factory=list)
    latex: str = ""
    steps: List[str] = field(default_factory=list)
    time_ms: float = 0.0


class SymPyEngine:
    """Motor de computacao simbolica usando SymPy."""

    def __init__(self):
        try:
            import sympy as sp
            self.sp = sp
            self._available = True
        except ImportError:
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    def solve(self, equation: str) -> SymbolicResult:
        """Resolve equacao simbolica."""
        if not self._available:
            return SymbolicResult(status="error", expression="SymPy not installed")

        t0 = time.time()
        try:
            sp = self.sp
            x = sp.Symbol('x')
            eq_str = equation.replace("=", "-(") + ")" if "=" in equation else equation

            if "=" in equation:
                left, right = equation.split("=", 1)
                eq = sp.sympify(f"({left.strip()}) - ({right.strip()})")
                sols = sp.solve(eq, x)
            else:
                eq = sp.sympify(eq_str)
                sols = sp.solve(eq, x)

            return SymbolicResult(
                status="solved",
                expression=equation,
                solutions=sols,
                latex=sp.latex(sols),
                time_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return SymbolicResult(status="error", expression=str(e), time_ms=(time.time() - t0) * 1000)

    def simplify(self, expression: str) -> SymbolicResult:
        """Simplifica expressao simbolica."""
        if not self._available:
            return SymbolicResult(status="error")
        t0 = time.time()
        try:
            sp = self.sp
            expr = sp.sympify(expression)
            simplified = sp.simplify(expr)
            return SymbolicResult(
                status="simplified",
                expression=str(simplified),
                latex=sp.latex(simplified),
                time_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return SymbolicResult(status="error", expression=str(e))

    def differentiate(self, expression: str, variable: str = "x", order: int = 1) -> SymbolicResult:
        """Derivada simbolica."""
        if not self._available:
            return SymbolicResult(status="error")
        t0 = time.time()
        try:
            sp = self.sp
            var = sp.Symbol(variable)
            expr = sp.sympify(expression)
            deriv = sp.diff(expr, var, order)
            return SymbolicResult(
                status="derivative",
                expression=str(deriv),
                latex=sp.latex(deriv),
                time_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return SymbolicResult(status="error", expression=str(e))

    def integrate(self, expression: str, variable: str = "x", a=None, b=None) -> SymbolicResult:
        """Integral simbolica (definida ou indefinida)."""
        if not self._available:
            return SymbolicResult(status="error")
        t0 = time.time()
        try:
            sp = self.sp
            var = sp.Symbol(variable)
            expr = sp.sympify(expression)

            if a is not None and b is not None:
                integral = sp.integrate(expr, (var, a, b))
            else:
                integral = sp.integrate(expr, var)

            return SymbolicResult(
                status="integral",
                expression=str(integral),
                latex=sp.latex(integral),
                time_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return SymbolicResult(status="error", expression=str(e))

    def prove_identity(self, equation: str) -> SymbolicResult:
        """Verifica se uma identidade matematica e verdadeira."""
        if not self._available:
            return SymbolicResult(status="error")
        t0 = time.time()
        try:
            sp = self.sp

            if "=" in equation:
                left, right = equation.split("=", 1)
                diff = sp.sympify(f"({left.strip()}) - ({right.strip()})")
                simplified = sp.simplify(diff)
                valid = simplified == 0

                return SymbolicResult(
                    status="valid" if valid else "invalid",
                    expression=equation,
                    solutions=[str(simplified)],
                    time_ms=(time.time() - t0) * 1000,
                )
            return SymbolicResult(status="error", expression="Use = for identity")
        except Exception as e:
            return SymbolicResult(status="error", expression=str(e))

    def expand(self, expression: str) -> SymbolicResult:
        """Expande expressao algebrica."""
        if not self._available:
            return SymbolicResult(status="error")
        t0 = time.time()
        try:
            sp = self.sp
            result = sp.expand(sp.sympify(expression))
            return SymbolicResult(
                status="expanded",
                expression=str(result),
                latex=sp.latex(result),
                time_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return SymbolicResult(status="error", expression=str(e))

    def factor(self, expression: str) -> SymbolicResult:
        """Fatora expressao algebrica."""
        if not self._available:
            return SymbolicResult(status="error")
        t0 = time.time()
        try:
            sp = self.sp
            result = sp.factor(sp.sympify(expression))
            return SymbolicResult(
                status="factored",
                expression=str(result),
                latex=sp.latex(result),
                time_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return SymbolicResult(status="error", expression=str(e))

    def latex_to_sympy(self, latex_str: str) -> SymbolicResult:
        """Converte LaTeX para expressao SymPy."""
        if not self._available:
            return SymbolicResult(status="error")
        t0 = time.time()
        try:
            sp = self.sp
            expr = sp.sympify(latex_str)
            return SymbolicResult(
                status="parsed",
                expression=str(expr),
                latex=sp.latex(expr),
                time_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return SymbolicResult(status="error", expression=str(e))


if __name__ == "__main__":
    engine = SymPyEngine()
    print("SymPy Engine:", "Available" if engine.available else "Not Installed")

    r = engine.solve("x**2 + 2*x + 1 = 0")
    print(f"Solve x^2+2x+1=0: {r.status} -> {r.solutions} ({r.time_ms:.1f}ms)")

    r2 = engine.simplify("(x+1)*(x-1)")
    print(f"Simplify (x+1)(x-1): {r2.status} -> {r2.expression}")

    r3 = engine.differentiate("x**3 + 2*x**2 + x")
    print(f"Derivative x^3+2x^2+x: {r3.expression}")

    r4 = engine.prove_identity("sin(x)**2 + cos(x)**2 = 1")
    print(f"Prove sin^2+cos^2=1: {r4.status}")
