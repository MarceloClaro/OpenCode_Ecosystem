import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from skill_generator import SkillGenerator


class TestSkillGenerator:
    def setup_method(self):
        self.gen = SkillGenerator()

    def test_available(self):
        assert isinstance(self.gen.available, bool)

    def test_available_is_true(self):
        assert self.gen.available is True

    def test_generate_method_returns_dict(self):
        result = self.gen.generate(
            name="test_skill",
            title="Test Skill",
            description="A test skill for validation.",
            class_name="TestClient",
            script_name="test.py",
        )
        assert isinstance(result, dict)

    def test_generate_has_status(self):
        result = self.gen.generate(
            name="test_skill",
            title="Test Skill",
            description="A test skill for validation.",
            class_name="TestClient",
            script_name="test.py",
        )
        assert result.get("status") == "generated"

    def test_generate_has_skill_name(self):
        result = self.gen.generate(
            name="test_skill",
            title="Test Skill",
            description="A test skill.",
            class_name="TestClient",
            script_name="test.py",
        )
        assert result.get("skill_name") == "test_skill"

    def test_generate_has_skill_md(self):
        result = self.gen.generate(
            name="test_skill",
            title="Test Skill",
            description="A test skill.",
            class_name="TestClient",
            script_name="test.py",
        )
        assert isinstance(result.get("skill_md"), str)
        assert len(result["skill_md"]) > 0

    def test_generate_has_script_py(self):
        result = self.gen.generate(
            name="test_skill",
            title="Test Skill",
            description="A test skill.",
            class_name="TestClient",
            script_name="test.py",
        )
        assert isinstance(result.get("script_py"), str)
        assert len(result["script_py"]) > 0
        assert "class TestClient" in result["script_py"]

    def test_generate_has_timestamp(self):
        result = self.gen.generate(
            name="test_skill",
            title="Test Skill",
            description="A test skill.",
            class_name="TestClient",
            script_name="test.py",
        )
        assert "timestamp" in result

    def test_generate_with_custom_params(self):
        result = self.gen.generate(
            name="my_skill",
            title="My Skill",
            description="Custom skill.",
            class_name="MyClient",
            script_name="my_script.py",
            api_url="https://api.example.com",
            api_name="Example API",
            qps=5.0,
        )
        assert result.get("api_url") == "https://api.example.com"
        assert result.get("class_name") == "MyClient"
        assert result.get("script_name") == "my_script.py"

    def test_skill_md_contains_title(self):
        result = self.gen.generate(
            name="my_skill",
            title="My Skill",
            description="Custom skill.",
            class_name="MyClient",
            script_name="my.py",
        )
        assert "My Skill" in result["skill_md"]

    def test_script_py_contains_class(self):
        result = self.gen.generate(
            name="my_skill",
            title="My Skill",
            description="Custom skill.",
            class_name="MyClient",
            script_name="my.py",
        )
        assert "class MyClient" in result["script_py"]
