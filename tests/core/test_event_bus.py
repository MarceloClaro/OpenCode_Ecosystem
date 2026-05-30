"""
Testes do AsyncEventBus (core/events.py)

Cobre:
- subscribe + publish: handler recebe evento
- publish com dados e source
- unsubscribe: remocao de handler
- wildcard topics (sensor.*)
- subscriber_count / topics / clear
- Multiplos handlers para mesmo topico
- Handler async que falha nao quebra os outros
- Event dataclass (id, timestamp)
"""

import asyncio
from typing import Any

import pytest

from core.events import AsyncEventBus, Event


@pytest.fixture
def bus():
    """EventBus limpo para cada teste."""
    return AsyncEventBus()


@pytest.fixture
def event_collector():
    """Retorna uma lista + função handler que coleta eventos na lista."""
    collected: list[Event] = []

    async def handler(event: Event):
        collected.append(event)

    return collected, handler


# ─── Subscribe / Publish ─────────────────────────────────────────────

class TestSubscribePublish:
    @pytest.mark.asyncio
    async def test_basic_publish(self, bus):
        received: list[Event] = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe('test.event', handler)
        count = await bus.publish('test.event')
        assert count == 1
        assert len(received) == 1
        assert received[0].topic == 'test.event'

    @pytest.mark.asyncio
    async def test_publish_with_data(self, bus):
        received: list[Any] = []

        async def handler(event: Event):
            received.append(event.data)

        bus.subscribe('data.event', handler)
        await bus.publish('data.event', {'key': 42})
        assert received[0] == {'key': 42}

    @pytest.mark.asyncio
    async def test_publish_with_source(self, bus):
        received: list[str] = []

        async def handler(event: Event):
            received.append(event.source)

        bus.subscribe('src.event', handler)
        await bus.publish('src.event', source='test-module')
        assert received[0] == 'test-module'

    @pytest.mark.asyncio
    async def test_no_subscribers_returns_zero(self, bus):
        count = await bus.publish('lonely.topic')
        assert count == 0

    @pytest.mark.asyncio
    async def test_event_has_id_and_timestamp(self, bus):
        received: list[Event] = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe('meta', handler)
        await bus.publish('meta', 'payload')
        event = received[0]
        assert event.id is not None
        assert len(event.id) == 12
        assert event.timestamp is not None

    @pytest.mark.asyncio
    async def test_subscribe_returns_id(self, bus):
        sub_id = bus.subscribe('x', lambda e: None)
        assert sub_id is not None
        assert isinstance(sub_id, str)
        assert len(sub_id) == 12


# ─── Unsubscribe ────────────────────────────────────────────────────

class TestUnsubscribe:
    @pytest.mark.asyncio
    async def test_unsubscribe_stops_handler(self, bus):
        received: list[Event] = []

        async def handler(event: Event):
            received.append(event)

        sub_id = bus.subscribe('test', handler)
        await bus.publish('test')
        assert len(received) == 1

        bus.unsubscribe('test', sub_id)
        await bus.publish('test')
        assert len(received) == 1  # nao incrementou

    @pytest.mark.asyncio
    async def test_unsubscribe_wildcard(self, bus):
        received: list[Event] = []

        async def handler(event: Event):
            received.append(event)

        sub_id = bus.subscribe('sensors.*', handler)
        bus.unsubscribe('sensors.*', sub_id)
        await bus.publish('sensors.temp')
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_unsubscribe_nonexistent_returns_false(self, bus):
        assert bus.unsubscribe('ghost', 'invalid') is False

    @pytest.mark.asyncio
    async def test_unsubscribe_twice(self, bus):
        async def h(e):
            pass
        sid = bus.subscribe('t', h)
        assert bus.unsubscribe('t', sid) is True
        assert bus.unsubscribe('t', sid) is False


# ─── Wildcard Topics ────────────────────────────────────────────────

class TestWildcardTopics:
    @pytest.mark.asyncio
    async def test_wildcard_matches_subtopic(self, bus):
        received: list[str] = []

        async def handler(event: Event):
            received.append(event.topic)

        bus.subscribe('sensors.*', handler)
        await bus.publish('sensors.temp')
        await bus.publish('sensors.humidity')
        assert len(received) == 2
        assert 'sensors.temp' in received
        assert 'sensors.humidity' in received

    @pytest.mark.asyncio
    async def test_wildcard_does_not_match_unrelated(self, bus):
        received: list[Event] = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe('sensors.*', handler)
        await bus.publish('actuators.move')
        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_exact_match_preferred(self, bus):
        """Handler exato e wildcard devem ambos receber."""
        exact: list[Event] = []
        wild: list[Event] = []

        async def h_exact(e):
            exact.append(e)

        async def h_wild(e):
            wild.append(e)

        bus.subscribe('sensors.temp', h_exact)
        bus.subscribe('sensors.*', h_wild)
        await bus.publish('sensors.temp')
        assert len(exact) == 1
        assert len(wild) == 1


# ─── Metadados ──────────────────────────────────────────────────────

class TestMetadata:
    def test_subscriber_count_exact(self, bus):
        async def h1(e):
            pass

        async def h2(e):
            pass

        bus.subscribe('x', h1)
        bus.subscribe('x', h2)
        assert bus.subscriber_count('x') == 2

    def test_subscriber_count_wildcard(self, bus):
        async def h(e):
            pass

        bus.subscribe('sensors.*', h)
        assert bus.subscriber_count('sensors.temp') == 1

    def test_subscriber_count_nonexistent(self, bus):
        assert bus.subscriber_count('void') == 0

    def test_topics_empty(self, bus):
        assert bus.topics() == []

    def test_topics_with_subscriptions(self, bus):
        async def h(e):
            pass

        bus.subscribe('a.b', h)
        bus.subscribe('c.d', h)
        bus.subscribe('wild.*', h)
        topics = bus.topics()
        assert 'a.b' in topics
        assert 'c.d' in topics
        assert 'wild.*' in topics

    def test_topics_after_unsubscribe(self, bus):
        async def h(e):
            pass

        sid = bus.subscribe('temp', h)
        bus.unsubscribe('temp', sid)
        assert bus.topics() == []


# ─── Clear ──────────────────────────────────────────────────────────

class TestClear:
    @pytest.mark.asyncio
    async def test_clear_removes_all(self, bus):
        async def h(e):
            pass

        bus.subscribe('a', h)
        bus.subscribe('b', h)
        cleared = bus.clear()
        assert cleared == 2
        assert bus.topics() == []
        assert bus.subscriber_count('a') == 0


# ─── Multiplos Handlers ─────────────────────────────────────────────

class TestMultipleHandlers:
    @pytest.mark.asyncio
    async def test_two_handlers_both_receive(self, bus):
        results: list[int] = []

        async def h1(e):
            results.append(1)

        async def h2(e):
            results.append(2)

        bus.subscribe('multi', h1)
        bus.subscribe('multi', h2)
        await bus.publish('multi')
        assert sorted(results) == [1, 2]

    @pytest.mark.asyncio
    async def test_handler_exception_does_not_block_others(self, bus):
        results: list[int] = []

        async def good(e):
            results.append(1)

        async def bad(e):
            raise ValueError("i'm broken")

        async def also_good(e):
            results.append(2)

        bus.subscribe('resilient', good)
        bus.subscribe('resilient', bad)
        bus.subscribe('resilient', also_good)
        count = await bus.publish('resilient')
        assert count == 2  # apenas os 2 bons contam
        assert results == [1, 2]


# ─── Event Loop ─────────────────────────────────────────────────────

class TestEventLoop:
    @pytest.mark.asyncio
    async def test_publish_with_explicit_loop(self):
        """Se loop for passado no init, publish usa o loop corrente."""
        bus = AsyncEventBus()
        received: list[Event] = []

        async def handler(event: Event):
            received.append(event)

        bus.subscribe('t', handler)
        await bus.publish('t')
        assert len(received) == 1
