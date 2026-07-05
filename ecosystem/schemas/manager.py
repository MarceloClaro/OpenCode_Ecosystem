"""
SchemaAwareStateManager — Wrapper que valida/migra dados usando SchemaRegistry.

Implementa o padrão descrito na SPEC-092: todo dado escrito passa por
validação contra o schema registrado, e todo dado lido passa por migração
automática para a versão mais recente do schema.
"""

from __future__ import annotations

from typing import Any, Protocol


class IStateBackend(Protocol):
    """Protocolo mínimo para backend de estado usado pelo SchemaAwareManager."""

    def get(self, key: str) -> str | None: ...

    def set(self, key: str, value: str) -> None: ...

    def delete(self, key: str) -> bool: ...

    def keys(self) -> list[str]: ...

    def exists(self, key: str) -> bool: ...

    def close(self) -> None: ...


class SchemaAwareStateManager:
    """Wrapper que adiciona validação de schema a um backend de estado.

    Attributes:
        backend: Backend de estado subjacente (deve implementar IStateBackend).
        schema_registry: SchemaRegistry usado para validação e migração.
        default_schema: Nome do schema padrão para dados sem schema explícito.
    """

    def __init__(
        self,
        backend: IStateBackend,
        schema_registry: object,
        default_schema: str | None = None,
    ) -> None:
        self._backend = backend
        self._schema_registry = schema_registry
        self.default_schema = default_schema

    @property
    def backend(self) -> IStateBackend:
        """Retorna o backend de estado subjacente."""
        return self._backend

    @property
    def schema_registry(self) -> object:
        """Retorna o SchemaRegistry."""
        return self._schema_registry

    def set(self, key: str, value: dict[str, Any], schema_name: str | None = None) -> None:
        """Armazena valor validando contra schema.

        Args:
            key: Chave do dado.
            value: Dicionário com dados.
            schema_name: Nome do schema (usa default_schema se None).

        Raises:
            SchemaValidationError: Se o valor não passar na validação.
        """
        schema = schema_name or self.default_schema
        if schema and hasattr(self._schema_registry, "validate"):
            self._schema_registry.validate(schema, value)
        import json
        self._backend.set(key, json.dumps(value))

    def get(self, key: str, schema_name: str | None = None) -> dict[str, Any] | None:
        """Recupera valor aplicando migração automática.

        Args:
            key: Chave do dado.
            schema_name: Nome do schema (usa default_schema se None).

        Returns:
            Dicionário com dados migrados, ou None se a chave não existir.
        """
        raw = self._backend.get(key)
        if raw is None:
            return None
        try:
            import json
            value = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

        schema = schema_name or self.default_schema
        if schema and hasattr(self._schema_registry, "migrate"):
            try:
                value = self._schema_registry.migrate(schema, value)
            except Exception:
                # Se a migração falhar, retorna o dado bruto
                pass
        return value
