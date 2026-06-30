#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TDD Test Suite for SPEC-056: Cognitive Diversity Expansion (R27)
===============================================================
12 Casos de Teste (CTs) — pytest

Autor: OpenCode Ecosystem (2026) — R27: TDD
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "system" / "academic-audit"))

from cognitive_diversity_injector import (
    DiversityArtifact,
    inject_diversity_artifacts,
    artifacts_to_noological_format,
    generate_cognitive_diversity_report,
)


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-01: Injetor gera 8 artefatos
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_01_eight_artifacts():
    """CT-056-01: Injetor gera 8 artefatos de diversidade."""
    artifacts = inject_diversity_artifacts()
    assert len(artifacts) == 8, f"Esperado 8, obtido {len(artifacts)}"


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-02: Cada artefato tem ID único
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_02_unique_ids():
    """CT-056-02: Cada artefato tem ID único."""
    artifacts = inject_diversity_artifacts()
    ids = [a.artifact_id for a in artifacts]
    assert len(ids) == len(set(ids)), "IDs duplicados detectados"


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-03: Cobre 5+ paradigmas distintos
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_03_five_paradigms():
    """CT-056-03: Artefatos cobrem 5+ paradigmas epistemológicos distintos."""
    artifacts = inject_diversity_artifacts()
    paradigms = set(a.paradigm for a in artifacts)
    assert len(paradigms) >= 5, f"Esperado >=5 paradigmas, obtido {len(paradigms)}: {paradigms}"


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-04: Cobre 4+ domínios cruzados
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_04_four_domains():
    """CT-056-04: Artefatos cobrem 4+ domínios de conhecimento."""
    artifacts = inject_diversity_artifacts()
    domains = set(a.domain for a in artifacts)
    assert len(domains) >= 4, f"Esperado >=4 dominios, obtido {len(domains)}: {domains}"


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-05: 4+ artefatos com game theory
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_05_four_gt_artifacts():
    """CT-056-05: Pelo menos 4 artefatos referenciam teoria dos jogos."""
    artifacts = inject_diversity_artifacts()
    gt_artifacts = [a for a in artifacts if a.game_theory is not None]
    assert len(gt_artifacts) >= 4, f"Esperado >=4 com GT, obtido {len(gt_artifacts)}"


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-06: Vetor de cobertura com 10 dimensões
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_06_ten_dimensions():
    """CT-056-06: Cada artefato tem vetor de cobertura de 10 dimensões."""
    artifacts = inject_diversity_artifacts()
    for art in artifacts:
        assert len(art.coverage_vector) == 10, (
            f"Artefato {art.artifact_id} tem {len(art.coverage_vector)} dimensões"
        )


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-07: Conversão para formato noológico
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_07_noological_conversion():
    """CT-056-07: Conversão para formato do Scanner Noológico."""
    artifacts = inject_diversity_artifacts()
    entries = artifacts_to_noological_format(artifacts)
    assert len(entries) == len(artifacts)
    for entry in entries:
        assert "artifact_id" in entry
        assert "dimensions" in entry
        assert "coverage_vector" in entry
        assert "paradigma" in entry["dimensions"]
        assert "metodo" in entry["dimensions"]


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-08: Relatório textual gerado
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_08_report_generated():
    """CT-056-08: Relatório textual é gerado corretamente."""
    artifacts = inject_diversity_artifacts()
    report = generate_cognitive_diversity_report(artifacts)
    assert "RELATÓRIO DE INJEÇÃO DE DIVERSIDADE COGNITIVA" in report
    assert "Total de artefatos: 8" in report
    assert "Impacto esperado" in report
    assert "Índice de Homogeneidade" in report


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-09: Campos obrigatórios do DiversityArtifact
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_09_artifact_fields():
    """CT-056-09: Todos os artefatos têm campos obrigatórios preenchidos."""
    artifacts = inject_diversity_artifacts()
    for art in artifacts:
        assert art.title, f"Artefato {art.artifact_id} sem título"
        assert art.description, f"Artefato {art.artifact_id} sem descrição"
        assert art.paradigm, f"Artefato {art.artifact_id} sem paradigma"
        assert len(art.description) > 50, f"Descrição muito curta em {art.artifact_id}"


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-10: Raciocínio distinto entre artefatos
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_10_reasoning_diversity():
    """CT-056-10: Pelo menos 4 tipos de raciocínio diferentes entre os artefatos."""
    artifacts = inject_diversity_artifacts()
    all_reasoning = set()
    for art in artifacts:
        all_reasoning.update(art.reasoning_types)
    assert len(all_reasoning) >= 4, f"Esperado >=4 tipos, obtido {len(all_reasoning)}"


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-11: Métodos variados
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_11_method_diversity():
    """CT-056-11: Pelo menos 4 métodos de investigação distintos."""
    artifacts = inject_diversity_artifacts()
    methods = set(a.method for a in artifacts)
    assert len(methods) >= 4, f"Esperado >=4 metodos, obtido {len(methods)}: {methods}"


# ═══════════════════════════════════════════════════════════════════════════
# CT-056-12: Níveis de análise variados
# ═══════════════════════════════════════════════════════════════════════════

def test_ct_056_12_analysis_level_diversity():
    """CT-056-12: Pelo menos 4 níveis de análise distintos."""
    artifacts = inject_diversity_artifacts()
    levels = set(a.level_of_analysis for a in artifacts)
    assert len(levels) >= 4, f"Esperado >=4 niveis, obtido {len(levels)}: {levels}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
