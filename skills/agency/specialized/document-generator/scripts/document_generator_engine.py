"""Document Generator Engine -- Template filling with variable substitution."""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
import re


class OutputFormat(Enum):
    PLAIN = "txt"
    JSON = "json"
    MARKDOWN = "md"


@dataclass
class Template:
    name: str
    content: str
    variables: list[str] = field(default_factory=list)
    format: OutputFormat = OutputFormat.PLAIN

    @property
    def required_vars(self) -> set[str]:
        pattern = r'\{\{(\w+)\}\}'
        return set(re.findall(pattern, self.content))

    @property
    def has_unresolved(self) -> bool:
        return len(self.required_vars) > 0

    def fill(self, vars_dict: dict[str, str]) -> str:
        result = self.content
        for key, value in vars_dict.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    def validate(self) -> tuple[bool, str]:
        if not self.name.strip():
            return False, "Nome do template vazio"
        if not self.content.strip():
            return False, "Conteudo do template vazio"
        return True, ""


@dataclass
class Document:
    template_name: str
    content: str
    metadata: dict = field(default_factory=dict)

    @property
    def word_count(self) -> int:
        return len(self.content.split())

    @property
    def char_count(self) -> int:
        return len(self.content)

    @property
    def has_metadata(self) -> bool:
        return len(self.metadata) > 0


@dataclass
class DocumentGenerator:
    templates: dict[str, Template] = field(default_factory=dict)

    def register_template(self, template: Template) -> bool:
        ok, _ = template.validate()
        if not ok:
            return False
        if template.name in self.templates:
            return False
        required = template.required_vars
        template.variables = sorted(required)
        self.templates[template.name] = template
        return True

    def generate(self, template_name: str, variables: dict[str, str]) -> Document | None:
        template = self.templates.get(template_name)
        if template is None:
            return None
        filled = template.fill(variables)
        return Document(
            template_name=template_name,
            content=filled,
            metadata={"variables_used": sorted(variables.keys())},
        )

    def check_missing_vars(self, template_name: str, provided: set[str]) -> list[str]:
        template = self.templates.get(template_name)
        if template is None:
            return []
        return sorted(template.required_vars - provided)

    @property
    def registered_templates(self) -> list[str]:
        return sorted(self.templates.keys())

    @property
    def template_count(self) -> int:
        return len(self.templates)
