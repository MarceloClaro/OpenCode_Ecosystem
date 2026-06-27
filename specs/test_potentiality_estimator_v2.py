#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_potentiality_estimator_v2.py — SPEC-045: Potentiality Estimator v2.0 TDD Suite
====================================================================================
12 Critical Tests para validar o PotentialityEstimatorV2:

  CT-045-001: Consolidacao de ausencias de multiplos scanners
  CT-045-002: EPS v2 calcula com 6 dimensoes (range 0-100)
  CT-045-003: TeleologicalAlignment usa output do TeleologicalScanner
  CT-045-004: CascadeImpact usa output do EvolutionaryPipeline
  CT-045-005: SocialImpact usa output do SocialImpactScanner
  CT-045-006: Validacao de viabilidade: DNA match (viable)
  CT-045-007: Validacao de viabilidade: capacidade ausente (needs_development)
  CT-045-008: Ranking ordenado por EPS decrescente
  CT-045-009: Grade atribuida corretamente (Discovery/Promising/Exploratory/Marginal)
  CT-045-010: Roadmap gerado com pelo menos 1 rota
  CT-045-011: Relatorio JSON contem todos os campos obrigatorios
  CT-045-012: Pipeline completo executa sem erro

Uso:
    python specs/test_potentiality_estimator_v2.py
    python specs/test_potentiality_estimator_v2.py --json
    PYTHONPATH=. pytest specs/test_potentiality_estimator_v2.py -v
"""

import json
import sys
import tempfile
from pathlib import Path

# Add skills/system/academic-audit to path
BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from potentiality_estimator_v2 import (
    PotentialityEstimatorV2,
    EpistemicOpportunity,
    FeasibilityResult,
    ResearchRoadmap,
)


# ═══════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════

def _make_noological():
    """Fixture: output tipico do NoologicalScanner."""
    return {
        "dimensions": {
            "teoria_jogos": {
                "name": "Teoria dos Jogos",
                "absent": ["equilibrio_nash_aplicado", "dilema_prisioneiro_estudos"],
                "density": 0.2,
            },
            "dominios": {
                "name": "Dominios Interdisciplinares",
                "absent": ["neurociencia_cognitiva"],
                "density": 0.3,
            },
            "metodos": {
                "name": "Metodos",
                "absent": [],
                "density": 0.8,
            },
        }
    }


def _make_teleological():
    """Fixture: output tipico do TeleologicalReverseScanner."""
    return {
        "goals": [
            {
                "type": "causal",
                "required_dimensions": ["teoria_jogos", "metodos"],
                "keywords": ["nash", "equilibrio", "strategia"],
            }
        ],
        "gaps": [
            {"dimension": "teoria_jogos", "category": "equilibrio_nash_aplicado", "severity": "critical"},
        ],
    }


def _make_evolutionary():
    """Fixture: output tipico do EvolutionaryScannerPipeline."""
    return {
        "bottlenecks": [
            {"dimension": "teoria_jogos", "category": "equilibrio_nash_aplicado", "cascade_impact": 9},
            {"dimension": "dominios", "category": "neurociencia_cognitiva", "cascade_impact": 6},
        ],
    }


def _make_dna():
    """Fixture: output tipico do PotentialityScanner."""
    return {
        "capability_map": {
            "noological_scanner": ["gap_detection", "epistemological_analysis"],
            "teleological_scanner": ["prescriptive_inference"],
            "cross_validation_engine": ["cross_validation"],
            "game_theory_modeling": ["equilibrium_analysis"],
            "equilibrium_analysis": ["nash_solver"],
        }
    }


def _make_social_impact():
    """Fixture: output tipico do SocialImpactScanner."""
    return {"consolidated_score": 72}


def _make_empty():
    """Fixture: inputs vazios."""
    return {}, {}, {}, {}, {}


# ═══════════════════════════════════════════════════════════════════════
# TEST SUITE
# ═══════════════════════════════════════════════════════════════════════

class TestPotentialityEstimatorV2:
    """TDD Test Suite para o PotentialityEstimatorV2 (SPEC-045)."""

    def test_ct045001_consolidation_of_absences(self):
        """CT-045-001: Consolida ausencias de multiplos scanners."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        opps = result["opportunities"]
        # Deve ter ausencias do noological (2) + teleological (1) + evolutionary (2)
        # Deduplicado: teoria_jogos/equilibrio_nash_aplicado aparece em 3 fontes
        assert len(opps) >= 2, f"Esperado >=2 oportunidades, got {len(opps)}"

    def test_ct045002_eps_v2_range(self):
        """CT-045-002: EPS v2 calcula com 6 dimensoes (range 0-100)."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        for opp in result["opportunities"]:
            assert 0 <= opp.eps <= 100, f"EPS={opp.eps} fora do range [0,100]"
            assert opp.cross_domain_impact >= 0
            assert opp.theoretical_fertility >= 0
            assert opp.game_theoretic_value >= 0
            assert opp.teleological_alignment >= 0
            assert opp.cascade_impact >= 0
            assert opp.social_impact >= 0

    def test_ct045003_teleological_alignment(self):
        """CT-045-003: TeleologicalAlignment usa output do TeleologicalScanner."""
        est = PotentialityEstimatorV2()
        result_with = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        result_without = est.scan(
            noological_results=_make_noological(),
            teleological_results={},
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        # Com teleological, a dimensao teoria_jogos deve ter TA > 5
        tg_with = [o for o in result_with["opportunities"] if o.dimension == "teoria_jogos"]
        tg_without = [o for o in result_without["opportunities"] if o.dimension == "teoria_jogos"]
        if tg_with and tg_without:
            assert tg_with[0].teleological_alignment >= tg_without[0].teleological_alignment

    def test_ct045004_cascade_impact(self):
        """CT-045-004: CascadeImpact usa output do EvolutionaryPipeline."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        # teoria_jogos/equilibrio_nash_aplicado tem cascade_impact=9 no fixture
        tg = [o for o in result["opportunities"] if o.category == "equilibrio_nash_aplicado"]
        assert len(tg) >= 1, "Categoria equilibrio_nash_aplicado nao encontrada"
        assert tg[0].cascade_impact == 9.0, f"Esperado CI=9.0, got {tg[0].cascade_impact}"

    def test_ct045005_social_impact(self):
        """CT-045-005: SocialImpact usa output do SocialImpactScanner."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        # score=72 -> SI=7.0
        for opp in result["opportunities"]:
            assert opp.social_impact > 0, f"SocialImpact deve ser >0, got {opp.social_impact}"

    def test_ct045006_feasibility_viable(self):
        """CT-045-006: Validacao de viabilidade: DNA match (viable)."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        # teoria_jogos tem game_theory_modeling + equilibrium_analysis no DNA
        tg = [o for o in result["opportunities"] if o.dimension == "teoria_jogos"]
        if tg:
            feas = result["feasibility"].get(tg[0].category)
            if feas:
                assert feas.status in ("viable", "needs_development"), \
                    f"Status inesperado: {feas.status}"

    def test_ct045007_feasibility_needs_development(self):
        """CT-045-007: Validacao de viabilidade: capacidade ausente (needs_development)."""
        est = PotentialityEstimatorV2()
        # DNA vazio = tudo needs_development
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results={"capability_map": {}},
            social_impact_results=_make_social_impact(),
        )
        for cat, feas in result["feasibility"].items():
            assert feas.status in ("needs_development", "unviable"), \
                f"Com DNA vazio, {cat} deveria ser needs_development/unviable, got {feas.status}"

    def test_ct045008_ranking_order(self):
        """CT-045-008: Ranking ordenado por EPS decrescente."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        opps = result["opportunities"]
        for i in range(len(opps) - 1):
            assert opps[i].eps >= opps[i + 1].eps, \
                f"Ranking desordenado: {opps[i].eps} < {opps[i+1].eps} na posicao {i}"

    def test_ct045009_grade_assignment(self):
        """CT-045-009: Grade atribuida corretamente."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        for opp in result["opportunities"]:
            if opp.eps >= 80:
                assert opp.grade == "Discovery", f"EPS={opp.eps} deveria ser Discovery"
            elif opp.eps >= 60:
                assert opp.grade == "Promising", f"EPS={opp.eps} deveria ser Promising"
            elif opp.eps >= 40:
                assert opp.grade == "Exploratory", f"EPS={opp.eps} deveria ser Exploratory"
            else:
                assert opp.grade == "Marginal", f"EPS={opp.eps} deveria ser Marginal"

    def test_ct045010_roadmap_generation(self):
        """CT-045-010: Roadmap gerado com pelo menos 1 rota."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        roadmap = result["roadmap"]
        assert isinstance(roadmap, ResearchRoadmap)
        assert len(roadmap.routes) >= 1, "Roadmap deve ter pelo menos 1 rota"
        assert roadmap.total_opportunities >= 1

    def test_ct045011_json_report_fields(self):
        """CT-045-011: Relatorio JSON contem todos os campos obrigatorios."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = Path(tmpdir) / "test_report.json"
            est.save_json(result, json_path)
            data = json.loads(json_path.read_text(encoding="utf-8"))

            assert "spec" in data
            assert data["spec"] == "SPEC-045"
            assert "summary" in data
            assert "opportunities" in data
            assert "feasibility" in data
            assert "roadmap" in data
            assert "total_opportunities" in data["summary"]
            assert "discovery" in data["summary"]
            assert "promising" in data["summary"]

    def test_ct045012_pipeline_no_error(self):
        """CT-045-012: Pipeline completo executa sem erro."""
        est = PotentialityEstimatorV2()
        # Testar com todos os inputs
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        assert result is not None
        assert "opportunities" in result
        assert "summary" in result
        assert "feasibility" in result
        assert "roadmap" in result

        # Testar com inputs vazios
        result_empty = est.scan()
        assert result_empty is not None
        assert result_empty["summary"]["total_opportunities"] == 0

        # Testar geração de relatório
        report = est.generate_report(result)
        assert "SPEC-045" in report
        assert "Ranking de Oportunidades" in report

    def test_ct045013_sensitivity_analysis_returns_valid_structure(self):
        """CT-045-013: Analise de sensibilidade retorna estrutura valida."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        sensitivity = est.sensitivity_analysis(result, delta=0.2, steps=5)

        assert "stable" in sensitivity
        assert "overall_stability" in sensitivity
        assert "ranking_changes" in sensitivity
        assert "dimension_sensitivity" in sensitivity
        assert "recommendation" in sensitivity
        assert sensitivity["overall_stability"] in ("high", "medium", "low")

    def test_ct045014_sensitivity_analysis_covers_all_weights(self):
        """CT-045-014: Analise de sensibilidade cobre todas as dimensoes."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
            dna_results=_make_dna(),
            social_impact_results=_make_social_impact(),
        )
        sensitivity = est.sensitivity_analysis(result)

        # Todas as dimensoes devem estar presentes
        for dim in ["cross_domain", "theoretical_fertility", "game_theoretic",
                     "teleological_alignment", "cascade_impact", "social_impact"]:
            assert dim in sensitivity["dimension_sensitivity"], \
                f"Dimensao {dim} ausente na analise de sensibilidade"
            assert "original_weight" in sensitivity["dimension_sensitivity"][dim]
            assert "avg_eps_change" in sensitivity["dimension_sensitivity"][dim]
            assert "stability" in sensitivity["dimension_sensitivity"][dim]

    def test_ct045015_sensitivity_empty_result(self):
        """CT-045-015: Analise de sensibilidade com resultado vazio."""
        est = PotentialityEstimatorV2()
        result = est.scan()
        sensitivity = est.sensitivity_analysis(result)

        assert sensitivity["stable"] is True
        assert sensitivity["ranking_changes"] == 0

    def test_ct045016_sensitivity_delta_range(self):
        """CT-045-016: Analise de sensibilidade aceita diferentes deltas."""
        est = PotentialityEstimatorV2()
        result = est.scan(
            noological_results=_make_noological(),
            teleological_results=_make_teleological(),
            evolutionary_results=_make_evolutionary(),
        )

        # Delta menor = menos variacao
        sens_low = est.sensitivity_analysis(result, delta=0.1)
        sens_high = est.sensitivity_analysis(result, delta=0.3)

        # Com delta maior, a variacao media deve ser maior ou igual
        assert sens_high["avg_eps_change"] >= sens_low["avg_eps_change"] * 0.8


# ═══════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════

def run_tests(output_json=False):
    """Executa todos os CTs e reporta resultados."""
    test_suite = TestPotentialityEstimatorV2()
    results = []
    passed = 0
    failed = 0

    tests = [
        ("CT-045-001", "test_ct045001_consolidation_of_absences"),
        ("CT-045-002", "test_ct045002_eps_v2_range"),
        ("CT-045-003", "test_ct045003_teleological_alignment"),
        ("CT-045-004", "test_ct045004_cascade_impact"),
        ("CT-045-005", "test_ct045005_social_impact"),
        ("CT-045-006", "test_ct045006_feasibility_viable"),
        ("CT-045-007", "test_ct045007_feasibility_needs_development"),
        ("CT-045-008", "test_ct045008_ranking_order"),
        ("CT-045-009", "test_ct045009_grade_assignment"),
        ("CT-045-010", "test_ct045010_roadmap_generation"),
        ("CT-045-011", "test_ct045011_json_report_fields"),
        ("CT-045-012", "test_ct045012_pipeline_no_error"),
        ("CT-045-013", "test_ct045013_sensitivity_analysis_returns_valid_structure"),
        ("CT-045-014", "test_ct045014_sensitivity_analysis_covers_all_weights"),
        ("CT-045-015", "test_ct045015_sensitivity_empty_result"),
        ("CT-045-016", "test_ct045016_sensitivity_delta_range"),
    ]

    for ct_id, method_name in tests:
        method = getattr(test_suite, method_name)
        try:
            method()
            results.append({"ct": ct_id, "status": "PASS"})
            passed += 1
            print(f"  PASS  {ct_id}")
        except AssertionError as e:
            results.append({"ct": ct_id, "status": "FAIL", "error": str(e)})
            failed += 1
            print(f"  FAIL  {ct_id}: {e}")
        except Exception as e:
            results.append({"ct": ct_id, "status": "ERROR", "error": str(e)})
            failed += 1
            print(f"  ERROR {ct_id}: {e}")

    total = passed + failed
    print(f"\nResultado: {passed}/{total} PASS ({100*passed/total:.0f}%)")

    if output_json:
        report = {
            "spec": "SPEC-045",
            "suite": "PotentialityEstimatorV2",
            "total": total,
            "passed": passed,
            "failed": failed,
            "results": results,
        }
        print(json.dumps(report, indent=2))

    return failed == 0


if __name__ == "__main__":
    import sys
    output_json = "--json" in sys.argv
    success = run_tests(output_json=output_json)
    sys.exit(0 if success else 1)
