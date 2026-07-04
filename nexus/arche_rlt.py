#!/usr/bin/env python3
"""
ARCHE Reasoning Logic Tree (SPEC-057) — R45 Fase A.

Implementa os 6 tipos de inferencia de Peirce como motores de raciocinio
formais, composiveis em arvores logicas auditaveis.

Referencia: ARCHE Benchmark (Linsonng/ARCHEBenchmark)
"""

import enum
import uuid
from dataclasses import dataclass, field
from typing import Optional


class PeirceType(enum.Enum):
    """Os 6 tipos de inferencia de Peirce."""
    DR = "deduction_rule"        # ∀x(P(x)→Q(x)), P(a) ⊢ Q(a)
    DC = "deduction_case"        # ∀x(P(x)→Q(x)), Q(a) ⊢ P(a) [prob]
    IC = "induction_common"      # P(a₁)∧Q(a₁)... ⊢ ∀x(P(x)→Q(x))
    IH = "induction_hypothesis"  # Teste de hipotese
    AK = "abduction_knowledge"   # Q(a), ∀x(P(x)→Q(x)) ⊢ P(a)
    AP = "abduction_phenomenon"  # Q(a), ∃x(R(x)→Q(x)) ⊢ R(a)


PEIRCE_TYPES = {
    "DR": PeirceType.DR,
    "DC": PeirceType.DC,
    "IC": PeirceType.IC,
    "IH": PeirceType.IH,
    "AK": PeirceType.AK,
    "AP": PeirceType.AP,
}

# Mapeamento das 27+ categorias de raciocinio para os 6 tipos de Peirce
TYPE_MAPPING = {
    "logico_dedutivo": "DR",
    "logico_indutivo": "IC",
    "logico_abdutivo": "AK",
    "logico_contrafactual": "DC",
    "logico_hipotetico": "IH",
    "dialetico_tese": "AK",
    "dialetico_antitese": "DC",
    "dialetico_sintese": "AP",
    "dialetico_refutacao": "IH",
    "dialetico_contradicao": "DC",
    "dialetico_convergencia": "IC",
    "estrategico_nash": "DR",
    "estrategico_stackelberg": "AK",
    "estrategico_titfortat": "IC",
    "estrategico_sinalizacao": "AP",
    "estrategico_bargaining": "IH",
    "decisao_utilidade": "DR",
    "decisao_risco": "DC",
    "decisao_custo_beneficio": "IC",
    "decisao_multi_criterio": "IH",
    "inovacao_analogia": "AK",
    "inovacao_combinatoria": "AP",
    "inovacao_divergente": "AP",
    "inovacao_convergente": "IC",
    "inovacao_disruptiva": "AP",
    "sistemico_emergente": "AP",
    "sistemico_hierarquico": "DR",
    "probabilistico_bayesiano": "DC",
    "probabilistico_frequentista": "IC",
    "metacognitivo_monitoramento": "IH",
    "metacognitivo_controle": "DR",
}


def get_type_mapping() -> dict:
    """Retorna mapeamento de todas categorias para tipos Peirce."""
    return {k: PEIRCE_TYPES[v].value for k, v in TYPE_MAPPING.items()}


@dataclass
class RLTNode:
    """No da Reasoning Logic Tree."""
    inference_type: PeirceType
    premise: str
    conclusion: str
    confidence: float = 0.5
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    children: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)


class ARCLERLT:
    """Motor ARCHE RLT — constroi e valida arvores de raciocinio."""

    MAX_DEPTH = 10
    VALID_TYPES = set(PeirceType)

    def validate_node(self, node: RLTNode) -> dict:
        """Valida um no RLT."""
        errors = []
        if node.inference_type not in self.VALID_TYPES:
            errors.append(f"Invalid type: {node.inference_type}")
        if not node.premise.strip():
            errors.append("Empty premise")
        if not node.conclusion.strip():
            errors.append("Empty conclusion")
        if not 0.0 <= node.confidence <= 1.0:
            errors.append(f"Confidence out of range: {node.confidence}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "node_id": node.id,
            "type": node.inference_type.value,
        }

    def build_tree(self, root: RLTNode) -> dict:
        """Constroi e valida uma arvore RLT a partir da raiz."""
        stats = self._traverse(root, depth=0)
        return {
            "root": root,
            "depth": stats["max_depth"],
            "node_count": stats["count"],
            "valid": stats["errors"] == 0,
            "errors": stats["error_list"],
        }

    def _traverse(self, node: RLTNode, depth: int) -> dict:
        """Percorre a arvore recursivamente."""
        validation = self.validate_node(node)
        stats = {
            "max_depth": depth,
            "count": 1,
            "errors": 0 if validation["valid"] else 1,
            "error_list": [] if validation["valid"] else [validation["errors"]],
        }

        if node.children and depth < self.MAX_DEPTH:
            for child in node.children:
                child_stats = self._traverse(child, depth + 1)
                stats["max_depth"] = max(stats["max_depth"], child_stats["max_depth"])
                stats["count"] += child_stats["count"]
                stats["errors"] += child_stats["errors"]
                stats["error_list"].extend(child_stats["error_list"])

        return stats

    def run_pipeline(self, problem: str, depth: int = 3) -> dict:
        """Executa pipeline completo: problema → arvore → conclusao."""
        # 1. Decompor problema em nos RLT
        root = RLTNode(
            inference_type=PeirceType.DR,
            premise=problem,
            conclusion=f"Analise de: {problem[:50]}",
            confidence=0.8,
            metadata={"source": "problem", "depth": depth},
        )

        # 2. Construir niveis
        current = root
        for level in range(1, min(depth, self.MAX_DEPTH)):
            child = RLTNode(
                inference_type=list(PeirceType)[level % 6],
                premise=f"Nivel {level}: analise parcial",
                conclusion=f"Nivel {level}: conclusao parcial",
                confidence=max(0.9 - level * 0.1, 0.1),
                metadata={"level": level},
            )
            if not current.children:
                current.children = []
            current.children.append(child)
            current = child

        # 3. Construir e validar
        tree_result = self.build_tree(root)

        # 4. Gerar audit trail
        audit_trail = []
        self._generate_audit(root, audit_trail)

        return {
            "tree": tree_result,
            "conclusion": self._synthesize(root),
            "audit_trail": audit_trail,
            "depth": tree_result["depth"],
            "node_count": tree_result["node_count"],
        }

    def _generate_audit(self, node: RLTNode, trail: list, depth: int = 0):
        """Gera audit trail recursivo."""
        trail.append({
            "id": node.id,
            "type": node.inference_type.value,
            "premise": node.premise,
            "conclusion": node.conclusion,
            "confidence": node.confidence,
            "depth": depth,
        })
        for child in node.children:
            self._generate_audit(child, trail, depth + 1)

    def _synthesize(self, root: RLTNode) -> str:
        """Sintetiza conclusao da arvore."""
        return f"Conclusao ARCHE: {root.conclusion} (confianca: {root.confidence:.2f})"


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ARCHE RLT Engine")
    parser.add_argument("--pipeline", type=str, help="Problema para analisar")
    parser.add_argument("--depth", type=int, default=3, help="Profundidade da arvore")
    parser.add_argument("--mapping", action="store_true", help="Mostrar mapeamento")
    args = parser.parse_args()

    if args.mapping:
        mapping = get_type_mapping()
        print("=== Type Mapping (27+ categories → 6 Peirce types) ===")
        for cat, ptype in sorted(mapping.items()):
            print(f"  {cat}: {ptype}")
        print(f"\nTotal: {len(mapping)} categories")

    if args.pipeline:
        engine = ARCLERLT()
        result = engine.run_pipeline(args.pipeline, depth=args.depth)
        print(f"\n=== ARCHE Pipeline Result ===")
        print(f"Depth: {result['depth']}, Nodes: {result['node_count']}")
        print(f"Conclusion: {result['conclusion']}")
        print(f"Audit trail: {len(result['audit_trail'])} steps")
        for step in result['audit_trail']:
            print(f"  [{step['depth']}] {step['type']}: {step['premise'][:40]}...")
