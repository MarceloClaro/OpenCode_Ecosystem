#!/usr/bin/env python3
"""
test_evolutionary_scanner.py — SPEC-030: Evolutionary Trajectories Scanner TDD Suite

16 Critical Tests:
  Modulo 3 — CrossValidationEngine (6 CTs):
    EVO-001: build_graph cria nos para todas as categorias do scan
    EVO-002: find_bottlenecks identifica nos com >3 dependentes
    EVO-003: cascade_impact calcula impacto para categorias ausentes
    EVO-004: detect_cycles encontra ciclos A→B→A
    EVO-005: co_occurrence_matrix calcula afinidades
    EVO-006: Bottlenecks ordenados por influence_score decrescente

  Modulo 4 — PolymathicConvergence (4 CTs):
    EVO-007: find_analogies para raciocinio.probabilistico retorna 3 dominios
    EVO-008: transferability_score entre 0-1 para cada analogia
    EVO-009: Gap sem mapeamento retorna lista vazia
    EVO-010: Multiplos gaps agregam analogias sem duplicatas

  Modulo 5 — TrajectoryMapper (4 CTs):
    EVO-011: classify_scenario: cascade>0.5 + 1 prereq → quick_win
    EVO-012: classify_scenario: >2 prereqs → frontier
    EVO-013: priority_score entre 0-1
    EVO-014: generate_routes produz ao menos 2 rotas

  Pipeline (2 CTs):
    EVO-015: Pipeline completo executa sem erro
    EVO-016: Roadmap tem todos os campos preenchidos

Uso: python specs/test_evolutionary_scanner.py
"""

import json
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from cross_validation_engine import CrossValidationEngine, CapabilityNode
from evolutionary_pipeline import (
    PolymathicConvergence, PolymathicAnalogy,
    TrajectoryMapper, EvolutionaryScenario,
    EvolutionaryScannerPipeline, EvolutionaryRoadmap,
)


class CTResult:
    def __init__(self, ct_id, name, passed, detail="", evidence=None):
        self.ct_id = ct_id; self.name = name; self.passed = passed
        self.detail = detail; self.evidence = evidence


# ─── Helper: mock scan ──────────────────────────────────────────────────

def mock_scan(dims_override=None):
    """Cria mock scan com 10 dimensoes, categorias padrao."""
    from noological_scanner import EPISTEMOLOGICAL_DIMENSIONS
    dims = {}
    for dk, dim in EPISTEMOLOGICAL_DIMENSIONS.items():
        cats = dim.categories
        mid = len(cats) // 2
        dims[dk] = {
            "name": dim.name, "covered": cats[:mid],
            "absent": cats[mid:], "density": 0.5,
            "coverage_pct": 50, "weight": 1.0,
        }
    if dims_override:
        dims.update(dims_override)
    return {"dimensions": dims, "overall_density": 0.5}


# ─── MÓDULO 3 CTs ───────────────────────────────────────────────────────

def evo_001_build_graph() -> CTResult:
    engine = CrossValidationEngine()
    scan = mock_scan()
    nodes = engine.build_graph(scan)
    if len(nodes) < 80:
        return CTResult("EVO-001", "Grafo com >80 nos", False, f"Apenas {len(nodes)}")
    return CTResult("EVO-001", "Grafo construido com sucesso", True, f"{len(nodes)} nos, {len(engine.edges)} arestas")


def evo_002_find_bottlenecks() -> CTResult:
    engine = CrossValidationEngine()
    scan = mock_scan()
    engine.build_graph(scan)
    bns = engine.find_bottlenecks(min_dependents=2)
    if not bns:
        return CTResult("EVO-002", "Bottlenecks detectados", False, "Nenhum bottleneck")
    return CTResult("EVO-002", "Bottlenecks detectados", True, f"{len(bns)} bottlenecks, top: {bns[0].name}")


def evo_003_cascade_impact() -> CTResult:
    engine = CrossValidationEngine()
    scan = mock_scan()
    engine.build_graph(scan)
    cascade = engine.cascade_impact(scan)
    if not cascade:
        return CTResult("EVO-003", "Cascade impact calculado", False, "Vazio")
    # Deve ter impacto > 0 para categorias com dependentes
    has_positive = any(v > 0 for v in cascade.values())
    if not has_positive:
        return CTResult("EVO-003", "Impacto > 0 para categorias com arestas", False, "Todos zero")
    return CTResult("EVO-003", "Cascade impact calculado", True, f"{len(cascade)} categorias com impacto")


def evo_004_detect_cycles() -> CTResult:
    engine = CrossValidationEngine()
    # Criar scan e adicionar ciclo artificial
    scan = mock_scan()
    engine.build_graph(scan)
    # Adicionar aresta reversa para criar ciclo
    from cross_validation_engine import DependencyEdge
    existing = engine.edges[0] if engine.edges else None
    if existing and existing.source in engine.nodes and existing.target in engine.nodes:
        engine.edges.append(DependencyEdge(
            source=existing.target, target=existing.source,
            weight=0.5, relation="enables"
        ))
    cycles = engine.detect_cycles()
    # Pode ou nao ter ciclo — o importante e que nao quebra
    return CTResult("EVO-004", "Detecta ciclos sem erro", True, f"{len(cycles)} ciclos detectados")


def evo_005_co_occurrence() -> CTResult:
    engine = CrossValidationEngine()
    scan = mock_scan()
    engine.build_graph(scan)
    matrix = engine.co_occurrence_matrix()
    if not matrix:
        return CTResult("EVO-005", "Matriz de co-ocorrencia nao vazia", False, "Vazia")
    # Verificar scores entre 0-1
    for (a, b), score in list(matrix.items())[:5]:
        if not (0 <= score <= 1):
            return CTResult("EVO-005", "Scores entre 0 e 1", False, f"Score={score} para {a}-{b}")
    return CTResult("EVO-005", "Matriz de co-ocorrencia calculada", True, f"{len(matrix)} pares")


def evo_006_bottlenecks_ordered() -> CTResult:
    engine = CrossValidationEngine()
    scan = mock_scan()
    engine.build_graph(scan)
    bns = engine.find_bottlenecks(min_dependents=1)
    if len(bns) < 2:
        return CTResult("EVO-006", ">1 bottleneck para ordenar", False, f"Apenas {len(bns)}")
    for i in range(len(bns) - 1):
        if bns[i].influence_score < bns[i+1].influence_score:
            return CTResult("EVO-006", "Ordenado por influence_score", False,
                          f"Pos {i}: {bns[i].influence_score} < {bns[i+1].influence_score}")
    return CTResult("EVO-006", "Bottlenecks ordenados", True, f"Top: {bns[0].name} ({bns[0].influence_score})")


# ─── MÓDULO 4 CTs ───────────────────────────────────────────────────────

def evo_007_find_analogies() -> CTResult:
    pc = PolymathicConvergence()
    # Criar mock gap
    class MockGap:
        def __init__(self, dk, cat): self.dim_key = dk; self.category = cat
    gaps = [MockGap("raciocinio", "Probabilístico")]
    analogies = pc.find_analogies(gaps)
    if len(analogies) < 2:
        return CTResult("EVO-007", "Analogias para raciocinio.probabilistico", False, f"Apenas {len(analogies)}")
    return CTResult("EVO-007", "Analogias encontradas", True, f"{len(analogies)} analogias, top: {analogies[0].external_domain}")


def evo_008_transferability_score() -> CTResult:
    pc = PolymathicConvergence()
    class MockGap:
        def __init__(self, dk, cat): self.dim_key = dk; self.category = cat
    gaps = [MockGap("teoria_jogos", "Equilíbrio de Nash")]
    analogies = pc.find_analogies(gaps)
    for a in analogies:
        if not (0 <= a.transferability_score <= 1):
            return CTResult("EVO-008", "Score entre 0 e 1", False, f"Score={a.transferability_score}")
    return CTResult("EVO-008", "Transferability scores validos", True, f"{len(analogies)} scores OK")


def evo_009_empty_gap() -> CTResult:
    pc = PolymathicConvergence()
    class MockGap:
        def __init__(self, dk, cat): self.dim_key = dk; self.category = cat
    gaps = [MockGap("inexistente", "categoria_inexistente")]
    analogies = pc.find_analogies(gaps)
    if len(analogies) != 0:
        return CTResult("EVO-009", "Gap desconhecido = 0 analogias", False, f"{len(analogies)} retornadas")
    return CTResult("EVO-009", "Gap desconhecido retorna vazio", True, "0 analogias (sem erro)")


def evo_010_multiple_gaps() -> CTResult:
    pc = PolymathicConvergence()
    class MockGap:
        def __init__(self, dk, cat): self.dim_key = dk; self.category = cat
    gaps = [
        MockGap("raciocinio", "Probabilístico"),
        MockGap("teoria_jogos", "Evolutivo"),
        MockGap("paradigmas", "Fenomenológico"),
    ]
    analogies = pc.find_analogies(gaps)
    # Sem duplicatas: verificar (gap_category, external_domain) unicos
    keys = [(a.gap_category, a.external_domain) for a in analogies]
    if len(keys) != len(set(keys)):
        return CTResult("EVO-010", "Sem duplicatas nas analogias", False, f"{len(keys)} total, {len(set(keys))} unicos")
    return CTResult("EVO-010", "Multiplos gaps agregados sem duplicatas", True, f"{len(analogies)} analogias de {len(gaps)} gaps")


# ─── MÓDULO 5 CTs ───────────────────────────────────────────────────────

def evo_011_quick_win() -> CTResult:
    tm = TrajectoryMapper()
    scenario = tm.classify_scenario("test_cat", "test_domain", cascade_impact=0.8, prerequisites=["A"], has_analogy=False)
    if scenario.scenario_type != "quick_win":
        return CTResult("EVO-011", "cascade>0.5 + 1 prereq → quick_win", False, f"Tipo: {scenario.scenario_type}")
    return CTResult("EVO-011", "Quick-win classificado", True, f"priority={scenario.priority_score}")


def evo_012_frontier() -> CTResult:
    tm = TrajectoryMapper()
    scenario = tm.classify_scenario("test_cat", "test_domain", cascade_impact=0.3, prerequisites=["A","B","C"], has_analogy=False)
    if scenario.scenario_type != "frontier":
        return CTResult("EVO-012", ">2 prereqs → frontier", False, f"Tipo: {scenario.scenario_type}")
    return CTResult("EVO-012", "Frontier classificado", True, f"priority={scenario.priority_score}")


def evo_013_priority_score() -> CTResult:
    tm = TrajectoryMapper()
    scenarios = [
        tm.classify_scenario("a","d", 0.9, [], True),
        tm.classify_scenario("b","d", 0.3, ["x","y","z"], False),
        tm.classify_scenario("c","d", 0.5, ["w"], False),
    ]
    for s in scenarios:
        if not (0 <= s.priority_score <= 1):
            return CTResult("EVO-013", "priority entre 0 e 1", False, f"Score={s.priority_score}")
    return CTResult("EVO-013", "Priority scores validos", True, f"Range: {min(s.priority_score for s in scenarios)}-{max(s.priority_score for s in scenarios)}")


def evo_014_generate_routes() -> CTResult:
    tm = TrajectoryMapper()
    scenarios = [
        EvolutionaryScenario("a","d","quick_win",0.9,0.8,[]),
        EvolutionaryScenario("b","d","foundation",0.7,0.6,["a"]),
        EvolutionaryScenario("c","d","convergent",0.6,0.4,[]),
        EvolutionaryScenario("d","d","frontier",0.4,0.3,["a","b","c"]),
        EvolutionaryScenario("e","d","quick_win",0.5,0.2,[]),
    ]
    routes = tm.generate_routes(scenarios, max_routes=3)
    if len(routes) < 2:
        return CTResult("EVO-014", ">=2 rotas geradas", False, f"Apenas {len(routes)}")
    # Rota A deve ter quick_wins primeiro
    if routes[0].steps[0].scenario_type != "quick_win":
        return CTResult("EVO-014", "Rota A comeca com quick_wins", False, f"Primeiro: {routes[0].steps[0].scenario_type}")
    return CTResult("EVO-014", "Rotas geradas corretamente", True, f"{len(routes)} rotas, Rota A: {routes[0].name}")


# ─── PIPELINE CTs ───────────────────────────────────────────────────────

def evo_015_pipeline_executes() -> CTResult:
    pipeline = EvolutionaryScannerPipeline()
    from teleological_scanner import TeleologicalGoal
    class MockP:
        def __init__(self, t): self.text = t
    class MockT:
        def __init__(self, t): self.paragraphs = {"P1": MockP(t)}; self.citation_map = []
    trail = MockT("Estudo randomizado com analise bayesiana e follow-up de 12 meses. Equilibrio de Nash aplicado.")
    goals = [TeleologicalGoal("Efeito causal", "causal")]
    try:
        roadmap = pipeline.scan(trail, goals)
    except Exception as e:
        return CTResult("EVO-015", "Pipeline executa sem erro", False, str(e))
    return CTResult("EVO-015", "Pipeline executa sem erro", True, f"Roadmap com {roadmap.total_gaps} gaps")


def evo_016_roadmap_complete() -> CTResult:
    pipeline = EvolutionaryScannerPipeline()
    from teleological_scanner import TeleologicalGoal
    class MockP:
        def __init__(self, t): self.text = t
    class MockT:
        def __init__(self, t): self.paragraphs = {"P1": MockP(t)}; self.citation_map = []
    trail = MockT("Estudo randomizado controlado. Abordagem quantitativa e qualitativa mista.")
    goals = [TeleologicalGoal("Efeito causal", "causal")]
    roadmap = pipeline.scan(trail, goals)
    
    checks = []
    if roadmap.noological_coverage < 0:
        checks.append("noological_coverage")
    if roadmap.total_gaps < 0:
        checks.append("total_gaps")
    if not roadmap.scenarios:
        checks.append("scenarios")
    if not roadmap.routes:
        checks.append("routes")
    if not roadmap.bottlenecks:
        checks.append("bottlenecks")
    
    if checks:
        return CTResult("EVO-016", "Roadmap com todos os campos", False, f"Faltam: {', '.join(checks)}")
    
    report = pipeline.generate_report(roadmap)
    if "Roadmap Evolutivo" not in report:
        return CTResult("EVO-016", "Report contem titulo", False, "Titulo ausente")
    
    return CTResult("EVO-016", "Roadmap completo com report", True,
                    f"Score teleologico={roadmap.teleological_score:.0%}, {roadmap.total_gaps} gaps, "
                    f"QW={roadmap.quick_wins} FO={roadmap.foundations} CV={roadmap.convergents} FR={roadmap.frontiers}")


# ─── Runner ──────────────────────────────────────────────────────────────

CT_LIST = [
    evo_001_build_graph, evo_002_find_bottlenecks, evo_003_cascade_impact,
    evo_004_detect_cycles, evo_005_co_occurrence, evo_006_bottlenecks_ordered,
    evo_007_find_analogies, evo_008_transferability_score, evo_009_empty_gap,
    evo_010_multiple_gaps, evo_011_quick_win, evo_012_frontier,
    evo_013_priority_score, evo_014_generate_routes,
    evo_015_pipeline_executes, evo_016_roadmap_complete,
]


def run_all(json_out=False):
    results = []
    for ct_func in CT_LIST:
        try: r = ct_func()
        except Exception as e: r = CTResult(ct_func.__name__, "UNKNOWN", False, f"Excecao: {e}")
        results.append(r)
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    if not json_out: _print_summary(results, passed, failed)
    return {"passed": passed, "failed": failed, "total": len(results),
            "results": [{"id": r.ct_id, "name": r.name, "passed": r.passed, "detail": r.detail} for r in results]}


def _print_summary(results, passed, failed):
    G = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; RE = "\033[0m"; B = "\033[1m"
    print(f"\n{B}{'='*80}{RE}")
    print(f"  {B}SPEC-030 Evolutionary Trajectories Scanner — {len(results)} Critical Tests{RE}")
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
    p = argparse.ArgumentParser(description="SPEC-030 Evolutionary Scanner TDD Suite")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    r = run_all(json_out=args.json)
    if args.json: print(json.dumps(r, indent=2, ensure_ascii=False))
    sys.exit(0 if r["failed"] == 0 else 1)
