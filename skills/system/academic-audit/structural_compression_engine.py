#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StructuralCompressionEngine v1.0 — SPEC-037b: Compressor Estrutural de Grandes Textos
=========================================================================================
Aplicacao operacional do StructuralNoiseScanner (SNS) para textos longos.

Problema:  T = informacao + exemplos + repeticoes + explicacoes + ruido
           Produzir T' tal que T' << T mas Conhecimento(T') ≈ Conhecimento(T)

Fluxo:
  1. Fragmentacao      — T → P1 + P2 + ... + Pn (quebra em partes)
  2. Vetorizacao SNS   — SNS(Pi) → Vi (vetor cognitivo de cada parte)
  3. Extracao          — Vi → {tese, argumento, exemplo, conceito, ruido}
  4. Remocao Redundancia — V = merge(V1...Vn) removendo sobreposicao
  5. Reconstrucao      — T' = ΣV (texto denso final)
  6. Delta             — Δ = comparar Estrutura(T) vs Estrutura(T')

Metricas:
  CR  (Compression Ratio)       = tokens_originais / tokens_finais
  CPS (Cognitive Preservation)  = estruturas_preservadas / estruturas_totais
  FLI (Functional Loss Index)   = funcoes_perdidas / funcoes_totais
  DG  (Density Gain)            = CPS × CR

Autor: OpenCode Ecosystem (2026) — R22: Structural Compression
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from structural_noise_scanner import (
    StructuralNoiseScanner, ElementClassifier,
    ClassifiedElement, ElementRole, CompressionResult,
)


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class CognitiveVector:
    """Vetor cognitivo extraido de uma parte do texto."""
    part_id: str
    thesis: str              # tese central da parte
    arguments: list[str]     # argumentos principais
    examples: list[str]      # exemplos minimos preservados
    concepts: list[str]      # conceitos estruturantes
    logical_deps: list[str]  # dependencias logicas entre partes
    noise_removed: list[str] # ruido identificado e removido
    structure_preserved: bool


@dataclass
class SCECompressionResult:
    """Resultado da compressao estrutural de grande texto."""
    original_tokens: int
    compressed_tokens: int
    original_parts: int
    cognitive_vectors: list[CognitiveVector]
    compressed_text: str
    compression_ratio: float       # CR
    cognitive_preservation: float  # CPS
    functional_loss: float         # FLI
    density_gain: float            # DG
    delta_report: dict[str, Any]   # relatorio delta inicial-final


# ═══════════════════════════════════════════════════════════════════════════
# STRUCTURAL COMPRESSION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class StructuralCompressionEngine:
    """Compressor estrutural para textos longos.

    Nao e um resumidor — e um compressor que preserva a estrutura cognitiva.
    So aprova a compressao se o texto final ainda permitir reconstruir
    o raciocinio original.

    Uso:
        sce = StructuralCompressionEngine()
        result = sce.compress(texto_gigante, part_size=2000)
        print(f"CR={result.compression_ratio:.1f}x, CPS={result.cognitive_preservation:.0%}")
    """

    def __init__(self):
        self.sns = StructuralNoiseScanner()
        self.classifier = ElementClassifier()

    def compress(self, text: str, part_size: int = 2000,
                 min_part_size: int = 100) -> SCECompressionResult:
        """Comprime um texto grande preservando estrutura cognitiva.

        Args:
            text: texto original (pode ser muito grande)
            part_size: tamanho maximo de cada parte em caracteres
            min_part_size: tamanho minimo para uma parte ser processada

        Returns:
            SCECompressionResult com metricas completas
        """
        original_tokens = self._count_tokens(text)

        # Etapa 1: Fragmentacao
        parts = self._fragment(text, part_size, min_part_size)

        # Etapa 2: Vetorizacao SNS em cada parte
        vectors = []
        for i, part in enumerate(parts):
            vector = self._vectorize(part, f"P{i+1}")
            vectors.append(vector)

        # Etapa 3: Remocao de redundancia entre vetores
        merged = self._merge_vectors(vectors)

        # Etapa 4: Reconstrucao do texto denso
        compressed_text = self._reconstruct(merged)

        # Etapa 5: Metricas
        compressed_tokens = self._count_tokens(compressed_text)
        cr = original_tokens / max(1, compressed_tokens)

        cps = self._compute_cps(vectors, merged)
        fli = 1.0 - cps
        dg = cps * cr

        # Etapa 6: Delta
        delta = self._compute_delta(text, compressed_text, vectors, merged)

        return SCECompressionResult(
            original_tokens=original_tokens,
            compressed_tokens=compressed_tokens,
            original_parts=len(parts),
            cognitive_vectors=vectors,
            compressed_text=compressed_text,
            compression_ratio=round(cr, 2),
            cognitive_preservation=round(cps, 4),
            functional_loss=round(fli, 4),
            density_gain=round(dg, 2),
            delta_report=delta,
        )

    # ─── ETAPA 1: FRAGMENTACAO ──────────────────────────────────────────

    def _fragment(self, text: str, part_size: int,
                  min_part_size: int) -> list[str]:
        """Quebra o texto em partes de tamanho controlado.

        Tenta quebrar em paragrafos naturais primeiro, depois por sentencas.
        """
        # Tentar quebrar por paragrafos (linhas em branco)
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        parts: list[str] = []
        current = ""

        for para in paragraphs:
            if len(current) + len(para) <= part_size:
                current += ("\n\n" if current else "") + para
            else:
                if len(current) >= min_part_size:
                    parts.append(current)
                current = para

        if len(current) >= min_part_size:
            parts.append(current)
        elif parts and current:
            parts[-1] += "\n\n" + current

        return parts if parts else [text]

    # ─── ETAPA 2: VETORIZACAO SNS ────────────────────────────────────────

    def _vectorize(self, part_text: str, part_id: str) -> CognitiveVector:
        """Extrai vetor cognitivo de uma parte usando SNS."""
        # Quebrar parte em elementos (sentencas)
        elements = self._split_sentences(part_text)

        # Executar SNS
        sns_result = self.sns.scan(elements)

        # Extrair componentes do vetor
        classified = self.sns.classifier.classify(elements)

        # Tese: primeira estrutura encontrada
        structures = [e for e in classified if e.role == ElementRole.STRUCTURE]
        thesis = structures[0].text if structures else part_text[:100]

        # Argumentos: elementos explanatory + estruturas adicionais
        arguments = [
            e.text for e in classified
            if e.role in (ElementRole.EXPLANATORY, ElementRole.FUNCTION)
        ]

        # Exemplos minimos preservados
        examples = [
            e.text for e in sns_result.reduced_model
            if e.role == ElementRole.EXAMPLE
        ]

        # Conceitos: estruturas + funcoes
        concepts = [
            e.function_label for e in classified
            if e.role == ElementRole.STRUCTURE
        ]

        # Ruido removido
        noise = [e.text for e in sns_result.removed_elements]

        return CognitiveVector(
            part_id=part_id,
            thesis=thesis,
            arguments=arguments[:5],
            examples=examples[:3],
            concepts=concepts[:5],
            logical_deps=[],
            noise_removed=noise[:5],
            structure_preserved=sns_result.sps >= 0.70,
        )

    def _split_sentences(self, text: str) -> list[str]:
        """Divide texto em sentencas."""
        # Split by sentence boundaries
        raw = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in raw if len(s.strip()) > 10]

    # ─── ETAPA 3: MERGE DE VETORES ───────────────────────────────────────

    def _merge_vectors(self, vectors: list[CognitiveVector]) -> dict[str, Any]:
        """Combina vetores cognitivos removendo redundancia entre partes."""
        all_theses: list[str] = []
        all_arguments: list[str] = []
        all_examples: list[str] = []
        all_concepts: list[str] = []
        seen_arguments: set[str] = set()
        seen_concepts: set[str] = set()
        seen_examples: set[str] = set()

        for v in vectors:
            all_theses.append(v.thesis)
            for arg in v.arguments:
                arg_key = arg[:60].lower()
                if arg_key not in seen_arguments:
                    all_arguments.append(arg)
                    seen_arguments.add(arg_key)
            for ex in v.examples:
                ex_key = ex[:40].lower()
                if ex_key not in seen_examples:
                    all_examples.append(ex)
                    seen_examples.add(ex_key)
            for c in v.concepts:
                if c not in seen_concepts:
                    all_concepts.append(c)
                    seen_concepts.add(c)

        return {
            "theses": all_theses,
            "arguments": all_arguments,
            "examples": all_examples[:5],   # manter no maximo 5 exemplos
            "concepts": all_concepts[:10],  # manter no maximo 10 conceitos
        }

    # ─── ETAPA 4: RECONSTRUCAO ────────────────────────────────────────────

    def _reconstruct(self, merged: dict[str, Any]) -> str:
        """Reconstroi texto denso a partir dos vetores merged."""
        lines: list[str] = []

        # Tese principal
        if merged["theses"]:
            lines.append(merged["theses"][0])

        # Argumentos
        if merged["arguments"]:
            lines.append("\nARGUMENTOS:")
            for i, arg in enumerate(merged["arguments"][:5], 1):
                lines.append(f"  {i}. {arg}")

        # Conceitos
        if merged["concepts"]:
            lines.append("\nCONCEITOS ESTRUTURANTES:")
            for c in merged["concepts"][:8]:
                lines.append(f"  • {c}")

        # Exemplos minimos
        if merged["examples"]:
            lines.append("\nEXEMPLOS:")
            for ex in merged["examples"][:3]:
                lines.append(f"  • {ex}")

        return "\n".join(lines)

    # ─── ETAPA 5: METRICAS ────────────────────────────────────────────────

    def _count_tokens(self, text: str) -> int:
        """Estimativa simples de tokens (palavras)."""
        return len(text.split())

    def _compute_cps(self, vectors: list[CognitiveVector],
                     merged: dict[str, Any]) -> float:
        """Cognitive Preservation Score."""
        preserved = sum(1 for v in vectors if v.structure_preserved)
        return preserved / max(1, len(vectors))

    def _compute_delta(self, original: str, compressed: str,
                       vectors: list[CognitiveVector],
                       merged: dict[str, Any]) -> dict[str, Any]:
        """Computa delta inicial-final."""
        original_structs = sum(len(v.concepts) for v in vectors)
        compressed_structs = len(merged.get("concepts", []))

        noise_total = sum(len(v.noise_removed) for v in vectors)
        total_elements = len(self._split_sentences(original))

        return {
            "original_tokens": self._count_tokens(original),
            "compressed_tokens": self._count_tokens(compressed),
            "original_structures": original_structs,
            "compressed_structures": compressed_structs,
            "noise_removed_total": noise_total,
            "structure_loss": max(0, original_structs - compressed_structs),
            "total_sentences": total_elements,
        }

    # ─── RELATORIO ────────────────────────────────────────────────────────

    def report(self, result: SCECompressionResult) -> str:
        """Relatorio de compressao em Markdown."""
        d = result.delta_report
        lines = [
            "# Relatorio de Compressao Estrutural (SCE)",
            "",
            f"**Compression Ratio (CR)**: {result.compression_ratio:.1f}x",
            f"**Cognitive Preservation (CPS)**: {result.cognitive_preservation:.0%}",
            f"**Functional Loss (FLI)**: {result.functional_loss:.0%}",
            f"**Density Gain (DG)**: {result.density_gain:.1f}",
            "",
            f"| Metrica | Original | Comprimido |",
            f"|---------|----------|------------|",
            f"| Tokens | {d['original_tokens']} | {d['compressed_tokens']} |",
            f"| Estruturas | {d['original_structures']} | {d['compressed_structures']} |",
            f"| Ruido removido | — | {d['noise_removed_total']} |",
            "",
            f"**Partes processadas**: {result.original_parts}",
            f"**Vetores cognitivos**: {len(result.cognitive_vectors)}",
        ]

        if result.functional_loss <= 0.10:
            lines.append("\n✅ **Compressao segura**: perda cognitiva minima.")
        elif result.functional_loss <= 0.30:
            lines.append("\n⚠️ **Compressao moderada**: revisar elementos removidos.")
        else:
            lines.append("\n❌ **Compressao destrutiva**: alta perda cognitiva detectada.")

        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════════════

def create_compression_engine() -> StructuralCompressionEngine:
    """Factory: cria compressor estrutural pronto para uso."""
    return StructuralCompressionEngine()
