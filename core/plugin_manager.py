"""
core/plugin_manager.py — Gerenciamento de Plugins com DI.

Descoberta, carregamento, registro e ciclo de vida de plugins.
Suporta plugins Python (.py) instalados via pip ou locais.

Uso com DI (novo):
    container = Container.instance()
    mgr = PluginManager(container=container)
    mgr.discover(["plugins/"])
    mgr.load_all()
    plugin = mgr.get_plugin("meu-plugin")

Uso legado (compatível):
    mgr = PluginManager()
    mgr.discover(["plugins/"])
"""

from __future__ import annotations

import importlib
import inspect
import logging
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, Protocol

from core.errors import PluginError, NotFoundError

logger = logging.getLogger(__name__)


# ── Protocolo Base para Plugins ────────────────────────────────────


class Plugin(Protocol):
    """Protocolo que todos os plugins podem implementar."""

    name: str

    async def on_load(self, config: dict[str, Any]) -> None:
        """Chamado quando o plugin é carregado."""
        ...

    async def on_unload(self) -> None:
        """Chamado quando o plugin é descarregado."""
        ...

    async def execute_hook(self, hook: str, context: dict[str, Any]) -> Any:
        """Executa um hook específico."""
        ...


# ── Metadados ──────────────────────────────────────────────────────


@dataclass
class PluginMeta:
    """Metadados de um plugin."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    plugin_type: str = "python"  # "python" | "typescript"
    hooks: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)


@dataclass
class PluginInstance:
    """Instância carregada de um plugin."""
    meta: PluginMeta
    module: Any = None
    instance: Any = None
    loaded_at: float = field(default_factory=time.time)
    enabled: bool = True


# ── PluginManager ──────────────────────────────────────────────────


class PluginManager:
    """Gerenciador de plugins com descoberta automática e suporte a DI.

    Args:
        auto_enable: Se True, plugins são ativados automaticamente após load.
        container: Container DI opcional para resolução de dependências.
    """

    def __init__(self, auto_enable: bool = True, container: Any = None) -> None:
        self._plugins: dict[str, PluginInstance] = {}
        self._search_dirs: list[Path] = []
        self._auto_enable = auto_enable
        self._container = container

        # Auto-registro no Container DI
        if container is not None and not container.is_registered('plugin_manager'):
            container.register('plugin_manager', self)

    # ── Descoberta ─────────────────────────────────────────────────

    def add_search_dir(self, directory: str | Path) -> None:
        """Adiciona diretório para busca de plugins."""
        path = Path(directory)
        if path.exists() and path.is_dir():
            self._search_dirs.append(path.resolve())
            logger.debug("Added plugin search dir: %s", path)

    def discover(self, directories: Optional[list[str | Path]] = None) -> list[str]:
        """Descobre plugins disponíveis nos diretórios de busca.

        Args:
            directories: Lista opcional de diretórios (adiciona aos existentes).

        Returns:
            Lista de nomes de plugins encontrados.
        """
        if directories:
            for d in directories:
                self.add_search_dir(d)

        found: list[str] = []
        for search_dir in self._search_dirs:
            for path in search_dir.glob("*.py"):
                if path.stem.startswith("_"):
                    continue
                if path.stem not in self._plugins:
                    self._plugins[path.stem] = PluginInstance(
                        meta=PluginMeta(
                            name=path.stem,
                            description=f"Plugin from {path.name}",
                        )
                    )
                    found.append(path.stem)
            # Também busca subdiretórios com __init__.py (pacotes)
            for path in search_dir.iterdir():
                if path.is_dir() and (path / "__init__.py").exists():
                    if path.name not in self._plugins:
                        self._plugins[path.name] = PluginInstance(
                            meta=PluginMeta(
                                name=path.name,
                                description=f"Plugin package from {path.name}/",

                            )
                        )
                        found.append(path.name)

        if found:
            logger.info("Discovered %d plugins: %s", len(found), found)
        return found

    # ── Carregamento ───────────────────────────────────────────────

    def load(self, name: str) -> bool:
        """Carrega um plugin específico.

        Args:
            name: Nome do plugin.

        Returns:
            True se carregado com sucesso.

        Raises:
            NotFoundError: Se o plugin não for encontrado.
            PluginError: Se o carregamento falhar.
        """
        plugin = self._plugins.get(name)
        if plugin is None:
            raise NotFoundError(f"Plugin '{name}' not found")

        try:
            module = importlib.import_module(name)
            plugin.module = module

            # Procura instância da classe Plugin
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, "execute_hook") and obj is not type:
                    plugin.instance = obj()
                    break

            plugin.loaded_at = time.time()
            logger.info("Loaded plugin '%s' (v%s)", name, plugin.meta.version)

            if self._auto_enable and plugin.instance:
                import asyncio
                try:
                    load_config = {"container": self._container} if self._container else {}
                    loop = asyncio.get_running_loop()
                    loop.create_task(plugin.instance.on_load(load_config))
                except RuntimeError:
                    pass

            return True

        except ImportError as e:
            raise PluginError(f"Failed to import plugin '{name}': {e}") from e
        except Exception as e:
            raise PluginError(f"Failed to load plugin '{name}': {e}") from e

    def load_all(self) -> int:
        """Carrega todos os plugins descobertos."""
        count = 0
        for name in list(self._plugins.keys()):
            try:
                if self.load(name):
                    count += 1
            except (PluginError, NotFoundError) as e:
                logger.warning("Skipping plugin '%s': %s", name, e)
        logger.info("Loaded %d/%d plugins", count, len(self._plugins))
        return count

    def unload(self, name: str) -> bool:
        """Descarrega um plugin."""
        plugin = self._plugins.get(name)
        if plugin is None:
            return False

        if plugin.instance:
            try:
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                    loop.create_task(plugin.instance.on_unload())
                except RuntimeError:
                    pass
            except Exception as e:
                logger.warning("Error unloading plugin '%s': %s", name, e)

        plugin.instance = None
        plugin.module = None
        plugin.enabled = False
        logger.info("Unloaded plugin '%s'", name)
        return True

    # ── Consultas ──────────────────────────────────────────────────

    def get_plugin(self, name: str) -> Optional[PluginInstance]:
        """Retorna um plugin pelo nome."""
        return self._plugins.get(name)

    def list_plugins(self, loaded_only: bool = False) -> list[PluginInstance]:
        """Lista plugins, opcionalmente apenas os carregados."""
        result = list(self._plugins.values())
        if loaded_only:
            result = [p for p in result if p.module is not None]
        return result

    def get_plugin_names(self) -> list[str]:
        return sorted(self._plugins.keys())

    @property
    def count(self) -> int:
        return len(self._plugins)

    @property
    def loaded_count(self) -> int:
        return sum(1 for p in self._plugins.values() if p.module is not None)

    # ── Descobrimento de Plugins TypeScript ────────────────────────

    def discover_ts_plugins(self, directories: Optional[list[str | Path]] = None) -> list[str]:
        """Descobre plugins TypeScript (.ts) para metadados.

        Args:
            directories: Lista de diretórios para buscar arquivos .ts.

        Returns:
            Lista de nomes de plugins TypeScript encontrados.
        """
        ts_dirs = directories or []
        if self._container:
            try:
                from core.config import settings
                ts_dirs.append(settings.ECO_ROOT / "plugins")
            except Exception:
                ts_dirs.append(Path.cwd() / "plugins")

        found: list[str] = []
        for ts_dir in ts_dirs:
            search_path = Path(ts_dir)
            if not search_path.exists():
                continue
            for path in search_path.glob("*.ts"):
                if path.stem.startswith("_"):
                    continue
                if path.stem not in self._plugins:
                    self._plugins[path.stem] = PluginInstance(
                        meta=PluginMeta(
                            name=path.stem,
                            description=f"TypeScript plugin from {path.name}",
                            plugin_type="typescript",
                        )
                    )
                    found.append(path.stem)

        if found:
            logger.info("Discovered %d TypeScript plugins: %s", len(found), found)
        return found

    def list_ts_plugins(self) -> list[PluginInstance]:
        """Lista apenas plugins TypeScript."""
        return [p for p in self._plugins.values() if p.meta.plugin_type == "typescript"]

    # ── Registro no Container DI ──────────────────────────────────

    def register_in_container(self, name: str) -> bool:
        """Registra um plugin específico no Container DI.

        O plugin fica acessível como 'plugin.<nome>' no Container.
        Exemplo: container.resolve('plugin.manus-evolve')

        Args:
            name: Nome do plugin.

        Returns:
            True se registrado com sucesso.
        """
        if self._container is None:
            logger.warning("No container to register plugin '%s'", name)
            return False

        plugin = self._plugins.get(name)
        if plugin is None:
            logger.warning("Plugin '%s' not found for container registration", name)
            return False

        container_key = f"plugin.{name}"
        if not self._container.is_registered(container_key):
            self._container.register(container_key, plugin)
            logger.debug("Registered plugin '%s' as '%s'", name, container_key)
        return True

    def register_all_in_container(self) -> int:
        """Registra todos os plugins descobertos no Container DI.

        Returns:
            Número de plugins registrados.
        """
        count = 0
        for name in list(self._plugins.keys()):
            if self.register_in_container(name):
                count += 1
        logger.info("Registered %d plugins in container", count)
        return count

    def get_plugin_status(self, name: str) -> Optional[dict]:
        """Retorna status detalhado de um plugin.

        Args:
            name: Nome do plugin.

        Returns:
            Dict com status ou None se não encontrado.
        """
        plugin = self._plugins.get(name)
        if plugin is None:
            return None

        return {
            "name": plugin.meta.name,
            "version": plugin.meta.version,
            "type": plugin.meta.plugin_type,
            "enabled": plugin.enabled,
            "loaded": plugin.module is not None,
            "loaded_at": plugin.loaded_at,
            "description": plugin.meta.description,
            "hooks": plugin.meta.hooks,
            "dependencies": plugin.meta.dependencies,
            "in_container": self._container.is_registered(f"plugin.{name}") if self._container else False,
        }

    def health_summary(self) -> dict:
        """Resumo de saúde de todos os plugins.

        Returns:
            Dict com contagens e status agregado.
        """
        plugins = list(self._plugins.values())
        total = len(plugins)
        enabled = sum(1 for p in plugins if p.enabled)
        loaded = sum(1 for p in plugins if p.module is not None)
        ts_count = sum(1 for p in plugins if p.meta.plugin_type == "typescript")
        py_count = sum(1 for p in plugins if p.meta.plugin_type == "python")
        registered = sum(
            1 for p in plugins
            if self._container and self._container.is_registered(f"plugin.{p.meta.name}")
        )

        return {
            "total": total,
            "enabled": enabled,
            "loaded": loaded,
            "typescript": ts_count,
            "python": py_count,
            "registered_in_container": registered,
            "plugins": [self.get_plugin_status(p.meta.name) for p in plugins],
        }

    def __repr__(self) -> str:
        py_count = sum(1 for p in self._plugins.values() if p.meta.plugin_type == "python")
        ts_count = sum(1 for p in self._plugins.values() if p.meta.plugin_type == "typescript")
        return f"PluginManager(python={py_count}, typescript={ts_count}, loaded={self.loaded_count})"
