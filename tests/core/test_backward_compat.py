"""
Testes de Compatibilidade via Container DI.
Substitui os antigos testes de proxy PEP 562 e LegacyState/Event proxies,
que foram removidos na Fase 4 da migracao DI.
"""

import pytest

from core import initialize_core, reset_for_testing
from core.container import Container


@pytest.fixture(autouse=True)
def auto_reset():
    reset_for_testing()
    yield
    reset_for_testing()


class TestContainerAccess:
    """Testa acesso a servicos via Container DI (unico caminho oficial)."""

    def test_resolve_state_manager_after_init(self):
        initialize_core()
        sm = Container.instance().resolve('state_manager')
        assert sm is not None
        sm.set('di_test', 'ok')
        assert sm.get('di_test') == 'ok'

    def test_resolve_event_bus_after_init(self):
        initialize_core()
        eb = Container.instance().resolve('event_bus')
        assert eb is not None
        assert hasattr(eb, 'subscribe')
        assert hasattr(eb, 'publish')
        assert hasattr(eb, 'topics')

    def test_container_singleton(self):
        initialize_core()
        c1 = Container.instance()
        c2 = Container.instance()
        assert c1 is c2

    def test_both_services_share_container(self):
        initialize_core()
        container = Container.instance()
        sm = container.resolve('state_manager')
        eb = container.resolve('event_bus')
        assert sm is not None
        assert eb is not None
        # Verifica que ambos estao no mesmo container
        registered = container.registered()
        assert 'state_manager' in registered
        assert 'event_bus' in registered

    def test_resolve_fails_before_init(self):
        reset_for_testing()
        with pytest.raises(Exception):
            Container.instance().resolve('state_manager')

    def test_resolve_fails_after_reset(self):
        initialize_core()
        reset_for_testing()
        with pytest.raises(Exception):
            Container.instance().resolve('state_manager')

    def test_resolve_unknown_service(self):
        from core.container import ServiceNotFoundError
        with pytest.raises(ServiceNotFoundError):
            Container.instance().resolve('non_existent_service')


class TestInitAndReset:
    """Testa ciclo de vida do container."""

    def test_init_registers_both_services(self):
        initialize_core()
        registered = Container.instance().registered()
        assert 'state_manager' in registered
        assert 'event_bus' in registered

    def test_reset_clears_all(self):
        initialize_core()
        Container.instance().reset()
        assert Container.instance().registered() == []

    def test_double_init_skips(self):
        initialize_core()
        container = Container.instance()
        sm1 = container.resolve('state_manager')
        initialize_core()  # segunda chamada deve logar warning e ignorar
        sm2 = container.resolve('state_manager')
        assert sm1 is sm2, "Double init deve manter mesma instancia"

    def test_can_reinit_after_reset(self):
        initialize_core()
        reset_for_testing()
        initialize_core()
        assert Container.instance().is_registered('state_manager')
