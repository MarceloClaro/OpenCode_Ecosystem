"""
AgentNodePipeline — Orquestrador do pipeline de nós ANP.

Gerencia o ciclo de vida completo:
   1. Registro de nós nomeados
   2. Definição de fases (sequências de nós)
   3. Execução sequencial com propagação de estado
   4. Checkpoint e resume (persistência em disco)
   5. Streaming de saída (callback por nó)
   6. Execução paralela via DAG (nós independentes em paralelo)
   7. Relatório de progresso

Inspirado pelo fluxo research() em BettaFish QueryEngine/agent.py:
    _generate_report_structure(query)
    → _process_paragraphs()
        → _initial_search_and_summary(i)
        → _reflection_loop(i)
    → _generate_final_report()
"""

from typing import Any, Dict, List, Optional, Callable, Set, Union
from datetime import datetime
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from .base_node import BaseNode, StateMutationNode
    from .pipeline_state import PipelineState, Phase, NodeResult
    from .middleware_chain import (
        BaseMiddleware,
        MiddlewareChain,
        create_default_chain,
    )
except ImportError:
    from base_node import BaseNode, StateMutationNode
    from pipeline_state import PipelineState, Phase, NodeResult
    from middleware_chain import (
        BaseMiddleware,
        MiddlewareChain,
        create_default_chain,
    )


class AgentNodePipeline:
    """Orquestrador de pipeline de agentes baseado em nós.

    Suporta:
    - Execução sequencial por fase
    - Execução paralela via DAG (nós independentes em paralelo)
    - Checkpoint/Resume (persistência em disco)
    - Streaming de saída (callback por nó e por streaming)

    Exemplo de uso:
        pipe = AgentNodePipeline("MeuPipeline")
        pipe.add_node("estrutura", StructureNode(llm))
        pipe.add_node("busca", SearchNode(search_fn))
        pipe.add_node("sumario", SummaryNode(llm))
        pipe.add_node("formata", FormatNode())

        pipe.add_phase("Planejamento", ["estrutura"])
        pipe.add_phase("Pesquisa", ["busca", "sumario"])
        pipe.add_phase("Entrega", ["formata"])

        state = pipe.run("O que é ANP?")
        print(state.get_artifact("formatted_output"))
    """

    def __init__(self, name: str = "AgentNodePipeline"):
        self.name = name
        self._nodes: Dict[str, BaseNode] = {}
        self._phases: List[Dict[str, Any]] = []
        self._dag: Dict[str, List[str]] = {}
        self._state: Optional[PipelineState] = None
        self._on_node_complete: Optional[Callable[[str, PipelineState], None]] = None
        self._on_node_stream: Optional[Callable[[str, Any, int, int], None]] = None
        self._checkpoint_dir: str = ""
        self._checkpoint_interval: int = 1  # salvar a cada N nós
        self._parallel: bool = False
        self._max_workers: int = 4
        # P17 — MiddlewareChain
        self._middleware: Optional[MiddlewareChain] = None

    # ── Registro ──────────────────────────────────────────────────────

    def add_node(
        self,
        name: str,
        node: BaseNode,
        depends_on: Optional[List[str]] = None,
    ) -> "AgentNodePipeline":
        """Registra um nó no pipeline.

        Args:
            name: Identificador único do nó.
            node: Instância de BaseNode ou StateMutationNode.
            depends_on: Lista de nós dos quais este depende (para DAG).
                        None = sem dependências (raiz do DAG).

        Returns:
            self para encadeamento.
        """
        if name in self._nodes:
            raise ValueError(f"Nó '{name}' já registrado no pipeline.")
        self._nodes[name] = node
        self._dag[name] = depends_on or []
        return self

    def set_dag(self, dag: Dict[str, List[str]]) -> "AgentNodePipeline":
        """Define o DAG de dependências entre todos os nós.

        Args:
            dag: Mapa node_name -> [node_names dos quais depende].
                  Nós que já foram registrados mas não estão no DAG
                  serão tratados como raízes (sem dependências).

        Returns:
            self para encadeamento.
        """
        for node_name, deps in dag.items():
            if node_name not in self._nodes:
                raise ValueError(
                    f"Nó '{node_name}' do DAG não registrado. "
                    f"Registre com add_node() primeiro."
                )
            for dep in deps:
                if dep not in self._nodes:
                    raise ValueError(
                        f"Dependência '{dep}' do nó '{node_name}' não registrada."
                    )
        self._dag.update(dag)
        return self

    def add_phase(
        self,
        phase_name: str,
        node_names: List[str],
    ) -> "AgentNodePipeline":
        """Define uma fase com sequência de nós.

        Args:
            phase_name: Nome da fase.
            node_names: Lista de nomes de nós já registrados.

        Returns:
            self para encadeamento.
        """
        for n in node_names:
            if n not in self._nodes:
                raise ValueError(
                    f"Nó '{n}' não registrado. Registre com add_node() primeiro."
                )
        self._phases.append({
            "name": phase_name,
            "node_names": node_names,
            "order": len(self._phases),
        })
        return self

    def on_node_complete(self, callback: Callable[[str, PipelineState], None]):
        """Hook executado após cada nó completar."""
        self._on_node_complete = callback
        return self

    def on_node_stream(self, callback: Callable[[str, Any, int, int], None]):
        """Hook de streaming: chamado durante a execução de nós longos.

        Callback recebe: (node_name, chunk, current_index, total_chunks)
        """
        self._on_node_stream = callback
        return self

    def enable_checkpoint(
        self,
        dir_path: str = ".reversa/checkpoints",
        interval: int = 1,
    ) -> "AgentNodePipeline":
        """Ativa checkpoint automático durante a execução.

        Args:
            dir_path: Diretório para salvar checkpoints.
            interval: Salvar a cada N nós processados (default: 1 = todo nó).

        Returns:
            self para encadeamento.
        """
        self._checkpoint_dir = dir_path
        self._checkpoint_interval = interval
        return self

    def enable_parallel(
        self,
        max_workers: int = 4,
    ) -> "AgentNodePipeline":
        """Ativa execução paralela entre fases via DAG.

        Args:
            max_workers: Número máximo de threads paralelas.

        Returns:
            self para encadeamento.
        """
        self._parallel = True
        self._max_workers = max_workers
        return self

    # ── P17 — MiddlewareChain ──────────────────────────────────────

    def use_middleware(
        self,
        chain: Optional[MiddlewareChain] = None,
        defaults: bool = True,
        **chain_kwargs,
    ) -> "AgentNodePipeline":
        """Define a cadeia de middlewares para este pipeline.

        Dois modos de uso:
        1. chain explícito: passe um MiddlewareChain já configurado.
        2. defaults=True: cria uma cadeia padrão (create_default_chain)
           com opções em **chain_kwargs.

        Inspirado pelo DeerFlow 11-layer Middleware Pipeline, onde
        _build_middlewares() monta dinamicamente a cadeia com base
        na configuração.

        Args:
            chain: MiddlewareChain já configurado (opcional).
            defaults: Se True (e chain=None), cria cadeia padrão.
            **chain_kwargs: Argumentos para create_default_chain().

        Returns:
            self para encadeamento.
        """
        if chain is not None:
            self._middleware = chain
        elif defaults:
            self._middleware = create_default_chain(**chain_kwargs)
        return self

    def get_middleware(self) -> Optional[MiddlewareChain]:
        """Retorna a cadeia de middlewares atual."""
        return self._middleware

    def add_middleware(self, middleware: BaseMiddleware) -> "AgentNodePipeline":
        """Adiciona um middleware à cadeia existente.

        Se nenhuma cadeia existir, cria uma cadeia vazia primeiro.

        Args:
            middleware: Instância de BaseMiddleware.

        Returns:
            self para encadeamento.
        """
        if self._middleware is None:
            self._middleware = MiddlewareChain()
        self._middleware.add(middleware)
        return self

    # ── Execução ──────────────────────────────────────────────────────

    # ── Execução Sequencial ────────────────────────────────────────────

    def run(
        self,
        query: str,
        metadata: Optional[Dict[str, Any]] = None,
        resume_from: Optional[str] = None,
    ) -> PipelineState:
        """Executa o pipeline completo.

        Suporta:
        - Execução sequencial por fase (padrão)
        - Execução paralela via DAG (se enable_parallel() ativado)
        - Checkpoint automático (se enable_checkpoint() ativado)
        - Streaming de saída (se on_node_stream() configurado)
        - Resume de checkpoint (se resume_from fornecido)

        Args:
            query: Consulta/entrada principal.
            metadata: Metadados adicionais para o estado.
            resume_from: Caminho de checkpoint para retomar.

        Returns:
            PipelineState após execução de todas as fases.
        """
        if resume_from:
            self._state = PipelineState.load_checkpoint(resume_from)
            return self._resume()

        self._state = PipelineState(
            query=query,
            metadata=metadata or {},
        )
        self._state.metadata["pipeline_name"] = self.name

        # Registrar DAG no estado
        self._state.set_dag(self._dag)

        # ── P17 — Middleware before_run hook ─────────────────────────
        if self._middleware:
            self._middleware.execute_before_run(query, self._state)

        # Execução paralela via DAG (se ativado e DAG tem dependências)
        if self._parallel and self._dag:
            result = self._run_dag()
        else:
            # Execução sequencial padrão
            self._run_sequential()

        self._state.mark_completed()

        # ── P17 — Middleware after_run hook ──────────────────────────
        if self._middleware and self._state:
            self._middleware.execute_after_run(self._state)

        # Checkpoint final com estado completo
        if self._checkpoint_dir and self._state:
            self._state.save_checkpoint(self._checkpoint_dir)

        return self._state

    def _run_sequential(self):
        """Executa as fases sequencialmente."""
        node_counter = 0

        for phase_def in self._phases:
            phase_name = phase_def["name"]
            node_names = phase_def["node_names"]
            phase_index = phase_def["order"]

            # Marca fase como running
            self._state.add_phase(phase_name, node_names)
            self._state.set_phase_status(phase_index, "running")

            # ── P17 — before_phase hook ────────────────────────────
            if self._middleware:
                self._middleware.execute_before_phase(
                    phase_name, phase_index, node_names, self._state
                )

            # Processa nós da fase
            phase_ok = True
            for node_name in node_names:
                node = self._nodes[node_name]
                node_counter += 1

                # Pular nós já executados (resume)
                if self._is_node_completed(node_name):
                    continue

                input_data = self._resolve_input(node_name)
                self._execute_node(node_name, node, input_data, phase_index)

                # Verificar se o nó falhou
                nr = self._state.node_results.get(node_name)
                if nr and nr.status == "failed":
                    phase_ok = False

                # Hook de callback
                if self._on_node_complete:
                    self._on_node_complete(node_name, self._state)

                # Checkpoint automático
                self._maybe_checkpoint(node_counter)

            # ── P17 — after_phase hook ─────────────────────────────
            if self._middleware:
                self._middleware.execute_after_phase(
                    phase_name, phase_index, self._state
                )

            # Atualiza status da fase
            self._state.set_phase_status(
                phase_index, "completed" if phase_ok else "failed"
            )

    # ── Execução Paralela via DAG ──────────────────────────────────────

    def _run_dag(self) -> PipelineState:
        """Executa o pipeline usando DAG com paralelismo entre nós
        independentes.

        Returns:
            PipelineState com resultados.
        """
        if not self._state:
            raise RuntimeError("PipelineState não inicializado.")

        # Obter ordenação topológica em camadas
        layers = self._state.get_dependency_order()

        node_counter = 0

        for phase_def in self._phases:
            phase_name = phase_def["name"]
            node_names = set(phase_def["node_names"])
            phase_index = phase_def["order"]

            self._state.add_phase(phase_name, list(node_names))
            self._state.set_phase_status(phase_index, "running")

            # ── P17 — before_phase hook ────────────────────────────
            if self._middleware:
                self._middleware.execute_before_phase(
                    phase_name, phase_index, list(node_names), self._state
                )

            # ── Multi-leva DAG: loop até todos os nós da fase processados ──
            # Cada leva executa os nós que ficaram prontos (todas as
            # dependências satisfeitas) em paralelo.
            processed: Set[str] = set()
            phase_ok = True

            while len(processed) < len(node_names):
                available = [
                    n for n in node_names
                    if n not in processed and self._is_ready(n, layers)
                ]
                if not available:
                    # Deadlock ou nós sem DAG — execução sequencial
                    for node_name in phase_def["node_names"]:
                        if node_name in processed or self._is_node_completed(node_name):
                            continue
                        node = self._nodes.get(node_name)
                        if not node:
                            continue
                        node_counter += 1
                        input_data = self._resolve_input(node_name)
                        self._execute_node(node_name, node, input_data, phase_index)
                        processed.add(node_name)
                        if self._on_node_complete:
                            self._on_node_complete(node_name, self._state)
                        self._maybe_checkpoint(node_counter)
                    break

                # Execução paralela desta leva
                with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
                    future_map = {}
                    for node_name in available:
                        if self._is_node_completed(node_name):
                            processed.add(node_name)
                            continue
                        node = self._nodes.get(node_name)
                        if not node:
                            continue
                        future = executor.submit(
                            self._run_node_safe, node_name, node, phase_index
                        )
                        future_map[future] = node_name

                    for future in as_completed(future_map):
                        node_name = future_map[future]
                        node_counter += 1
                        try:
                            future.result()
                        except Exception as e:
                            phase_ok = False
                            if self._state is not None:
                                self._state.register_result(
                                    node_name,
                                    NodeResult(
                                        node_name=node_name,
                                        status="failed",
                                        error=str(e),
                                    ),
                                )
                        processed.add(node_name)
                        if self._on_node_complete:
                            self._on_node_complete(node_name, self._state)
                        self._maybe_checkpoint(node_counter)

            # ── P17 — after_phase hook ─────────────────────────────
            if self._middleware:
                self._middleware.execute_after_phase(
                    phase_name, phase_index, self._state
                )

            self._state.set_phase_status(
                phase_index, "completed" if phase_ok else "failed"
            )

        self._state.mark_completed()
        return self._state

    def _is_ready(self, node_name: str, layers: List[set]) -> bool:
        """Verifica se um nó está pronto para execução baseado em seu
        layer no DAG."""
        if not self._state:
            return True
        # Nós sem DAG ficam prontos sempre
        if node_name not in self._state.dag:
            return True
        # Verifica se o nó está na primeira camada não-processada
        deps = self._state.dag.get(node_name, [])
        if not deps:
            return True
        # Verifica se todas as dependências foram concluídas
        return all(
            dep in self._state.node_results
            and self._state.node_results[dep].status == "completed"
            for dep in deps
        )

    def _is_node_completed(self, node_name: str) -> bool:
        """Verifica se um nó já foi executado (para resume)."""
        if not self._state:
            return False
        nr = self._state.node_results.get(node_name)
        return nr is not None and nr.status == "completed"

    def _run_node_safe(self, node_name: str, node: BaseNode, phase_index: int = 0) -> Any:
        """Executa um nó com resolução de input e middlewares.

        Ao contrário de _run_node, passa pelo _execute_node para que
        os middlewares (P17) sejam aplicados mesmo em execução paralela.
        """
        input_data = self._resolve_input(node_name)
        # _execute_node gerencia middlewares, artifacts e register_result
        self._execute_node(node_name, node, input_data, phase_index)
        if self._state:
            return self._state.get_artifact(node_name)
        return None

    def _run_node(self, node_name: str, node: BaseNode, input_data: Any) -> Any:
        """Executa um nó e registra resultado."""
        if isinstance(node, StateMutationNode):
            self._state = node.mutate_state(input_data, self._state)
            output = self._state.get_artifact(node_name)
        else:
            output = node.run(input_data)
            self._state.store_artifact(node_name, output)
            self._state.register_result(
                node_name,
                NodeResult(
                    node_name=node_name,
                    status="completed",
                    output_summary=str(output)[:200],
                ),
            )
        return output

    def _execute_node(
        self,
        node_name: str,
        node: BaseNode,
        input_data: Any,
        phase_index: int,
    ):
        """Executa um nó com suporte a streaming e middlewares.

        Com middlewares (P17), a execução passa pela MiddlewareChain:
          MiddlewareChain.execute_node(node_name, input_data, state, run_fn)
            ├── before_node (todos)
            ├── wrap_node (casca de cebola)
            │     └── retry, validação, etc.
            └── after_node (todos, ordem inversa)

        Sem middlewares, executa diretamente como antes (compatibilidade).
        """
        if isinstance(node, StateMutationNode):
            if self._state is not None:
                self._state = node.mutate_state(input_data, self._state)
            return

        if self._state is None:
            return

        # ── Função real de execução do nó ─────────────────────────
        def run_node(actual_input: Any) -> Any:
            # Streaming support
            if hasattr(node, "run_streaming") and self._on_node_stream:
                total_chunks = 4  # estimativa
                chunks = []
                for i, chunk in enumerate(node.run_streaming(actual_input)):
                    chunks.append(chunk)
                    if self._on_node_stream:
                        self._on_node_stream(node_name, chunk, i, total_chunks)
                return "\n".join(chunks) if chunks else ""
            return node.run(actual_input)

        # ── Com middlewares: execução delegada à cadeia ────────────
        if self._middleware:
            try:
                result = self._middleware.execute_node(
                    node_name, input_data, self._state, run_node
                )
                self._state.store_artifact(node_name, result)
                self._state.register_result(
                    node_name,
                    NodeResult(
                        node_name=node_name,
                        status="completed",
                        output_summary=str(result)[:200],
                    ),
                )
            except Exception as e:
                self._state.register_result(
                    node_name,
                    NodeResult(
                        node_name=node_name,
                        status="failed",
                        error=str(e),
                    ),
                )
            return

        # ── Sem middlewares: execução direta (compatibilidade) ────
        try:
            result = run_node(input_data)

            if self._state is not None:
                self._state.store_artifact(node_name, result)
                self._state.register_result(
                    node_name,
                    NodeResult(
                        node_name=node_name,
                        status="completed",
                        output_summary=str(result)[:200],
                    ),
                )
        except Exception as e:
            if self._state is not None:
                self._state.register_result(
                    node_name,
                    NodeResult(
                        node_name=node_name,
                        status="failed",
                        error=str(e),
                    ),
                )

    def _maybe_checkpoint(self, node_counter: int):
        """Salva checkpoint se configurado e no intervalo certo."""
        if (
            self._checkpoint_dir
            and node_counter % self._checkpoint_interval == 0
            and self._state
        ):
            self._state.save_checkpoint(self._checkpoint_dir)

    # ── Resume ─────────────────────────────────────────────────────────

    def _resume(self) -> PipelineState:
        """Retoma execução de um checkpoint salvo."""
        if not self._state:
            raise RuntimeError("Nenhum estado para retomar.")

        # Contar nós já completados
        completed = sum(
            1 for nr in self._state.node_results.values()
            if nr.status == "completed"
        )

        # Execução sequencial (resume sempre sequencial por simplicidade)
        self._run_sequential()
        self._state.mark_completed()
        return self._state

    def _resolve_input(self, node_name: str) -> Any:
        """Resolve o input para um nó baseado no estado atual.

        Regras de resolução (em ordem de precedência):
        1. Nós especiais (estrutura, search, etc.) — nomes semânticos
        2. DAG: se o nó tem dependências, retorna o artefato da
           primeira dependência concluída (fluxo pipeline-like)
        3. Fallback: query original do pipeline
        """
        if not self._state:
            return ""

        # 1. Nós especiais (nomes semânticos)
        if node_name == "estrutura" or node_name == "structure":
            return self._state.query
        if "search" in node_name.lower() or "busca" in node_name:
            return {
                "query": self._state.query,
                "context": self._state.get_artifact("summary", ""),
            }
        if "summary" in node_name.lower() or "sumario" in node_name:
            return {
                "query": self._state.query,
                "results": self._state.get_artifact("search_results", []),
            }
        if "reflect" in node_name.lower():
            return {
                "query": self._state.query,
                "context": self._state.get_artifact("summary", ""),
            }
        if "format" in node_name.lower():
            return self._state

        # 2. DAG: propaga output da(s) dependência(s)
        deps = self._dag.get(node_name, [])
        if deps:
            results = []
            for dep in deps:
                dep_result = self._state.get_artifact(dep)
                if dep_result is not None:
                    results.append(dep_result)
            if len(results) == 1:
                return results[0]
            elif len(results) > 1:
                # Múltiplas dependências: concatena como string
                return ",".join(str(r) for r in results)
            return None

        # 3. Fallback: query original
        return self._state.query

    # ── Consulta ──────────────────────────────────────────────────────

    @property
    def state(self) -> Optional[PipelineState]:
        return self._state

    def get_progress(self) -> Dict[str, Any]:
        if self._state is None:
            return {"status": "not_started", "name": self.name}
        return self._state.get_progress()

    def get_result(self, node_name: str) -> Any:
        if self._state is None:
            return None
        return self._state.get_artifact(node_name)

    def describe(self) -> Dict[str, Any]:
        """Retorna descrição completa do pipeline."""
        return {
            "name": self.name,
            "num_nodes": len(self._nodes),
            "num_phases": len(self._phases),
            "nodes": {k: v.describe() for k, v in self._nodes.items()},
            "phases": [
                {"name": p["name"], "nodes": p["node_names"]}
                for p in self._phases
            ],
        }

    # ── Factory methods ───────────────────────────────────────────────

    @classmethod
    def create_search_pipeline(
        cls,
        llm_client: Any,
        search_fn: Callable[[str, int], List[Dict]],
        name: str = "SearchPipeline",
    ) -> "AgentNodePipeline":
        """Cria um pipeline ANP completo (Structure → Search → Reflect → Format).

        Este factory method reproduz o fluxo completo do BettaFish
        QueryEngine em uma única chamada.

        Args:
            llm_client: Instância de LLMClient.
            search_fn: Função de busca (query, max_results) -> List[Dict].

        Returns:
            AgentNodePipeline configurado.
        """
        # Import com fallback para execução direta vs módulo
        try:
            from .node_types import (
                StructureNode, SearchNode, SummaryNode,
                ReflectNode, FormatNode,
            )
        except ImportError:
            from node_types import (
                StructureNode, SearchNode, SummaryNode,
                ReflectNode, FormatNode,
            )

        search_node = SearchNode(search_fn, llm_client=llm_client)

        pipe = cls(name)
        pipe.add_node("estrutura", StructureNode(llm_client))
        pipe.add_node("busca", search_node)
        pipe.add_node("sumario", SummaryNode(llm_client))
        pipe.add_node("reflexao", ReflectNode(llm_client, search_node))
        pipe.add_node("formata", FormatNode())

        pipe.add_phase("Planejamento", ["estrutura"])
        pipe.add_phase("Pesquisa", ["busca", "sumario"])
        pipe.add_phase("Refinamento", ["reflexao"])
        pipe.add_phase("Entrega", ["formata"])

        return pipe
