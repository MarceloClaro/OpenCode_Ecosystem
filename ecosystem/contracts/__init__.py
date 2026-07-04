"""
Contract Registry — Registro central de contratos entre módulos do ecossistema.

Fornece:
- ContractRegistry: registro central com verificação de aderência
- ContractEntry: dataclass de metadados do contrato
- Interfaces formais (ABCs + Protocols) para todos os módulos
- Testes de contrato reutilizáveis
"""

from ecosystem.contracts.registry import ContractRegistry, ContractEntry

__all__ = [
    "ContractRegistry",
    "ContractEntry",
]
