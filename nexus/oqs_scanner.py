#!/usr/bin/env python3
"""
Optimal Question Scanner (SPEC-056) — R45 Fase A.

Gera, vetoriza e seleciona a pergunta otima que maximiza a reducao
de incerteza com minimo esforco cognitivo.

Pipeline: UncertaintyScanner → QuestionVectorizer → ConvergenceScore → Selector
"""

import math
import re
import uuid
from dataclasses import dataclass, field
from typing import Optional


class UncertaintyScanner:
    """Escaneia incertezas de um problema.

    Etapas:
    1. Identificar categorias de incerteza
    2. Detectar ruido estrutural
    3. Extrair texto filtrado
    """

    UNCERTAINTY_KEYWORDS = {
        "epistemic": [
            "nao sei", "desconhecido", "incerto", "talvez",
            "duvida", "ambiguo", "indeterminado",
        ],
        "aleatory": [
            "aleatorio", "estocastico", "probabilidade",
            "variacao", "imprevisivel", "caotico",
        ],
        "structural": [
            "complexo", "emergente", "nao-linear",
            "dinamico", "interdependente", "acoplado",
        ],
        "semantic": [
            "ambiguo", "vago", "impreciso", "mal-definido",
            "interpretacao", "polissemico",
        ],
    }

    NOISE_PATTERNS = [
        r'\bexemplos?\b', r'\bilustra[çc][aã]o\b',
        r'\bdetalhes?\b', r'\bespecificamente\b',
        r'\bisto [ée]\b', r'\bcomo por exemplo\b',
    ]

    def scan(self, text: str) -> dict:
        """Escaneia incertezas no texto do problema."""
        text_lower = text.lower()

        # Categorias de incerteza
        categories = {}
        for cat, keywords in self.UNCERTAINTY_KEYWORDS.items():
            matches = [kw for kw in keywords if kw in text_lower]
            categories[cat] = {
                "detected": len(matches) > 0,
                "matches": matches,
                "count": len(matches),
            }

        # Ruido estrutural
        noise_matches = []
        for pattern in self.NOISE_PATTERNS:
            found = re.findall(pattern, text_lower)
            noise_matches.extend(found)

        # Texto filtrado (remover ruido)
        filtered = text
        for pattern in self.NOISE_PATTERNS:
            filtered = re.sub(pattern, "", filtered, flags=re.IGNORECASE)

        return {
            "uncertainty_categories": categories,
            "structural_noise": {
                "patterns_found": len(noise_matches),
                "matches": noise_matches[:10],
                "noise_score": min(len(noise_matches) * 10, 100),
            },
            "filtered_text": filtered.strip(),
            "total_uncertainty_score": sum(
                1 for c in categories.values() if c["detected"]
            ) * 25,
        }


class QuestionVectorizer:
    """Vetoriza perguntas para comparacao.

    Implementa um vetorizador simples baseado em features:
    - Comprimento da pergunta
    - Presenca de termos de acao (verbos)
    - Presenca de termos de qualidade
    - Cobertura semântica
    """

    ACTION_TERMS = [
        "como", "qual", "quais", "onde", "quando", "por que",
        "otimizar", "reduzir", "aumentar", "melhorar", "implementar",
        "comparar", "avaliar", "medir", "validar", "testar",
    ]
    QUALITY_TERMS = [
        "melhor", "otimo", "eficiente", "eficaz", "robusto",
        "escalavel", "confiavel", "preciso", "rapido",
    ]

    def vectorize(self, questions: list[str]) -> list[list[float]]:
        """Vetoriza lista de perguntas em vectores de features."""
        vectors = []
        for q in questions:
            q_lower = q.lower()
            words = q_lower.split()

            features = [
                len(q) / 200.0,                           # comprimento normalizado
                sum(1 for t in self.ACTION_TERMS if t in q_lower) / 5.0,  # acao
                sum(1 for t in self.QUALITY_TERMS if t in q_lower) / 3.0, # qualidade
                len(set(words)) / max(len(words), 1),     # diversidade lexical
                min(len(words) / 20.0, 1.0),               # densidade
            ]
            vectors.append(features)

        return vectors


class ConvergenceScore:
    """Calcula Convergence Score (CS) para perguntas.

    CS = URS + SVS - DRI - CCI

    Onde:
    - URS: Uncertainty Reduction Score (0-35)
    - SVS: Search Space Reduction Score (0-35)
    - DRI: Dispersion Risk Index (0-15)
    - CCI: Cognitive Cost Index (0-15)
    """

    def calculate(
        self,
        question: str,
        uncertainty_reduction: float,
        search_space_reduction: float,
        dispersion_risk: float = 0.0,
        cognitive_cost: float = 0.0,
    ) -> float:
        """Calcula CS para uma pergunta."""
        urs = min(uncertainty_reduction / 10.0, 1.0) * 35
        svs = min(search_space_reduction / 10.0, 1.0) * 35
        dri = min(dispersion_risk / 10.0, 1.0) * 15
        cci = min(cognitive_cost / 10.0, 1.0) * 15

        cs = urs + svs - dri - cci
        return round(max(cs, 0), 2)


class OQSPipeline:
    """Pipeline completo OQS."""

    def __init__(self):
        self.scanner = UncertaintyScanner()
        self.vectorizer = QuestionVectorizer()
        self.scorer = ConvergenceScore()

    def select_best_question(
        self,
        problem: str,
        candidates: list[str],
    ) -> Optional[dict]:
        """Seleciona a melhor pergunta do conjunto."""
        if not candidates:
            return None

        # 1. Escanear incertezas do problema
        uncertainty = self.scanner.scan(problem)

        # 2. Vetorizar perguntas
        vectors = self.vectorizer.vectorize(candidates)

        # 3. Calcular score para cada pergunta
        scored = []
        for i, (q, vec) in enumerate(zip(candidates, vectors)):
            # Features do vetor influenciam os componentes do CS
            urs = 5.0 + vec[1] * 5.0  # acao
            svs = 5.0 + vec[2] * 5.0  # qualidade
            dri = 5.0 - vec[3] * 3.0  # diversidade (mais diverso = menos risco)
            cci = 5.0 - vec[4] * 2.0  # densidade

            cs = self.scorer.calculate(
                question=q,
                uncertainty_reduction=urs,
                search_space_reduction=svs,
                dispersion_risk=max(dri, 0),
                cognitive_cost=max(cci, 0),
            )

            scored.append({
                "question": q,
                "score": cs,
                "vector": vec,
                "index": i,
            })

        # 4. Selecionar melhor
        scored.sort(key=lambda x: x["score"], reverse=True)

        return scored[0]

    def full_pipeline(self, problem: str, candidates: list[str]) -> dict:
        """Executa pipeline completo com diagnostico."""
        # Uncertainty scan
        uncertainty = self.scanner.scan(problem)

        # Select best
        best = self.select_best_question(problem, candidates)

        return {
            "problem": problem,
            "uncertainty_score": uncertainty["total_uncertainty_score"],
            "noise_score": uncertainty["structural_noise"]["noise_score"],
            "candidates_analyzed": len(candidates),
            "best_question": best["question"] if best else None,
            "best_score": best["score"] if best else 0,
            "all_scores": sorted(
                [{"q": s["question"], "score": s["score"]}
                 for s in ([best] if best else [])],
                key=lambda x: x["score"],
                reverse=True,
            ),
        }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OQS Scanner")
    parser.add_argument("--problem", type=str, help="Problema para analisar")
    parser.add_argument("--candidates", nargs="+",
                        help="Perguntas candidatas")
    parser.add_argument("--scan", action="store_true",
                        help="Apenas escanear incertezas")
    args = parser.parse_args()

    if args.scan and args.problem:
        scanner = UncertaintyScanner()
        result = scanner.scan(args.problem)
        print(f"=== Uncertainty Scan ===")
        print(f"Score: {result['total_uncertainty_score']}")
        print(f"Noise: {result['structural_noise']['noise_score']}")
        for cat, info in result["uncertainty_categories"].items():
            status = "✓" if info["detected"] else "✗"
            print(f"  {status} {cat}: {info['count']} matches")

    if args.problem and args.candidates:
        pipeline = OQSPipeline()
        result = pipeline.full_pipeline(args.problem, args.candidates)
        print(f"\n=== OQS Pipeline ===")
        print(f"Problem: {result['problem'][:60]}")
        print(f"Best: {result['best_question']} (score: {result['best_score']})")
        print(f"Uncertainty: {result['uncertainty_score']}")
        print(f"Noise: {result['noise_score']}")
