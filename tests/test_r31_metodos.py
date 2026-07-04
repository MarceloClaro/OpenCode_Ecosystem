"""
Testes TDD para R31: Métodos Qualitativos Restantes.
SPEC-070 (Fenomenológico), SPEC-071 (Grounded Theory),
SPEC-072 (Estudo de Caso), SPEC-073 (Pesquisa-Ação).
"""

import os
import pytest


class TestFenomenologico:
    """CTs para SPEC-070: Método Qualitativo Fenomenológico."""

    SPEC = "specs/SPEC-070-METODO-FENOMENOLOGICO.md"
    SKILL = "skills/research/analise-fenomenologica/SKILL.md"

    def test_ct01_spec_exists(self):
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-070" in c
        assert "Active" in c

    def test_ct02_keywords(self):
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "fenomenológico" in c
        assert "qualitativo" in c

    def test_ct03_skill_exists(self):
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "analise-fenomenologica" in c

    def test_ct04_rules_qual(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "Qualitativo fenomenológico" in c
        assert "enables" in c


class TestGroundedTheory:
    """CTs para SPEC-071: Grounded Theory."""

    SPEC = "specs/SPEC-071-METODO-GROUNDED-THEORY.md"
    SKILL = "skills/research/grounded-theory/SKILL.md"

    def test_ct01_spec_exists(self):
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-071" in c
        assert "Active" in c

    def test_ct02_keywords(self):
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "grounded theory" in c
        assert "qualitativo" in c

    def test_ct03_skill_exists(self):
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "grounded-theory" in c

    def test_ct04_rules_qual(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "Qualitativo grounded theory" in c
        assert "enables" in c


class TestEstudoCaso:
    """CTs para SPEC-072: Estudo de Caso."""

    SPEC = "specs/SPEC-072-METODO-ESTUDO-CASO.md"
    SKILL = "skills/research/estudo-de-caso/SKILL.md"

    def test_ct01_spec_exists(self):
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-072" in c
        assert "Active" in c

    def test_ct02_keywords(self):
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "estudo de caso" in c
        assert "yin" in c

    def test_ct03_skill_exists(self):
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "estudo-de-caso" in c

    def test_ct04_rules_qual(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "Estudo de caso" in c
        assert "enables" in c


class TestPesquisaAcao:
    """CTs para SPEC-073: Pesquisa-Ação."""

    SPEC = "specs/SPEC-073-METODO-PESQUISA-ACAO.md"
    SKILL = "skills/research/pesquisa-acao/SKILL.md"

    def test_ct01_spec_exists(self):
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-073" in c
        assert "Active" in c

    def test_ct02_keywords(self):
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "pesquisa-ação" in c
        assert "ciclo reflexivo" in c

    def test_ct03_skill_exists(self):
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "pesquisa-acao" in c

    def test_ct04_rules_qual(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "Pesquisa-ação" in c
        assert "enables" in c
