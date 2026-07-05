"""
ecosystem — Canonical Entrypoint do OpenCode Ecosystem.

Ponto de entrada único, centralizado e auditável para todo o ecossistema.
Gerencia contratos entre módulos, schemas de estado e grafo de dependências.

Uso:
    >>> from ecosystem import contract_registry, schema_registry, get_version
    >>> get_version()
    '7.2.0 (ciclo R46)'

Nota técnica:
    Usa __getattr__ de módulo (PEP 562) para lazy imports verdadeiros.
    Nenhum submodulo é importado até que o atributo seja acessado.
"""

from __future__ import annotations

import typing as _t

__version__ = "7.2.0"
__ecosystem_version__ = "R46"
__schema_version__ = "1.0.0"


def get_version() -> str:
    """Retorna a versão completa do ecossistema."""
    return f"{__version__} (ciclo {__ecosystem_version__})"


# ── Lazy module-level attributes (PEP 562) ──────────────────────────
# Só importa os módulos pesados quando o atributo é lido.

def __getattr__(name: str) -> _t.Any:
    """Carrega singletons sob demanda via __getattr__ de módulo.

    Evita importação em cascata na inicialização do pacote.
    """
    if name == "contract_registry":
        from ecosystem.contracts.registry import ContractRegistry
        val: _t.Any = ContractRegistry()
        globals()["contract_registry"] = val  # cache
        return val

    if name == "schema_registry":
        from ecosystem.schemas.registry import SchemaRegistry
        val = SchemaRegistry()
        globals()["schema_registry"] = val
        return val

    if name == "dependency_analyzer":
        from ecosystem.deps.analyzer import DependencyAnalyzer
        val = DependencyAnalyzer()
        globals()["dependency_analyzer"] = val
        return val

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Retorna atributos públicos do módulo."""
    return [
        "contract_registry",
        "schema_registry",
        "dependency_analyzer",
        "get_version",
        "__version__",
        "__ecosystem_version__",
        "__schema_version__",
    ]


__all__ = [
    "contract_registry",
    "schema_registry",
    "dependency_analyzer",
    "get_version",
]
