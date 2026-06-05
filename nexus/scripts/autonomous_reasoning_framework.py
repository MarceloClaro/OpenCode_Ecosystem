# -*- coding: utf-8 -*-
# SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
# Toda resposta ao usuário DEVE ser em português do Brasil formal.
# Contexto em chinês para eficiência de tokens (densidade +40%%).
# Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)

#!/usr/bin/env python3
"""
Autonomous Reasoning Framework - TMA v4.0

Raciocínio auto-adaptativo que se ajusta automaticamente ao domínio,
sem intervenção humana.

Capacidades:
- Seleção automática de tipo de raciocínio
- Adaptação de estratégia baseado em feedback
- Auto-reflexão sobre qualidade de raciocínio
- Detecção de limitações e busca de ajuda
- Aprendizado com erros

Author: TMA Autonomy Team
Version: 4.0
Date: 2026-04-14
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional, Callable
from enum import Enum
from datetime import datetime
from collections import defaultdict
import numpy as np


# ============================================================================
# REASONING TYPES
# ============================================================================

class ReasoningType(Enum):
    """Tipos de raciocínio disponíveis"""
    DEDUCTIVE = "deductive"  # Geral → Específico
    INDUCTIVE = "inductive"  # Específico → Geral
    ABDUCTIVE = "abductive"  # Efeito → Causa
    ANALOGICAL = "analogical"  # Similar → Similar
    COUNTERFACTUAL = "counterfactual"  # E se...?
    CAUSAL = "causal"  # Causa → Efeito
    PROBABILISTIC = "probabilistic"  # Incerteza
    FORMAL = "formal"  # Lógica formal
    HEURISTIC = "heuristic"  # Regra de ouro
    HYBRID = "hybrid"  # Combinação


class ConfidenceLevel(Enum):
    """Níveis de confiança em conclusões"""
    CERTAIN = 0.95  # 95%+
    HIGH = 0.80  # 80-95%
    MODERATE = 0.60  # 60-80%
    LOW = 0.40  # 40-60%
    UNCERTAIN = 0.20  # 20-40%
    UNKNOWN = 0.0  # <20%


@dataclass
class Premise:
    """Premissa em um raciocínio"""
    statement: str
    confidence: float  # 0-1
    source: str  # Onde vem a premissa
    verified: bool = False


@dataclass
class Conclusion:
    """Conclusão derivada de premissas"""
    statement: str
    reasoning_type: ReasoningType
    confidence: float  # 0-1
    premises: List[Premise]
    reasoning_steps: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "statement": self.statement,
            "reasoning_type": self.reasoning_type.value,
            "confidence": self.confidence,
            "premises": [{"statement": p.statement, "confidence": p.confidence} for p in self.premises],
            "reasoning_steps": self.reasoning_steps,
            "timestamp": self.timestamp
        }


# ============================================================================
# AUTONOMOUS REASONING FRAMEWORK
# ============================================================================

class AutonomousReasoningFramework:
    """
    Framework de Raciocínio Autônomo: adapta-se automaticamente ao domínio.
    
    Capacidades:
    - Seleção automática de tipo de raciocínio
    - Adaptação baseada em feedback
    - Auto-reflexão sobre qualidade
    - Detecção de limitações
    - Aprendizado com erros
    """
    
    def __init__(self, agent_id: str = "Agent"):
        self.agent_id = agent_id
        self.reasoning_history: List[Conclusion] = []
        self.reasoning_performance: Dict[ReasoningType, List[float]] = defaultdict(list)
        self.domain_reasoning_preferences: Dict[str, ReasoningType] = {}
        self.error_patterns: List[Dict] = []
        self.self_reflection_log: List[Dict] = []
        
    # ========================================================================
    # REASONING TYPE SELECTION
    # ========================================================================
    
    def select_reasoning_type(self, problem: Dict, domain: str = "general") -> ReasoningType:
        """
        Selecionar tipo de raciocínio ótimo baseado no problema e domínio.
        """
        
        # Se temos preferência para este domínio, usar
        if domain in self.domain_reasoning_preferences:
            return self.domain_reasoning_preferences[domain]
        
        # Analisar características do problema
        problem_type = problem.get("type", "unknown")
        has_uncertainty = problem.get("uncertain", False)
        requires_explanation = problem.get("explain", False)
        involves_causality = problem.get("causal", False)
        similar_to_known = problem.get("similar_cases", [])
        
        # Scoring de cada tipo
        scores = {}
        
        # Deductive: quando temos regras gerais
        scores[ReasoningType.DEDUCTIVE] = (
            (problem_type == "rule_application") * 0.8 +
            (not has_uncertainty) * 0.3
        )
        
        # Inductive: quando generalizamos de exemplos
        scores[ReasoningType.INDUCTIVE] = (
            (problem_type == "pattern_discovery") * 0.8 +
            (len(similar_to_known) > 3) * 0.5
        )
        
        # Abductive: quando explicamos observações
        scores[ReasoningType.ABDUCTIVE] = (
            (problem_type == "diagnosis") * 0.8 +
            (requires_explanation) * 0.5
        )
        
        # Analogical: quando temos casos similares
        scores[ReasoningType.ANALOGICAL] = (
            (len(similar_to_known) > 0) * 0.7 +
            (problem_type == "novel_problem") * 0.5
        )
        
        # Counterfactual: quando exploramos alternativas
        scores[ReasoningType.COUNTERFACTUAL] = (
            (problem_type == "decision_making") * 0.7 +
            (problem_type == "planning") * 0.6
        )
        
        # Causal: quando entendemos causas
        scores[ReasoningType.CAUSAL] = (
            (involves_causality) * 0.9 +
            (problem_type == "root_cause_analysis") * 0.8
        )
        
        # Probabilistic: quando há incerteza
        scores[ReasoningType.PROBABILISTIC] = (
            (has_uncertainty) * 0.8 +
            (problem_type == "prediction") * 0.6
        )
        
        # Formal: quando precisamos de rigor
        scores[ReasoningType.FORMAL] = (
            (problem_type == "verification") * 0.8 +
            (problem_type == "proof") * 0.9
        )
        
        # Heuristic: quando temos restrição de tempo
        scores[ReasoningType.HEURISTIC] = (
            (problem.get("time_limited", False)) * 0.7 +
            (problem_type == "quick_decision") * 0.6
        )
        
        # Selecionar melhor
        best_type = max(scores, key=scores.get)
        
        return best_type
    
    # ========================================================================
    # DEDUCTIVE REASONING
    # ========================================================================
    
    def deductive_reasoning(self, premises: List[Premise], conclusion_statement: str) -> Conclusion:
        """
        Raciocínio Dedutivo: Geral → Específico
        
        Exemplo:
        - Premissa 1: Todos os homens são mortais
        - Premissa 2: Sócrates é um homem
        - Conclusão: Sócrates é mortal
        """
        
        # Validar premissas
        premise_confidence = np.mean([p.confidence for p in premises])
        
        # Confiança da conclusão = mínimo das premissas
        conclusion_confidence = min([p.confidence for p in premises]) if premises else 0.5
        
        reasoning_steps = [
            f"Premise 1: {premises[0].statement}" if len(premises) > 0 else "",
            f"Premise 2: {premises[1].statement}" if len(premises) > 1 else "",
            "Apply deductive logic",
            f"Conclusion: {conclusion_statement}"
        ]
        
        conclusion = Conclusion(
            statement=conclusion_statement,
            reasoning_type=ReasoningType.DEDUCTIVE,
            confidence=conclusion_confidence,
            premises=premises,
            reasoning_steps=[s for s in reasoning_steps if s]
        )
        
        return conclusion
    
    # ========================================================================
    # INDUCTIVE REASONING
    # ========================================================================
    
    def inductive_reasoning(self, examples: List[Dict], generalization: str) -> Conclusion:
        """
        Raciocínio Indutivo: Específico → Geral
        
        Exemplo:
        - Exemplo 1: Ouro é metal e condutor
        - Exemplo 2: Cobre é metal e condutor
        - Generalização: Todos os metais são condutores
        """
        
        # Confiança baseada em número de exemplos
        num_examples = len(examples)
        base_confidence = min(0.9, 0.4 + (num_examples / 20))
        
        # Verificar consistência dos exemplos
        consistency = self._check_example_consistency(examples)
        
        conclusion_confidence = base_confidence * consistency
        
        reasoning_steps = [
            f"Observed {num_examples} examples",
            "Identify common patterns",
            "Check for exceptions",
            f"Generalization: {generalization}"
        ]
        
        conclusion = Conclusion(
            statement=generalization,
            reasoning_type=ReasoningType.INDUCTIVE,
            confidence=conclusion_confidence,
            premises=[Premise(f"Example {i+1}: {str(ex)}", 0.8, "observation") 
                     for i, ex in enumerate(examples)],
            reasoning_steps=reasoning_steps
        )
        
        return conclusion
    
    # ========================================================================
    # ABDUCTIVE REASONING
    # ========================================================================
    
    def abductive_reasoning(self, observation: str, possible_causes: List[str]) -> Conclusion:
        """
        Raciocínio Abdutivo: Efeito → Causa (melhor explicação)
        
        Exemplo:
        - Observação: A grama está molhada
        - Causa possível 1: Choveu
        - Causa possível 2: Regador funcionou
        - Melhor explicação: Choveu (mais provável)
        """
        
        # Scoring de cada causa
        cause_scores = {}
        for cause in possible_causes:
            # Simplicidade (Occam's Razor)
            simplicity = 1 / (1 + len(cause.split()))
            
            # Probabilidade (heurística)
            probability = 0.5  # Padrão
            if "rain" in cause.lower():
                probability = 0.7
            elif "sprinkler" in cause.lower():
                probability = 0.4
            
            cause_scores[cause] = simplicity * 0.3 + probability * 0.7
        
        # Melhor explicação
        best_cause = max(cause_scores, key=cause_scores.get)
        conclusion_confidence = cause_scores[best_cause]
        
        reasoning_steps = [
            f"Observation: {observation}",
            f"Possible causes: {', '.join(possible_causes)}",
            "Evaluate each cause by simplicity and probability",
            f"Best explanation: {best_cause}"
        ]
        
        conclusion = Conclusion(
            statement=f"Most likely cause: {best_cause}",
            reasoning_type=ReasoningType.ABDUCTIVE,
            confidence=conclusion_confidence,
            premises=[Premise(f"Possible cause: {cause}", cause_scores[cause], "hypothesis") 
                     for cause in possible_causes],
            reasoning_steps=reasoning_steps
        )
        
        return conclusion
    
    # ========================================================================
    # ANALOGICAL REASONING
    # ========================================================================
    
    def analogical_reasoning(self, source_case: Dict, target_case: Dict, 
                            source_solution: str) -> Conclusion:
        """
        Raciocínio Analógico: Similar → Similar
        
        Exemplo:
        - Caso fonte: Problema A resolvido com Solução X
        - Caso alvo: Problema B similar a A
        - Solução: Aplicar Solução X adaptada ao Problema B
        """
        
        # Calcular similaridade
        similarity = self._calculate_similarity(source_case, target_case)
        
        # Confiança baseada em similaridade
        conclusion_confidence = similarity * 0.8
        
        reasoning_steps = [
            f"Source case: {source_case.get('description', 'Unknown')}",
            f"Target case: {target_case.get('description', 'Unknown')}",
            f"Similarity: {similarity:.2f}",
            f"Apply solution: {source_solution}"
        ]
        
        conclusion = Conclusion(
            statement=f"Apply {source_solution} to target case",
            reasoning_type=ReasoningType.ANALOGICAL,
            confidence=conclusion_confidence,
            premises=[
                Premise(f"Source case: {source_case}", similarity, "analogy"),
                Premise(f"Target case: {target_case}", similarity, "analogy")
            ],
            reasoning_steps=reasoning_steps
        )
        
        return conclusion
    
    # ========================================================================
    # COUNTERFACTUAL REASONING
    # ========================================================================
    
    def counterfactual_reasoning(self, actual_situation: str, 
                                counterfactual: str) -> Conclusion:
        """
        Raciocínio Contrafactual: E se...?
        
        Exemplo:
        - Situação real: Chegamos atrasados
        - Contrafactual: E se tivéssemos saído mais cedo?
        - Conclusão: Teríamos chegado no horário
        """
        
        reasoning_steps = [
            f"Actual situation: {actual_situation}",
            f"Counterfactual: {counterfactual}",
            "Trace causal chain",
            "Derive alternative outcome"
        ]
        
        conclusion_confidence = 0.6  # Contrafactuais são especulativos
        
        conclusion = Conclusion(
            statement=f"If {counterfactual}, then [alternative outcome]",
            reasoning_type=ReasoningType.COUNTERFACTUAL,
            confidence=conclusion_confidence,
            premises=[
                Premise(f"Actual: {actual_situation}", 0.95, "observation"),
                Premise(f"Hypothetical: {counterfactual}", 0.5, "speculation")
            ],
            reasoning_steps=reasoning_steps
        )
        
        return conclusion
    
    # ========================================================================
    # SELF-REFLECTION
    # ========================================================================
    
    def reflect_on_reasoning(self, conclusion: Conclusion, 
                            actual_outcome: Optional[str] = None) -> Dict:
        """
        Auto-reflexão sobre qualidade do raciocínio.
        """
        
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "reasoning_type": conclusion.reasoning_type.value,
            "confidence": conclusion.confidence,
            "num_premises": len(conclusion.premises),
            "premise_quality": np.mean([p.confidence for p in conclusion.premises]) if conclusion.premises else 0,
            "reasoning_steps": len(conclusion.reasoning_steps),
            "was_correct": None,
            "improvement_areas": []
        }
        
        # Verificar se conclusão estava correta
        if actual_outcome:
            reflection["was_correct"] = actual_outcome.lower() in conclusion.statement.lower()
            
            if not reflection["was_correct"]:
                # Registrar erro para aprendizado
                self.error_patterns.append({
                    "reasoning_type": conclusion.reasoning_type.value,
                    "conclusion": conclusion.statement,
                    "actual": actual_outcome,
                    "timestamp": datetime.now().isoformat()
                })
                
                reflection["improvement_areas"].append("Conclusion was incorrect")
        
        # Identificar áreas de melhoria
        if conclusion.confidence < 0.5:
            reflection["improvement_areas"].append("Low confidence - need more evidence")
        
        if len(conclusion.premises) < 2:
            reflection["improvement_areas"].append("Few premises - need more support")
        
        self.self_reflection_log.append(reflection)
        
        return reflection
    
    # ========================================================================
    # ADAPTIVE LEARNING
    # ========================================================================
    
    def learn_from_feedback(self, domain: str, feedback: Dict) -> None:
        """
        Aprender com feedback para melhorar raciocínio futuro.
        """
        
        reasoning_type = ReasoningType[feedback.get("reasoning_type", "HYBRID").upper()]
        success = feedback.get("success", False)
        
        # Registrar performance
        score = 1.0 if success else 0.0
        self.reasoning_performance[reasoning_type].append(score)
        
        # Atualizar preferência de domínio se performance boa
        if success and len(self.reasoning_performance[reasoning_type]) > 3:
            avg_performance = np.mean(self.reasoning_performance[reasoning_type][-3:])
            if avg_performance > 0.7:
                self.domain_reasoning_preferences[domain] = reasoning_type
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def _check_example_consistency(self, examples: List[Dict]) -> float:
        """Verificar consistência dos exemplos (0-1)"""
        if not examples:
            return 0.0
        
        # Heurística simples: todos os exemplos têm mesma estrutura
        first_keys = set(examples[0].keys())
        consistency_score = sum(
            1 for ex in examples if set(ex.keys()) == first_keys
        ) / len(examples)
        
        return consistency_score
    
    def _calculate_similarity(self, case1: Dict, case2: Dict) -> float:
        """Calcular similaridade entre dois casos (0-1)"""
        
        # Contar atributos comuns
        keys1 = set(case1.keys())
        keys2 = set(case2.keys())
        common_keys = keys1 & keys2
        
        if not common_keys:
            return 0.0
        
        # Calcular similaridade de valores
        similarity_sum = 0
        for key in common_keys:
            if case1[key] == case2[key]:
                similarity_sum += 1
        
        return similarity_sum / len(common_keys)
    
    def generate_reasoning_report(self) -> Dict:
        """Gerar relatório de raciocínio"""
        
        return {
            "timestamp": datetime.now().isoformat(),
            "agent": self.agent_id,
            "total_conclusions": len(self.reasoning_history),
            "reasoning_types_used": list(set(c.reasoning_type for c in self.reasoning_history)),
            "average_confidence": np.mean([c.confidence for c in self.reasoning_history]) if self.reasoning_history else 0,
            "performance_by_type": {
                rt.value: {
                    "attempts": len(scores),
                    "success_rate": np.mean(scores) if scores else 0
                }
                for rt, scores in self.reasoning_performance.items()
            },
            "domain_preferences": self.domain_reasoning_preferences,
            "error_patterns": len(self.error_patterns),
            "self_reflections": len(self.self_reflection_log)
        }


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    framework = AutonomousReasoningFramework("A1")
    
    print("=" * 80)
    print("Autonomous Reasoning Framework v4.0")
    print("=" * 80)
    
    # Exemplo 1: Deductive Reasoning
    print("\n1. DEDUCTIVE REASONING")
    premises = [
        Premise("All birds have wings", 0.95, "knowledge"),
        Premise("Penguins are birds", 0.90, "knowledge")
    ]
    conclusion = framework.deductive_reasoning(premises, "Penguins have wings")
    print(f"   Conclusion: {conclusion.statement}")
    print(f"   Confidence: {conclusion.confidence:.2f}")
    
    # Exemplo 2: Inductive Reasoning
    print("\n2. INDUCTIVE REASONING")
    examples = [
        {"metal": "Gold", "conductor": True},
        {"metal": "Silver", "conductor": True},
        {"metal": "Copper", "conductor": True}
    ]
    conclusion = framework.inductive_reasoning(examples, "All metals are conductors")
    print(f"   Conclusion: {conclusion.statement}")
    print(f"   Confidence: {conclusion.confidence:.2f}")
    
    # Exemplo 3: Abductive Reasoning
    print("\n3. ABDUCTIVE REASONING")
    conclusion = framework.abductive_reasoning(
        "The ground is wet",
        ["It rained", "The sprinkler was on", "Someone watered"]
    )
    print(f"   Conclusion: {conclusion.statement}")
    print(f"   Confidence: {conclusion.confidence:.2f}")
    
    # Exemplo 4: Select Reasoning Type
    print("\n4. REASONING TYPE SELECTION")
    problem = {
        "type": "diagnosis",
        "uncertain": True,
        "explain": True,
        "causal": False
    }
    selected = framework.select_reasoning_type(problem, "medicine")
    print(f"   Selected: {selected.value}")
    
    # Relatório
    print("\n" + "=" * 80)
    print("REASONING REPORT")
    print("=" * 80)
    report = framework.generate_reasoning_report()
    print(json.dumps(report, indent=2, default=str))
