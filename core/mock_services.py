"""
core/mock_services.py (proposto) - Mocks para Testes com DI.
Implementacoes ficticias type-safe de IStateManager e IEventBus.
"""

from __future__ import annotations
import asyncio
import uuid
from dataclasses import dataclass
from typing import Any, Callable
from core.interfaces import IStateManager, IEventBus


@dataclass
class RecordedEvent:
    topic: str
    data: Any = None
    source: str = ''


class MockStateManager(IStateManager):
    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self.operations: list[str] = []

    def get(self, key: str, default: Any = None) -> Any:
        self.operations.append(f'get:{key}')
        return self._store.get(key, default)

    def set(self, key: str, data: Any) -> None:
        self.operations.append(f'set:{key}')
        self._store[key] = data

    def delete(self, key: str) -> bool:
        self.operations.append(f'delete:{key}')
        return self._store.pop(key, None) is not None

    def keys(self) -> list[str]:
        self.operations.append('keys')
        return list(self._store.keys())

    def exists(self, key: str) -> bool:
        self.operations.append(f'exists:{key}')
        return key in self._store

    def close(self) -> None:
        self.operations.append('close')

    def clear(self) -> None:
        self._store.clear()
        self.operations.clear()

    def __len__(self) -> int:
        return len(self._store)


class MockEventBus(IEventBus):
    def __init__(self) -> None:
        self.events: list[RecordedEvent] = []
        self._subscriptions: dict[str, dict[str, Callable]] = {}
        self._wildcard_topics: dict[str, dict[str, Callable]] = {}

    def subscribe(self, topic: str, handler: Callable) -> str:
        sub_id = uuid.uuid4().hex[:12]
        if topic.endswith('.*'):
            self._wildcard_topics.setdefault(topic, {})[sub_id] = handler
        else:
            self._subscriptions.setdefault(topic, {})[sub_id] = handler
        return sub_id

    def unsubscribe(self, topic: str, sub_id: str) -> bool:
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
        from dataclasses import dataclass
        event = RecordedEvent(topic=topic, data=data, source=source)
        self.events.append(event)
        handlers: list[Callable] = []
        subs = self._subscriptions.get(topic, {})
        handlers.extend(subs.values())
        prefix = topic.rsplit('.', 1)[0] if '.' in topic else topic
        wsubs = self._wildcard_topics.get(f'{prefix}.*', {})
        handlers.extend(wsubs.values())
        count = 0
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
                count += 1
            except Exception:
                pass
        return count

    def subscriber_count(self, topic: str) -> int:
        count = len(self._subscriptions.get(topic, {}))
        prefix = topic.rsplit('.', 1)[0] if '.' in topic else topic
        return count + len(self._wildcard_topics.get(f'{prefix}.*', {}))

    def topics(self) -> list[str]:
        return sorted(list(self._subscriptions.keys()) + list(self._wildcard_topics.keys()))

    def clear(self) -> int:
        total = self.subscriber_count('') if self._subscriptions else 0
        self._subscriptions.clear()
        self._wildcard_topics.clear()
        self.events.clear()
        return total

    def reset(self) -> None:
        self.events.clear()
        self._subscriptions.clear()
        self._wildcard_topics.clear()

    def published(self, topic: str) -> bool:
        return any(e.topic == topic for e in self.events)
