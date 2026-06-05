"""
Node Types — Implementações concretas de nós para o pipeline ANP.

Fornece uma biblioteca de nós reutilizáveis que implementam os padrões
identificados no BettaFish QueryEngine/MediaEngine/InsightEngine:

  • TransformNode    — Transformação genérica de dados (função pura)
  • LLMQueryNode     — Chamada a LLM com prompt template
  • SearchNode       — Busca em fonte externa (web, DB, API)
  • ReflectNode      — Loop de reflexão sobre resultado anterior
  • StructureNode    — Geração de estrutura a partir de query
  • SummaryNode      — Sumarização de conteúdo
  • FormatNode       — Formatação de saída (MD, JSON, etc.)

Cada nó pode operar em modo StateMutation (transformando o pipeline state)
ou em modo função pura (apenas run -> resultado).
"""

import json
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime

try:
    from .base_node import BaseNode, StateMutationNode
    from .pipeline_state import PipelineState, NodeResult
except ImportError:
    from base_node import BaseNode, StateMutationNode
    from pipeline_state import PipelineState, NodeResult


# ═══════════════════════════════════════════════════════════════════════
# 1. TransformNode — Nó de transformação genérica
# ═══════════════════════════════════════════════════════════════════════

class TransformNode(BaseNode):
    """Nó que aplica uma função de transformação aos dados.

    Útil para: limpeza, extração, parsing, conversão de formatos.

    Exemplo:
        node = TransformNode(fn=lambda x: x.upper(), node_name="uppercase")
    """

    def __init__(
        self,
        fn: Callable[[Any], Any],
        node_name: str = "",
        validate_fn: Optional[Callable[[Any], bool]] = None,
    ):
        super().__init__(node_name or "TransformNode")
        self._fn = fn
        self._validate_fn = validate_fn

    def run(self, input_data: Any, **kwargs) -> Any:
        return self._fn(input_data)

    def validate_input(self, input_data: Any) -> bool:
        if self._validate_fn:
            return self._validate_fn(input_data)
        return True


# ═══════════════════════════════════════════════════════════════════════
# 2. LLMQueryNode — Nó de chamada a LLM
# ═══════════════════════════════════════════════════════════════════════

class LLMQueryNode(StateMutationNode):
    """Nó que consulta um LLM e armazena o resultado no estado.

    Inspirado pelos nós de busca/sumário do BettaFish que usam
    LLMClient para gerar conteúdo estruturado.

    Args:
        llm_client: Instância de LLMClient.
        system_prompt_template: Template para system prompt (usa {query}).
        node_name: Nome do nó.
        output_key: Chave no state.artifacts para armazenar resultado.
    """

    def __init__(
        self,
        llm_client: Any,  # LLMClient (type hint evita import circular)
        system_prompt_template: str,
        node_name: str = "",
        output_key: str = "llm_result",
        temperature: float = 0.3,
    ):
        super().__init__(node_name or "LLMQueryNode")
        self.llm = llm_client
        self.system_prompt_template = system_prompt_template
        self.output_key = output_key
        self.temperature = temperature

    def run(self, input_data: Any, **kwargs) -> str:
        """Chama o LLM e retorna a resposta textual."""
        system_prompt = self.system_prompt_template.format(
            query=str(input_data)[:2000]
        )
        return self.llm.invoke(
            system_prompt=system_prompt,
            user_message=str(input_data),
            temperature=self.temperature,
        )

    def mutate_state(
        self, input_data: Any, state: PipelineState, **kwargs
    ) -> PipelineState:
        start = datetime.now()
        try:
            result = self.run(input_data, **kwargs)
            duration = (datetime.now() - start).total_seconds() * 1000
            state.store_artifact(self.output_key, result)
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="completed",
                    output_summary=str(result)[:200],
                    duration_ms=duration,
                ),
            )
        except Exception as e:
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="failed",
                    error=str(e),
                ),
            )
        return state


# ═══════════════════════════════════════════════════════════════════════
# 3. SearchNode — Nó de busca externa
# ═══════════════════════════════════════════════════════════════════════

class SearchNode(StateMutationNode):
    """Nó que executa busca em fonte externa.

    Inspirado pelos nós FirstSearchNode/ReflectionNode do BettaFish
    que geram queries de busca e as executam via Tavily/Bocha/DB.

    Args:
        search_fn: Função que executa a busca (query -> List[Dict]).
        llm_client: Opcional, para geração inteligente de queries.
        node_name: Nome do nó.
        output_key: Chave no state.artifacts.
    """

    def __init__(
        self,
        search_fn: Callable[[str, Any], List[Dict[str, Any]]],
        llm_client: Any = None,
        node_name: str = "",
        output_key: str = "search_results",
    ):
        super().__init__(node_name or "SearchNode")
        self.search_fn = search_fn
        self.llm = llm_client
        self.output_key = output_key

    def run(self, input_data: str, **kwargs) -> List[Dict[str, Any]]:
        """Executa a busca e retorna resultados."""
        max_results = kwargs.get("max_results", 10)
        return self.search_fn(input_data, max_results)

    def mutate_state(
        self, input_data: Any, state: PipelineState, **kwargs
    ) -> PipelineState:
        start = datetime.now()
        try:
            results = self.run(input_data, **kwargs)
            duration = (datetime.now() - start).total_seconds() * 1000
            state.store_artifact(self.output_key, results)
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="completed",
                    output_summary=f"{len(results)} results",
                    duration_ms=duration,
                ),
            )
        except Exception as e:
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="failed",
                    error=str(e),
                ),
            )
        return state


# ═══════════════════════════════════════════════════════════════════════
# 4. ReflectNode — Nó de reflexão/iteração
# ═══════════════════════════════════════════════════════════════════════

class ReflectNode(StateMutationNode):
    """Nó que executa um loop de reflexão sobre um resultado.

    Inspirado pelo ReflectionNode do BettaFish: após uma busca/sumarização
    inicial, este nó identifica lacunas e gera novas queries para
    aprofundamento.

    Args:
        llm_client: LLMClient para gerar reflexões.
        search_node: SearchNode para executar buscas de reflexão.
        max_reflections: Número máximo de ciclos de reflexão.
        node_name: Nome do nó.
    """

    def __init__(
        self,
        llm_client: Any,
        search_node: SearchNode,
        max_reflections: int = 3,
        node_name: str = "",
    ):
        super().__init__(node_name or "ReflectNode")
        self.llm = llm_client
        self.search_node = search_node
        self.max_reflections = max_reflections

    def run(self, input_data: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """Executa o loop de reflexão.

        input_data esperado:
            query: str          — Consulta original
            context: str        — Contexto atual (último summary)
        """
        query = input_data.get("query", "")
        context = input_data.get("context", "")

        all_reflections = []
        for i in range(self.max_reflections):
            reflection_prompt = (
                f"Consulta original: {query}\n"
                f"Estado atual: {context}\n\n"
                f"O que ainda está faltando? Gere uma query de busca "
                f"para preencher esta lacuna. Responda apenas com a query."
            )
            reflection_query = self.llm.invoke(
                system_prompt="Você é um analista crítico. Identifique lacunas.",
                user_message=reflection_prompt,
            )
            results = self.search_node.run(reflection_query)
            all_reflections.append({
                "iteration": i + 1,
                "reflection_query": reflection_query,
                "results": results,
            })
            if not results:
                break
        return all_reflections

    def mutate_state(
        self, input_data: Any, state: PipelineState, **kwargs
    ) -> PipelineState:
        start = datetime.now()
        try:
            reflections = self.run(input_data, **kwargs)
            duration = (datetime.now() - start).total_seconds() * 1000
            state.store_artifact("reflections", reflections)
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="completed",
                    output_summary=f"{len(reflections)} reflection cycles",
                    duration_ms=duration,
                ),
            )
        except Exception as e:
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="failed",
                    error=str(e),
                ),
            )
        return state


# ═══════════════════════════════════════════════════════════════════════
# 5. StructureNode — Geração de estrutura de relatório
# ═══════════════════════════════════════════════════════════════════════

class StructureNode(StateMutationNode):
    """Nó que gera a estrutura de um documento/relatório.

    Inspirado pelo ReportStructureNode do BettaFish: a partir de uma
    query, planeja seções/parágrafos que serão processados
    individualmente.

    Args:
        llm_client: LLMClient para gerar a estrutura.
        node_name: Nome do nó.
        output_key: Chave no state.artifacts.
    """

    def __init__(
        self,
        llm_client: Any,
        node_name: str = "",
        output_key: str = "structure",
    ):
        super().__init__(node_name or "StructureNode")
        self.llm = llm_client
        self.output_key = output_key

    def run(self, input_data: str, **kwargs) -> List[Dict[str, str]]:
        """Gera estrutura de seções a partir de uma query."""
        system_prompt = (
            "Você é um arquiteto de informação. Para a consulta abaixo, "
            "gere uma estrutura de relatório com seções. "
            "Responda APENAS com JSON array: "
            '[{"title": "...", "description": "..."}]'
        )
        response = self.llm.invoke_json(
            system_prompt=system_prompt,
            user_message=input_data,
        )
        if isinstance(response, list):
            return response
        return response.get("sections", [])

    def mutate_state(
        self, input_data: Any, state: PipelineState, **kwargs
    ) -> PipelineState:
        start = datetime.now()
        try:
            structure = self.run(input_data, **kwargs)
            duration = (datetime.now() - start).total_seconds() * 1000
            state.store_artifact(self.output_key, structure)
            state.set_metadata("num_sections", len(structure))
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="completed",
                    output_summary=f"{len(structure)} sections",
                    duration_ms=duration,
                ),
            )
        except Exception as e:
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="failed",
                    error=str(e),
                ),
            )
        return state


# ═══════════════════════════════════════════════════════════════════════
# 6. SummaryNode — Sumarização de conteúdo
# ═══════════════════════════════════════════════════════════════════════

class SummaryNode(StateMutationNode):
    """Nó que sumariza conteúdo.

    Inspirado pelos nós FirstSummaryNode/ReflectionSummaryNode
    do BettaFish: compila resultados de busca em um sumário coerente.

    Args:
        llm_client: LLMClient para gerar sumários.
        node_name: Nome do nó.
        output_key: Chave no state.artifacts.
    """

    def __init__(
        self,
        llm_client: Any,
        node_name: str = "",
        output_key: str = "summary",
    ):
        super().__init__(node_name or "SummaryNode")
        self.llm = llm_client
        self.output_key = output_key

    def run(self, input_data: Dict[str, Any], **kwargs) -> str:
        """Sumariza resultados de busca em texto coerente.

        input_data:
            query: str — Consulta original
            results: List[Dict] — Resultados da busca
        """
        query = input_data.get("query", "")
        results = input_data.get("results", [])

        results_text = json.dumps(results, ensure_ascii=False, indent=2)[:4000]

        system_prompt = (
            "Você é um analista. Com base nos resultados de busca abaixo, "
            "produza um sumário conciso que responda à consulta original. "
            "Cite fontes quando possível."
        )
        user_message = (
            f"Consulta: {query}\n\n"
            f"Resultados:\n{results_text}"
        )
        return self.llm.invoke(
            system_prompt=system_prompt,
            user_message=user_message,
        )

    def mutate_state(
        self, input_data: Any, state: PipelineState, **kwargs
    ) -> PipelineState:
        start = datetime.now()
        try:
            summary = self.run(input_data, **kwargs)
            duration = (datetime.now() - start).total_seconds() * 1000
            state.store_artifact(self.output_key, summary)
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="completed",
                    output_summary=str(summary)[:200],
                    duration_ms=duration,
                ),
            )
        except Exception as e:
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="failed",
                    error=str(e),
                ),
            )
        return state


# ═══════════════════════════════════════════════════════════════════════
# 7. FormatNode — Formatação de saída
# ═══════════════════════════════════════════════════════════════════════

class FormatNode(StateMutationNode):
    """Nó que formata o resultado final.

    Inspirado pelo ReportFormattingNode do BettaFish: pega os dados
    processados e produz saída formatada (Markdown, JSON, HTML...).

    Args:
        formatter_fn: Função que recebe (state) e retorna string formatada.
        format_type: "markdown" | "json" | "custom"
        node_name: Nome do nó.
        output_key: Chave no state.artifacts.
    """

    def __init__(
        self,
        formatter_fn: Optional[Callable[[PipelineState], str]] = None,
        format_type: str = "markdown",
        node_name: str = "",
        output_key: str = "formatted_output",
    ):
        super().__init__(node_name or "FormatNode")
        self.formatter_fn = formatter_fn
        self.format_type = format_type
        self.output_key = output_key

    def run(self, input_data: PipelineState, **kwargs) -> str:
        """Formata o estado do pipeline como saída legível."""
        if self.formatter_fn:
            return self.formatter_fn(input_data)

        if self.format_type == "json":
            return input_data.to_json()
        # Default: markdown
        progress = input_data.get_progress()
        lines = [
            f"# Relatório: {progress['query']}",
            f"",
            f"**Status:** {'Concluído' if progress['is_completed'] else 'Em andamento'}",
            f"**Progresso:** {progress['completed_phases']}/{progress['total_phases']} fases",
            f"",
        ]
        for phase in input_data.phases:
            lines.append(f"## {phase.name} ({phase.status})")
            for node_name in phase.node_names:
                result = input_data.get_result(node_name)
                if result:
                    lines.append(f"- **{node_name}**: {result.status}")
                    if result.output_summary:
                        lines.append(f"  → {result.output_summary[:100]}")
        return "\n".join(lines)

    def mutate_state(
        self, input_data: Any, state: PipelineState, **kwargs
    ) -> PipelineState:
        start = datetime.now()
        try:
            formatted = self.run(state, **kwargs)
            duration = (datetime.now() - start).total_seconds() * 1000
            state.store_artifact(self.output_key, formatted)
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="completed",
                    output_summary=f"{len(formatted)} chars ({self.format_type})",
                    duration_ms=duration,
                ),
            )
        except Exception as e:
            state.register_result(
                self.node_name,
                NodeResult(
                    node_name=self.node_name,
                    status="failed",
                    error=str(e),
                ),
            )
        return state
