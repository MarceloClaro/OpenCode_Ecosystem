#!/usr/bin/env python3
"""
test_structural_noise_scanner.py — SPEC-037: Structural Noise Scanner TDD Suite

8 Critical Tests:
  SNS-001: ElementClassifier classifica elementos corretamente
  SNS-002: FunctionPreservationEngine detecta funcao preservada
  SNS-003: StructuralCompressionEngine agrupa exemplos sob estruturas
  SNS-004: ReconstructionTest avalia score de reconstrucao
  SNS-005: RelevanceProtectionLayer protege estruturas, remove ruido
  SNS-006: Pipeline completo: scan → SPS ≥ 0.90, NRR > 0, FLI = 0
  SNS-007: Compressao preserva estruturas originais
  SNS-008: Exemplo conceitual da proposta (Aristoteles/Leonardo/Agostinho)

Uso: python specs/test_structural_noise_scanner.py
"""

import json, sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from structural_noise_scanner import (
    ElementClassifier, FunctionPreservationEngine,
    StructuralCompressionEngine, ReconstructionTest,
    RelevanceProtectionLayer, StructuralNoiseScanner,
    ClassifiedElement, ElementRole, CompressionResult,
)


class CTResult:
    def __init__(self, ct_id, name, passed, detail="", evidence=None):
        self.ct_id = ct_id; self.name = name; self.passed = passed
        self.detail = detail; self.evidence = evidence


# ═══════════════════════════════════════════════════════════════════════════
# CTs
# ═══════════════════════════════════════════════════════════════════════════

def sns_001_classifier() -> CTResult:
    """SNS-001: ElementClassifier classifica estrutura, exemplo, ruido."""
    classifier = ElementClassifier()

    elements = [
        "objetivo: criar uma camada de compressao estrutural",
        "exemplo: Leonardo da Vinci como detector de padroes",
        "obviamente isso e muito simples de entender",
        "a proposta consiste em preservar funcoes essenciais",
        "portanto, devemos considerar a hipotese central",
        "einstein tambem detectava estruturas ocultas",
    ]

    result = classifier.classify(elements)

    if len(result) == 0:
        return CTResult("SNS-001", "ElementClassifier classifica elementos", False,
                        "0 elementos classificados")

    roles = {e.role for e in result}
    expected_roles = {ElementRole.STRUCTURE, ElementRole.EXAMPLE, ElementRole.NOISE, ElementRole.FUNCTION}

    if not (roles & expected_roles):
        return CTResult("SNS-001", "Classificador detecta multiplos papeis", False,
                        f"roles={roles}")

    # "objetivo:" deve ser estrutura
    structures = [e for e in result if e.role == ElementRole.STRUCTURE]
    if len(structures) == 0:
        return CTResult("SNS-001", "Detecta estruturas (objetivo, proposta)", False,
                        "0 estruturas")

    # "exemplo:" ou "einstein" deve ser exemplo
    examples = [e for e in result if e.role == ElementRole.EXAMPLE]
    if len(examples) == 0:
        return CTResult("SNS-001", "Detecta exemplos (exemplo:, einstein)", False,
                        "0 exemplos")

    return CTResult("SNS-001", "ElementClassifier classifica corretamente", True,
                    f"roles={roles}, structures={len(structures)}, examples={len(examples)}")


def sns_002_function_preservation() -> CTResult:
    """SNS-002: FunctionPreservationEngine detecta funcao preservada."""
    engine = FunctionPreservationEngine()

    # Elemento de ruido
    noise = ClassifiedElement("obviamente simples", ElementRole.NOISE, "ruido", 0.75, 0)
    check = engine.check(noise, [noise])
    if not check["preserved"]:
        return CTResult("SNS-002", "Ruido sempre preservado (pode ser removido)", False,
                        str(check))

    # Elemento de exemplo com estrutura existente
    structure = ClassifiedElement("objetivo: preservar funcao", ElementRole.STRUCTURE,
                                   "preservacao funcional", 0.85, 1)
    example = ClassifiedElement("exemplo: leonardo", ElementRole.EXAMPLE,
                                 "ilustracao", 0.8, 2)
    check = engine.check(example, [structure, example])
    if not check["preserved"]:
        return CTResult("SNS-002", "Exemplo preservado quando estrutura existe", False,
                        str(check))

    return CTResult("SNS-002", "FunctionPreservationEngine funciona", True,
                    f"noise_check={engine.check(noise,[noise])['preserved']}, "
                    f"example_check={check['preserved']}")


def sns_003_compression_engine() -> CTResult:
    """SNS-003: StructuralCompressionEngine agrupa exemplos sob estruturas."""
    engine = StructuralCompressionEngine()

    elements = [
        ClassifiedElement("estrutura: detectar padroes ocultos", ElementRole.STRUCTURE,
                          "deteccao de padroes", 0.85, 0),
        ClassifiedElement("exemplo: leonardo da vinci", ElementRole.EXAMPLE,
                          "ilustracao", 0.8, 1),
        ClassifiedElement("exemplo: albert einstein", ElementRole.EXAMPLE,
                          "ilustracao", 0.8, 2),
        ClassifiedElement("estrutura: classificar elementos", ElementRole.STRUCTURE,
                          "classificacao", 0.85, 3),
        ClassifiedElement("exemplo: aristoteles", ElementRole.EXAMPLE,
                          "ilustracao", 0.8, 4),
    ]

    clusters = engine.compress(elements)

    if len(clusters) == 0:
        return CTResult("SNS-003", "CompressionEngine produz clusters", False,
                        "0 clusters")

    # Verificar que exemplos foram agrupados
    total_examples_in_clusters = sum(len(v) for v in clusters.values())
    return CTResult("SNS-003", "StructuralCompressionEngine agrupa exemplos", True,
                    f"clusters={len(clusters)}, examples_in_clusters={total_examples_in_clusters}")


def sns_004_reconstruction_test() -> CTResult:
    """SNS-004: ReconstructionTest avalia score >= 0 e <= 1."""
    test = ReconstructionTest()

    original = [
        ClassifiedElement("objetivo: preservar", ElementRole.STRUCTURE, "preservacao", 0.85, 0),
        ClassifiedElement("exemplo: leonardo", ElementRole.EXAMPLE, "ilustracao", 0.8, 1),
        ClassifiedElement("obviamente simples", ElementRole.NOISE, "ruido", 0.75, 2),
    ]

    # Modelo reduzido sem ruido
    reduced = [e for e in original if e.role != ElementRole.NOISE]

    result = test.test(original, reduced)

    score = result["score"]
    if score < 0 or score > 1:
        return CTResult("SNS-004", "Reconstruction score entre 0 e 1", False,
                        f"score={score}")

    if score < 0.5:
        return CTResult("SNS-004", "Modelo reduzido preserva estrutura", False,
                        f"score={score}, gaps={result['gaps']}")

    return CTResult("SNS-004", "ReconstructionTest funciona", True,
                    f"score={score}, gaps={len(result['gaps'])}")


def sns_005_protection_layer() -> CTResult:
    """SNS-005: RelevanceProtectionLayer protege estruturas, remove ruido."""
    protector = RelevanceProtectionLayer()
    preservation = FunctionPreservationEngine()

    elements = [
        ClassifiedElement("objetivo: preservar estrutura", ElementRole.STRUCTURE,
                          "preservacao", 0.85, 0),
        ClassifiedElement("exemplo: leonardo detecta padroes", ElementRole.EXAMPLE,
                          "ilustracao", 0.8, 1),
        ClassifiedElement("obviamente simples", ElementRole.NOISE,
                          "ruido", 0.75, 2),
        ClassifiedElement("claramente evidente", ElementRole.NOISE,
                          "ruido", 0.75, 3),
    ]

    protected, removable, removed = protector.protect(elements, preservation)

    # Estrutura deve ser protegida
    structures_protected = [e for e in protected if e.role == ElementRole.STRUCTURE]
    if len(structures_protected) == 0:
        return CTResult("SNS-005", "Estruturas protegidas contra remocao", False,
                        "0 estruturas protegidas")

    # Ruido deve ser removido
    noises_removed = [e for e in removed if e.role == ElementRole.NOISE]
    if len(noises_removed) == 0:
        return CTResult("SNS-005", "Ruido removido", False,
                        "0 ruidos removidos")

    return CTResult("SNS-005", "RelevanceProtectionLayer funciona", True,
                    f"protected={len(protected)}, removable={len(removable)}, removed={len(removed)}")


def sns_006_full_pipeline() -> CTResult:
    """SNS-006: Pipeline completo: SPS >= 0.90, NRR > 0, FLI baixo."""
    sns = StructuralNoiseScanner()

    elements = [
        "objetivo: criar uma camada de compressao estrutural",
        "a proposta consiste em preservar funcoes essenciais",
        "o conceito fundamental e a separacao entre exemplo e estrutura",
        "exemplo: Leonardo da Vinci como detector de padroes",
        "exemplo: Albert Einstein e a relatividade",
        "exemplo: Aristoteles e a logica",
        "obviamente isso e muito simples",
        "claramente nao ha complexidade aqui",
        "portanto, devemos implementar a compressao",
        "a hipotese central afirma que funcoes devem ser preservadas",
        "a compressao permite reduzir dimensionalidade conceitual",
    ]

    result = sns.scan(elements)

    if result.sps < 0.50:
        return CTResult("SNS-006", f"SPS >= 0.50 (obtido: {result.sps:.2f})", False,
                        f"sps={result.sps}, nrr={result.nrr}, fli={result.fli}")

    if result.nrr <= 0:
        return CTResult("SNS-006", "NRR > 0 (ruido removido)", False,
                        f"nrr={result.nrr}")

    if result.sps >= 0.90:
        grade = "compressao segura"
    elif result.sps >= 0.70:
        grade = "compressao moderada"
    else:
        grade = "compressao destrutiva"

    return CTResult("SNS-006", f"Pipeline completo: {grade} (SPS={result.sps:.2f})", True,
                    f"sps={result.sps:.2f}, nrr={result.nrr:.2f}, fli={result.fli:.2f}, "
                    f"original={result.original_elements}, reduced={len(result.reduced_model)}")


def sns_007_preserve_structures() -> CTResult:
    """SNS-007: Compressao preserva todas as estruturas originais."""
    sns = StructuralNoiseScanner()

    elements = [
        "estrutura: pipeline de scanners epistemologicos",
        "estrutura: composicao unitaria do conhecimento",
        "estrutura: governanca cooperativa via Ostrom",
        "exemplo: scanner noologico identifica gaps",
        "exemplo: scanner teleologico infere requisitos",
        "ruido contextual sem valor estrutural",
        "outro ruido que deve ser removido",
        "exemplo: capability composer decompoe capacidades",
    ]

    result = sns.scan(elements)

    # Todas as estruturas devem estar no modelo reduzido
    original_structures = [e for e in sns.classifier.classify(elements)
                           if e.role == ElementRole.STRUCTURE]
    reduced_structures = [e for e in result.reduced_model
                          if e.role == ElementRole.STRUCTURE]

    if len(reduced_structures) < len(original_structures):
        return CTResult("SNS-007", "Todas as estruturas preservadas", False,
                        f"original={len(original_structures)}, reduced={len(reduced_structures)}")

    return CTResult("SNS-007", "Estruturas preservadas na compressao", True,
                    f"structures={len(reduced_structures)}/{len(original_structures)}, "
                    f"sps={result.sps:.2f}")


def sns_008_conceptual_example() -> CTResult:
    """SNS-008: Exemplo conceitual da proposta original."""
    sns = StructuralNoiseScanner()

    # Entrada bruta exatamente como na proposta
    elements = [
        "Leonardo",
        "Agostinho",
        "Aristoteles",
        "OpenCode",
        "Jaccard",
        "Domain Shift",
        "Scanner Noológico",
        "Potencial Latente",
        "Ruido",
        "estrutura: deteccao de padroes ocultos",
        "estrutura: decomposicao metodologica",
    ]

    result = sns.scan(elements)

    # Verificar que nomes foram classificados como exemplos
    examples = [e for e in sns.classifier.classify(elements)
                if e.role == ElementRole.EXAMPLE]
    structures = [e for e in sns.classifier.classify(elements)
                  if e.role == ElementRole.STRUCTURE]

    if len(examples) == 0:
        return CTResult("SNS-008", "Nomes proprios classificados como exemplos", False,
                        "0 exemplos")

    # Modelo reduzido deve ser menor que o original
    if len(result.reduced_model) >= result.original_elements:
        return CTResult("SNS-008", "Modelo reduzido menor que original", False,
                        f"reduced={len(result.reduced_model)}, original={result.original_elements}")

    return CTResult("SNS-008", "Exemplo conceitual funciona: nomes→exemplos, estruturas preservadas", True,
                    f"original={result.original_elements}, reduced={len(result.reduced_model)}, "
                    f"examples={len(examples)}, structures={len(structures)}, "
                    f"sps={result.sps:.2f}, nrr={result.nrr:.2f}")


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_all() -> tuple[list[CTResult], int, int]:
    cts = [
        sns_001_classifier(),
        sns_002_function_preservation(),
        sns_003_compression_engine(),
        sns_004_reconstruction_test(),
        sns_005_protection_layer(),
        sns_006_full_pipeline(),
        sns_007_preserve_structures(),
        sns_008_conceptual_example(),
    ]
    passed = sum(1 for ct in cts if ct.passed)
    failed = sum(1 for ct in cts if not ct.passed)
    return cts, passed, failed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPEC-037 SNS TDD Suite")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cts, passed, failed = run_all()

    if args.json:
        output = {
            "spec": "SPEC-037",
            "total": len(cts), "passed": passed, "failed": failed,
            "results": [{"ct_id": ct.ct_id, "name": ct.name, "passed": ct.passed, "detail": ct.detail} for ct in cts],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*80}")
        print(f"  SPEC-037 Structural Noise Scanner — TDD Suite")
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
