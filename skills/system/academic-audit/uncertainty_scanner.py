#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UncertaintyScanner v1.0 — Mapeamento de Incertezas (OQS Etapa 2)
================================================================
SPEC-056: Optimal Question Scanner — Componente de escaneamento de incertezas.

Mapeia as incertezas presentes em um problema para alimentar o
Question Vectorizer e o cálculo do Convergence Score.

Etapas:
  1. Problem Intake: normaliza o problema bruto
  2. Uncertainty Scan: identifica lacunas, ambiguidades, premissas
  3. Structural Noise Filter: remove ruído improdutivo

Uso:
    from uncertainty_scanner import UncertaintyScanner
    scanner = UncertaintyScanner()
    result = scanner.scan("Problema ou texto para análise")
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# ═══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class Uncertainty:
    """Uma incerteza identificada no problema."""
    category: str         # conceitual | terminológica | premisa | relacional | ambígua
    description: str      # descrição da incerteza
    fragment: str         # trecho do texto que gerou a incerteza
    severity: float       # 0.0 (baixa) a 1.0 (crítica)
    confidence: float     # 0.0 a 1.0 — quão certo estamos desta incerteza


@dataclass
class ProblemIntake:
    """Problema normalizado após a etapa de intake."""
    raw_text: str
    normalized_text: str
    object_of_analysis: str
    initial_scope: str
    word_count: int
    has_hypothesis: bool


@dataclass
class NoisyElement:
    """Elemento de ruído estrutural identificado."""
    type: str             # repetição | metáfora | redundância | bifurcação | termo_decorativo
    fragment: str
    removal_rationale: str


@dataclass
class UncertaintyScanResult:
    """Resultado completo do escaneamento de incertezas."""
    problem: ProblemIntake
    uncertainties: list[Uncertainty] = field(default_factory=list)
    noisy_elements: list[NoisyElement] = field(default_factory=list)
    critical_points: list[str] = field(default_factory=list)
    ambiguity_zones: list[str] = field(default_factory=list)
    filtered_text: str = ""
    timestamp: str = ""


# ═══════════════════════════════════════════════════════════════════════
# PATTERNS FOR NOISE DETECTION
# ═══════════════════════════════════════════════════════════════════════

REPETITION_PATTERNS = [
    (r'(.{15,})\1{2,}', 'repetição'),
]

METAPHOR_INDICATORS = [
    r'\bcomo\s+se\b',
    r'\bé\s+como\b',
    r'\bmetaforicamente\b',
    r'\bquase\s+como\b',
    r'\buma\s+espécie\s+de\b',
]

BIFURCATION_PATTERNS = [
    r'\bpor\s+outro\s+lado\b',
    r'\bpor\sum\s+lado\b',
    r'\balternativamente\b',
    r'\boutra\s+possibilidade\b',
    r'\bporém\s+também\b',
]

DECORATIVE_TERMS = [
    'neste contexto', 'vale ressaltar', 'importante mencionar',
    'como já dito', 'conforme mencionado', 'cabe destacar',
]


# ═══════════════════════════════════════════════════════════════════════
# UNCERTAINTY KEYWORDS
# ═══════════════════════════════════════════════════════════════════════

UNCERTAINTY_PATTERNS: dict[str, list[str]] = {
    "conceitual": [
        r'\bqual\s+é\b', r'\bo\s+que\s+é\b', r'\bcomo\s+definir\b',
        r'\bsignifica\b', r'\bconceito\s+de\b', r'\bnatureza\s+de\b',
    ],
    "terminológica": [
        r'\btermo\b', r'\bpalavra\b', r'\bchamado\b', r'\bdenominado\b',
        r'\btambém\s+conhecido\b', r'\bambiguidade\b',
    ],
    "premissa": [
        r'\bse\b.*\bentão\b', r'\bpresum[eê]|parto\s+do\s+princípio\b',
        r'\bassumindo\b', r'\bhipótese\b', r'\bpremissa\b',
        r'\bdado\s+que\b', r'\bconsiderando\s+que\b',
    ],
    "relacional": [
        r'\brelação\b', r'\bconexão\b', r'\bentre\b.*\be\b',
        r'\bdepend[eê]ncia\b', r'\bcorrelação\b', r'\bligação\b',
        r'\binflu[eê]ncia\b',
    ],
    "ambígua": [
        r'\bdúvida\b', r'\bnão\s+sei\b', r'\bincerto\b',
        r'\bpode\s+ser\b', r'\btalvez\b', r'\bpossivelmente\b',
        r'\b不确定\b',  # CJK uncertainty marker — zero tolerance
    ],
}


# ═══════════════════════════════════════════════════════════════════════
# SCANNER
# ═══════════════════════════════════════════════════════════════════════

class UncertaintyScanner:
    """Mapeia incertezas presentes em um problema (OQS Etapa 2)."""

    def __init__(self, enable_noise_filter: bool = True):
        self.enable_noise_filter = enable_noise_filter

    def scan(self, raw_text: str) -> UncertaintyScanResult:
        """Executa o pipeline completo de escaneamento de incertezas.

        Args:
            raw_text: Texto bruto do problema a ser analisado.

        Returns:
            UncertaintyScanResult com incertezas, ruídos e texto filtrado.
        """
        # Etapa 1: Problem Intake
        problem = self._problem_intake(raw_text)

        # Etapa 2: Uncertainty Scan
        uncertainties = self._scan_uncertainties(problem.normalized_text)

        # Etapa 3: Structural Noise Filter
        noisy_elements, filtered_text = self._filter_noise(
            problem.normalized_text
        ) if self.enable_noise_filter else ([], problem.normalized_text)

        # Identificar pontos críticos
        critical_points = [
            u.description for u in uncertainties if u.severity >= 0.7
        ]

        # Identificar zonas de ambiguidade
        ambiguity_zones = [
            u.description for u in uncertainties if u.category == "ambígua"
        ]

        return UncertaintyScanResult(
            problem=problem,
            uncertainties=sorted(uncertainties, key=lambda u: u.severity, reverse=True),
            noisy_elements=noisy_elements,
            critical_points=critical_points,
            ambiguity_zones=ambiguity_zones,
            filtered_text=filtered_text,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _problem_intake(self, raw_text: str) -> ProblemIntake:
        """Etapa 1: Normaliza o problema bruto."""
        if not raw_text or not raw_text.strip():
            raise ValueError("Texto do problema não pode ser vazio")

        normalized = raw_text.strip()
        # Remove espaços múltiplos
        normalized = re.sub(r'\s+', ' ', normalized)
        # Remove linhas em branco excessivas
        normalized = re.sub(r'\n{3,}', '\n\n', normalized)

        # Extrair objeto de análise (heurística: primeiros 100 caracteres)
        object_candidate = normalized[:100].split('.')[0].strip()
        if len(object_candidate) > 80:
            object_candidate = object_candidate[:77] + "..."

        # Escopo inicial (heurística)
        if len(normalized) < 100:
            scope = "micro"
        elif len(normalized) < 500:
            scope = "meso"
        else:
            scope = "macro"

        # Verificar se contém hipótese
        has_hypothesis = bool(
            re.search(r'\bhipótese\b|\bH[0-9]\b|\bH_\b', normalized)
        )

        return ProblemIntake(
            raw_text=raw_text,
            normalized_text=normalized,
            object_of_analysis=object_candidate,
            initial_scope=scope,
            word_count=len(normalized.split()),
            has_hypothesis=has_hypothesis,
        )

    def _scan_uncertainties(
        self, text: str
    ) -> list[Uncertainty]:
        """Etapa 2: Identifica incertezas no texto."""
        uncertainties = []
        found_categories: dict[str, set[str]] = {}

        for category, patterns in UNCERTAINTY_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    start = max(0, match.start() - 40)
                    end = min(len(text), match.end() + 40)
                    fragment = text[start:end].strip()
                    fragment = re.sub(r'\s+', ' ', fragment)

                    # Evitar duplicatas próximas
                    if category in found_categories:
                        if any(
                            abs(len(fragment) - len(existing)) < 10
                            for existing in found_categories[category]
                        ):
                            continue

                    # Calcular severidade com base no contexto
                    severity = self._calc_severity(category, fragment)

                    # Confiança
                    confidence = 0.7 if category != "ambígua" else 0.5

                    uncertainties.append(Uncertainty(
                        category=category,
                        description=self._describe_uncertainty(category, match.group()),
                        fragment=fragment,
                        severity=severity,
                        confidence=confidence,
                    ))

                    if category not in found_categories:
                        found_categories[category] = set()
                    found_categories[category].add(fragment)

        return uncertainties

    def _calc_severity(self, category: str, fragment: str) -> float:
        """Calcula severidade da incerteza (0.0 a 1.0)."""
        base_severity = {
            "conceitual": 0.8,
            "premissa": 0.9,
            "relacional": 0.7,
            "terminológica": 0.5,
            "ambígua": 0.6,
        }.get(category, 0.5)

        # Ajustar com base em indicadores de urgência
        urgency_indicators = [
            r'\bcrítico\b', r'\b urgente\b', r'\bemergencial\b',
            r'\bdecisão\b', r'\bbloqueador\b', r'\bgargalo\b',
        ]
        for indicator in urgency_indicators:
            if re.search(indicator, fragment, re.IGNORECASE):
                base_severity = min(1.0, base_severity + 0.2)
                break

        return round(min(1.0, base_severity), 2)

    def _describe_uncertainty(self, category: str, match: str) -> str:
        """Gera descrição legível da incerteza."""
        descriptions = {
            "conceitual": f"Conceito não definido: '{match}'",
            "premissa": f"Premissa não verificada: '{match}'",
            "relacional": f"Relação não especificada: '{match}'",
            "terminológica": f"Termo ambíguo: '{match}'",
            "ambígua": f"Incerteza explícita: '{match}'",
        }
        return descriptions.get(category, f"Incerteza detectada: '{match}'")

    def _filter_noise(
        self, text: str
    ) -> tuple[list[NoisyElement], str]:
        """Etapa 3: Filtra ruído estrutural do texto."""
        noisy_elements = []
        filtered = text

        # 1. Repetições
        for pattern, noise_type in REPETITION_PATTERNS:
            matches = re.finditer(pattern, filtered)
            for match in matches:
                noisy_elements.append(NoisyElement(
                    type=noise_type,
                    fragment=match.group()[:80],
                    removal_rationale="Repetição textual identificada",
                ))
                # Remove repetição (mantém primeira ocorrência)
                first = match.group()[:len(match.group()) // 2]
                filtered = filtered.replace(match.group(), first, 1)

        # 2. Metáforas excessivas
        for pattern in METAPHOR_INDICATORS:
            matches = re.finditer(pattern, filtered, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 20)
                end = min(len(filtered), match.end() + 20)
                fragment = filtered[start:end].strip()
                noisy_elements.append(NoisyElement(
                    type="metáfora",
                    fragment=re.sub(r'\s+', ' ', fragment),
                    removal_rationale="Metáfora que pode desviar a investigação",
                ))

        # 3. Bifurcações prematuras
        for pattern in BIFURCATION_PATTERNS:
            matches = re.finditer(pattern, filtered, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 30)
                end = min(len(filtered), match.end() + 30)
                fragment = filtered[start:end].strip()
                noisy_elements.append(NoisyElement(
                    type="bifurcação",
                    fragment=re.sub(r'\s+', ' ', fragment),
                    removal_rationale="Bifurcação prematura que amplia ruído",
                ))

        # 4. Termos decorativos
        for term in DECORATIVE_TERMS:
            if term in filtered.lower():
                # Encontrar posição real (case insensitive)
                idx = filtered.lower().find(term)
                if idx >= 0:
                    fragment = filtered[idx:idx + len(term)]
                    noisy_elements.append(NoisyElement(
                        type="termo_decorativo",
                        fragment=fragment,
                        removal_rationale="Termo decorativo sem valor investigativo",
                    ))

        return noisy_elements, filtered


# ═══════════════════════════════════════════════════════════════════════
# QUICK TEST
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Teste simples
    test_problem = (
        "Preciso entender se o OpenCode Ecosystem pode evoluir. "
        "O que é evolução em ecossistemas cognitivos? "
        "Talvez a resposta esteja na relação entre scanners e motores de raciocínio. "
        "Por outro lado, pode ser que o conceito de pergunta ótima seja apenas resumo. "
        "Como definir se uma pergunta é melhor que outra? "
        "Assumindo que perguntas têm valor, então precisamos de métricas. "
        "Vale ressaltar que este é um tópico importante."
    )

    scanner = UncertaintyScanner()
    result = scanner.scan(test_problem)

    print(f"=== UNCERTAINTY SCAN ===")
    print(f"Objeto: {result.problem.object_of_analysis}")
    print(f"Escopo: {result.problem.initial_scope}")
    print(f"Palavras: {result.problem.word_count}")
    print(f"Tem hipótese: {result.problem.has_hypothesis}")
    print(f"\nIncertezas ({len(result.uncertainties)}):")
    for u in result.uncertainties:
        print(f"  [{u.severity:.2f}] {u.category}: {u.description[:60]}")
    print(f"\nRuídos ({len(result.noisy_elements)}):")
    for n in result.noisy_elements:
        print(f"  {n.type}: {n.fragment[:50]}")
    print(f"\nPontos críticos: {result.critical_points}")
    print(f"Zonas de ambiguidade: {result.ambiguity_zones}")
