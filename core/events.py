"""
core/events.py (refatorado - proposto) - Event Bus Local com DI.
Implementa IEventBus. Remove instancia global.
"""

from __future__ import annotations
import asyncio
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Optional
from core.interfaces import IEventBus

logger = logging.getLogger(__name__)
EventHandler = Callable[['Event'], Coroutine[Any, Any, None]]


@dataclass
class Event:
    topic: str
    data: Any = None
    source: str = ''
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    timestamp: str = field(default_factory=lambda: time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime()))


class AsyncEventBus(IEventBus):
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self._lock = threading.Lock()
        self._loop = loop
        self._subscriptions: dict[str, dict[str, EventHandler]] = {}
        self._wildcard_topics: dict[str, dict[str, EventHandler]] = {}

    def subscribe(self, topic: str, handler: EventHandler) -> str:
        sub_id = uuid.uuid4().hex[:12]
        with self._lock:
            if topic.endswith('.*'):
                self._wildcard_topics.setdefault(topic, {})[sub_id] = handler
            else:
                self._subscriptions.setdefault(topic, {})[sub_id] = handler
        return sub_id

    def unsubscribe(self, topic: str, sub_id: str) -> bool:
        with self._lock:
            subs = self._subscriptions.get(topic)
            if subs and sub_id in subs:
                del subs[sub_id]
                if not subs:
                    del self._subscriptions[topic]
                return True
            for wt in list(self._wildcard_topics.keys()):
                wsubs = self._wildcard_topics[wt]
                if sub_id in wsubs:
                    del wsubs[sub_id]
                    if not wsubs:
                        del self._wildcard_topics[wt]
                    return True
        return False

    async def publish(self, topic: str, data: Any = None, source: str = '') -> int:
        event = Event(topic=topic, data=data, source=source)
        handlers: list[EventHandler] = []
        with self._lock:
            subs = self._subscriptions.get(topic)
            if subs:
                handlers.extend(subs.values())
            prefix = topic.rsplit('.', 1)[0] if '.' in topic else topic
            wsubs = self._wildcard_topics.get(f'{prefix}.*')
            if wsubs:
                handlers.extend(wsubs.values())
        if not handlers:
            return 0
        results = await asyncio.gather(*[h(event) for h in handlers], return_exceptions=True)
        count = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error('Handler %d for %s failed: %s', i, topic, result)
            else:
                count += 1
        return count

    def subscriber_count(self, topic: str) -> int:
        count = 0
        with self._lock:
            subs = self._subscriptions.get(topic)
            if subs:
                count += len(subs)
            prefix = topic.rsplit('.', 1)[0] if '.' in topic else topic
            wsubs = self._wildcard_topics.get(f'{prefix}.*')
            if wsubs:
                count += len(wsubs)
        return count

    def topics(self) -> list[str]:
        with self._lock:
            return sorted(list(self._subscriptions.keys()) + list(self._wildcard_topics.keys()))

    def clear(self) -> int:
        count = 0
        with self._lock:
            for subs in self._subscriptions.values():
                count += len(subs)
            for wsubs in self._wildcard_topics.values():
                count += len(wsubs)
            self._subscriptions.clear()
            self._wildcard_topics.clear()
        return count
