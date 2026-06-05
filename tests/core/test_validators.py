"""
Testes dos Validadores (core/validators.py)

Cobre as 18 funcoes de validacao:
- validate_identifier, validate_slug, validate_semver, validate_hex_color
- validate_path_exists, validate_directory, validate_file
- validate_in_range, validate_positive, validate_non_negative, validate_score
- validate_non_empty, validate_max_length, validate_min_length
- validate_json_string, validate_schema
- validate_type, validate_one_of
"""

import json
import tempfile
from pathlib import Path

import pytest

from core.errors import ValidationError
from core.validators import (
    validate_identifier,
    validate_slug,
    validate_semver,
    validate_hex_color,
    validate_path_exists,
    validate_directory,
    validate_file,
    validate_in_range,
    validate_positive,
    validate_non_negative,
    validate_score,
    validate_non_empty,
    validate_max_length,
    validate_min_length,
    validate_json_string,
    validate_schema,
    validate_type,
    validate_one_of,
)


# ── Identificadores ─────────────────────────────────────────────────


class TestIdentifiers:
    def test_valid_identifier(self):
        assert validate_identifier("my_var") == "my_var"
        assert validate_identifier("_private") == "_private"
        assert validate_identifier("MyClass123") == "MyClass123"

    def test_invalid_identifier(self):
        with pytest.raises(ValidationError, match="identifier"):
            validate_identifier("123abc")
        with pytest.raises(ValidationError, match="identifier"):
            validate_identifier("my-var")
        with pytest.raises(ValidationError, match="identifier"):
            validate_identifier("")
        with pytest.raises(ValidationError, match="identifier"):
            validate_identifier("   ")

    def test_identifier_custom_field(self):
        with pytest.raises(ValidationError, match="nome"):
            validate_identifier("123", field="nome")

    def test_slug_valid(self):
        assert validate_slug("meu-modulo") == "meu-modulo"
        assert validate_slug("abc-123") == "abc-123"
        assert validate_slug("a") == "a"

    def test_slug_invalid(self):
        with pytest.raises(ValidationError, match="slug"):
            validate_slug("Meu_Modulo")
        with pytest.raises(ValidationError, match="slug"):
            validate_slug("-leading")
        with pytest.raises(ValidationError, match="slug"):
            validate_slug("trailing-")
        with pytest.raises(ValidationError, match="slug"):
            validate_slug("")

    def test_slug_lowercases(self):
        assert validate_slug("ABC-Def") == "abc-def"

    def test_semver_valid(self):
        assert validate_semver("1.2.3") == "1.2.3"
        assert validate_semver("0.0.0") == "0.0.0"
        assert validate_semver("999.999.999") == "999.999.999"

    def test_semver_invalid(self):
        with pytest.raises(ValidationError, match="version"):
            validate_semver("1.2")
        with pytest.raises(ValidationError, match="version"):
            validate_semver("v1.2.3")
        with pytest.raises(ValidationError, match="version"):
            validate_semver("1.2.3-beta")
        with pytest.raises(ValidationError, match="version"):
            validate_semver("")

    def test_hex_color_valid(self):
        assert validate_hex_color("#FFF") == "#FFF"
        assert validate_hex_color("#ff0000") == "#FF0000"
        assert validate_hex_color("#abc123") == "#ABC123"

    def test_hex_color_invalid(self):
        with pytest.raises(ValidationError, match="color"):
            validate_hex_color("red")
        with pytest.raises(ValidationError, match="color"):
            validate_hex_color("#GGG")
        with pytest.raises(ValidationError, match="color"):
            validate_hex_color("")
        with pytest.raises(ValidationError, match="color"):
            validate_hex_color("#1234")


# ── Caminhos ────────────────────────────────────────────────────────


class TestPaths:
    def test_path_exists(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        result = validate_path_exists(f)
        assert result == f

    def test_path_not_exists(self):
        with pytest.raises(ValidationError, match="does not exist"):
            validate_path_exists(Path("/nonexistent/path/xyz123"))

    def test_directory_valid(self, tmp_path):
        result = validate_directory(tmp_path)
        assert result == tmp_path

    def test_directory_is_file(self, tmp_path):
        f = tmp_path / "file.txt"
        f.write_text("x")
        with pytest.raises(ValidationError, match="not a directory"):
            validate_directory(f)

    def test_file_valid(self, tmp_path):
        f = tmp_path / "data.txt"
        f.write_text("data")
        result = validate_file(f)
        assert result == f

    def test_file_is_directory(self, tmp_path):
        with pytest.raises(ValidationError, match="not a file"):
            validate_file(tmp_path)


# ── Numericos ───────────────────────────────────────────────────────


class TestNumeric:
    def test_in_range_ok(self):
        assert validate_in_range(5, 0, 10) == 5
        assert validate_in_range(0, 0, 10) == 0
        assert validate_in_range(10, 0, 10) == 10

    def test_in_range_fail(self):
        with pytest.raises(ValidationError, match="between"):
            validate_in_range(11, 0, 10)

    def test_positive_ok(self):
        assert validate_positive(1) == 1
        assert validate_positive(0.001) == 0.001

    def test_positive_fail(self):
        with pytest.raises(ValidationError, match="positive"):
            validate_positive(0)
        with pytest.raises(ValidationError, match="positive"):
            validate_positive(-1)

    def test_non_negative_ok(self):
        assert validate_non_negative(0) == 0
        assert validate_non_negative(5) == 5

    def test_non_negative_fail(self):
        with pytest.raises(ValidationError, match=">= 0"):
            validate_non_negative(-0.1)

    def test_score_ok(self):
        assert validate_score(0) == 0
        assert validate_score(50) == 50
        assert validate_score(100) == 100

    def test_score_fail(self):
        with pytest.raises(ValidationError, match="between"):
            validate_score(-1)
        with pytest.raises(ValidationError, match="between"):
            validate_score(101)


# ── Strings ─────────────────────────────────────────────────────────


class TestStrings:
    def test_non_empty_ok(self):
        assert validate_non_empty("hello") == "hello"
        assert validate_non_empty(" a ") == "a"

    def test_non_empty_fail(self):
        with pytest.raises(ValidationError, match="empty"):
            validate_non_empty("")
        with pytest.raises(ValidationError, match="empty"):
            validate_non_empty("   ")
        with pytest.raises(ValidationError, match="empty"):
            validate_non_empty(None)

    def test_max_length_ok(self):
        assert validate_max_length("abc", 5) == "abc"
        assert validate_max_length("hello", 5) == "hello"

    def test_max_length_fail(self):
        with pytest.raises(ValidationError, match="exceeds"):
            validate_max_length("toolong", 3)

    def test_min_length_ok(self):
        assert validate_min_length("abc", 2) == "abc"
        assert validate_min_length("ab", 2) == "ab"

    def test_min_length_fail(self):
        with pytest.raises(ValidationError, match="too short"):
            validate_min_length("a", 2)


# ── JSON / Schema ───────────────────────────────────────────────────


class TestJsonAndSchema:
    def test_valid_json_dict(self):
        result = validate_json_string('{"a": 1, "b": "x"}')
        assert result == {"a": 1, "b": "x"}

    def test_valid_json_list(self):
        result = validate_json_string("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_invalid_json(self):
        with pytest.raises(ValidationError, match="JSON"):
            validate_json_string("not json")

    def test_schema_all_fields_present(self):
        data = {"name": "test", "version": "1.0", "active": True}
        result = validate_schema(data, ["name", "version"])
        assert result == data

    def test_schema_missing_fields(self):
        with pytest.raises(ValidationError, match="missing"):
            validate_schema({"name": "test"}, ["name", "version", "count"])

    def test_schema_not_a_dict(self):
        with pytest.raises(ValidationError, match="must be a dict"):
            validate_schema([1, 2, 3], ["name"])


# ── Tipos Genericos ─────────────────────────────────────────────────


class TestGenericTypes:
    def test_validate_type_ok(self):
        assert validate_type(42, int) == 42
        assert validate_type("hello", str) == "hello"
        assert validate_type([1], list) == [1]

    def test_validate_type_fail(self):
        with pytest.raises(ValidationError, match="must be"):
            validate_type("42", int)
        with pytest.raises(ValidationError, match="must be"):
            validate_type(42, str, field="idade")

    def test_one_of_ok(self):
        assert validate_one_of("azul", ["verde", "azul", "vermelho"]) == "azul"
        assert validate_one_of(1, [1, 2, 3]) == 1

    def test_one_of_fail(self):
        with pytest.raises(ValidationError, match="one of"):
            validate_one_of("roxo", ["verde", "azul"])


class TestCustomFieldNames:
    """Testa que o parametro field personaliza a mensagem de erro."""

    def test_identifier_custom_field(self):
        with pytest.raises(ValidationError, match="nome_do_modulo"):
            validate_identifier("123", field="nome_do_modulo")

    def test_score_custom_field(self):
        with pytest.raises(ValidationError, match="confidence"):
            validate_score(200, field="confidence")
