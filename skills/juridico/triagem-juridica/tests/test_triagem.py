import pytest, os


class TestTriagemJuridica:
    """Validacao estrutural da skill triagem-juridica."""

    def test_skill_exists(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        assert os.path.exists(path), "SKILL.md nao encontrado"

    def test_has_category(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        content = open(path, encoding='utf-8').read()
        assert 'category: juridico' in content

    def test_has_version(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        content = open(path, encoding='utf-8').read()
        assert 'version:' in content

    def test_has_compliance_oab(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        content = open(path, encoding='utf-8').read()
        assert 'OAB' in content or 'compliance' in content.lower()
