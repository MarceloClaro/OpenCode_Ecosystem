import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from dataclasses import asdict
from edital_search import (
    Edital, classificar, calcular_score, buscar_sync,
    _carregar_curados, _buscar_curados, CACHE_VERSION
)


class TestEditalSearch:
    def setup_method(self):
        self.edital = Edital(
            titulo="Edital FAPESP Bolsa Mestrado IA em Saude",
            url="https://fapesp.br/edital-ia-saude-2026",
            portal="fapesp",
        )

    def test_edital_dataclass(self):
        assert self.edital.titulo.startswith("Edital")
        assert self.edital.url.startswith("https://")
        assert self.edital.score == 50.0
        assert self.edital.fonte == "web"

    def test_classificar_dimensoes(self):
        dims = classificar(
            "Edital FAPESP Bolsa Mestrado IA em Saude",
            "https://fapesp.br/edital-ia-saude-2026"
        )
        assert "area" in dims
        assert "perfil" in dims
        assert "mecanismo" in dims
        assert "abrangencia" in dims
        assert "status" in dims
        for area_found in dims["area"]:
            assert isinstance(area_found, str)
            assert area_found != ""

    def test_calcular_score_range(self):
        dims = classificar("Pesquisa IA", "https://exemplo.com/edital")
        score = calcular_score(dims, tipo="pesquisa", perfil="pesquisador")
        assert 0.0 <= score <= 100.0
        assert isinstance(score, (int, float))

    def test_curadoria_disponivel(self):
        curados = _carregar_curados()
        assert isinstance(curados, list)
        if len(curados) > 0:
            assert "titulo" in curados[0]
            assert "url" in curados[0]

    def test_buscar_curados_fallback(self):
        resultados = _buscar_curados("IA saude", max_results=5)
        assert isinstance(resultados, list)
        for r in resultados:
            assert "titulo" in r
            assert "url" in r
            assert r.get("fonte") == "curadoria"

    def test_cache_version(self):
        assert CACHE_VERSION == "v7.1"
