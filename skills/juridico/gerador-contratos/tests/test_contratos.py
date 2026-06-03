import pytest, os


class TestGeradorContratos:
    """Validacao estrutural da skill gerador-contratos."""

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

    def test_references_exist(self):
        ref_dir = os.path.join(os.path.dirname(__file__), '..', 'references')
        assert os.path.isdir(ref_dir), "diretorio references nao encontrado"
        refs = os.listdir(ref_dir)
        assert len(refs) > 0, "references/ vazio"
