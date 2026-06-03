"""CTs para MCP Builder Engine -- 4 testes criticos de validacao de ferramentas."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from mcp_builder_engine import ParamDef, ParamType, ToolDef, ToolRegistry


def test_ct1_param_validation():
    """CT-01: Validacao de parametro obrigatorio e tipos corretos."""
    p = ParamDef(name="limit", ptype=ParamType.INTEGER, required=True, description="Max results")

    ok, msg = p.validate(50)
    assert ok is True, f"Esperado OK, obteve: {msg}"

    ok, msg = p.validate(None)
    assert ok is False

    ok, msg = p.validate("abc")
    assert ok is False


def test_ct2_tool_registry_unique_names():
    """CT-02: Registro rejeita nomes duplicados e com espacos."""
    registry = ToolRegistry()

    ok = registry.register(ToolDef(name="search_tickets", description="Busca tickets"))
    assert ok is True

    ok = registry.register(ToolDef(name="search_tickets", description="Duplicado"))
    assert ok is False

    ok = registry.register(ToolDef(name="bad name", description="Espaco no nome"))
    assert ok is False

    assert registry.registered_count == 1


def test_ct3_validate_tool_call():
    """CT-03: Validacao de chamada de ferramenta completa."""
    registry = ToolRegistry()
    tool = ToolDef(
        name="create_issue",
        description="Cria issue",
        parameters=[
            ParamDef(name="title", ptype=ParamType.STRING, required=True),
            ParamDef(name="priority", ptype=ParamType.ENUM, required=False, choices=["low", "medium", "high"]),
            ParamDef(name="assignee", ptype=ParamType.STRING, required=False),
        ],
    )
    registry.register(tool)

    ok, msg = registry.validate_tool_call("create_issue", {"title": "Bug fix"})
    assert ok is True

    ok, msg = registry.validate_tool_call("create_issue", {})
    assert ok is False

    ok, msg = registry.validate_tool_call("create_issue", {"title": "X", "priority": "critical"})
    assert ok is False

    ok, msg = registry.validate_tool_call("nonexistent", {})
    assert ok is False


def test_ct4_error_formatting():
    """CT-04: Formatacao de erro e sucesso no padrao MCP."""
    registry = ToolRegistry()
    registry.register(ToolDef(name="ping", description="Verifica conectividade", parameters=[]))

    err = registry.format_error("API indisponivel")
    assert err["isError"] is True
    assert "API indisponivel" in err["content"][0]["text"]

    ok = registry.format_success({"status": "ok"})
    assert "isError" not in ok
    assert "status" in ok["content"][0]["text"]
