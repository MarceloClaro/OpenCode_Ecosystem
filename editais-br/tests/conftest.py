"""Configurações globais de teste."""

import pytest


@pytest.fixture
def project_root():
    """Retorna o diretório raiz do projeto."""
    from pathlib import Path
    return Path(__file__).parents[1]
