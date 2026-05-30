# -*- coding: utf-8 -*-
# SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
# Toda resposta ao usuário DEVE ser em português do Brasil formal.
# Contexto em chinês para eficiência de tokens (densidade +40%%).
# Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)

"""
TMA v5.0 MICRO - Micro Reasoning Types
38 sub-tipos de raciocínio granular com seleção automática
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Callable, Optional, Tuple
from enum import Enum
import json


class ReasoningCategory(Enum):
    """Categorias de raciocínio"""
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    CAUSAL = "causal"
    COUNTERFACTUAL = "counterfactual"
    BAYESIAN = "bayesian"
    ANALOGICAL = "analogical"
    FORMAL = "formal"
    ABDUCTIVE = "abductive"


@dataclass
class ReasoningType:
    """Definição de um tipo de raciocínio"""
    name: str
    category: ReasoningCategory
    description: str
    formula: str
    requirements: List[str]
    strengths: List[str]
    weaknesses: List[str]
    best_for: List[str]
    complexity: float  # 0-1
    confidence: float  # 0-1
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            "name": self.name,
            "category": self.category.value,
            "description": self.description,
            "formula": self.formula,
            "requirements": self.requirements,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "best_for": self.best_for,
            "complexity": self.complexity,
            "confidence": self.confidence
        }


class MicroReasoningEngine:
    """Motor de raciocínio com 38 sub-tipos"""
    
    def __init__(self):
        self.reasoning_types: Dict[str, ReasoningType] = {}
        self._init_all_reasoning_types()
        self.selection_history: List[Dict] = []
    
    def _init_all_reasoning_types(self):
        """Inicializa todos os 38 sub-tipos"""
        # Deductive (8 tipos)
        self._init_deductive_types()
        # Inductive (6 tipos)
        self._init_inductive_types()
        # Causal (5 tipos)
        self._init_causal_types()
        # Counterfactual (4 tipos)
        self._init_counterfactual_types()
        # Bayesian (5 tipos)
        self._init_bayesian_types()
        # Analogical (4 tipos)
        self._init_analogical_types()
        # Formal (3 tipos)
        self._init_formal_types()
        # Abductive (3 tipos)
        self._init_abductive_types()
    
    def _init_deductive_types(self):
        """8 tipos de raciocínio dedutivo"""
        
        self.reasoning_types["modus_ponens"] = ReasoningType(
            name="Modus Ponens",
            category=ReasoningCategory.DEDUCTIVE,
            description="Se A implica B, e A é verdadeiro, então B é verdadeiro",
            formula="A→B, A ⊢ B",
            requirements=["implication", "premise"],
            strengths=["válido logicamente", "simples", "rápido"],
            weaknesses=["requer implicação clara", "não gera novos conhecimentos"],
            best_for=["validação", "verificação", "aplicação de regras"],
            complexity=0.3,
            confidence=0.95
        )
        
        self.reasoning_types["modus_tollens"] = ReasoningType(
            name="Modus Tollens",
            category=ReasoningCategory.DEDUCTIVE,
            description="Se A implica B, e B é falso, então A é falso",
            formula="A→B, ¬B ⊢ ¬A",
            requirements=["implication", "negated_conclusion"],
            strengths=["válido logicamente", "útil para refutação"],
            weaknesses=["requer implicação clara"],
            best_for=["refutação", "eliminação", "diagnóstico negativo"],
            complexity=0.3,
            confidence=0.95
        )
        
        self.reasoning_types["hypothetical_syllogism"] = ReasoningType(
            name="Hypothetical Syllogism",
            category=ReasoningCategory.DEDUCTIVE,
            description="Se A implica B, e B implica C, então A implica C",
            formula="A→B, B→C ⊢ A→C",
            requirements=["chain_of_implications"],
            strengths=["válido logicamente", "cria cadeias de raciocínio"],
            weaknesses=["requer múltiplas implicações"],
            best_for=["rastreamento de consequências", "planejamento"],
            complexity=0.4,
            confidence=0.95
        )
        
        self.reasoning_types["disjunctive_syllogism"] = ReasoningType(
            name="Disjunctive Syllogism",
            category=ReasoningCategory.DEDUCTIVE,
            description="Se A ou B, e não A, então B",
            formula="A∨B, ¬A ⊢ B",
            requirements=["disjunction", "negated_alternative"],
            strengths=["válido logicamente", "útil para eliminação"],
            weaknesses=["requer disjunção clara"],
            best_for=["eliminação de alternativas", "classificação"],
            complexity=0.3,
            confidence=0.95
        )
        
        self.reasoning_types["conjunction"] = ReasoningType(
            name="Conjunction",
            category=ReasoningCategory.DEDUCTIVE,
            description="Se A é verdadeiro e B é verdadeiro, então A e B é verdadeiro",
            formula="A, B ⊢ A∧B",
            requirements=["multiple_premises"],
            strengths=["simples", "combina informações"],
            weaknesses=["não gera novos conhecimentos"],
            best_for=["combinação de fatos", "síntese"],
            complexity=0.2,
            confidence=0.99
        )
        
        self.reasoning_types["negation"] = ReasoningType(
            name="Negation (Contradiction)",
            category=ReasoningCategory.DEDUCTIVE,
            description="Se A e não A, então contradição",
            formula="A, ¬A ⊢ ⊥",
            requirements=["contradiction"],
            strengths=["detecta inconsistências"],
            weaknesses=["não resolve contradições"],
            best_for=["detecção de erro", "validação"],
            complexity=0.2,
            confidence=0.99
        )
        
        self.reasoning_types["universal_instantiation"] = ReasoningType(
            name="Universal Instantiation",
            category=ReasoningCategory.DEDUCTIVE,
            description="Se para todo x P(x), então P(a)",
            formula="∀x P(x) ⊢ P(a)",
            requirements=["universal_quantification"],
            strengths=["válido logicamente", "aplica regras gerais"],
            weaknesses=["requer quantificação universal"],
            best_for=["aplicação de regras", "especialização"],
            complexity=0.4,
            confidence=0.95
        )
        
        self.reasoning_types["identity"] = ReasoningType(
            name="Identity",
            category=ReasoningCategory.DEDUCTIVE,
            description="Se a = b e P(a), então P(b)",
            formula="a=b, P(a) ⊢ P(b)",
            requirements=["equality", "property"],
            strengths=["válido logicamente", "substitui equivalentes"],
            weaknesses=["requer igualdade estabelecida"],
            best_for=["substituição", "simplificação"],
            complexity=0.3,
            confidence=0.95
        )
    
    def _init_inductive_types(self):
        """6 tipos de raciocínio indutivo"""
        
        self.reasoning_types["enumeration"] = ReasoningType(
            name="Enumeration",
            category=ReasoningCategory.INDUCTIVE,
            description="Se todos os casos observados têm propriedade P, então provavelmente todos têm",
            formula="P(a₁), P(a₂), ..., P(aₙ) ⊢ ∀x P(x)",
            requirements=["multiple_observations", "pattern"],
            strengths=["gera hipóteses", "baseado em dados"],
            weaknesses=["não é válido logicamente", "viés de amostragem"],
            best_for=["descoberta de padrões", "geração de hipóteses"],
            complexity=0.5,
            confidence=0.6
        )
        
        self.reasoning_types["analogy"] = ReasoningType(
            name="Analogy",
            category=ReasoningCategory.INDUCTIVE,
            description="A é similar a B, B tem propriedade P, então provavelmente A tem P",
            formula="A ≈ B, P(B) ⊢ P(A)",
            requirements=["similarity", "shared_properties"],
            strengths=["criativo", "gera novas ideias"],
            weaknesses=["não é válido logicamente", "pode ser enganoso"],
            best_for=["transferência de conhecimento", "inovação"],
            complexity=0.6,
            confidence=0.5
        )
        
        self.reasoning_types["generalization"] = ReasoningType(
            name="Generalization",
            category=ReasoningCategory.INDUCTIVE,
            description="Padrão observado em amostra → padrão geral",
            formula="Pattern(sample) ⊢ Pattern(population)",
            requirements=["sample_data", "statistical_validity"],
            strengths=["gera conhecimento geral", "baseado em dados"],
            weaknesses=["viés de amostragem", "requer dados suficientes"],
            best_for=["extração de regras", "modelagem"],
            complexity=0.6,
            confidence=0.65
        )
        
        self.reasoning_types["abduction_inductive"] = ReasoningType(
            name="Abduction (Inductive)",
            category=ReasoningCategory.INDUCTIVE,
            description="Observação O, Teoria T explica O → T é provável",
            formula="O, T explains O ⊢ T",
            requirements=["observation", "explanatory_theory"],
            strengths=["gera hipóteses", "baseado em observação"],
            weaknesses=["não é válido logicamente"],
            best_for=["diagnóstico", "descoberta"],
            complexity=0.7,
            confidence=0.55
        )
        
        self.reasoning_types["causal_inductive"] = ReasoningType(
            name="Causal (Inductive)",
            category=ReasoningCategory.INDUCTIVE,
            description="X sempre precede Y → X causa Y",
            formula="X precedes Y consistently ⊢ X causes Y",
            requirements=["temporal_sequence", "correlation"],
            strengths=["descobre relações causais"],
            weaknesses=["correlação ≠ causalidade"],
            best_for=["descoberta de causas", "análise de impacto"],
            complexity=0.7,
            confidence=0.5
        )
        
        self.reasoning_types["probabilistic"] = ReasoningType(
            name="Probabilistic",
            category=ReasoningCategory.INDUCTIVE,
            description="P(A|B) = P(B|A)P(A)/P(B)",
            formula="P(A|B) = P(B|A)P(A)/P(B)",
            requirements=["probability_data", "conditional_probabilities"],
            strengths=["quantifica incerteza", "baseado em dados"],
            weaknesses=["requer dados de probabilidade"],
            best_for=["previsão", "análise de risco"],
            complexity=0.7,
            confidence=0.75
        )
    
    def _init_causal_types(self):
        """5 tipos de raciocínio causal"""
        
        self.reasoning_types["direct_causal"] = ReasoningType(
            name="Direct Causal",
            category=ReasoningCategory.CAUSAL,
            description="X causa Y diretamente",
            formula="X → Y",
            requirements=["direct_relationship", "mechanism"],
            strengths=["simples", "direto"],
            weaknesses=["pode ignorar mediadores"],
            best_for=["relações simples", "ação-reação"],
            complexity=0.4,
            confidence=0.7
        )
        
        self.reasoning_types["indirect_causal"] = ReasoningType(
            name="Indirect Causal",
            category=ReasoningCategory.CAUSAL,
            description="X causa Y indiretamente através de Z",
            formula="X → Z → Y",
            requirements=["mediator", "chain"],
            strengths=["explica cadeias causais"],
            weaknesses=["mais complexo"],
            best_for=["sistemas complexos", "rastreamento"],
            complexity=0.6,
            confidence=0.6
        )
        
        self.reasoning_types["common_cause"] = ReasoningType(
            name="Common Cause",
            category=ReasoningCategory.CAUSAL,
            description="Z causa tanto X quanto Y",
            formula="Z → X, Z → Y",
            requirements=["common_source", "multiple_effects"],
            strengths=["explica correlações"],
            weaknesses=["requer identificação de causa comum"],
            best_for=["análise de correlação", "confundidores"],
            complexity=0.6,
            confidence=0.6
        )
        
        self.reasoning_types["confounder"] = ReasoningType(
            name="Confounder",
            category=ReasoningCategory.CAUSAL,
            description="Z confunde relação entre X e Y",
            formula="Z ← X → Y",
            requirements=["confounding_variable"],
            strengths=["detecta confundidores"],
            weaknesses=["complexo de identificar"],
            best_for=["análise causal", "ajuste de confundidores"],
            complexity=0.7,
            confidence=0.55
        )
        
        self.reasoning_types["mediator"] = ReasoningType(
            name="Mediator",
            category=ReasoningCategory.CAUSAL,
            description="X causa Y através de mediador Z",
            formula="X → Z → Y",
            requirements=["mediating_variable"],
            strengths=["explica mecanismos"],
            weaknesses=["requer identificação de mediador"],
            best_for=["análise de mecanismo", "decomposição"],
            complexity=0.7,
            confidence=0.6
        )
    
    def _init_counterfactual_types(self):
        """4 tipos de raciocínio contrafactual"""
        
        self.reasoning_types["simple_counterfactual"] = ReasoningType(
            name="Simple Counterfactual",
            category=ReasoningCategory.COUNTERFACTUAL,
            description="Se tivesse feito X, Y teria acontecido",
            formula="¬A → ¬B (dado A → B)",
            requirements=["conditional", "alternative"],
            strengths=["explora alternativas"],
            weaknesses=["especulativo"],
            best_for=["planejamento", "aprendizado"],
            complexity=0.6,
            confidence=0.5
        )
        
        self.reasoning_types["conditional_counterfactual"] = ReasoningType(
            name="Conditional Counterfactual",
            category=ReasoningCategory.COUNTERFACTUAL,
            description="Se tivesse feito X em vez de Y, Z teria acontecido",
            formula="¬A ∧ B → ¬C (dado A ∧ ¬B → C)",
            requirements=["multiple_alternatives"],
            strengths=["compara alternativas"],
            weaknesses=["muito especulativo"],
            best_for=["análise de decisão", "otimização"],
            complexity=0.7,
            confidence=0.45
        )
        
        self.reasoning_types["multiple_counterfactual"] = ReasoningType(
            name="Multiple Counterfactual",
            category=ReasoningCategory.COUNTERFACTUAL,
            description="Se tivesse feito X e W, Z teria acontecido",
            formula="¬A ∧ ¬B → ¬C",
            requirements=["multiple_changes"],
            strengths=["explora combinações"],
            weaknesses=["exponencialmente complexo"],
            best_for=["análise de cenários", "planejamento estratégico"],
            complexity=0.8,
            confidence=0.4
        )
        
        self.reasoning_types["iterative_counterfactual"] = ReasoningType(
            name="Iterative Counterfactual",
            category=ReasoningCategory.COUNTERFACTUAL,
            description="Se tivesse feito X, então Y, então Z teria acontecido",
            formula="¬A → ¬B → ¬C",
            requirements=["sequence_of_changes"],
            strengths=["explora cadeias de eventos"],
            weaknesses=["muito especulativo"],
            best_for=["análise de impacto", "previsão"],
            complexity=0.8,
            confidence=0.35
        )
    
    def _init_bayesian_types(self):
        """5 tipos de raciocínio Bayesiano"""
        
        self.reasoning_types["prior"] = ReasoningType(
            name="Prior",
            category=ReasoningCategory.BAYESIAN,
            description="P(H) - probabilidade da hipótese antes de evidência",
            formula="P(H)",
            requirements=["background_knowledge"],
            strengths=["incorpora conhecimento prévio"],
            weaknesses=["subjetivo"],
            best_for=["inicialização", "contexto"],
            complexity=0.4,
            confidence=0.7
        )
        
        self.reasoning_types["likelihood"] = ReasoningType(
            name="Likelihood",
            category=ReasoningCategory.BAYESIAN,
            description="P(E|H) - probabilidade de evidência dado hipótese",
            formula="P(E|H)",
            requirements=["evidence", "hypothesis"],
            strengths=["quantifica relação evidência-hipótese"],
            weaknesses=["requer dados"],
            best_for=["avaliação de evidência"],
            complexity=0.5,
            confidence=0.75
        )
        
        self.reasoning_types["posterior"] = ReasoningType(
            name="Posterior",
            category=ReasoningCategory.BAYESIAN,
            description="P(H|E) - probabilidade de hipótese dado evidência",
            formula="P(H|E) = P(E|H)P(H)/P(E)",
            requirements=["prior", "likelihood", "evidence"],
            strengths=["atualiza crença com evidência"],
            weaknesses=["requer cálculo"],
            best_for=["atualização de crença", "inferência"],
            complexity=0.6,
            confidence=0.8
        )
        
        self.reasoning_types["bayesian_update"] = ReasoningType(
            name="Bayesian Update",
            category=ReasoningCategory.BAYESIAN,
            description="Atualiza posterior com nova evidência iterativamente",
            formula="P(H|E₁,E₂,...) = P(Eₙ|H)P(H|E₁,...,Eₙ₋₁)/P(Eₙ)",
            requirements=["sequential_evidence"],
            strengths=["incorpora múltiplas evidências"],
            weaknesses=["requer cálculo iterativo"],
            best_for=["aprendizado contínuo", "filtragem"],
            complexity=0.7,
            confidence=0.8
        )
        
        self.reasoning_types["bayesian_inference"] = ReasoningType(
            name="Bayesian Inference",
            category=ReasoningCategory.BAYESIAN,
            description="Infere melhor hipótese pela máxima posteriori",
            formula="H* = argmax P(H|E)",
            requirements=["multiple_hypotheses", "evidence"],
            strengths=["seleciona melhor hipótese"],
            weaknesses=["requer comparação de todas"],
            best_for=["seleção de modelo", "diagnóstico"],
            complexity=0.7,
            confidence=0.8
        )
    
    def _init_analogical_types(self):
        """4 tipos de raciocínio analógico"""
        
        self.reasoning_types["structural_analogy"] = ReasoningType(
            name="Structural Analogy",
            category=ReasoningCategory.ANALOGICAL,
            description="Estrutura A ≈ Estrutura B",
            formula="Structure(A) ≈ Structure(B)",
            requirements=["structural_similarity"],
            strengths=["descobre padrões estruturais"],
            weaknesses=["superficial"],
            best_for=["reconhecimento de padrão", "classificação"],
            complexity=0.5,
            confidence=0.6
        )
        
        self.reasoning_types["functional_analogy"] = ReasoningType(
            name="Functional Analogy",
            category=ReasoningCategory.ANALOGICAL,
            description="Função A ≈ Função B",
            formula="Function(A) ≈ Function(B)",
            requirements=["functional_similarity"],
            strengths=["descobre funções equivalentes"],
            weaknesses=["requer compreensão funcional"],
            best_for=["design", "otimização"],
            complexity=0.6,
            confidence=0.65
        )
        
        self.reasoning_types["procedural_analogy"] = ReasoningType(
            name="Procedural Analogy",
            category=ReasoningCategory.ANALOGICAL,
            description="Processo A ≈ Processo B",
            formula="Process(A) ≈ Process(B)",
            requirements=["process_similarity"],
            strengths=["transfere procedimentos"],
            weaknesses=["contexto-dependente"],
            best_for=["transferência de conhecimento", "automação"],
            complexity=0.6,
            confidence=0.6
        )
        
        self.reasoning_types["relational_analogy"] = ReasoningType(
            name="Relational Analogy",
            category=ReasoningCategory.ANALOGICAL,
            description="Relação A ≈ Relação B",
            formula="Relation(A) ≈ Relation(B)",
            requirements=["relational_similarity"],
            strengths=["descobre relações abstratas"],
            weaknesses=["abstrato"],
            best_for=["raciocínio abstrato", "matemática"],
            complexity=0.7,
            confidence=0.55
        )
    
    def _init_formal_types(self):
        """3 tipos de raciocínio formal"""
        
        self.reasoning_types["direct_proof"] = ReasoningType(
            name="Direct Proof",
            category=ReasoningCategory.FORMAL,
            description="Assume A, deriva B, logo A→B",
            formula="A ⊢ B ⟹ ⊢ A→B",
            requirements=["logical_derivation"],
            strengths=["válido logicamente", "direto"],
            weaknesses=["requer derivação completa"],
            best_for=["prova matemática", "verificação"],
            complexity=0.7,
            confidence=0.95
        )
        
        self.reasoning_types["proof_by_contradiction"] = ReasoningType(
            name="Proof by Contradiction",
            category=ReasoningCategory.FORMAL,
            description="Assume ¬A, deriva ⊥, logo A",
            formula="¬A ⊢ ⊥ ⟹ ⊢ A",
            requirements=["contradiction_derivation"],
            strengths=["poderoso", "válido logicamente"],
            weaknesses=["pode ser indireto"],
            best_for=["prova de impossibilidade", "refutação"],
            complexity=0.8,
            confidence=0.95
        )
        
        self.reasoning_types["proof_by_induction"] = ReasoningType(
            name="Proof by Induction",
            category=ReasoningCategory.FORMAL,
            description="Base: P(1), Passo: P(n)→P(n+1), logo ∀n P(n)",
            formula="P(1) ∧ (∀n P(n)→P(n+1)) ⟹ ∀n P(n)",
            requirements=["base_case", "inductive_step"],
            strengths=["válido para infinitos casos"],
            weaknesses=["requer base e passo"],
            best_for=["prova sobre sequências", "recursão"],
            complexity=0.8,
            confidence=0.95
        )
    
    def _init_abductive_types(self):
        """3 tipos de raciocínio abdutivo"""
        
        self.reasoning_types["best_explanation"] = ReasoningType(
            name="Best Explanation",
            category=ReasoningCategory.ABDUCTIVE,
            description="Qual teoria melhor explica observação?",
            formula="O, T₁ explains O, T₂ explains O ⊢ best(T₁, T₂)",
            requirements=["observation", "multiple_explanations"],
            strengths=["seleciona melhor explicação"],
            weaknesses=["requer critério de qualidade"],
            best_for=["diagnóstico", "descoberta"],
            complexity=0.7,
            confidence=0.6
        )
        
        self.reasoning_types["diagnostic"] = ReasoningType(
            name="Diagnostic",
            category=ReasoningCategory.ABDUCTIVE,
            description="Qual causa explica sintomas?",
            formula="Symptoms, Cause explains Symptoms ⊢ Cause",
            requirements=["symptoms", "causal_model"],
            strengths=["prático", "aplicável"],
            weaknesses=["requer modelo causal"],
            best_for=["diagnóstico médico", "troubleshooting"],
            complexity=0.7,
            confidence=0.65
        )
        
        self.reasoning_types["reconstruction"] = ReasoningType(
            name="Reconstruction",
            category=ReasoningCategory.ABDUCTIVE,
            description="Qual história explica evidência?",
            formula="Evidence, Story explains Evidence ⊢ Story",
            requirements=["evidence", "narrative"],
            strengths=["cria narrativas coerentes"],
            weaknesses=["múltiplas histórias possíveis"],
            best_for=["investigação", "análise histórica"],
            complexity=0.8,
            confidence=0.55
        )
    
    def select_reasoning_type(
        self,
        domain_characteristics: Dict[str, Any],
        problem_type: str,
        constraints: Dict[str, Any]
    ) -> Tuple[ReasoningType, float]:
        """Seleciona melhor tipo de raciocínio automaticamente"""
        
        scores: Dict[str, float] = {}
        
        # Calcular score para cada tipo
        for type_name, reasoning_type in self.reasoning_types.items():
            score = self._calculate_reasoning_score(
                reasoning_type,
                domain_characteristics,
                problem_type,
                constraints
            )
            scores[type_name] = score
        
        # Selecionar melhor
        best_type_name = max(scores, key=scores.get)
        best_type = self.reasoning_types[best_type_name]
        best_score = scores[best_type_name]
        
        # Registrar seleção
        self.selection_history.append({
            "timestamp": str(__import__('datetime').datetime.now()),
            "selected": best_type_name,
            "score": best_score,
            "all_scores": scores
        })
        
        return best_type, best_score
    
    def _calculate_reasoning_score(
        self,
        reasoning_type: ReasoningType,
        domain_characteristics: Dict[str, Any],
        problem_type: str,
        constraints: Dict[str, Any]
    ) -> float:
        """Calcula score para um tipo de raciocínio"""
        
        score = 0.0
        
        # 1. Compatibilidade com tipo de problema
        if problem_type in reasoning_type.best_for:
            score += 0.3
        
        # 2. Complexidade vs constraints
        max_complexity = constraints.get("max_complexity", 1.0)
        if reasoning_type.complexity <= max_complexity:
            score += 0.2 * (1 - reasoning_type.complexity / max_complexity)
        
        # 3. Confiança
        min_confidence = constraints.get("min_confidence", 0.0)
        if reasoning_type.confidence >= min_confidence:
            score += 0.3 * (reasoning_type.confidence / 1.0)
        
        # 4. Requisitos disponíveis
        available_data = domain_characteristics.get("available_data", [])
        required_met = sum(1 for req in reasoning_type.requirements if req in available_data)
        score += 0.2 * (required_met / max(len(reasoning_type.requirements), 1))
        
        return min(score, 1.0)
    
    def get_reasoning_type(self, name: str) -> Optional[ReasoningType]:
        """Retorna tipo de raciocínio por nome"""
        return self.reasoning_types.get(name)
    
    def get_reasoning_types_by_category(self, category: ReasoningCategory) -> List[ReasoningType]:
        """Retorna tipos de raciocínio por categoria"""
        return [
            rt for rt in self.reasoning_types.values()
            if rt.category == category
        ]
    
    def get_all_reasoning_types(self) -> List[ReasoningType]:
        """Retorna todos os tipos de raciocínio"""
        return list(self.reasoning_types.values())
    
    def generate_reasoning_report(self) -> str:
        """Gera relatório de raciocínio"""
        report = f"""
╔════════════════════════════════════════════════════════════════╗
║           MICRO REASONING TYPES REPORT                        ║
╚════════════════════════════════════════════════════════════════╝

Total Reasoning Types: {len(self.reasoning_types)}

By Category:
"""
        
        for category in ReasoningCategory:
            types_in_category = self.get_reasoning_types_by_category(category)
            report += f"\n  {category.value.upper()}: {len(types_in_category)} types"
            for rt in types_in_category:
                report += f"\n    - {rt.name} (complexity: {rt.complexity:.1f}, confidence: {rt.confidence:.1f})"
        
        report += f"\n\nSelection History: {len(self.selection_history)} selections"
        
        return report


# Exemplo de uso
if __name__ == "__main__":
    engine = MicroReasoningEngine()
    
    # Selecionar tipo de raciocínio
    domain_chars = {
        "available_data": ["implication", "premise", "multiple_observations"],
        "uncertainty": 0.3
    }
    
    reasoning_type, score = engine.select_reasoning_type(
        domain_chars,
        "validation",
        {"max_complexity": 0.5, "min_confidence": 0.7}
    )
    
    print(f"Selected: {reasoning_type.name}")
    print(f"Score: {score:.2f}")
    print(f"Formula: {reasoning_type.formula}")
    
    # Relatório
    print(engine.generate_reasoning_report())
