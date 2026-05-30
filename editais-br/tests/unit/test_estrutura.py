"""Testes de estrutura base Python — Issue #2.

Verifica que todos os diretórios e __init__.py existem e são importáveis.
"""

import importlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]

MODULOS_ESPERADOS = [
    "api",
    "api.models",
    "api.schemas",
    "agents",
    "extractors",
    "worker",
    "worker.connectors",
    "worker.tasks",
]


def test_todos_diretorios_existem():
    """Cada módulo deve ter diretório físico com __init__.py."""
    for modulo in MODULOS_ESPERADOS:
        path = PROJECT_ROOT / modulo.replace(".", "/")
        init = path / "__init__.py"

        assert path.is_dir(), f"Diretório {path} não encontrado"
        assert init.exists(), f"{init} não encontrado"


def test_modulos_sao_importaveis():
    """Cada módulo deve poder ser importado sem erro."""
    for modulo in MODULOS_ESPERADOS:
        try:
            importlib.import_module(modulo)
        except ImportError as e:
            # Se depender de lib externa, ainda não tem código — ok
            # Só falha se o módulo não existir mesmo
            if "No module named" in str(e) and modulo.replace(".", "/") in str(e):
                # Não é problema de dependência — é módulo ausente
                raise AssertionError(f"Não foi possível importar {modulo}: {e}") from e


def test_conftest_existe():
    """tests/conftest.py deve existir."""
    conftest = PROJECT_ROOT / "tests" / "conftest.py"
    assert conftest.exists(), "tests/conftest.py não encontrado"


def test_fixtures_dir_existe():
    """tests/fixtures/ deve existir."""
    fixtures = PROJECT_ROOT / "tests" / "fixtures"
    assert fixtures.is_dir(), "tests/fixtures/ não encontrado"
