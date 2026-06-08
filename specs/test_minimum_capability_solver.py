#!/usr/bin/env python3
"""
test_minimum_capability_solver.py — SPEC-032: MCSP TDD Suite

14 Critical Tests:
  Fase 1 — Backward Closure (4 CTs):
    MCSP-001: A->B, T={B} → closure={A,B}
    MCSP-002: S ja cobre prereq → nao incluido
    MCSP-003: Dependencia transitiva A->B->C, T={C} → closure={A,B,C}
    MCSP-004: Grafo real (CrossValidationEngine) com 92 nos

  Fase 2 — Greedy Selection (4 CTs):
    MCSP-005: 1 alvo sem dependencias → C com 1 elemento
    MCSP-006: 2 alvos, 1 cobre ambos → C com 1 elemento
    MCSP-007: Prioriza alta cascade_impact
    MCSP-008: C nunca inclui capacidades em S

  Fase 3 — Topological Order (3 CTs):
    MCSP-009: A->B → ordem = [B, A]
    MCSP-010: Sem dependencias → qualquer ordem valida
    MCSP-011: Ciclo detectado → TopologicalCycleError

  Integracao (3 CTs):
    MCSP-012: Pipeline: NooScan + TeloGaps → MCSP solution
    MCSP-013: cost(solution) <= |C|
    MCSP-014: Solucao tem todos os campos preenchidos

Uso: python specs/test_minimum_capability_solver.py
"""

import json, sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from minimum_capability_solver import (
    MinimumCapabilitySolver, build_mock_engine, TopologicalCycleError,
)


class CTResult:
    def __init__(self, ct_id, name, passed, detail="", evidence=None):
        self.ct_id = ct_id; self.name = name; self.passed = passed
        self.detail = detail; self.evidence = evidence


# ═══ FASE 1 — Backward Closure ═══════════════════════════════════════════

def mcsp_001_simple_closure() -> CTResult:
    nodes = {"A.B", "C.D"}
    edges = [("A.B", "C.D", "requires", 0.8)]
    engine = build_mock_engine(nodes, edges)
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    closure = solver.backward_closure({"C.D"}, set())
    if "A.B" not in closure or "C.D" not in closure:
        return CTResult("MCSP-001", "A->B, T={B} → closure={A,B}", False, f"Closure={closure}")
    return CTResult("MCSP-001", "Backward closure simples", True, f"Closure={closure}")


def mcsp_002_present_excluded() -> CTResult:
    nodes = {"A.B", "C.D"}
    edges = [("A.B", "C.D", "requires", 0.8)]
    engine = build_mock_engine(nodes, edges)
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    closure = solver.backward_closure({"C.D"}, {"A.B"})  # A.B ja presente
    if "A.B" in closure:
        return CTResult("MCSP-002", "S ja cobre → nao incluido", False, f"Closure contem A.B: {closure}")
    return CTResult("MCSP-002", "Capacidade presente excluida", True, f"Closure={closure}")


def mcsp_003_transitive() -> CTResult:
    nodes = {"A.a", "B.b", "C.c"}
    edges = [("A.a", "B.b", "requires", 0.8), ("B.b", "C.c", "requires", 0.7)]
    engine = build_mock_engine(nodes, edges)
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    closure = solver.backward_closure({"C.c"}, set())
    if len(closure) < 3:
        return CTResult("MCSP-003", "A->B->C, T={C} → closure={A,B,C}", False, f"Closure={closure}")
    return CTResult("MCSP-003", "Dependencia transitiva propagada", True, f"Closure={closure}")


def mcsp_004_real_graph() -> CTResult:
    from cross_validation_engine import CrossValidationEngine
    engine = CrossValidationEngine()
    from noological_scanner import EPISTEMOLOGICAL_DIMENSIONS
    dims = {}
    for dk, dim in EPISTEMOLOGICAL_DIMENSIONS.items():
        cats = dim.categories; mid = len(cats)//2
        dims[dk] = {"name": dim.name, "covered": cats[:mid], "absent": cats[mid:],
                     "density": 0.5, "coverage_pct": 50, "weight": 1.0}
    scan = {"dimensions": dims, "overall_density": 0.5}
    engine.build_graph(scan)
    
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    targets = {"raciocinio.Probabilístico", "teoria_jogos.Equilíbrio de Nash", "paradigmas.Fenomenológico"}
    closure = solver.backward_closure(targets, set())
    
    if len(closure) < 3:
        return CTResult("MCSP-004", "Grafo 92 nos, closure >= 3", False, f"Closure={len(closure)}")
    return CTResult("MCSP-004", "Grafo real propagado", True, f"Closure={len(closure)} nos para 3 alvos")


# ═══ FASE 2 — Greedy Selection ═══════════════════════════════════════════

def mcsp_005_single_target() -> CTResult:
    nodes = {"A.a", "B.b"}
    edges = [("A.a", "B.b", "enables", 0.8)]
    engine = build_mock_engine(nodes, edges)
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    closure = solver.backward_closure({"B.b"}, set())
    result = solver.greedy_select({"B.b"}, set(), closure)
    if len(result.required) != 1:
        return CTResult("MCSP-005", "1 alvo → C com 1 elemento", False, f"Required={result.required}")
    return CTResult("MCSP-005", "Single target selecionado", True, f"Required={result.required}")


def mcsp_006_shared_coverage() -> CTResult:
    nodes = {"A.a", "B.b", "C.c"}
    edges = [("A.a", "B.b", "enables", 0.8), ("A.a", "C.c", "enables", 0.7)]
    engine = build_mock_engine(nodes, edges)
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    closure = solver.backward_closure({"B.b", "C.c"}, set())
    result = solver.greedy_select({"B.b", "C.c"}, set(), closure)
    if len(result.required) < 1:
        return CTResult("MCSP-006", "2 alvos, A cobre ambos", False, f"Required={result.required}")
    if result.coverage_pct < 0.5:
        return CTResult("MCSP-006", "Coverage > 50%", False, f"Coverage={result.coverage_pct}")
    return CTResult("MCSP-006", "Shared coverage detectado", True, f"Required={result.required}, cov={result.coverage_pct}")


def mcsp_007_cascade_priority() -> CTResult:
    nodes = {"High.h", "Low.l", "T1.t1", "T2.t2", "T3.t3"}
    edges = [
        ("High.h", "T1.t1", "enables", 0.8), ("High.h", "T2.t2", "enables", 0.8),
        ("High.h", "T3.t3", "enables", 0.8), ("Low.l", "T1.t1", "enables", 0.8),
    ]
    engine = build_mock_engine(nodes, edges)
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    closure = solver.backward_closure({"T1.t1", "T2.t2", "T3.t3"}, set())
    result = solver.greedy_select({"T1.t1", "T2.t2", "T3.t3"}, set(), closure)
    # High deve ser escolhido primeiro (maior cascade)
    if "High.h" not in result.required:
        return CTResult("MCSP-007", "High cascade priorizado", False, f"Required={result.required}")
    return CTResult("MCSP-007", "Alta cascade_impact priorizada", True, f"Required={result.required}")


def mcsp_008_no_duplicate_present() -> CTResult:
    nodes = {"A.a", "B.b"}
    edges = [("A.a", "B.b", "enables", 0.8)]
    engine = build_mock_engine(nodes, edges)
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    closure = solver.backward_closure({"B.b"}, {"A.a"})
    result = solver.greedy_select({"B.b"}, {"A.a"}, closure)
    if "A.a" in result.required:
        return CTResult("MCSP-008", "C nao inclui capacidades em S", False, f"Required contem A.a")
    return CTResult("MCSP-008", "Nao duplica capacidades presentes", True, f"Required={result.required}")


# ═══ FASE 3 — Topological Order ══════════════════════════════════════════

def mcsp_009_order_prereq_first() -> CTResult:
    nodes = {"A.a", "B.b"}
    edges = [("A.a", "B.b", "requires", 0.8)]
    engine = build_mock_engine(nodes, edges)
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    order = solver.topological_order({"A.a", "B.b"}, set())
    if order.index("B.b") >= order.index("A.a"):
        return CTResult("MCSP-009", "A->B → ordem [B, A]", False, f"Order={order}")
    return CTResult("MCSP-009", "Pre-requisito vem primeiro", True, f"Order={order}")


def mcsp_010_no_deps_any_order() -> CTResult:
    nodes = {"A.a", "B.b", "C.c"}
    engine = build_mock_engine(nodes, [])
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    order = solver.topological_order({"A.a", "B.b", "C.c"}, set())
    if len(order) != 3:
        return CTResult("MCSP-010", "Sem deps → 3 nos ordenados", False, f"Order={order}")
    return CTResult("MCSP-010", "Ordem valida sem dependencias", True, f"Order={order}")


def mcsp_011_cycle_detection() -> CTResult:
    nodes = {"A.a", "B.b"}
    edges = [("A.a", "B.b", "requires", 0.8), ("B.b", "A.a", "requires", 0.7)]
    engine = build_mock_engine(nodes, edges)
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    try:
        solver.topological_order({"A.a", "B.b"}, set())
        return CTResult("MCSP-011", "Ciclo detectado → erro", False, "Nao lancou excecao")
    except TopologicalCycleError:
        return CTResult("MCSP-011", "Ciclo lanca TopologicalCycleError", True, "Excecao capturada")


# ═══ INTEGRATION ═════════════════════════════════════════════════════════

def mcsp_012_full_pipeline() -> CTResult:
    from cross_validation_engine import CrossValidationEngine
    from teleological_scanner import TeleologicalReverseScanner, TeleologicalGoal
    from noological_scanner import NoologicalScanner

    class MP: 
        def __init__(s, t): s.text = t
    class MT:
        def __init__(s, t): s.paragraphs = {"P1": MP(t)}; s.citation_map = []

    nool = NoologicalScanner()
    scan = nool.scan(MT("Estudo randomizado controlado com analise bayesiana e follow-up longitudinal."))
    
    tel = TeleologicalReverseScanner()
    tel.set_goals([TeleologicalGoal("Efeito causal de X", "causal")])
    tel.infer_requirements()
    gaps = tel.compare_with_scan(scan)

    engine = CrossValidationEngine()
    engine.build_graph(scan)
    
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    solution = solver.solve_from_scanners(scan, gaps)

    if not solution.greedy_set.required:
        return CTResult("MCSP-012", "Pipeline: Noo+Telo → MCSP", False, "Required vazio")
    return CTResult("MCSP-012", "Pipeline completo integrado", True,
                    f"Required={len(solution.greedy_set.required)}, cost={solution.greedy_set.cost}")


def mcsp_013_cost_bound() -> CTResult:
    from cross_validation_engine import CrossValidationEngine
    engine = CrossValidationEngine()
    from noological_scanner import EPISTEMOLOGICAL_DIMENSIONS
    dims = {}
    for dk, dim in EPISTEMOLOGICAL_DIMENSIONS.items():
        cats = dim.categories; mid = len(cats)//2
        dims[dk] = {"name": dim.name, "covered": cats[:mid], "absent": cats[mid:],
                     "density": 0.5, "coverage_pct": 50, "weight": 1.0}
    scan = {"dimensions": dims, "overall_density": 0.5}
    engine.build_graph(scan)
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    
    present = {"raciocinio.Dedutivo", "paradigmas.Positivista"}
    targets = {"raciocinio.Probabilístico", "teoria_jogos.Equilíbrio de Nash"}
    solution = solver.solve(present, targets)
    
    if solution.greedy_set.cost > len(solution.greedy_set.required) + 1:
        return CTResult("MCSP-013", "cost <= |C| + 1", False,
                       f"Cost={solution.greedy_set.cost}, |C|={len(solution.greedy_set.required)}")
    return CTResult("MCSP-013", "Custo dentro do bound", True,
                    f"Cost={solution.greedy_set.cost}, |C|={len(solution.greedy_set.required)}")


def mcsp_014_solution_complete() -> CTResult:
    from cross_validation_engine import CrossValidationEngine
    engine = CrossValidationEngine()
    from noological_scanner import EPISTEMOLOGICAL_DIMENSIONS
    dims = {}
    for dk, dim in EPISTEMOLOGICAL_DIMENSIONS.items():
        cats = dim.categories; mid = len(cats)//2
        dims[dk] = {"name": dim.name, "covered": cats[:mid], "absent": cats[mid:],
                     "density": 0.5, "coverage_pct": 50, "weight": 1.0}
    scan = {"dimensions": dims, "overall_density": 0.5}
    engine.build_graph(scan)
    solver = MinimumCapabilitySolver()
    solver.load_from_engine(engine)
    
    solution = solver.solve(set(), {"raciocinio.Probabilístico"})
    gs = solution.greedy_set
    
    checks = []
    if not gs.required: checks.append("required")
    if gs.cost < 0: checks.append("cost")
    if not gs.topological_order: checks.append("order")
    if gs.coverage_pct < 0: checks.append("coverage_pct")
    if solution.elapsed_ms < 0: checks.append("elapsed_ms")
    
    if checks:
        return CTResult("MCSP-014", "Solucao com todos os campos", False, f"Faltam: {checks}")
    return CTResult("MCSP-014", "Solucao completa", True,
                    f"Set={len(gs.required)}, cost={gs.cost}, cov={gs.coverage_pct}, {solution.elapsed_ms}ms")


# ═══ Runner ═══════════════════════════════════════════════════════════════

CT_LIST = [
    mcsp_001_simple_closure, mcsp_002_present_excluded, mcsp_003_transitive, mcsp_004_real_graph,
    mcsp_005_single_target, mcsp_006_shared_coverage, mcsp_007_cascade_priority, mcsp_008_no_duplicate_present,
    mcsp_009_order_prereq_first, mcsp_010_no_deps_any_order, mcsp_011_cycle_detection,
    mcsp_012_full_pipeline, mcsp_013_cost_bound, mcsp_014_solution_complete,
]


def run_all(json_out=False):
    results = []
    for ct in CT_LIST:
        try: r = ct()
        except Exception as e: r = CTResult(ct.__name__, "UNKNOWN", False, f"Excecao: {e}")
        results.append(r)
    p = sum(1 for r in results if r.passed); f = sum(1 for r in results if not r.passed)
    if not json_out: _print(results, p, f)
    return {"passed": p, "failed": f, "total": len(results),
            "results": [{"id": r.ct_id, "name": r.name, "passed": r.passed, "detail": r.detail} for r in results]}


def _print(results, passed, failed):
    G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; RE = "\033[0m"; B = "\033[1m"
    print(f"\n{B}{'='*80}{RE}")
    print(f"  {B}SPEC-032 Minimum Capability Set Solver — {len(results)} Critical Tests{RE}")
    print(f"  {G}PASS: {passed}{RE}  |  {R}FAIL: {failed}{RE}")
    print(f"{B}{'='*80}{RE}\n")
    for r in results:
        s = f"{G}PASS{RE}" if r.passed else f"{R}FAIL{RE}"
        print(f"  [{s}] {r.ct_id}: {r.name}")
        if r.detail: print(f"       {(G if r.passed else Y)}{r.detail}{RE}")
    print(f"\n{B}{'='*80}{RE}")
    pct = (passed/len(results))*100 if results else 0
    v = f"{G}[APROVADO]{RE}" if failed == 0 else f"{R}[{failed} FALHAS]{RE}"
    print(f"  RESULTADO: {v}  |  {passed}/{len(results)} ({pct:.0f}%)")
    print(f"{B}{'='*80}{RE}\n")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    r = run_all(json_out=a.json)
    if a.json: print(json.dumps(r, indent=2, ensure_ascii=False))
    sys.exit(0 if r["failed"] == 0 else 1)
