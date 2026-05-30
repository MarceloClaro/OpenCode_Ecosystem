"""
Testes de Integracao Nexus DI (Fase 5).

Cobre:
- Nexus scripts resolvem do Container (sync_orchestrator, mcp_router, context_offload)
- CommandRegistry integrado com command/
- PluginManager descobre plugins TS via Container
- Cross-module: command_registry + agent_manager + state_manager
- Compatibilidade retroativa Nexus scripts sem DI
"""
import inspect
from pathlib import Path

import pytest

from core import initialize_core, reset_for_testing
from core.container import Container


@pytest.fixture(autouse=True)
def auto_reset():
    reset_for_testing()
    yield
    reset_for_testing()


BASE_DIR = Path(__file__).resolve().parents[2]  # opencode root


# ─── Nexus Scripts DI ──────────────────────────────────────────────

class TestNexusMCPRouterDI:
    """MCPRouter deve aceitar container e ter from_container factory."""

    def test_mcp_router_accepts_container(self):
        from nexus.scripts.mcp_router import MCPRouter
        initialize_core()
        router = MCPRouter(container=Container.instance())
        assert router._container is not None

    def test_mcp_router_from_container(self):
        from nexus.scripts.mcp_router import MCPRouter
        initialize_core()
        router = MCPRouter.from_container(Container.instance())
        assert router._container is not None
        assert isinstance(router, MCPRouter)

    def test_mcp_router_backward_compat(self):
        from nexus.scripts.mcp_router import MCPRouter
        router = MCPRouter()  # sem container
        assert router._container is None
        assert hasattr(router, 'route_task')
        assert hasattr(router, 'register_mcp')


class TestNexusContextOffloadDI:
    """ContextOffloadManager deve aceitar container e ter from_container factory."""

    def test_context_offload_accepts_container(self):
        from nexus.scripts.context_offload import ContextOffloadManager
        initialize_core()
        mgr = ContextOffloadManager(container=Container.instance())
        assert mgr._container is not None

    def test_context_offload_from_container(self):
        from nexus.scripts.context_offload import ContextOffloadManager
        initialize_core()
        mgr = ContextOffloadManager.from_container(Container.instance())
        assert mgr._container is not None

    def test_context_offload_backward_compat(self):
        from nexus.scripts.context_offload import ContextOffloadManager
        mgr = ContextOffloadManager()  # sem container
        assert mgr._container is None
        assert hasattr(mgr, 'create_session')
        assert hasattr(mgr, 'add_entry')

    def test_context_offload_functional(self):
        from nexus.scripts.context_offload import ContextOffloadManager
        mgr = ContextOffloadManager(base_dir=str(BASE_DIR / ".reversa" / "test_context"))
        sid = mgr.create_session("test-di-session")
        assert sid == "test-di-session"
        eid = mgr.add_entry("test content", priority=5)
        assert eid is not None
        ctx = mgr.get_session_context()
        assert len(ctx) >= 1
        session_state = mgr.get_session_state()
        assert session_state is not None
        assert session_state["entry_count"] >= 1


class TestSyncOrchestratorDI:
    """SyncOrchestrator ja usa DI via Container.instance().resolve('state_manager')."""

    def test_sync_orchestrator_imports(self):
        from nexus.scripts.sync_orchestrator import SyncOrchestrator
        orch = SyncOrchestrator()
        assert hasattr(orch, 'run_full_sync')
        assert hasattr(orch, 'save_state')

    def test_sync_orchestrator_components(self):
        from nexus.scripts.sync_orchestrator import (
            SyncOrchestrator, ComponentDiscovery, DynamicScoringEngine,
            AutoHealingEngine, CrossValidationEngine, ConflictDetector, HealthEngine,
            DynamicScore, SyncComponent,
        )
        assert ComponentDiscovery is not None
        assert DynamicScoringEngine is not None
        assert AutoHealingEngine is not None
        assert CrossValidationEngine is not None
        assert ConflictDetector is not None
        assert HealthEngine is not None
        assert DynamicScore is not None
        assert SyncComponent is not None


# ─── CommandRegistry ↔ Core Integration ────────────────────────────

class TestCommandRegistryIntegration:
    """CommandRegistry integrado com Container e command/ directory."""

    def test_command_registry_in_container(self):
        initialize_core()
        registry = Container.instance().resolve('command_registry')
        assert registry is not None
        assert registry.count >= 14

    def test_command_registry_finds_reversa(self):
        initialize_core()
        registry = Container.instance().resolve('command_registry')
        cmd = registry.find("reversa")
        assert cmd is not None
        assert cmd.name == "reversa"
        assert len(cmd.triggers) >= 5
        assert "/reversa" in cmd.triggers

    def test_command_registry_finds_all_commands(self):
        initialize_core()
        registry = Container.instance().resolve('command_registry')
        all_cmds = registry.list()
        names = [c.name for c in all_cmds]
        for expected in ['auto', 'commit', 'evolve', 'plan', 'quantum',
                         'research', 'reversa', 'review', 'ticket']:
            assert expected in names, f"Command /{expected} not found"

    def test_command_registry_fuzzy_search(self):
        initialize_core()
        registry = Container.instance().resolve('command_registry')
        # Busca por parte do trigger
        cmd = registry.find("reverse engineering")
        assert cmd is not None
        assert cmd.name == "reversa"

    def test_command_registry_unknown(self):
        initialize_core()
        registry = Container.instance().resolve('command_registry')
        cmd = registry.find("nonexistent-command-xyz")
        assert cmd is None

    def test_command_registry_summary(self):
        initialize_core()
        registry = Container.instance().resolve('command_registry')
        summary = registry.summary()
        assert summary["total"] >= 14
        assert "reversa" in summary["names"]
        assert summary["loaded"] is True


# ─── PluginManager ↔ Core Integration ──────────────────────────────

class TestPluginManagerIntegration:
    """PluginManager descobre plugins TS e resolve do Container."""

    def test_plugin_manager_in_container(self):
        initialize_core()
        pm = Container.instance().resolve('plugin_manager')
        assert pm is not None
        assert hasattr(pm, 'discover_ts_plugins')
        assert hasattr(pm, 'list_ts_plugins')

    def test_ts_plugins_discovered_after_init(self):
        initialize_core()
        pm = Container.instance().resolve('plugin_manager')
        # verify TS plugins were discovered during initialize_core
        ts_list = pm.list_ts_plugins()
        ts_names = [p.meta.name for p in ts_list]
        assert "manus-evolve" in ts_names
        assert "ecosystem-sync" in ts_names
        assert "bernstein-sync" in ts_names

    def test_ts_plugin_has_correct_type(self):
        initialize_core()
        pm = Container.instance().resolve('plugin_manager')
        for plugin in pm.list_ts_plugins():
            assert plugin.meta.plugin_type == "typescript"

    def test_discover_ts_method_manual(self):
        pm = Container.instance().resolve('plugin_manager')
        # explicit call
        found = pm.discover_ts_plugins([str(BASE_DIR / "plugins")])
        # should return known ones or empty if already discovered
        ts_names = pm.get_plugin_names()
        assert "manus-evolve" in ts_names or "ecosystem-sync" in ts_names


# ─── Plugin Registration in Container ─────────────────────────────

class TestPluginRegistrationInContainer:
    """Plugins registrados no Container como 'plugin.<nome>'."""

    def test_plugins_registered_in_container_after_init(self):
        initialize_core()
        c = Container.instance()
        assert c.is_registered('plugin.manus-evolve'), "plugin.manus-evolve should be registered"
        assert c.is_registered('plugin.ecosystem-sync'), "plugin.ecosystem-sync should be registered"
        assert c.is_registered('plugin.bernstein-sync'), "plugin.bernstein-sync should be registered"

    def test_resolve_plugin_from_container(self):
        initialize_core()
        c = Container.instance()
        plugin = c.resolve('plugin.manus-evolve')
        assert plugin is not None
        assert plugin.meta.name == "manus-evolve"
        assert plugin.meta.plugin_type == "typescript"

    def test_plugin_status_method(self):
        initialize_core()
        pm = Container.instance().resolve('plugin_manager')
        status = pm.get_plugin_status('manus-evolve')
        assert status is not None
        assert status['name'] == 'manus-evolve'
        assert status['type'] == 'typescript'
        assert status['in_container'] is True

    def test_plugin_status_nonexistent(self):
        initialize_core()
        pm = Container.instance().resolve('plugin_manager')
        status = pm.get_plugin_status('nonexistent-plugin')
        assert status is None

    def test_health_summary(self):
        initialize_core()
        pm = Container.instance().resolve('plugin_manager')
        summary = pm.health_summary()
        assert summary['total'] >= 3
        assert summary['typescript'] >= 3
        assert summary['registered_in_container'] >= 3
        assert len(summary['plugins']) >= 3


# ─── Cross-Module Integration ──────────────────────────────────────

class TestCrossModuleIntegration:
    """command_registry + agent_manager + state_manager integrados."""

    def test_core_services_available(self):
        initialize_core()
        c = Container.instance()
        for name in ['state_manager', 'event_bus', 'agent_manager',
                     'plugin_manager', 'skill_manager', 'cache',
                     'task_queue', 'command_registry']:
            assert c.is_registered(name), f"{name} not in container"
            svc = c.resolve(name)
            assert svc is not None

        # Plugin individuais no Container
        for plugin_key in ['plugin.manus-evolve', 'plugin.ecosystem-sync', 'plugin.bernstein-sync']:
            assert c.is_registered(plugin_key), f"{plugin_key} not in container"

    def test_command_registry_and_state_manager(self):
        initialize_core()
        c = Container.instance()
        registry = c.resolve('command_registry')
        sm = c.resolve('state_manager')

        # Use state_manager para persistir dados do registry
        cmd_summary = registry.summary()
        sm.set('cmd_summary', cmd_summary)
        restored = sm.get('cmd_summary')
        assert restored['total'] == cmd_summary['total']
        assert restored['names'] == cmd_summary['names']

    def test_command_registry_and_agent_manager(self):
        initialize_core()
        c = Container.instance()
        registry = c.resolve('command_registry')
        am = c.resolve('agent_manager')

        # Verifica que ambos existem e tem metodos esperados
        assert hasattr(am, 'register_agent_type')
        assert hasattr(am, 'get_agent')
        cmd_list = registry.list()
        # Cada comando poderia ter um agente correspondente
        assert len(cmd_list) >= 14

    def test_plugin_manager_and_state_manager(self):
        initialize_core()
        c = Container.instance()
        pm = c.resolve('plugin_manager')
        sm = c.resolve('state_manager')

        ts_plugins = pm.list_ts_plugins()
        plugin_names = [p.meta.name for p in ts_plugins]

        # Persiste via state_manager
        sm.set('ts_plugins', plugin_names)
        restored = sm.get('ts_plugins', [])
        assert len(restored) >= 3
        assert "manus-evolve" in restored
        assert "ecosystem-sync" in restored

    def test_task_queue_and_command_registry(self):
        initialize_core()
        c = Container.instance()
        tq = c.resolve('task_queue')
        registry = c.resolve('command_registry')

        # Ambos funcionam independentemente
        assert hasattr(tq, 'enqueue')
        assert hasattr(tq, 'start')
        assert registry.count >= 14
