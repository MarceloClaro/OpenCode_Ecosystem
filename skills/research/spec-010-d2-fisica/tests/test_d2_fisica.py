import pytest, os


class TestSpecD2Fisica:
    """Validacao estrutural da skill spec-010-d2-fisica."""

    def test_skill_exists(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        assert os.path.exists(path), "SKILL.md nao encontrado"

    def test_has_category(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        content = open(path, encoding='utf-8').read()
        assert 'category: research' in content

    def test_has_version(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        content = open(path, encoding='utf-8').read()
        assert 'version:' in content

    def test_has_spec_id(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        content = open(path, encoding='utf-8').read()
        assert 'SPEC-010' in content or 'spec-010' in content
