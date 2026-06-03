#!/usr/bin/env python
# =====================================================================
# FULL PIPELINE v1 — Pipeline Integrado C5
# =====================================================================
# Integra ParallelChain + SynthesisEngine com seleção automática de
# estratégia baseada em perfil do problema.
#
# Pipeline completo:
#   1. analyze_problem → ProblemProfile
#   2. select_strategy → strategy
#   3. run_chains (ParallelChain) → list[ChainResult]
#   4. synthesize (SynthesisEngine) → SynthesisResult
#   5. measure & report → FullPipelineResult / BenchmarkResult
# =====================================================================

import sys, os, time, re
from dataclasses import dataclass, field
from typing import Optional

# Path setup
_V12_AGENTS = os.path.dirname(__file__)
if _V12_AGENTS not in sys.path:
    sys.path.insert(0, _V12_AGENTS)

from parallel_chain import ParallelChain, ChainResult
from synthesis_engine import SynthesisEngine, SynthesisResult


# =====================================================================
# CONSTANTS — Heurísticas de Seleção de Estratégia
# =====================================================================

STRATEGY_RULES: dict[str, str] = {
    "code":        "weighted_vote",
    "math":        "weighted_vote",
    "physics":     "weighted_vote",
    "debate":      "debate",
    "controversy": "debate",
    "creative":    "ensemble",
    "exploration": "ensemble",
    "quick":       "best_of",
    "simple":      "best_of",
}

COMPLEXITY_MAP: dict[str, str] = {
    "low":      "best_of",
    "medium":   "weighted_vote",
    "high":     "debate",
    "research": "ensemble",
}


# =====================================================================
# DATA STRUCTURES
# =====================================================================

@dataclass
class ProblemProfile:
    """Perfil do problema para seleção de estratégia."""
    complexity: str = "medium"           # low | medium | high | research
    domain: str = "general"              # math | physics | code | debate | creative | general
    num_chains: int = 4                  # Número de cadeias paralelas
    preferred_strategy: Optional[str] = None  # Override explícito


@dataclass
class FullPipelineResult:
    """Resultado completo do pipeline."""
    answer: str
    strategy: str
    confidence: float
    chain_count: int
    total_elapsed_ms: float
    chain_results: list = field(default_factory=list)
    synthesis_result: Optional[SynthesisResult] = None


@dataclass
class BenchmarkResult:
    """Resultado do benchmark empírico."""
    total_elapsed_ms: float
    chain_times_ms: list = field(default_factory=list)
    synthesis_time_ms: float = 0.0
    speedup_vs_sequential: float = 0.0
    chain_pci_scores: list = field(default_factory=list)
    mean_pci: float = 0.0
    strategy_used: str = ""
    synthesis_confidence: float = 0.0
    chain_count: int = 0
    final_answer: str = ""


# =====================================================================
# FULL PIPELINE
# =====================================================================

class FullPipeline:
    """
    Pipeline completo de raciocínio paralelo com seleção automática.

    Uso:
        fp = FullPipeline()
        result = fp.run("Solve x^2 = 4")
        benchmark = fp.run_with_benchmark("Solve x^2 = 4")

    Ou com perfil customizado:
        profile = ProblemProfile(domain="math", complexity="low")
        fp = FullPipeline(profile=profile)
        result = fp.run("Solve x^2 = 4", strategy="best_of")
    """

    def __init__(self, profile: Optional[ProblemProfile] = None):
        self.profile = profile or ProblemProfile()
        self.parallel_chain = ParallelChain(max_workers=self.profile.num_chains)
        self.synthesis_engine = SynthesisEngine()

    # ----------------------------------------------------------------
    # FASE 1: Análise do Problema
    # ----------------------------------------------------------------

    def analyze_problem(self, problem: str) -> ProblemProfile:
        """
        Analisa o problema para determinar perfil (domínio + complexidade).

        Args:
            problem: Texto do problema a ser analisado

        Returns:
            ProblemProfile com domínio e complexidade detectados
        """
        problem_lower = problem.lower()

        # --- Detecção de domínio por keywords (word boundaries) ---
        domain = "general"
        domain_keywords: dict[str, list[str]] = {
            "math": [
                "math", "equation", "theorem", "proof", "calculate",
                "sum", "integral", "derivative", "algebra", "geometry",
                "matrix", "vector", "statistics", "probability",
            ],
            "physics": [
                "physics", "force", "energy", "velocity", "mass",
                "acceleration", "gravity", "wave", "quantum",
                "thermodynamics", "electric", "magnetic",
            ],
            "code": [
                "code", "function", "algorithm", "program",
                "implement", "debug", "bug", "syntax",
                "python", "javascript", "java", "typescript",
                "software", "api", "database", "compile",
            ],
            "debate": [
                "debate", "argue", "controversy", "pros and cons",
                "vs", "versus", "opinion", "ethical",
                "should we", "is it better",
            ],
            "creative": [
                "creative", "design", "brainstorm", "idea",
                "imagine", "generate", "create", "innovate",
                "novel", "original",
            ],
        }

        for d, keywords in domain_keywords.items():
            if any(re.search(rf'\b{re.escape(kw)}\b', problem_lower) for kw in keywords):
                domain = d
                break

        # --- Detecção de complexidade ---
        word_count = len(problem_lower.split())
        if word_count < 10:
            complexity = "low"
        elif word_count < 30:
            complexity = "medium"
        elif word_count < 60:
            complexity = "high"
        else:
            complexity = "research"

        # Preserva num_chains do perfil original
        self.profile = ProblemProfile(
            complexity=complexity,
            domain=domain,
            num_chains=self.profile.num_chains,
            preferred_strategy=self.profile.preferred_strategy,
        )
        return self.profile

    # ----------------------------------------------------------------
    # FASE 2: Seleção de Estratégia
    # ----------------------------------------------------------------

    def select_strategy(self, profile: Optional[ProblemProfile] = None) -> str:
        """
        Seleciona estratégia de síntese baseada no perfil.

        Regras (em ordem de precedência):
        1. preferred_strategy (override explícito)
        2. complexidade "research" → ensemble (sobrescreve domínio)
        3. complexidade "high" → debate (sobrescreve domínio)
        4. Regra de domínio (STRATEGY_RULES)
        5. Regra de complexidade baixa/média (COMPLEXITY_MAP)
        6. Default: weighted_vote

        Args:
            profile: Perfil do problema (usa self.profile se None)

        Returns:
            Nome da estratégia
        """
        p = profile or self.profile

        # 1. Override explícito
        if p.preferred_strategy:
            return p.preferred_strategy

        # 2. Research sempre usa ensemble (complexidade > domínio)
        if p.complexity == "research":
            return "ensemble"

        # 3. High sempre usa debate (complexidade > domínio)
        if p.complexity == "high":
            return "debate"

        # 4. Regra de domínio
        strategy = STRATEGY_RULES.get(p.domain)
        if strategy:
            return strategy

        # 5. Regra de complexidade (low → best_of, medium → weighted_vote)
        strategy = COMPLEXITY_MAP.get(p.complexity)
        if strategy:
            return strategy

        # 6. Default
        return "weighted_vote"

    # ----------------------------------------------------------------
    # FASE 3-5: Execução Completa
    # ----------------------------------------------------------------

    def run(
        self,
        problem: str,
        strategy: Optional[str] = None,
    ) -> FullPipelineResult:
        """
        Executa pipeline completo: analyze → select → run → synthesize → report.

        Args:
            problem: Problema a ser resolvido
            strategy: Estratégia opcional (override da seleção automática)

        Returns:
            FullPipelineResult com resposta consolidada
        """
        start = time.time()

        # 1. Analisa problema
        profile = self.analyze_problem(problem)

        # 2. Seleciona estratégia
        if strategy is None:
            strategy = self.select_strategy(profile)

        # 3. Executa cadeias em paralelo
        chain_results = self.parallel_chain.run_chains(
            problem=problem,
            verify=False,
        )

        # 4. Sintetiza resultados
        synthesis = self.synthesis_engine.synthesize(
            chain_results,
            strategy=strategy,
        )

        elapsed = (time.time() - start) * 1000

        return FullPipelineResult(
            answer=synthesis.final_answer,
            strategy=synthesis.strategy,
            confidence=synthesis.confidence,
            chain_count=len(chain_results),
            total_elapsed_ms=elapsed,
            chain_results=chain_results,
            synthesis_result=synthesis,
        )

    # ----------------------------------------------------------------
    # Benchmark Empírico
    # ----------------------------------------------------------------

    def run_with_benchmark(self, problem: str) -> BenchmarkResult:
        """
        Executa pipeline com medição empírica detalhada.

        Calcula speedup simulando execução sequencial:
            speedup = sum(elapsed_ms) / max(elapsed_ms)

        Args:
            problem: Problema a ser resolvido

        Returns:
            BenchmarkResult com métricas detalhadas
        """
        start = time.time()

        # 1. Analisa e seleciona estratégia
        profile = self.analyze_problem(problem)
        strategy = self.select_strategy(profile)

        # 2. Executa cadeias em paralelo
        chain_results = self.parallel_chain.run_chains(
            problem=problem,
            verify=False,
        )

        # 3. Calcula speedup
        parallel_time = max(
            (r.elapsed_ms for r in chain_results),
            default=0.1,
        )
        sequential_time = sum(r.elapsed_ms for r in chain_results)
        speedup = sequential_time / max(parallel_time, 0.1)

        # 4. Sintetiza
        synthesis = self.synthesis_engine.synthesize(
            chain_results,
            strategy=strategy,
        )

        # 5. Métricas por cadeia
        chain_times = [r.elapsed_ms for r in chain_results]
        chain_pcis = [r.pci_score for r in chain_results]
        mean_pci = (
            sum(chain_pcis) / max(len(chain_pcis), 1)
            if chain_pcis
            else 0.0
        )

        total_elapsed = (time.time() - start) * 1000

        return BenchmarkResult(
            total_elapsed_ms=total_elapsed,
            chain_times_ms=chain_times,
            synthesis_time_ms=synthesis.elapsed_ms,
            speedup_vs_sequential=round(speedup, 2),
            chain_pci_scores=chain_pcis,
            mean_pci=round(mean_pci, 2),
            strategy_used=synthesis.strategy,
            synthesis_confidence=synthesis.confidence,
            chain_count=len(chain_results),
            final_answer=synthesis.final_answer,
        )
