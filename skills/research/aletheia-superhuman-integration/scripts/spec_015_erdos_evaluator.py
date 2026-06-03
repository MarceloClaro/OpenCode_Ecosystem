#!/usr/bin/env python3
"""
SPEC-015: ErdosEvaluator
=========================

Implementa avaliação de Erdős 700 problems (Feng et al., 2026).

Responsabilidades:
1. Carregar dataset Erdős 700 (ou subset para teste)
2. Executar AletheiaSession em cada problema
3. Grading por especialistas (simulado para teste)
4. Métricas: technically_correct, meaningfully_correct, autonomy_level
5. Comparação com baseline Aletheia

Feng et al. (2026b) Evaluation Protocol:
- 700 "Open" problems (Bloom's Erdős database)
- Aletheia returned solutions: 212/700
- Technically correct: 63/212 (29.7%)
- Meaningfully correct: 13/212 (6.1%)
- Autonomous resolutions: 4 (Erdős-652, 654, 1040, 1051)

Seed: 42 | Reproducível | TDD: 8 testes
"""

import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random

SEED = 42
random.seed(SEED)


class ErdosProblemDifficulty(Enum):
    OLYMPIAD = "olympiad"
    PHD_EXERCISE = "phd_exercise"
    RESEARCH_OPEN = "research_open"


class ErdosGradingLevel(Enum):
    NO_SOLUTION = "no_solution"  # Não retornou solução
    TECHNICALLY_INCORRECT = "technically_incorrect"  # Solução errada
    TECHNICALLY_CORRECT = "technically_correct"  # Solução correta (pode ter gaps)
    MEANINGFULLY_CORRECT = "meaningfully_correct"  # Solução completa e publicável
    NOVEL_CONTRIBUTION = "novel_contribution"  # Novo resultado demonstrado


@dataclass
class ErdosProblem:
    """Um problema da coleção Erdős."""
    erdos_id: str  # ex: "Erdos-1051"
    statement: str
    domain: str  # "number_theory", "combinatorics", etc
    difficulty: ErdosProblemDifficulty
    known_solution: Optional[str] = None  # Solução conhecida (para validação)
    references: List[str] = field(default_factory=list)
    source_year: int = 0


@dataclass
class EvaluationResult:
    """Resultado da avaliação de um problema."""
    problem_id: str
    grading: ErdosGradingLevel
    solution_returned: bool
    solution_quality: float  # 0.0-1.0 (simulado para teste)
    expert_comments: List[str] = field(default_factory=list)
    autonomy_level: str = "L0"  # L0-L4
    evaluation_date: str = ""


@dataclass
class ErdosEvaluationMetrics:
    """Métricas aggregadas da avaliação."""
    total_problems: int
    solutions_returned: int
    technically_correct: int
    meaningfully_correct: int
    novel_contributions: int
    success_rate_returned: float  # solutions_returned / total
    success_rate_technically: float  # technically_correct / solutions_returned
    success_rate_meaningful: float  # meaningfully_correct / solutions_returned
    average_autonomy_level: float
    comparison_with_aletheia: Dict  # delta vs baseline


class ErdosDatasetLoader:
    """Carrega problemas Erdős (versão simulada para teste)."""
    
    def __init__(self, use_realistic_subset: bool = True):
        """
        Args:
            use_realistic_subset: Se True, simula 700 problemas com distribuição realista.
                                Se False, apenas problemas de teste manuais.
        """
        self.problems: List[ErdosProblem] = []
        self._load_problems(use_realistic_subset)
    
    def _load_problems(self, use_realistic: bool):
        """Carrega problemas."""
        
        if use_realistic:
            # Simula 700 problemas com distribuição por domínio e dificuldade
            # Aletheia evaluation: 212 returned, 63 technically correct, 13 meaningful, 4 novel
            
            domains = ["number_theory", "combinatorics", "algebra", "geometry", "analysis"]
            difficulties = list(ErdosProblemDifficulty)
            
            for i in range(700):
                domain = random.choice(domains)
                difficulty = random.choice(difficulties)
                
                self.problems.append(ErdosProblem(
                    erdos_id=f"Erdos-{1000+i}",
                    statement=f"[Simulated] Problem {i+1} in {domain}",
                    domain=domain,
                    difficulty=difficulty,
                    source_year=1970 + random.randint(0, 50),
                ))
        
        else:
            # Apenas problemas manualmente anotados (para teste)
            self.problems = [
                ErdosProblem(
                    erdos_id="Erdos-652",
                    statement="Conjecture about distances in finite sets",
                    domain="combinatorics",
                    difficulty=ErdosProblemDifficulty.RESEARCH_OPEN,
                    source_year=1988,
                ),
                ErdosProblem(
                    erdos_id="Erdos-654",
                    statement="Graph coloring with constraints",
                    domain="combinatorics",
                    difficulty=ErdosProblemDifficulty.RESEARCH_OPEN,
                    source_year=1990,
                ),
                ErdosProblem(
                    erdos_id="Erdos-1040",
                    statement="Number-theoretic inequality",
                    domain="number_theory",
                    difficulty=ErdosProblemDifficulty.RESEARCH_OPEN,
                    source_year=1995,
                ),
                ErdosProblem(
                    erdos_id="Erdos-1051",
                    statement="Algebraic conjecture",
                    domain="algebra",
                    difficulty=ErdosProblemDifficulty.RESEARCH_OPEN,
                    source_year=1998,
                ),
            ]
    
    def get_problem(self, problem_id: str) -> Optional[ErdosProblem]:
        """Recupera um problema por ID."""
        for p in self.problems:
            if p.erdos_id == problem_id:
                return p
        return None
    
    def list_problems(self, domain: Optional[str] = None,
                      difficulty: Optional[ErdosProblemDifficulty] = None) -> List[ErdosProblem]:
        """Lista problemas com filtros opcionais."""
        filtered = self.problems
        if domain:
            filtered = [p for p in filtered if p.domain == domain]
        if difficulty:
            filtered = [p for p in filtered if p.difficulty == difficulty]
        return filtered
    
    def get_subset(self, size: int) -> List[ErdosProblem]:
        """Retorna subset aleatório de size problemas."""
        return random.sample(self.problems, min(size, len(self.problems)))


class ErdosGrader:
    """
    Simula grading por especialistas.
    
    Na prática, seria feito por matemáticos; aqui simulamos com heurísticas.
    """
    
    def __init__(self, seed: int = SEED):
        random.seed(seed)
    
    def grade_solution(self, problem: ErdosProblem, solution: Optional[str],
                       aletheia_verifier_score: float = 0.0,
                       cora_checks_passed: int = 7) -> EvaluationResult:
        """
        Grada uma solução para um problema.
        
        Args:
            problem: O problema Erdős
            solution: Texto da solução (None se não foi retornada)
            aletheia_verifier_score: Score do Aletheia verifier (0-1)
            cora_checks_passed: Quantos dos 7 checks Cora passaram
        
        Returns:
            EvaluationResult com grading
        """
        
        result = EvaluationResult(
            problem_id=problem.erdos_id,
            solution_returned=solution is not None,
            grading=ErdosGradingLevel.NO_SOLUTION,
            solution_quality=0.0,
        )
        
        if solution is None:
            return result
        
        # Estima qualidade baseada em verifier scores
        cora_score = cora_checks_passed / 7.0
        combined_score = (aletheia_verifier_score + cora_score) / 2
        result.solution_quality = combined_score
        
        # Determina grading
        if combined_score < 0.3:
            result.grading = ErdosGradingLevel.TECHNICALLY_INCORRECT
            result.autonomy_level = "L0"
            result.expert_comments = ["Solution fundamentally flawed"]
        
        elif combined_score < 0.6:
            result.grading = ErdosGradingLevel.TECHNICALLY_CORRECT
            result.autonomy_level = "L1"
            result.expert_comments = ["Correct but with gaps or incomplete proof"]
        
        elif combined_score < 0.85:
            result.grading = ErdosGradingLevel.MEANINGFULLY_CORRECT
            result.autonomy_level = "L2"
            result.expert_comments = ["Publication-grade solution with minor refinements"]
        
        else:
            result.grading = ErdosGradingLevel.NOVEL_CONTRIBUTION
            result.autonomy_level = "L3"
            result.expert_comments = ["Significant new insight or improved proof"]
        
        return result


class ErdosEvaluator:
    """Orquestrador da avaliação Erdős 700."""
    
    ALETHEIA_BASELINE = {
        "total": 700,
        "solutions_returned": 212,
        "technically_correct": 63,
        "meaningfully_correct": 13,
        "novel_contributions": 4,
    }
    
    def __init__(self, verbose: bool = False):
        self.dataset = ErdosDatasetLoader(use_realistic_subset=False)  # Para teste
        self.grader = ErdosGrader()
        self.results: Dict[str, EvaluationResult] = {}
        self.verbose = verbose
    
    def evaluate_problem(self, problem: ErdosProblem, solution: Optional[str],
                        aletheia_score: float, cora_passed: int) -> EvaluationResult:
        """Avalia um único problema."""
        result = self.grader.grade_solution(problem, solution, aletheia_score, cora_passed)
        self.results[problem.erdos_id] = result
        
        if self.verbose:
            print(f"  [{problem.erdos_id}] {result.grading.value} | Quality: {result.solution_quality:.2f}")
        
        return result
    
    def evaluate_batch(self, problems: List[ErdosProblem],
                       solution_generator) -> Dict[str, EvaluationResult]:
        """
        Avalia um batch de problemas.
        
        Args:
            problems: Lista de problemas
            solution_generator: Função que retorna (solution, aletheia_score, cora_passed)
                                para um dado problema
        """
        for problem in problems:
            solution, aletheia_score, cora_passed = solution_generator(problem)
            self.evaluate_problem(problem, solution, aletheia_score, cora_passed)
        
        return self.results
    
    def compute_metrics(self) -> ErdosEvaluationMetrics:
        """Computa métricas aggregadas."""
        
        if not self.results:
            return ErdosEvaluationMetrics(
                total_problems=0,
                solutions_returned=0,
                technically_correct=0,
                meaningfully_correct=0,
                novel_contributions=0,
                success_rate_returned=0.0,
                success_rate_technically=0.0,
                success_rate_meaningful=0.0,
                average_autonomy_level=0.0,
                comparison_with_aletheia={},
            )
        
        total = len(self.results)
        returned = sum(1 for r in self.results.values() if r.solution_returned)
        technically = sum(1 for r in self.results.values() 
                         if r.grading in [ErdosGradingLevel.TECHNICALLY_CORRECT,
                                         ErdosGradingLevel.MEANINGFULLY_CORRECT,
                                         ErdosGradingLevel.NOVEL_CONTRIBUTION])
        meaningful = sum(1 for r in self.results.values()
                        if r.grading in [ErdosGradingLevel.MEANINGFULLY_CORRECT,
                                        ErdosGradingLevel.NOVEL_CONTRIBUTION])
        novel = sum(1 for r in self.results.values()
                   if r.grading == ErdosGradingLevel.NOVEL_CONTRIBUTION)
        
        # Autonomy levels: L0=0, L1=1, L2=2, L3=3, L4=4
        autonomy_mapping = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}
        autonomy_values = [autonomy_mapping.get(r.autonomy_level, 0) for r in self.results.values()]
        avg_autonomy = sum(autonomy_values) / len(autonomy_values) if autonomy_values else 0.0
        
        # Comparação com Aletheia
        comparison = {
            "opencode_vs_aletheia_solutions_returned": f"{returned}/{total} vs {self.ALETHEIA_BASELINE['solutions_returned']}/{self.ALETHEIA_BASELINE['total']}",
            "opencode_vs_aletheia_technically_correct": f"{technically}/{returned} vs {self.ALETHEIA_BASELINE['technically_correct']}/{self.ALETHEIA_BASELINE['solutions_returned']}",
            "opencode_vs_aletheia_meaningful": f"{meaningful}/{returned} vs {self.ALETHEIA_BASELINE['meaningfully_correct']}/{self.ALETHEIA_BASELINE['solutions_returned']}",
            "delta_meaningful_pct": f"{(meaningful/returned*100 if returned > 0 else 0):.1f}% vs {(self.ALETHEIA_BASELINE['meaningfully_correct']/self.ALETHEIA_BASELINE['solutions_returned']*100):.1f}%",
        }
        
        return ErdosEvaluationMetrics(
            total_problems=total,
            solutions_returned=returned,
            technically_correct=technically,
            meaningfully_correct=meaningful,
            novel_contributions=novel,
            success_rate_returned=returned / total if total > 0 else 0.0,
            success_rate_technically=technically / returned if returned > 0 else 0.0,
            success_rate_meaningful=meaningful / returned if returned > 0 else 0.0,
            average_autonomy_level=avg_autonomy,
            comparison_with_aletheia=comparison,
        )
    
    def generate_report(self) -> Dict:
        """Gera relatório JSON com resultados."""
        metrics = self.compute_metrics()
        
        return {
            "evaluation_metadata": {
                "total_problems_evaluated": metrics.total_problems,
                "dataset": "Erdos 700 (simulated subset for SPEC-015 testing)",
                "evaluation_date": "2026-05-30",
            },
            "metrics": {
                "solutions_returned": metrics.solutions_returned,
                "technically_correct": metrics.technically_correct,
                "meaningfully_correct": metrics.meaningfully_correct,
                "novel_contributions": metrics.novel_contributions,
                "success_rates": {
                    "returned": round(metrics.success_rate_returned, 3),
                    "technically_correct_of_returned": round(metrics.success_rate_technically, 3),
                    "meaningful_of_returned": round(metrics.success_rate_meaningful, 3),
                },
                "average_autonomy_level": round(metrics.average_autonomy_level, 2),
            },
            "comparison_with_aletheia": metrics.comparison_with_aletheia,
            "baseline_aletheia": self.ALETHEIA_BASELINE,
            "results_by_problem": {
                pid: {
                    "grading": r.grading.value,
                    "quality": round(r.solution_quality, 2),
                    "autonomy_level": r.autonomy_level,
                    "comments": r.expert_comments,
                }
                for pid, r in self.results.items()
            }
        }


if __name__ == "__main__":
    # Test: Simulated Erdős evaluation on 4 problems
    evaluator = ErdosEvaluator(verbose=True)
    
    # Recupera 4 problemas conhecidos
    problems = evaluator.dataset.problems
    
    # Simula generator de soluções
    def mock_solution_generator(problem):
        # Simula: alguns problemas retornam soluções, com scores variados
        if problem.erdos_id in ["Erdos-652", "Erdos-654"]:
            return ("Simulated solution", 0.85, 6)  # Aletheia score 0.85, 6/7 Cora checks
        elif problem.erdos_id == "Erdos-1040":
            return ("Simulated solution", 0.72, 5)
        elif problem.erdos_id == "Erdos-1051":
            return ("Simulated solution", 0.92, 7)  # Novel contribution
        else:
            return (None, 0.0, 0)  # No solution
    
    # Avalia batch
    evaluator.evaluate_batch(problems, mock_solution_generator)
    
    # Compute e imprime métricas
    metrics = evaluator.compute_metrics()
    print(f"\nErdős Evaluation Metrics:")
    print(f"  Total problems: {metrics.total_problems}")
    print(f"  Solutions returned: {metrics.solutions_returned}/{metrics.total_problems}")
    print(f"  Technically correct: {metrics.technically_correct}")
    print(f"  Meaningfully correct: {metrics.meaningfully_correct}")
    print(f"  Success rate (meaningful): {metrics.success_rate_meaningful:.2%}")
    print(f"  Average autonomy level: {metrics.average_autonomy_level:.2f}")
    
    # Report
    report = evaluator.generate_report()
    print(f"\nComparison with Aletheia:")
    for key, value in metrics.comparison_with_aletheia.items():
        print(f"  {key}: {value}")
