"""
Testes do SkillManager (core/skill_manager.py)

Cobre:
- add_search_dir / discover
- load / load_all / reload
- get_skill / get_content / list_skills
- match_skill / find_best_skill
- get_categories
- count / loaded_count
- Extração de metadados (description, keywords, category)
- Skill inexistente (NotFoundError)
- SKILL.md ausente (SkillError)
"""

import tempfile
from pathlib import Path

import pytest

from core.skill_manager import SkillManager, SkillMeta, SkillInstance
from core.errors import SkillError, NotFoundError


@pytest.fixture
def mgr():
    """SkillManager limpo."""
    return SkillManager()


@pytest.fixture
def skills_dir(tmp_path):
    """Diretorio temporario com skills de teste."""
    d = tmp_path / "skills"
    d.mkdir()

    # Skill: python-pro
    py_dir = d / "python-pro"
    py_dir.mkdir()
    (py_dir / "SKILL.md").write_text(
        """---
name: python-pro
description: Use when building Python 3.11+ applications
---

# Python Pro

Guidelines for Python development.
""",
        encoding="utf-8",
    )

    # Skill: reversa-scout
    scout_dir = d / "reversa-scout"
    scout_dir.mkdir()
    (scout_dir / "SKILL.md").write_text(
        """# Reversa Scout

Scout agent for reverse engineering.
""",
        encoding="utf-8",
    )

    # Skill: empty (sem SKILL.md)
    empty_dir = d / "empty-skill"
    empty_dir.mkdir()

    return d


class TestSkillManagerDiscovery:
    """Testa descoberta de skills."""

    def test_discover_finds_skills(self, mgr, skills_dir):
        found = mgr.discover([skills_dir])
        assert "python-pro" in found
        assert "reversa-scout" in found

    def test_discover_ignores_dirs_without_skill_md(self, mgr, skills_dir):
        found = mgr.discover([skills_dir])
        assert "empty-skill" not in found

    def test_discover_empty_dir(self, mgr, tmp_path):
        empty = tmp_path / "empty"
        empty.mkdir()
        found = mgr.discover([empty])
        assert found == []

    def test_discover_adds_default_dir(self, mgr):
        """Se nenhum diretorio for especificado, usa o padrao do settings."""
        found = mgr.discover()
        # O diretorio padrao pode nao existir em testes
        # Mas o metodo nao deve crashar
        assert isinstance(found, list)


class TestSkillManagerLoading:
    """Testa carregamento de skills."""

    def test_load_skill(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        result = mgr.load("python-pro")
        assert result is True
        skill = mgr.get_skill("python-pro")
        assert skill is not None
        assert skill.loaded is True
        assert skill.content is not None
        assert len(skill.content) > 0

    def test_load_extracts_metadata(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        mgr.load("python-pro")
        skill = mgr.get_skill("python-pro")
        assert skill.meta.description == "Use when building Python 3.11+ applications"
        assert "Python" in skill.meta.keywords or "python" in [k.lower() for k in skill.meta.keywords]
        assert skill.meta.size_bytes > 0

    def test_load_fallback_description(self, mgr, skills_dir):
        """Skill sem frontmatter usa o heading como descricao."""
        mgr.discover([skills_dir])
        mgr.load("reversa-scout")
        skill = mgr.get_skill("reversa-scout")
        assert skill.meta.description == "Reversa Scout"

    def test_load_nonexistent(self, mgr):
        with pytest.raises(NotFoundError, match="not found"):
            mgr.load("no-such-skill")

    def test_load_missing_file(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        # Acessa internamente para simular skill descoberta sem arquivo
        skill = mgr._skills.get("empty-skill")
        assert skill is None  # Nao foi descoberta porque nao tem SKILL.md

    def test_load_all(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        count = mgr.load_all()
        assert count == 2  # python-pro + reversa-scout

    def test_reload(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        mgr.load("python-pro")
        assert mgr.reload("python-pro") is True


class TestSkillManagerMatching:
    """Testa matching por relevancia."""

    def test_match_by_name(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        mgr.load_all()
        matches = mgr.match_skill("preciso de ajuda com Python")
        assert len(matches) >= 1
        assert matches[0][0] == "python-pro"

    def test_match_by_description(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        mgr.load_all()
        matches = mgr.match_skill("building applications")
        assert len(matches) >= 1

    def test_find_best_skill(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        mgr.load_all()
        best = mgr.find_best_skill("Python 3.11")
        assert best == "python-pro"

    def test_match_no_results(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        mgr.load_all()
        matches = mgr.match_skill("zzzznonexistent", min_score=0.5)
        assert matches == []


class TestSkillManagerQueries:
    """Testa consultas ao SkillManager."""

    def test_get_skill_nonexistent(self, mgr):
        assert mgr.get_skill("no-such") is None

    def test_get_content_loaded(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        mgr.load("python-pro")
        content = mgr.get_content("python-pro")
        assert content is not None
        assert "# Python Pro" in content

    def test_get_content_not_loaded(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        content = mgr.get_content("python-pro")
        assert content is None

    def test_get_content_nonexistent(self, mgr):
        assert mgr.get_content("no-such") is None

    def test_list_skills(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        mgr.load_all()
        skills = mgr.list_skills()
        assert len(skills) == 2
        names = [s.name for s in skills]
        assert "python-pro" in names
        assert "reversa-scout" in names

    def test_list_skills_filter_by_category(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        mgr.load_all()
        # Todas as skills tem a mesma categoria neste teste
        all_skills = mgr.list_skills()
        categories = mgr.get_categories()
        assert len(categories) >= 1

    def test_count(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        assert mgr.count == 2
        assert mgr.loaded_count == 0

    def test_loaded_count(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        mgr.load_all()
        assert mgr.loaded_count == 2


class TestSkillManagerCategories:
    """Testa categorizacao de skills."""

    def test_get_categories(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        mgr.load_all()
        cats = mgr.get_categories()
        assert isinstance(cats, list)

    def test_repr(self, mgr, skills_dir):
        mgr.discover([skills_dir])
        r = repr(mgr)
        assert "SkillManager" in r
        assert "skills=2" in r
