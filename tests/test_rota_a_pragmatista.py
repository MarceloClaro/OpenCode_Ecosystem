"""
Testes TDD para Rota A1: Paradigma Pragmatista (SPEC-064)
Valida que o artefato de conhecimento do paradigma pragmatista
está presente e é detectável pelo scanner noológico.
"""

import os
import re
import pytest

SPEC_PATH = "specs/SPEC-064-PARADIGMA-PRAGMATISTA.md"
DIMENSOES_PATH = "skills/system/academic-audit/noological_scanner.py"
CROSS_VAL_PATH = "skills/system/academic-audit/cross_validation_engine.py"


class TestPragmatistaSPEC:
    """CTs para SPEC-064: Paradigma Pragmatista."""

    def test_ct01_spec_exists(self):
        """CT-01: SPEC-064 existe com campos obrigatorios."""
        assert os.path.exists(SPEC_PATH), f"Arquivo {SPEC_PATH} nao encontrado"
        with open(SPEC_PATH) as f:
            content = f.read()
        assert "# SPEC-064" in content, "Cabecalho SPEC-064 ausente"
        assert "Active" in content, "Status Active ausente"
        assert "paradigmas" in content, "Dimensao paradigmas ausente"

    def test_ct02_keywords_present(self):
        """CT-02: Palavras-chave incluem 'pragmatista' e 'misto'."""
        with open(SPEC_PATH) as f:
            content = f.read()
        assert "pragmatista" in content.lower(), "Keyword 'pragmatista' ausente"
        assert "misto" in content.lower(), "Keyword 'misto' ausente"
        assert "triangula" in content.lower(), "Keyword 'triangula' ausente"

    def test_ct03_rules_registered(self):
        """CT-03: Regras de validacao cruzada registradas."""
        with open(CROSS_VAL_PATH) as f:
            content = f.read()
        regras_esperadas = [
            'paradigmas.Pragmatista',
            'metodos.Misto sequencial',
            'raciocinio.Abdutivo',
            'metodos.Pesquisa-ação',
        ]
        for regra in regras_esperadas:
            assert regra in content, f"Regra '{regra}' ausente em cross_validation_engine.py"

    def test_ct04_noological_detects(self):
        """CT-04: Scanner noologico inclui Pragmatista como categoria."""
        with open(DIMENSOES_PATH) as f:
            content = f.read()
        assert "Pragmatista" in content, "Pragmatista nao encontrado no noological_scanner.py"

    def test_ct05_rules_enables_misto(self):
        """CT-05: Regra enables para Misto sequencial e convergente."""
        with open(CROSS_VAL_PATH) as f:
            content = f.read()
        assert 'Misto sequencial' in content, 'Regra Misto sequencial ausente'
        assert 'Misto convergente' in content, 'Regra Misto convergente ausente'

    def test_ct06_artifact_diversity(self):
        """CT-06: CognitiveDiversityInjector possui artefato Pragmatista."""
        injector_path = "skills/system/academic-audit/cognitive_diversity_injector.py"
        assert os.path.exists(injector_path)
        with open(injector_path) as f:
            content = f.read()
        assert "Pragmatista" in content, "Nenhum artefato Pragmatista no injector"


class TestRevisaoSistematica:
    """CTs para SPEC-065: Revisao Sistematica."""

    def test_ct01_spec_exists(self):
        assert os.path.exists("specs/SPEC-065-REVISAO-SISTEMATICA.md")

    def test_ct02_skill_exists(self):
        assert os.path.exists("skills/research/revisao-sistematica/SKILL.md")
        with open("skills/research/revisao-sistematica/SKILL.md") as f:
            content = f.read()
        assert "revisao-sistematica" in content
        assert "PRISMA" in content

    def test_ct03_picos_defined(self):
        with open("specs/SPEC-065-REVISAO-SISTEMATICA.md") as f:
            content = f.read()
        assert "PICOS" in content or "picos" in content.lower()


class TestMetodosMistos:
    """CTs para SPEC-066: Metodos Mistos."""

    def test_ct01_spec_exists(self):
        assert os.path.exists("specs/SPEC-066-METODOS-MISTOS.md")

    def test_ct02_skill_exists(self):
        assert os.path.exists("skills/research/metodos-mistos/SKILL.md")
        with open("skills/research/metodos-mistos/SKILL.md") as f:
            content = f.read()
        assert "metodos-mistos" in content
        assert "sequencial" in content

    def test_ct03_triangulation_protocol(self):
        with open("skills/research/metodos-mistos/SKILL.md") as f:
            content = f.read()
        assert "triangulacao" in content.lower() or "triangula" in content.lower()


class TestNeurocienciasDominio:
    """CTs para SPEC-067: Neurociencias como Dominio Cruzado."""

    def test_ct01_spec_exists(self):
        assert os.path.exists("specs/SPEC-067-NEUROCIENCIAS-DOMINIO.md")

    def test_ct02_skill_exists(self):
        assert os.path.exists("skills/research/neurociencias-dominio/SKILL.md")
        with open("skills/research/neurociencias-dominio/SKILL.md") as f:
            content = f.read()
        assert "neurociencias" in content.lower()

    def test_ct03_neuroimaging_methods(self):
        with open("skills/research/neurociencias-dominio/SKILL.md") as f:
            content = f.read()
        assert "fMRI" in content or "EEG" in content


class TestAnaliseQualitativa:
    """CTs para Skill de Analise Qualitativa."""

    def test_ct01_skill_exists(self):
        assert os.path.exists("skills/research/analise-qualitativa/SKILL.md")
        with open("skills/research/analise-qualitativa/SKILL.md") as f:
            content = f.read()
        assert "analise-qualitativa" in content

    def test_ct02_thematic_analysis_template(self):
        with open("skills/research/analise-qualitativa/SKILL.md") as f:
            content = f.read()
        assert "tematica" in content.lower() or "tematic" in content.lower()

    def test_ct03_grounded_theory(self):
        with open("skills/research/analise-qualitativa/SKILL.md") as f:
            content = f.read()
        assert "Grounded" in content or "grounded" in content

    def test_ct04_entry_interview_roteiro(self):
        with open("skills/research/analise-qualitativa/SKILL.md") as f:
            content = f.read()
        assert "entrevista" in content.lower() or "entrevistas" in content.lower()
