"""BaseAgent — classe abstrata para agentes de IA.

Todos os agentes DEVEM herdar desta classe.
"""

from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Classe base abstrata para agentes de IA.

    Attributes:
        model: Nome do modelo (ex: 'deepseek-v4-flash').
        api_key: Chave de API.
    """

    model: str = ""
    api_key: str = ""

    @abstractmethod
    def execute(self, input_data: str) -> dict:
        """Executa o agente com os dados de entrada.

        Args:
            input_data: Texto de entrada para o agente processar.

        Returns:
            Dicionário com o resultado do processamento.
        """
        ...
