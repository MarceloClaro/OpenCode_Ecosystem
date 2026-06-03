"""
test_domain_shift_camada1b.py — TDD suite for SPEC-008-B
Camada 1B: Decomposicao Institucional para Deteccao de Domain Shift
9 CTs (CT-8B.1 a CT-8B.9)
"""
import json
import sys
import os
import random
import pytest
import numpy as np

# Adiciona o diretorio do script ao path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Importa o modulo de auditoria
import domain_shift_audit as dsa
from domain_shift_audit import (
    gerar_corpus, decompor_variancia, bootstrap_limiar_jaccard,
    aplicar_regra_decisao, BootstrapThresholds, jaccard
)


class TestCT8B1_InstituicoesExclusivas:
    """CT-8B.1: Decomposicao identifica instituicoes exclusivas de T2."""

    def test_trf6_detectada_como_apenas_t2(self):
        """RED->GREEN: TRF-6 deve aparecer em apenas_T2."""
        corpus = gerar_corpus(n_docs_por_inst_ano=20)
        decomp = decompor_variancia(corpus)

        assert "TRF-6" in decomp["instituicoes_em_t2"], \
            "TRF-6 deveria estar em T2"
        assert "TRF-6" in decomp["instituicoes_apenas_t2"], \
            "TRF-6 deveria ser exclusiva de T2"
        assert "TRF-6" not in decomp["instituicoes_em_t1"], \
            "TRF-6 nao deveria estar em T1"


class TestCT8B2_DeltaTemporal:
    """CT-8B.2: Delta temporal computado apenas para s em ambos os periodos."""

    def test_delta_temporal_apenas_para_instituicoes_em_ambos(self):
        """RED->GREEN: Delta temporal so existe para inst em T1 e T2."""
        corpus = gerar_corpus(n_docs_por_inst_ano=20)
        decomp = decompor_variancia(corpus)

        # Instituicoes em ambos os periodos
        inst_ambos = set(decomp["instituicoes_em_t1"]) & set(decomp["instituicoes_em_t2"])

        for inst_key in inst_ambos:
            assert inst_key in decomp["deltas_temporal"], \
                f"{inst_key} deveria ter delta temporal"

        # TRF-6 nao deve ter delta temporal
        assert "TRF-6" not in decomp["deltas_temporal"], \
            "TRF-6 nao deveria ter delta temporal (so existe em T2)"


class TestCT8B3_DistribuicaoNula:
    """CT-8B.3: Distribuicao nula tem pelo menos 2 pares."""

    def test_distribuicao_nula_tem_minimo_2_pares(self):
        """RED->GREEN: len(null) >= 2 para bootstrap viavel."""
        corpus = gerar_corpus(n_docs_por_inst_ano=20)
        decomp = decompor_variancia(corpus)

        jaccards_nulos = [d["jaccard"] for d in decomp["deltas_cross_inst"]]
        assert len(jaccards_nulos) >= 2, \
            f"Distribuicao nula precisa de >=2 pares, tem {len(jaccards_nulos)}"


class TestCT8B4_LimiaresMonotonicos:
    """CT-8B.4: Bootstrap gera limiares monotonicos."""

    def test_limiares_monotonicos(self):
        """RED->GREEN: P50 <= P75 <= P90 <= P95 <= P99."""
        corpus = gerar_corpus(n_docs_por_inst_ano=20)
        decomp = decompor_variancia(corpus)
        jaccards_nulos = [d["jaccard"] for d in decomp["deltas_cross_inst"]]

        thresholds = bootstrap_limiar_jaccard(jaccards_nulos)

        assert thresholds.percentil_50 <= thresholds.percentil_75, \
            "P50 deve ser <= P75"
        assert thresholds.percentil_75 <= thresholds.percentil_90, \
            "P75 deve ser <= P90"
        assert thresholds.percentil_90 <= thresholds.percentil_95, \
            "P90 deve ser <= P95"
        assert thresholds.percentil_95 <= thresholds.percentil_99, \
            "P95 deve ser <= P99"
        assert thresholds.recomendado_estrito >= thresholds.recomendado_moderado, \
            "Estrito deve ser >= Moderado"


class TestCT8B5_ShiftConhecido:
    """CT-8B.5: Instituicoes com shift conhecido tem delta_t menor que sem shift."""

    def test_stf_com_shift_tem_delta_menor_que_tjsp_sem_shift(self):
        """RED->GREEN: delta_t(STF) < delta_t(TJ-SP)."""
        corpus = gerar_corpus(n_docs_por_inst_ano=40)
        decomp = decompor_variancia(corpus)

        dt_stf = decomp["deltas_temporal"]["STF"]["jaccard"]
        dt_tjsp = decomp["deltas_temporal"]["TJ-SP"]["jaccard"]

        # STF tem shift_2024 (novos templates), TJ-SP nao
        assert dt_stf < dt_tjsp, \
            f"STF com shift ({dt_stf:.4f}) deveria ter Jaccard < TJ-SP sem shift ({dt_tjsp:.4f})"


class TestCT8B6_EvidenciaForteApesarShift:
    """CT-8B.6: Delta_t(STF) > P99 para corpus com shift moderado."""

    def test_stf_acima_limiar_estrito(self):
        """RED->GREEN: Apesar do shift, STF passa no limiar estrito."""
        corpus = gerar_corpus(n_docs_por_inst_ano=40)
        decomp = decompor_variancia(corpus)
        jaccards_nulos = [d["jaccard"] for d in decomp["deltas_cross_inst"]]
        thresholds = bootstrap_limiar_jaccard(jaccards_nulos)

        dt_stf = decomp["deltas_temporal"]["STF"]["jaccard"]
        assert dt_stf > thresholds.recomendado_estrito, \
            f"STF ({dt_stf:.4f}) deveria > P99 ({thresholds.recomendado_estrito:.4f})"


class TestCT8B7_TRF6_SemBaseline:
    """CT-8B.7: TRF-6 classificada como 'sem baseline temporal'."""

    def test_trf6_sem_baseline_temporal(self):
        """RED->GREEN: TRF-6 diagnosticada como aguardar T3."""
        corpus = gerar_corpus(n_docs_por_inst_ano=40)
        decomp = decompor_variancia(corpus)
        jaccards_nulos = [d["jaccard"] for d in decomp["deltas_cross_inst"]]
        thresholds = bootstrap_limiar_jaccard(jaccards_nulos)
        decisoes = aplicar_regra_decisao(decomp, thresholds)

        trf6_decision = [d for d in decisoes if d["instituicao"] == "TRF-6"]
        assert len(trf6_decision) == 0, \
            "TRF-6 nao deveria ter decisao (sem baseline temporal)"


class TestCT8B8_RelatorioTransparencia:
    """CT-8B.8: Relatorio de transparencia inclui limiar calibrado e D_null."""

    def test_relatorio_contem_campos_obrigatorios(self):
        """RED->GREEN: >= 5 campos obrigatorios no relatorio."""
        corpus = gerar_corpus(n_docs_por_inst_ano=40)
        decomp = decompor_variancia(corpus)
        jaccards_nulos = [d["jaccard"] for d in decomp["deltas_cross_inst"]]
        thresholds = bootstrap_limiar_jaccard(jaccards_nulos)

        # Verifica campos obrigatorios
        assert thresholds.n_bootstrap > 0, "n_bootstrap ausente"
        assert thresholds.media_distribuicao_nula >= 0, "media ausente"
        assert thresholds.std_distribuicao_nula >= 0, "std ausente"
        assert thresholds.recomendado_moderado > 0, "limiar moderado ausente"
        assert thresholds.recomendado_estrito > 0, "limiar estrito ausente"
        assert len(jaccards_nulos) > 0, "D_null vazia"


class TestCT8B9_Reprodutibilidade:
    """CT-8B.9: Reproducibilidade — mesma seed -> mesmos resultados."""

    def test_mesma_seed_mesmo_jaccard(self):
        """RED->GREEN: Dois corpora com mesma seed tem mesmos deltas."""
        # Reseta tudo: modulo cache, random, numpy
        dsa._template_pool_cache.clear()
        random.seed(42)
        np.random.seed(42)
        corpus1 = gerar_corpus(n_docs_por_inst_ano=20)
        decomp1 = decompor_variancia(corpus1)

        dsa._template_pool_cache.clear()
        random.seed(42)
        np.random.seed(42)
        corpus2 = gerar_corpus(n_docs_por_inst_ano=20)
        decomp2 = decompor_variancia(corpus2)

        # STF deve ter mesmo Jaccard
        j1 = decomp1["deltas_temporal"]["STF"]["jaccard"]
        j2 = decomp2["deltas_temporal"]["STF"]["jaccard"]
        assert j1 == j2, \
            f"Mesma seed deveria produzir mesmo Jaccard: {j1} != {j2}"

        # Cross-inst T1 deve ser identico
        cross1 = sorted([d["jaccard"] for d in decomp1["deltas_cross_inst"]])
        cross2 = sorted([d["jaccard"] for d in decomp2["deltas_cross_inst"]])
        assert cross1 == cross2, \
            "Cross-inst deveria ser identico com mesma seed"
