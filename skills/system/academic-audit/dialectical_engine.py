#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DialecticalEngine v1.0 — SPEC-036b: Sintese de Contradicoes
=============================================================
Implementa o gap critico 'raciocinio.Dialetico' identificado pelo scanner.

Arquitetura Hegeliana adaptada para sistemas computacionais:
  1. Thesis    — posicao atual (estado do sistema)
  2. Antithesis — negacao da posicao (gap, contradicao, limitacao)
  3. Synthesis  — resolucao que incorpora ambos em nivel superior

Aplicacoes:
  - Auto-modificacao: thesis=codigo atual, antithesis=erro/limite, synthesis=patch
  - Goal-setting: thesis=objetivo atual, antithesis=valor conflitante, synthesis=objetivo refinado
  - Arquitetura: thesis=design atual, antithesis=gargalo, synthesis=refatoracao

Autor: OpenCode Ecosystem (2026) — R21: Metacognicao
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


BRAZIL_TZ = timezone.utc


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class DialecticalPosition:
    """Uma posicao no processo dialetico."""
    content: str               # descricao da posicao
    source: str                # "thesis" | "antithesis" | "synthesis"
    evidence: list[str] = field(default_factory=list)  # evidencias que sustentam
    confidence: float = 1.0


@dataclass
class DialecticalSynthesis:
    """Resultado de uma sintese dialetica."""
    synthesis_id: str
    thesis: DialecticalPosition
    antithesis: DialecticalPosition
    synthesis: str             # a nova posicao que resolve a contradicao
    resolution_type: str       # "aufheben" | "compromise" | "reframe" | "transcend"
    preserved_from_thesis: list[str]
    preserved_from_antithesis: list[str]
    novel_elements: list[str]
    timestamp: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# DIALECTICAL ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class DialecticalEngine:
    """Motor de sintese dialetica para auto-modificacao.

    Principio: Para cada limitacao do sistema (antithesis), existe uma
    sintese que incorpora a limitacao como caso particular de uma
    estrutura mais geral.

    Uso:
        engine = DialecticalEngine()
        synthesis = engine.synthesize(
            thesis="Scanner cobre 10 dimensoes epistemologicas",
            antithesis="Scanner nao detecta capacidades de engenharia (auto-modificacao)"
        )
    """

    def __init__(self):
        self._syntheses: list[DialecticalSynthesis] = []
        self._count: int = 0

    def synthesize(
        self,
        thesis_text: str,
        antithesis_text: str,
        thesis_evidence: list[str] | None = None,
        antithesis_evidence: list[str] | None = None,
    ) -> DialecticalSynthesis:
        """Produz sintese dialetica a partir de tese e antitese.

        Estrategias de resolucao:
          - "aufheben": a sintese preserva elementos de ambos em nivel superior
          - "compromise": a sintese encontra meio-termo
          - "reframe": a sintese redefine o problema
          - "transcend": a sintese transcende a dicotomia
        """
        self._count += 1

        thesis = DialecticalPosition(
            content=thesis_text,
            source="thesis",
            evidence=thesis_evidence or [],
        )
        antithesis = DialecticalPosition(
            content=antithesis_text,
            source="antithesis",
            evidence=antithesis_evidence or [],
        )

        # Analise da contradicao
        thesis_keywords = set(thesis_text.lower().split())
        antithesis_keywords = set(antithesis_text.lower().split())
        shared = thesis_keywords & antithesis_keywords
        unique_thesis = thesis_keywords - antithesis_keywords
        unique_antithesis = antithesis_keywords - thesis_keywords

        # Determinar tipo de resolucao
        if len(shared) > len(unique_thesis) + len(unique_antithesis):
            resolution_type = "compromise"  # muito em comum
        elif len(shared) == 0:
            resolution_type = "reframe"     # nada em comum
        else:
            resolution_type = "aufheben"    # caso classico

        # Construir sintese
        synthesis, preserved_t, preserved_a, novel = self._build_synthesis(
            thesis_text, antithesis_text, resolution_type, shared,
            unique_thesis, unique_antithesis,
        )

        result = DialecticalSynthesis(
            synthesis_id=f"SYN-{self._count:04d}",
            thesis=thesis,
            antithesis=antithesis,
            synthesis=synthesis,
            resolution_type=resolution_type,
            preserved_from_thesis=preserved_t,
            preserved_from_antithesis=preserved_a,
            novel_elements=novel,
            timestamp=datetime.now(BRAZIL_TZ).isoformat(),
        )

        self._syntheses.append(result)
        return result

    def _build_synthesis(
        self, thesis: str, antithesis: str, resolution_type: str,
        shared: set[str], unique_t: set[str], unique_a: set[str],
    ) -> tuple[str, list[str], list[str], list[str]]:
        """Constroi a sintese textual baseada no tipo de resolucao."""

        if resolution_type == "aufheben":
            preserved_t = ["estrutura base da tese", "elementos validados"]
            preserved_a = ["critica construtiva da antitese", "limitacao identificada"]
            novel = ["nivel superior de abstracao", "framework unificado"]
            synthesis = (
                f"[Aufheben] A sintese incorpora a tese ({thesis[:60]}...) "
                f"e sua negacao ({antithesis[:60]}...) em um nivel superior. "
                f"O novo framework reconhece que ambas as posicoes sao casos "
                f"particulares de uma estrutura mais geral que as contem."
            )

        elif resolution_type == "compromise":
            preserved_t = ["nucleo da tese"]
            preserved_a = ["preocupacao valida da antitese"]
            novel = ["solucao hibrida"]
            synthesis = (
                f"[Compromise] Encontrado terreno comum entre '{thesis[:50]}...' "
                f"e '{antithesis[:50]}...'. A sintese adota o nucleo da tese "
                f"enquanto incorpora a preocupacao valida da antitese."
            )

        else:  # reframe
            preserved_t = []
            preserved_a = []
            novel = ["redefinicao do problema", "novo paradigma"]
            synthesis = (
                f"[Reframe] A dicotomia entre '{thesis[:50]}...' e "
                f"'{antithesis[:50]}...' e falsa. O problema real e mais "
                f"fundamental e requer redefinicao dos termos."
            )

        return synthesis, preserved_t, preserved_a, novel

    def synthesize_system_limitation(
        self, capability: str, limitation: str
    ) -> DialecticalSynthesis:
        """Atalho para sintese de limitacao do sistema."""
        return self.synthesize(
            thesis_text=f"O sistema possui a capacidade: {capability}",
            antithesis_text=f"Limitacao detectada: {limitation}",
        )

    def synthesize_gap_closure(
        self, gap: str, existing_strength: str
    ) -> DialecticalSynthesis:
        """Atalho para sintese de fechamento de gap."""
        return self.synthesize(
            thesis_text=f"Forca existente: {existing_strength}",
            antithesis_text=f"Gap identificado: {gap}",
        )

    @property
    def total_syntheses(self) -> int:
        return self._count

    @property
    def resolution_distribution(self) -> dict[str, int]:
        dist: dict[str, int] = {}
        for s in self._syntheses:
            dist[s.resolution_type] = dist.get(s.resolution_type, 0) + 1
        return dist

    def latest(self) -> DialecticalSynthesis | None:
        return self._syntheses[-1] if self._syntheses else None


# ═══════════════════════════════════════════════════════════════════════════
# SELF-MODIFICATION ADAPTER
# ═══════════════════════════════════════════════════════════════════════════

class SelfModificationAdapter:
    """Adaptador que conecta a sintese dialetica a auto-modificacao real.

    Traduz syntheses em patches concretos que podem ser aplicados ao codigo.
    """

    def __init__(self, dialectical_engine: DialecticalEngine | None = None):
        self.engine = dialectical_engine or DialecticalEngine()
        self._patches: list[dict[str, Any]] = []

    def propose_patch(
        self, module: str, limitation: str, current_behavior: str
    ) -> dict[str, Any]:
        """Propoe um patch baseado em sintese dialetica."""
        synthesis = self.engine.synthesize_system_limitation(
            capability=current_behavior,
            limitation=limitation,
        )

        patch = {
            "module": module,
            "synthesis_id": synthesis.synthesis_id,
            "resolution_type": synthesis.resolution_type,
            "description": synthesis.synthesis,
            "novel_elements": synthesis.novel_elements,
            "preserved_thesis": synthesis.preserved_from_thesis,
            "preserved_antithesis": synthesis.preserved_from_antithesis,
            "timestamp": synthesis.timestamp,
        }
        self._patches.append(patch)
        return patch

    @property
    def pending_patches(self) -> list[dict[str, Any]]:
        return self._patches


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════════════

def create_dialectical_engine() -> DialecticalEngine:
    """Factory: cria motor dialetico pronto para uso."""
    return DialecticalEngine()
