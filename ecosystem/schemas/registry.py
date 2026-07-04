"""
Schema Registry — Registro central de schemas JSON para validação de estado.

Gerencia:
- Registro de schemas JSON Schema
- Validação de dados contra schema
- Versionamento e migração automática
- Audit trail de mudanças
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ecosystem.schemas.versions import SemanticVersion


class SchemaValidationError(Exception):
    """Erro de validação de schema."""
    pass


class SchemaNotFoundError(Exception):
    """Schema não encontrado no registro."""
    pass


class SchemaEntry:
    """Entrada de schema no registro.

    Attributes:
        name: Nome do schema
        schema_data: Dict do JSON Schema
        version: Versão semântica atual
        description: Descrição do schema
        migration_fn: Função de migração entre versões (opcional)
    """

    def __init__(
        self,
        name: str,
        schema_data: dict[str, Any],
        version: str = "1.0.0",
        description: str = "",
        migration_fn: callable | None = None,
    ):
        self.name = name
        self.schema_data = schema_data
        self.version = SemanticVersion.parse(version)
        self.description = description
        self._migration_fn = migration_fn

    def validate(self, data: dict[str, Any]) -> bool:
        """Valida dados contra o schema.

        Args:
            data: Dados a validar

        Returns:
            True se válido

        Raises:
            SchemaValidationError: Se dados não conformam ao schema
        """
        errors = self._validate_internal(data)
        if errors:
            raise SchemaValidationError(
                f"Schema '{self.name}' v{self.version}: {len(errors)} erro(s):\n"
                + "\n".join(f"  - {e}" for e in errors)
            )
        return True

    def _validate_internal(self, data: dict[str, Any]) -> list[str]:
        """Validação interna sem exceção.

        Implementa validação básica de required fields e tipos.
        Para validação completa, usar biblioteca como `jsonschema`.
        """
        errors: list[str] = []
        props = self.schema_data.get("properties", {})
        required = self.schema_data.get("required", [])

        # Valida campos obrigatórios
        for field in required:
            if field not in data:
                errors.append(f"Campo obrigatório '{field}' ausente")

        # Valida tipos básicos
        for field, value in data.items():
            if field in props:
                expected_type = props[field].get("type")
                if expected_type and value is not None:
                    self._check_type(field, value, expected_type, errors)

        return errors

    def _check_type(
        self, field: str, value: Any, expected_type: str, errors: list[str]
    ) -> None:
        """Verifica tipo de um campo."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "object": dict,
            "array": list,
        }
        py_type = type_map.get(expected_type)
        if py_type and not isinstance(value, py_type):
            errors.append(
                f"Campo '{field}': esperado {expected_type}, "
                f"recebido {type(value).__name__}"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serializa entrada para dict."""
        return {
            "name": self.name,
            "version": str(self.version),
            "description": self.description,
            "required_fields": self.schema_data.get("required", []),
            "property_count": len(self.schema_data.get("properties", {})),
        }


class SchemaRegistry:
    """Registro central de schemas para artefatos de estado.

    Gerencia:
    - Schemas JSON para cada artefato de estado
    - Validação automática na leitura/escrita
    - Migração entre versões de schema
    - Audit trail de operações
    """

    def __init__(self):
        self._schemas: dict[str, SchemaEntry] = {}
        self._audit_trail: list[dict[str, Any]] = []

    def register(self, entry: SchemaEntry) -> None:
        """Registra um schema no registry.

        Args:
            entry: SchemaEntry a registrar

        Raises:
            ValueError: Se nome já registrado
        """
        if entry.name in self._schemas:
            raise ValueError(f"Schema '{entry.name}' já registrado.")
        self._schemas[entry.name] = entry

    def get(self, name: str) -> SchemaEntry:
        """Recupera um schema por nome.

        Args:
            name: Nome do schema

        Returns:
            SchemaEntry

        Raises:
            SchemaNotFoundError: Se não encontrado
        """
        if name not in self._schemas:
            raise SchemaNotFoundError(f"Schema '{name}' não encontrado.")
        return self._schemas[name]

    def validate(self, name: str, data: dict[str, Any]) -> bool:
        """Valida dados contra um schema registrado.

        Args:
            name: Nome do schema
            data: Dados a validar

        Returns:
            True se válido
        """
        entry = self.get(name)
        return entry.validate(data)

    def current_version(self, name: str) -> str:
        """Versão atual de um schema."""
        entry = self.get(name)
        return str(entry.version)

    def migrate(self, name: str, data: dict[str, Any]) -> dict[str, Any]:
        """Executa migração de dados para a versão atual do schema.

        Args:
            name: Nome do schema
            data: Dados a migrar

        Returns:
            Dados migrados
        """
        entry = self.get(name)

        # Extrai versão atual dos dados
        data_version_str = data.get("__schema_version__", "0.0.0")
        try:
            data_version = SemanticVersion.parse(data_version_str)
        except ValueError:
            data_version = SemanticVersion(0, 0, 0)

        target_version = entry.version

        # Se já está na versão alvo, retorna
        if data_version == target_version:
            return data

        # Aplica migração se disponível
        if entry._migration_fn:
            migrated = entry._migration_fn(data, str(data_version), str(target_version))
        else:
            migrated = self._default_migrate(data, data_version, target_version, entry)

        # Atualiza versão
        migrated["__schema_version__"] = str(target_version)

        # Audit trail
        self._audit_trail.append({
            "schema": name,
            "from_version": str(data_version),
            "to_version": str(target_version),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return migrated

    def _default_migrate(
        self,
        data: dict[str, Any],
        from_ver: SemanticVersion,
        to_ver: SemanticVersion,
        entry: SchemaEntry,
    ) -> dict[str, Any]:
        """Migração padrão: adiciona campos obrigatórios faltantes."""
        result = dict(data)
        props = entry.schema_data.get("properties", {})
        required = entry.schema_data.get("required", [])

        for field in required:
            if field not in result:
                prop = props.get(field, {})
                default = prop.get("default")
                if default is not None:
                    result[field] = default
                elif prop.get("type") == "string":
                    result[field] = ""
                elif prop.get("type") == "integer":
                    result[field] = 0
                elif prop.get("type") == "array":
                    result[field] = []
                elif prop.get("type") == "object":
                    result[field] = {}

        return result

    def all_schemas(self) -> list[SchemaEntry]:
        """Retorna todos os schemas registrados."""
        return list(self._schemas.values())

    def count(self) -> int:
        """Número de schemas registrados."""
        return len(self._schemas)

    def get_audit_trail(self) -> list[dict[str, Any]]:
        """Retorna o audit trail de migrações."""
        return self._audit_trail.copy()

    def snapshot(self) -> dict[str, Any]:
        """Snapshot do registry para auditoria."""
        return {
            "registry_version": "1.0.0",
            "total_schemas": self.count(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "schemas": {
                name: entry.to_dict()
                for name, entry in self._schemas.items()
            },
        }

    def to_json(self, indent: int = 2) -> str:
        """Serializa snapshot para JSON."""
        return json.dumps(self.snapshot(), indent=indent, ensure_ascii=False)
