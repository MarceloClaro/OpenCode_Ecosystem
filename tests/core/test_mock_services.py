"""
Testes dos Mock Services (core/mock_services.py)

Cobre:
- MockStateManager: CRUD, operations tracking, clear
- MockEventBus: subscribe/publish/unsubscribe, RecordedEvent
- MockEventBus: published(), clear(), reset()
"""

import pytest

from core.mock_services import MockStateManager, MockEventBus, RecordedEvent


# ─── MockStateManager ────────────────────────────────────────────────

class TestMockStateManager:
    @pytest.fixture
    def ms(self):
        return MockStateManager()

    def test_set_and_get(self, ms):
        ms.set('key', 'value')
        assert ms.get('key') == 'value'

    def test_get_with_default(self, ms):
        assert ms.get('missing', 42) == 42
        assert ms.get('missing') is None

    def test_delete_existing(self, ms):
        ms.set('x', 1)
        assert ms.delete('x') is True
        assert ms.get('x') is None

    def test_delete_nonexistent(self, ms):
        assert ms.delete('phantom') is False

    def test_keys(self, ms):
        ms.set('a', 1)
        ms.set('b', 2)
        assert sorted(ms.keys()) == ['a', 'b']

    def test_exists(self, ms):
        ms.set('present', True)
        assert ms.exists('present') is True
        assert ms.exists('absent') is False

    def test_close(self, ms):
        ms.close()
        assert 'close' in ms.operations

    def test_tracks_operations(self, ms):
        ms.set('a', 1)
        ms.get('a')
        ms.delete('a')
        assert ms.operations == ['set:a', 'get:a', 'delete:a']

    def test_clear_resets_everything(self, ms):
        ms.set('a', 1)
        ms.set('b', 2)
        ms.clear()
        assert ms.get('a') is None
        assert ms.get('b') is None
        assert ms.operations == ['get:a', 'get:b']  # clear nao apaga rastro posterior

    def test_len(self, ms):
        assert len(ms) == 0
        ms.set('a', 1)
        assert len(ms) == 1
        ms.set('b', 2)
        assert len(ms) == 2
        ms.delete('a')
        assert len(ms) == 1


# ─── MockEventBus ────────────────────────────────────────────────────

class TestMockEventBus:
    @pytest.fixture
    def mb(self):
        return MockEventBus()

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self, mb):
        received: list[RecordedEvent] = []

        def handler(event: RecordedEvent):
            received.append(event)

        mb.subscribe('test.event', handler)
        await mb.publish('test.event', {'key': 'val'}, source='test')
        assert len(received) == 1
        assert received[0].topic == 'test.event'
        assert received[0].data == {'key': 'val'}
        assert received[0].source == 'test'

    @pytest.mark.asyncio
    async def test_publish_without_subscribers(self, mb):
        count = await mb.publish('nobody.listens')
        assert count == 0

    @pytest.mark.asyncio
    async def test_publish_records_event(self, mb):
        await mb.publish('recorded', 'data')
        assert len(mb.events) == 1
        assert mb.events[0].topic == 'recorded'
        assert mb.events[0].data == 'data'

    @pytest.mark.asyncio
    async def test_published_check(self, mb):
        await mb.publish('event.one')
        assert mb.published('event.one') is True
        assert mb.published('event.two') is False

    @pytest.mark.asyncio
    async def test_clear_events_and_subscriptions(self, mb):
        def handler(e):
            pass

        mb.subscribe('a', handler)
        await mb.publish('a')
        cleared = mb.clear()
        assert cleared >= 0  # clear retorna numero de subs removidos
        assert mb.events == []
        assert mb.subscriber_count('a') == 0

    @pytest.mark.asyncio
    async def test_reset(self, mb):
        def handler(e):
            pass

        mb.subscribe('x', handler)
        await mb.publish('x')
        mb.reset()
        assert mb.events == []
        assert mb.subscriber_count('x') == 0
        assert mb.published('x') is False

    @pytest.mark.asyncio
    async def test_wildcard_topic(self, mb):
        received: list[RecordedEvent] = []

        def handler(event: RecordedEvent):
            received.append(event)

        mb.subscribe('sensors.*', handler)
        await mb.publish('sensors.temp', 36.5)
        assert len(received) == 1
        assert received[0].data == 36.5

    @pytest.mark.asyncio
    async def test_unsubscribe(self, mb):
        received: list[RecordedEvent] = []

        def handler(event: RecordedEvent):
            received.append(event)

        sub_id = mb.subscribe('t', handler)
        await mb.publish('t')
        assert len(received) == 1

        mb.unsubscribe('t', sub_id)
        await mb.publish('t')
        assert len(received) == 1  # nao incrementou

    @pytest.mark.asyncio
    async def test_subscriber_count(self, mb):
        def h1(e):
            pass

        def h2(e):
            pass

        mb.subscribe('topic', h1)
        mb.subscribe('topic', h2)
        assert mb.subscriber_count('topic') == 2
