#!/usr/bin/env python3
"""
test_noological_scanner.py — SPEC-028: Noological Scanner TDD Suite

14 Critical Tests para validar o NoologicalScanner v2.0:
  CT-NS-001: Instanciacao com dimensoes padrao (10 dims, 92 cats)
  CT-NS-002: set_domain aplica pesos para psicologia
  CT-NS-003: set_domain ignora dominio desconhecido
  CT-NS-004: scan com corpus vazio retorna coverage 0
  CT-NS-005: scan detecta categorias em corpus rico
  CT-NS-006: _category_present detecta keywords
  CT-NS-007: _category_present falha para keywords ausentes
  CT-NS-008: _identify_blind_spots_v2 ordena por density
  CT-NS-009: _cross_correlation gera 45 pares
  CT-NS-010: _grade retorna conceito A-F correto
  CT-NS-011: generate_markdown_report antes do scan = erro
  CT-NS-012: scan garante integridade (covered+absent==92)
  CT-NS-013: Keywords enriquecidas detectam teoria dos jogos
  CT-NS-014: _detect_comfort_zones identifica zonas de conforto

Uso:
    python specs/test_noological_scanner.py
    python specs/test_noological_scanner.py --json
"""

import json
import sys
import os
from pathlib import Path
from typing import Any

# Add skills/system/academic-audit to path
BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from noological_scanner import (
    NoologicalScanner,
    KnowledgeDimension,
    EPISTEMOLOGICAL_DIMENSIONS,
    DOMAIN_WEIGHTS,
    ENRICHED_KW,
)

# ─── Mock Classes ────────────────────────────────────────────────────────

class MockParagraph:
    def __init__(self, text: str):
        self.text = text


class MockAuditTrail:
    """Simula AcademicAuditTrail com paragraphs e citation_map."""

    def __init__(self, paragraphs: dict[str, str] | None = None,
                 citations: list[str] | None = None):
        self.paragraphs = {
            k: MockParagraph(v) for k, v in (paragraphs or {}).items()
        }
        self.citation_map = citations or []


class MockTextAnalyzer:
    """Simula TextAnalyzer com word_counts."""

    def __init__(self, word_counts: dict[str, int] | None = None):
        self.word_counts = word_counts or {}


# ─── Helpers ─────────────────────────────────────────────────────────────

class CTResult:
    def __init__(self, ct_id: str, name: str, passed: bool,
                 detail: str = "", evidence: Any = None):
        self.ct_id = ct_id
        self.name = name
        self.passed = passed
        self.detail = detail
        self.evidence = evidence


# ─── CT Implementations ──────────────────────────────────────────────────

def ct_ns_001_default_dimensions() -> CTResult:
    """CT-NS-001: Scanner instancia com 10 dimensoes e 92 categorias."""
    scanner = NoologicalScanner()
    dims = scanner.dimensions
    n_dims = len(dims)
    total_cats = sum(len(d.categories) for d in dims.values())

    if n_dims != 10:
        return CTResult("CT-NS-001", "10 dimensoes padrao", False,
                        f"{n_dims} dimensoes (esperado 10)")
    if total_cats != 92:
        return CTResult("CT-NS-001", "92 categorias totais", False,
                        f"{total_cats} categorias (esperado 92)")

    return CTResult("CT-NS-001", "10 dimensoes, 92 categorias", True,
                    f"{n_dims} dimensoes, {total_cats} categorias",
                    {"dims": n_dims, "cats": total_cats})


def ct_ns_002_domain_weights_psicologia() -> CTResult:
    """CT-NS-002: set_domain('psicologia') aplica pesos corretos."""
    scanner = NoologicalScanner()
    scanner.set_domain("psicologia")
    w = scanner.domain_weights

    checks = []
    if w.get("paradigmas") != 1.2:
        checks.append(f"paradigmas={w.get('paradigmas')} esperado 1.2")
    if w.get("teoria_jogos") != 0.6:
        checks.append(f"teoria_jogos={w.get('teoria_jogos')} esperado 0.6")
    if w.get("metodos") != 1.1:
        checks.append(f"metodos={w.get('metodos')} esperado 1.1")

    if checks:
        return CTResult("CT-NS-002", "Domain weights psicologia", False,
                        "; ".join(checks))

    return CTResult("CT-NS-002", "Domain weights psicologia", True,
                    f"paradigmas={w['paradigmas']}, teoria_jogos={w['teoria_jogos']}")


def ct_ns_003_unknown_domain() -> CTResult:
    """CT-NS-003: set_domain('astrologia') resulta em weights vazio, sem erro."""
    scanner = NoologicalScanner()
    try:
        scanner.set_domain("astrologia")
    except Exception as e:
        return CTResult("CT-NS-003", "Dominio desconhecido sem erro", False,
                        f"Excecao: {e}")

    if scanner.domain_weights != {}:
        return CTResult("CT-NS-003", "Domain weights vazio", False,
                        f"Weights nao vazios: {scanner.domain_weights}")

    return CTResult("CT-NS-003", "Dominio desconhecido = weights vazio", True,
                    "weights={}")


def ct_ns_004_empty_corpus() -> CTResult:
    """CT-NS-004: scan com corpus vazio retorna coverage 0 e grade F."""
    scanner = NoologicalScanner()
    # Audit trail sem paragraphs e sem citation_map
    empty_trail = MockAuditTrail()  # paragraphs vazio, citation_map vazio
    result = scanner.scan(empty_trail)

    if result["overall_density"] != 0.0:
        return CTResult("CT-NS-004", "overall_density == 0 para corpus vazio", False,
                        f"density={result['overall_density']}")
    if result["categories_covered"] != 0:
        return CTResult("CT-NS-004", "categories_covered == 0", False,
                        f"covered={result['categories_covered']}")
    if not result["completeness_grade"].startswith("F"):
        return CTResult("CT-NS-004", "completeness_grade == F", False,
                        f"grade={result['completeness_grade']}")

    return CTResult("CT-NS-004", "Corpus vazio = coverage 0, grade F", True,
                    f"density={result['overall_density']}, grade={result['completeness_grade']}")


def ct_ns_005_rich_corpus_detection() -> CTResult:
    """CT-NS-005: Corpus rico detecta categorias esperadas."""
    scanner = NoologicalScanner()
    rich_text = (
        "Estudo positivista com análise quantitativa experimental randomizada. "
        "Grupo controle e follow-up longitudinal de 6 meses. "
        "Abordagem cognitivo-comportamental (TCC) com avaliação neurobiológica. "
        "Análise dedutiva das hipóteses e pensamento automático. "
        "Resultados com significância estatística bayesiana."
    )
    trail = MockAuditTrail({"P1": rich_text, "P2": "continuacao do estudo"})
    result = scanner.scan(trail)

    paradigmas = result["dimensions"]["paradigmas"]
    metodos = result["dimensions"]["metodos"]
    teorias = result["dimensions"]["teorias"]

    checks = []
    if "Positivista" not in paradigmas["covered"]:
        checks.append("paradigmas: Positivista nao detectado")
    if "Quantitativo experimental" not in metodos["covered"]:
        checks.append("metodos: Quantitativo experimental nao detectado")
    if "Cognitivo-comportamental" not in teorias["covered"]:
        checks.append("teorias: TCC nao detectado")

    if checks:
        return CTResult("CT-NS-005", "Corpus rico detecta categorias", False,
                        "; ".join(checks),
                        {"paradigmas_covered": paradigmas["covered"],
                         "metodos_covered": metodos["covered"],
                         "teorias_covered": teorias["covered"]})

    return CTResult("CT-NS-005", "Corpus rico detecta categorias", True,
                    f"paradigmas={paradigmas['coverage_pct']}%, metodos={metodos['coverage_pct']}%, teorias={teorias['coverage_pct']}%")


def ct_ns_006_category_present_true() -> CTResult:
    """CT-NS-006: _category_present detecta keywords no corpus."""
    scanner = NoologicalScanner()
    corpus = "analise quantitativa experimental com grupo controle randomizado"
    result = scanner._category_present("Quantitativo experimental", corpus.lower(), "metodos")

    if not result:
        return CTResult("CT-NS-006", "Keyword detection positiva", False,
                        "Nao detectou 'Quantitativo experimental'")
    return CTResult("CT-NS-006", "Keyword detection positiva", True,
                    "Detectou 'experimental'+'randomiz'+'control'")


def ct_ns_007_category_present_false() -> CTResult:
    """CT-NS-007: _category_present falha para corpus sem keywords.

    NOTA: O scanner usa substring matching (ex: 'control' casa com 'controle').
    Este bug esta documentado na SPEC-028 secao 3.5 como 'Falso positivo por
    substring + negacao'. O teste usa corpus sem nenhuma substring das keywords
    para isolar o caso basico.
    """
    scanner = NoologicalScanner()
    # Corpus sem NENHUMA substring das keywords de "Quantitativo experimental":
    # keywords = ["experiment", "randomiz", "control", "ensaio clinico"]
    corpus = "analise puramente qualitativa com entrevistas abertas e observacao participante"
    result = scanner._category_present("Quantitativo experimental", corpus.lower(), "metodos")

    if result:
        return CTResult("CT-NS-007", "Keyword detection negativa", False,
                        f"Detectou falsamente em corpus sem keywords: {corpus[:80]}")
    return CTResult("CT-NS-007", "Keyword detection negativa", True,
                    "Corretamente nao detectou em corpus puramente qualitativo")


def ct_ns_008_blind_spots_ordered() -> CTResult:
    """CT-NS-008: _identify_blind_spots_v2 ordena por density crescente."""
    scanner = NoologicalScanner()
    # Mock dim_results com densidades variadas
    dim_results = {
        "dim_a": {"name": "A", "coverage_pct": 50, "density": 0.5,
                   "absent": [], "blind_spot_score": 0, "weight": 1.0},
        "dim_b": {"name": "B", "coverage_pct": 10, "density": 0.1,
                   "absent": ["x"], "blind_spot_score": 0.15, "weight": 1.0},
        "dim_c": {"name": "C", "coverage_pct": 0, "density": 0.0,
                   "absent": ["y"], "blind_spot_score": 0.25, "weight": 1.2},
    }

    spots = scanner._identify_blind_spots_v2(dim_results)

    if len(spots) < 2:
        return CTResult("CT-NS-008", "Blind spots > 2 detectados", False,
                        f"Apenas {len(spots)} spots (densidades 0.5, 0.1, 0.0)")
    if spots[0]["density"] > spots[1]["density"]:
        return CTResult("CT-NS-008", "Ordenado por density crescente", False,
                        f"Ordem errada: d0={spots[0]['density']}, d1={spots[1]['density']}")

    return CTResult("CT-NS-008", "Blind spots ordenados por density", True,
                    f"Menor density={spots[0]['density']}, maior={spots[-1]['density']}")


def ct_ns_009_cross_correlation_pairs() -> CTResult:
    """CT-NS-009: _cross_correlation gera 45 pares para 10 dimensoes."""
    scanner = NoologicalScanner()
    # Mock 10 dims com coverage_pct variado
    dim_results = {}
    for i in range(10):
        dim_results[f"dim_{i}"] = {
            "name": f"Dim {i}", "coverage_pct": i * 10, "density": i * 0.1,
            "absent": [], "weight": 1.0
        }

    pairs = scanner._cross_correlation(dim_results)

    expected = 10 * 9 // 2  # 45
    if len(pairs) != expected:
        return CTResult("CT-NS-009", f"{expected} pares de correlacao", False,
                        f"{len(pairs)} pares (esperado {expected})")

    # Verifica que a correlacao esta entre 0 e 1
    for p in pairs:
        if not (0 <= p["correlation"] <= 1):
            return CTResult("CT-NS-009", "Correlacao entre 0 e 1", False,
                            f"{p['dim1']}-{p['dim2']}: corr={p['correlation']}")

    return CTResult("CT-NS-009", "45 pares de correlacao", True,
                    f"{len(pairs)} pares, corr max={pairs[0]['correlation']}")


def ct_ns_010_grade() -> CTResult:
    """CT-NS-010: _grade retorna conceitos A-F corretos."""
    scanner = NoologicalScanner()
    test_cases = [
        (0.85, "A"), (0.75, "A"), (0.70, "A"),
        (0.65, "B"), (0.50, "B"),
        (0.45, "C"), (0.30, "C"),
        (0.25, "D"), (0.10, "D"),
        (0.05, "F"), (0.0, "F"),
    ]

    failures = []
    for density, expected_grade in test_cases:
        grade = scanner._grade(density)
        if not grade.startswith(expected_grade):
            failures.append(f"d={density}: esperado {expected_grade}, obteve {grade}")

    if failures:
        return CTResult("CT-NS-010", "Grade A-F para 11 densidades", False,
                        "; ".join(failures[:3]))

    return CTResult("CT-NS-010", "Grade A-F para 11 densidades", True,
                    "Todos os 11 casos corretos")


def ct_ns_011_report_before_scan() -> CTResult:
    """CT-NS-011: generate_markdown_report antes do scan retorna msg de erro."""
    scanner = NoologicalScanner()
    report = scanner.generate_markdown_report()

    if "Nenhum escaneamento" not in report:
        return CTResult("CT-NS-011", "Report antes do scan = aviso", False,
                        f"Retornou: {report[:100]}")

    return CTResult("CT-NS-011", "Report antes do scan = aviso", True,
                    "Mensagem correta: 'Nenhum escaneamento realizado.'")


def ct_ns_012_data_integrity() -> CTResult:
    """CT-NS-012: scan garante covered + absent = total_categories."""
    scanner = NoologicalScanner()
    trail = MockAuditTrail({"P1": "estudo experimental randomizado"})
    result = scanner.scan(trail)

    checks = []
    total_from_sum = result["categories_covered"] + result["categories_absent"]
    if total_from_sum != result["total_categories"]:
        checks.append(f"covered+absent={total_from_sum} != total={result['total_categories']}")

    for dim_key, dim_data in result["dimensions"].items():
        dim_total = len(dim_data["covered"]) + len(dim_data["absent"])
        original = EPISTEMOLOGICAL_DIMENSIONS[dim_key]
        expected_total = len(original.categories)
        if dim_total != expected_total:
            checks.append(f"{dim_key}: covered+absent={dim_total} != expected={expected_total}")

    if checks:
        return CTResult("CT-NS-012", "Integridade covered+absent==total", False,
                        "; ".join(checks[:5]))

    return CTResult("CT-NS-012", "Integridade covered+absent==total", True,
                    f"10 dims OK, total={result['total_categories']}")


def ct_ns_013_enriched_keywords() -> CTResult:
    """CT-NS-013: Keywords enriquecidas detectam teoria dos jogos via ENRICHED_KW."""
    scanner = NoologicalScanner()
    # Corpus com keywords de Equilibrio de Nash
    corpus = "O equilibrio de Nash e a estrategia dominante em jogos nao-cooperativos"
    result = scanner._category_present_v2(
        "Equilíbrio de Nash", corpus.lower(), "teoria_jogos", None
    )

    if not result:
        return CTResult("CT-NS-013", "ENRICHED_KW detecta Nash", False,
                        "Nao detectou 'Equilibrio de Nash' no corpus")

    # Tambem testa Dilema do Prisioneiro
    corpus2 = "O dilema do prisioneiro mostra que cooperacao emerge sob certos payoffs"
    result2 = scanner._category_present_v2(
        "Dilema do Prisioneiro", corpus2.lower(), "teoria_jogos", None
    )
    if not result2:
        return CTResult("CT-NS-013", "ENRICHED_KW detecta Dilema do Prisioneiro", False,
                        "Nao detectou 'Dilema do Prisioneiro'")

    return CTResult("CT-NS-013", "ENRICHED_KW detecta keywords teoria dos jogos", True,
                    "Nash e D.Prisioneiro detectados")


def ct_ns_014_comfort_zones() -> CTResult:
    """CT-NS-014: _detect_comfort_zones identifica zonas de conforto."""
    scanner = NoologicalScanner()
    # Mock: 3 dims de alta densidade, 3 de baixa
    dim_results = {
        "high_a": {"name": "Alta A", "coverage_pct": 70, "density": 0.7,
                    "absent": [], "weight": 1.0},
        "high_b": {"name": "Alta B", "coverage_pct": 85, "density": 0.85,
                    "absent": [], "weight": 1.0},
        "high_c": {"name": "Alta C", "coverage_pct": 65, "density": 0.65,
                    "absent": [], "weight": 1.0},
        "low_a": {"name": "Baixa A", "coverage_pct": 15, "density": 0.15,
                   "absent": ["x"], "weight": 1.0},
        "low_b": {"name": "Baixa B", "coverage_pct": 5, "density": 0.05,
                   "absent": ["y"], "weight": 1.0},
        "low_c": {"name": "Baixa C", "coverage_pct": 10, "density": 0.10,
                   "absent": ["z"], "weight": 1.0},
    }

    zones = scanner._detect_comfort_zones(dim_results)

    if not zones:
        return CTResult("CT-NS-014", "Comfort zones detectadas", False,
                        "Nenhuma zona detectada")

    # Cada zona deve ter os campos obrigatorios
    for z in zones:
        if "comfort_zone" not in z or "comfort_density" not in z or "neglected" not in z:
            return CTResult("CT-NS-014", "Campos obrigatorios nas zonas", False,
                            f"Zona incompleta: {z}")

    return CTResult("CT-NS-014", "Comfort zones detectadas", True,
                    f"{len(zones)} zonas, ex: {zones[0]['comfort_zone']} -> {zones[0]['neglected']}")


# ─── Runner ──────────────────────────────────────────────────────────────

CT_LIST = [
    ct_ns_001_default_dimensions,
    ct_ns_002_domain_weights_psicologia,
    ct_ns_003_unknown_domain,
    ct_ns_004_empty_corpus,
    ct_ns_005_rich_corpus_detection,
    ct_ns_006_category_present_true,
    ct_ns_007_category_present_false,
    ct_ns_008_blind_spots_ordered,
    ct_ns_009_cross_correlation_pairs,
    ct_ns_010_grade,
    ct_ns_011_report_before_scan,
    ct_ns_012_data_integrity,
    ct_ns_013_enriched_keywords,
    ct_ns_014_comfort_zones,
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
        "passed": passed,
        "failed": failed,
        "total": len(results),
        "results": [
            {"id": r.ct_id, "name": r.name, "passed": r.passed, "detail": r.detail}
            for r in results
        ],
    }


def _print_summary(results: list[CTResult], passed: int, failed: int):
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    print(f"\n{BOLD}{'=' * 80}{RESET}")
    print(f"  {BOLD}SPEC-028 Noological Scanner TDD Suite — {len(results)} Critical Tests{RESET}")
    print(f"  {GREEN}PASS: {passed}{RESET}  |  {RED}FAIL: {failed}{RESET}")
    print(f"{BOLD}{'=' * 80}{RESET}\n")

    for r in results:
        status = f"{GREEN}PASS{RESET}" if r.passed else f"{RED}FAIL{RESET}"
        print(f"  [{status}] {r.ct_id}: {r.name}")
        if r.detail:
            color = GREEN if r.passed else YELLOW
            print(f"       {color}{r.detail}{RESET}")
        if r.evidence and not r.passed:
            ev = r.evidence
            if isinstance(ev, list):
                for item in ev[:3]:
                    print(f"         - {item}")
            elif isinstance(ev, dict):
                for k, v in list(ev.items())[:5]:
                    print(f"         {k}: {v}")

    print(f"\n{BOLD}{'=' * 80}{RESET}")
    pct = (passed / len(results)) * 100 if results else 0
    verdict = f"{GREEN}[APROVADO]{RESET}" if failed == 0 else f"{RED}[{failed} FALHAS]{RESET}"
    print(f"  RESULTADO: {verdict}  |  {passed}/{len(results)} ({pct:.0f}%)")
    print(f"{BOLD}{'=' * 80}{RESET}\n")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SPEC-028 Noological Scanner TDD Suite")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    parser.add_argument("--ct", type=str, help="Executar CT específico (ex: CT-NS-001)")
    args = parser.parse_args()

    if args.ct:
        target = args.ct.upper().replace('-', '_').replace('CT_', 'ct_').replace('NS_', 'ns_')
        for ct_func in CT_LIST:
            if ct_func.__name__.startswith(target):
                r = ct_func()
                print(json.dumps({
                    "id": r.ct_id, "name": r.name, "passed": r.passed,
                    "detail": r.detail
                }, indent=2, ensure_ascii=False))
                sys.exit(0 if r.passed else 1)
        print(f"CT não encontrado: {args.ct}")
        sys.exit(2)

    result = run_all(json_out=args.json)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["failed"] == 0 else 1)
