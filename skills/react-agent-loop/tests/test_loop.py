"""
TDD tests for AgentLoop — ReAct engine com ciclo Thought→Action→Observation.
CT-1: test_init — inicializacao de AgentLoop, ToolRegistry, LoopState
CT-2: test_execute_tool — execucao de tool via registry com sucesso e falha
CT-3: test_max_iterations — loop termina ao atingir MAX_ITERATIONS
CT-4: test_available — tool registry vazia retorna erro adequado
"""

import os
import sys
import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

from agent_loop import (
    AgentLoop, ToolRegistry, ToolCall, ToolResult,
    LoopState, BaseTool, FileWriterTool, BashTool,
    DEFAULT_MAX_ITERATIONS,
)


class EchoTool(BaseTool):
    @property
    def name(self):
        return "echo"

    @property
    def description(self):
        return "Retorna o input como output"

    @property
    def parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto a ecoar"},
            },
            "required": ["text"],
        }

    def execute(self, text="", **kwargs):
        return ToolResult(output=f"echo: {text}")


class AlwaysFailTool(BaseTool):
    @property
    def name(self):
        return "always_fail"

    @property
    def description(self):
        return "Sempre falha"

    @property
    def parameters_schema(self):
        return {"type": "object", "properties": {}}

    def execute(self, **kwargs):
        raise ValueError("erro forcado")


class MockLLM:
    def __init__(self, responses=None):
        self.responses = responses or []
        self.calls = []

    def chat(self, messages, **kwargs):
        self.calls.append(messages)
        if self.responses:
            return self.responses.pop(0)
        return "resposta final simulada"


class TestAgentLoop:

    def test_init(self):
        llm = MockLLM()
        tools = ToolRegistry()
        loop = AgentLoop(llm_client=llm, tool_registry=tools, max_iterations=3)
        assert loop._max_iterations == 3
        assert loop._tools is tools

        state = LoopState()
        assert state.iterations == 0
        assert state.terminated is False
        assert state.final_answer is None

    def test_execute_tool(self):
        tools = ToolRegistry()
        tools.register(EchoTool())
        tools.register(AlwaysFailTool())

        result_ok = tools.execute(ToolCall(name="echo", arguments={"text": "ola"}))
        assert result_ok.success is True
        assert "echo: ola" in result_ok.output

        result_fail = tools.execute(ToolCall(name="always_fail", arguments={}))
        assert result_fail.success is False
        assert result_fail.error is not None

        result_unknown = tools.execute(ToolCall(name="nonexistent", arguments={}))
        assert result_unknown.success is False
        assert "desconhecida" in result_unknown.error.lower() or "Tool desconhecida" in result_unknown.error

    def test_execute_tool_validates_required_arguments(self):
        tools = ToolRegistry()
        tools.register(EchoTool())

        result = tools.execute(ToolCall(name="echo", arguments={}))
        assert result.success is False
        assert "obrigatorio" in result.error.lower()

    def test_file_writer_stays_inside_base_dir(self, tmp_path):
        tool = FileWriterTool(base_dir=tmp_path)

        result = tool.execute(path="notes/result.txt", content="ok")
        assert result.success is True
        assert (tmp_path / "notes" / "result.txt").read_text(encoding="utf-8") == "ok"

        traversal = tool.execute(path="../outside.txt", content="bad")
        assert traversal.success is False
        assert "diretorio base" in traversal.error

        absolute = tool.execute(path=str(tmp_path.parent / "outside.txt"), content="bad")
        assert absolute.success is False
        assert "relativo" in absolute.error

    def test_file_writer_rejects_overwrite_by_default(self, tmp_path):
        tool = FileWriterTool(base_dir=tmp_path)
        target = tmp_path / "existing.txt"
        target.write_text("original", encoding="utf-8")

        result = tool.execute(path="existing.txt", content="new")
        assert result.success is False
        assert target.read_text(encoding="utf-8") == "original"

    def test_bash_tool_denies_commands_by_default(self):
        result = BashTool().execute(command="echo hello")

        assert result.success is False
        assert "nao permitido" in result.error

    def test_bash_tool_runs_allowlisted_command_without_shell(self, tmp_path):
        tool = BashTool(allowed_commands={"echo"}, base_dir=tmp_path)

        result = tool.execute(command="echo hello")

        assert result.success is True
        assert result.output == "hello"

    def test_max_iterations(self):
        tool_responses = []
        for i in range(6):
            tool_responses.append(
                '```json\n{"name": "echo", "arguments": {"text": "msg"}}\n```'
            )

        llm = MockLLM(tool_responses)
        tools = ToolRegistry()
        tools.register(EchoTool())

        loop = AgentLoop(llm_client=llm, tool_registry=tools, max_iterations=3)
        result = loop.run("faca algo")
        assert "limite maximo de iteracoes" in result.lower()

    def test_available(self):
        tools = ToolRegistry()
        assert len(tools._tools) == 0

        unknown = tools.execute(ToolCall(name="ghost", arguments={}))
        assert unknown.success is False

        prompt = tools.get_system_prompt_addendum()
        assert prompt == ""

        tools.register(EchoTool())
        prompt2 = tools.get_system_prompt_addendum()
        assert "echo" in prompt2
        assert "## Ferramentas Disponiveis" in prompt2
