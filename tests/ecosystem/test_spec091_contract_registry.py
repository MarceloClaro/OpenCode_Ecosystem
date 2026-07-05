"""
Testes TDD para SPEC-091: Module Contract Registry.

Valida:
- CT-9101: ContractRegistry aceita registros
- CT-9102: get() retorna contrato por nome
- CT-9103: implementations_of() lista implementações
- CT-9104: IAgent com métodos abstratos
- CT-9105: IScanner com métodos abstratos
- CT-9106: verify_all() verifica aderência
- CT-9107: IAdapter definido
- CT-9108: snapshot() serializa
- CT-9109: export_graph() gera dependências
- CT-9110: Teste de contrato — implementação inválida é rejeitada
"""

import pytest
from ecosystem.contracts.registry import (
    ContractRegistry,
    ContractEntry,
    ContractStatus,
    ContractNotFoundError,
    ContractError,
)
from ecosystem.contracts.interfaces import (
    IStateManager,
    IAgent,
    IScanner,
    IAdapter,
    IEventBus,
    ICache,
    ITaskQueue,
    IPlugin,
    IPipeline,
)


@pytest.fixture
def registry():
    """Fixture: ContractRegistry vazio."""
    return ContractRegistry()


@pytest.fixture
def populated_registry(registry):
    """Fixture: ContractRegistry com contratos registrados."""
    registry.register(ContractEntry(
        name="IStateManager",
        interface_type="IStateManager",
        module_path="ecosystem/contracts/interfaces/istate_manager.py",
        implementations=["core/state.py", "core/state_file.py", "core/state_manager.py"],
        version="1.0.0",
        status=ContractStatus.STABLE,
        description="Gerenciamento de estado persistente",
    ))
    registry.register(ContractEntry(
        name="IAgent",
        interface_type="IAgent",
        module_path="ecosystem/contracts/interfaces/iagent.py",
        implementations=[],
        version="1.0.0",
        status=ContractStatus.DRAFT,
        description="Interface base para agentes",
    ))
    return registry


# === CT-9101: ContractRegistry aceita registros ===
class TestRegistration:
    def test_ct9101_register_accepts_entry(self, registry):
        """CT-9101: register() aceita ContractEntry."""
        entry = ContractEntry(
            name="ITest",
            interface_type="ITest",
            module_path="test.py",
            implementations=["test_impl.py"],
        )
        registry.register(entry)
        assert registry.count() == 1

    def test_ct9101_register_duplicate_raises(self, registry):
        """CT-9101b: register() duplicado lança erro."""
        entry = ContractEntry(
            name="ITest", interface_type="ITest", module_path="test.py"
        )
        registry.register(entry)
        with pytest.raises(ContractError):
            registry.register(entry)


# === CT-9102: get() retorna contrato por nome ===
class TestGet:
    def test_ct9102_get_by_name(self, populated_registry):
        """CT-9102: get() retorna ContractEntry."""
        entry = populated_registry.get("IStateManager")
        assert isinstance(entry, ContractEntry)
        assert entry.name == "IStateManager"

    def test_ct9102_get_not_found_raises(self, registry):
        """CT-9102b: get() para nome inexistente lança erro."""
        with pytest.raises(ContractNotFoundError):
            registry.get("INaoExiste")


# === CT-9103: implementations_of() ===
class TestImplementations:
    def test_ct9103_implementations_listed(self, populated_registry):
        """CT-9103: implementations_of() retorna lista."""
        impls = populated_registry.implementations_of("IStateManager")
        assert len(impls) == 3
        assert "core/state.py" in impls

    def test_ct9103_empty_implementation(self, populated_registry):
        """CT-9103b: implementation vazia retorna lista vazia."""
        impls = populated_registry.implementations_of("IAgent")
        assert impls == []


# === CT-9104: IAgent com métodos abstratos ===
class TestIAgentContract:
    def test_ct9104_iagent_has_abstract_methods(self):
        """CT-9104: IAgent define initialize, execute, health_check."""
        import inspect
        methods = [
            name for name, method in inspect.getmembers(
                IAgent, predicate=inspect.isfunction
            )
        ]
        assert "initialize" in methods
        assert "execute" in methods
        assert "health_check" in methods


# === CT-9105: IScanner com métodos abstratos ===
class TestIScannerContract:
    def test_ct9105_iscanner_has_abstract_methods(self):
        """CT-9105: IScanner define scan, analyze, report."""
        import inspect
        methods = [
            name for name, method in inspect.getmembers(
                IScanner, predicate=inspect.isfunction
            )
        ]
        assert "scan" in methods
        assert "analyze" in methods
        assert "report" in methods


# === CT-9106: verify_all() ===
class TestVerify:
    def test_ct9106_verify_all_returns_dict(self, populated_registry):
        """CT-9106: verify_all() retorna dict com resultados."""
        results = populated_registry.verify_all()
        assert isinstance(results, dict)
        assert "IStateManager" in results

    def test_ct9106_verify_complete_contract(self, populated_registry):
        """CT-9106b: Contrato completo passa verificação."""
        results = populated_registry.verify_all()
        assert results["IStateManager"] is True


# === CT-9107: IAdapter definido ===
class TestIAdapterContract:
    def test_ct9107_iadapter_has_methods(self):
        """CT-9107: IAdapter define can_handle, execute, describe."""
        import inspect
        methods = [
            name for name, method in inspect.getmembers(
                IAdapter, predicate=inspect.isfunction
            )
        ]
        assert "can_handle" in methods
        assert "execute" in methods
        assert "describe" in methods


# === CT-9108: snapshot() ===
class TestSnapshot:
    def test_ct9108_snapshot_serializes(self, populated_registry):
        """CT-9108: snapshot() retorna dict com metadados."""
        snap = populated_registry.snapshot()
        assert "registry_version" in snap
        assert "total_contracts" in snap
        assert "contracts" in snap
        assert snap["total_contracts"] == 2

    def test_ct9108_to_json(self, populated_registry):
        """CT-9108b: to_json() retorna string JSON."""
        json_str = populated_registry.to_json()
        assert isinstance(json_str, str)
        assert "IStateManager" in json_str


# === CT-9109: export_graph() ===
class TestExportGraph:
    def test_ct9109_export_graph_structure(self, populated_registry):
        """CT-9109: export_graph() gera grafo com nós e arestas."""
        graph = populated_registry.export_graph()
        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) >= 4  # 2 contratos + 3 implementações


# === CT-9110: Teste de contrato — implementação inválida é rejeitada ===
class TestContractAdherence:
    def test_ct9110_incomplete_implementation_raises_typeerror(self):
        """CT-9110: Implementação parcial de IStateManager levanta TypeError."""
        # Cria implementação que omite métodos obrigatórios
        class IncompleteStateManager(IStateManager):
            def get(self, key: str) -> str:
                return "mock"
            # Omite: set, delete, keys, exists, close

        with pytest.raises(TypeError):
            IncompleteStateManager()

    def test_ct9110_complete_implementation_instantiates(self):
        """CT-9110b: Implementação completa de IStateManager instancia."""
        class CompleteStateManager(IStateManager):
            def get(self, key: str) -> str:
                return "mock"
            def set(self, key: str, value: str) -> None:
                pass
            def delete(self, key: str) -> bool:
                return True
            def keys(self) -> list[str]:
                return []
            def exists(self, key: str) -> bool:
                return True
            def close(self) -> None:
                pass

        obj = CompleteStateManager()
        assert isinstance(obj, IStateManager)
