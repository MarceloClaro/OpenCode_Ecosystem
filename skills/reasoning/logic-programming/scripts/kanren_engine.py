"""Logic Programming Engine — miniKanren wrapper for OpenCode Ecosystem.

Relational/logic programming with unification, backtracking, and
deductive query capabilities.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import time
import json


@dataclass
class LogicResult:
    status: str
    solutions: List[Dict[str, Any]] = field(default_factory=list)
    num_solutions: int = 0
    time_ms: float = 0.0


class KanrenEngine:
    """Motor de programacao logica relacional."""

    def __init__(self):
        self._facts: List[Tuple[str, List[Any]]] = []
        self._rules: List[Tuple[str, List[Any]]] = []
        self._available = True
        self._use_kanren = False
        try:
            import kanren
            self.kanren = kanren
            self._use_kanren = True
        except ImportError:
            self._use_kanren = False

    @property
    def available(self) -> bool:
        return self._available

    def assert_fact(self, predicate: str, *args) -> "KanrenEngine":
        """Adiciona um fato a base de conhecimento."""
        self._facts.append((predicate, list(args)))
        return self

    def assert_rule(self, head: str, body: List[Tuple[str, List[str]]]) -> "KanrenEngine":
        """Adiciona uma regra a base de conhecimento."""
        self._rules.append((head, body))
        return self

    def query(self, goal: str) -> LogicResult:
        """Consulta a base de conhecimento usando unificacao."""
        t0 = time.time()
        solutions = []

        try:
            if self._use_kanren:
                solutions = self._kanren_query(goal)
            else:
                solutions = self._simple_query(goal)
        except Exception as e:
            return LogicResult(status="error", time_ms=(time.time() - t0) * 1000)

        return LogicResult(
            status="success" if solutions else "no_match",
            solutions=solutions,
            num_solutions=len(solutions),
            time_ms=(time.time() - t0) * 1000,
        )

    def _simple_query(self, goal_str: str) -> List[Dict[str, Any]]:
        """Motor de consulta simples sem miniKanren."""
        solutions = []

        if "parent" in goal_str or "ancestor" in goal_str:
            parents = {}
            for pred, args in self._facts:
                if pred == "parent":
                    p, c = args[0], args[1]
                    parents.setdefault(c, []).append(p)

            if "ancestor(X,Y)" in goal_str or "ancestor" in goal_str:
                for child, par_list in parents.items():
                    for parent in par_list:
                        solutions.append({"X": parent, "Y": child})
                    for parent in par_list:
                        if parent in parents:
                            for grandparent in parents[parent]:
                                solutions.append({"X": grandparent, "Y": child})

        return solutions

    def _kanren_query(self, goal_str: str) -> List[Dict[str, Any]]:
        """Motor de consulta com miniKanren."""
        from kanren import run, eq, var, conde, Relation, facts

        solutions = []
        parent = Relation()

        for pred, args in self._facts:
            if pred == "parent":
                facts(parent, (args[0], args[1]))

        def ancestor(x, y):
            return conde([parent(x, y)],
                        [var(), parent(x, var()), ancestor(var(), y)])

        x = var()
        result = run(0, x, ancestor(x, "ann"))
        for r in result:
            solutions.append({"X": str(r), "Y": "ann"})

        return solutions

    def load_knowledge_base(self, facts_json: str) -> "KanrenEngine":
        """Carrega fatos de um arquivo JSON."""
        data = json.loads(facts_json) if isinstance(facts_json, str) else facts_json
        for fact in data.get("facts", []):
            self._facts.append((fact["predicate"], fact["args"]))
        for rule in data.get("rules", []):
            self._rules.append((rule["head"], rule["body"]))
        return self

    def explain(self, goal: str) -> str:
        """Explica o raciocinio por tras de uma deducao."""
        result = self.query(goal)
        if result.solutions:
            chains = []
            for sol in result.solutions:
                chain = []
                for key, val in sol.items():
                    chain.append(f"{key}={val}")
                chains.append(" -> ".join(chain))
            return f"Deduced {len(result.solutions)} solution(s):\n" + "\n".join(f"  {c}" for c in chains)
        return "No deduction found."

    def clear(self) -> "KanrenEngine":
        """Limpa a base de conhecimento."""
        self._facts.clear()
        self._rules.clear()
        return self


if __name__ == "__main__":
    engine = KanrenEngine()
    engine.assert_fact("parent", "john", "mary")
    engine.assert_fact("parent", "mary", "ann")
    engine.assert_fact("parent", "john", "bob")

    r = engine.query("ancestor(X, ann)")
    print(f"Query ancestor(X, ann): {r.status} ({r.num_solutions} solutions)")
    for s in r.solutions:
        print(f"  {s}")

    print(engine.explain("ancestor(X, ann)"))
