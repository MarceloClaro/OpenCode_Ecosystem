import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from uv_installer import UVInstaller


class TestUVInstaller:
    def setup_method(self):
        self.uv = UVInstaller(uv_cmd="uv")

    def test_available(self):
        assert isinstance(self.uv.available, bool)

    def test_uv_command_is_string(self):
        assert isinstance(self.uv.uv_command, str)

    def test_install_method_returns_dict(self):
        result = self.uv.install(["nonexistent-package-xyz"])
        assert isinstance(result, dict)

    def test_install_has_status(self):
        result = self.uv.install(["nonexistent-package-xyz"])
        assert "status" in result

    def test_install_empty_packages(self):
        result = self.uv.install([])
        assert isinstance(result, dict)

    def test_install_empty_packages_error(self):
        result = self.uv.install([])
        assert result.get("status") == "error"
        assert "No packages" in result.get("message", "")

    def test_list_installed_returns_dict(self):
        result = self.uv.list_installed(timeout=30)
        assert isinstance(result, dict)

    def test_list_installed_has_status(self):
        result = self.uv.list_installed(timeout=30)
        assert "status" in result

    def test_version_returns_str_or_none(self):
        ver = self.uv.version
        assert ver is None or isinstance(ver, str)

    def test_uv_not_available_install(self):
        fake = UVInstaller(uv_cmd="uv_nonexistent_xyz")
        if not fake.available:
            result = fake.install(["pkg"])
            assert result.get("status") == "error"
            assert "not installed" in result.get("message", "")
