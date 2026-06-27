#!/usr/bin/env python3
"""
test_rupture_potential_index.py — SPEC-055: Rupture Potential Index TDD Suite

14 Critical Tests (CT) para validar RupturePotentialIndex:
  CT-RPI-001 a CT-RPI-003: Estrutura e configuracao
  CT-RPI-004 a CT-RPI-006: Calculo do RPI
  CT-RPI-007 a CT-RPI-009: Matriz decisoria EPS x RPI
  CT-RPI-010 a CT-RPI-011: Custo de Oportunidade (CO)
  CT-RPI-012 a CT-RPI-014: Portifolio e integracao

Uso:
    python specs/test_rupture_potential_index.py
    python specs/test_rupture_potential_index.py --json
"""

import json
import sys
from pathlib import Path
from typing import Any

# Add skills/system/academic-audit to path
BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from rupture_potential_index import (
    RupturePotentialIndex,
    ResearchOpportunity,
    DecisionQuadrant,
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


def make_opportunity(opp_id: str,
                     de: float = 0.5, ft: float = 0.5,
                     rr: float = 0.5, co: float = 0.5,
                     eps: float = 60.0) -> ResearchOpportunity:
    """Helper para criar ResearchOpportunity de teste."""
    return ResearchOpportunity(
        opportunity_id=opp_id,
        label=f"Oportunidade {opp_id}",
        epistemic_distance=de,
        fertility=ft,
        risk_reward=rr,
        cost_opportunity=co,
        eps_score=eps,
    )


# ─── CT Implementations ──────────────────────────────────────────────────

def ct_rpi_001_default_config() -> CTResult:
    """CT-RPI-001: RPI instancia com pesos padrao."""
    rpi = RupturePotentialIndex()
    weights = rpi.weights

    expected = {"de": 0.30, "ft": 0.25, "rr": 0.25, "co": 0.20}
    for k, v in expected.items():
        actual = weights.get(k, -1)
        if actual != v:
            return CTResult("CT-RPI-001", "Pesos padrao", False,
                            f"Peso {k}={actual}, esperado {v}")

    return CTResult("CT-RPI-001", "Pesos padrao", True,
                    f"Pesos OK: {weights}")


def ct_rpi_002_opportunity_creation() -> CTResult:
    """CT-RPI-002: ResearchOpportunity criada com atributos validos."""
    opp = make_opportunity("OP-001", de=0.8, ft=0.7, rr=0.6, co=0.3, eps=75.0)

    checks = [
        (opp.opportunity_id == "OP-001", "ID incorreto"),
        (0 <= opp.epistemic_distance <= 1, f"DE={opp.epistemic_distance}"),
        (0 <= opp.fertility <= 1, f"FT={opp.fertility}"),
        (0 <= opp.risk_reward <= 1, f"RR={opp.risk_reward}"),
        (0 <= opp.cost_opportunity <= 1, f"CO={opp.cost_opportunity}"),
        (0 <= opp.eps_score <= 100, f"EPS={opp.eps_score}"),
    ]

    for ok, msg in checks:
        if not ok:
            return CTResult("CT-RPI-002", "Criacao oportunidade", False, msg)

    return CTResult("CT-RPI-002", "Criacao oportunidade", True,
                    f"OP-001 criada: DE={opp.epistemic_distance}, FT={opp.fertility}")


def ct_rpi_003_register_opportunities() -> CTResult:
    """CT-RPI-003: Aceita e conta oportunidades de pesquisa."""
    rpi = RupturePotentialIndex()
    opps = [
        make_opportunity("OP-001"),
        make_opportunity("OP-002"),
        make_opportunity("OP-003"),
    ]
    for o in opps:
        rpi.register_opportunity(o)

    if rpi.opportunity_count() != 3:
        return CTResult("CT-RPI-003", "Registro oportunidades", False,
                        f"Esperado 3, got {rpi.opportunity_count()}")

    return CTResult("CT-RPI-003", "Registro oportunidades", True,
                    "3 oportunidades registradas")


def ct_rpi_004_rpi_calculation_high() -> CTResult:
    """CT-RPI-004: RPI alto para alta DE + FT + RR com baixo CO."""
    rpi = RupturePotentialIndex()
    opp = make_opportunity("Ruptura", de=0.9, ft=0.8, rr=0.8, co=0.1, eps=50.0)
    rpi.register_opportunity(opp)

    result = rpi.compute(opp.opportunity_id)
    rpi_score = result.get("rpi_score", -1)

    if rpi_score < 60:
        return CTResult("CT-RPI-004", "RPI alto", False,
                        f"RPI={rpi_score:.1f}, esperado >=60 para alta ruptura")

    return CTResult("CT-RPI-004", "RPI alto", True,
                    f"RPI={rpi_score:.1f} (potencial de ruptura alto)")


def ct_rpi_005_rpi_calculation_low() -> CTResult:
    """CT-RPI-005: RPI baixo para baixa DE + FT + RR com alto CO."""
    rpi = RupturePotentialIndex()
    opp = make_opportunity("Incremental", de=0.1, ft=0.2, rr=0.2, co=0.8, eps=80.0)
    rpi.register_opportunity(opp)

    result = rpi.compute(opp.opportunity_id)
    rpi_score = result.get("rpi_score", 100)

    if rpi_score > 40:
        return CTResult("CT-RPI-005", "RPI baixo", False,
                        f"RPI={rpi_score:.1f}, esperado <=40 para baixa ruptura")

    return CTResult("CT-RPI-005", "RPI baixo", True,
                    f"RPI={rpi_score:.1f} (baixo potencial de ruptura)")


def ct_rpi_006_rpi_negative_cost() -> CTResult:
    """CT-RPI-006: CO>0.5 reduz o RPI significativamente."""
    rpi = RupturePotentialIndex()

    low_co = make_opportunity("Custo baixo", de=0.6, ft=0.6, rr=0.6, co=0.1, eps=60.0)
    high_co = make_opportunity("Custo alto", de=0.6, ft=0.6, rr=0.6, co=0.9, eps=60.0)

    rpi.register_opportunity(low_co)
    rpi.register_opportunity(high_co)

    res_low = rpi.compute(low_co.opportunity_id)
    res_high = rpi.compute(high_co.opportunity_id)

    rpi_low = res_low.get("rpi_score", 0)
    rpi_high = res_high.get("rpi_score", 100)

    if rpi_low <= rpi_high:
        return CTResult("CT-RPI-006", "Penalidade CO", False,
                        f"CO baixo RPI={rpi_low:.1f} <= CO alto RPI={rpi_high:.1f}")

    return CTResult("CT-RPI-006", "Penalidade CO", True,
                    f"RPI(CO=0.1)={rpi_low:.1f} > RPI(CO=0.9)={rpi_high:.1f}")


def ct_rpi_007_quadrant_rupture_segura() -> CTResult:
    """CT-RPI-007: Quadrante 'Ruptura Segura' (EPS>=60, RPI>=60)."""
    rpi = RupturePotentialIndex()
    opp = make_opportunity("RS-1", de=0.9, ft=0.8, rr=0.8, co=0.1, eps=70.0)
    rpi.register_opportunity(opp)

    result = rpi.compute(opp.opportunity_id)
    quadrant = result.get("quadrant", "")

    if quadrant != DecisionQuadrant.RUPTURA_SEGURA.value:
        return CTResult("CT-RPI-007", "Ruptura Segura", False,
                        f"Quadrante={quadrant}, esperado={DecisionQuadrant.RUPTURA_SEGURA.value}")

    return CTResult("CT-RPI-007", "Ruptura Segura", True,
                    f"Classificado como {quadrant}")


def ct_rpi_008_quadrant_especulativo() -> CTResult:
    """CT-RPI-008: Quadrante 'Ruptura Especulativa' (EPS<60, RPI>=60)."""
    rpi = RupturePotentialIndex()
    opp = make_opportunity("RE-1", de=0.9, ft=0.8, rr=0.7, co=0.2, eps=40.0)
    rpi.register_opportunity(opp)

    result = rpi.compute(opp.opportunity_id)
    quadrant = result.get("quadrant", "")

    if quadrant != DecisionQuadrant.RUPTURA_ESPECULATIVA.value:
        return CTResult("CT-RPI-008", "Ruptura Especulativa", False,
                        f"Quadrante={quadrant}, esperado={DecisionQuadrant.RUPTURA_ESPECULATIVA.value}")

    return CTResult("CT-RPI-008", "Ruptura Especulativa", True,
                    f"Classificado como {quadrant}")


def ct_rpi_009_quadrant_incremental() -> CTResult:
    """CT-RPI-009: Quadrante 'Melhoria Incremental' (EPS>=60, RPI<60)."""
    rpi = RupturePotentialIndex()
    opp = make_opportunity("MI-1", de=0.3, ft=0.3, rr=0.3, co=0.3, eps=85.0)
    rpi.register_opportunity(opp)

    result = rpi.compute(opp.opportunity_id)
    quadrant = result.get("quadrant", "")

    if quadrant != DecisionQuadrant.MELHORIA_INCREMENTAL.value:
        return CTResult("CT-RPI-009", "Melhoria Incremental", False,
                        f"Quadrante={quadrant}, esperado={DecisionQuadrant.MELHORIA_INCREMENTAL.value}")

    return CTResult("CT-RPI-009", "Melhoria Incremental", True,
                    f"Classificado como {quadrant}")


def ct_rpi_010_cost_opportunity_high() -> CTResult:
    """CT-RPI-010: CO alto penaliza RPI mesmo com DE/FT altos."""
    rpi = RupturePotentialIndex()
    opp = make_opportunity("Alto custo", de=0.8, ft=0.8, rr=0.7, co=0.9, eps=45.0)
    rpi.register_opportunity(opp)

    result = rpi.compute(opp.opportunity_id)
    rpi_score = result.get("rpi_score", 100)

    if rpi_score > 50:
        return CTResult("CT-RPI-010", "CO alto", False,
                        f"RPI={rpi_score:.1f}, custo oportunidade 0.9 deveria reduzir abaixo de 50")

    return CTResult("CT-RPI-010", "CO alto", True,
                    f"RPI={rpi_score:.1f} (penalizado por CO=0.9)")


def ct_rpi_011_cost_opportunity_zero() -> CTResult:
    """CT-RPI-011: CO=0 nao penaliza o RPI."""
    rpi = RupturePotentialIndex()
    opp = make_opportunity("Sem custo", de=0.5, ft=0.5, rr=0.5, co=0.0, eps=50.0)
    rpi.register_opportunity(opp)

    result = rpi.compute(opp.opportunity_id)
    components = result.get("components", {})
    co_contribution = components.get("co_contribution", -999)

    if co_contribution != 0:
        return CTResult("CT-RPI-011", "CO zero", False,
                        f"Contribuicao CO={co_contribution}, esperado 0")

    return CTResult("CT-RPI-011", "CO zero", True,
                    f"CO=0 nao penaliza: contribuicao={co_contribution}")


def ct_rpi_012_portfolio_generation() -> CTResult:
    """CT-RPI-012: Gera portfolio diversificado com multiplas oportunidades."""
    rpi = RupturePotentialIndex()
    opps = [
        make_opportunity("Segura", de=0.6, ft=0.6, rr=0.6, co=0.2, eps=75.0),
        make_opportunity("Especulativa", de=0.9, ft=0.8, rr=0.7, co=0.3, eps=45.0),
        make_opportunity("Incremental", de=0.2, ft=0.3, rr=0.3, co=0.1, eps=90.0),
        make_opportunity("Rotina", de=0.1, ft=0.1, rr=0.2, co=0.8, eps=30.0),
    ]
    for o in opps:
        rpi.register_opportunity(o)

    portfolio = rpi.compute_portfolio()
    n_items = len(portfolio.get("opportunities", []))

    if n_items < 4:
        return CTResult("CT-RPI-012", "Portfolio", False,
                        f"Apenas {n_items} oportunidades no portfolio")

    # Check that we have diverse quadrants
    quadrants = set(o.get("quadrant", "") for o in portfolio["opportunities"])
    if len(quadrants) < 2:
        return CTResult("CT-RPI-012", "Portfolio", False,
                        f"Apenas {len(quadrants)} quadrantes: {quadrants}")

    return CTResult("CT-RPI-012", "Portfolio", True,
                    f"Portfolio: {n_items} oportunidades em {len(quadrants)} quadrantes: {quadrants}")


def ct_rpi_013_custom_weights() -> CTResult:
    """CT-RPI-013: Aceita pesos customizados na configuracao."""
    custom_weights = {"de": 0.40, "ft": 0.30, "rr": 0.20, "co": 0.10}
    rpi = RupturePotentialIndex(weights=custom_weights)

    for k, v in custom_weights.items():
        if rpi.weights.get(k) != v:
            return CTResult("CT-RPI-013", "Pesos custom", False,
                            f"Peso {k}={rpi.weights.get(k)}, esperado {v}")

    # Verify effect on calculation
    opp = make_opportunity("Custom test", de=1.0, ft=0.0, rr=0.0, co=0.0, eps=50.0)
    rpi.register_opportunity(opp)
    result = rpi.compute(opp.opportunity_id)
    rpi_score = result.get("rpi_score", 0)

    # With de=0.40 weight, DE=1 contributes 40 points
    if rpi_score < 30 or rpi_score > 50:
        return CTResult("CT-RPI-013", "Pesos custom", False,
                        f"RPI={rpi_score:.1f} inesperado para DE=1.0 peso=0.40")

    return CTResult("CT-RPI-013", "Pesos custom", True,
                    f"RPI={rpi_score:.1f} com pesos customizados")


def ct_rpi_014_export_portfolio() -> CTResult:
    """CT-RPI-014: Portfolio exportavel para JSON."""
    rpi = RupturePotentialIndex()
    opps = [
        make_opportunity("A", de=0.7, ft=0.6, rr=0.6, co=0.2, eps=70.0),
        make_opportunity("B", de=0.2, ft=0.3, rr=0.3, co=0.1, eps=85.0),
    ]
    for o in opps:
        rpi.register_opportunity(o)

    portfolio = rpi.compute_portfolio()

    try:
        json_str = json.dumps(portfolio, indent=2, default=str)
        parsed = json.loads(json_str)
        return CTResult("CT-RPI-014", "Export JSON", True,
                        f"JSON valido, {len(json_str)} bytes")
    except (TypeError, ValueError) as e:
        return CTResult("CT-RPI-014", "Export JSON", False, str(e))


# ─── Runner ──────────────────────────────────────────────────────────────

ALL_TESTS = [
    ct_rpi_001_default_config,
    ct_rpi_002_opportunity_creation,
    ct_rpi_003_register_opportunities,
    ct_rpi_004_rpi_calculation_high,
    ct_rpi_005_rpi_calculation_low,
    ct_rpi_006_rpi_negative_cost,
    ct_rpi_007_quadrant_rupture_segura,
    ct_rpi_008_quadrant_especulativo,
    ct_rpi_009_quadrant_incremental,
    ct_rpi_010_cost_opportunity_high,
    ct_rpi_011_cost_opportunity_zero,
    ct_rpi_012_portfolio_generation,
    ct_rpi_013_custom_weights,
    ct_rpi_014_export_portfolio,
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
        print(f"  SPEC-055: Rupture Potential Index — TDD Suite")
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
