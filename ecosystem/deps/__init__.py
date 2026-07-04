"""
Dependency Graph — Análise e validação do grafo de dependências do ecossistema.

Fornece:
- DependencyAnalyzer: análise estática de dependências via AST
- DependencyGraph: grafo canônico com nós e arestas
- Validação contra regras de camada
- Detecção de circulares e duplicatas
"""

from ecosystem.deps.analyzer import (
    DependencyAnalyzer,
    Dependency,
    Violation,
    DependencyGraph,
)

__all__ = [
    "DependencyAnalyzer",
    "Dependency",
    "Violation",
    "DependencyGraph",
]
