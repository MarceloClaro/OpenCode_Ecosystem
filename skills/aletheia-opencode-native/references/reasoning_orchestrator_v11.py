"""
ReasoningOrchestrator-v11 — Orquestrador de 68 Tipos de Raciocínio

Integra:
- 15 Tipos de Teoria dos Jogos
- 53 Outros tipos (lógica, dialética, decisão, estratégia, inovação)
Total: 68 tipos em 12 categorias

Seleção automática baseada em:
- Categoria do problema (Geometry, Algebra, Combinatorics, etc.)
- Dificuldade (IMO-easy, IMO-mid, IMO-hard)
- Padrões no enunciado
- Raciocínios aplicados previamente
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json


class ReasoningCategory(Enum):
    """12 Categorias de Raciocínio"""
    LOGIC = "LOGIC"                      # 5 tipos
    DIALECTIC = "DIALECTIC"              # 5 tipos
    GAME_THEORY = "GAME_THEORY"          # 15 tipos
    DECISION = "DECISION"                # 5 tipos
    STRATEGY = "STRATEGY"                # 5 tipos
    INNOVATION = "INNOVATION"            # 8 tipos
    ANALYSIS = "ANALYSIS"                # 5 tipos
    SYNTHESIS = "SYNTHESIS"              # 5 tipos
    ENUMERATION = "ENUMERATION"          # 3 tipos
    CONSTRUCTION = "CONSTRUCTION"        # 4 tipos
    INDUCTION = "INDUCTION"              # 3 tipos
    APPROXIMATION = "APPROXIMATION"      # 5 tipos


# Mapeamento de 68 tipos de raciocínio
REASONING_TYPES_V11 = {
    # 1. LOGIC (5 tipos)
    "PROPOSITIONAL_LOGIC": {"category": ReasoningCategory.LOGIC, "score": 0.7},
    "FIRST_ORDER_LOGIC": {"category": ReasoningCategory.LOGIC, "score": 0.75},
    "PROOF_BY_CONTRADICTION": {"category": ReasoningCategory.LOGIC, "score": 0.8},
    "LOGICAL_EQUIVALENCE": {"category": ReasoningCategory.LOGIC, "score": 0.65},
    "RESOLUTION_METHOD": {"category": ReasoningCategory.LOGIC, "score": 0.6},
    
    # 2. DIALECTIC (5 tipos)
    "THESIS_ANTITHESIS": {"category": ReasoningCategory.DIALECTIC, "score": 0.65},
    "HEGELIAN_SYNTHESIS": {"category": ReasoningCategory.DIALECTIC, "score": 0.7},
    "SOCRATIC_METHOD": {"category": ReasoningCategory.DIALECTIC, "score": 0.6},
    "DIALECTICAL_NEGATION": {"category": ReasoningCategory.DIALECTIC, "score": 0.65},
    "ARGUMENTATION_STRUCTURE": {"category": ReasoningCategory.DIALECTIC, "score": 0.62},
    
    # 3. GAME THEORY (15 tipos) — importados do reasoning_game_theory.py
    "NASH_EQUILIBRIUM": {"category": ReasoningCategory.GAME_THEORY, "score": 0.8},
    "MINIMAX_STRATEGY": {"category": ReasoningCategory.GAME_THEORY, "score": 0.75},
    "PARETO_OPTIMALITY": {"category": ReasoningCategory.GAME_THEORY, "score": 0.7},
    "DOMINANT_STRATEGY": {"category": ReasoningCategory.GAME_THEORY, "score": 0.65},
    "COALITION_FORMATION": {"category": ReasoningCategory.GAME_THEORY, "score": 0.7},
    "ZERO_SUM_ANALYSIS": {"category": ReasoningCategory.GAME_THEORY, "score": 0.75},
    "COOPERATIVE_SOLUTION": {"category": ReasoningCategory.GAME_THEORY, "score": 0.65},
    "PRISONERS_DILEMMA": {"category": ReasoningCategory.GAME_THEORY, "score": 0.6},
    "SYMMETRY_BREAKING": {"category": ReasoningCategory.GAME_THEORY, "score": 0.7},
    "SYMMETRIC_EQUILIBRIUM": {"category": ReasoningCategory.GAME_THEORY, "score": 0.75},
    "INFORMATION_ASYMMETRY": {"category": ReasoningCategory.GAME_THEORY, "score": 0.65},
    "SIGNALING_STRATEGY": {"category": ReasoningCategory.GAME_THEORY, "score": 0.6},
    "EVOLUTIONARY_STABLE": {"category": ReasoningCategory.GAME_THEORY, "score": 0.7},
    "SEQUENTIAL_GAME": {"category": ReasoningCategory.GAME_THEORY, "score": 0.75},
    "POTENTIAL_FUNCTION": {"category": ReasoningCategory.GAME_THEORY, "score": 0.8},
    
    # 4. DECISION (5 tipos)
    "EXPECTED_VALUE": {"category": ReasoningCategory.DECISION, "score": 0.7},
    "UTILITY_THEORY": {"category": ReasoningCategory.DECISION, "score": 0.65},
    "DECISION_TREE": {"category": ReasoningCategory.DECISION, "score": 0.65},
    "REGRET_ANALYSIS": {"category": ReasoningCategory.DECISION, "score": 0.6},
    "OPTIMAL_STOPPING": {"category": ReasoningCategory.DECISION, "score": 0.7},
    
    # 5. STRATEGY (5 tipos)
    "DIVIDE_AND_CONQUER": {"category": ReasoningCategory.STRATEGY, "score": 0.8},
    "GREEDY_ALGORITHM": {"category": ReasoningCategory.STRATEGY, "score": 0.75},
    "DYNAMIC_PROGRAMMING": {"category": ReasoningCategory.STRATEGY, "score": 0.8},
    "BACKTRACKING": {"category": ReasoningCategory.STRATEGY, "score": 0.7},
    "BRANCH_AND_BOUND": {"category": ReasoningCategory.STRATEGY, "score": 0.72},
    
    # 6. INNOVATION (8 tipos)
    "LATERAL_THINKING": {"category": ReasoningCategory.INNOVATION, "score": 0.65},
    "ANALOGICAL_REASONING": {"category": ReasoningCategory.INNOVATION, "score": 0.7},
    "METAPHOR_TRANSFER": {"category": ReasoningCategory.INNOVATION, "score": 0.6},
    "REFRAMING": {"category": ReasoningCategory.INNOVATION, "score": 0.65},
    "CONCEPTUAL_BLENDING": {"category": ReasoningCategory.INNOVATION, "score": 0.62},
    "CONSTRAINT_RELAXATION": {"category": ReasoningCategory.INNOVATION, "score": 0.68},
    "SERENDIPITY_HARVESTING": {"category": ReasoningCategory.INNOVATION, "score": 0.55},
    "PATTERN_INVERSION": {"category": ReasoningCategory.INNOVATION, "score": 0.65},
    
    # 7. ANALYSIS (5 tipos)
    "CASE_ANALYSIS": {"category": ReasoningCategory.ANALYSIS, "score": 0.75},
    "DIMENSIONAL_ANALYSIS": {"category": ReasoningCategory.ANALYSIS, "score": 0.7},
    "ASYMPTOTIC_ANALYSIS": {"category": ReasoningCategory.ANALYSIS, "score": 0.72},
    "PERTURBATION_METHOD": {"category": ReasoningCategory.ANALYSIS, "score": 0.68},
    "SCALING_ARGUMENT": {"category": ReasoningCategory.ANALYSIS, "score": 0.65},
    
    # 8. SYNTHESIS (5 tipos)
    "COMPOSITION": {"category": ReasoningCategory.SYNTHESIS, "score": 0.7},
    "INTEGRATION": {"category": ReasoningCategory.SYNTHESIS, "score": 0.68},
    "UNIFICATION": {"category": ReasoningCategory.SYNTHESIS, "score": 0.7},
    "EMERGENT_PROPERTY": {"category": ReasoningCategory.SYNTHESIS, "score": 0.62},
    "HOLISTIC_VIEW": {"category": ReasoningCategory.SYNTHESIS, "score": 0.65},
    
    # 9. ENUMERATION (3 tipos)
    "EXHAUSTIVE_SEARCH": {"category": ReasoningCategory.ENUMERATION, "score": 0.6},
    "PIGEONHOLE_PRINCIPLE": {"category": ReasoningCategory.ENUMERATION, "score": 0.75},
    "COUNTING_ARGUMENT": {"category": ReasoningCategory.ENUMERATION, "score": 0.7},
    
    # 10. CONSTRUCTION (4 tipos)
    "EXPLICIT_CONSTRUCTION": {"category": ReasoningCategory.CONSTRUCTION, "score": 0.75},
    "ITERATIVE_REFINEMENT": {"category": ReasoningCategory.CONSTRUCTION, "score": 0.7},
    "RECURSIVE_DEFINITION": {"category": ReasoningCategory.CONSTRUCTION, "score": 0.72},
    "ALGORITHM_IMPLEMENTATION": {"category": ReasoningCategory.CONSTRUCTION, "score": 0.68},
    
    # 11. INDUCTION (3 tipos)
    "MATHEMATICAL_INDUCTION": {"category": ReasoningCategory.INDUCTION, "score": 0.85},
    "STRONG_INDUCTION": {"category": ReasoningCategory.INDUCTION, "score": 0.82},
    "TRANSFINITE_INDUCTION": {"category": ReasoningCategory.INDUCTION, "score": 0.75},
    
    # 12. APPROXIMATION (5 tipos)
    "CONTINUOUS_RELAXATION": {"category": ReasoningCategory.APPROXIMATION, "score": 0.68},
    "DISCRETE_APPROXIMATION": {"category": ReasoningCategory.APPROXIMATION, "score": 0.65},
    "LINEAR_APPROXIMATION": {"category": ReasoningCategory.APPROXIMATION, "score": 0.7},
    "PROBABILISTIC_METHOD": {"category": ReasoningCategory.APPROXIMATION, "score": 0.75},
    "LIMIT_ARGUMENT": {"category": ReasoningCategory.APPROXIMATION, "score": 0.72},
}

assert len(REASONING_TYPES_V11) == 68, f"Expected 68 reasoning types, got {len(REASONING_TYPES_V11)}"


@dataclass
class ReasoningSelection:
    """Seleção de raciocínios aplicáveis a um problema"""
    problem_id: str
    selected_reasonings: List[Tuple[str, float]]  # (reasoning_type, score)
    reasoning_by_category: Dict[str, List[str]]
    confidence_score: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReasoningOrchestrator:
    """Orquestrador que seleciona 68 tipos de raciocínio automaticamente"""
    
    def __init__(self):
        """Inicializar orquestrador com 68 tipos"""
        self.reasoning_types = REASONING_TYPES_V11
        self.category_counts = self._count_by_category()
    
    def _count_by_category(self) -> Dict[str, int]:
        """Contar quantos tipos em cada categoria"""
        counts = {}
        for reasoning_type, info in self.reasoning_types.items():
            category = info["category"].value
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def select_for_problem(
        self,
        problem: Any,
        top_k: int = 5,
        use_category_hint: bool = True
    ) -> ReasoningSelection:
        """
        Selecionar raciocínios aplicáveis para um problema
        
        Args:
            problem: IMOProblem
            top_k: Quantos raciocínios retornar (default: 5)
            use_category_hint: Usar categoria do problema para priorizar
        
        Returns:
            ReasoningSelection com raciocínios recomendados
        """
        problem_id = getattr(problem, "problem_id", "Unknown")
        problem_category = getattr(problem, "category", "Algebra")
        problem_level = getattr(problem, "level", "IMO-mid")
        problem_statement = getattr(problem, "problem_statement", "")
        
        # Calcular scores para cada raciocínio
        scores = {}
        for reasoning_type, info in self.reasoning_types.items():
            score = info["score"]
            
            # Bônus por categoria do problema
            if use_category_hint:
                score += self._get_category_bonus(problem_category, reasoning_type)
            
            # Bônus por dificuldade
            score += self._get_difficulty_bonus(problem_level, reasoning_type)
            
            # Bônus por keywords no enunciado
            score += self._get_keyword_bonus(problem_statement, reasoning_type)
            
            # Cap at 1.0
            scores[reasoning_type] = min(1.0, score)
        
        # Ordenar por score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Selecionar top_k
        selected = ranked[:top_k]
        
        # Agrupar por categoria
        reasoning_by_category = {}
        for reasoning_type, score in selected:
            category = self.reasoning_types[reasoning_type]["category"].value
            if category not in reasoning_by_category:
                reasoning_by_category[category] = []
            reasoning_by_category[category].append(reasoning_type)
        
        # Calcular confidence
        avg_score = sum(s for _, s in selected) / len(selected) if selected else 0.0
        confidence = avg_score  # Simplificado: média dos scores
        
        result = ReasoningSelection(
            problem_id=problem_id,
            selected_reasonings=selected,
            reasoning_by_category=reasoning_by_category,
            confidence_score=confidence,
            metadata={
                "problem_category": problem_category,
                "problem_level": problem_level,
                "all_scores": dict(ranked),  # Debug info
            }
        )
        
        return result
    
    def _get_category_bonus(self, problem_category: str, reasoning_type: str) -> float:
        """Bônus baseado na categoria do problema"""
        bonuses = {
            "Geometry": {
                "GEOMETRIC_CONSTRUCTION": 0.15,
                "SYMMETRY_BREAKING": 0.12,
                "PERTURBATION_METHOD": 0.1,
            },
            "Algebra": {
                "MATHEMATICAL_INDUCTION": 0.15,
                "ALGEBRAIC_MANIPULATION": 0.12,
                "POLYNOMIAL_ANALYSIS": 0.1,
            },
            "Combinatorics": {
                "PIGEONHOLE_PRINCIPLE": 0.15,
                "COUNTING_ARGUMENT": 0.12,
                "ENUMERATION": 0.1,
            },
            "Number Theory": {
                "MATHEMATICAL_INDUCTION": 0.12,
                "MODULAR_ARITHMETIC": 0.1,
                "DIVISIBILITY_ANALYSIS": 0.08,
            },
            "Inequality": {
                "OPTIMIZATION": 0.12,
                "CALCULUS_METHOD": 0.1,
                "LAGRANGE_MULTIPLIERS": 0.08,
            },
        }
        
        category_bonuses = bonuses.get(problem_category, {})
        return category_bonuses.get(reasoning_type, 0.0)
    
    def _get_difficulty_bonus(self, problem_level: str, reasoning_type: str) -> float:
        """Bônus baseado na dificuldade"""
        advanced_reasonings = [
            "GAME_THEORY", "TRANSFINITE_INDUCTION", "PERTURBATION_METHOD",
            "PROBABILISTIC_METHOD", "EVOLUTIONARY_STABLE"
        ]
        
        if problem_level == "IMO-hard":
            # Hard problems benefit from advanced reasoning
            if any(adv in reasoning_type for adv in advanced_reasonings):
                return 0.1
        elif problem_level == "IMO-easy":
            # Easy problems benefit from direct reasoning
            direct_reasonings = ["EXPLICIT_CONSTRUCTION", "MATHEMATICAL_INDUCTION"]
            if any(direct in reasoning_type for direct in direct_reasonings):
                return 0.1
        
        return 0.0
    
    def _get_keyword_bonus(self, problem_statement: str, reasoning_type: str) -> float:
        """Bônus baseado em keywords no enunciado"""
        keywords_map = {
            "maximize": ["OPTIMIZATION", "GREEDY_ALGORITHM", "DYNAMIC_PROGRAMMING"],
            "minimize": ["OPTIMIZATION", "GREEDY_ALGORITHM"],
            "construct": ["EXPLICIT_CONSTRUCTION", "ITERATIVE_REFINEMENT"],
            "prove": ["MATHEMATICAL_INDUCTION", "PROOF_BY_CONTRADICTION"],
            "exists": ["PIGEONHOLE_PRINCIPLE", "CONSTRUCTION"],
            "for all": ["MATHEMATICAL_INDUCTION", "QUANTIFIED_LOGIC"],
            "count": ["COUNTING_ARGUMENT", "ENUMERATION"],
            "strategy": ["GAME_THEORY", "MINIMAX_STRATEGY"],
            "game": ["GAME_THEORY", "NASH_EQUILIBRIUM"],
            "equilibrium": ["NASH_EQUILIBRIUM", "SYMMETRIC_EQUILIBRIUM"],
            "symmetry": ["SYMMETRY_BREAKING", "SYMMETRIC_EQUILIBRIUM"],
            "partition": ["COALITION_FORMATION", "CASE_ANALYSIS"],
            "sequence": ["MATHEMATICAL_INDUCTION", "SEQUENTIAL_GAME"],
            "optimal": ["OPTIMIZATION", "DYNAMIC_PROGRAMMING", "PARETO_OPTIMALITY"],
        }
        
        statement_lower = problem_statement.lower()
        
        for keyword, reasoning_list in keywords_map.items():
            if keyword in statement_lower:
                if reasoning_type in reasoning_list:
                    return 0.08
        
        return 0.0
    
    def get_category_overview(self) -> Dict[str, Dict[str, Any]]:
        """Obter visão geral de todas as 12 categorias"""
        overview = {}
        
        for category in ReasoningCategory:
            types_in_category = [
                reasoning_type
                for reasoning_type, info in self.reasoning_types.items()
                if info["category"] == category
            ]
            
            avg_score = sum(
                self.reasoning_types[t]["score"]
                for t in types_in_category
            ) / len(types_in_category) if types_in_category else 0.0
            
            overview[category.value] = {
                "count": len(types_in_category),
                "average_score": avg_score,
                "reasoning_types": types_in_category,
            }
        
        return overview
    
    def generate_strategy_report(self, selection: ReasoningSelection) -> Dict[str, Any]:
        """Gerar relatório de estratégia de raciocínio"""
        
        report = {
            "problem_id": selection.problem_id,
            "total_reasoning_types": len(self.reasoning_types),
            "selected_count": len(selection.selected_reasonings),
            "confidence_score": selection.confidence_score,
            "top_5_reasonings": [
                {
                    "reasoning_type": reasoning_type,
                    "score": score,
                    "category": self.reasoning_types[reasoning_type]["category"].value,
                }
                for reasoning_type, score in selection.selected_reasonings[:5]
            ],
            "reasoning_by_category": selection.reasoning_by_category,
            "category_distribution": {
                category: len(reasonings)
                for category, reasonings in selection.reasoning_by_category.items()
            },
            "recommendation": self._generate_recommendation(selection),
        }
        
        return report
    
    def _generate_recommendation(self, selection: ReasoningSelection) -> str:
        """Gerar recomendação textual"""
        if not selection.selected_reasonings:
            return "No applicable reasoning strategies found."
        
        top_3 = selection.selected_reasonings[:3]
        reasoning_names = ", ".join(r[0].replace("_", " ").title() for r in top_3)
        
        confidence_desc = {
            "high": "with high confidence" if selection.confidence_score > 0.75 else "",
            "medium": "with moderate confidence" if 0.5 <= selection.confidence_score <= 0.75 else "",
            "low": "with low confidence" if selection.confidence_score < 0.5 else "",
        }
        
        conf_text = ""
        if selection.confidence_score > 0.75:
            conf_text = "with high confidence"
        elif selection.confidence_score > 0.5:
            conf_text = "with moderate confidence"
        else:
            conf_text = "with caution"
        
        return f"Apply {reasoning_names} {conf_text} ({selection.confidence_score:.2f})."


def create_orchestrator() -> ReasoningOrchestrator:
    """Factory para criar ReasoningOrchestrator"""
    return ReasoningOrchestrator()


if __name__ == "__main__":
    from imo_benchmark_adapter import IMOProblem
    
    problem = IMOProblem(
        problem_id="REASONING-001",
        problem_statement="""
        Prove that for any partition of a set into subsets,
        there exists an optimal strategy to maximize coverage.
        """,
        solution="Use game theory and dynamic programming.",
        grading_guidelines="Must use formal proof.",
        category="Combinatorics",
        level="IMO-hard",
        short_answer="Optimal strategy exists",
        source="IMO-ProofBench"
    )
    
    orchestrator = create_orchestrator()
    
    # Visão geral
    overview = orchestrator.get_category_overview()
    print("\n[REASONING ORCHESTRATOR v11]")
    print(f"Total Categories: {len(overview)}")
    print(f"Total Reasoning Types: {sum(cat['count'] for cat in overview.values())}")
    print(f"\nCategory Breakdown:")
    for category, info in overview.items():
        print(f"  {category}: {info['count']} types (avg score: {info['average_score']:.2f})")
    
    # Seleção para problema
    selection = orchestrator.select_for_problem(problem, top_k=5)
    report = orchestrator.generate_strategy_report(selection)
    
    print(f"\n[SELECTION FOR PROBLEM: {problem.problem_id}]")
    print(f"Confidence: {selection.confidence_score:.3f}")
    print(f"Selected: {len(selection.selected_reasonings)} out of 68 reasoning types")
    print(f"\nTop 5 Reasoning Strategies:")
    for i, (reasoning_type, score) in enumerate(selection.selected_reasonings[:5], 1):
        category = orchestrator.reasoning_types[reasoning_type]["category"].value
        print(f"  {i}. {reasoning_type} ({score:.3f}) [{category}]")
    
    print(f"\nRecommendation: {report['recommendation']}")
    print(f"\nCategory Distribution: {report['category_distribution']}")
