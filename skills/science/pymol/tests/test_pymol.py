import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from pymol_renderer import PyMOLRenderer


class TestPyMOLRenderer:
    def setup_method(self):
        self.renderer = PyMOLRenderer(pymol_cmd="pymol")

    def test_available(self):
        assert isinstance(self.renderer.available, bool)

    def test_pymol_command_is_string(self):
        assert isinstance(self.renderer.pymol_command, str)

    def test_render_returns_dict(self):
        result = self.renderer.render("nonexistent.pdb")
        assert isinstance(result, dict)

    def test_render_has_status(self):
        result = self.renderer.render("nonexistent.pdb")
        assert "status" in result

    def test_bad_file_handled(self):
        result = self.renderer.render("/nonexistent/path/file.pdb")
        assert "status" in result

    def test_bad_file_returns_error(self):
        result = self.renderer.render("/nonexistent/path/file.pdb")
        assert result.get("file") is None

    def test_missing_file_error(self):
        result = self.renderer.render("missing.pdb")
        assert "message" in result

    def test_render_with_output_path(self):
        result = self.renderer.render("nonexistent.pdb", output="/tmp/test.png")
        assert isinstance(result, dict)

    def test_render_with_custom_params(self):
        result = self.renderer.render(
            "nonexistent.pdb",
            width=800,
            height=600,
            dpi=150,
            representation="surface",
            color_scheme="spectrum",
            background="black",
            ray_trace=False,
        )
        assert isinstance(result, dict)
