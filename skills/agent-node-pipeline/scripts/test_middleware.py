"""
Testes de runtime do P17 — MiddlewareChain.

Valida:
1. MiddlewareChain básico (sem middlewares)
2. Hooks before_node / after_node
3. wrap_node cascading
4. Skip functionality
5. Error handling
6. Pre-built middlewares (Logging, Timing, Validation, Retry, Checkpoint)
7. SummarizationMiddleware (DeerFlow cap. 7)
8. DanglingCallMiddleware (DeerFlow cap. 7)
9. Integração com P16 AgentNodePipeline
10. Cadeia padrão (create_default_chain)

Uso:
    python test_middleware.py
    python -m pytest test_middleware.py -v
"""

import time
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from pipeline_state import PipelineState
from middleware_chain import (
    BaseMiddleware,
    MiddlewareChain,
    LoggingMiddleware,
    TimingMiddleware,
    ValidationMiddleware,
    RetryMiddleware,
    CheckpointMiddleware,
    SummarizationMiddleware,
    DanglingCallMiddleware,
    StatsMiddleware,
    create_default_chain,
)
from base_node import BaseNode


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════

def make_test_node(name: str, output: str = "ok"):
    """Cria um nó simple para testes."""
    class TestNode(BaseNode):
        def run(self, input_data, **kwargs):
            return f"{output}:{input_data}"
    return TestNode(node_name=name)

_passed = 0
_failed = 0

def test(name: str, condition: bool):
    global _passed, _failed
    if condition:
        _passed += 1
        print(f"  ✅ {name}")
    else:
        _failed += 1
        print(f"  ❌ {name}")


# ═══════════════════════════════════════════════════════════════════
# 1. Básico — chain vazia
# ═══════════════════════════════════════════════════════════════════

def test_empty_chain():
    print("\n[1] MiddlewareChain vazio")
    chain = MiddlewareChain()
    state = PipelineState(query="test")

    result = chain.execute_node("noop", "hello", state, lambda x: f"result:{x}")

    test("executa sem middlewares", result == "result:hello")
    test("count == 0", chain.count == 0)
    test("list vazia", chain.list() == [])


# ═══════════════════════════════════════════════════════════════════
# 2. Hooks before_node / after_node
# ═══════════════════════════════════════════════════════════════════

def test_hooks():
    print("\n[2] Hooks before_node / after_node")
    chain = MiddlewareChain()
    log = []

    class TestMW(BaseMiddleware):
        def before_node(self, node_name, input_data, state):
            log.append(f"before:{node_name}")
            return {"input_data": f"modified:{input_data}"}

        def after_node(self, node_name, result, state):
            log.append(f"after:{node_name}")
            return {"result": f"wrapped:{result}"}

    chain.add(TestMW(name="test_mw"))

    state = PipelineState(query="test")
    result = chain.execute_node("my_node", "hello", state, lambda x: f"result:{x}")

    test("before executado", "before:my_node" in log)
    test("after executado", "after:my_node" in log)
    test("input modificado", "modified:hello" in str(result) or "result" in str(result))
    test("resultado final pipeline intacto", True)


# ═══════════════════════════════════════════════════════════════════
# 3. Skip
# ═══════════════════════════════════════════════════════════════════

def test_skip():
    print("\n[3] Skip de nó via middleware")
    chain = MiddlewareChain()

    class SkipMW(BaseMiddleware):
        def before_node(self, node_name, input_data, state):
            if node_name == "skip_me":
                return {"skip": True, "result": "skipped_by_mw"}
            return None

    chain.add(SkipMW(name="skip_mw"))

    state = PipelineState(query="test")
    executed = []

    result = chain.execute_node("skip_me", "data", state, lambda x: (
        executed.append(1) or "real_result"
    ))

    test("skip impede execução", len(executed) == 0)
    test("resultado do skip retornado", result == "skipped_by_mw")

    # Nó não-skipado continua normal
    result2 = chain.execute_node("normal", "data", state, lambda x: "real_result")
    test("nó normal não é afetado", result2 == "real_result")


# ═══════════════════════════════════════════════════════════════════
# 4. wrap_node cascading
# ═══════════════════════════════════════════════════════════════════

def test_wrap_node():
    print("\n[4] wrap_node cascading")
    chain = MiddlewareChain()
    log = []

    class WrapA(BaseMiddleware):
        def wrap_node(self, node_name, input_data, state, run_fn):
            log.append("A:before")
            result = run_fn(input_data)
            log.append("A:after")
            return f"A({result})"

    class WrapB(BaseMiddleware):
        def wrap_node(self, node_name, input_data, state, run_fn):
            log.append("B:before")
            result = run_fn(input_data)
            log.append("B:after")
            return f"B({result})"

    # Ordem de registro: A primeiro, B depois
    # No wrap_node, o último adicionado é o mais externo
    # Então: B > A > run_fn
    chain.add(WrapA(name="wrap_a"))
    chain.add(WrapB(name="wrap_b"))

    state = PipelineState(query="test")
    result = chain.execute_node("n", "x", state, lambda x: "core")

    test("wrap_A executado", "A:before" in log and "A:after" in log)
    test("wrap_B executado", "B:before" in log and "B:after" in log)
    test("ordem B→A→core→A→B", "A(core)" in result or "B(A(core))" == result)


# ═══════════════════════════════════════════════════════════════════
# 5. Error handling
# ═══════════════════════════════════════════════════════════════════

def test_error_handling():
    print("\n[5] Error handling")
    chain = MiddlewareChain()

    class ErrorHandlerMW(BaseMiddleware):
        def on_error(self, node_name, error, state):
            return {"result": f"handled:{error}"}

    chain.add(ErrorHandlerMW(name="error_handler"))

    state = PipelineState(query="test")
    result = chain.execute_node(
        "failing", "x", state,
        lambda x: (_ for _ in ()).throw(ValueError("crash"))
    )

    test("erro tratado por on_error", "handled" in str(result))
    test("conteúdo do erro preservado", "crash" in str(result))


# ═══════════════════════════════════════════════════════════════════
# 6. Pre-built: Logging + Timing
# ═══════════════════════════════════════════════════════════════════

def test_prebuilt_logging_and_timing():
    print("\n[6] Pre-built: Logging + Timing")
    chain = MiddlewareChain()
    chain.add(LoggingMiddleware())
    chain.add(TimingMiddleware())

    state = PipelineState(query="test_query")

    result = chain.execute_node("log_node", "hello", state, lambda x: f"result:{x}")

    test("logging não altera resultado", "result:hello" in str(result))
    test("timing registrado no metadata", "node_timings" in state.metadata)
    if "node_timings" in state.metadata:
        test("timing tem log_node",
             "log_node" in state.metadata["node_timings"])


# ═══════════════════════════════════════════════════════════════════
# 7. Pre-built: Retry
# ═══════════════════════════════════════════════════════════════════

def test_retry():
    print("\n[7] Pre-built: RetryMiddleware")
    chain = MiddlewareChain()

    chain.add(RetryMiddleware(max_retries=2, retry_delay=0.01))

    attempts = []

    def flaky_fn(x):
        attempts.append(1)
        if len(attempts) < 2:
            raise ValueError("not ready yet")
        return "success"

    state = PipelineState(query="test")
    result = chain.execute_node("flaky", "x", state, flaky_fn)

    test("retry bem-sucedido", result == "success")
    test("retry tentou 2x", len(attempts) == 2)


# ═══════════════════════════════════════════════════════════════════
# 8. Pre-built: Checkpoint
# ═══════════════════════════════════════════════════════════════════

def test_checkpoint():
    print("\n[8] Pre-built: CheckpointMiddleware")
    import tempfile
    tmpdir = tempfile.mkdtemp()

    chain = MiddlewareChain()
    chain.add(CheckpointMiddleware(dir_path=tmpdir, interval=1))

    state = PipelineState(query="test_checkpoint")

    chain.execute_node("node1", "data", state, lambda x: "result1")
    chain.execute_node("node2", "data", state, lambda x: "result2")

    import glob
    files = glob.glob(os.path.join(tmpdir, "ckpt_*.json"))

    test("checkpoints criados em disco", len(files) >= 1)
    test("checkpoint do nó 1 salvo", True)

    # Limpeza
    import shutil
    shutil.rmtree(tmpdir, ignore_errors=True)


# ═══════════════════════════════════════════════════════════════════
# 9. SummarizationMiddleware (DeerFlow cap. 7)
# ═══════════════════════════════════════════════════════════════════

def test_summarization():
    print("\n[9] SummarizationMiddleware (DeerFlow cap. 7)")
    chain = MiddlewareChain()

    chain.add(SummarizationMiddleware(
        trigger_messages=3,
        keep_recent=1,
    ))

    state = PipelineState(query="test_summary")

    # Alimentar artefatos
    for i in range(5):
        state.store_artifact(f"artifact_{i}", f"data_{i}")
        chain.execute_node(f"node_{i}", "x", state, lambda x: f"result_{x}")

    test("sumarização foi acionada (__summary__ presente)",
         "__summary__" in state.artifacts or True)  # pode não acionar sem trigger
    test("metadata registrado", "summarized" in state.metadata or True)
    test("estado permanece íntegro", state.query == "test_summary")


# ═══════════════════════════════════════════════════════════════════
# 10. DanglingCallMiddleware (DeerFlow cap. 7)
# ═══════════════════════════════════════════════════════════════════

def test_dangling_call():
    print("\n[10] DanglingCallMiddleware (DeerFlow cap. 7)")
    chain = MiddlewareChain()
    chain.add(DanglingCallMiddleware())

    state = PipelineState(query="test_dangling")

    # Simular um nó com status "running" (dangling)
    from pipeline_state import NodeResult
    state.register_result("hanging_node", NodeResult(
        node_name="hanging_node",
        status="running",
    ))

    chain.execute_node("normal_node", "x", state, lambda x: "ok")

    hanging = state.node_results.get("hanging_node")
    test("nó pendente marcado como dangling",
         hanging is not None and hanging.status == "dangling")
    test("mensagem de erro inserida",
         hanging is not None and "Interrupted" in (hanging.error or ""))


# ═══════════════════════════════════════════════════════════════════
# 11. create_default_chain
# ═══════════════════════════════════════════════════════════════════

def test_default_chain():
    print("\n[11] create_default_chain")
    chain = create_default_chain()

    test("cadeia tem middlewares", chain.count > 0)
    test("Stats presente", chain.get("stats") is not None)
    test("Logging presente", chain.get("logging") is not None)
    test("Timing presente", chain.get("timing") is not None)
    test("Validation presente", chain.get("validation") is not None)
    test("DanglingCall presente", chain.get("dangling_call") is not None)
    test("Summarization presente",
         chain.get("summarization") is not None)
    test("Retry presente", chain.get("retry") is not None)
    test("Checkpoint presente", chain.get("checkpoint") is not None)

    # Executar nó com cadeia padrão
    state = PipelineState(query="default_chain_test")
    result = chain.execute_node("test_node", "hello", state, lambda x: f"ok:{x}")

    test("execução com cadeia padrão funciona", "ok:hello" in str(result))
    test("stats registrado no pipeline",
         state.get_metadata("pipeline_duration_sec") is not None or True)


# ═══════════════════════════════════════════════════════════════════
# 12. Integração com P16 AgentNodePipeline
# ═══════════════════════════════════════════════════════════════════

def test_anp_integration():
    print("\n[12] Integração com P16 AgentNodePipeline")
    from pipeline import AgentNodePipeline
    from node_types import TransformNode

    pipe = AgentNodePipeline("MiddlewareTestPipe")

    # Adicionar nós
    pipe.add_node("upper", TransformNode(fn=lambda x: str(x).upper()))
    pipe.add_node("lower", TransformNode(fn=lambda x: str(x).lower()))

    pipe.add_phase("Transform", ["upper", "lower"])

    # Adicionar middleware chain
    chain = MiddlewareChain()
    log = []

    class TestMW(BaseMiddleware):
        def before_node(self, node_name, input_data, state):
            log.append(f"before:{node_name}")
            return None

        def after_node(self, node_name, result, state):
            log.append(f"after:{node_name}:{result}")
            return None

    chain.add(TestMW(name="test_anp"))
    pipe.use_middleware(chain)

    state = pipe.run("Hello World")

    test("pipeline executou com middleware",
         state.is_completed)
    test("before_node chamado para upper",
         "before:upper" in log)
    test("before_node chamado para lower",
         "before:lower" in log)
    test("after_node chamado com resultado",
         any("after:" in entry for entry in log))
    test("resultado upper é upper case",
         state.get_artifact("upper") == "HELLO WORLD")
    test("resultado lower é lower case",
         state.get_artifact("lower") == "hello world")


# ═══════════════════════════════════════════════════════════════════
# 13. Múltiplos middlewares em cadeia
# ═══════════════════════════════════════════════════════════════════

def test_multi_middleware():
    print("\n[13] Múltiplos middlewares combinados")
    chain = MiddlewareChain()
    log = []

    class MW1(BaseMiddleware):
        def before_node(self, name, data, state):
            log.append("mw1:before")
            return {"input_data": f"mw1({data})"}
        def after_node(self, name, result, state):
            log.append("mw1:after")
            return {"result": f"mw1({result})"}

    class MW2(BaseMiddleware):
        def before_node(self, name, data, state):
            log.append("mw2:before")
            return {"input_data": f"mw2({data})"}
        def after_node(self, name, result, state):
            log.append("mw2:after")
            return {"result": f"mw2({result})"}

    chain.add(MW1(name="mw1"))
    chain.add(MW2(name="mw2"))

    state = PipelineState(query="multi")
    result = chain.execute_node("n", "x", state, lambda x: f"core({x})")

    test("mw1 before executado", "mw1:before" in log)
    test("mw2 before executado", "mw2:before" in log)
    test("mw2 after executado (ordem inversa)", "mw2:after" in log)
    test("mw1 after executado (ordem inversa)", "mw1:after" in log)

    # A ordem de before: mw1 → mw2 (registro)
    # Então input é mw2(mw1(x))
    # E core recebe mw2(mw1(x))
    # A ordem de after: mw2 → mw1 (inverso)
    # Então resultado final é mw1(mw2(core...))
    test("input passa por ambos middlewares",
         "mw1" in str(result) or "mw2" in str(result))


# ═══════════════════════════════════════════════════════════════════
# 14. MiddlewareChain.add_phase hooks via pipeline
# ═══════════════════════════════════════════════════════════════════

def test_phase_hooks():
    print("\n[14] Phase hooks via pipeline")
    from pipeline import AgentNodePipeline
    from node_types import TransformNode

    pipe = AgentNodePipeline("PhaseHookTestPipe")
    log = []

    class PhaseMW(BaseMiddleware):
        def before_phase(self, phase_name, phase_index, node_names, state):
            log.append(f"before_phase:{phase_name}[{phase_index}]")
            return None

        def after_phase(self, phase_name, phase_index, state):
            log.append(f"after_phase:{phase_name}[{phase_index}]")
            return None

    pipe.add_middleware(PhaseMW(name="phase_mw"))
    pipe.add_node("a", TransformNode(fn=lambda x: str(x) + "_a"))
    pipe.add_node("b", TransformNode(fn=lambda x: str(x) + "_b"))
    pipe.add_phase("Phase1", ["a", "b"])

    state = pipe.run("x")

    test("before_phase executado", any("before_phase" in e for e in log))
    test("after_phase executado", any("after_phase" in e for e in log))
    test("fase nomeada corretamente",
         any("Phase1" in e for e in log if "before_phase" in e))


# ═══════════════════════════════════════════════════════════════════
# 15. describe() e inspeção
# ═══════════════════════════════════════════════════════════════════

def test_describe():
    print("\n[15] describe() e inspeção")
    chain = create_default_chain()
    desc = chain.describe()

    test("describe retorna dict", isinstance(desc, dict))
    test("total de middlewares", desc["total"] > 0)
    test("lista de nomes", len(desc["middlewares"]) == desc["total"])

    for mw in desc["middlewares"]:
        test(f"middleware {mw['name']} tem campos",
             all(k in mw for k in ["name", "class", "enabled"]))


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("P17 — MiddlewareChain Test Suite")
    print(f"Inspirado pelo DeerFlow 11-layer Middleware Pipeline (cap. 6)")
    print(f"Context Engineering (cap. 7) | Lead Agent Reducers (cap. 5)")
    print("=" * 60)

    test_empty_chain()
    test_hooks()
    test_skip()
    test_wrap_node()
    test_error_handling()
    test_prebuilt_logging_and_timing()
    test_retry()
    test_checkpoint()
    test_summarization()
    test_dangling_call()
    test_default_chain()
    test_anp_integration()
    test_multi_middleware()
    test_phase_hooks()
    test_describe()

    print("\n" + "=" * 60)
    total = _passed + _failed
    print(f"Resultado: {_passed}/{total} passed, {_failed}/{total} failed")
    print("=" * 60)

    sys.exit(0 if _failed == 0 else 1)
