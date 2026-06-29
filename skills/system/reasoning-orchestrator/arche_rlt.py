# -*- coding: utf-8 -*-
"""
ARCHE Reasoning Logic Tree (RLT) — R28
Formaliza 212+ tipos de raciocinio nos 6 tipos de inferencia de Peirce
com arvores logicas auditaveis e composicao de inferencias.

Inspirado em: ARCHE Benchmark (Linsonng/ARCHEBenchmark)
"""

import uuid
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from datetime import datetime


class PeirceType(Enum):
    """Os 6 tipos de inferencia de Peirce (ARCHE Benchmark)"""
    DEDUCTION_RULE = "DR"       # Regra + Caso → Resultado (necessario)
    DEDUCTION_CASE = "DC"       # Regra + Resultado → Caso (probabilistico)
    INDUCTION_COMMON = "IC"     # Caso + Resultado → Regra (generalizacao)
    INDUCTION_HYPOTHESIS = "IH" # Resultado + Hipotese → Confirmacao (teste)
    ABDUCTION_KNOWLEDGE = "AK"  # Resultado + Regra → Explicacao (ontologia conhecida)
    ABDUCTION_PHENOMENON = "AP" # Resultado → Nova categoria (descoberta)

    @classmethod
    def from_string(cls, s: str) -> "PeirceType":
        mapping = {
            "DR": cls.DEDUCTION_RULE,
            "DC": cls.DEDUCTION_CASE,
            "IC": cls.INDUCTION_COMMON,
            "IH": cls.INDUCTION_HYPOTHESIS,
            "AK": cls.ABDUCTION_KNOWLEDGE,
            "AP": cls.ABDUCTION_PHENOMENON,
            "deduction_rule": cls.DEDUCTION_RULE,
            "deduction_case": cls.DEDUCTION_CASE,
            "induction_common": cls.INDUCTION_COMMON,
            "induction_hypothesis": cls.INDUCTION_HYPOTHESIS,
            "abduction_knowledge": cls.ABDUCTION_KNOWLEDGE,
            "abduction_phenomenon": cls.ABDUCTION_PHENOMENON,
        }
        return mapping.get(s.upper(), cls.ABDUCTION_PHENOMENON)


class LogicalCycleError(Exception):
    """Erro lancado quando um ciclo logico e detectado na RLT"""
    pass


class InvalidPremiseError(Exception):
    """Erro lancado quando uma premissa nao e valida"""
    pass


@dataclass
class RLTNode:
    """No da Reasoning Logic Tree"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    inference_type: PeirceType = PeirceType.ABDUCTION_KNOWLEDGE
    premise: str = ""
    conclusion: str = ""
    confidence: float = 1.0
    children: List["RLTNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "inference_type": self.inference_type.value,
            "inference_type_name": self.inference_type.name,
            "premise": self.premise,
            "conclusion": self.conclusion,
            "confidence": round(self.confidence, 4),
            "children": [c.to_dict() for c in self.children],
            "metadata": self.metadata,
            "created_at": self.created_at,
        }

    def add_child(self, child: "RLTNode") -> None:
        """Adiciona filho validando que a conclusao do filho alimenta a premissa do pai"""
        if child.conclusion and self.premise:
            # Verificacao fuzzy: conclusao do filho deve estar contida na premissa do pai
            child_words = set(child.conclusion.lower().split())
            premise_words = set(self.premise.lower().split())
            overlap = child_words & premise_words
            if len(overlap) < max(1, len(child_words) // 3):
                # Aviso mas nao bloqueia — pode ser inferencia indireta
                child.metadata["coherence_warning"] = (
                    f"Baixa sobreposicao: conclusao filho '{child.conclusion[:30]}...' "
                    f"na premissa pai '{self.premise[:30]}...'"
                )
        self.children.append(child)

    def count_nodes(self) -> int:
        """Conta total de nos na subarvore"""
        return 1 + sum(c.count_nodes() for c in self.children)

    def depth(self) -> int:
        """Retorna profundidade maxima da subarvore"""
        if not self.children:
            return 1
        return 1 + max(c.depth() for c in self.children)

    def get_inference_types_used(self) -> List[str]:
        """Retorna lista de tipos de inferencia usados na arvore"""
        types = [self.inference_type.value]
        for c in self.children:
            types.extend(c.get_inference_types_used())
        return list(set(types))


class ReasoningMapper:
    """
    Mapeia os 212+ tipos de raciocinio do ecossistema para os 6 tipos de Peirce.

    Mapping rules:
    - DR: dedutivo, silogistico, formal, algoritmico, Z3-verify
    - DC: probabilistico, bayesiano, numerico, estatistico
    - IC: indutivo, enumeracao, generalizacao, analogico
    - IH: hipotetico-dedutivo, teste, falsificacionista, experimento
    - AK: abdutivo, explicacao, diagnostico, causal, ontologico
    - AP: inovacao, descoberta, criativo, emergente, contrafactual
    """

    # Mapeamento de keywords para tipo Peirce
    KEYWORD_MAP: Dict[str, PeirceType] = {
        # DR — Deduction Rule
        "modus_ponens": PeirceType.DEDUCTION_RULE,
        "modus_tollens": PeirceType.DEDUCTION_RULE,
        "hypothetical_syllogism": PeirceType.DEDUCTION_RULE,
        "disjunctive_syllogism": PeirceType.DEDUCTION_RULE,
        "conjunction": PeirceType.DEDUCTION_RULE,
        "universal_instantiation": PeirceType.DEDUCTION_RULE,
        "identity": PeirceType.DEDUCTION_RULE,
        "direct_proof": PeirceType.DEDUCTION_RULE,
        "proof_by_contradiction": PeirceType.DEDUCTION_RULE,
        "proof_by_cases": PeirceType.DEDUCTION_RULE,
        "dedutivo": PeirceType.DEDUCTION_RULE,
        "silogistico": PeirceType.DEDUCTION_RULE,
        "formal": PeirceType.DEDUCTION_RULE,
        "algoritmico": PeirceType.DEDUCTION_RULE,
        "axiomatico": PeirceType.DEDUCTION_RULE,
        "primeiros_principios": PeirceType.DEDUCTION_RULE,
        "first_principles": PeirceType.DEDUCTION_RULE,
        "reducionista": PeirceType.DEDUCTION_RULE,
        # DC — Deduction Case
        "probabilistico": PeirceType.DEDUCTION_CASE,
        "bayesiano": PeirceType.DEDUCTION_CASE,
        "bayesian": PeirceType.DEDUCTION_CASE,
        "bayesian_inference": PeirceType.DEDUCTION_CASE,
        "bayesian_update": PeirceType.DEDUCTION_CASE,
        "prior": PeirceType.DEDUCTION_CASE,
        "likelihood": PeirceType.DEDUCTION_CASE,
        "posterior": PeirceType.DEDUCTION_CASE,
        "numerico": PeirceType.DEDUCTION_CASE,
        "estatistico": PeirceType.DEDUCTION_CASE,
        "statistical": PeirceType.DEDUCTION_CASE,
        # IC — Induction Common
        "indutivo": PeirceType.INDUCTION_COMMON,
        "inductive": PeirceType.INDUCTION_COMMON,
        "enumeracao": PeirceType.INDUCTION_COMMON,
        "enumeration": PeirceType.INDUCTION_COMMON,
        "generalizacao": PeirceType.INDUCTION_COMMON,
        "generalization": PeirceType.INDUCTION_COMMON,
        "analogico": PeirceType.INDUCTION_COMMON,
        "analogical": PeirceType.INDUCTION_COMMON,
        "analogy": PeirceType.INDUCTION_COMMON,
        "structural_analogy": PeirceType.INDUCTION_COMMON,
        "functional_analogy": PeirceType.INDUCTION_COMMON,
        "procedural_analogy": PeirceType.INDUCTION_COMMON,
        "relational_analogy": PeirceType.INDUCTION_COMMON,
        # IH — Induction Hypothesis
        "hipotetico_dedutivo": PeirceType.INDUCTION_HYPOTHESIS,
        "hypothetico_deductive": PeirceType.INDUCTION_HYPOTHESIS,
        "falsificacionista": PeirceType.INDUCTION_HYPOTHESIS,
        "falsificationist": PeirceType.INDUCTION_HYPOTHESIS,
        "cetico": PeirceType.INDUCTION_HYPOTHESIS,
        "skeptical": PeirceType.INDUCTION_HYPOTHESIS,
        "experimento": PeirceType.INDUCTION_HYPOTHESIS,
        "experiment": PeirceType.INDUCTION_HYPOTHESIS,
        "teste": PeirceType.INDUCTION_HYPOTHESIS,
        "test": PeirceType.INDUCTION_HYPOTHESIS,
        "causal_inductive": PeirceType.INDUCTION_HYPOTHESIS,
        # AK — Abduction Knowledge
        "abdutivo": PeirceType.ABDUCTION_KNOWLEDGE,
        "abductive": PeirceType.ABDUCTION_KNOWLEDGE,
        "abduction": PeirceType.ABDUCTION_KNOWLEDGE,
        "abduction_inductive": PeirceType.ABDUCTION_KNOWLEDGE,
        "explicacao": PeirceType.ABDUCTION_KNOWLEDGE,
        "explanation": PeirceType.ABDUCTION_KNOWLEDGE,
        "diagnostico": PeirceType.ABDUCTION_KNOWLEDGE,
        "diagnosis": PeirceType.ABDUCTION_KNOWLEDGE,
        "causal": PeirceType.ABDUCTION_KNOWLEDGE,
        "direct_causal": PeirceType.ABDUCTION_KNOWLEDGE,
        "indirect_causal": PeirceType.ABDUCTION_KNOWLEDGE,
        "common_cause": PeirceType.ABDUCTION_KNOWLEDGE,
        "confounder": PeirceType.ABDUCTION_KNOWLEDGE,
        "mediator": PeirceType.ABDUCTION_KNOWLEDGE,
        "ontologico": PeirceType.ABDUCTION_KNOWLEDGE,
        "ontological": PeirceType.ABDUCTION_KNOWLEDGE,
        "teleologico": PeirceType.ABDUCTION_KNOWLEDGE,
        "teleological": PeirceType.ABDUCTION_KNOWLEDGE,
        # AP — Abduction Phenomenon
        "inovacao": PeirceType.ABDUCTION_PHENOMENON,
        "innovation": PeirceType.ABDUCTION_PHENOMENON,
        "descoberta": PeirceType.ABDUCTION_PHENOMENON,
        "discovery": PeirceType.ABDUCTION_PHENOMENON,
        "criativo": PeirceType.ABDUCTION_PHENOMENON,
        "creative": PeirceType.ABDUCTION_PHENOMENON,
        "emergente": PeirceType.ABDUCTION_PHENOMENON,
        "emergent": PeirceType.ABDUCTION_PHENOMENON,
        "contrafactual": PeirceType.ABDUCTION_PHENOMENON,
        "counterfactual": PeirceType.ABDUCTION_PHENOMENON,
        "simple_counterfactual": PeirceType.ABDUCTION_PHENOMENON,
        "conditional_counterfactual": PeirceType.ABDUCTION_PHENOMENON,
        "multiple_counterfactual": PeirceType.ABDUCTION_PHENOMENON,
        "iterative_counterfactual": PeirceType.ABDUCTION_PHENOMENON,
        "lateral": PeirceType.ABDUCTION_PHENOMENON,
        "lateral_thinking": PeirceType.ABDUCTION_PHENOMENON,
        "divergente": PeirceType.ABDUCTION_PHENOMENON,
        "divergent": PeirceType.ABDUCTION_PHENOMENON,
    }

    # Categorias para fallback por prefixo
    CATEGORY_PREFIX_MAP: Dict[str, PeirceType] = {
        "deduct": PeirceType.DEDUCTION_RULE,
        "syllog": PeirceType.DEDUCTION_RULE,
        "proof": PeirceType.DEDUCTION_RULE,
        "bayes": PeirceType.DEDUCTION_CASE,
        "prob": PeirceType.DEDUCTION_CASE,
        "induct": PeirceType.INDUCTION_COMMON,
        "general": PeirceType.INDUCTION_COMMON,
        "enumer": PeirceType.INDUCTION_COMMON,
        "analog": PeirceType.INDUCTION_COMMON,
        "hypoth": PeirceType.INDUCTION_HYPOTHESIS,
        "falsif": PeirceType.INDUCTION_HYPOTHESIS,
        "exper": PeirceType.INDUCTION_HYPOTHESIS,
        "abduct": PeirceType.ABDUCTION_KNOWLEDGE,
        "causal": PeirceType.ABDUCTION_KNOWLEDGE,
        "diagn": PeirceType.ABDUCTION_KNOWLEDGE,
        "explic": PeirceType.ABDUCTION_KNOWLEDGE,
        "counter": PeirceType.ABDUCTION_PHENOMENON,
        "creativ": PeirceType.ABDUCTION_PHENOMENON,
        "emerge": PeirceType.ABDUCTION_PHENOMENON,
        "lateral": PeirceType.ABDUCTION_PHENOMENON,
        "diverg": PeirceType.ABDUCTION_PHENOMENON,
        "innov": PeirceType.ABDUCTION_PHENOMENON,
    }

    def __init__(self):
        self._coverage: Dict[str, str] = {}  # reasoning_type -> peirce_type

    def map_reasoning_type(self, reasoning_type: str) -> PeirceType:
        """
        Mapeia um tipo de raciocinio para o tipo Peirce correspondente.
        Usa busca exata -> prefixo -> fallback AK.
        """
        # Normalizacao
        normalized = reasoning_type.strip().lower().replace(" ", "_").replace("-", "_")
        normalized = normalized.replace("á", "a").replace("ã", "a").replace("â", "a")
        normalized = normalized.replace("é", "e").replace("ê", "e").replace("í", "i")
        normalized = normalized.replace("ó", "o").replace("ô", "o").replace("ú", "u")
        normalized = normalized.replace("ç", "c")

        # 1. Busca exata
        if normalized in self.KEYWORD_MAP:
            result = self.KEYWORD_MAP[normalized]
            self._coverage[reasoning_type] = result.value
            return result

        # 2. Busca por prefixo
        for prefix, pt in self.CATEGORY_PREFIX_MAP.items():
            if normalized.startswith(prefix):
                self._coverage[reasoning_type] = pt.value
                return pt

        # 3. Busca parcial (palavra contida)
        for keyword, pt in self.KEYWORD_MAP.items():
            if keyword in normalized or normalized in keyword:
                self._coverage[reasoning_type] = pt.value
                return pt

        # 4. Fallback: Abduction Knowledge (explicacao)
        self._coverage[reasoning_type] = PeirceType.ABDUCTION_KNOWLEDGE.value
        return PeirceType.ABDUCTION_KNOWLEDGE

    def get_coverage_report(self) -> Dict[str, Any]:
        """Retorna relatorio de cobertura do mapeamento"""
        type_counts: Dict[str, int] = {}
        for rt, pt in self._coverage.items():
            type_counts[pt] = type_counts.get(pt, 0) + 1

        return {
            "total_mapped": len(self._coverage),
            "by_peirce_type": type_counts,
            "unmapped": [],
        }

    def map_all_known_types(self) -> Dict[str, str]:
        """Mapeia todos os tipos conhecidos do ecossistema"""
        known_types = list(self.KEYWORD_MAP.keys())
        result = {}
        for t in known_types:
            result[t] = self.map_reasoning_type(t).value
        return result


class RLTBuilder:
    """
    Construtor de Reasoning Logic Trees.

    Constroi arvores a partir de:
    - Lista de passos de raciocinio encadeados
    - Pergunta + cadeia de inferencia
    - Pipeline OQS (pergunta otima) -> RLT
    """

    def __init__(self, mapper: Optional[ReasoningMapper] = None):
        self.mapper = mapper or ReasoningMapper()
        self.max_depth = 10

    def build_from_steps(self, steps: List[Dict]) -> RLTNode:
        """
        Constroi RLT a partir de uma lista de passos.

        Cada passo deve ter:
        - premise: str
        - conclusion: str
        - inference_type: str (opcional, mapeado se ausente)
        - confidence: float (opcional, default 1.0)
        """
        if not steps:
            raise InvalidPremiseError("Lista de passos vazia")

        # Validar ciclos
        self._check_cycles(steps)

        # Construir nos de baixo para cima
        nodes = []
        for i, step in enumerate(steps):
            inference_type_str = step.get("inference_type", "")
            if inference_type_str:
                pt = self.mapper.map_reasoning_type(inference_type_str)
            else:
                pt = PeirceType.ABDUCTION_KNOWLEDGE

            node = RLTNode(
                inference_type=pt,
                premise=step.get("premise", ""),
                conclusion=step.get("conclusion", ""),
                confidence=step.get("confidence", 1.0),
                metadata={"step_index": i},
            )
            nodes.append(node)

        # Conectar em arvore: cada no e filho do anterior
        root = nodes[-1]  # segura porque testamos not steps no inicio
        for i in range(len(nodes) - 2, -1, -1):
            nodes[i + 1].add_child(nodes[i])

        # Verificar profundidade maxima
        if root.depth() > self.max_depth:
            self._truncate(root, self.max_depth)

        return root

    def build_from_premises(self, premises: List[str],
                            conclusion: str,
                            inference_type: str = "abduction") -> RLTNode:
        """Constroi RLT simples a partir de premissas e conclusao"""
        pt = self.mapper.map_reasoning_type(inference_type)

        # Criar nos folha (premissas)
        leaf_nodes = []
        for i, premise in enumerate(premises):
            leaf = RLTNode(
                inference_type=PeirceType.DEDUCTION_RULE,
                premise=premise,
                conclusion=premise,
                confidence=1.0,
                metadata={"is_premise": True, "index": i},
            )
            leaf_nodes.append(leaf)

        # No intermediario: combina premissas
        if len(leaf_nodes) > 1:
            combined_premise = "; ".join(premises)
            mid = RLTNode(
                inference_type=PeirceType.INDUCTION_COMMON,
                premise=combined_premise,
                conclusion=f"Evidencias combinadas: {len(premises)} premissas",
                confidence=min(1.0, 0.8 + 0.05 * len(premises)),
                metadata={"is_combined": True},
            )
            for leaf in leaf_nodes:
                mid.add_child(leaf)
            parent = mid
        else:
            parent = leaf_nodes[0]

        # No raiz: conclusao final
        root = RLTNode(
            inference_type=pt,
            premise=parent.conclusion,
            conclusion=conclusion,
            confidence=parent.confidence * 0.9,
        )
        root.add_child(parent)

        return root

    def _check_cycles(self, steps: List[Dict]) -> None:
        """Verifica se ha ciclos logicos nos passos"""
        conclusions = set()
        for step in steps:
            conc = step.get("conclusion", "").strip().lower()
            prem = step.get("premise", "").strip().lower()
            if conc and conc == prem and len(conc) > 10:
                raise LogicalCycleError(
                    f"Ciclo logico detectado: conclusao == premissa ('{conc[:50]}...')"
                )
            if conc in conclusions:
                raise LogicalCycleError(
                    f"Conclusao duplicada: '{conc[:50]}...' aparece em mais de um passo"
                )
            conclusions.add(conc)

    def _truncate(self, node: RLTNode, max_depth: int) -> None:
        """Trunca arvore para profundidade maxima"""
        if max_depth <= 1:
            node.children = []
            node.metadata["truncated"] = True
            return
        for child in node.children:
            self._truncate(child, max_depth - 1)

    def to_json(self, root: RLTNode, indent: int = 2) -> str:
        """Exporta RLT como JSON"""
        return json.dumps(root.to_dict(), indent=indent, ensure_ascii=False)

    def to_mermaid(self, root: RLTNode) -> str:
        """Exporta RLT como diagrama Mermaid"""
        lines = ["graph TD"]
        node_id_map: Dict[str, str] = {}

        def _add_node(node: RLTNode, counter: List[int]) -> str:
            c = counter[0]
            counter[0] += 1
            label = f"{node.inference_type.value}: {node.conclusion[:40]}..."
            node_id = f"N{c}"
            node_id_map[node.id] = node_id
            lines.append(f'    {node_id}["{label}"]')
            for child in node.children:
                child_id = _add_node(child, counter)
                lines.append(f"    {node_id} --> {child_id}")
            return node_id

        _add_node(root, [0])
        return "\n".join(lines)


class RLTValidator:
    """
    Validador de coerencia logica da RLT.

    Verifica:
    - Coerencia: conclusao filho -> premissa pai
    - Fecho: raiz contem conclusao final
    - Profundidade maxima
    - Integridade dos nos
    """

    @staticmethod
    def validate(root: RLTNode) -> Dict[str, Any]:
        """Valida RLT completa. Retorna relatorio."""
        issues = []
        total_gaps = 0

        def _validate_node(node: RLTNode, path: List[str]) -> None:
            nonlocal total_gaps
            for child in node.children:
                # Verificar coerencia
                if child.conclusion and node.premise:
                    child_words = set(child.conclusion.lower().split())
                    premise_words = set(node.premise.lower().split())
                    overlap = child_words & premise_words
                    if len(overlap) == 0:
                        total_gaps += 1
                        issues.append({
                            "type": "coherence_gap",
                            "severity": "warning",
                            "node_id": child.id,
                            "detail": f"Conclusao '{child.conclusion[:40]}...' nao se conecta com premissa '{node.premise[:40]}...'",
                        })

                # Verificar confianca
                if child.confidence <= 0:
                    issues.append({
                        "type": "zero_confidence",
                        "severity": "error",
                        "node_id": child.id,
                        "detail": f"Confianca zero no no {child.id}",
                    })

                _validate_node(child, path + [child.id])

        _validate_node(root, [root.id])

        # Calcular metrics
        depth = root.depth()
        total_nodes = root.count_nodes()

        return {
            "is_valid": len([i for i in issues if i["severity"] == "error"]) == 0,
            "total_nodes": total_nodes,
            "depth": depth,
            "max_depth_exceeded": depth > 10,
            "coherence_gaps": total_gaps,
            "inference_types_used": root.get_inference_types_used(),
            "issues": issues,
            "root_confidence": round(root.confidence, 4),
        }

    @staticmethod
    def compute_root_confidence(root: RLTNode) -> float:
        """Propaga confianca dos filhos para a raiz"""
        if not root.children:
            return root.confidence

        child_confidences = [
            RLTValidator.compute_root_confidence(c) for c in root.children
        ]
        avg_child_conf = sum(child_confidences) / len(child_confidences)
        return round(root.confidence * avg_child_conf, 4)


class ARCHEEngine:
    """
    Motor principal ARCHE RLT.

    Integra:
    - ReasoningMapper (mapeamento 212+ tipos -> 6 Peirce)
    - RLTBuilder (construcao de arvores)
    - RLTValidator (validacao de coerencia)
    - Pipeline OQS (R27) -> ARCHE RLT
    """

    def __init__(self):
        self.mapper = ReasoningMapper()
        self.builder = RLTBuilder(mapper=self.mapper)
        self.validator = RLTValidator()

    def analyze_reasoning_chain(self, steps: List[Dict]) -> Dict[str, Any]:
        """
        Analisa uma cadeia de raciocinio completa.

        Args:
            steps: Lista de dicionarios com premise, conclusion,
                  inference_type (opcional), confidence (opcional)

        Returns:
            Dict com RLT, validacao e metadados
        """
        # Construir RLT
        root = self.builder.build_from_steps(steps)

        # Validar
        validation = self.validator.validate(root)
        root_confidence = self.validator.compute_root_confidence(root)

        # Atualizar confianca na raiz
        root.confidence = root_confidence

        # Mapa de tipos usados
        type_map = {}
        for step in steps:
            it = step.get("inference_type", "")
            if it:
                pt = self.mapper.map_reasoning_type(it)
                type_map[it] = pt.value

        return {
            "rlt": root.to_dict(),
            "validation": validation,
            "root_confidence": root_confidence,
            "type_mapping": type_map,
            "mermaid": self.builder.to_mermaid(root),
            "total_nodes": root.count_nodes(),
            "depth": root.depth(),
        }

    def map_all_reasoning_types(self) -> Dict[str, Any]:
        """Mapeia todos os tipos de raciocinio conhecidos"""
        mapping = self.mapper.map_all_known_types()
        coverage = self.mapper.get_coverage_report()

        # Estatisticas
        type_counts: Dict[str, int] = {}
        for pt in mapping.values():
            type_counts[pt] = type_counts.get(pt, 0) + 1

        return {
            "total_types_mapped": len(mapping),
            "mapping": mapping,
            "by_peirce_type": type_counts,
            "coverage_report": coverage,
            "peirce_types": [t.value for t in PeirceType],
        }

    def pipeline_oqs_to_rlt(self, oqs_result: Dict) -> Dict[str, Any]:
        """
        Pipeline: OQS (R27) -> ARCHE RLT (R28).

        Recebe resultado do Optimal Question Scanner e constroi RLT.
        """
        optimal_question = oqs_result.get("optimal_question", "")
        uncertainty_categories = oqs_result.get("uncertainty_categories", [])
        convergence_score = oqs_result.get("convergence_score", 0.5)

        # Construir passos a partir da pergunta otima
        steps = [
            {
                "premise": f"Problema analisado com incertezas: {', '.join(uncertainty_categories[:3])}",
                "conclusion": f"Questao otima formulada: {optimal_question[:100]}",
                "inference_type": "abduction_knowledge",
                "confidence": convergence_score,
            }
        ]

        root = self.builder.build_from_steps(steps)
        validation = self.validator.validate(root)

        return {
            "optimal_question": optimal_question,
            "rlt": root.to_dict(),
            "validation": validation,
            "convergence_score": convergence_score,
            "pipeline": "OQS -> ARCHE RLT",
        }
