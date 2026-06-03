import pytest
import sys
import os
import json
import tempfile

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, SCRIPTS_DIR)

REFERENCES_DIR = os.path.join(os.path.dirname(__file__), '..', 'references')


class TestAcademicMLPipeline:
    """
    academic-ml-pipeline tests for the 7-stage ML analysis workflow.
    """

    def test_references_exist(self):
        etapas = [
            "etapa1.md", "etapa2.md", "etapa3.md", "etapa4.md",
            "etapa5.md", "etapa6.md", "etapa7.md"
        ]
        for etapa in etapas:
            path = os.path.join(REFERENCES_DIR, etapa)
            assert os.path.exists(path), f"Missing reference: {etapa}"

    def test_references_have_content(self):
        for i in range(1, 8):
            path = os.path.join(REFERENCES_DIR, f"etapa{i}.md")
            with open(path, encoding="utf-8") as f:
                content = f.read()
            assert len(content) > 50, f"etapa{i}.md is too short"

    def test_feature_catalog(self):
        path = os.path.join(REFERENCES_DIR, "feature_catalog.md")
        assert os.path.exists(path)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert len(content) > 20

    def test_results_template_json(self):
        path = os.path.join(REFERENCES_DIR, "results_template.json")
        assert os.path.exists(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, (dict, list))

    def test_skill_metadata(self):
        skill_path = os.path.join(os.path.dirname(__file__), '..', 'SKILL.md')
        assert os.path.exists(skill_path)
        with open(skill_path, encoding="utf-8") as f:
            content = f.read()
        assert "academic-ml-pipeline" in content.lower()
        assert "pipeline" in content.lower()
