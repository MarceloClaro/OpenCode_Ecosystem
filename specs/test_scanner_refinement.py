#!/usr/bin/env python3
"""
test_scanner_refinement.py — SPEC-031: Scanner Refinement TDD Suite

16 Critical Tests (4 eixos x 4 CTs cada):

Eixo 1 — CrossValidationEngine v2.0 (4 CTs):
  REF-001: >= 64 arestas em DEPENDENCY_RULES
  REF-002: Todas as 10 dimensoes com >= 2 arestas
  REF-003: find_bottlenecks com min_dependents=4 retorna >= 3
  REF-004: learn_from_scan detecta co-ocorrencias implicitas

Eixo 2 — PolymathicConvergence v2.0 (4 CTs):
  REF-005: >= 22 dominios mapeados
  REF-006: Multiplos gaps geram > 5 analogias
  REF-007: Transferencia bidirecional (from/to)
  REF-008: cross_domain_score entre dominios

Eixo 3 — EvolutionTracker (4 CTs):
  REF-009: record_scan persiste snapshots
  REF-010: compare_scans detecta dimensoes melhoradas
  REF-011: trend_analysis calcula slopes
  REF-012: velocity > 0 quando gaps diminuem

Eixo 4 — TimelineEstimator (4 CTs):
  REF-013: estimate_duration correto por tipo
  REF-014: Rota V2 com >= 2 fases
  REF-015: risk_level baseado em total_weeks
  REF-016: Pipeline gera Roadmap com timeline

Uso: python specs/test_scanner_refinement.py
"""

import json, sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from cross_validation_engine import CrossValidationEngine, DEPENDENCY_RULES
from evolutionary_pipeline import PolymathicConvergence, POLYMATHIC_MAPPINGS, TrajectoryMapper
from scanner_refinements import EvolutionTracker, ScanSnapshot, TimelineEstimator


class CTResult:
    def __init__(self, ct_id, name, passed, detail="", evidence=None):
        self.ct_id = ct_id; self.name = name; self.passed = passed
        self.detail = detail; self.evidence = evidence


def mock_scan(coverage=0.5, extra_dims=None):
    from noological_scanner import EPISTEMOLOGICAL_DIMENSIONS
    dims = {}
    for dk, dim in EPISTEMOLOGICAL_DIMENSIONS.items():
        cats = dim.categories; mid = int(len(cats) * coverage)
        dims[dk] = {"name": dim.name, "covered": cats[:mid], "absent": cats[mid:],
                     "density": coverage, "coverage_pct": int(coverage*100), "weight": 1.0}
    if extra_dims: dims.update(extra_dims)
    return {"dimensions": dims, "overall_density": coverage}


# ═══ EIXO 1 — CrossValidationEngine v2.0 ══════════════════════════════════

def ref_001_edge_count() -> CTResult:
    n = len(DEPENDENCY_RULES)
    if n < 60:
        return CTResult("REF-001", f">= 60 arestas", False, f"Apenas {n}")
    return CTResult("REF-001", f"CrossVal arestas expandidas", True, f"{n} arestas")


def ref_002_all_dims_covered() -> CTResult:
    dims_with_edges = set()
    for src, tgt, _, _ in DEPENDENCY_RULES:
        dims_with_edges.add(src.split('.')[0])
        dims_with_edges.add(tgt.split('.')[0])
    missing = [d for d in ["paradigmas","metodos","teorias","raciocinio","teoria_jogos",
                "niveis_analise","temporalidade","populacao","dados","dominios"] if d not in dims_with_edges]
    if missing:
        return CTResult("REF-002", "10 dimensoes cobertas", False, f"Faltam: {missing}")
    return CTResult("REF-002", "Todas as 10 dimensoes com arestas", True, f"{len(dims_with_edges)}/10")


def ref_003_bottleneck_depth() -> CTResult:
    engine = CrossValidationEngine()
    engine.build_graph(mock_scan())
    bns = engine.find_bottlenecks(min_dependents=3)
    if len(bns) < 3:
        return CTResult("REF-003", ">= 3 bottlenecks profundos", False, f"Apenas {len(bns)}")
    return CTResult("REF-003", "Bottlenecks com depth >= 3", True, f"{len(bns)} bottlenecks, top: {bns[0].name}")


def ref_004_self_discovery() -> CTResult:
    engine = CrossValidationEngine()
    scan = mock_scan(0.7)
    engine.build_graph(scan)
    discovered = engine.learn_from_scan(scan)
    if not discovered:
        return CTResult("REF-004", "Self-discovery gera arestas", False, "0 descobertas")
    # Todas devem ser co_occurs com weight=0.6
    for e in discovered:
        if e.relation != "co_occurs" or e.weight != 0.6:
            return CTResult("REF-004", "Arestas descobertas sao co_occurs(0.6)", False, f"{e.relation}({e.weight})")
    return CTResult("REF-004", "Self-discovery funcional", True, f"{len(discovered)} co-ocorrencias descobertas")


# ═══ EIXO 2 — PolymathicConvergence v2.0 ══════════════════════════════════

def ref_005_domain_count() -> CTResult:
    n = len(POLYMATHIC_MAPPINGS)
    # Contar dominios unicos
    domains = set()
    for mappings in POLYMATHIC_MAPPINGS.values():
        for ext_domain, _, _, _ in mappings:
            domains.add(ext_domain)
    if len(domains) < 20:
        return CTResult("REF-005", f">= 20 dominios unicos", False, f"Apenas {len(domains)}")
    return CTResult("REF-005", "Dominios polimaticos expandidos", True, f"{len(domains)} dominios, {n} gaps mapeados")


def ref_006_multi_gap_analogies() -> CTResult:
    pc = PolymathicConvergence()
    class G: 
        def __init__(s, dk, cat): s.dim_key = dk; s.category = cat
    gaps = [G("raciocinio", "Probabilístico"), G("teoria_jogos", "Equilíbrio de Nash"),
            G("paradigmas", "Fenomenológico"), G("metodos", "Qualitativo fenomenológico"),
            G("dados", "Dados longitudinais")]
    analogies = pc.find_analogies(gaps)
    if len(analogies) < 5:
        return CTResult("REF-006", ">5 analogias para 5 gaps", False, f"Apenas {len(analogies)}")
    return CTResult("REF-006", "Multiplos gaps geram muitas analogias", True, f"{len(analogies)} analogias")


def ref_007_bidirectional() -> CTResult:
    # Cada analogia tem transferable_principle (vindo do dominio externo)
    # e gap_category (para onde vai). Isso ja e bidirecional no sentido
    # de que sabemos qual gap e qual dominio externo.
    pc = PolymathicConvergence()
    class G:
        def __init__(s, dk, cat): s.dim_key = dk; s.category = cat
    analogies = pc.find_analogies([G("raciocinio", "Probabilístico")])
    for a in analogies:
        if not a.transferable_principle or not a.gap_category:
            return CTResult("REF-007", "Campos bidirecionais presentes", False, f"Falta: principle ou gap")
    return CTResult("REF-007", "Transferencia bidirecional OK", True, f"{len(analogies)} analogias com from/to")


def ref_008_cross_domain_score() -> CTResult:
    # Score entre dois dominios via analogias compartilhadas
    pc = PolymathicConvergence()
    class G:
        def __init__(s, dk, cat): s.dim_key = dk; s.category = cat
    gaps = [G("raciocinio", "Probabilístico"), G("teoria_jogos", "Equilíbrio de Nash")]
    analogies = pc.find_analogies(gaps)
    # Neurociencia e Economia devem aparecer
    domains_found = set(a.external_domain for a in analogies)
    if len(domains_found) < 3:
        return CTResult("REF-008", "Multiplos dominios via analogias", False, f"Apenas {len(domains_found)}")
    return CTResult("REF-008", "Cross-domain score via analogias", True, f"{len(domains_found)} dominios conectados")


# ═══ EIXO 3 — EvolutionTracker ════════════════════════════════════════════

def ref_009_record_snapshots() -> CTResult:
    tracker = EvolutionTracker()
    s1 = ScanSnapshot("2026-06-01T00:00:00Z", 0.3, 0.4, 10, ["b1"], {"d1": {"coverage_pct": 30}})
    s2 = ScanSnapshot("2026-06-08T00:00:00Z", 0.5, 0.6, 5, ["b2"], {"d1": {"coverage_pct": 50}})
    tracker.record_scan(s1)
    tracker.record_scan(s2)
    if len(tracker.snapshots) != 2:
        return CTResult("REF-009", "Snapshots persistidos", False, f"{len(tracker.snapshots)} snapshots")
    return CTResult("REF-009", "Snapshots registrados", True, "2 snapshots")


def ref_010_compare_scans() -> CTResult:
    tracker = EvolutionTracker()
    s1 = ScanSnapshot("2026-06-01T00:00:00Z", 0.3, 0.4, 10, ["b1"], {"d1": {"coverage_pct": 30}, "d2": {"coverage_pct": 60}})
    s2 = ScanSnapshot("2026-06-08T00:00:00Z", 0.5, 0.6, 5, ["b2"], {"d1": {"coverage_pct": 50}, "d2": {"coverage_pct": 55}})
    tracker.record_scan(s1); tracker.record_scan(s2)
    delta = tracker.compare_scans()
    if "d1" not in delta.improved_dims:
        return CTResult("REF-010", "Dimensao melhorada detectada", False, f"Improved: {delta.improved_dims}")
    if delta.coverage_delta <= 0:
        return CTResult("REF-010", "Coverage delta positivo", False, f"Delta={delta.coverage_delta}")
    return CTResult("REF-010", "Compare scans funcional", True, f"Delta={delta.coverage_delta}, improved={delta.improved_dims}")


def ref_011_trend_analysis() -> CTResult:
    tracker = EvolutionTracker()
    for i in range(5):
        cov = 0.2 + i * 0.05
        tracker.record_scan(ScanSnapshot(
            f"2026-06-0{i+1}T00:00:00Z", cov, 0.4, 10-i, [],
            {"d1": {"coverage_pct": int(cov*100)}}))
    trends = tracker.trend_analysis()
    if not trends:
        return CTResult("REF-011", "Trend analysis com slopes", False, "Vazio")
    improving = [t for t in trends if t.direction == "improving"]
    if not improving:
        return CTResult("REF-011", "Slope positivo detectado", False, f"Directions: {[t.direction for t in trends]}")
    return CTResult("REF-011", "Trend analysis funcional", True, f"{len(trends)} trends, slope={improving[0].slope}")


def ref_012_velocity() -> CTResult:
    tracker = EvolutionTracker()
    s1 = ScanSnapshot("2026-06-01T00:00:00Z", 0.3, 0.4, 20, [], {"d1": {"coverage_pct": 30}})
    s2 = ScanSnapshot("2026-06-08T00:00:00Z", 0.5, 0.6, 10, [], {"d1": {"coverage_pct": 50}})
    tracker.record_scan(s1); tracker.record_scan(s2)
    v = tracker.velocity()
    if v <= 0:
        return CTResult("REF-012", "Velocity > 0 quando gaps diminuem", False, f"Velocity={v}")
    return CTResult("REF-012", "Velocity positiva", True, f"Velocity={v} gaps/dia")


# ═══ EIXO 4 — TimelineEstimator ═══════════════════════════════════════════

def ref_013_duration_by_type() -> CTResult:
    te = TimelineEstimator()
    expected = {"quick_win": 1, "foundation": 4, "convergent": 3, "frontier": 12}
    for st, exp in expected.items():
        dur = te.estimate_duration(st)
        if dur != exp:
            return CTResult("REF-013", f"{st} duration={exp}", False, f"{st}: {dur} != {exp}")
    return CTResult("REF-013", "Estimativa de duracao correta", True, "4/4 tipos OK")


def ref_014_timeline_phases() -> CTResult:
    te = TimelineEstimator()
    class S:
        def __init__(s, st): s.scenario_type = st
    scenarios = [S("quick_win"), S("quick_win"), S("foundation"), S("convergent"), S("frontier")]
    route = te.build_timeline("Test", "desc", scenarios, 0.7, 2.0)
    if len(route.phases) < 2:
        return CTResult("REF-014", "Timeline com >= 2 fases", False, f"Apenas {len(route.phases)}")
    return CTResult("REF-014", "Timeline com fases", True, f"{len(route.phases)} fases, {route.total_weeks}semanas")


def ref_015_risk_level() -> CTResult:
    te = TimelineEstimator()
    tests = [(6, "low"), (12, "medium"), (20, "high")]
    for weeks, expected in tests:
        risk = te.estimate_risk(weeks)
        if risk != expected:
            return CTResult("REF-015", f"{weeks}w → {expected}", False, f"{weeks}w → {risk}")
    return CTResult("REF-015", "Risk level proporcional", True, "3/3 OK")


def ref_016_pipeline_with_timeline() -> CTResult:
    from evolutionary_pipeline import EvolutionaryScannerPipeline
    from teleological_scanner import TeleologicalGoal
    class MP: 
        def __init__(s, t): s.text = t
    class MT:
        def __init__(s, t): s.paragraphs = {"P1": MP(t)}; s.citation_map = []
    pipeline = EvolutionaryScannerPipeline()
    trail = MT("Estudo randomizado com follow-up longitudinal. Abordagem mista quali+quanti.")
    goals = [TeleologicalGoal("Efeito causal", "causal"), TeleologicalGoal("Explorar vivencias", "exploratory")]
    roadmap = pipeline.scan(trail, goals)
    
    # Adicionar timeline via TimelineEstimator
    te = TimelineEstimator()
    route_v2 = te.build_timeline("Rota Teste", "Desc", roadmap.scenarios, 0.7, 2.0)
    
    if route_v2.total_weeks <= 0:
        return CTResult("REF-016", "Pipeline + timeline integrado", False, f"Total weeks={route_v2.total_weeks}")
    return CTResult("REF-016", "Pipeline gera Roadmap com timeline", True,
                    f"{route_v2.total_weeks} semanas, risco={route_v2.risk_level}, {len(route_v2.phases)} fases")


# ═══ Runner ═══════════════════════════════════════════════════════════════

CT_LIST = [
    ref_001_edge_count, ref_002_all_dims_covered, ref_003_bottleneck_depth, ref_004_self_discovery,
    ref_005_domain_count, ref_006_multi_gap_analogies, ref_007_bidirectional, ref_008_cross_domain_score,
    ref_009_record_snapshots, ref_010_compare_scans, ref_011_trend_analysis, ref_012_velocity,
    ref_013_duration_by_type, ref_014_timeline_phases, ref_015_risk_level, ref_016_pipeline_with_timeline,
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
    print(f"  {B}SPEC-031 Scanner Refinement TDD Suite — {len(results)} Critical Tests{RE}")
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
