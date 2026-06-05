"""
core/__init__.py (refatorado) - Core Runtime com DI.
Inicializacao explicita via initialize_core().
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import Any
from core.config import settings, OpenCodeSettings
from core.container import Container
from core.state import SQLiteStateManager
from core.events import AsyncEventBus
from core.interfaces import IStateManager, IEventBus, ICache, ITaskQueue
from core.agent_manager import AgentManager
from core.plugin_manager import PluginManager
from core.skill_manager import SkillManager
from core.cache import TTLCache
from core.task_queue import TaskQueue
from core.rest_client import RestClient
from core.command_registry import CommandRegistry, discover_command_dir

logger = logging.getLogger(__name__)

settings: OpenCodeSettings = settings


def initialize_core(
    db_path: str | Path = '',
    cache_maxsize: int = 1000,
    cache_ttl: float = 300.0,
    task_queue_workers: int = 4,
) -> None:
    """Inicializa o core com injecao de dependencia explicita.

    Registra no Container DI:
    - state_manager (SQLiteStateManager)
    - event_bus (AsyncEventBus)
    - agent_manager (AgentManager)
    - plugin_manager (PluginManager)
    - skill_manager (SkillManager)
    - cache (TTLCache)
    - task_queue (TaskQueue)
    """
    if Container.instance().is_registered('state_manager'):
        logger.warning('Core already initialized - skipping')
        return

    path = Path(db_path) if db_path else settings.state_db_path()
    sm = SQLiteStateManager(path)
    eb = AsyncEventBus()

    container = Container.instance()
    container.register('state_manager', sm)
    container.register('event_bus', eb)

    agent_mgr = AgentManager(container=container)
    plugin_mgr = PluginManager(container=container)
    skill_mgr = SkillManager(container=container)
    cache_svc = TTLCache(maxsize=cache_maxsize, default_ttl=cache_ttl, container=container)
    task_q = TaskQueue(max_concurrent=task_queue_workers, container=container)

    container.register('agent_manager', agent_mgr)
    container.register('plugin_manager', plugin_mgr)
    container.register('skill_manager', skill_mgr)
    container.register('cache', cache_svc)
    container.register('task_queue', task_q)

    # Plugin discovery: TypeScript plugins via Container bridge
    found_ts = plugin_mgr.discover_ts_plugins()
    if found_ts:
        plugin_mgr.register_all_in_container()
        logger.info("Registered %d TS plugins in Container", len(found_ts))

    # Command registry bridge (lê command/*.md)
    cmd_dir = discover_command_dir(settings.ECO_ROOT)
    cmd_reg = CommandRegistry(command_dir=cmd_dir, container=container)
    container.register('command_registry', cmd_reg)

    import asyncio
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(eb.publish('core.initialized', {'db_path': str(path)}))
    except RuntimeError:
        logger.debug('No running event loop - deferring core.initialized event')

    logger.info('Core initialized - db=%s, cache=%dx%.0fs, queue=%dw',
                path, cache_maxsize, cache_ttl, task_queue_workers)


def reset_for_testing() -> None:
    """Reseta o container - USO APENAS EM TESTES."""
    Container.instance().reset()
    logger.warning('Core reset for testing - all services cleared')


__all__ = [
    'settings',
    'initialize_core',
    'reset_for_testing',
    'Container',
    'IStateManager',
    'IEventBus',
    'ICache',
    'ITaskQueue',
    'AgentManager',
    'PluginManager',
    'SkillManager',
    'TTLCache',
    'TaskQueue',
    'RestClient',
    'CommandRegistry',
]
