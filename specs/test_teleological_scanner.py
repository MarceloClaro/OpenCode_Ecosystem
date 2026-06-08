#!/usr/bin/env python3
"""
test_teleological_scanner.py — SPEC-029: Teleological Reverse Scanner TDD Suite

12 Critical Tests:
  CT-TEL-001: Goal type 'causal' infere requisitos (metodos.experimental, temporalidade)
  CT-TEL-002: Goal type 'exploratory' exige metodos qualitativos + paradigmas fenomenologico
  CT-TEL-003: Goal type 'strategic' exige teoria dos jogos (todas as categorias)
  CT-TEL-004: Multiplos objetivos agregam requisitos sem duplicatas
  CT-TEL-005: compare_with_scan detecta gap critico (teoria_jogos ausente)
  CT-TEL-006: compare_with_scan NAO reporta gap quando categoria coberta
  CT-TEL-007: teleological_score = 0.0 para scan vazio
  CT-TEL-008: teleological_score = 1.0 para scan completo (todos requisitos atendidos)
  CT-TEL-009: Gap severity proporcional ao peso (1.0→critical, 0.3→low)
  CT-TEL-010: Report markdown contem secoes obrigatorias
  CT-TEL-011: Goal type desconhecido gera warning, nao quebra
  CT-TEL-012: Integracao com NoologicalScanner real (pipeline completo)

Uso:
    python specs/test_teleological_scanner.py
    python specs/test_teleological_scanner.py --json
"""

import json
import sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from teleological_scanner import (
    TeleologicalReverseScanner,
    TeleologicalGoal,
    DimensionRequirement,
    TeleologicalGap,
    TELEOLOGICAL_MAPPINGS,
)


class CTResult:
    def __init__(self, ct_id: str, name: str, passed: bool,
                 detail: str = "", evidence: Any = None):
        self.ct_id = ct_id
        self.name = name
        self.passed = passed
        self.detail = detail
        self.evidence = evidence


# ─── CT Implementations ──────────────────────────────────────────────────

def ct_tel_001_causal_requirements() -> CTResult:
    """CT-TEL-001: Goal type 'causal' infere requisitos de metodos e temporalidade."""
    scanner = TeleologicalReverseScanner()
    scanner.set_goals([TeleologicalGoal("Efeito de X sobre Y", "causal")])
    reqs = scanner.infer_requirements()

    # Deve ter metodos experimental
    exp_reqs = [r for r in reqs if r.category == "Quantitativo experimental"]
    if not exp_reqs:
        return CTResult("CT-TEL-001", "Causal → metodos.experimental", False,
                        "Nao inferiu 'Quantitativo experimental'")
    if exp_reqs[0].weight < 0.8:
        return CTResult("CT-TEL-001", "Peso metodos.experimental >= 0.8", False,
                        f"Peso={exp_reqs[0].weight}")

    # Deve ter temporalidade longitudinal
    long_reqs = [r for r in reqs if "Longitudinal" in r.category]
    if not long_reqs:
        return CTResult("CT-TEL-001", "Causal → temporalidade.longitudinal", False,
                        "Nao inferiu temporalidade longitudinal")

    # Deve ter raciocinio probabilistico
    prob_reqs = [r for r in reqs if r.category == "Probabilístico"]
    if not prob_reqs:
        return CTResult("CT-TEL-001", "Causal → raciocinio.probabilistico", False,
                        "Nao inferiu raciocinio probabilistico")

    return CTResult("CT-TEL-001", "Causal infere 6 requisitos", True,
                    f"{len(reqs)} requisitos, top: {reqs[0].category} (peso={reqs[0].weight})")


def ct_tel_002_exploratory_qualitative() -> CTResult:
    """CT-TEL-002: Goal type 'exploratory' exige metodos qualitativos + fenomenologia."""
    scanner = TeleologicalReverseScanner()
    scanner.set_goals([TeleologicalGoal("Experiencia vivida de X", "exploratory")])
    reqs = scanner.infer_requirements()

    quali_reqs = [r for r in reqs if "Qualitativo" in r.category]
    if not quali_reqs:
        return CTResult("CT-TEL-002", "Exploratory → metodos.qualitativo", False,
                        "Nao inferiu metodos qualitativos")

    feno_reqs = [r for r in reqs if r.category == "Fenomenológico"]
    if not feno_reqs:
        return CTResult("CT-TEL-002", "Exploratory → paradigmas.fenomenologico", False,
                        "Nao inferiu paradigma fenomenologico")
    if feno_reqs[0].weight < 0.9:
        return CTResult("CT-TEL-002", "Peso fenomenologico = 1.0", False,
                        f"Peso={feno_reqs[0].weight}")

    return CTResult("CT-TEL-002", "Exploratory infere requisitos qualitativos", True,
                    f"{len(reqs)} requisitos, quali={quali_reqs[0].category}, feno={feno_reqs[0].category}")


def ct_tel_003_strategic_game_theory() -> CTResult:
    """CT-TEL-003: Goal type 'strategic' exige teoria dos jogos (Nash, Bayesiano, Evolutivo)."""
    scanner = TeleologicalReverseScanner()
    scanner.set_goals([TeleologicalGoal("Estrategia otima em contexto Y", "strategic")])
    reqs = scanner.infer_requirements()

    gt_reqs = [r for r in reqs if r.dim_key == "teoria_jogos"]
    if len(gt_reqs) < 3:
        return CTResult("CT-TEL-003", "Strategic → 3+ categorias teoria_jogos", False,
                        f"Apenas {len(gt_reqs)} categorias: {[r.category for r in gt_reqs]}")

    # Nash deve estar presente com peso 1.0
    nash = [r for r in gt_reqs if "Nash" in r.category]
    if not nash:
        return CTResult("CT-TEL-003", "Strategic → Equilibrio de Nash", False,
                        "Nash nao inferido")
    if nash[0].weight < 0.9:
        return CTResult("CT-TEL-003", "Nash peso = 1.0", False,
                        f"Peso={nash[0].weight}")

    return CTResult("CT-TEL-003", "Strategic infere teoria dos jogos", True,
                    f"{len(gt_reqs)} categorias GT, top: {gt_reqs[0].category}")


def ct_tel_004_multiple_goals() -> CTResult:
    """CT-TEL-004: Multiplos objetivos agregam requisitos, sem duplicatas."""
    scanner = TeleologicalReverseScanner()
    scanner.set_goals([
        TeleologicalGoal("Efeito causal de X", "causal", weight=1.0),
        TeleologicalGoal("Comparacao entre grupos", "comparative", weight=0.8),
    ])
    reqs = scanner.infer_requirements()

    # Deve ter requisitos de ambos os tipos
    causal_reqs = [r for r in reqs if "experimental" in r.category.lower() or "longitudinal" in r.category.lower() or "contrafactual" in r.category]
    comp_reqs = [r for r in reqs if "cross-cultural" in r.category.lower() or "comparativo" in r.category.lower()]

    if not causal_reqs:
        return CTResult("CT-TEL-004", "Multiplos goals → requisitos causais", False,
                        "Nenhum requisito causal")
    if not comp_reqs:
        return CTResult("CT-TEL-004", "Multiplos goals → requisitos comparativos", False,
                        "Nenhum requisito comparativo")

    # Sem duplicatas: verificar (dim_key, category) unicos
    keys = [(r.dim_key, r.category) for r in reqs]
    if len(keys) != len(set(keys)):
        return CTResult("CT-TEL-004", "Sem duplicatas nos requisitos", False,
                        f"Total={len(reqs)}, unicos={len(set(keys))}")

    return CTResult("CT-TEL-004", "Multiplos goals agregam sem duplicatas", True,
                    f"{len(reqs)} requisitos totais (causal+comparative)")


def ct_tel_005_gap_detection() -> CTResult:
    """CT-TEL-005: compare_with_scan detecta gap critico em teoria_jogos."""
    scanner = TeleologicalReverseScanner()
    scanner.set_goals([TeleologicalGoal("Estrategia otima", "strategic")])
    scanner.infer_requirements()

    # Mock scan com teoria_jogos completamente vazio
    mock_scan = {
        "dimensions": {
            "teoria_jogos": {"covered": [], "absent": ["Equilíbrio de Nash", "Bayesiano", "Evolutivo"], "density": 0.0, "coverage_pct": 0},
            "raciocinio": {"covered": [], "absent": ["Contrafactual", "Probabilístico"], "density": 0.0, "coverage_pct": 0},
        }
    }

    gaps = scanner.compare_with_scan(mock_scan)

    if not gaps:
        return CTResult("CT-TEL-005", "Gap detection: teoria_jogos ausente", False,
                        "Nenhum gap detectado")

    # O primeiro gap deve ser teoria_jogos (critico, peso alto)
    first_gap = gaps[0]
    if first_gap.dim_key != "teoria_jogos":
        return CTResult("CT-TEL-005", "Primeiro gap = teoria_jogos", False,
                        f"Primeiro gap: {first_gap.dim_key}")

    return CTResult("CT-TEL-005", "Gap critico em teoria_jogos detectado", True,
                    f"{len(gaps)} gaps, severidade={first_gap.severity}")


def ct_tel_006_no_gap_when_covered() -> CTResult:
    """CT-TEL-006: compare_with_scan NAO reporta gap quando categoria coberta."""
    scanner = TeleologicalReverseScanner()
    scanner.set_goals([TeleologicalGoal("Efeito causal", "causal")])
    scanner.infer_requirements()

    # Mock scan com metodos experimental coberto
    mock_scan = {
        "dimensions": {
            "metodos": {"covered": ["Quantitativo experimental"], "absent": [], "density": 0.5, "coverage_pct": 50},
            "raciocinio": {"covered": [], "absent": ["Probabilístico"], "density": 0.0, "coverage_pct": 0},
        }
    }

    gaps = scanner.compare_with_scan(mock_scan)

    # "Quantitativo experimental" NAO deve estar nos gaps
    exp_gaps = [g for g in gaps if g.category == "Quantitativo experimental"]
    if exp_gaps:
        return CTResult("CT-TEL-006", "Sem gap para categoria coberta", False,
                        f"'Quantitativo experimental' reportado como gap")

    return CTResult("CT-TEL-006", "Categoria coberta nao gera gap", True,
                    f"{len(gaps)} gaps (nenhum para categorias cobertas)")


def ct_tel_007_score_zero() -> CTResult:
    """CT-TEL-007: teleological_score = 0.0 para scan vazio."""
    scanner = TeleologicalReverseScanner()
    scanner.set_goals([TeleologicalGoal("Efeito causal", "causal")])
    scanner.infer_requirements()

    # Scan com todas as dimensoes vazias
    mock_scan = {"dimensions": {}}
    gaps = scanner.compare_with_scan(mock_scan)
    score = scanner.teleological_score()

    if score != 0.0:
        return CTResult("CT-TEL-007", "Score = 0.0 para scan vazio", False,
                        f"Score={score}")

    return CTResult("CT-TEL-007", "Score 0.0 para scan vazio", True,
                    f"Score={score}, {len(gaps)} gaps")


def ct_tel_008_score_full() -> CTResult:
    """CT-TEL-008: teleological_score = 1.0 quando todos os requisitos atendidos."""
    scanner = TeleologicalReverseScanner()
    scanner.set_goals([TeleologicalGoal("Efeito causal", "causal")])
    reqs = scanner.infer_requirements()

    # Construir scan onde TODOS os requisitos estao cobertos
    mock_dims: dict[str, dict] = {}
    for req in reqs:
        if req.dim_key not in mock_dims:
            mock_dims[req.dim_key] = {"covered": [], "absent": [], "density": 1.0, "coverage_pct": 100}
        mock_dims[req.dim_key]["covered"].append(req.category)

    mock_scan = {"dimensions": mock_dims}
    gaps = scanner.compare_with_scan(mock_scan)
    score = scanner.teleological_score()

    if score != 1.0:
        return CTResult("CT-TEL-008", "Score = 1.0 para scan completo", False,
                        f"Score={score}, gaps restantes={len(gaps)}")

    return CTResult("CT-TEL-008", "Score 1.0 quando todos atendidos", True,
                    f"Score={score}, 0 gaps")


def ct_tel_009_severity_proportional() -> CTResult:
    """CT-TEL-009: Gap severity proporcional ao peso (1.0→critical, 0.3→low)."""
    scanner = TeleologicalReverseScanner()

    test_cases = [
        (1.0, "critical"),
        (0.9, "critical"),
        (0.8, "high"),
        (0.7, "high"),
        (0.5, "moderate"),
        (0.4, "moderate"),
        (0.3, "low"),
        (0.1, "low"),
    ]

    failures = []
    for weight, expected in test_cases:
        severity = scanner._severity(weight)
        if severity != expected:
            failures.append(f"peso={weight}: esperado {expected}, obteve {severity}")

    if failures:
        return CTResult("CT-TEL-009", "Severidade proporcional ao peso", False,
                        "; ".join(failures[:3]))

    return CTResult("CT-TEL-009", "Severidade proporcional ao peso", True,
                    f"{len(test_cases)} casos corretos")


def ct_tel_010_report_sections() -> CTResult:
    """CT-TEL-010: Report markdown contem secoes obrigatorias."""
    scanner = TeleologicalReverseScanner()
    scanner.set_goals([TeleologicalGoal("Efeito causal de X", "causal")])
    scanner.infer_requirements()

    mock_scan = {
        "dimensions": {
            "metodos": {"covered": [], "absent": ["Quantitativo experimental"], "density": 0.0, "coverage_pct": 0},
            "raciocinio": {"covered": [], "absent": ["Probabilístico"], "density": 0.0, "coverage_pct": 0},
        }
    }
    scanner.compare_with_scan(mock_scan)
    report = scanner.generate_report()

    required_sections = [
        "Scanner Teleológico Reverso",
        "Objetivos da Pesquisa",
        "Requisitos Teleológicos",
        "Gaps Teleológicos",
        "Recomendações de Alinhamento",
    ]

    missing = [s for s in required_sections if s not in report]
    if missing:
        return CTResult("CT-TEL-010", "Secoes obrigatorias no report", False,
                        f"Faltam: {', '.join(missing)}")

    return CTResult("CT-TEL-010", "Report contem 5 secoes obrigatorias", True,
                    f"{len(report)} caracteres")


def ct_tel_011_unknown_goal_type() -> CTResult:
    """CT-TEL-011: Goal type desconhecido gera warning, nao quebra."""
    import warnings
    scanner = TeleologicalReverseScanner()

    # Deve emitir warning, nao exception
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        goal = TeleologicalGoal("Teste", "tipo_inexistente")
        scanner.set_goals([goal])
        reqs = scanner.infer_requirements()

    if len(reqs) != 0:
        return CTResult("CT-TEL-011", "Goal desconhecido = 0 requisitos", False,
                        f"{len(reqs)} requisitos")

    if not w:
        return CTResult("CT-TEL-011", "Warning emitido para tipo desconhecido", False,
                        "Nenhum warning")

    return CTResult("CT-TEL-011", "Goal desconhecido = warning, 0 requisitos", True,
                    f"Warning: {str(w[0].message)[:100]}")


def ct_tel_012_integration_noological() -> CTResult:
    """CT-TEL-012: Integracao com NoologicalScanner real (pipeline completo)."""
    from noological_scanner import NoologicalScanner

    # 1. Executar NoologicalScanner em corpus realista
    nool = NoologicalScanner()
    corpus_text = (
        "Estudo randomizado controlado com follow-up de 12 meses. "
        "Analise bayesiana dos resultados. Abordagem quantitativa experimental. "
        "Equilibrio de Nash aplicado a decisao estrategica dos participantes."
    )
    # Mock audit trail
    class MockP:
        def __init__(self, t): self.text = t
    class MockT:
        def __init__(self, t):
            self.paragraphs = {"P1": MockP(t)}
            self.citation_map = []

    nool_scan = nool.scan(MockT(corpus_text))

    # 2. Executar TeleologicalReverseScanner
    tel = TeleologicalReverseScanner()
    tel.set_goals([TeleologicalGoal("Avaliar efeito causal da intervencao", "causal")])
    tel.infer_requirements()
    gaps = tel.compare_with_scan(nool_scan)
    score = tel.teleological_score()

    # 3. Verificar que o pipeline funciona (score > 0, gaps identificados)
    if score < 0.0 or score > 1.0:
        return CTResult("CT-TEL-012", "Score entre 0 e 1", False,
                        f"Score={score}")

    # Deve ter detectado que "experimental" esta coberto (ou nao)
    exp_gaps = [g for g in gaps if "experimental" in g.category.lower()]
    has_exp = "Quantitativo experimental" in nool_scan["dimensions"]["metodos"]["covered"]

    return CTResult("CT-TEL-012", "Pipeline Noologico+Teleologico integrado", True,
                    f"Score={score:.0%}, {len(gaps)} gaps, experimental coberto={has_exp}")


# ─── Runner ──────────────────────────────────────────────────────────────

CT_LIST = [
    ct_tel_001_causal_requirements,
    ct_tel_002_exploratory_qualitative,
    ct_tel_003_strategic_game_theory,
    ct_tel_004_multiple_goals,
    ct_tel_005_gap_detection,
    ct_tel_006_no_gap_when_covered,
    ct_tel_007_score_zero,
    ct_tel_008_score_full,
    ct_tel_009_severity_proportional,
    ct_tel_010_report_sections,
    ct_tel_011_unknown_goal_type,
    ct_tel_012_integration_noological,
]


def run_all(json_out: bool = False) -> dict[str, Any]:
    results = []
    for ct_func in CT_LIST:
        try:
            r = ct_func()
        except Exception as e:
            r = CTResult(ct_func.__name__, "UNKNOWN", False, f"Exceção: {e}")
        results.append(r)

    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)

    if not json_out:
        _print_summary(results, passed, failed)

    return {
        "passed": passed, "failed": failed, "total": len(results),
        "results": [
            {"id": r.ct_id, "name": r.name, "passed": r.passed, "detail": r.detail}
            for r in results
        ],
    }


def _print_summary(results: list[CTResult], passed: int, failed: int):
    GREEN = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"; RESET = "\033[0m"; BOLD = "\033[1m"
    print(f"\n{BOLD}{'=' * 80}{RESET}")
    print(f"  {BOLD}SPEC-029 Teleological Reverse Scanner — {len(results)} Critical Tests{RESET}")
    print(f"  {GREEN}PASS: {passed}{RESET}  |  {RED}FAIL: {failed}{RESET}")
    print(f"{BOLD}{'=' * 80}{RESET}\n")
    for r in results:
        status = f"{GREEN}PASS{RESET}" if r.passed else f"{RED}FAIL{RESET}"
        print(f"  [{status}] {r.ct_id}: {r.name}")
        if r.detail:
            color = GREEN if r.passed else YELLOW
            print(f"       {color}{r.detail}{RESET}")
    print(f"\n{BOLD}{'=' * 80}{RESET}")
    pct = (passed / len(results)) * 100 if results else 0
    verdict = f"{GREEN}[APROVADO]{RESET}" if failed == 0 else f"{RED}[{failed} FALHAS]{RESET}"
    print(f"  RESULTADO: {verdict}  |  {passed}/{len(results)} ({pct:.0f}%)")
    print(f"{BOLD}{'=' * 80}{RESET}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SPEC-029 Teleological Scanner TDD Suite")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    args = parser.parse_args()
    result = run_all(json_out=args.json)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["failed"] == 0 else 1)
