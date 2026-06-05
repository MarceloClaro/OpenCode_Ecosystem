"""
Testes do PluginManager (core/plugin_manager.py)

Cobre:
- add_search_dir / discover
- load / load_all / unload
- get_plugin / list_plugins / get_plugin_names
- count / loaded_count
- Descoberta em diretorios e subdiretorios (pacotes)
- Plugin inexistente (NotFoundError)
- Import failing (PluginError)
"""

import tempfile
from pathlib import Path

import pytest

from core.plugin_manager import PluginManager, PluginMeta, PluginInstance
from core.errors import PluginError, NotFoundError


@pytest.fixture
def mgr():
    """PluginManager com auto_enable=False para testes."""
    return PluginManager(auto_enable=False)


@pytest.fixture
def plugin_dir(tmp_path):
    """Diretorio temporario com plugins de teste."""
    d = tmp_path / "plugins"
    d.mkdir()

    # Plugin valido
    (d / "hello_plugin.py").write_text(
        """
class HelloPlugin:
    name = "hello"

    async def on_load(self, config):
        self.loaded = True

    async def on_unload(self):
        self.unloaded = True

    async def execute_hook(self, hook, context):
        return f"{hook}:{context}"

plugin = HelloPlugin()
""",
        encoding="utf-8",
    )

    # Plugin com sintaxe invalida
    (d / "broken_plugin.py").write_text(
        "this is not valid python @@@",
        encoding="utf-8",
    )

    return d


class TestPluginManagerDiscovery:
    """Testa descoberta de plugins."""

    def test_discover_adds_search_dir(self, mgr, plugin_dir):
        mgr.add_search_dir(plugin_dir)
        assert len(mgr._search_dirs) == 1

    def test_discover_finds_plugins(self, mgr, plugin_dir):
        found = mgr.discover([plugin_dir])
        # Deve encontrar pelo menos hello_plugin
        assert "hello_plugin" in found

    def test_discover_ignores_private(self, mgr, plugin_dir):
        (plugin_dir / "_private.py").write_text("# private", encoding="utf-8")
        found = mgr.discover([plugin_dir])
        assert "_private" not in found

    def test_discover_empty_dir(self, mgr, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        found = mgr.discover([empty])
        assert found == []

    def test_discover_nonexistent_dir(self, mgr):
        mgr.add_search_dir("/nonexistent/path")
        found = mgr.discover()
        assert found == []


class TestPluginManagerLoading:
    """Testa carregamento de plugins."""

    def test_load_success(self, mgr, plugin_dir):
        mgr.discover([plugin_dir])
        result = mgr.load("hello_plugin")
        assert result is True
        plugin = mgr.get_plugin("hello_plugin")
        assert plugin is not None
        assert plugin.module is not None

    def test_load_nonexistent(self, mgr):
        with pytest.raises(NotFoundError, match="not found"):
            mgr.load("no-such-plugin")

    def test_load_broken_plugin(self, mgr, plugin_dir):
        mgr.discover([plugin_dir])
        with pytest.raises(PluginError, match="Failed to"):
            mgr.load("broken_plugin")

    def test_load_all(self, mgr, plugin_dir):
        mgr.discover([plugin_dir])
        count = mgr.load_all()
        # Pelo menos o hello_plugin deve carregar
        # O broken pode falhar, mas load_all continua
        assert count >= 1

    def test_unload(self, mgr, plugin_dir):
        mgr.discover([plugin_dir])
        mgr.load("hello_plugin")
        result = mgr.unload("hello_plugin")
        assert result is True
        plugin = mgr.get_plugin("hello_plugin")
        assert plugin.enabled is False

    def test_unload_nonexistent(self, mgr):
        assert mgr.unload("no-such") is False


class TestPluginManagerQueries:
    """Testa consultas ao PluginManager."""

    def test_get_plugin_nonexistent(self, mgr):
        assert mgr.get_plugin("no-such") is None

    def test_list_plugins(self, mgr, plugin_dir):
        mgr.discover([plugin_dir])
        plugins = mgr.list_plugins()
        assert len(plugins) >= 1

    def test_list_plugins_loaded_only(self, mgr, plugin_dir):
        mgr.discover([plugin_dir])
        # Nenhum carregado ainda
        loaded = mgr.list_plugins(loaded_only=True)
        assert loaded == []

    def test_get_plugin_names(self, mgr, plugin_dir):
        mgr.discover([plugin_dir])
        names = mgr.get_plugin_names()
        assert "hello_plugin" in names

    def test_count(self, mgr, plugin_dir):
        mgr.discover([plugin_dir])
        assert mgr.count >= 1

    def test_loaded_count(self, mgr, plugin_dir):
        mgr.discover([plugin_dir])
        assert mgr.loaded_count == 0
        mgr.load("hello_plugin")
        assert mgr.loaded_count == 1


class TestPluginManagerPackageDiscovery:
    """Testa descoberta de plugins como pacotes (com __init__.py)."""

    def test_discover_package(self, mgr, plugin_dir):
        pkg_dir = plugin_dir / "mypackage"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text(
            'name = "mypackage"\n',
            encoding="utf-8",
        )
        mgr.discover([plugin_dir])
        assert "mypackage" in mgr.get_plugin_names()


class TestPluginManagerEdgeCases:
    """Casos extremos."""

    def test_repr(self, mgr):
        r = repr(mgr)
        assert "PluginManager" in r
        assert "plugins=0" in r

    def test_add_search_dir_nonexistent(self, mgr):
        mgr.add_search_dir("/nonexistent")
        # Nao deve crashar, apenas nao adiciona
        assert len(mgr._search_dirs) == 0

    def test_add_search_dir_file(self, mgr, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        mgr.add_search_dir(f)  # Nao e diretorio
        assert len(mgr._search_dirs) == 0
