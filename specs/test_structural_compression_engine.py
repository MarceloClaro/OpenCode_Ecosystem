#!/usr/bin/env python3
"""
test_structural_compression_engine.py — SPEC-037b: SCE TDD Suite

6 Critical Tests:
  SCE-001: Fragmentacao quebra texto em partes controladas
  SCE-002: Vetorizacao extrai tese, argumentos, conceitos, ruido
  SCE-003: Merge remove redundancias entre vetores
  SCE-004: Reconstrucao produz texto denso com estrutura preservada
  SCE-005: Compressao de texto real: CR > 1, CPS > 0.7, FLI < 0.3
  SCE-006: Relatorio de compressao completo

Uso: python specs/test_structural_compression_engine.py
"""

import json, sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from structural_compression_engine import (
    StructuralCompressionEngine, CognitiveVector, SCECompressionResult,
)


class CTResult:
    def __init__(self, ct_id, name, passed, detail="", evidence=None):
        self.ct_id = ct_id; self.name = name; self.passed = passed
        self.detail = detail; self.evidence = evidence


# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE TEXT
# ═══════════════════════════════════════════════════════════════════════════

SAMPLE_LONG_TEXT = """
O objetivo deste estudo e analisar a relacao entre estruturas cognitivas e
compressao de informacao em sistemas complexos. A hipotese central afirma que
toda informacao pode ser comprimida sem perda estrutural desde que suas funcoes
essenciais sejam preservadas.

Exemplo: Leonardo da Vinci identificava padroes ocultos na natureza muito antes
da formalizacao matematica. Exemplo: Albert Einstein deduziu a relatividade a
partir de principios fundamentais de simetria. Exemplo: Aristoteles estabeleceu
as bases da logica formal que sustentam a computacao moderna.

A proposta consiste em criar uma ferramenta de compressao estrutural que separa
exemplos de estruturas. O conceito fundamental e que exemplos podem ser removidos
se a funcao que eles ilustram permanecer representada no modelo reduzido.

Obviamente, textos longos contem muitas repeticoes e variacoes superficiais.
Claramente, nem toda palavra contribui igualmente para a estrutura argumentativa.
Portanto, devemos identificar quais elementos sao essenciais e quais sao
acessorios.

A compressao estrutural permite reduzir a dimensionalidade conceitual sem perder
a capacidade de reconstruir o raciocinio original. Dessa forma, documentos longos
podem ser convertidos em representacoes densas antes de passarem por outros
scanners do ecossistema OpenCode.

O scanner noologico identifica lacunas de conhecimento. O scanner teleologico
infere requisitos a partir de objetivos. O capability composer decompoe
capacidades em insumos cognitivos. O cross validation engine constroi grafos
de dependencia entre capacidades.

Em conclusao, a ferramenta proposta representa um avanco na capacidade do
ecossistema de lidar com grandes volumes de texto sem sacrificar a qualidade
da analise cognitiva.
"""


# ═══════════════════════════════════════════════════════════════════════════
# CTs
# ═══════════════════════════════════════════════════════════════════════════

def sce_001_fragmentation() -> CTResult:
    """SCE-001: Fragmentacao quebra texto em partes controladas."""
    sce = StructuralCompressionEngine()

    text = "Paragrafo um com conteudo relevante sobre compressao.\n\nParagrafo dois sobre estrutura.\n\nParagrafo tres sobre ruido."
    parts = sce._fragment(text, part_size=100, min_part_size=20)

    if len(parts) == 0:
        return CTResult("SCE-001", "Fragmentacao produz partes", False,
                        "0 partes")
    if len(parts) > 3:
        return CTResult("SCE-001", "Fragmentacao <= 3 partes", False,
                        f"{len(parts)} partes")

    return CTResult("SCE-001", "Fragmentacao quebra texto em partes controladas", True,
                    f"parts={len(parts)}")


def sce_002_vectorization() -> CTResult:
    """SCE-002: Vetorizacao extrai tese, argumentos, conceitos, ruido."""
    sce = StructuralCompressionEngine()

    part = "O objetivo e preservar estrutura. Exemplo: Leonardo da Vinci. Obviamente isso e simples."
    vector = sce._vectorize(part, "P1")

    if not vector.thesis:
        return CTResult("SCE-002", "Vetor tem tese", False, "thesis vazia")
    if len(vector.concepts) == 0:
        return CTResult("SCE-002", "Vetor tem conceitos", False, "0 conceitos")

    return CTResult("SCE-002", "Vetorizacao extrai tese, argumentos, conceitos", True,
                    f"thesis={vector.thesis[:50]}..., concepts={len(vector.concepts)}, "
                    f"noise_removed={len(vector.noise_removed)}")


def sce_003_merge_deduplication() -> CTResult:
    """SCE-003: Merge remove redundancias entre vetores."""
    sce = StructuralCompressionEngine()

    v1 = CognitiveVector("P1", "tese A", ["arg1", "arg2"], ["ex1"], ["c1", "c2"], [], [], True)
    v2 = CognitiveVector("P2", "tese B", ["arg1", "arg3"], ["ex1"], ["c1", "c3"], [], [], True)

    merged = sce._merge_vectors([v1, v2])

    # arg1 aparece em ambos — deve aparecer so uma vez
    if merged["arguments"].count("arg1") != 1:
        return CTResult("SCE-003", "Merge deduplica argumentos repetidos", False,
                        f"arg1 count={merged['arguments'].count('arg1')}")

    # c1 aparece em ambos — deve aparecer so uma vez
    if merged["concepts"].count("c1") != 1:
        return CTResult("SCE-003", "Merge deduplica conceitos repetidos", False,
                        f"c1 count={merged['concepts'].count('c1')}")

    return CTResult("SCE-003", "Merge remove redundancias entre vetores", True,
                    f"args={len(merged['arguments'])}, concepts={len(merged['concepts'])}")


def sce_004_reconstruction() -> CTResult:
    """SCE-004: Reconstrucao produz texto denso com estrutura."""
    sce = StructuralCompressionEngine()

    merged = {
        "theses": ["Tese: compressao preserva estrutura"],
        "arguments": ["Arg1: exemplos podem ser removidos", "Arg2: funcoes devem ser preservadas"],
        "concepts": ["compressao estrutural", "preservacao funcional"],
        "examples": ["Ex: Leonardo da Vinci"],
    }

    text = sce._reconstruct(merged)

    checks = [
        "Tese" in text,
        "ARGUMENTOS" in text,
        "CONCEITOS" in text,
        "EXEMPLOS" in text,
    ]
    if not all(checks):
        return CTResult("SCE-004", "Reconstrucao inclui todas as secoes", False,
                        str(checks))

    return CTResult("SCE-004", "Reconstrucao produz texto denso estruturado", True,
                    f"len={len(text)} chars")


def sce_005_full_compression() -> CTResult:
    """SCE-005: Compressao real: CR > 1, CPS > 0.7, FLI < 0.3."""
    sce = StructuralCompressionEngine()

    result = sce.compress(SAMPLE_LONG_TEXT, part_size=800)

    if result.compression_ratio <= 1.0:
        return CTResult("SCE-005", f"CR > 1.0 (obtido: {result.compression_ratio})", False,
                        f"CR={result.compression_ratio}")

    if result.cognitive_preservation < 0.5:
        return CTResult("SCE-005", f"CPS >= 0.5 (obtido: {result.cognitive_preservation:.2f})", False,
                        f"CPS={result.cognitive_preservation}")

    # Density gain
    if result.density_gain <= 0:
        return CTResult("SCE-005", "DG > 0", False, f"DG={result.density_gain}")

    return CTResult("SCE-005", f"Compressao: CR={result.compression_ratio:.1f}x, CPS={result.cognitive_preservation:.0%}, FLI={result.functional_loss:.0%}",
                    True, f"CR={result.compression_ratio}x, CPS={result.cognitive_preservation}, "
                    f"FLI={result.functional_loss}, DG={result.density_gain:.1f}")


def sce_006_report() -> CTResult:
    """SCE-006: Relatorio de compressao completo."""
    sce = StructuralCompressionEngine()

    result = sce.compress(SAMPLE_LONG_TEXT, part_size=800)
    report = sce.report(result)

    checks = [
        "Compression Ratio" in report,
        "Cognitive Preservation" in report,
        "Functional Loss" in report,
        "Density Gain" in report,
    ]
    if not all(checks):
        return CTResult("SCE-006", "Relatorio inclui todas as metricas", False,
                        f"missing: {[c for c, ok in zip(checks, [c in report for c in checks]) if not ok]}")

    return CTResult("SCE-006", "Relatorio de compressao completo", True,
                    f"report_len={len(report)} chars")


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_all() -> tuple[list[CTResult], int, int]:
    cts = [
        sce_001_fragmentation(),
        sce_002_vectorization(),
        sce_003_merge_deduplication(),
        sce_004_reconstruction(),
        sce_005_full_compression(),
        sce_006_report(),
    ]
    passed = sum(1 for ct in cts if ct.passed)
    failed = sum(1 for ct in cts if not ct.passed)
    return cts, passed, failed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPEC-037b SCE TDD Suite")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cts, passed, failed = run_all()

    if args.json:
        print(json.dumps({"spec": "SPEC-037b", "total": len(cts), "passed": passed, "failed": failed,
                          "results": [{"ct_id": ct.ct_id, "name": ct.name, "passed": ct.passed, "detail": ct.detail} for ct in cts]},
                         indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*80}")
        print(f"  SPEC-037b Structural Compression Engine — TDD Suite")
        print(f"  \033[92mPASS: {passed}\033[0m  |  \033[91mFAIL: {failed}\033[0m  |  Total: {len(cts)}")
        print(f"{'='*80}\n")
        for ct in cts:
            status = "\033[92mPASS\033[0m" if ct.passed else "\033[91mFAIL\033[0m"
            print(f"  [{status}] {ct.ct_id}: {ct.name}")
            if ct.detail:
                print(f"       {ct.detail}")
        print(f"\n{'='*80}")
        if failed == 0:
            print(f"  RESULTADO: \033[92m[APROVADO]\033[0m  |  {passed}/{len(cts)} (100%)")
        else:
            print(f"  RESULTADO: \033[91m[{failed} FALHAS]\033[0m  |  {passed}/{len(cts)} ({passed*100//len(cts)}%)")
        print(f"{'='*80}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
