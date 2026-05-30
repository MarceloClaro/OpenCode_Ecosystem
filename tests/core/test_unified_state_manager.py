"""
Testes do UnifiedStateManager (core/state_manager.py)

Cobre:
- Inicializacao com db_path e file_base_dir
- Roteamento: chaves com prefixo file: -> FileStateManager
- Roteamento: chaves sem prefixo -> SQLiteStateManager
- get / set / delete / exists / keys (ambos backends)
- Singleton get_state_manager()
- reset_state_manager()
- Acesso direto aos backends (.sqlite, .file)
"""

import tempfile
from pathlib import Path

import pytest

from core.state_manager import UnifiedStateManager, get_state_manager, reset_state_manager


@pytest.fixture
def usm(tmp_path):
    """UnifiedStateManager com diretorios temporarios."""
    db = tmp_path / "test.db"
    file_dir = tmp_path / "file_state"
    return UnifiedStateManager(db_path=db, file_base_dir=file_dir)


class TestUnifiedStateManagerRouting:
    """Testa roteamento entre backends SQLite e File."""

    def test_sqlite_by_default(self, usm):
        usm.set("normal_key", "sqlite_value")
        assert usm.get("normal_key") == "sqlite_value"
        # Deve existir no SQLite
        assert usm.sqlite.exists("normal_key")

    def test_file_with_prefix(self, usm):
        usm.set("file:my_file", "file_value")
        assert usm.get("file:my_file") == "file_value"
        # Deve existir no FileStateManager (sem prefixo)
        assert usm.file.exists("my_file")

    def test_file_key_overlap(self, usm):
        """Chaves com mesmo nome em backends diferentes nao conflitam."""
        usm.set("shared", "sqlite")
        usm.set("file:shared", "file")
        assert usm.get("shared") == "sqlite"
        assert usm.get("file:shared") == "file"

    def test_delete_sqlite(self, usm):
        usm.set("k", "v")
        assert usm.delete("k") is True
        assert usm.get("k") is None

    def test_delete_file(self, usm):
        usm.set("file:k", "v")
        assert usm.delete("file:k") is True
        assert usm.get("file:k") is None

    def test_exists_both_backends(self, usm):
        assert usm.exists("x") is False
        assert usm.exists("file:x") is False
        usm.set("x", 1)
        usm.set("file:x", 2)
        assert usm.exists("x") is True
        assert usm.exists("file:x") is True

    def test_keys_from_both(self, usm):
        usm.set("a", 1)
        usm.set("b", 2)
        usm.set("file:c", 3)
        keys = usm.keys()
        assert "a" in keys
        assert "b" in keys
        assert "file:c" in keys

    def test_get_default(self, usm):
        assert usm.get("no_such", 42) == 42
        assert usm.get("file:no_such", "default") == "default"

    def test_complex_types(self, usm):
        data = {"nested": {"list": [1, 2, 3], "bool": True, "null": None}}
        usm.set("complex", data)
        assert usm.get("complex") == data

        file_data = [1, "two", 3.0]
        usm.set("file:complex_list", file_data)
        assert usm.get("file:complex_list") == file_data


class TestUnifiedStateManagerSingleton:
    """Testa o singleton global."""

    def test_get_state_manager(self):
        reset_state_manager()
        sm = get_state_manager()
        assert isinstance(sm, UnifiedStateManager)
        # Mesma instancia na segunda chamada
        sm2 = get_state_manager()
        assert sm is sm2

    def test_reset(self):
        reset_state_manager()
        sm1 = get_state_manager()
        reset_state_manager()
        sm2 = get_state_manager()
        assert sm1 is not sm2  # Instancia nova apos reset

    def test_singleton_with_params(self):
        reset_state_manager()
        sm = get_state_manager()
        sm.set("test", "ok")
        assert sm.get("test") == "ok"
        reset_state_manager()


class TestUnifiedStateManagerAccessors:
    """Testa acesso direto aos backends."""

    def test_sqlite_property(self, usm):
        assert usm.sqlite is not None
        usm.sqlite.set("direct", "value")
        assert usm.sqlite.get("direct") == "value"

    def test_file_property(self, usm):
        assert usm.file is not None
        usm.file.set("direct", "value")
        assert usm.file.get("direct") == "value"

    def test_close(self, usm):
        usm.close()  # Nao deve crashar

    def test_repr(self, usm):
        r = repr(usm)
        assert "UnifiedStateManager" in r


class TestUnifiedStateManagerEdgeCases:
    """Casos extremos."""

    def test_empty_keys(self, usm):
        assert usm.keys() == []

    def test_delete_nonexistent(self, usm):
        assert usm.delete("no_such_key") is False
        assert usm.delete("file:no_such_key") is False

    def test_file_prefix_only(self, usm):
        """Apenas 'file:' como prefixo (nao 'File:' ou 'FILE:')."""
        usm.set("File:test", "normal")  # Sem prefixo reconhecido -> SQLite
        # Deve ir para SQLite (case sensitive)
        assert usm.sqlite.exists("File:test") or usm._resolve("File:test") is usm._sqlite
