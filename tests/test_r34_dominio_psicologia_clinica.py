"""
Testes TDD para R34: Domínio Psicologia Clínica.
SPEC-077.
"""

import os
import pytest


class TestPsicologiaClinica:
    """CTs para SPEC-077: Domínio Psicologia Clínica."""

    SPEC = "specs/SPEC-077-DOMINIO-PSICOLOGIA-CLINICA.md"
    SKILL = "skills/research/psicologia-clinica/SKILL.md"

    def test_ct01_spec_exists(self):
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-077" in c and "Active" in c

    def test_ct02_keywords(self):
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "psicologia clínica" in c or "psicologia clinica" in c
        assert "dsm-5" in c

    def test_ct03_uses_metodo(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "uses" in c and "Fenomenologico" in c

    def test_ct04_enables_paradigma(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "enables" in c and "Fenomenologico" in c

    def test_ct05_skill_exists(self):
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "psicologia-clinica" in c and "SPEC-077" in c

    def test_ct06_template_avaliacao(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "avaliação" in c.lower() or "avaliacao" in c.lower()

    def test_ct07_template_dsm(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "DSM-5" in c

    def test_ct08_template_qualitativo(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "qualitativ" in c.lower()


class TestDadosQualitativos:
    """CTs para SPEC-078: Dados Qualitativos."""

    SPEC = "specs/SPEC-078-DADOS-QUALITATIVOS.md"
    SKILL = "skills/research/dados-qualitativos/SKILL.md"

    def test_ct01_spec_exists(self):
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-078" in c and "Active" in c

    def test_ct02_keywords(self):
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "dados qualitativos" in c or "dados qualitativos" in c
        assert "entrevista" in c

    def test_ct03_produced_by(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "produced_by" in c and "GroundedTheory" in c

    def test_ct04_requires(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "requires" in c and "Indutivo" in c

    def test_ct05_skill_exists(self):
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "dados-qualitativos" in c and "SPEC-078" in c

    def test_ct06_entrevista(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "entrevista" in c.lower()

    def test_ct07_grupo_focal(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "grupo focal" in c.lower()

    def test_ct08_coreq(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "COREQ" in c


class TestMetaAnalise:
    """CTs para SPEC-079: Meta-análise."""

    SPEC = "specs/SPEC-079-METODO-META-ANALISE.md"
    SKILL = "skills/research/meta-analise/SKILL.md"

    def test_ct01_spec_exists(self):
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-079" in c and "Active" in c

    def test_ct02_keywords(self):
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "meta-análise" in c or "meta-analise" in c
        assert "effect size" in c

    def test_ct03_requires_revisao(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "requires" in c and "RevisaoSistematica" in c

    def test_ct04_requires_probabilistico(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "requires" in c and "Probabilistico" in c

    def test_ct05_skill_exists(self):
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "meta-analise" in c and "SPEC-079" in c

    def test_ct06_forest_plot(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "forest plot" in c.lower()

    def test_ct07_heterogeneidade(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "I²" in c or "heterogeneidade" in c.lower()

    def test_ct08_publication_bias(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "viés" in c.lower() or "funnel" in c.lower() or "Egger" in c
