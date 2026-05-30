"""
Testes do SQLiteStateManager (core/state.py)

Cobre:
- get / set / delete / exists / keys
- get com default
- Unicode e tipos complexos (dict, list, int, bool, None)
- transaction() context manager
- import_json / export_json
- get_updated_at
- close / reopen (thread-local connections)
"""

import json
import tempfile
from pathlib import Path

import pytest

from core.state import SQLiteStateManager


@pytest.fixture
def db_path():
    """Cria um arquivo temporario unico para cada teste."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        path = Path(f.name)
    yield path
    # Cleanup
    try:
        path.unlink(missing_ok=True)
        wal = path.with_suffix('.db-wal')
        shm = path.with_suffix('.db-shm')
        wal.unlink(missing_ok=True)
        shm.unlink(missing_ok=True)
    except OSError:
        pass


@pytest.fixture
def sm(db_path):
    """StateManager limpo para cada teste."""
    mgr = SQLiteStateManager(db_path)
    yield mgr
    mgr.close()


# ─── CRUD Básico ─────────────────────────────────────────────────────

class TestBasicCRUD:
    def test_set_and_get(self, sm):
        sm.set('name', 'Marcelo')
        assert sm.get('name') == 'Marcelo'

    def test_get_nonexistent_returns_default(self, sm):
        assert sm.get('ghost') is None
        assert sm.get('ghost', 42) == 42

    def test_get_nonexistent_no_default(self, sm):
        assert sm.get('ghost') is None

    def test_overwrite_existing(self, sm):
        sm.set('key', 'primeiro')
        sm.set('key', 'segundo')
        assert sm.get('key') == 'segundo'

    def test_delete_existing(self, sm):
        sm.set('x', 100)
        assert sm.delete('x') is True
        assert sm.get('x') is None

    def test_delete_nonexistent(self, sm):
        assert sm.delete('phantom') is False

    def test_exists_true(self, sm):
        sm.set('present', True)
        assert sm.exists('present') is True

    def test_exists_false(self, sm):
        assert sm.exists('absent') is False

    def test_keys_empty(self, sm):
        assert sm.keys() == []

    def test_keys_multiple(self, sm):
        sm.set('a', 1)
        sm.set('b', 2)
        sm.set('c', 3)
        assert sm.keys() == ['a', 'b', 'c']

    def test_keys_after_delete(self, sm):
        sm.set('a', 1)
        sm.set('b', 2)
        sm.delete('a')
        assert sm.keys() == ['b']


# ─── Tipos de Dados ──────────────────────────────────────────────────

class TestDataTypes:
    def test_store_dict(self, sm):
        data = {'user': 'marce', 'role': 'admin', 'tags': [1, 2, 3]}
        sm.set('user:profile', data)
        assert sm.get('user:profile') == data

    def test_store_list(self, sm):
        sm.set('items', [1, 'dois', 3.0, True])
        assert sm.get('items') == [1, 'dois', 3.0, True]

    def test_store_integer(self, sm):
        sm.set('count', 42)
        assert sm.get('count') == 42

    def test_store_boolean(self, sm):
        sm.set('flag', True)
        assert sm.get('flag') is True

    def test_store_none(self, sm):
        sm.set('nothing', None)
        assert sm.get('nothing') is None

    def test_store_unicode(self, sm):
        sm.set('emoji', '🔥 🐍 🚀')
        result = sm.get('emoji')
        assert result == '🔥 🐍 🚀'

    def test_nested_dict(self, sm):
        data = {'level1': {'level2': {'level3': 'deep'}}}
        sm.set('nested', data)
        assert sm.get('nested') == data


# ─── Transaction ─────────────────────────────────────────────────────

class TestTransaction:
    def test_transaction_modify(self, sm):
        sm.set('cart', {'items': [], 'total': 0})
        with sm.transaction('cart') as cart:
            cart['items'].append('item1')
            cart['total'] += 10
        result = sm.get('cart')
        assert result['items'] == ['item1']
        assert result['total'] == 10

    def test_transaction_persists_on_exit(self, sm):
        """Ao sair do bloco with, o dado modificado deve persistir."""
        sm.set('config', {'theme': 'dark', 'zoom': 1})
        with sm.transaction('config') as cfg:
            cfg['zoom'] = 2
        assert sm.get('config') == {'theme': 'dark', 'zoom': 2}

    def test_transaction_new_key_creates_empty(self, sm):
        """Transacao em chave inexistente cria dict vazio."""
        with sm.transaction('new') as data:
            data['x'] = 1
        assert sm.get('new') == {'x': 1}


# ─── Import / Export ─────────────────────────────────────────────────

class TestImportExport:
    def test_import_json_file(self, sm, tmp_path):
        json_file = tmp_path / 'test.json'
        json_file.write_text(json.dumps({'hello': 'world'}), encoding='utf-8')
        assert sm.import_json(json_file, 'imported') is True
        assert sm.get('imported') == {'hello': 'world'}

    def test_import_json_nonexistent(self, sm):
        fake = Path('/nonexistent/file.json')
        assert sm.import_json(fake) is False

    def test_export_json(self, sm, tmp_path):
        sm.set('export_key', {'data': 123})
        out = tmp_path / 'exported.json'
        assert sm.export_json('export_key', out) is True
        content = json.loads(out.read_text(encoding='utf-8'))
        assert content == {'data': 123}

    def test_export_nonexistent(self, sm, tmp_path):
        out = tmp_path / 'ghost.json'
        assert sm.export_json('ghost', out) is False

    def test_import_json_gz(self, sm, tmp_path):
        import gzip
        gz_file = tmp_path / 'test.json.gz'
        with gzip.open(gz_file, 'wt', encoding='utf-8') as f:
            json.dump({'gz': True}, f)
        assert sm.import_json(gz_file, 'gzipped') is True
        assert sm.get('gzipped') == {'gz': True}


# ─── Timestamps ──────────────────────────────────────────────────────

class TestTimestamps:
    def test_get_updated_at_exists(self, sm):
        sm.set('ts', 'value')
        ts = sm.get_updated_at('ts')
        assert ts is not None
        assert isinstance(ts, str)
        assert 'T' in ts or '-' in ts  # datetime ISO-like

    def test_get_updated_at_nonexistent(self, sm):
        assert sm.get_updated_at('no_such_key') is None


# ─── Conexao / Cleanup ──────────────────────────────────────────────

class TestConnection:
    def test_close_and_reopen(self, sm, db_path):
        """Fechar e reabrir deve manter dados."""
        sm.set('persist', 'value')
        sm.close()

        sm2 = SQLiteStateManager(db_path)
        assert sm2.get('persist') == 'value'
        sm2.close()

    def test_close_twice_no_error(self, sm):
        sm.close()
        sm.close()  # nao deve levantar excecao

    def test_multiple_managers_same_db(self, db_path):
        """Dois managers no mesmo banco devem ver os mesmos dados."""
        sm1 = SQLiteStateManager(db_path)
        sm2 = SQLiteStateManager(db_path)
        sm1.set('shared', 'visible')
        assert sm2.get('shared') == 'visible'
        sm1.close()
        sm2.close()
