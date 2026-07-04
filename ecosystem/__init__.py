"""
ecosystem — Canonical Entrypoint do OpenCode Ecosystem.

Ponto de entrada único, centralizado e auditável para todo o ecossistema.
Gerencia contratos entre módulos, schemas de estado e grafo de dependências.
"""

__version__ = "7.2.0"
__ecosystem_version__ = "R46"
__schema_version__ = "1.0.0"

from ecosystem.contracts.registry import ContractRegistry, ContractEntry
from ecosystem.schemas.registry import SchemaRegistry
from ecosystem.deps.analyzer import DependencyAnalyzer

# Singleton do registro de contratos
contract_registry = ContractRegistry()

# Singleton do registro de schemas
schema_registry = SchemaRegistry()

# Singleton do analisador de dependências
dependency_analyzer = DependencyAnalyzer()


def get_version() -> str:
    """Retorna a versão completa do ecossistema."""
    return f"{__version__} (ciclo {__ecosystem_version__})"


__all__ = [
    "contract_registry",
    "schema_registry",
    "dependency_analyzer",
    "ContractRegistry",
    "ContractEntry",
    "SchemaRegistry",
    "DependencyAnalyzer",
    "get_version",
]
