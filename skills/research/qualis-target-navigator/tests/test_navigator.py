import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from navigator import (
    Journal, ManuscriptProfile, JournalScore,
    score_journal, rank_journals,
    jaccard_similarity, normalizar_tempo, normalizar_aceitacao,
    normalizar_apc, inferir_area_capes,
    QUALIS_SCORE, QUALIS_ORDER, CAPES_AREAS, PESOS
)


class TestNavigator:
    def setup_method(self):
        self.manuscript = ManuscriptProfile(
            titulo="IA na Educacao Superior",
            abstract="Estudo sobre impacto de IA generativa no ensino superior brasileiro...",
            keywords=["inteligencia artificial", "educacao superior", "chatgpt",
                      "ensino", "tecnologia educacional", "formacao docente"],
            area_capes="EDUCACAO"
        )
        self.journals = [
            Journal("Computers & Education", "0360-1315", "A1", "EDUCACAO",
                    ["educacao", "tecnologia", "computador", "ensino", "aprendizagem", "digital"],
                    apc_brl=18000, tempo_medio_resposta_meses=4,
                    taxa_aceitacao_pct=15, cite_score=17.6, sjr=3.02),
            Journal("Educacao & Sociedade", "0101-7330", "A1", "EDUCACAO",
                    ["educacao", "sociedade", "politica educacional", "formacao", "ensino"],
                    acesso_aberto=True, apc_brl=0,
                    tempo_medio_resposta_meses=8, taxa_aceitacao_pct=25,
                    cite_score=1.2, sjr=0.32),
            Journal("Revista Brasileira de Informatica na Educacao", "1414-5685", "A2", "EDUCACAO",
                    ["informatica", "educacao", "tecnologia", "ensino", "computador", "ia"],
                    acesso_aberto=True, apc_brl=0,
                    tempo_medio_resposta_meses=5, taxa_aceitacao_pct=30,
                    cite_score=1.5, sjr=0.28),
        ]

    def test_jaccard_similarity(self):
        a = ["inteligencia artificial", "educacao", "ensino"]
        b = ["educacao", "tecnologia", "ensino", "aprendizagem"]
        sim = jaccard_similarity(a, b)
        assert 0.0 <= sim <= 1.0
        assert sim > 0.0

        c = ["completamente", "diferente"]
        sim2 = jaccard_similarity(a, c)
        assert sim2 == 0.0

    def test_normalizadores_range(self):
        assert normalizar_tempo(6) == pytest.approx(0.75)
        assert normalizar_tempo(0) == 1.0
        assert normalizar_tempo(48) == 0.0

        assert normalizar_aceitacao(30) == pytest.approx(0.5)
        assert normalizar_aceitacao(60) == 1.0

        assert normalizar_apc(0) == 1.0
        assert normalizar_apc(6000) == 0.0

    def test_score_journal(self):
        result = score_journal(self.manuscript, self.journals[0])
        assert isinstance(result, JournalScore)
        assert 0.0 <= result.score_total <= 1.0
        assert result.score_qualis == QUALIS_SCORE[self.journals[0].qualis]
        assert result.score_scope >= 0.0
        assert result.justificativa != ""

    def test_rank_journals(self):
        ranked = rank_journals(self.manuscript, self.journals, top_n=3)
        assert len(ranked) == 3
        for i in range(len(ranked) - 1):
            assert ranked[i].score_total >= ranked[i + 1].score_total
        assert ranked[0].journal.qualis in QUALIS_SCORE

    def test_inferir_area_capes(self):
        area = inferir_area_capes(["inteligencia artificial", "computacao", "dados"])
        assert isinstance(area, str)
        assert len(area) > 0

        area_vazia = inferir_area_capes([])
        assert area_vazia == "INTERDISCIPLINAR"

    def test_pesos_somam(self):
        soma = sum(PESOS.values())
        assert soma == pytest.approx(1.0)

    def test_areas_capes_disponiveis(self):
        assert isinstance(CAPES_AREAS, list)
        assert len(CAPES_AREAS) > 30
        assert "CIENCIA DA COMPUTACAO" in CAPES_AREAS
        assert "EDUCACAO" in CAPES_AREAS

    def test_qualis_order(self):
        assert QUALIS_ORDER[0] == "A1"
        assert QUALIS_ORDER[-1] == "C"
        assert QUALIS_SCORE["A1"] == 1.0
        assert QUALIS_SCORE["C"] == 0.0
