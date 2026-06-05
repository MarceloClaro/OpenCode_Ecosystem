"""
Testes de Integracao do Core (core/__init__.py)

Cobre:
- initialize_core() registra servicos no Container
- reset_for_testing() limpa o Container
- initialize_core() com db_path customizado
- initialize_core() com path vazio (usa default do settings)
- Double-init nao recria servicos
- Container.instance() resolve servicos apos init
- __all__ contem os nomes esperados
"""

import tempfile
from pathlib import Path

import pytest

from core import (
    __all__,
    initialize_core,
    reset_for_testing,
    Container,
    IStateManager,
    IEventBus,
    ICache,
    ITaskQueue,
    AgentManager,
    PluginManager,
    SkillManager,
    TTLCache,
    TaskQueue,
    RestClient,
)


@pytest.fixture(autouse=True)
def auto_reset():
    """Garante core limpo antes e depois de cada teste."""
    reset_for_testing()
    yield
    reset_for_testing()


# ─── initialize_core ─────────────────────────────────────────────────

class TestInitializeCore:
    def test_initialize_registers_services(self):
        initialize_core()
        container = Container.instance()
        for name in ['state_manager', 'event_bus', 'agent_manager',
                     'plugin_manager', 'skill_manager', 'cache', 'task_queue']:
            assert container.is_registered(name), f"{name} not registered"

    def test_initialize_with_custom_db_path(self):
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = Path(f.name)
        try:
            initialize_core(str(db_path))
            sm = Container.instance().resolve('state_manager')
            sm.set('custom', 'path')
            assert sm.get('custom') == 'path'
            sm.close()
        finally:
            for p in [db_path, db_path.with_suffix('.db-wal'), db_path.with_suffix('.db-shm')]:
                try:
                    p.unlink(missing_ok=True)
                except PermissionError:
                    pass

    def test_double_init_skips(self):
        initialize_core()
        container = Container.instance()
        sm1 = container.resolve('state_manager')
        initialize_core()  # segunda chamada deve logar warning e ignorar
        sm2 = container.resolve('state_manager')
        assert sm1 is sm2, "Double init deve manter mesma instancia"


# ─── reset_for_testing ──────────────────────────────────────────────

class TestResetForTesting:
    def test_reset_clears_container(self):
        initialize_core()
        assert Container.instance().is_registered('state_manager')
        reset_for_testing()
        assert not Container.instance().is_registered('state_manager')

    def test_reset_allows_reinit(self):
        initialize_core()
        reset_for_testing()
        initialize_core()
        assert Container.instance().is_registered('state_manager')


    def test_managers_registered_after_init(self):
        """initialize_core() must register all three managers."""
        initialize_core()
        container = Container.instance()
        for mgr_name in ['agent_manager', 'plugin_manager', 'skill_manager']:
            assert container.is_registered(mgr_name), f"{mgr_name} not registered"
            mgr = container.resolve(mgr_name)
            assert mgr is not None
            assert hasattr(mgr, 'discover') or hasattr(mgr, 'register_agent_type')


# ─── Container Access ──────────────────────────────────────────────

class TestContainerAccess:
    def test_resolve_state_manager_after_init(self):
        initialize_core()
        sm = Container.instance().resolve('state_manager')
        assert sm is not None
        assert hasattr(sm, 'get')
        assert hasattr(sm, 'set')
        sm.set('container_test', 'works')
        assert sm.get('container_test') == 'works'

    def test_resolve_event_bus_after_init(self):
        import asyncio
        initialize_core()
        eb = Container.instance().resolve('event_bus')
        assert eb is not None
        assert hasattr(eb, 'subscribe')
        assert hasattr(eb, 'publish')
        assert hasattr(eb, 'topics')

    def test_resolve_fails_before_init(self):
        reset_for_testing()
        with pytest.raises(Exception):
            Container.instance().resolve('state_manager')

    def test_resolve_fails_after_reset(self):
        initialize_core()
        reset_for_testing()
        with pytest.raises(Exception):
            Container.instance().resolve('state_manager')


# ─── __all__ ─────────────────────────────────────────────────────────

class TestAll:
    def test_all_contains_expected_names(self):
        expected = {
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
        }
        assert set(__all__) == expected

    def test_can_import_all_names(self):
        """Verifica que todos os nomes em __all__ sao importaveis."""
        from core import (
            settings,
            initialize_core,
            reset_for_testing,
            Container,
            IStateManager,
            IEventBus,
            ICache,
            ITaskQueue,
            AgentManager,
            PluginManager,
            SkillManager,
            TTLCache,
            TaskQueue,
            RestClient,
            CommandRegistry,
        )
