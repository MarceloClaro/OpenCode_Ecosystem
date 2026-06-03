"""
ReAct Agent Loop — Ciclo Thought -> Action -> Observation.

Extraido de SandeClaw (specs/agent-loop.md, PRD.md secao 6.2).
Implementa o padrao ReAct (Reasoning and Acting) com:
  - Iterador com MAX_ITERATIONS hard limit configuracao
  - Parsing de tool calls do output do LLM
  - Injecao de observacao de volta no contexto
  - Log detalhado de cada etapa para monitoramento

Integracao OpenCode:
  - Substitui loops ReAct ad-hoc espalhados pelo ecossistema
    (agent-forum, reasoning-orchestrator, cora-debate)
  - Desacopla engine de raciocinio do transporte (Telegram/CLI/HTTP)
  - Tool registry plugavel — qualquer skill pode expor tools
  - Hard limit impede loops infinitos e gasto excessivo de tokens
"""

from __future__ import annotations

import json
import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol

logger = logging.getLogger(__name__)

DEFAULT_MAX_ITERATIONS = 5
DEFAULT_TOOL_TIMEOUT_S = 60


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    call_id: str = ""

    @classmethod
    def from_json(cls, raw: str | dict[str, Any]) -> "ToolCall | None":
        try:
            if isinstance(raw, str):
                data = json.loads(raw)
            else:
                data = raw
            if "name" not in data:
                fn = data.get("function", {})
                data = {"name": fn.get("name", ""), "arguments": fn.get("arguments", {})}
                if isinstance(data["arguments"], str):
                    data["arguments"] = json.loads(data["arguments"])
            return cls(
                name=data.get("name", ""),
                arguments=data.get("arguments", {}),
                call_id=data.get("call_id", ""),
            )
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            logger.warning("Falha ao parsear ToolCall: %s", exc)
            return None


@dataclass
class ToolResult:
    output: str
    success: bool = True
    error: str | None = None

    @classmethod
    def failure(cls, error: str) -> "ToolResult":
        return cls(output=f'{{"error": "{error}"}}', success=False, error=error)


class BaseTool(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def description(self) -> str: ...

    @property
    @abstractmethod
    def parameters_schema(self) -> dict[str, Any]: ...

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult: ...

    def to_openai_tool(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema,
            },
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self._tools[tool.name] = tool
        logger.info("Tool registrada: %s", tool.name)

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def execute(self, call: ToolCall) -> ToolResult:
        tool = self._tools.get(call.name)
        if tool is None:
            return ToolResult.failure(f"Tool desconhecida: {call.name}")
        try:
            return tool.execute(**call.arguments)
        except Exception as exc:
            logger.exception("Tool '%s' lancou excecao", call.name)
            return ToolResult.failure(str(exc))

    def get_system_prompt_addendum(self) -> str:
        if not self._tools:
            return ""
        tools_desc = "\n".join(
            f"- {t.name}: {t.description}" for t in self._tools.values()
        )
        return (
            "\n## Ferramentas Disponiveis\n"
            f"{tools_desc}\n"
            "\nPara usar uma ferramenta, responda EXATAMENTE neste formato JSON:\n"
            '{"tool_call": {"name": "<nome>", "arguments": {<args>}}}\n'
        )

    def get_tool_schemas(self) -> list[dict[str, Any]]:
        return [t.to_openai_tool() for t in self._tools.values()]


@dataclass
class LoopState:
    messages: list[dict[str, str]] = field(default_factory=list)
    iterations: int = 0
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    final_answer: str | None = None
    terminated: bool = False
    logs: list[str] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({"role": role, "content": content})

    def log(self, step: str, detail: str) -> None:
        entry = f"[Iter {self.iterations}] {step}: {detail}"
        self.logs.append(entry)
        logger.info(entry)


class LLMClient(Protocol):
    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str: ...


class AgentLoop:
    """
    Engine ReAct central.

    Uso:
        loop = AgentLoop(llm_client=provider_factory, tool_registry=registry)
        answer = loop.run("Crie um arquivo chamado teste.txt com 'Ola mundo'")
    """

    def __init__(
        self,
        llm_client: LLMClient,
        tool_registry: ToolRegistry,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        system_prompt: str = "",
    ) -> None:
        self._llm = llm_client
        self._tools = tool_registry
        self._max_iterations = max_iterations
        self._base_system_prompt = system_prompt

    def run(self, user_input: str, context_messages: list[dict[str, str]] | None = None) -> str:
        state = LoopState(
            messages=list(context_messages) if context_messages else [],
            max_iterations=self._max_iterations,
        )

        tools_addendum = self._tools.get_system_prompt_addendum()
        system_content = self._base_system_prompt + tools_addendum

        system_msg = {"role": "system", "content": system_content}
        full_messages = [system_msg] + state.messages + [{"role": "user", "content": user_input}]

        while state.iterations < state.max_iterations and not state.terminated:
            state.iterations += 1
            raw = self._call_llm(full_messages)
            tool_call = self._parse_tool_call(raw)

            if tool_call:
                self._execute_tool(state, tool_call, full_messages)
            else:
                state.final_answer = raw
                state.terminated = True
                state.log("FINAL", raw[:200])

        if not state.terminated:
            state.final_answer = (
                "Atingi o limite maximo de iteracoes "
                f"({state.max_iterations}). "
                "Nao consegui completar a tarefa solicitada."
            )
            state.log("LIMIT", f"MAX_ITERATIONS={state.max_iterations} atingido")

        return state.final_answer or ""

    def _call_llm(self, messages: list[dict[str, str]]) -> str:
        return self._llm.chat(messages)

    def _parse_tool_call(self, raw: str) -> ToolCall | None:
        for delimiter in ["```json", "```"]:
            if delimiter in raw:
                block = raw.split(delimiter, 1)[1]
                block = block.split("```", 1)[0].strip()
                tc = ToolCall.from_json(block)
                if tc and tc.name:
                    return tc

        for line in raw.strip().split("\n"):
            line = line.strip()
            if line.startswith("{") and "tool_call" in line:
                try:
                    data = json.loads(line)
                    inner = data.get("tool_call", data)
                    return ToolCall.from_json(inner)
                except json.JSONDecodeError:
                    continue

        return None

    def _execute_tool(
        self,
        state: LoopState,
        tool_call: ToolCall,
        messages: list[dict[str, str]],
    ) -> None:
        state.log("ACTION", f"{tool_call.name}({json.dumps(tool_call.arguments)})")
        result = self._tools.execute(tool_call)

        if result.success:
            state.log("OBSERVATION", result.output[:200])
            observation = f"Tool '{tool_call.name}' executada com sucesso. Resultado: {result.output}"
        else:
            state.log("ERROR", f"{tool_call.name}: {result.error}")
            observation = (
                f"Tool '{tool_call.name}' falhou. Erro: {result.error}. "
                "Corrija os argumentos e tente novamente, ou use outra abordagem."
            )

        messages.append({"role": "assistant", "content": f"[Tool call: {tool_call.name}]"})
        messages.append({"role": "user", "content": observation})


class FileWriterTool(BaseTool):
    """Tool de exemplo: escreve arquivo no filesystem."""

    @property
    def name(self) -> str:
        return "write_file"

    @property
    def description(self) -> str:
        return "Cria ou sobrescreve um arquivo com o conteudo especificado"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Caminho do arquivo"},
                "content": {"type": "string", "description": "Conteudo a escrever"},
            },
            "required": ["path", "content"],
        }

    def execute(self, path: str = "", content: str = "", **_: Any) -> ToolResult:
        try:
            from pathlib import Path
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
            return ToolResult(output=f"Arquivo '{path}' criado com sucesso ({len(content)} bytes)")
        except Exception as exc:
            return ToolResult.failure(str(exc))


class BashTool(BaseTool):
    """Tool de exemplo: executa comando shell."""

    @property
    def name(self) -> str:
        return "bash"

    @property
    def description(self) -> str:
        return "Executa um comando shell e retorna a saida"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Comando a executar"},
                "workdir": {"type": "string", "description": "Diretorio de trabalho (opcional)"},
            },
            "required": ["command"],
        }

    def execute(self, command: str = "", workdir: str = "", **_: Any) -> ToolResult:
        import subprocess
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=DEFAULT_TOOL_TIMEOUT_S,
                cwd=workdir or None,
            )
            output = result.stdout.strip() or result.stderr.strip()
            return ToolResult(output=output, success=result.returncode == 0)
        except subprocess.TimeoutExpired:
            return ToolResult.failure(f"Comando excedeu timeout de {DEFAULT_TOOL_TIMEOUT_S}s")
        except Exception as exc:
            return ToolResult.failure(str(exc))
