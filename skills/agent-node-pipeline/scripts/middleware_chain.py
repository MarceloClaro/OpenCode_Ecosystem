"""
MiddlewareChain — Cadeia de middlewares para o pipeline ANP (P17).

Inspirado pelo DeerFlow 11-layer Middleware Pipeline (ByteDance).
Cada middleware implementa hooks que envolvem a execução de nós,
fases e do pipeline completo.

Hooks disponíveis (adaptados do DeerFlow):
  before_node / after_node   → envolve cada nó
  before_phase / after_phase → envolve cada fase
  wrap_node                  → substitui completamente a execução de um nó
  on_error                   → tratamento de erros

Hooks DeerFlow equivalentes:
  before_agent  → before_node (execução do nó)
  after_agent   → after_node
  before_model  → before_node (específico para LLM)
  after_model   → after_node
  wrap_model_call  → wrap_node (substitui chamada)
  wrap_tool_call   → tratado como middleware específico

Pre-built middlewares:
  ✅ LoggingMiddleware      — loga execução de nós
  ✅ TimingMiddleware       — mede e registra duração
  ✅ ValidationMiddleware   — valida entradas/saídas
  ✅ RetryMiddleware        — retenta em caso de falha
  ✅ CheckpointMiddleware   — checkpoint automático
  ✅ SummarizationMiddleware — sumarização automática (DeerFlow cap. 7)
  ✅ DanglingCallMiddleware  — repara chamadas pendentes (DeerFlow cap. 7)
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type
from datetime import datetime
import time
import logging
import traceback

try:
    from .pipeline_state import PipelineState, NodeResult
except ImportError:
    from pipeline_state import PipelineState, NodeResult


# ═══════════════════════════════════════════════════════════════════
# BaseMiddleware
# ═══════════════════════════════════════════════════════════════════

class BaseMiddleware(ABC):
    """Middleware abstrato com 6 hooks para o pipeline ANP.

    Cada hook retorna None (sem modificação) ou um dicionário com
    as modificações a serem aplicadas pelo MiddlewareChain.

    Atributo de classe:
        enabled: Se True, este middleware é executado. Pode ser
                 desativado dinamicamente.
    """

    enabled: bool = True
    name: str = ""

    def __init__(self, name: str = ""):
        self.name = name or self.__class__.__name__

    # ── Hooks principais ────────────────────────────────────────────

    def before_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        """Executado antes de cada nó.

        Args:
            node_name: Nome do nó que será executado.
            input_data: Dados de entrada do nó.
            state: Estado atual do pipeline.

        Returns:
            None (sem modificação) ou dict com:
            - "input_data": dados de entrada modificados
            - "state": estado modificado (não usual)
            - "skip": True para pular este nó (com resultado opcional em "result")
            - "result": resultado pré-definido (se skip=True)
        """
        return None

    def after_node(
        self,
        node_name: str,
        result: Any,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        """Executado após cada nó.

        Args:
            node_name: Nome do nó executado.
            result: Resultado produzido pelo nó.
            state: Estado atual do pipeline.

        Returns:
            None (sem modificação) ou dict com:
            - "result": resultado modificado
            - "state": estado modificado
        """
        return None

    def before_phase(
        self,
        phase_name: str,
        phase_index: int,
        node_names: List[str],
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        """Executado antes de cada fase."""
        return None

    def after_phase(
        self,
        phase_name: str,
        phase_index: int,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        """Executado após cada fase."""
        return None

    def wrap_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
        run_fn: Callable[[Any], Any],
    ) -> Any:
        """Wrapper completo em torno da execução de um nó.

        Permite que o middleware substitua completamente como um nó
        é executado. Equivalente ao wrap_model_call do DeerFlow.

        Args:
            node_name: Nome do nó.
            input_data: Dados de entrada.
            state: Estado do pipeline.
            run_fn: Função que executa o nó (recebe input_data, retorna resultado).

        Returns:
            Resultado da execução (potencialmente modificado).
        """
        return run_fn(input_data)

    def on_error(
        self,
        node_name: str,
        error: Exception,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        """Tratamento de erro na execução de um nó.

        Returns:
            None (propaga erro) ou dict com:
            - "result": resultado de fallback (erro será suprimido)
            - "retry": True para retentar (se combinado com RetryMiddleware)
        """
        return None

    # ── Hooks do pipeline completo ──────────────────────────────────

    def before_run(
        self,
        query: str,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        """Executado antes de toda a execução do pipeline."""
        return None

    def after_run(
        self,
        state: PipelineState,
    ) -> None:
        """Executado após toda a execução do pipeline."""
        pass


# ═══════════════════════════════════════════════════════════════════
# MiddlewareChain
# ═══════════════════════════════════════════════════════════════════

class MiddlewareChain:
    """Cadeia ordenada de middlewares.

    Orquestra a execução sequencial dos hooks de cada middleware,
    na ordem em que foram registrados.

    Uso:
        chain = MiddlewareChain()
        chain.add(LoggingMiddleware())
        chain.add(TimingMiddleware())
        chain.add(RetryMiddleware(max_retries=2))

        # Executar nó com middlewares
        result = chain.execute_node("busca", input_data, state, run_fn)
    """

    def __init__(self):
        self._middlewares: List[BaseMiddleware] = []

    # ── Registro ───────────────────────────────────────────────────

    def add(self, middleware: BaseMiddleware) -> "MiddlewareChain":
        """Adiciona um middleware ao final da cadeia.

        Args:
            middleware: Instância de BaseMiddleware.

        Returns:
            self para encadeamento.
        """
        if not isinstance(middleware, BaseMiddleware):
            raise TypeError(
                f"Esperado BaseMiddleware, recebido {type(middleware).__name__}"
            )
        self._middlewares.append(middleware)
        return self

    def insert(self, index: int, middleware: BaseMiddleware) -> "MiddlewareChain":
        """Insere um middleware em posição específica.

        Args:
            index: Índice de inserção (0 = primeiro).
            middleware: Instância de BaseMiddleware.

        Returns:
            self para encadeamento.
        """
        self._middlewares.insert(index, middleware)
        return self

    def remove(self, name: str) -> bool:
        """Remove um middleware pelo nome.

        Returns:
            True se encontrado e removido, False caso contrário.
        """
        for i, m in enumerate(self._middlewares):
            if m.name == name:
                self._middlewares.pop(i)
                return True
        return False

    def get(self, name: str) -> Optional[BaseMiddleware]:
        """Busca um middleware pelo nome."""
        for m in self._middlewares:
            if m.name == name:
                return m
        return None

    def clear(self):
        """Remove todos os middlewares."""
        self._middlewares.clear()

    @property
    def count(self) -> int:
        return len(self._middlewares)

    def list(self) -> List[Dict[str, Any]]:
        """Lista todos os middlewares registrados."""
        return [
            {
                "name": m.name,
                "class": m.__class__.__name__,
                "enabled": m.enabled,
            }
            for m in self._middlewares
        ]

    # ── Execução de hooks ──────────────────────────────────────────

    def execute_before_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
    ) -> tuple[Any, PipelineState, bool, Any]:
        """Executa before_node de todos os middlewares.

        Returns:
            (input_data_modificado, state_modificado, skip, skip_result)
        """
        modified_input = input_data
        modified_state = state
        skip = False
        skip_result = None

        for mw in self._middlewares:
            if not mw.enabled:
                continue
            try:
                result = mw.before_node(node_name, modified_input, modified_state)
                if result is not None:
                    if "input_data" in result:
                        modified_input = result["input_data"]
                    if "state" in result:
                        modified_state = result["state"]
                    if result.get("skip"):
                        skip = True
                        skip_result = result.get("result")
                        break  # skip propaga, não executa mais middlewares
            except Exception as e:
                logging.warning(
                    "Middleware '%s'.before_node falhou: %s", mw.name, e
                )

        return modified_input, modified_state, skip, skip_result

    def execute_after_node(
        self,
        node_name: str,
        result: Any,
        state: PipelineState,
    ) -> Any:
        """Executa after_node de todos os middlewares (ordem inversa)."""
        modified_result = result
        modified_state = state

        for mw in reversed(self._middlewares):
            if not mw.enabled:
                continue
            try:
                r = mw.after_node(node_name, modified_result, modified_state)
                if r is not None:
                    if "result" in r:
                        modified_result = r["result"]
                    if "state" in r:
                        modified_state = r["state"]
            except Exception as e:
                logging.warning(
                    "Middleware '%s'.after_node falhou: %s", mw.name, e
                )

        return modified_result

    def execute_wrap_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
        run_fn: Callable[[Any], Any],
    ) -> Any:
        """Executa a cadeia de wrap_node (casca de cebola).

        O último middleware a ser adicionado é o mais externo,
        ou seja, o primeiro a envolver a chamada.

        Isto replica o padrão do DeerFlow onde middlewares como
        ClarificationMiddleware (último) envolvem todos os outros.
        """
        # Construir cadeia de wrappers (casca de cebola)
        wrappers = [m for m in self._middlewares if m.enabled]

        if not wrappers:
            return run_fn(input_data)

        # DeerFlow semantics: o último middleware adicionado é o mais externo
        # (primeiro a envolver a chamada). Iteramos na ordem de registro,
        # então A (primeiro) envolve run_fn, e B (último) envolve A-wrapper.
        # Resultado: B(A(run_fn)), ou seja, B é o mais externo.
        chain_fn = run_fn
        for mw in wrappers:
            current_chain = chain_fn
            def make_wrapper(mw_obj, next_fn):
                def wrapper(data):
                    return mw_obj.wrap_node(node_name, data, state, next_fn)
                return wrapper
            chain_fn = make_wrapper(mw, chain_fn)

        return chain_fn(input_data)

    def execute_before_phase(
        self,
        phase_name: str,
        phase_index: int,
        node_names: List[str],
        state: PipelineState,
    ) -> PipelineState:
        modified_state = state
        for mw in self._middlewares:
            if not mw.enabled:
                continue
            try:
                r = mw.before_phase(phase_name, phase_index, node_names, modified_state)
                if r is not None and "state" in r:
                    modified_state = r["state"]
            except Exception as e:
                logging.warning(
                    "Middleware '%s'.before_phase falhou: %s", mw.name, e
                )
        return modified_state

    def execute_after_phase(
        self,
        phase_name: str,
        phase_index: int,
        state: PipelineState,
    ) -> PipelineState:
        modified_state = state
        for mw in self._middlewares:
            if not mw.enabled:
                continue
            try:
                r = mw.after_phase(phase_name, phase_index, modified_state)
                if r is not None and "state" in r:
                    modified_state = r["state"]
            except Exception as e:
                logging.warning(
                    "Middleware '%s'.after_phase falhou: %s", mw.name, e
                )
        return modified_state

    def execute_on_error(
        self,
        node_name: str,
        error: Exception,
        state: PipelineState,
    ) -> tuple[bool, Optional[Any]]:
        """Executa on_error de todos os middlewares.

        Returns:
            (handled, fallback_result) — handled=True se algum middleware
            tratou o erro (retornou result), False caso contrário.
        """
        for mw in self._middlewares:
            if not mw.enabled:
                continue
            try:
                r = mw.on_error(node_name, error, state)
                if r is not None:
                    if "result" in r:
                        return True, r["result"]
                    if r.get("retry"):
                        return True, None  # indica retry
            except Exception as e:
                logging.warning(
                    "Middleware '%s'.on_error falhou: %s", mw.name, e
                )
        return False, None

    def execute_before_run(
        self,
        query: str,
        state: PipelineState,
    ) -> PipelineState:
        modified_state = state
        for mw in self._middlewares:
            if not mw.enabled:
                continue
            try:
                r = mw.before_run(query, modified_state)
                if r is not None and "state" in r:
                    modified_state = r["state"]
            except Exception as e:
                logging.warning(
                    "Middleware '%s'.before_run falhou: %s", mw.name, e
                )
        return modified_state

    def execute_after_run(self, state: PipelineState):
        for mw in self._middlewares:
            if not mw.enabled:
                continue
            try:
                mw.after_run(state)
            except Exception as e:
                logging.warning(
                    "Middleware '%s'.after_run falhou: %s", mw.name, e
                )

    # ── Método de conveniência para executar um nó com toda a cadeia ─

    def execute_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
        run_fn: Callable[[Any], Any],
    ) -> Any:
        """Executa um nó atravessando toda a cadeia de middlewares.

        1. before_node (todos, ordem direta)
        2. wrap_node (casca de cebola)
        3. after_node (todos, ordem inversa)

        Se before_node retornar skip=True, o nó não é executado.
        Se on_error for tratado, o resultado de fallback é usado.

        Returns:
            Resultado final do nó após todos os middlewares.
        """
        # Fase 1: before_node
        mod_input, mod_state, skip, skip_result = self.execute_before_node(
            node_name, input_data, state
        )

        if skip:
            return skip_result

        # Fase 2: wrap_node (casca de cebola)
        try:
            result = self.execute_wrap_node(node_name, mod_input, mod_state, run_fn)
        except Exception as e:
            # Fase 2b: on_error
            handled, fallback = self.execute_on_error(node_name, e, mod_state)
            if handled and fallback is not None:
                result = fallback
            else:
                raise

        # Fase 3: after_node
        result = self.execute_after_node(node_name, result, mod_state)

        return result

    def describe(self) -> Dict[str, Any]:
        return {
            "total": self.count,
            "middlewares": self.list(),
        }


# ═══════════════════════════════════════════════════════════════════
# Middlewares pré-construídos
# ═══════════════════════════════════════════════════════════════════

class LoggingMiddleware(BaseMiddleware):
    """Loga execução de cada nó no pipeline.

    Inspirado pelo padrão de observabilidade do DeerFlow.
    """

    def __init__(self, name: str = "logging", logger: Optional[logging.Logger] = None):
        super().__init__(name)
        self.logger = logger or logging.getLogger("anp.middleware")

    def before_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        query_str = str(state.query) if state.query is not None else ""
        self.logger.info("[ANP] ▶ Iniciando nó '%s' | query: %s",
                         node_name,
                         (query_str[:60] + "...") if len(query_str) > 60
                         else query_str)
        return None

    def after_node(
        self,
        node_name: str,
        result: Any,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        result_str = str(result)[:100] if result else "(None)"
        self.logger.info("[ANP] ✓ Nó '%s' concluído | resultado: %s",
                         node_name, result_str)
        return None

    def on_error(
        self,
        node_name: str,
        error: Exception,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        self.logger.error("[ANP] ✗ Nó '%s' falhou: %s\n%s",
                          node_name, error, traceback.format_exc())
        return None


class TimingMiddleware(BaseMiddleware):
    """Mede e registra o tempo de execução de cada nó.

    Também acumula estatísticas de tempo no metadata do pipeline.
    """

    def __init__(self, name: str = "timing"):
        super().__init__(name)
        self._timings: Dict[str, float] = {}

    def before_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        self._timings[node_name] = time.time()
        return None

    def after_node(
        self,
        node_name: str,
        result: Any,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        start = self._timings.pop(node_name, None)
        if start is not None:
            elapsed = time.time() - start
            # Armazenar no metadata do estado
            timings = state.get_metadata("node_timings", {})
            timings[node_name] = round(elapsed, 3)
            state.set_metadata("node_timings", timings)
        return None


class ValidationMiddleware(BaseMiddleware):
    """Valida entradas e saídas dos nós.

    Pode pular nós (skip) se a entrada for inválida,
    ou registrar advertências se a saída não atender expectativas.

    Inspirado pela validação de estado do DeerFlow ThreadState.
    """

    def __init__(
        self,
        name: str = "validation",
        input_validators: Optional[Dict[str, Callable[[Any], bool]]] = None,
        output_validators: Optional[Dict[str, Callable[[Any], bool]]] = None,
        strict: bool = False,
    ):
        super().__init__(name)
        self.input_validators = input_validators or {}
        self.output_validators = output_validators or {}
        self.strict = strict

    def before_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        validator = self.input_validators.get(node_name)
        if validator and not validator(input_data):
            msg = f"Validação de entrada falhou para nó '{node_name}'"
            if self.strict:
                raise ValueError(msg)
            logging.warning("[ANP] ⚠ %s", msg)
        return None

    def after_node(
        self,
        node_name: str,
        result: Any,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        validator = self.output_validators.get(node_name)
        if validator and not validator(result):
            msg = f"Validação de saída falhou para nó '{node_name}'"
            if self.strict:
                raise ValueError(msg)
            logging.warning("[ANP] ⚠ %s", msg)
        return None


class RetryMiddleware(BaseMiddleware):
    """Retenta execução de nós em caso de falha.

    Configuração:
        max_retries: Número máximo de retentativas (default: 2).
        retry_delay: Segundos de espera entre retentativas (default: 1.0).
        retryable_exceptions: Tupla de exceções que podem ser retentadas.
                              None = todas as exceções.

    Inspirado pela resiliência do DeerFlow em cenários de
    timeout e falha de modelo.
    """

    def __init__(
        self,
        name: str = "retry",
        max_retries: int = 2,
        retry_delay: float = 1.0,
        retryable_exceptions: Optional[tuple] = None,
    ):
        super().__init__(name)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retryable_exceptions = retryable_exceptions

    def wrap_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
        run_fn: Callable[[Any], Any],
    ) -> Any:
        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                return run_fn(input_data)
            except Exception as e:
                last_error = e
                if self.retryable_exceptions is not None and \
                   not isinstance(e, self.retryable_exceptions):
                    raise  # não retentável, propaga
                if attempt < self.max_retries:
                    logging.info(
                        "[ANP] ↻ Retry nó '%s' (tentativa %d/%d) após: %s",
                        node_name, attempt + 1, self.max_retries, e
                    )
                    time.sleep(self.retry_delay)
                else:
                    logging.error(
                        "[ANP] ✗ Retry nó '%s' esgotado após %d tentativas",
                        node_name, self.max_retries
                    )
        if last_error is None:
            raise RuntimeError(
                f"RetryMiddleware: nó '{node_name}' falhou sem exceção"
            )
        raise last_error  # re-raise da última exceção


class CheckpointMiddleware(BaseMiddleware):
    """Salva checkpoint automaticamente após cada nó.

    Usa wrap_node em vez de after_node para garantir que o checkpoint
    seja salvo APÓS a execução do nó (resultado calculado) mas sem
    depender do store_artifact externo do pipeline.

    O store_artifact do pipeline (chamado após execute_node retornar)
    é idempotente — o artefato já foi armazenado aqui.

    Inspirado pelo checkpoint automático do DeerFlow (SqliteSaver,
    PostgresSaver) e pela persistência de ThreadState.
    """

    def __init__(
        self,
        name: str = "checkpoint",
        dir_path: str = ".reversa/checkpoints",
        interval: int = 1,
    ):
        super().__init__(name)
        self.dir_path = dir_path
        self.interval = interval
        self._counter = 0

    def wrap_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
        run_fn: Callable[[Any], Any],
    ) -> Any:
        """Executa o nó e salva checkpoint após a execução."""
        result = run_fn(input_data)
        # Armazenar artefato e node_result AGORA (antes do after_node,
        # para que o checkpoint inclua este resultado completo)
        state.store_artifact(node_name, result)
        state.register_result(
            node_name,
            NodeResult(
                node_name=node_name,
                status="completed",
                output_summary=str(result)[:200],
            ),
        )
        self._counter += 1
        if self._counter % self.interval == 0:
            try:
                path = state.save_checkpoint(self.dir_path)
                logging.info("[ANP] 💾 Checkpoint salvo: %s", path)
            except Exception as e:
                logging.warning("[ANP] ⚠ Falha ao salvar checkpoint: %s", e)
        return result


class SummarizationMiddleware(BaseMiddleware):
    """Sumarização automática do estado do pipeline.

    Inspirado pelo SummarizationMiddleware do DeerFlow (cap. 7):
    - Trigger por mensagens/tokens/fraction
    - keep_recent: quantas mensagens manter
    - trim_tokens_to_summarize: limite para sumarização

    DeerFlow equivalente: SummarizationMiddleware (LangChain built-in)
    """

    SUMMARIZATION_PROMPT = (
        "Summarize the following conversation history in a concise paragraph "
        "that preserves all key facts, decisions, and action items:\n\n{text}"
    )

    def __init__(
        self,
        name: str = "summarization",
        trigger_messages: int = 20,
        keep_recent: int = 10,
        enabled: bool = True,
        llm_summarize_fn: Optional[Callable[[str], str]] = None,
    ):
        super().__init__(name)
        self.trigger_messages = trigger_messages
        self.keep_recent = keep_recent
        self.enabled = enabled
        self.llm_summarize_fn = llm_summarize_fn

    def before_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None

        # Verificar número de artefatos (análogo a mensagens no DeerFlow)
        num_artifacts = len(state.artifacts)
        if num_artifacts < self.trigger_messages:
            return None

        # Já foi sumarizado?
        if state.get_metadata("summarized", False):
            return None

        # Coletar artefatos recentes para sumarizar
        artifact_keys = list(state.artifacts.keys())
        to_summarize = artifact_keys[:-self.keep_recent] if len(artifact_keys) > self.keep_recent else []

        if not to_summarize:
            return None

        try:
            # Usar LLM ou fallback textual
            if self.llm_summarize_fn:
                text_to_summarize = "\n".join(
                    f"{k}: {str(state.artifacts[k])[:500]}"
                    for k in to_summarize
                )
                summary = self.llm_summarize_fn(
                    self.SUMMARIZATION_PROMPT.format(text=text_to_summarize)
                )
            else:
                # Fallback: sumarização simples (contagem)
                summary = (
                    f"[Auto-summary] Pipeline processed {num_artifacts} artifacts. "
                    f"Nodes completed: {len(state.node_results)}. "
                    f"Last {self.keep_recent} artifacts preserved."
                )

            # Remover artefatos sumarizados
            for k in to_summarize:
                state.artifacts.pop(k, None)

            # Armazenar sumário
            state.store_artifact("__summary__", summary)
            state.set_metadata("summarized", True)
            state.set_metadata("summary_timestamp", datetime.now().isoformat())
            state.set_metadata("summarized_artifacts", len(to_summarize))

            logging.info(
                "[ANP] 📝 Sumarização: %d artefatos → 1 sumário",
                len(to_summarize)
            )

        except Exception as e:
            logging.warning("[ANP] ⚠ Falha na sumarização: %s", e)

        return None


class DanglingCallMiddleware(BaseMiddleware):
    """Detecta e repara chamadas de ferramenta pendentes (dangling tool calls).

    Inspirado pelo DanglingToolCallMiddleware do DeerFlow (cap. 7):

    Quando um AIMessage tem tool_calls mas não há ToolMessage correspondente,
    insere ToolMessages de placeholder para evitar erros de formato na LLM.

    No contexto ANP, isto se aplica a nós que retornaram resultados parciais
    ou foram interrompidos antes de registrar o resultado completo.
    """

    DANGLING_MESSAGE = (
        "[Interrupted — tool call did not return a result.]"
    )

    def __init__(self, name: str = "dangling_call"):
        super().__init__(name)

    def before_node(
        self,
        node_name: str,
        input_data: Any,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        # Verificar se há nós no node_results com status "running" ou
        # "pending" em nós que já deveriam ter sido processados.
        pending_nodes = [
            name for name, nr in state.node_results.items()
            if nr.status in ("pending", "running")
        ]

        if not pending_nodes:
            return None

        # Marcar nós pendentes como "dangling"
        for name in pending_nodes:
            state.node_results[name].status = "dangling"
            state.node_results[name].error = self.DANGLING_MESSAGE
            state.node_results[name].output_summary = (
                "[Interrupted — no result produced]"
            )

        if pending_nodes:
            logging.warning(
                "[ANP] 🔧 Reparados %d nós pendentes (dangling): %s",
                len(pending_nodes), pending_nodes
            )

        return None


class StatsMiddleware(BaseMiddleware):
    """Acumula estatísticas da execução do pipeline.

    Coleta: tempo total, nós por status, artefatos, etc.
    Útil para monitoramento e debugging.
    """

    def __init__(self, name: str = "stats"):
        super().__init__(name)
        self._start_time: Optional[float] = None

    def before_run(
        self,
        query: str,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        self._start_time = time.time()
        state.set_metadata("pipeline_start", datetime.now().isoformat())
        return None

    def after_run(self, state: PipelineState):
        if self._start_time:
            elapsed = time.time() - self._start_time
            state.set_metadata("pipeline_duration_sec", round(elapsed, 2))

        # Estatísticas dos nós
        statuses = {}
        for nr in state.node_results.values():
            statuses[nr.status] = statuses.get(nr.status, 0) + 1

        state.set_metadata("node_stats", {
            "total": len(state.node_results),
            "by_status": statuses,
        })
        state.set_metadata("pipeline_end", datetime.now().isoformat())

    def after_node(
        self,
        node_name: str,
        result: Any,
        state: PipelineState,
    ) -> Optional[Dict[str, Any]]:
        # Contagem acumulada de nós processados
        completed = sum(
            1 for nr in state.node_results.values()
            if nr.status == "completed"
        )
        state.set_metadata("nodes_completed", completed)
        state.set_metadata("artifacts_total", len(state.artifacts))
        return None


# ═══════════════════════════════════════════════════════════════════
# Factory: cria cadeia completa com middlewares padrão
# ═══════════════════════════════════════════════════════════════════

def create_default_chain(
    checkpoint_dir: str = ".reversa/checkpoints",
    checkpoint_interval: int = 1,
    retry_enabled: bool = True,
    retry_max: int = 2,
    summarization_trigger: int = 20,
    summarization_keep: int = 10,
    **kwargs,
) -> MiddlewareChain:
    """Cria uma MiddlewareChain com middlewares pré-configurados.

    Ordem de execução (inspirada pelo DeerFlow 11-layer pipeline):
      1. StatsMiddleware     → coleta estatísticas
      2. LoggingMiddleware   → loga execução
      3. TimingMiddleware    → mede tempo
      4. ValidationMiddleware → valida entradas/saídas
      5. DanglingCallMiddleware → repara chamadas pendentes
      6. SummarizationMiddleware → sumariza quando necessário
      7. RetryMiddleware     → retenta em falha
      8. CheckpointMiddleware → salva checkpoint

    Args:
        checkpoint_dir: Diretório para checkpoints.
        checkpoint_interval: Salvar a cada N nós.
        retry_enabled: Ativar retry automático.
        retry_max: Máximo de retentativas.
        summarization_trigger: Artefatos para disparar sumarização.
        summarization_keep: Artefatos recentes a preservar.
        **kwargs: Passado para middlewares individuais.

    Returns:
        MiddlewareChain configurada.
    """
    chain = MiddlewareChain()

    # 1. Stats (primeiro, para medir tudo)
    chain.add(StatsMiddleware())

    # 2. Logging
    chain.add(LoggingMiddleware())

    # 3. Timing
    chain.add(TimingMiddleware())

    # 4. Validation
    chain.add(ValidationMiddleware())

    # 5. DanglingCall (repara antes de qualquer processamento)
    chain.add(DanglingCallMiddleware())

    # 6. Summarization (antes de retry, para reduzir estado)
    chain.add(SummarizationMiddleware(
        trigger_messages=summarization_trigger,
        keep_recent=summarization_keep,
    ))

    # 7. Retry (envolve a execução real)
    if retry_enabled:
        chain.add(RetryMiddleware(max_retries=retry_max))

    # 8. Checkpoint (último, salva após tudo)
    chain.add(CheckpointMiddleware(
        dir_path=checkpoint_dir,
        interval=checkpoint_interval,
    ))

    return chain
