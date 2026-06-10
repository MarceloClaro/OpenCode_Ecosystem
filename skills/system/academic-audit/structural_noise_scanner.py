#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StructuralNoiseScanner v1.0 — SPEC-037: Compressao Estrutural com Preservacao Funcional
=========================================================================================
Implementa a camada proposta de reducao de ruido estrutural do OpenCode Ecosystem.

Modelo Formal: C = E + S + R → C' = S + E*
  C  = corpus/fenomeno observado
  E  = exemplos e manifestacoes superficiais
  S  = estruturas e funcoes essenciais
  R  = ruido residual
  C' = modelo reduzido (estruturas + exemplos minimos)
  E* = exemplos minimos necessarios para reconstrucao

5 Modulos:
  1. ElementClassifier          — classifica cada elemento (exemplo/estrutura/funcao/ruido)
  2. FunctionPreservationEngine — verifica se funcao sobrevive apos remocao do elemento
  3. StructuralCompressionEngine — agrupa variacoes superficiais em estrutura comum
  4. ReconstructionTest         — testa se modelo reduzido reconstroi o original
  5. RelevanceProtectionLayer   — impede remocao indevida de informacao relevante

Metricas:
  SPS (Structural Preservation Score) — funcoes preservadas / funcoes totais
  NRR (Noise Reduction Rate)         — elementos removidos / elementos totais
  FLI (Functional Loss Index)        — funcoes perdidas / funcoes totais

Autor: OpenCode Ecosystem (2026) — R22: Structural Noise Scanner
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════════
# ENUMS & DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

class ElementRole(str, Enum):
    """Classificacao do papel de cada elemento no fenomeno."""
    EXAMPLE = "example"           # manifestacao superficial, ilustracao
    STRUCTURE = "structure"       # funcao essencial, arcabouco
    FUNCTION = "function"         # papel que o elemento cumpre no sistema
    NOISE = "noise"               # ruido, irrelevante
    REDUNDANCY = "redundancy"     # repete estrutura ja capturada
    EXPLANATORY = "explanatory"   # vetor explicativo, ajuda a reconstruir


@dataclass
class ClassifiedElement:
    """Elemento classificado com metadados."""
    text: str
    role: ElementRole
    function_label: str           # descricao da funcao (ex.: "detector de estruturas latentes")
    confidence: float             # 0-1
    position: int                 # posicao no texto original
    removable: bool = False       # True se pode ser removido sem perda funcional
    removal_justification: str = ""


@dataclass
class CompressionResult:
    """Resultado da compressao estrutural."""
    original_elements: int
    classified: dict[ElementRole, int]
    reduced_model: list[ClassifiedElement]
    removed_elements: list[ClassifiedElement]
    protected_elements: list[ClassifiedElement]
    clusters: dict[str, list[str]]        # estrutura → [exemplos agrupados]
    sps: float                             # Structural Preservation Score
    nrr: float                             # Noise Reduction Rate
    fli: float                             # Functional Loss Index
    reconstruction_score: float            # 0-1: capacidade de reconstrucao
    reconstruction_gaps: list[str]         # lacunas detectadas


# ═══════════════════════════════════════════════════════════════════════════
# 1. ELEMENT CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════

class ElementClassifier:
    """Classifica cada elemento do corpus em exemplo, estrutura, funcao ou ruido.

    Heuristicas:
      - Nomes proprios, metaforas, citacoes → EXAMPLE
      - Verbos de acao, definicoes, relacoes logicas → STRUCTURE
      - Palavras funcionais, conectores, preposicoes → FUNCTION
      - Repeticoes, filler words, baixa densidade informacional → NOISE
      - Elementos que replicam estrutura ja capturada → REDUNDANCY
      - Elementos que conectam ou explicam outros → EXPLANATORY
    """

    # Keywords estruturais (indicam funcao essencial)
    STRUCTURAL_PATTERNS: list[str] = [
        "objetivo", "proposta", "conceito", "hipotese", "formalmente",
        "condicao", "requisito", "arquitetura", "modulo", "camada",
        "pipeline", "fluxo", "estrutura", "fundamento", "principio",
        "depende", "implica", "resulta", "produz", "transforma",
        "separar", "distinguir", "preservar", "identificar", "classificar",
    ]

    # Keywords de exemplo (manifestacoes superficiais)
    EXAMPLE_PATTERNS: list[str] = [
        "exemplo", "leonardo", "einstein", "aristoteles", "agostinho",
        "ilustracao", "caso", "instancia", "aplicacao", "demonstracao",
        "da vinci", "newton", "darwin", "freud", "piaget",
    ]

    # Keywords de ruido (baixa densidade informacional)
    NOISE_PATTERNS: list[str] = [
        "obviamente", "claramente", "evidentemente", "basicamente",
        "simplesmente", "certamente", "naturalmente", "provavelmente",
    ]

    # Keywords de funcao (conectores, operadores logicos)
    FUNCTION_PATTERNS: list[str] = [
        "portanto", "entretanto", "contudo", "alem disso", "dessa forma",
        "consequentemente", "por outro lado", "em contraste", "similarmente",
    ]

    def classify(self, elements: list[str]) -> list[ClassifiedElement]:
        """Classifica uma lista de elementos textuais."""
        classified: list[ClassifiedElement] = []
        seen_functions: set[str] = set()

        for i, elem in enumerate(elements):
            text = elem.strip().lower()
            if not text:
                continue

            func_label = "indefinido"

            # Heuristica 1: identificar papel estrutural
            if any(p in text for p in self.STRUCTURAL_PATTERNS):
                role = ElementRole.STRUCTURE
                func_label = self._extract_function_label(text)
                confidence = 0.85

            # Heuristica 2: identificar exemplos
            elif any(p in text for p in self.EXAMPLE_PATTERNS):
                role = ElementRole.EXAMPLE
                func_label = self._extract_function_label(text) or "ilustracao"
                confidence = 0.8

            # Heuristica 3: identificar ruido
            elif any(p in text for p in self.NOISE_PATTERNS):
                role = ElementRole.NOISE
                func_label = "ruido"
                confidence = 0.75

            # Heuristica 4: identificar funcoes (conectores)
            elif any(p in text for p in self.FUNCTION_PATTERNS):
                role = ElementRole.FUNCTION
                func_label = "conector logico"
                confidence = 0.7

            # Heuristica 5: identificar redundancia (funcao ja vista antes)
            elif func_label != "indefinido" and func_label in seen_functions:
                role = ElementRole.REDUNDANCY
                confidence = 0.6

            else:
                role = ElementRole.EXPLANATORY
                func_label = self._extract_function_label(text) or "explicativo"
                confidence = 0.5

            seen_functions.add(func_label)

            classified.append(ClassifiedElement(
                text=elem.strip(),
                role=role,
                function_label=func_label,
                confidence=confidence,
                position=i,
            ))

        return classified

    def _extract_function_label(self, text: str) -> str:
        """Extrai um rotulo funcional do texto."""
        # Padroes comuns de funcao
        patterns = [
            (r"(?:proposta|objetivo|conceito).*?(?:criar|construir|desenvolver|implementar)\s+(.+)", 1),
            (r"(?:permite|possibilita|viabiliza)\s+(.+)", 1),
            (r"(?:detect\w+|identific\w+|classific\w+|separ\w+|distingu\w+)\s+(.+)", 0),
            (r"(?:preserv\w+|reconstru\w+|compress\w+)\s+(.+)", 0),
        ]

        for pattern, group in patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                label = m.group(group) if group else m.group(0)
                return label[:60].strip()

        # Fallback: primeiras 3 palavras significantes
        words = text.split()[:4]
        return " ".join(words)[:50] if words else "indefinido"


# ═══════════════════════════════════════════════════════════════════════════
# 2. FUNCTION PRESERVATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class FunctionPreservationEngine:
    """Verifica se a funcao de um elemento sobrevive apos sua remocao.

    Principio: Uma informacao so pode ser removida se sua funcao
    continuar representada em outro elemento do modelo.
    """

    def check(self, element: ClassifiedElement,
              remaining: list[ClassifiedElement]) -> dict[str, Any]:
        """Verifica preservacao funcional.

        Returns:
            {"preserved": bool, "by": str|None, "risk": "none"|"low"|"high"}
        """
        # Regra 1: Elementos de ruido sempre podem ser removidos
        if element.role == ElementRole.NOISE:
            return {"preserved": True, "by": "ruido", "risk": "none"}

        # Regra 2: Redundancias podem ser removidas (funcao ja existe)
        if element.role == ElementRole.REDUNDANCY:
            return {"preserved": True, "by": "redundancia", "risk": "low"}

        # Regra 3: Verificar se a mesma funcao existe em outro elemento
        same_function = [
            e for e in remaining
            if e.function_label == element.function_label
            and e.position != element.position
        ]
        if same_function:
            return {
                "preserved": True,
                "by": same_function[0].text[:50],
                "risk": "low",
            }

        # Regra 4: Estruturas nunca podem ser removidas se unicas
        if element.role == ElementRole.STRUCTURE:
            return {"preserved": False, "by": None, "risk": "high"}

        # Regra 5: Exemplos podem ser removidos se a estrutura existe
        structure_elements = [e for e in remaining if e.role == ElementRole.STRUCTURE]
        if element.role == ElementRole.EXAMPLE and structure_elements:
            return {"preserved": True, "by": "estrutura", "risk": "low"}

        return {"preserved": False, "by": None, "risk": "high"}


# ═══════════════════════════════════════════════════════════════════════════
# 3. STRUCTURAL COMPRESSION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class StructuralCompressionEngine:
    """Agrupa multiplas manifestacoes superficiais em uma estrutura comum.

    Exemplo:
      "Leonardo" + "Einstein" + "Aristoteles" → "detectores de estruturas ocultas"
    """

    def compress(self, elements: list[ClassifiedElement]) -> dict[str, list[str]]:
        """Agrupa exemplos e variacoes sob suas funcoes estruturais comuns.

        Returns:
            {estrutura: [exemplo1, exemplo2, ...]}
        """
        clusters: dict[str, list[str]] = {}
        structure_items: dict[str, str] = {}

        # Passo 1: Identificar estruturas e suas funcoes
        for elem in elements:
            if elem.role == ElementRole.STRUCTURE:
                structure_items[elem.function_label] = elem.text

        # Passo 2: Agrupar exemplos sob estruturas (por function_label)
        for elem in elements:
            if elem.role == ElementRole.EXAMPLE:
                # Tentar correspondencia por function_label primeiro
                matched = False
                for func_label, struct_text in structure_items.items():
                    # Se o exemplo compartilha palavras com a estrutura OU tem mesma funcao
                    elem_words = set(elem.text.lower().split())
                    struct_words = set(struct_text.lower().split())
                    common = elem_words & struct_words
                    if len(common) > 0 or elem.function_label == func_label:
                        clusters.setdefault(func_label, []).append(elem.text)
                        matched = True
                        break

                # Fallback: agrupar todos os exemplos sob "ilustracoes"
                if not matched and structure_items:
                    first_structure = next(iter(structure_items))
                    clusters.setdefault(first_structure, []).append(elem.text)

        # Passo 3: Agrupar elementos com mesma funcao
        func_groups: dict[str, list[str]] = {}
        for elem in elements:
            if elem.role in (ElementRole.EXPLANATORY, ElementRole.FUNCTION):
                func_groups.setdefault(elem.function_label, []).append(elem.text)

        # Merge: grupos com >= 2 elementos
        for func_label, items in func_groups.items():
            if len(items) >= 2:
                clusters[f"grupo:{func_label}"] = items

        return clusters

    def _find_best_structure(self, elem: ClassifiedElement,
                             structures: dict[str, str]) -> str | None:
        """Encontra a estrutura mais proxima de um exemplo."""
        if not structures:
            return None

        # Heuristica: correspondencia por keywords compartilhadas
        elem_words = set(elem.text.lower().split())
        best_score = 0
        best_structure = None

        for func_label, struct_text in structures.items():
            struct_words = set(struct_text.lower().split())
            common = elem_words & struct_words
            score = len(common) / max(1, len(elem_words))
            if score > best_score:
                best_score = score
                best_structure = func_label

        return best_structure if best_score > 0.1 else None


# ═══════════════════════════════════════════════════════════════════════════
# 4. RECONSTRUCTION TEST
# ═══════════════════════════════════════════════════════════════════════════

class ReconstructionTest:
    """Testa se o modelo reduzido ainda permite reconstruir a estrutura original.

    Principio: Reconstrucao(Modelo Reduzido) ≈ Estrutura(Fenomeno Original)
    """

    def test(self, original: list[ClassifiedElement],
             reduced: list[ClassifiedElement]) -> dict[str, Any]:
        """Avalia capacidade de reconstrucao.

        Returns:
            {"score": 0-1, "gaps": [...], "missing_functions": [...]}
        """
        original_structures = {e.function_label for e in original
                               if e.role == ElementRole.STRUCTURE}
        reduced_structures = {e.function_label for e in reduced
                              if e.role == ElementRole.STRUCTURE}

        original_functions = {e.function_label for e in original
                              if e.role != ElementRole.NOISE}
        reduced_functions = {e.function_label for e in reduced
                             if e.role != ElementRole.NOISE}

        # Gaps: estruturas que desapareceram
        missing_structures = original_structures - reduced_structures
        missing_functions = original_functions - reduced_functions

        # Score: proporcao de funcoes preservadas
        total_functions = len(original_functions)
        preserved = len(reduced_functions & original_functions)

        score = preserved / max(1, total_functions)

        gaps: list[str] = []
        if missing_structures:
            gaps.append(f"Estruturas perdidas: {missing_structures}")
        if missing_functions:
            gaps.append(f"Funcoes perdidas: {missing_functions}")

        return {
            "score": round(score, 4),
            "gaps": gaps,
            "missing_structures": list(missing_structures),
            "missing_functions": list(missing_functions),
            "preserved_ratio": round(preserved / max(1, total_functions), 4),
        }


# ═══════════════════════════════════════════════════════════════════════════
# 5. RELEVANCE PROTECTION LAYER
# ═══════════════════════════════════════════════════════════════════════════

class RelevanceProtectionLayer:
    """Impede remocao indevida de informacao relevante.

    Regras:
      1. So remove se funcao esta representada em outro elemento
      2. So remove se retirada nao altera reconstrucao estrutural
      3. So remove se for repeticao sem funcao nova
    """

    def protect(self, elements: list[ClassifiedElement],
                preservation: FunctionPreservationEngine) -> tuple[list[ClassifiedElement],
                                                                     list[ClassifiedElement],
                                                                     list[ClassifiedElement]]:
        """Separa elementos em protegidos, removiveis e removidos.

        Returns:
            (protegidos, removiveis, efetivamente removidos)
        """
        protected: list[ClassifiedElement] = []
        removable: list[ClassifiedElement] = []
        removed: list[ClassifiedElement] = []

        remaining = [e for e in elements if e.role != ElementRole.NOISE]

        for elem in elements:
            # Regra 1: Ruido sempre removivel
            if elem.role == ElementRole.NOISE:
                elem.removable = True
                elem.removal_justification = "ruido — baixa densidade informacional"
                removable.append(elem)
                removed.append(elem)
                continue

            # Regra 2: Verificar preservacao funcional
            check = preservation.check(elem, remaining)
            if check["preserved"] and check["risk"] != "high":
                elem.removable = True
                elem.removal_justification = f"funcao preservada por: {check['by']}"
                removable.append(elem)
                if elem.role == ElementRole.REDUNDANCY:
                    removed.append(elem)
                elif elem.role == ElementRole.EXAMPLE and check["risk"] == "low":
                    removed.append(elem)
                else:
                    protected.append(elem)  # nao remover exemplos com risco medio
            else:
                elem.removable = False
                elem.removal_justification = f"protegido — risco: {check['risk']}"
                protected.append(elem)

        return protected, removable, removed


# ═══════════════════════════════════════════════════════════════════════════
# STRUCTURAL NOISE SCANNER (Orquestrador)
# ═══════════════════════════════════════════════════════════════════════════

class StructuralNoiseScanner:
    """Scanner de ruido estrutural: comprime preservando funcao.

    Pipeline:
      Corpus → ElementClassifier → FunctionPreservationEngine
      → StructuralCompressionEngine → ReconstructionTest
      → RelevanceProtectionLayer → Modelo Reduzido Auditavel

    Uso:
        sns = StructuralNoiseScanner()
        result = sns.scan(["texto 1", "texto 2", ...])
        print(f"SPS={result.sps:.0%}, NRR={result.nrr:.0%}, FLI={result.fli:.0%}")
    """

    def __init__(self):
        self.classifier = ElementClassifier()
        self.preservation = FunctionPreservationEngine()
        self.compressor = StructuralCompressionEngine()
        self.reconstructor = ReconstructionTest()
        self.protector = RelevanceProtectionLayer()

    def scan(self, elements: list[str]) -> CompressionResult:
        """Executa o pipeline completo de compressao estrutural.

        Args:
            elements: lista de strings (paragrafos, sentencas, frases)

        Returns:
            CompressionResult com metricas e modelo reduzido
        """
        # 1. Classificar
        classified = self.classifier.classify(elements)

        # 2. Separar em protegidos vs removiveis
        protected, removable, removed = self.protector.protect(classified, self.preservation)

        # 3. Comprimir estruturalmente
        clusters = self.compressor.compress(classified)

        # 4. Construir modelo reduzido (estruturas + 1 exemplo por estrutura + explanatory essenciais)
        reduced: list[ClassifiedElement] = []
        # Todas as estruturas (essenciais)
        for e in protected:
            if e.role == ElementRole.STRUCTURE:
                reduced.append(e)
        # Um exemplo por estrutura (minimo para reconstrucao)
        added_examples: set[str] = set()
        for e in protected:
            if e.role == ElementRole.EXAMPLE and e.function_label not in added_examples:
                reduced.append(e)
                added_examples.add(e.function_label)
        # Elementos explanatory que nao sao redundantes
        for e in protected:
            if e.role == ElementRole.EXPLANATORY and e.function_label not in added_examples:
                reduced.append(e)
                added_examples.add(e.function_label)

        # 5. Testar reconstrucao
        reconstruction = self.reconstructor.test(classified, reduced)

        # 6. Calcular metricas
        total_functions = len({e.function_label for e in classified if e.role != ElementRole.NOISE})
        preserved_functions = len({e.function_label for e in reduced if e.role != ElementRole.NOISE})
        lost_functions = max(0, total_functions - preserved_functions)

        sps = preserved_functions / max(1, total_functions)
        nrr = len(removed) / max(1, len(elements))
        fli = lost_functions / max(1, total_functions)

        return CompressionResult(
            original_elements=len(elements),
            classified=self._count_by_role(classified),
            reduced_model=reduced,
            removed_elements=removed,
            protected_elements=protected,
            clusters=clusters,
            sps=round(sps, 4),
            nrr=round(nrr, 4),
            fli=round(fli, 4),
            reconstruction_score=reconstruction["score"],
            reconstruction_gaps=reconstruction["gaps"],
        )

    def _count_by_role(self, elements: list[ClassifiedElement]) -> dict[ElementRole, int]:
        counts: dict[ElementRole, int] = {}
        for e in elements:
            counts[e.role] = counts.get(e.role, 0) + 1
        return counts

    @property
    def metrics(self) -> dict[str, str]:
        """Descricao das metricas do scanner."""
        return {
            "SPS": "Structural Preservation Score — funcoes preservadas / funcoes totais (>=0.90 seguro)",
            "NRR": "Noise Reduction Rate — elementos removidos / elementos totais",
            "FLI": "Functional Loss Index — funcoes perdidas / funcoes totais (quanto menor, melhor)",
            "Reconstruction": "Score de reconstrucao — capacidade de explicar o original a partir do reduzido",
        }


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════════════

def create_structural_noise_scanner() -> StructuralNoiseScanner:
    """Factory: cria scanner de ruido estrutural pronto para uso."""
    return StructuralNoiseScanner()
