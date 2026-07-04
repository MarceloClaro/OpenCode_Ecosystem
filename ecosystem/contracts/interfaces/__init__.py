"""
Interfaces formais do ecossistema.

Define os contratos ABC/Protocol que todos os módulos devem implementar.
"""

from ecosystem.contracts.interfaces.istate_manager import IStateManager
from ecosystem.contracts.interfaces.ievent_bus import IEventBus
from ecosystem.contracts.interfaces.icache import ICache
from ecosystem.contracts.interfaces.itask_queue import ITaskQueue
from ecosystem.contracts.interfaces.iagent import IAgent
from ecosystem.contracts.interfaces.iplugin import IPlugin
from ecosystem.contracts.interfaces.iscanner import IScanner
from ecosystem.contracts.interfaces.ipipeline import IPipeline
from ecosystem.contracts.interfaces.iadapter import IAdapter

__all__ = [
    "IStateManager",
    "IEventBus",
    "ICache",
    "ITaskQueue",
    "IAgent",
    "IPlugin",
    "IScanner",
    "IPipeline",
    "IAdapter",
]
