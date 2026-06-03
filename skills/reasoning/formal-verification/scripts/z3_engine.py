"""Z3 Formal Verification Engine for OpenCode Ecosystem.

SMT solver wrapper: theorem proving, constraint solving, optimization.
Uses Microsoft Z3 Theorem Prover 4.16.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import time
import re


@dataclass
class ProofResult:
    status: str
    proof: str = ""
    counterexample: Optional[Dict[str, Any]] = None
    time_ms: float = 0.0


class Z3Engine:
    """Motor Z3 simplificado para verificacao formal."""

    def __init__(self):
        self._available = False
        try:
            from z3 import Solver, Real, Int, Bool, sat, unsat
            self.Solver = Solver
            self.Real = Real
            self.Int = Int
            self.Bool = Bool
            self.SAT = sat
            self.UNSAT = unsat
            self._available = True
        except ImportError:
            pass

    @property
    def available(self) -> bool:
        return self._available

    def check_sat(self, constraints: List[str]) -> ProofResult:
        """Verifica satisfabilidade de restricoes."""
        if not self._available:
            return ProofResult(status="unavailable")

        t0 = time.time()
        try:
            s = self.Solver()
            x = self.Real('x')
            y = self.Real('y')

            for c in constraints:
                expr = self._parse(c, {"x": x, "y": y})
                if expr is not None:
                    s.add(expr)

            r = s.check()
            ms = (time.time() - t0) * 1000

            if r == self.SAT:
                m = s.model()
                return ProofResult(
                    status="sat",
                    proof="Satisfativel",
                    counterexample={str(d): str(m.evaluate(d)) for d in m.decls() if str(d) != 'Bool'},
                    time_ms=ms,
                )
            return ProofResult(status=str(r), proof="", time_ms=ms)
        except Exception as e:
            return ProofResult(status="error", proof=str(e), time_ms=(time.time()-t0)*1000)

    def prove(self, premise: str, conclusion: str) -> ProofResult:
        """Prova teorema: premise => conclusion."""
        if not self._available:
            return ProofResult(status="unavailable")

        t0 = time.time()
        try:
            from z3 import Implies, Not

            s = self.Solver()
            x = self.Real('x')
            y = self.Real('y')

            p = self._parse(premise, {"x": x, "y": y})
            c = self._parse(conclusion, {"x": x, "y": y})

            if p is None or c is None:
                return ProofResult(status="parse_error", time_ms=(time.time()-t0)*1000)

            s.add(Not(Implies(p, c)))
            r = s.check()
            ms = (time.time() - t0) * 1000

            if r == self.UNSAT:
                return ProofResult(status="valid", proof="Teorema provado", time_ms=ms)
            elif r == self.SAT:
                m = s.model()
                return ProofResult(
                    status="invalid",
                    proof="Contraexemplo encontrado",
                    counterexample={str(d): str(m.evaluate(d)) for d in m.decls() if str(d) != 'Bool'},
                    time_ms=ms,
                )
            return ProofResult(status=str(r), time_ms=ms)
        except Exception as e:
            return ProofResult(status="error", proof=str(e), time_ms=(time.time()-t0)*1000)

    def _parse(self, expr: str, env: dict):
        """Parser robusto de expressoes para Z3."""
        from z3 import And, Or, Not

        expr = expr.strip()

        if " and " in expr:
            parts = expr.split(" and ")
            atoms = [self._parse(p.strip(), env) for p in parts]
            result = atoms[0]
            for a in atoms[1:]:
                result = And(result, a)
            return result

        if " or " in expr:
            parts = expr.split(" or ")
            atoms = [self._parse(p.strip(), env) for p in parts]
            result = atoms[0]
            for a in atoms[1:]:
                result = Or(result, a)
            return result

        if "not " in expr:
            return Not(self._parse(expr[4:].strip(), env))

        ops = [(">=", lambda a, b: a >= b), ("<=", lambda a, b: a <= b),
               (">", lambda a, b: a > b), ("<", lambda a, b: a < b),
               ("==", lambda a, b: a == b), ("!=", lambda a, b: a != b)]

        for op, func in ops:
            if op in expr and expr.count(op) == 1:
                parts = expr.split(op, 1)
                if len(parts) == 2:
                    left = self._eval_arith(parts[0].strip(), env)
                    right = self._eval_arith(parts[1].strip(), env)
                    if left is not None and right is not None:
                        return func(left, right)

        return None

    def _eval_arith(self, val: str, env: dict):
        """Avalia expressao aritmetica."""
        val = val.strip()

        if val in env:
            return env[val]

        try:
            return float(val)
        except ValueError:
            pass

        if "+" in val:
            parts = val.split("+")
            result = None
            for p in parts:
                v = self._eval_arith(p.strip(), env)
                if v is not None:
                    result = v if result is None else result + v
            return result

        if "-" in val and val[0] != "-":
            parts = val.split("-")
            vals = [self._eval_arith(p.strip(), env) for p in parts]
            if all(v is not None for v in vals):
                r = vals[0]
                for v in vals[1:]:
                    r = r - v
                return r

        if "*" in val:
            parts = val.split("*")
            vals = [self._eval_arith(p.strip(), env) for p in parts]
            if all(v is not None for v in vals):
                r = vals[0]
                for v in vals[1:]:
                    r = r * v
                return r

        return None


if __name__ == "__main__":
    engine = Z3Engine()
    print("Z3 Engine:", "OK" if engine.available else "Not Installed")

    # Prova: se x>0 e y>0 entao x+y>0
    r = engine.prove("x > 0 and y > 0", "x + y > 0")
    print(f"Prove (x>0 ^ y>0 => x+y>0): {r.status} ({r.time_ms:.1f}ms)")

    # Resolve sistema
    r2 = engine.check_sat(["x + y == 10", "x - y == 2"])
    print(f"Solve (x+y=10, x-y=2): {r2.status}")
    if r2.counterexample:
        print(f"  {r2.counterexample}")

    # Contradicao
    r3 = engine.check_sat(["x > 0", "x < 0"])
    print(f"Contradiction (x>0 ^ x<0): {r3.status}")
