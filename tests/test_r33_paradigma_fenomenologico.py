"""
Testes TDD para R33: Paradigma Fenomenológico.
SPEC-076 (Fenomenológico como paradigma completo).
"""

import os
import pytest


class TestFenomenologicoParadigma:
    """CTs para SPEC-076: Paradigma Fenomenológico."""

    SPEC = "specs/SPEC-076-PARADIGMA-FENOMENOLOGICO.md"
    SKILL = "skills/research/fenomenologico-paradigma/SKILL.md"

    def test_ct01_spec_exists(self):
        """CT-01: SPEC-076 deve existir com metadados."""
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-076" in c
        assert "Active" in c

    def test_ct02_keywords(self):
        """CT-02: Palavras-chave incluem 'fenomenológico' e 'Husserl'."""
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "fenomenológico" in c or "fenomenologico" in c
        assert "husserl" in c

    def test_ct03_enables_metodo(self):
        """CT-03: Regra enables para metodos.Fenomenologico registrada."""
        with open(self.SPEC) as f:
            c = f.read()
        assert "enables" in c
        assert "metodos.Fenomenologico" in c

    def test_ct04_co_occurs(self):
        """CT-04: Regra co_occurs com paradigmas.Interpretativista."""
        with open(self.SPEC) as f:
            c = f.read()
        assert "co_occurs" in c
        assert "Interpretativista" in c

    def test_ct05_skill_exists(self):
        """CT-05: Skill fenomenológico como paradigma existe com frontmatter."""
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "fenomenologico-paradigma" in c or "fenomenológico" in c
        assert "SPEC-076" in c

    def test_ct06_husserl(self):
        """CT-06: Template de análise husserliana existe."""
        with open(self.SKILL) as f:
            c = f.read()
        assert "Husserl" in c

    def test_ct07_enactive(self):
        """CT-07: Template de IA enativa (4E cognition) existe."""
        with open(self.SKILL) as f:
            c = f.read()
        assert "enativa" in c.lower() or "4E" in c or "Enactive" in c

    def test_ct08_distinction(self):
        """CT-08: Distinção método vs paradigma documentada."""
        with open(self.SKILL) as f:
            c = f.read()
        assert "método" in c.lower() or "metodo" in c.lower()
        assert "paradigma" in c.lower()
        assert "SPEC-070" in c or "SPEC-076" in c
