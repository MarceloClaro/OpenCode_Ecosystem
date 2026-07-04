"""
Schema Registry — Versionamento e validação de schemas de estado.

Fornece:
- SchemaRegistry: registro central de schemas JSON
- SchemaAwareStateManager: wrapper com validação automática
- Versionamento semântico (MAJOR.MINOR.PATCH)
- Migração automática entre versões
"""

from ecosystem.schemas.registry import SchemaRegistry, SchemaValidationError
from ecosystem.schemas.versions import SemanticVersion

__all__ = [
    "SchemaRegistry",
    "SchemaValidationError",
    "SemanticVersion",
]
