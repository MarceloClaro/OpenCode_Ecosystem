"""MCP Builder Engine -- Tool schema validation and registry management."""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field


class ParamType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"


@dataclass
class ParamDef:
    name: str
    ptype: ParamType
    required: bool = True
    default: object = None
    choices: list[str] | None = None
    description: str = ""

    @property
    def is_optional(self) -> bool:
        return not self.required

    def validate(self, value: object) -> tuple[bool, str]:
        if value is None:
            if self.required:
                return False, f"Parametro obrigatorio '{self.name}' ausente"
            return True, ""
        if self.ptype == ParamType.STRING and not isinstance(value, str):
            return False, f"'{self.name}' deve ser string"
        if self.ptype == ParamType.INTEGER and not isinstance(value, int):
            return False, f"'{self.name}' deve ser inteiro"
        if self.ptype == ParamType.FLOAT and not isinstance(value, (int, float)):
            return False, f"'{self.name}' deve ser float"
        if self.ptype == ParamType.BOOLEAN and not isinstance(value, bool):
            return False, f"'{self.name}' deve ser booleano"
        if self.ptype == ParamType.ENUM and self.choices and value not in self.choices:
            return False, f"'{self.name}' valor '{value}' invalido. Opcoes: {self.choices}"
        return True, ""


@dataclass
class ToolDef:
    name: str
    description: str
    parameters: list[ParamDef] = field(default_factory=list)

    @property
    def required_params(self) -> list[ParamDef]:
        return [p for p in self.parameters if p.required]

    @property
    def optional_params(self) -> list[ParamDef]:
        return [p for p in self.parameters if not p.required]

    def validate_call(self, params: dict) -> tuple[bool, str]:
        for param in self.parameters:
            ok, msg = param.validate(params.get(param.name))
            if not ok:
                return False, msg
        return True, ""


@dataclass
class ToolRegistry:
    tools: dict[str, ToolDef] = field(default_factory=dict)

    def register(self, tool: ToolDef) -> bool:
        if tool.name in self.tools:
            return False
        if not tool.name or " " in tool.name:
            return False
        self.tools[tool.name] = tool
        return True

    def unregister(self, name: str) -> bool:
        return self.tools.pop(name, None) is not None

    def validate_tool_call(self, tool_name: str, params: dict) -> tuple[bool, str]:
        if tool_name not in self.tools:
            return False, f"Ferramenta '{tool_name}' nao registrada"
        return self.tools[tool_name].validate_call(params)

    @property
    def registered_count(self) -> int:
        return len(self.tools)

    @property
    def tool_names(self) -> list[str]:
        return sorted(self.tools.keys())

    def format_error(self, message: str) -> dict:
        return {"isError": True, "content": [{"type": "text", "text": message}]}

    def format_success(self, data: object) -> dict:
        return {"content": [{"type": "text", "text": str(data)}]}
