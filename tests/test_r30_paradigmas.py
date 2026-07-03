"""
Testes TDD para R30: Paradigma Positivista (SPEC-068) e Interpretativista (SPEC-069).
"""

import os
import pytest


class TestPositivista:
    """CTs para SPEC-068: Paradigma Positivista."""

    SPEC = "specs/SPEC-068-PARADIGMA-POSITIVISTA.md"
    SKILL = "skills/research/paradigma-positivista/SKILL.md"

    def test_ct01_spec_exists(self):
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-068" in c
        assert "Active" in c

    def test_ct02_keywords(self):
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "positivista" in c
        assert "falseabilidade" in c or "falseab" in c

    def test_ct03_skill_exists(self):
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "paradigma-positivista" in c

    def test_ct04_rules_quant(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "Quantitativo experimental" in c
        assert "enables" in c


class TestInterpretativista:
    """CTs para SPEC-069: Paradigma Interpretativista."""

    SPEC = "specs/SPEC-069-PARADIGMA-INTERPRETATIVISTA.md"
    SKILL = "skills/research/paradigma-interpretativista/SKILL.md"

    def test_ct01_spec_exists(self):
        assert os.path.exists(self.SPEC)
        with open(self.SPEC) as f:
            c = f.read()
        assert "# SPEC-069" in c
        assert "Active" in c

    def test_ct02_keywords(self):
        with open(self.SPEC) as f:
            c = f.read().lower()
        assert "interpretativista" in c
        assert "fenomenológico" in c or "fenomenol" in c

    def test_ct03_skill_exists(self):
        assert os.path.exists(self.SKILL)
        with open(self.SKILL) as f:
            c = f.read()
        assert "paradigma-interpretativista" in c

    def test_ct04_rules_qual(self):
        with open(self.SPEC) as f:
            c = f.read()
        assert "Qualitativo fenomenológico" in c
        assert "enables" in c
