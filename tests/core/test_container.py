"""
Testes do Container de DI (core/container.py)

Cobre:
- Singleton: instance() sempre retorna o mesmo objeto
- register + resolve: registro e resolucao direta
- register_factory: fabrica lazy (so instancia na primeira resolve)
- is_registered / registered(): introspeccao
- reset(): limpeza total
- ServiceNotFoundError: erro para servico inexistente
- Thread safety: Lock protege acesso concorrente
"""

import threading
from typing import Any

import pytest

from core.container import Container, ContainerError, ServiceNotFoundError


@pytest.fixture(autouse=True)
def reset_container():
    """Garante container limpo antes e depois de cada teste."""
    Container.instance().reset()
    yield
    Container.instance().reset()


# ─── Singleton ───────────────────────────────────────────────────────

class TestContainerSingleton:
    def test_instance_returns_same_object(self):
        c1 = Container.instance()
        c2 = Container.instance()
        assert c1 is c2, "instance() deve retornar sempre o mesmo objeto"

    def test_different_containers_are_different(self):
        c1 = Container()
        c2 = Container()
        assert c1 is not c2, "Construtores diretos devem gerar objetos diferentes"


# ─── Register / Resolve ───────────────────────────────────────────────

class TestRegisterResolve:
    def test_register_and_resolve(self):
        container = Container.instance()
        container.register('db', {'conn': 'sqlite'})
        assert container.resolve('db') == {'conn': 'sqlite'}

    def test_resolve_nonexistent_raises(self):
        container = Container.instance()
        with pytest.raises(ServiceNotFoundError):
            container.resolve('nobody_home')

    def test_register_overwrites_existing(self):
        container = Container.instance()
        container.register('x', 1)
        container.register('x', 2)
        assert container.resolve('x') == 2

    def test_register_after_factory_removes_factory(self):
        container = Container.instance()
        container.register_factory('x', lambda: 42)
        container.register('x', 99)
        assert container.resolve('x') == 99
        assert 'x' not in container._factories

    def test_resolve_preserves_reference(self):
        """Objeto resolvido deve ser o mesmo (singleton do servico)."""
        container = Container.instance()
        obj = {'counter': 0}
        container.register('obj', obj)
        resolved = container.resolve('obj')
        resolved['counter'] += 1
        assert container.resolve('obj')['counter'] == 1


# ─── Factory ─────────────────────────────────────────────────────────

class TestFactory:
    def test_factory_is_lazy(self):
        """Factory so deve ser chamada na primeira resolve."""
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return {'created': True}

        container = Container.instance()
        container.register_factory('lazy', factory)
        assert call_count == 0, "Factory nao deve ser chamada no registro"

        obj1 = container.resolve('lazy')
        assert call_count == 1, "Factory deve ser chamada na 1a resolve"
        assert obj1['created'] is True

        obj2 = container.resolve('lazy')
        assert call_count == 1, "Factory nao deve ser chamada de novo (cache)"
        assert obj1 is obj2, "Cache deve retornar mesmo objeto"

    def test_factory_error_bubbles(self):
        """Erro dentro da factory deve propagar."""
        container = Container.instance()

        def broken():
            raise ValueError("factory exploded")

        container.register_factory('broken', broken)
        with pytest.raises(ValueError, match="factory exploded"):
            container.resolve('broken')

    def test_factory_replaced_by_register(self):
        container = Container.instance()
        container.register_factory('x', lambda: 10)
        container.register('x', 20)
        assert container.resolve('x') == 20
        assert container._factories.get('x') is None


# ─── Introspeccao ────────────────────────────────────────────────────

class TestIntrospection:
    def test_is_registered_true(self):
        container = Container.instance()
        container.register('a', 1)
        assert container.is_registered('a') is True

    def test_is_registered_false(self):
        container = Container.instance()
        assert container.is_registered('ghost') is False

    def test_is_registered_factory(self):
        container = Container.instance()
        container.register_factory('f', lambda: 2)
        assert container.is_registered('f') is True

    def test_registered_list(self):
        container = Container.instance()
        container.register('a', 1)
        container.register_factory('b', lambda: 2)
        names = container.registered()
        assert 'a' in names
        assert 'b' in names

    def test_registered_after_resolve_factory(self):
        """Factory resolvida vira servico - registered() reflete isso."""
        container = Container.instance()
        container.register_factory('f', lambda: 42)
        container.resolve('f')
        names = container.registered()
        assert 'f' in names


# ─── Reset ──────────────────────────────────────────────────────────

class TestReset:
    def test_reset_clears_all(self):
        container = Container.instance()
        container.register('a', 1)
        container.register_factory('b', lambda: 2)
        container.reset()
        assert container.registered() == []
        assert container.is_registered('a') is False
        assert container.is_registered('b') is False

    def test_reset_allows_reregister(self):
        container = Container.instance()
        container.register('x', 1)
        container.reset()
        container.register('x', 2)
        assert container.resolve('x') == 2

    def test_reset_does_not_break_singleton(self):
        c1 = Container.instance()
        c1.register('k', 'v')
        c1.reset()
        c2 = Container.instance()
        assert c1 is c2
        assert c2.registered() == []


# ─── Error Handling ──────────────────────────────────────────────────

class TestErrors:
    def test_service_not_found_message(self):
        container = Container.instance()
        with pytest.raises(ServiceNotFoundError) as exc_info:
            container.resolve('missing')
        assert 'missing' in str(exc_info.value)

    def test_container_error_is_exception(self):
        assert issubclass(ServiceNotFoundError, ContainerError)
        assert issubclass(ContainerError, Exception)


# ─── Thread Safety ───────────────────────────────────────────────────

class TestThreadSafety:
    def test_concurrent_register_resolve(self):
        """
        Registros concorrentes nao devem corromper o estado interno.
        """
        container = Container.instance()
        n_threads = 20
        results: list[bool] = []
        lock = threading.Lock()

        def worker(i: int):
            try:
                container.register(f'k{i}', i)
                val = container.resolve(f'k{i}')
                assert val == i, f"Esperado {i}, obtido {val}"
                with lock:
                    results.append(True)
            except Exception:
                with lock:
                    results.append(False)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(n_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert all(results), "Todos os acessos concorrentes devem ser bem-sucedidos"
        assert len(container.registered()) == n_threads
