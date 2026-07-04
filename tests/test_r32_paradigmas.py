"""
Testes TDD para R32: Paradigmas Restantes.
SPEC-074 (Construtivista), SPEC-075 (Pós-estruturalista).
"""

import os
import pytest


class TestConstrutivista:
    """CTs para SPEC-074: Paradigma Construtivista."""

    SPEC = "specs/SPEC-074-PARADIGMA-CONSTRUTIVISTA.md"
    SKILL = "skills/research/construtivista/SKILL.md"

    def test_ct01_spec_exists(self):
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-074" in c
        assert "Active" in c

    def test_ct02_keywords(self):
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "construtivista" in c
        assert "epistemologia genética" in c or "epistemologia" in c

    def test_ct03_enables_pesquisa_acao(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "enables" in c
        assert "Pesquisa-Ação" in c or "Pesquisa" in c

    def test_ct04_co_occurs_pragmatista(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "co_occurs" in c
        assert "Pragmatista" in c

    def test_ct05_skill_exists(self):
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "construtivista" in c
        assert "SPEC-074" in c

    def test_ct06_template_ciclo(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "Ciclo de Aprendizagem" in c or "assimila" in c.lower()

    def test_ct07_template_design(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "Design Construtivista" in c or "CDM" in c or "MAS" in c


class TestPosEstruturalista:
    """CTs para SPEC-075: Paradigma Pós-estruturalista."""

    SPEC = "specs/SPEC-075-PARADIGMA-POS-ESTRUTURALISTA.md"
    SKILL = "skills/research/pos-estruturalista/SKILL.md"

    def test_ct01_spec_exists(self):
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-075" in c
        assert "Active" in c

    def test_ct02_keywords(self):
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "pós-estruturalista" in c or "pos-estruturalista" in c
        assert "foucault" in c

    def test_ct03_enables_analise_critica(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "enables" in c
        assert "analise.Crítica" in c or "Crítica" in c

    def test_ct04_co_occurs_critico(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "co_occurs" in c
        assert "Crítico" in c or "Critico" in c

    def test_ct05_skill_exists(self):
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "pos-estruturalista" in c or "pós-estruturalista" in c
        assert "SPEC-075" in c

    def test_ct06_foucault_template(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "Foucault" in c or "foucaultiana" in c.lower()

    def test_ct07_derrida_template(self):
        with open(self.SKILL) as f:
            c = f.read()
        assert "Derrida" in c or "desconstrução" in c or "desconstrucao" in c.lower()
