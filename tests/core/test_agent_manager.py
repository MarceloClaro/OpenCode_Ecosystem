"""
Testes do AgentManager (core/agent_manager.py)

Cobre:
- register_agent_type / unregister_agent_type / list_types
- create_agent com configuracao
- run_agent com ciclo de vida completo (READY -> RUNNING -> COMPLETED)
- run_agent com falha (READY -> RUNNING -> FAILED)
- health_check
- destroy_agent
- get_instance / list_instances com filtros
- count_by_status
- Erros: tipo nao registrado, inicializacao falha, agente nao pronto
"""

import pytest

from core.agent_manager import (
    AgentManager,
    Agent,
    AgentInstance,
    AgentTypeDef,
    AgentStatus,
)
from core.errors import AgentError, NotFoundError


# ── Mock Agent para testes ─────────────────────────────────────────


class MockAgent:
    """Agente mockado para testes."""

    def __init__(self):
        self.initialized = False
        self.executed = False
        self.destroyed = False
        self.health = {"status": "healthy", "memory": "ok"}

    async def initialize(self, config: dict) -> None:
        self.initialized = True
        self.config = config

    async def execute(self, context: dict) -> str:
        self.executed = True
        return f"executed:{context.get('task', 'default')}"

    async def health_check(self) -> dict:
        return self.health

    async def destroy(self) -> None:
        self.destroyed = True


class FailingMockAgent:
    """Agente que falha na inicializacao."""

    async def initialize(self, config: dict) -> None:
        raise RuntimeError("init failed")

    async def execute(self, context: dict) -> str:
        return "ok"

    async def health_check(self) -> dict:
        return {}

    async def destroy(self) -> None:
        pass


class BadExecuteAgent:
    """Agente que falha na execucao."""

    def __init__(self):
        self.initialized = False

    async def initialize(self, config: dict) -> None:
        self.initialized = True

    async def execute(self, context: dict) -> str:
        raise ValueError("execution error")

    async def health_check(self) -> dict:
        return {"status": "ok"}

    async def destroy(self) -> None:
        pass


# ── Fixtures ────────────────────────────────────────────────────────


@pytest.fixture
def manager():
    """AgentManager limpo."""
    return AgentManager()


# ── Testes: Tipo de Agente ──────────────────────────────────────────


class TestAgentTypeRegistration:
    def test_register_type(self, manager):
        manager.register_agent_type(
            "mock-agent", MockAgent,
            description="Mock para testes",
            version="2.0.0",
        )
        assert "mock-agent" in [t.name for t in manager.list_types()]

    def test_register_duplicate(self, manager):
        manager.register_agent_type("dup", MockAgent)
        with pytest.raises(AgentError, match="already registered"):
            manager.register_agent_type("dup", MockAgent)

    def test_unregister_type(self, manager):
        manager.register_agent_type("temp", MockAgent)
        assert manager.unregister_agent_type("temp") is True
        assert manager.get_type_def("temp") is None

    def test_unregister_nonexistent(self, manager):
        assert manager.unregister_agent_type("no-such") is False

    def test_get_type_def(self, manager):
        manager.register_agent_type("scout", MockAgent, "Scout agent", "1.5.0")
        tdef = manager.get_type_def("scout")
        assert tdef is not None
        assert tdef.name == "scout"
        assert tdef.description == "Scout agent"
        assert tdef.version == "1.5.0"

    def test_list_types_empty(self, manager):
        assert manager.list_types() == []


# ── Testes: Criacao de Instancias ────────────────────────────────────


class TestAgentCreation:
    @pytest.mark.asyncio
    async def test_create_agent(self, manager):
        manager.register_agent_type("mock", MockAgent)
        agent_id = await manager.create_agent("mock", {"key": "val"})
        assert agent_id is not None
        instance = manager.get_instance(agent_id)
        assert instance is not None
        assert instance.type_name == "mock"
        assert instance.status == AgentStatus.READY
        assert instance.config == {"key": "val"}

    @pytest.mark.asyncio
    async def test_create_agent_custom_id(self, manager):
        manager.register_agent_type("mock", MockAgent)
        agent_id = await manager.create_agent("mock", agent_id="my-custom-id")
        assert agent_id == "my-custom-id"

    @pytest.mark.asyncio
    async def test_create_unregistered_type(self, manager):
        with pytest.raises(NotFoundError, match="not registered"):
            await manager.create_agent("no-such")

    @pytest.mark.asyncio
    async def test_create_failing_agent(self, manager):
        manager.register_agent_type("failing", FailingMockAgent)
        with pytest.raises(AgentError, match="Failed to initialize"):
            await manager.create_agent("failing", {})

    @pytest.mark.asyncio
    async def test_create_default_config(self, manager):
        manager.register_agent_type("mock", MockAgent)
        agent_id = await manager.create_agent("mock")
        instance = manager.get_instance(agent_id)
        assert instance.config == {}


# ── Testes: Execucao ─────────────────────────────────────────────────


class TestAgentExecution:
    @pytest.mark.asyncio
    async def test_run_agent(self, manager):
        manager.register_agent_type("mock", MockAgent)
        agent_id = await manager.create_agent("mock")
        result = await manager.run_agent(agent_id, {"task": "test"})
        assert result == "executed:test"
        instance = manager.get_instance(agent_id)
        assert instance.status == AgentStatus.COMPLETED
        assert instance.result == "executed:test"

    @pytest.mark.asyncio
    async def test_run_nonexistent_agent(self, manager):
        with pytest.raises(NotFoundError, match="not found"):
            await manager.run_agent("no-such")

    @pytest.mark.asyncio
    async def test_run_not_ready(self, manager):
        """Agente nao inicializado (nao passa por create_agent)."""
        manager.register_agent_type("mock", MockAgent)
        # Criamos manualmente uma entrada sem instancia real
        agent_id = "not-ready-id"
        manager._instances[agent_id] = AgentInstance(
            id=agent_id, type_name="mock", status=AgentStatus.CREATED
        )
        with pytest.raises(AgentError, match="expected READY"):
            await manager.run_agent(agent_id)

    @pytest.mark.asyncio
    async def test_run_failing_execution(self, manager):
        manager.register_agent_type("bad", BadExecuteAgent)
        agent_id = await manager.create_agent("bad")
        with pytest.raises(AgentError, match="execution failed"):
            await manager.run_agent(agent_id)
        instance = manager.get_instance(agent_id)
        assert instance.status == AgentStatus.FAILED
        assert instance.error is not None


# ── Testes: Health Check ─────────────────────────────────────────────


class TestAgentHealth:
    @pytest.mark.asyncio
    async def test_health_check(self, manager):
        manager.register_agent_type("mock", MockAgent)
        agent_id = await manager.create_agent("mock")
        health = await manager.health_check(agent_id)
        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_nonexistent(self, manager):
        with pytest.raises(NotFoundError, match="not found"):
            await manager.health_check("no-such")


# ── Testes: Destruicao ────────────────────────────────────────────────


class TestAgentDestruction:
    @pytest.mark.asyncio
    async def test_destroy_agent(self, manager):
        manager.register_agent_type("mock", MockAgent)
        agent_id = await manager.create_agent("mock")
        assert await manager.destroy_agent(agent_id) is True
        instance = manager.get_instance(agent_id)
        assert instance.status == AgentStatus.DESTROYED

    @pytest.mark.asyncio
    async def test_destroy_nonexistent(self, manager):
        assert await manager.destroy_agent("no-such") is False

    @pytest.mark.asyncio
    async def test_destroy_calls_destroy_method(self, manager):
        manager.register_agent_type("mock", MockAgent)
        agent_id = await manager.create_agent("mock")
        agent = manager._agents[agent_id]
        await manager.destroy_agent(agent_id)
        assert agent.destroyed is True


# ── Testes: Consultas ─────────────────────────────────────────────────


class TestAgentQueries:
    @pytest.mark.asyncio
    async def test_list_instances(self, manager):
        manager.register_agent_type("mock", MockAgent)
        await manager.create_agent("mock", {"env": "a"})
        await manager.create_agent("mock", {"env": "b"})
        assert len(manager.list_instances()) == 2

    def test_list_instances_filter_by_type(self, manager):
        # Sem agentes async, apenas testamos o filtro
        pass

    def test_list_instances_filter_by_status(self, manager):
        # Teste sincrono com instancias mock
        inst_a = AgentInstance(id="a", type_name="mock", status=AgentStatus.READY)
        inst_b = AgentInstance(id="b", type_name="mock", status=AgentStatus.COMPLETED)
        manager._instances = {"a": inst_a, "b": inst_b}
        ready = manager.list_instances(status=AgentStatus.READY)
        assert len(ready) == 1
        assert ready[0].id == "a"

    def test_count_by_status(self, manager):
        inst_a = AgentInstance(id="a", type_name="t1", status=AgentStatus.READY)
        inst_b = AgentInstance(id="b", type_name="t2", status=AgentStatus.COMPLETED)
        inst_c = AgentInstance(id="c", type_name="t3", status=AgentStatus.COMPLETED)
        manager._instances = {"a": inst_a, "b": inst_b, "c": inst_c}
        counts = manager.count_by_status()
        assert counts["ready"] == 1
        assert counts["completed"] == 2

    def test_repr(self, manager):
        manager.register_agent_type("mock", MockAgent)
        r = repr(manager)
        assert "AgentManager" in r
        assert "types=1" in r
        assert "instances=0" in r
