# -*- coding: utf-8 -*-
"""
MICRO REASONING TYPES v5.0 - Sem necessidade de DI (logica pura de tipos).

Analise:
- MicroReasoningEngine e um motor de selecao de tipos de raciocinio
- Nao importa core.state_manager, core.event_bus ou qualquer infra
- Dependencias: dataclasses, typing, enum, json
- E uma biblioteca de tipos/classificacao, nao um servico

Decisao:
- NAO requer refatoracao DI
- Mantido como modulo de logica pura
- Copia documentada para referencia de arquitetura
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

class ReasoningCategory(Enum):
    DEDUCTIVE = "deductive"; INDUCTIVE = "inductive"; CAUSAL = "causal"
    COUNTERFACTUAL = "counterfactual"; BAYESIAN = "bayesian"
    ANALOGICAL = "analogical"; FORMAL = "formal"; ABDUCTIVE = "abductive"

@dataclass
class ReasoningType:
    name: str; category: ReasoningCategory; description: str; formula: str
    requirements: List[str]; strengths: List[str]; weaknesses: List[str]
    best_for: List[str]; complexity: float; confidence: float
    def to_dict(self) -> Dict:
        return {"name":self.name,"category":self.category.value,"description":self.description,
            "formula":self.formula,"requirements":self.requirements,"strengths":self.strengths,
            "weaknesses":self.weaknesses,"best_for":self.best_for,
            "complexity":self.complexity,"confidence":self.confidence}

class MicroReasoningEngine:
    def __init__(self):
        self.reasoning_types: Dict[str, ReasoningType] = {}
        self._init_all_reasoning_types()
        self.selection_history: List[Dict] = []

    def _init_all_reasoning_types(self):
        self._init_deductive_types(); self._init_inductive_types()
        self._init_causal_types(); self._init_counterfactual_types()
        self._init_bayesian_types(); self._init_analogical_types()
        self._init_formal_types(); self._init_abductive_types()

    def _init_deductive_types(self):
        for t in [
            ("modus_ponens","Modus Ponens","Se A implica B, e A e verdadeiro, entao B e verdadeiro",
             ["implication","premise"],["validacao","verificacao","aplicacao de regras"],0.3,0.95),
            ("modus_tollens","Modus Tollens","Se A implica B, e B e falso, entao A e falso",
             ["implication","negated_conclusion"],["refutacao","eliminacao","diagnostico negativo"],0.3,0.95),
            ("hypothetical_syllogism","Hypothetical Syllogism","Se A implica B, e B implica C, entao A implica C",
             ["chain_of_implications"],["rastreamento de consequencias","planejamento"],0.4,0.95),
            ("disjunctive_syllogism","Disjunctive Syllogism","Se A ou B, e nao A, entao B",
             ["disjunction","negated_alternative"],["eliminacao de alternativas","classificacao"],0.3,0.95),
            ("conjunction","Conjunction","Se A e verdadeiro e B e verdadeiro, entao A e B e verdadeiro",
             ["multiple_premises"],["combinacao de fatos","sintese"],0.2,0.99),
            ("negation","Negation (Contradiction)","Se A e nao A, entao contradicao",
             ["contradiction"],["deteccao de erro","validacao"],0.2,0.99),
            ("universal_instantiation","Universal Instantiation","Se para todo x P(x), entao P(a)",
             ["universal_quantification"],["aplicacao de regras","especializacao"],0.4,0.95),
            ("identity","Identity","Se a = b e P(a), entao P(b)",
             ["equality","property"],["substituicao","simplificacao"],0.3,0.95)
        ]:
            self.reasoning_types[t[0]] = ReasoningType(name=t[1],category=ReasoningCategory.DEDUCTIVE,
                description=t[2],formula="",requirements=t[3],strengths=[],weaknesses=[],
                best_for=t[4],complexity=t[5],confidence=t[6])

    def _init_inductive_types(self):
        # Fallbacks vazios ou placeholders para manter compatibilidade com _init_all_reasoning_types
        pass

    def _init_causal_types(self):
        pass

    def _init_counterfactual_types(self):
        pass

    def _init_bayesian_types(self):
        pass

    def _init_analogical_types(self):
        pass

    def _init_formal_types(self):
        pass

    def _init_abductive_types(self):
        pass

    def select_reasoning_type(self, dc: Dict[str,Any], pt: str, cons: Dict[str,Any]) -> Tuple[ReasoningType, float]:
        scores = {}
        for n, rt in self.reasoning_types.items():
            sc = 0.0
            if pt in rt.best_for: sc += 0.3
            mc = cons.get("max_complexity",1.0)
            if rt.complexity <= mc: sc += 0.2*(1-rt.complexity/mc)
            if rt.confidence >= cons.get("min_confidence",0.0): sc += 0.3*(rt.confidence/1.0)
            ad = dc.get("available_data",[])
            sc += 0.2*sum(1 for r in rt.requirements if r in ad)/max(len(rt.requirements),1)
            scores[n] = min(sc,1.0)
        
        # Fallback se scores estiver vazio
        if not scores:
            # Retorna um reasoning type padrão para evitar KeyError
            for n, rt in self.reasoning_types.items():
                return rt, 1.0
            # Se nem isso, retorna um genérico
            dummy = ReasoningType(name="Default deductive", category=ReasoningCategory.DEDUCTIVE,
                                  description="Default", formula="", requirements=[], strengths=[],
                                  weaknesses=[], best_for=[], complexity=0.1, confidence=0.9)
            return dummy, 1.0

        bn = max(scores,key=scores.get)
        self.selection_history.append({"selected":bn,"score":scores[bn]})
        return self.reasoning_types[bn], scores[bn]

    def get_reasoning_type(self, name: str) -> Optional[ReasoningType]:
        return self.reasoning_types.get(name)

    def get_reasoning_types_by_category(self, cat: ReasoningCategory) -> List[ReasoningType]:
        return [rt for rt in self.reasoning_types.values() if rt.category==cat]

    def get_all_reasoning_types(self) -> List[ReasoningType]:
        return list(self.reasoning_types.values())

    def generate_reasoning_report(self) -> str:
        return f"Total Reasoning Types: {len(self.reasoning_types)}\nSelection History: {len(self.selection_history)} selections"
