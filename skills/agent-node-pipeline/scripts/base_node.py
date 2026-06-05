"""
BaseNode — Contrato abstrato para todos os nós do pipeline ANP.

Hierarquia:
  BaseNode (interface genérica)
    └── StateMutationNode (nó que transforma o estado do pipeline)

Inspirado por BaseNode em BettaFish QueryEngine/nodes/base_node.py.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

# Import compatível com execução direta e como módulo
try:
    from .pipeline_state import PipelineState
except ImportError:
    from pipeline_state import PipelineState


class BaseNode(ABC):
    """Nó base abstrato. Todo nó no pipeline deve estender esta classe.

    Attributes:
        node_name: Identificador do nó (default: nome da classe).
    """

    def __init__(self, node_name: str = ""):
        self.node_name = node_name or self.__class__.__name__

    # ── Interface obrigatória ──────────────────────────────────────────

    @abstractmethod
    def run(self, input_data: Any, **kwargs) -> Any:
        """Executa a lógica central do nó.

        Args:
            input_data: Dados de entrada (qualquer tipo serializável).
            **kwargs: Parâmetros adicionais específicos do nó.

        Returns:
            Resultado do processamento.
        """
        ...

    # ── Hooks opcionais ────────────────────────────────────────────────

    def validate_input(self, input_data: Any) -> bool:
        """Valida se a entrada é adequada antes de processar.

        Retorna True se válida. Sobrescreva para lógica customizada.
        """
        return True

    def process_output(self, output: Any) -> Any:
        """Pós-processamento do resultado bruto do run().

        Útil para limpeza, transformação ou validação de saída.
        """
        return output

    # ── Utilitários ────────────────────────────────────────────────────

    def describe(self) -> Dict[str, Any]:
        """Metadados do nó para inspeção/debug."""
        return {
            "node_name": self.node_name,
            "class": self.__class__.__name__,
            "module": self.__class__.__module__,
        }


class StateMutationNode(BaseNode):
    """Nó que transforma o estado do pipeline.

    Estende BaseNode adicionando o método mutate_state(), que recebe
    o PipelineState atual e retorna uma nova instância modificada.

    Este é o padrão central dos nós do BettaFish: cada nó recebe
    o estado, aplica sua transformação e retorna o novo estado.
    """

    @abstractmethod
    def mutate_state(
        self,
        input_data: Any,
        state: PipelineState,
        **kwargs,
    ) -> PipelineState:
        """Transforma o estado do pipeline.

        Args:
            input_data: Dados de entrada para o nó.
            state: Estado atual do pipeline (NÃO modificado in-place).
            **kwargs: Parâmetros adicionais.

        Returns:
            Nova instância de PipelineState com as modificações aplicadas.
        """
        ...

    # Conveniência: run() delega para mutate_state com state vazio
    def run(self, input_data: Any, **kwargs) -> Any:
        new_state = self.mutate_state(input_data, PipelineState(), **kwargs)
        return new_state
