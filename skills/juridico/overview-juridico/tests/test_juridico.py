import pytest, sys, os

class TestJuridicoOverview:
    def test_skill_exists(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        assert os.path.exists(path), "SKILL.md not found"
    
    def test_frontmatter_has_category(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        with open(path, encoding='utf-8') as f:
            content = f.read()
        assert 'category: juridico' in content

    def test_frontmatter_has_version(self):
        path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        with open(path, encoding='utf-8') as f:
            content = f.read()
        assert 'version:' in content
