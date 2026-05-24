# -*- coding: utf-8 -*-
"""core.events - Barramento de eventos assincrono (fire-and-forget)."""

import asyncio
from collections import defaultdict
from typing import Any, Callable, Coroutine, Optional


class EventBus:
    """EventBus simples com suporte a handlers sync e async."""

    def __init__(self):
        self._handlers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, event: str, handler: Callable) -> None:
        self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: Callable) -> None:
        if event in self._handlers:
            self._handlers[event].remove(handler)

    async def publish(self, event: str, data: Any = None, source: str = "") -> None:
        payload = {"event": event, "data": data, "source": source}
        for handler in self._handlers.get(event, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(payload)
                else:
                    handler(payload)
            except Exception:
                pass

    def publish_sync(self, event: str, data: Any = None, source: str = "") -> None:
        payload = {"event": event, "data": data, "source": source}
        for handler in self._handlers.get(event, []):
            try:
                if not asyncio.iscoroutinefunction(handler):
                    handler(payload)
            except Exception:
                pass

    def clear(self):
        self._handlers.clear()
