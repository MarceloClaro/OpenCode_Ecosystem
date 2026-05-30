"""
core/validators.py — Validação de Inputs e Schemas.

Funções reutilizáveis para validar identificadores, caminhos,
intervalos numéricos, schemas JSON e tipos básicos.
Integra-se naturalmente com Pydantic e com a hierarquia de
exceções do core.

Uso:
    from core.validators import validate_identifier, validate_in_range

    name = validate_identifier("my_agent")
    score = validate_in_range(0.85, 0.0, 1.0, field="score")
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from core.errors import ValidationError

# --- Expressões Regulares Compiladas ---

_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_HEX_COLOR_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


# ═══════════════════════════════════════════════════════════════════
# Identificadores
# ═══════════════════════════════════════════════════════════════════


def validate_identifier(name: str, field: str = "identifier") -> str:
    """Valida que o nome é um identificador Python válido.

    Regra: começa com letra ou ``_``, seguido de letras, dígitos ou ``_``.

    Returns:
        O nome validado (para encadeamento).

    Raises:
        ValidationError: Se o formato for inválido.
    """
    if not isinstance(name, str) or not name.strip():
        raise ValidationError(f"{field} must be a non-empty string")
    name = name.strip()
    if not _IDENTIFIER_RE.match(name):
        raise ValidationError(
            f"{field} '{name}' must start with a letter or underscore "
            f"and contain only letters, digits, and underscores"
        )
    return name


def validate_slug(slug: str, field: str = "slug") -> str:
    """Valida formato slug (kebab-case). Ex: ``meu-modulo``."""
    if not isinstance(slug, str) or not slug.strip():
        raise ValidationError(f"{field} must be a non-empty string")
    slug = slug.strip().lower()
    if not _SLUG_RE.match(slug):
        raise ValidationError(
            f"{field} '{slug}' must be kebab-case (e.g. 'meu-modulo')"
        )
    return slug


def validate_semver(version: str, field: str = "version") -> str:
    """Valida formato de versão semântica (``X.Y.Z``)."""
    if not isinstance(version, str) or not version.strip():
        raise ValidationError(f"{field} must be a non-empty string")
    version = version.strip()
    if not _SEMVER_RE.match(version):
        raise ValidationError(
            f"{field} '{version}' must be semver format (e.g. '1.2.3')"
        )
    return version


def validate_hex_color(color: str, field: str = "color") -> str:
    """Valida formato de cor hexadecimal (``#RGB`` ou ``#RRGGBB``)."""
    if not isinstance(color, str) or not color.strip():
        raise ValidationError(f"{field} must be a non-empty string")
    color = color.strip()
    if not _HEX_COLOR_RE.match(color):
        raise ValidationError(
            f"{field} '{color}' must be hex color (#RGB or #RRGGBB)"
        )
    return color.upper()


# ═══════════════════════════════════════════════════════════════════
# Caminhos
# ═══════════════════════════════════════════════════════════════════


def validate_path_exists(path: str | Path, field: str = "path") -> Path:
    """Valida que o caminho existe no sistema de arquivos."""
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"{field} '{p}' does not exist")
    return p


def validate_directory(path: str | Path, field: str = "path") -> Path:
    """Valida que o caminho é um diretório existente."""
    p = validate_path_exists(path, field)
    if not p.is_dir():
        raise ValidationError(f"{field} '{p}' is not a directory")
    return p


def validate_file(path: str | Path, field: str = "path") -> Path:
    """Valida que o caminho é um arquivo existente."""
    p = validate_path_exists(path, field)
    if not p.is_file():
        raise ValidationError(f"{field} '{p}' is not a file")
    return p


# ═══════════════════════════════════════════════════════════════════
# Numéricos
# ═══════════════════════════════════════════════════════════════════


def validate_in_range(
    value: float,
    min_val: float,
    max_val: float,
    field: str = "value",
) -> float:
    """Valida que o valor está dentro do intervalo ``[min_val, max_val]``."""
    if not (min_val <= value <= max_val):
        raise ValidationError(
            f"{field} must be between {min_val} and {max_val}, got {value}"
        )
    return value


def validate_positive(value: float, field: str = "value") -> float:
    """Valida que o valor é estritamente positivo (``> 0``)."""
    if value <= 0:
        raise ValidationError(f"{field} must be positive (> 0), got {value}")
    return value


def validate_non_negative(value: float, field: str = "value") -> float:
    """Valida que o valor não é negativo (``>= 0``)."""
    if value < 0:
        raise ValidationError(f"{field} must be >= 0, got {value}")
    return value


def validate_score(value: float, field: str = "score") -> float:
    """Valida score no intervalo ``[0, 100]`` (padrão do ecossistema)."""
    return validate_in_range(value, 0.0, 100.0, field=field)


# ═══════════════════════════════════════════════════════════════════
# Strings
# ═══════════════════════════════════════════════════════════════════


def validate_non_empty(value: Any, field: str = "value") -> str:
    """Garante que o valor é uma string não vazia (após *strip*)."""
    if not value:
        raise ValidationError(f"{field} must not be empty")
    s = str(value).strip()
    if not s:
        raise ValidationError(f"{field} must not be empty or whitespace-only")
    return s


def validate_max_length(value: str, max_len: int, field: str = "value") -> str:
    """Valida que a string não excede o comprimento máximo."""
    if len(value) > max_len:
        raise ValidationError(
            f"{field} exceeds max length of {max_len} (got {len(value)})"
        )
    return value


def validate_min_length(value: str, min_len: int, field: str = "value") -> str:
    """Valida que a string atinge o comprimento mínimo."""
    if len(value) < min_len:
        raise ValidationError(
            f"{field} is too short ({len(value)} < {min_len})"
        )
    return value


# ═══════════════════════════════════════════════════════════════════
# JSON / Schema
# ═══════════════════════════════════════════════════════════════════


def validate_json_string(text: str, field: str = "json") -> dict[str, Any] | list[Any]:
    """Valida que a string contém JSON válido e retorna o objeto parseado."""
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValidationError(f"{field} is not valid JSON: {e}") from e


def validate_schema(
    data: Any,
    required_fields: list[str],
    field: str = "data",
) -> dict[str, Any]:
    """Valida a presença de campos obrigatórios em um dicionário."""
    if not isinstance(data, dict):
        raise ValidationError(f"{field} must be a dict, got {type(data).__name__}")
    missing = [k for k in required_fields if k not in data]
    if missing:
        raise ValidationError(
            f"{field} missing required fields: {', '.join(missing)}"
        )
    return data


# ═══════════════════════════════════════════════════════════════════
# Tipos Genéricos
# ═══════════════════════════════════════════════════════════════════


def validate_type(value: Any, expected_type: type, field: str = "value") -> Any:
    """Valida que o valor é do tipo esperado."""
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"{field} must be {expected_type.__name__}, "
            f"got {type(value).__name__}"
        )
    return value


def validate_one_of(value: Any, options: list[Any], field: str = "value") -> Any:
    """Valida que o valor está entre as opções permitidas."""
    if value not in options:
        formatted = ", ".join(repr(o) for o in options)
        raise ValidationError(
            f"{field} must be one of [{formatted}], got {value!r}"
        )
    return value
