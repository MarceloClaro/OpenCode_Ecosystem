# -*- coding: utf-8 -*-
"""
Metacognitive Search Engine — SPEC-062
======================================
Implementa busca em árvore metacognitiva (Inference-Time Scaling) guiada
por um Process Verifier e monitoramento de loops em tempo de execução.

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger("metacognitive-search")


@dataclass
class ReasoningNode:
    """Nó da árvore de raciocínio contendo o estado do pensamento."""
    node_id: int
    parent_id: Optional[int]
    step_content: str
    depth: int
    score: float = 1.0
    accumulated_confidence: float = 1.0
    children: List[int] = field(default_factory=list)
    metacognitive_state: Dict[str, Any] = field(default_factory=dict)


class ProcessVerifier:
    """Avalia a corretude lógica e relevância de cada passo de raciocínio (Process Reward Model simplificado)."""

    @staticmethod
    def evaluate_step(step: str, problem_context: str, previous_steps: List[str]) -> Tuple[float, List[str]]:
        """Dá um score de 0.0 a 1.0 para o passo de raciocínio e retorna falhas detectadas."""
        score = 1.0
        flaws = []
        step_lower = step.lower()
        
        # 1. Checar contradições óbvias de auto-correção/conflitos
        contradiction_words = ["porém, não", "contradiz", "inconsistente", "erro na linha", "invalido"]
        for w in contradiction_words:
            if w in step_lower:
                score -= 0.25
                flaws.append(f"Contradição em potencial detectada pelo termo '{w}'.")

        # 2. Relevância em relação à pergunta
        # Extrai palavras-chave da pergunta
        question_words = [w for w in problem_context.lower().split() if len(w) > 4]
        matches = sum(1 for w in question_words if w in step_lower)
        if matches == 0 and len(question_words) > 0:
            score -= 0.15
            flaws.append("O passo possui baixa relevância com os termos do problema principal.")

        # 3. Complexidade / Raciocínio preguiçoso
        if len(step.split()) < 5:
            score -= 0.3
            flaws.append("Passo de raciocínio muito curto ou superficial.")

        # 4. Checar consistência com passos anteriores (detecção de loop de ideias)
        for prev in previous_steps:
            # Jaccard similarity simplificado
            w_prev = set(prev.lower().split())
            w_step = set(step_lower.split())
            if len(w_prev) > 0 and len(w_step) > 0:
                intersection = len(w_prev.intersection(w_step))
                union = len(w_prev.union(w_step))
                jaccard = intersection / union
                if jaccard > 0.7:
                    score -= 0.5
                    flaws.append("Ideia redundante ou repetitiva identificada em relação ao histórico.")
                    
        return max(0.0, score), flaws


class MetacognitiveMonitor:
    """Monitora o progresso cognitivo geral, detecção de loops globais e níveis de confiança."""

    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold

    def should_backtrack(self, node: ReasoningNode) -> bool:
        """Determina se o nó atual deve sofrer backtracking/poda."""
        # Se a confiança ou score cair abaixo do limite (threshold)
        if node.score < self.threshold:
            return True
        # Se o nó detectou loop grave em seu estado metacognitivo
        if node.metacognitive_state.get("loop_detected", False):
            return True
        return False


class MetacognitiveSearchEngine:
    """Motor de busca em árvore metacognitiva com backtracking e orçamento de computação."""

    def __init__(self, max_depth: int = 5, branch_factor: int = 3, min_score: float = 0.6):
        self.max_depth = max_depth
        self.branch_factor = branch_factor
        self.verifier = ProcessVerifier()
        self.monitor = MetacognitiveMonitor(threshold=min_score)
        self.node_counter = 0

    def search(self, problem: str, generation_callback: callable) -> Dict[str, Any]:
        """
        Executa busca em profundidade com backtracking.
        O generation_callback(node_context, k) simula a expansão de k alternativas.
        """
        nodes: Dict[int, ReasoningNode] = {}
        
        # Criar nó raiz
        root_id = self._next_id()
        root = ReasoningNode(
            node_id=root_id,
            parent_id=None,
            step_content="Início do raciocínio estruturado.",
            depth=0
        )
        nodes[root_id] = root
        
        # Expandir raiz para iniciar a lista de filhos a processar
        history = [root.step_content]
        alternatives = generation_callback(root.step_content, self.branch_factor)
        root_children = []
        backtrack_count = 0
        
        for alt in alternatives:
            score, flaws = self.verifier.evaluate_step(alt, problem, history)
            child_id = self._next_id()
            child_node = ReasoningNode(
                node_id=child_id,
                parent_id=root_id,
                step_content=alt,
                depth=1,
                score=score,
                accumulated_confidence=round(root.accumulated_confidence * score, 4),
                metacognitive_state={"flaws": flaws, "loop_detected": any("redundante" in f for f in flaws)}
            )
            nodes[child_id] = child_node
            root.children.append(child_id)
            if not self.monitor.should_backtrack(child_node):
                root_children.append(child_id)
            else:
                backtrack_count += 1
                
        stack = [([root_id], root_children)]
        solutions = []
        
        while stack:
            path, pending_children = stack[-1]
            
            if not pending_children:
                # Todos os caminhos deste ramo explorados, fazer backtrack
                stack.pop()
                backtrack_count += 1
                continue
                
            # Extrair próximo filho
            next_child_id = pending_children.pop()
            next_node = nodes[next_child_id]
            new_path = path + [next_child_id]
            
            if next_node.depth >= self.max_depth:
                solutions.append(new_path)
                continue
                
            # Expandir este nó gerando alternativas
            history = [nodes[nid].step_content for nid in new_path]
            alternatives = generation_callback(next_node.step_content, self.branch_factor)
            next_children = []
            
            for alt in alternatives:
                score, flaws = self.verifier.evaluate_step(alt, problem, history)
                child_id = self._next_id()
                child_node = ReasoningNode(
                    node_id=child_id,
                    parent_id=next_child_id,
                    step_content=alt,
                    depth=next_node.depth + 1,
                    score=score,
                    accumulated_confidence=round(next_node.accumulated_confidence * score, 4),
                    metacognitive_state={"flaws": flaws, "loop_detected": any("redundante" in f for f in flaws)}
                )
                nodes[child_id] = child_node
                next_node.children.append(child_id)
                if not self.monitor.should_backtrack(child_node):
                    next_children.append(child_id)
                else:
                    backtrack_count += 1
                    
            stack.append((new_path, next_children))

        # Selecionar a melhor trajetória
        best_path = []
        best_score = -1.0
        for path in solutions:
            path_score = sum(nodes[nid].score for nid in path) / len(path)
            if path_score > best_score:
                best_score = path_score
                best_path = path
                
        # Montar a explicação consolidada
        explanation = "\n".join([f"Passo {i}: {nodes[nid].step_content}" for i, nid in enumerate(best_path)])
        
        return {
            "status": "sucesso" if best_path else "inconclusivo",
            "best_path_nodes": best_path,
            "best_score": round(best_score, 4) if best_score >= 0 else 0.0,
            "total_nodes_explored": len(nodes),
            "backtracks": backtrack_count,
            "solution_explanation": explanation
        }

    def _next_id(self) -> int:
        self.node_counter += 1
        return self.node_counter


def solve_with_metacognitive_search(problem: str, difficulty: str = "medium") -> Dict[str, Any]:
    """Função de entrada que unifica e executa a busca metacognitiva com base em dificuldade."""
    # Configura orçamento de computação dinâmico
    depth = 3 if difficulty == "easy" else 5
    branch = 2 if difficulty == "easy" else 3
    
    engine = MetacognitiveSearchEngine(max_depth=depth, branch_factor=branch)
    
    # Mock do gerador de alternativas baseado no contexto
    def mock_generator(context: str, k: int) -> List[str]:
        import hashlib
        sentences = [
            "Primeiro analisamos as propriedades fundamentais dos inteiros envolvidos na equacao.",
            "Aplicamos o algoritmo de divisao euclidiana para reduzir o grau do problema.",
            "Provamos por inducao finita que a propriedade e valida para todo numero natural.",
            "Derivamos a formula de congruencia utilizando o pequeno teorema de Fermat.",
            "Consolidamos a demonstracao combinando os lemas anteriores em uma conclusao formal.",
            "Avaliamos o comportamento assintotico dos termos no limite infinito.",
            "Utilizamos a identidade de Bezout para garantir a existencia de solucoes inteiras.",
            "Verificamos se existem contra-exemplos minimos para a hipotese formulada.",
            "Esboçamos o grafo de transicoes para mapear os estados possiveis do sistema.",
            "Concluimos que o divisor comum obtido e de fato o maior possivel."
        ]
        idx = int(hashlib.md5(context.encode("utf-8")).hexdigest(), 16)
        return [sentences[(idx + i) % len(sentences)] for i in range(k)]

    return engine.search(problem, mock_generator)


if __name__ == "__main__":
    res = solve_with_metacognitive_search("Qual é o valor ótimo do problema X?")
    print(res)
