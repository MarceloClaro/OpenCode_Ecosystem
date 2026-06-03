import pytest, os


class TestPesquisaJurisprudencia:
    """Validacao estrutural da skill pesquisa-jurisprudencia."""

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

    def test_has_citacao_rules(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        content = open(path, encoding='utf-8').read()
        assert 'Citacao' in content or 'EMENTA' in content
