"""
Contract Registry — Implementação do registro central de contratos.

Permite registrar, consultar e verificar aderência de contratos entre módulos.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal


class ContractStatus(str, Enum):
    """Status de um contrato no registro."""
    STABLE = "stable"
    DRAFT = "draft"
    DEPRECATED = "deprecated"


@dataclass
class ContractEntry:
    """Metadados de um contrato registrado.

    Attributes:
        name: Nome único do contrato (ex: "IStateManager")
        interface_type: Nome da classe ABC/Protocol
        module_path: Caminho do módulo onde o contrato está definido
        implementations: Lista de caminhos de módulos que implementam o contrato
        version: Versão semântica do contrato
        status: Status (stable, draft, deprecated)
        test_suite: Caminho para testes de contrato (opcional)
        description: Descrição do contrato
        created_at: Timestamp de criação
    """
    name: str
    interface_type: str
    module_path: str
    implementations: list[str] = field(default_factory=list)
    version: str = "1.0.0"
    status: ContractStatus = ContractStatus.DRAFT
    test_suite: str | None = None
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serializa para dicionário."""
        result = asdict(self)
        result["status"] = self.status.value
        return result


class ContractError(Exception):
    """Erro relacionado a contratos."""
    pass


class ContractNotFoundError(ContractError):
    """Contrato não encontrado no registro."""
    pass


class ContractVerificationError(ContractError):
    """Falha na verificação de aderência ao contrato."""
    pass


class ContractRegistry:
    """Registro central de contratos entre módulos.

    Características:
    - Registro de contratos com metadados
    - Consulta por nome ou tipo
    - Verificação de aderência (todas as implementações)
    - Snapshot serializável para auditoria
    - Exportação de grafo de dependências entre contratos
    """

    def __init__(self):
        self._contracts: dict[str, ContractEntry] = {}

    def register(self, entry: ContractEntry) -> None:
        """Registra um contrato no registry.

        Args:
            entry: Contrato a ser registrado

        Raises:
            ContractError: Se o nome do contrato já existir
        """
        if entry.name in self._contracts:
            raise ContractError(
                f"Contrato '{entry.name}' já registrado. "
                f"Use update() para atualizar."
            )
        self._contracts[entry.name] = entry

    def update(self, entry: ContractEntry) -> None:
        """Atualiza um contrato existente.

        Args:
            entry: Contrato com dados atualizados

        Raises:
            ContractNotFoundError: Se o contrato não existir
        """
        if entry.name not in self._contracts:
            raise ContractNotFoundError(f"Contrato '{entry.name}' não encontrado.")
        self._contracts[entry.name] = entry

    def get(self, name: str) -> ContractEntry:
        """Recupera um contrato por nome.

        Args:
            name: Nome do contrato

        Returns:
            ContractEntry correspondente

        Raises:
            ContractNotFoundError: Se não encontrado
        """
        if name not in self._contracts:
            raise ContractNotFoundError(f"Contrato '{name}' não encontrado.")
        return self._contracts[name]

    def get_by_interface(self, interface_type: str) -> list[ContractEntry]:
        """Recupera contratos por nome do tipo da interface.

        Args:
            interface_type: Nome da classe ABC/Protocol

        Returns:
            Lista de contratos que usam essa interface
        """
        return [
            c for c in self._contracts.values()
            if c.interface_type == interface_type
        ]

    def implementations_of(self, interface_name: str) -> list[str]:
        """Lista implementações registradas para um contrato.

        Args:
            interface_name: Nome do contrato/interface

        Returns:
            Lista de caminhos de módulos implementadores
        """
        try:
            contract = self.get(interface_name)
            return contract.implementations.copy()
        except ContractNotFoundError:
            return []

    def add_implementation(self, contract_name: str, impl_path: str) -> None:
        """Adiciona uma implementação a um contrato existente.

        Args:
            contract_name: Nome do contrato
            impl_path: Caminho do módulo implementador
        """
        contract = self.get(contract_name)
        if impl_path not in contract.implementations:
            contract.implementations.append(impl_path)

    def all_contracts(self) -> list[ContractEntry]:
        """Retorna todos os contratos registrados."""
        return list(self._contracts.values())

    def count(self) -> int:
        """Número de contratos registrados."""
        return len(self._contracts)

    def verify_all(self) -> dict[str, bool]:
        """Verifica aderência de todos os contratos.

        Uma verificação básica confirma que:
        - O contrato tem um nome
        - A interface_type está preenchida
        - O module_path existe
        - Implementações foram registradas

        Returns:
            Dict mapeando nome do contrato → status de verificação
        """
        results: dict[str, bool] = {}
        for name, contract in self._contracts.items():
            checks = [
                bool(contract.name),
                bool(contract.interface_type),
                bool(contract.module_path),
                len(contract.implementations) > 0,
            ]
            results[name] = all(checks)
        return results

    def snapshot(self) -> dict[str, Any]:
        """Serializa todo o registro para dicionário (audit trail).

        Returns:
            Dict completo com todos os contratos e metadados
        """
        return {
            "registry_version": "1.0.0",
            "total_contracts": self.count(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "contracts": {
                name: entry.to_dict()
                for name, entry in self._contracts.items()
            },
        }

    def export_graph(self) -> dict[str, Any]:
        """Exporta grafo de dependências entre contratos.

        Returns:
            Dict no formato {nodes: [...], edges: [...]}
            compatível com SPEC-093 (DependencyGraph).
        """
        nodes = []
        edges = []
        for name, entry in self._contracts.items():
            nodes.append({
                "id": f"contract:{name}",
                "label": name,
                "type": "contract",
                "module": entry.module_path,
                "status": entry.status.value,
            })
            for impl in entry.implementations:
                impl_id = f"impl:{impl}"
                nodes.append({
                    "id": impl_id,
                    "label": impl.rsplit("/", 1)[-1],
                    "type": "implementation",
                    "module": impl,
                })
                edges.append({
                    "source": impl_id,
                    "target": f"contract:{name}",
                    "type": "implements",
                })
        return {"nodes": nodes, "edges": edges}

    def to_json(self, indent: int = 2) -> str:
        """Serializa o snapshot para JSON."""
        return json.dumps(self.snapshot(), indent=indent, ensure_ascii=False)
