import pytest
import os

class TestAcademicExportABNT:
    """Validacao basica da skill academic-export-abnt"""

    def test_skill_exists(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        assert os.path.exists(path)

    def test_has_category(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        content = open(path, encoding='utf-8').read()
        assert 'category:' in content or 'categoria:' in content

    def test_templates_exist(self):
        base = os.path.join(os.path.dirname(__file__), '..', 'templates')
        assert os.path.isdir(base)
        templates = os.listdir(base)
        assert len(templates) > 0

    def test_references_exist(self):
        base = os.path.join(os.path.dirname(__file__), '..', 'references')
        assert os.path.isdir(base)
        refs = os.listdir(base)
        assert len(refs) > 0
