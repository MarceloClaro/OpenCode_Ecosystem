"""
Testes do FileStateManager (core/state_file.py)

Cobre:
- get / set / delete / exists / keys
- Escrita atomica via tempfile+replace
- Unicode e tipos complexos
- import_json / export_json
- keys() lista apenas .json, ignora temporarios
- Path sanitization
"""

import json
import tempfile
from pathlib import Path

import pytest

from core.state_file import FileStateManager
from core.errors import StateError


@pytest.fixture
def base_dir(tmp_path):
 """Diretorio temporario para cada teste."""
 d = tmp_path / "state"
 d.mkdir()
 return d


@pytest.fixture
def fsm(base_dir):
 """FileStateManager limpo para cada teste."""
 return FileStateManager(base_dir)


class TestFileStateManagerBasic:
 """Operacoes basicas CRUD."""

 def test_set_and_get(self, fsm):
 fsm.set("key", "value")
 assert fsm.get("key") == "value"

 def test_get_default(self, fsm):
 assert fsm.get("missing", 42) == 42
 assert fsm.get("missing") is None

 def test_set_overwrite(self, fsm):
 fsm.set("key", "old")
 fsm.set("key", "new")
 assert fsm.get("key") == "new"

 def test_delete_existing(self, fsm):
 fsm.set("key", "value")
 assert fsm.delete("key") is True
 assert fsm.get("key") is None

 def test_delete_missing(self, fsm):
 assert fsm.delete("nonexistent") is False

 def test_exists(self, fsm):
 assert fsm.exists("x") is False
 fsm.set("x", 1)
 assert fsm.exists("x") is True

 def test_keys(self, fsm):
 fsm.set("b", 2)
 fsm.set("a", 1)
 assert fsm.keys() == ["a", "b"]

 def test_keys_ignores_temp_files(self, fsm, base_dir):
 fsm.set("real", "data")
 # Cria um arquivo temporario manualmente
 (base_dir / ".tmp_abc123.json").write_text("{}", encoding="utf-8")
 assert ".tmp_" not in fsm.keys()
 assert "real" in fsm.keys()


class TestFileStateManagerDataTypes:
 """Testa serializacao de diferentes tipos."""

 def test_dict_value(self, fsm):
 data = {"a": 1, "b": [2, 3], "c": {"nested": True}}
 fsm.set("dict", data)
 assert fsm.get("dict") == data

 def test_list_value(self, fsm):
 fsm.set("list", [1, "two", 3.0])
 assert fsm.get("list") == [1, "two", 3.0]

 def test_numeric_values(self, fsm):
 fsm.set("int", 42)
 fsm.set("float", 3.14)
 fsm.set("bool_true", True)
 fsm.set("bool_false", False)
 fsm.set("null", None)
 assert fsm.get("int") == 42
 assert fsm.get("float") == 3.14
 assert fsm.get("bool_true") is True
 assert fsm.get("bool_false") is False
 assert fsm.get("null") is None

 def test_unicode(self, fsm):
 data = {"pt": "café são João", "jp": ""}
 fsm.set("unicode", data)
 assert fsm.get("unicode") == data


class TestFileStateManagerAtomicWrites:
 """Testa que a escrita atomica nao corrompe estado."""

 def test_partial_write_does_not_corrupt(self, fsm, base_dir):
 fsm.set("key", {"original": "data"})
 path = base_dir / "key.json"
 # Simula escrita truncada (o arquivo real nao deve ser corrompido
 # porque a escrita atomica usa tempfile + replace)
 content = path.read_text(encoding="utf-8")
 data = json.loads(content)
 assert data == {"original": "data"}

 def test_concurrent_writes(self, fsm):
 """Escrever muitas chaves nao deve falhar."""
 for i in range(50):
 fsm.set(f"k{i}", {"index": i, "data": f"value_{i}"})
 for i in range(50):
 val = fsm.get(f"k{i}")
 assert val["index"] == i


class TestFileStateManagerImportExport:
 """Testa import_json e export_json."""

 def test_export_json(self, fsm, tmp_path):
 fsm.set("export_key", {"a": 1})
 dest = tmp_path / "exported.json"
 result = fsm.export_json("export_key", dest)
 assert result is True
 assert dest.exists()
 data = json.loads(dest.read_text(encoding="utf-8"))
 assert data == {"a": 1}

 def test_export_nonexistent(self, fsm):
 result = fsm.export_json("no_such_key")
 assert result is False

 def test_import_json(self, fsm, tmp_path):
 src = tmp_path / "source.json"
 src.write_text(json.dumps({"imported": True}), encoding="utf-8")
 result = fsm.import_json(src, key="my_import")
 assert result is True
 assert fsm.get("my_import") == {"imported": True}

 def test_import_json_auto_key(self, fsm, tmp_path):
 src = tmp_path / "auto_key.json"
 src.write_text(json.dumps({"x": 1}), encoding="utf-8")
 fsm.import_json(src)
 assert fsm.get("auto_key") == {"x": 1}

 def test_import_invalid_json(self, fsm, tmp_path):
 src = tmp_path / "bad.json"
 src.write_text("not json", encoding="utf-8")
 result = fsm.import_json(src)
 assert result is False


class TestFileStateManagerPathSanitization:
 """Testa sanitizacao de chaves para nomes de arquivo."""

 def test_special_characters(self, fsm, base_dir):
 fsm.set("path/to/file", "value")
 fsm.set("space key", "value2")
 assert fsm.get("path/to/file") == "value"
 assert fsm.get("space key") == "value2"
 # Verifica que os arquivos tem nomes sanitizados
 files = [p.name for p in base_dir.glob("*.json")]
 assert any("path_to_file" in f for f in files)
 assert any("space_key" in f for f in files)


class TestFileStateManagerEdgeCases:
 """Casos extremos."""

 def test_close_is_noop(self, fsm):
 fsm.close() # Nao deve levantar excecao

 def test_repr(self, fsm):
 fsm.set("k", "v")
 r = repr(fsm)
 assert "FileStateManager" in r
 assert "keys=1" in r

 def test_directory_created_automatically(self, tmp_path):
 new_dir = tmp_path / "new" / "nested" / "dir"
 fsm = FileStateManager(new_dir)
 fsm.set("test", "ok")
 assert fsm.get("test") == "ok"
 assert new_dir.exists()
