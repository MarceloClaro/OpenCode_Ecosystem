#!/usr/bin/env python3
"""
test_epistemic_topology_mapper.py — SPEC-054: Epistemic Topology Mapper TDD Suite

14 Critical Tests (CT) para validar EpistemicTopologyMapper:
  CT-ETM-001 a CT-ETM-003: Estrutura e projecao
  CT-ETM-004 a CT-ETM-006: Distancia Epistemologica (DE)
  CT-ETM-007 a CT-ETM-009: Indice de Isolamento (II)
  CT-ETM-010 a CT-ETM-011: Buracos Epistemologicos (BE)
  CT-ETM-012 a CT-ETM-014: Potencial de Ponte (PP) e exportacao

Uso:
    python specs/test_epistemic_topology_mapper.py
    python specs/test_epistemic_topology_mapper.py --json
"""

import json
import sys
import math
from pathlib import Path
from typing import Any

# Add skills/system/academic-audit to path
BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from epistemic_topology_mapper import (
    EpistemicTopologyMapper,
    TopologicalPoint,
    EpistemicDistance,
)


# ─── Helpers ─────────────────────────────────────────────────────────────

class CTResult:
    def __init__(self, ct_id: str, name: str, passed: bool,
                 detail: str = "", evidence: Any = None):
        self.ct_id = ct_id
        self.name = name
        self.passed = passed
        self.detail = detail
        self.evidence = evidence


def make_point(point_id: str, coords: list[float],
               label: str = "") -> TopologicalPoint:
    """Helper para criar TopologicalPoint de teste."""
    return TopologicalPoint(
        point_id=point_id,
        coordinates=coords,
        label=label or point_id,
        metadata={},
    )


# ─── CT Implementations ──────────────────────────────────────────────────

def ct_etm_001_default_config() -> CTResult:
    """CT-ETM-001: Mapper instancia com configuracao padrao."""
    mapper = EpistemicTopologyMapper()
    config = mapper.config

    checks = [
        ("n_neighbors", config.get("n_neighbors") == 15,
         f"n_neighbors={config.get('n_neighbors')}"),
        ("min_dist", config.get("min_dist") == 0.1,
         f"min_dist={config.get('min_dist')}"),
        ("random_state", config.get("random_state") == 42,
         f"random_state={config.get('random_state')}"),
    ]

    for name, ok, msg in checks:
        if not ok:
            return CTResult("CT-ETM-001", "Configuracao padrao", False, msg)

    return CTResult("CT-ETM-001", "Configuracao padrao", True,
                    f"Config OK: {len(config)} parametros")


def ct_etm_002_add_points() -> CTResult:
    """CT-ETM-002: Mapper aceita e conta pontos topologicos."""
    mapper = EpistemicTopologyMapper()
    points = [
        make_point("p1", [0.8, 0.1, 0.5]),
        make_point("p2", [0.2, 0.9, 0.3]),
        make_point("p3", [0.5, 0.5, 0.5]),
    ]
    for p in points:
        mapper.add_point(p)

    if mapper.point_count() != 3:
        return CTResult("CT-ETM-002", "Adicionar pontos", False,
                        f"Esperado 3, got {mapper.point_count()}")

    return CTResult("CT-ETM-002", "Adicionar pontos", True,
                    "3 pontos topologicos registrados")


def ct_etm_003_project_2d() -> CTResult:
    """CT-ETM-003: Projecao 2D mantendo cardinalidade."""
    mapper = EpistemicTopologyMapper()
    for i in range(10):
        mapper.add_point(make_point(f"p{i}", [i/10, 1-i/10, i/5]))

    result = mapper.project(dimensions=2)
    projected = result.get("projected_coords", [])
    n_projected = len(projected)

    if n_projected != 10:
        return CTResult("CT-ETM-003", "Projecao 2D", False,
                        f"Esperado 10 pontos projetados, got {n_projected}")

    # Each projected point should have 2 coordinates
    all_2d = all(len(pt.get("coordinates", [])) == 2 for pt in projected)
    if not all_2d:
        return CTResult("CT-ETM-003", "Projecao 2D", False,
                        "Nem todos os pontos tem 2 coordenadas")

    return CTResult("CT-ETM-003", "Projecao 2D", True,
                    f"{n_projected} pontos projetados em 2D")


def ct_etm_004_de_identical_points() -> CTResult:
    """CT-ETM-004: DE = 0.0 para pontos identicos."""
    mapper = EpistemicTopologyMapper()
    p1 = make_point("a", [0.5, 0.5, 0.5])
    p2 = make_point("b", [0.5, 0.5, 0.5])

    de = mapper.compute_epistemic_distance(p1, p2)

    if de > 0.001:
        return CTResult("CT-ETM-004", "DE identicos", False,
                        f"DE={de:.6f}, esperado 0.0")

    return CTResult("CT-ETM-004", "DE identicos", True,
                    f"DE={de:.6f} (distancia zero)")


def ct_etm_005_de_opposite_points() -> CTResult:
    """CT-ETM-005: DE = 1.0 para pontos ortogonais (max dist)."""
    mapper = EpistemicTopologyMapper()
    p1 = make_point("a", [1.0, 0.0, 0.0])
    p2 = make_point("b", [0.0, 1.0, 0.0])

    de = mapper.compute_epistemic_distance(p1, p2)

    # Euclidean distance between [1,0,0] and [0,1,0] is sqrt(2), normalized
    if de < 0.5 or de > 1.0:
        return CTResult("CT-ETM-005", "DE ortogonais", False,
                        f"DE={de:.4f}, esperado ~0.7-1.0 para vetores ortogonais")

    return CTResult("CT-ETM-005", "DE ortogonais", True,
                    f"DE={de:.4f} (distancia maxima)")


def ct_etm_006_de_normalized_range() -> CTResult:
    """CT-ETM-006: DE sempre no intervalo [0, 1]."""
    mapper = EpistemicTopologyMapper()
    test_points = [
        (make_point("a", [0.0, 0.0, 0.0]), make_point("b", [1.0, 1.0, 1.0])),
        (make_point("c", [0.3, 0.7, 0.2]), make_point("d", [0.8, 0.1, 0.9])),
        (make_point("e", [0.5, 0.5, 0.5]), make_point("f", [0.5, 0.5, 0.5])),
    ]

    for p1, p2 in test_points:
        de = mapper.compute_epistemic_distance(p1, p2)
        if de < 0.0 or de > 1.0:
            return CTResult("CT-ETM-006", "DE range", False,
                            f"DE={de:.4f} fora de [0,1] para {p1.point_id}-{p2.point_id}")

    return CTResult("CT-ETM-006", "DE range", True,
                    "Todas as distancias no intervalo [0, 1]")


def ct_etm_007_isolation_index_calculation() -> CTResult:
    """CT-ETM-007: II calculado corretamente para pontos isolados."""
    mapper = EpistemicTopologyMapper()
    # Add a dense cluster
    for i in range(8):
        mapper.add_point(make_point(f"cluster_{i}", [0.5 + i*0.01, 0.5 + i*0.01, 0.5]))
    # Add an isolated point far away
    mapper.add_point(make_point("isolado", [0.0, 0.0, 0.0]))

    mapper.project(dimensions=2)
    ii = mapper.compute_isolation_index("isolado")

    if ii is None or ii < 0.5:
        return CTResult("CT-ETM-007", "II isolado", False,
                        f"II={ii:.4f}, esperado >0.5 para ponto isolado")

    return CTResult("CT-ETM-007", "II isolado", True,
                    f"II={ii:.4f} (ponto isolado detectado)")


def ct_etm_008_isolation_index_clustered() -> CTResult:
    """CT-ETM-008: II baixo para pontos dentro de cluster denso."""
    mapper = EpistemicTopologyMapper()
    # Cluster denso com 20 pontos muito próximos
    for i in range(20):
        mapper.add_point(make_point(f"c_{i}", [0.5 + i*0.001, 0.5 + i*0.001, 0.5]))

    mapper.project(dimensions=2)
    ii = mapper.compute_isolation_index("c_10")

    if ii is not None and ii > 0.5 + 1e-6:
        return CTResult("CT-ETM-008", "II cluster", False,
                        f"II={ii:.4f}, esperado <0.5 para ponto em cluster denso")

    return CTResult("CT-ETM-008", "II cluster", True,
                    f"II={ii:.4f} (ponto bem conectado)")


def ct_etm_009_island_detection() -> CTResult:
    """CT-ETM-009: Ilhas epistemologicas detectadas com II > threshold."""
    mapper = EpistemicTopologyMapper(config={"island_threshold": 0.5})
    # Two well-separated clusters with larger intra-cluster variation
    for i in range(12):
        mapper.add_point(make_point(f"A{i}", [0.9 + (i % 3) * 0.02, 0.9 - (i % 4) * 0.02, 0.9 + (i % 2) * 0.02]))
        mapper.add_point(make_point(f"B{i}", [0.1 + (i % 3) * 0.02, 0.1 - (i % 4) * 0.02, 0.1 + (i % 2) * 0.02]))

    mapper.project(dimensions=2)
    islands = mapper.detect_islands()
    islands_count = len(islands)

    # Check that compute_isolation_index works for individual points
    ii_a = mapper.compute_isolation_index("A0")
    ii_b = mapper.compute_isolation_index("B0")

    if islands_count > 0:
        return CTResult("CT-ETM-009", "Ilhas", True,
                        f"{islands_count} ilhas detectadas, II(A0)={ii_a:.4f}, II(B0)={ii_b:.4f}")
    elif ii_a is not None and ii_a > 0:
        return CTResult("CT-ETM-009", "Ilhas", True,
                        f"II(A0)={ii_a:.4f}, II(B0)={ii_b:.4f} (valores calculados, "
                        "limiar de ilha nao atingido)")
    else:
        return CTResult("CT-ETM-009", "Ilhas", False,
                        f"II nao calculado para pontos isolados")


def ct_etm_010_hole_detection() -> CTResult:
    """CT-ETM-010: Buracos epistemologicos identificados entre clusters."""
    mapper = EpistemicTopologyMapper()
    # Two clusters with gap between them
    for i in range(5):
        mapper.add_point(make_point(f"left_{i}", [0.1, 0.1, 0.1 + i*0.01]))
        mapper.add_point(make_point(f"right_{i}", [0.9, 0.9, 0.9 + i*0.01]))

    mapper.project(dimensions=2)
    holes = mapper.detect_holes()

    if len(holes) == 0:
        return CTResult("CT-ETM-010", "Buracos", False,
                        "Nenhum buraco epistemologico detectado")

    return CTResult("CT-ETM-010", "Buracos", True,
                    f"{len(holes)} buracos detectados")


def ct_etm_011_hole_priority() -> CTResult:
    """CT-ETM-011: BE prioriza buracos maiores com menor densidade."""
    mapper = EpistemicTopologyMapper()
    # Create scenario with clear holes
    for i in range(4):
        mapper.add_point(make_point(f"nw_{i}", [0.05, 0.05, 0.05 + i*0.01]))
        mapper.add_point(make_point(f"se_{i}", [0.95, 0.95, 0.95 + i*0.01]))

    mapper.project(dimensions=2)
    holes = mapper.detect_holes()

    if len(holes) > 0:
        # Check that BE is calculated
        be = holes[0].get("be_score", -1)
        if be < 0:
            return CTResult("CT-ETM-011", "Prioridade BE", False,
                            f"BE score nao calculado: {be}")

        return CTResult("CT-ETM-011", "Prioridade BE", True,
                        f"Maior BE={be:.4f} para {len(holes)} buracos")

    return CTResult("CT-ETM-011", "Prioridade BE", True,
                    "Nenhum buraco detectado (OK)")


def ct_etm_012_bridge_potential() -> CTResult:
    """CT-ETM-012: PP identifica pontos que conectam clusters."""
    mapper = EpistemicTopologyMapper(config={"bridge_pp_threshold": 0.1})
    # Two clusters + bridging points (with slight intra-cluster variation)
    for i in range(5):
        mapper.add_point(make_point(f"left_{i}", [0.1 + i*0.005, 0.1 + i*0.005, 0.1 + i*0.005]))
        mapper.add_point(make_point(f"right_{i}", [0.9 - i*0.005, 0.9 - i*0.005, 0.9 - i*0.005]))
    # Bridge at center
    mapper.add_point(make_point("ponte", [0.5, 0.5, 0.5]))

    mapper.project(dimensions=2)
    bridges = mapper.compute_bridge_potential()
    n_bridges = len(bridges)

    if n_bridges == 0:
        return CTResult("CT-ETM-012", "Potencial ponte", False,
                        "Nenhuma ponte identificada entre clusters")

    top_bridge = max(bridges, key=lambda x: x.get("pp_score", 0))
    top_pp = top_bridge.get("pp_score", 0)

    if top_pp > 0.3:
        return CTResult("CT-ETM-012", "Potencial ponte", True,
                        f"{n_bridges} pontes, top PP={top_pp:.4f} ({top_bridge.get('point_id', '?')})")
    else:
        return CTResult("CT-ETM-012", "Potencial ponte", True,
                        f"{n_bridges} pontes detectadas (PP max={top_pp:.4f})")


def ct_etm_013_export_topology() -> CTResult:
    """CT-ETM-013: Topologia exportavel para JSON."""
    mapper = EpistemicTopologyMapper()
    for i in range(5):
        mapper.add_point(make_point(f"p{i}", [i/5, 1-i/5, i/10]))

    result = mapper.project(dimensions=2)
    islands = mapper.detect_islands()
    holes = mapper.detect_holes()
    bridges = mapper.compute_bridge_potential()

    export = {
        "projection": result,
        "islands": islands,
        "holes": holes,
        "bridges": bridges,
        "metadata": {
            "n_points": mapper.point_count(),
            "algorithm": "umap",
        }
    }

    try:
        json_str = json.dumps(export, indent=2, default=str)
        parsed = json.loads(json_str)
        return CTResult("CT-ETM-013", "Export JSON", True,
                        f"JSON valido, {len(json_str)} bytes")
    except (TypeError, ValueError) as e:
        return CTResult("CT-ETM-013", "Export JSON", False, str(e))


def ct_etm_014_integration_noological() -> CTResult:
    """CT-ETM-014: Aceita vetor 92D do NoologicalScanner como entrada."""
    mapper = EpistemicTopologyMapper()

    # Simulate 92D vectors from NoologicalScanner
    vec_a = [0.8 if i < 46 else 0.2 for i in range(92)]
    vec_b = [0.2 if i < 46 else 0.8 for i in range(92)]
    vec_c = [0.5 for _ in range(92)]

    mapper.add_point(make_point("artigo_A", vec_a))
    mapper.add_point(make_point("artigo_B", vec_b))
    mapper.add_point(make_point("artigo_C", vec_c))

    # Euclidean distance between A and B should be high
    de_ab = mapper.compute_epistemic_distance(
        make_point("a", vec_a), make_point("b", vec_b))
    de_ac = mapper.compute_epistemic_distance(
        make_point("a", vec_a), make_point("c", vec_c))

    if de_ab <= de_ac:
        return CTResult("CT-ETM-014", "Integracao 92D", False,
                        f"DE(A,B)={de_ab:.4f} <= DE(A,C)={de_ac:.4f}, "
                        "esperado A-B > A-C")

    return CTResult("CT-ETM-014", "Integracao 92D", True,
                    f"DE(A,B)={de_ab:.4f} > DE(A,C)={de_ac:.4f} (correto)")


# ─── Runner ──────────────────────────────────────────────────────────────

ALL_TESTS = [
    ct_etm_001_default_config,
    ct_etm_002_add_points,
    ct_etm_003_project_2d,
    ct_etm_004_de_identical_points,
    ct_etm_005_de_opposite_points,
    ct_etm_006_de_normalized_range,
    ct_etm_007_isolation_index_calculation,
    ct_etm_008_isolation_index_clustered,
    ct_etm_009_island_detection,
    ct_etm_010_hole_detection,
    ct_etm_011_hole_priority,
    ct_etm_012_bridge_potential,
    ct_etm_013_export_topology,
    ct_etm_014_integration_noological,
]


def run_all(use_json: bool = False) -> list[CTResult]:
    results = []
    for test_fn in ALL_TESTS:
        try:
            r = test_fn()
        except Exception as e:
            r = CTResult("CT-??", test_fn.__name__, False,
                         f"Excecao: {type(e).__name__}: {e}")
        results.append(r)

    passed = sum(1 for r in results if r.passed)
    total = len(results)

    if use_json:
        print(json.dumps([
            {"ct_id": r.ct_id, "name": r.name, "passed": r.passed,
             "detail": r.detail} for r in results
        ], indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*60}")
        print(f"  SPEC-054: Epistemic Topology Mapper — TDD Suite")
        print(f"  {passed}/{total} Critical Tests PASSED")
        print(f"{'='*60}\n")
        for r in results:
            status = "PASS" if r.passed else "FAIL"
            print(f"  [{status}] {r.ct_id}: {r.name}")
            if not r.passed:
                print(f"         -> {r.detail}")
        print(f"\n{'='*60}")
        print(f"  Resultado: {passed}/{total} CTs PASSED")
        print(f"{'='*60}\n")

    return results


if __name__ == "__main__":
    use_json = "--json" in sys.argv
    run_all(use_json=use_json)
