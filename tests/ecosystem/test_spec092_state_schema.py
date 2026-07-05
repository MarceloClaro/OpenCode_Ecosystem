"""
Testes TDD para SPEC-092: State Artifact Schema Versioning.

Valida:
- CT-9201: SchemaRegistry registra schema JSON
- CT-9202: Validação rejeita dados inválidos
- CT-9203: Dado válido passa pela validação
- CT-9204: Migração automática entre versões
- CT-9205: SchemaAwareStateManager.set() valida
- CT-9206: SchemaAwareStateManager.get() valida
- CT-9207: Versionamento semântico
- CT-9208: ecosystem-state.json schema válido
- CT-9209: Audit trail registra mudanças
- CT-9210: Migração batch
"""

import json
from pathlib import Path

import pytest
from ecosystem.schemas.registry import (
    SchemaRegistry,
    SchemaEntry,
    SchemaValidationError,
    SchemaNotFoundError,
)
from ecosystem.schemas.versions import SemanticVersion


# Schema de exemplo para testes
ECOSYSTEM_STATE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "EcosystemState",
    "type": "object",
    "required": ["version", "current_cycle", "last_updated"],
    "properties": {
        "version": {"type": "string"},
        "current_cycle": {"type": "string"},
        "last_updated": {"type": "string"},
        "tests_passing": {"type": "integer"},
        "total_cts": {"type": "integer"},
    },
}


@pytest.fixture
def registry():
    """Fixture: SchemaRegistry vazio."""
    return SchemaRegistry()


@pytest.fixture
def populated_registry(registry):
    """Fixture: SchemaRegistry com schema registrado."""
    registry.register(SchemaEntry(
        name="ecosystem_state",
        schema_data=ECOSYSTEM_STATE_SCHEMA,
        version="1.0.0",
        description="Schema do ecosystem-state.json",
    ))
    return registry


# === CT-9201: SchemaRegistry registra schema ===
class TestRegistration:
    def test_ct9201_register_schema(self, registry):
        """CT-9201: register() aceita schema JSON."""
        entry = SchemaEntry(
            name="test_schema",
            schema_data={"type": "object", "properties": {}},
        )
        registry.register(entry)
        assert registry.count() == 1

    def test_ct9201_register_duplicate_raises(self, registry):
        """CT-9201b: register() duplicado lança ValueError."""
        entry = SchemaEntry(
            name="dup", schema_data={"type": "object", "properties": {}}
        )
        registry.register(entry)
        with pytest.raises(ValueError):
            registry.register(entry)


# === CT-9202: Validação rejeita dados inválidos ===
class TestValidationFailure:
    def test_ct9202_rejects_missing_required(self, populated_registry):
        """CT-9202: Validação rejeita falta de campo obrigatório."""
        with pytest.raises(SchemaValidationError) as exc:
            populated_registry.validate("ecosystem_state", {"foo": "bar"})
        assert "Campo obrigatório" in str(exc.value)

    def test_ct9202_rejects_wrong_type(self, populated_registry):
        """CT-9202b: Validação rejeita tipo errado."""
        with pytest.raises(SchemaValidationError) as exc:
            populated_registry.validate(
                "ecosystem_state",
                {
                    "version": "1.0",
                    "current_cycle": "R46",
                    "last_updated": "now",
                    "tests_passing": "not_an_int",  # deve ser int
                },
            )
        assert "esperado" in str(exc.value)


# === CT-9203: Dado válido passa ===
class TestValidationSuccess:
    def test_ct9203_valid_data_passes(self, populated_registry):
        """CT-9203: Dado válido passa na validação."""
        result = populated_registry.validate(
            "ecosystem_state",
            {
                "version": "7.2.0",
                "current_cycle": "R46",
                "last_updated": "2026-07-04T20:00:00Z",
                "tests_passing": 420,
                "total_cts": 420,
            },
        )
        assert result is True


# === CT-9204: Migração automática ===
class TestMigration:
    def test_ct9204_migration_adds_missing_fields(self, populated_registry):
        """CT-9204: migrate() adiciona campos obrigatórios faltantes."""
        migrated = populated_registry.migrate(
            "ecosystem_state",
            {
                "version": "1.0",
                "current_cycle": "R46",
                # last_updated ausente
            },
        )
        assert "last_updated" in migrated  # adicionado
        assert migrated["__schema_version__"] == "1.0.0"

    def test_ct9204_no_migration_needed(self, populated_registry):
        """CT-9204b: Dados já na versão correta não são alterados."""
        data = {
            "version": "7.2.0",
            "current_cycle": "R46",
            "last_updated": "now",
            "__schema_version__": "1.0.0",
        }
        migrated = populated_registry.migrate("ecosystem_state", data)
        assert migrated["version"] == "7.2.0"


# === CT-9205: SchemaAwareStateManager.set() valida na escrita ===
class TestSchemaAwareManager:
    def test_ct9205_schema_aware_set_validates(self, populated_registry):
        """CT-9205: SchemaAwareStateManager.set() valida dados contra schema."""
        from ecosystem.schemas.manager import SchemaAwareStateManager
        from ecosystem.schemas.registry import SchemaValidationError

        # Mock de backend dict
        class DictBackend:
            def __init__(self):
                self._data: dict[str, str] = {}
            def get(self, key: str) -> str | None:
                return self._data.get(key)
            def set(self, key: str, value: str) -> None:
                self._data[key] = value
            def delete(self, key: str) -> bool:
                return self._data.pop(key, None) is not None
            def keys(self) -> list[str]:
                return list(self._data.keys())
            def exists(self, key: str) -> bool:
                return key in self._data
            def close(self) -> None:
                self._data.clear()

        backend = DictBackend()
        manager = SchemaAwareStateManager(backend, populated_registry, default_schema="ecosystem_state")

        # Dados válidos passam
        manager.set("test_key", {
            "version": "7.2.0",
            "current_cycle": "R46",
            "last_updated": "2026-07-04T20:00:00Z",
            "tests_passing": 420,
            "total_cts": 420,
        })
        assert backend.exists("test_key")

        # Dados inválidos são rejeitados
        with pytest.raises(SchemaValidationError):
            manager.set("invalid_key", {"foo": "bar"})

    def test_ct9205_registry_usable_by_manager(self, populated_registry):
        """CT-9205b: SchemaRegistry pode ser consumido pelo manager."""
        schema = populated_registry.get("ecosystem_state")
        assert schema.name == "ecosystem_state"
        assert str(schema.version) == "1.0.0"


# === CT-9206: SchemaAwareStateManager.get() migra na leitura ===
class TestSchemaAwareGet:
    def test_ct9206_schema_aware_get_migrates(self, populated_registry):
        """CT-9206: SchemaAwareStateManager.get() corrige dados corrompidos."""
        from ecosystem.schemas.manager import SchemaAwareStateManager

        class DictBackend:
            def __init__(self):
                self._data: dict[str, str] = {}
            def get(self, key: str) -> str | None:
                return self._data.get(key)
            def set(self, key: str, value: str) -> None:
                self._data[key] = value
            def delete(self, key: str) -> bool:
                return self._data.pop(key, None) is not None
            def keys(self) -> list[str]:
                return list(self._data.keys())
            def exists(self, key: str) -> bool:
                return key in self._data
            def close(self) -> None:
                self._data.clear()

        backend = DictBackend()
        manager = SchemaAwareStateManager(backend, populated_registry, default_schema="ecosystem_state")

        # Dados sem campo obrigatório last_updated
        import json
        backend.set("corrupted", json.dumps({
            "version": "1.0",
            "current_cycle": "R46",
            # last_updated ausente
        }))

        # get() deve migrar/adicionar campo faltante
        result = manager.get("corrupted")
        assert result is not None
        assert "last_updated" in result  # Campo adicionado pela migração

    def test_ct9206_get_returns_none_for_missing(self, populated_registry):
        """CT-9206b: get() retorna None para chave inexistente."""
        from ecosystem.schemas.manager import SchemaAwareStateManager

        class DictBackend:
            def __init__(self):
                self._data: dict[str, str] = {}
            def get(self, key: str) -> str | None:
                return self._data.get(key)
            def set(self, key: str, value: str) -> None:
                self._data[key] = value
            def delete(self, key: str) -> bool:
                return self._data.pop(key, None) is not None
            def keys(self) -> list[str]:
                return list(self._data.keys())
            def exists(self, key: str) -> bool:
                return key in self._data
            def close(self) -> None:
                self._data.clear()

        backend = DictBackend()
        manager = SchemaAwareStateManager(backend, populated_registry, default_schema="ecosystem_state")
        assert manager.get("chave_inexistente") is None


# === CT-9207: Versionamento semântico ===
class TestSemanticVersion:
    def test_ct9207_parse_valid(self):
        """CT-9207: parse() aceita versão válida."""
        v = SemanticVersion.parse("1.2.3")
        assert v.major == 1
        assert v.minor == 2
        assert v.patch == 3

    def test_ct9207_parse_invalid_raises(self):
        """CT-9207b: parse() rejeita versão inválida."""
        with pytest.raises(ValueError):
            SemanticVersion.parse("abc")

    def test_ct9207_bump_major(self):
        """CT-9207c: bump_major() incrementa corretamente."""
        v = SemanticVersion(1, 2, 3)
        bumped = v.bump_major()
        assert bumped.major == 2
        assert bumped.minor == 0
        assert bumped.patch == 0

    def test_ct9207_bump_minor(self):
        """CT-9207d: bump_minor() incrementa corretamente."""
        v = SemanticVersion(1, 2, 3)
        bumped = v.bump_minor()
        assert bumped.major == 1
        assert bumped.minor == 3
        assert bumped.patch == 0

    def test_ct9207_bump_patch(self):
        """CT-9207e: bump_patch() incrementa corretamente."""
        v = SemanticVersion(1, 2, 3)
        bumped = v.bump_patch()
        assert bumped.major == 1
        assert bumped.minor == 2
        assert bumped.patch == 4

    def test_ct9207_comparison(self):
        """CT-9207f: Comparação entre versões."""
        assert SemanticVersion(1, 0, 0) < SemanticVersion(2, 0, 0)
        assert SemanticVersion(1, 0, 0) == SemanticVersion(1, 0, 0)
        assert SemanticVersion(2, 0, 0) > SemanticVersion(1, 9, 9)


# === CT-9208: ecosystem-state.json schema ===
class TestEcosystemStateSchema:
    def test_ct9208_schema_is_valid(self):
        """CT-9208: Schema registrado é válido."""
        entry = SchemaEntry(
            name="ecosystem_state",
            schema_data=ECOSYSTEM_STATE_SCHEMA,
            version="1.0.0",
        )
        assert entry.schema_data["title"] == "EcosystemState"


# === CT-9209: Audit trail ===
class TestAuditTrail:
    def test_ct9209_audit_trail_records_migration(self, populated_registry):
        """CT-9209: Migração gera entrada no audit trail."""
        assert len(populated_registry.get_audit_trail()) == 0
        populated_registry.migrate(
            "ecosystem_state",
            {"version": "1.0"},
        )
        assert len(populated_registry.get_audit_trail()) >= 1
        record = populated_registry.get_audit_trail()[0]
        assert record["schema"] == "ecosystem_state"


# === CT-9210: Snapshot ===
class TestSnapshot:
    def test_ct9210_snapshot_contains_schemas(self, populated_registry):
        """CT-9210: snapshot() lista todos os schemas."""
        snap = populated_registry.snapshot()
        assert snap["total_schemas"] == 1
        assert "ecosystem_state" in snap["schemas"]
