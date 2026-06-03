"""
TDD tests for SkillWatcher — Hot-reload de skills com file watcher.
CT-1: test_init — inicializacao de SkillRegistry e SkillWatcher
CT-2: test_watch_directory — scan_once detecta skills no diretorio
CT-3: test_on_change — registro de eventos on_add/on_update/on_remove
CT-4: test_available — validacao de skill com erro de sintaxe
"""

import os
import sys
import tempfile
import shutil
import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

import skill_watcher as sw


class TestSkillRegistry:

    def test_init(self):
        reg = sw.SkillRegistry()
        assert len(reg.list_all()) == 0
        assert len(reg.list_enabled()) == 0

    def test_register_and_get(self):
        reg = sw.SkillRegistry()
        entry = sw.SkillEntry(name="test-skill", path="/fake/path", kind="python")
        reg.register(entry)
        assert reg.get("test-skill") is not None
        assert reg.get("test-skill").name == "test-skill"
        assert len(reg.list_all()) == 1

    def test_unregister(self):
        reg = sw.SkillRegistry()
        entry = sw.SkillEntry(name="test-skill", path="/fake/path", kind="python")
        reg.register(entry)
        reg.unregister("test-skill")
        assert reg.get("test-skill") is None

    def test_callback_fire(self):
        reg = sw.SkillRegistry()
        events = []

        def on_add(e):
            events.append(("add", e.name))

        reg.on("on_add", on_add)
        entry = sw.SkillEntry(name="cb-skill", path="/tmp", kind="python")
        reg.register(entry)
        assert ("add", "cb-skill") in events

    def test_to_dict(self):
        reg = sw.SkillRegistry()
        entry = sw.SkillEntry(name="s1", path="/tmp/s1", kind="python", version="1.0.0")
        reg.register(entry)
        d = reg.to_dict()
        assert "s1" in d
        assert d["s1"]["version"] == "1.0.0"


class TestSkillParser:

    def test_parse_without_skill_md(self):
        with tempfile.TemporaryDirectory() as d:
            result = sw.SkillParser.parse(sw.Path(d))
            assert result is None

    def test_detect_kind_python(self):
        with tempfile.TemporaryDirectory() as d:
            scripts = sw.Path(d) / "scripts"
            scripts.mkdir()
            (scripts / "mod.py").touch()
            kind = sw.SkillParser._detect_kind(sw.Path(d))
            assert kind == "python"


class TestSkillValidator:

    def test_valid_python_skill(self):
        with tempfile.TemporaryDirectory() as d:
            scripts = sw.Path(d) / "scripts"
            scripts.mkdir()
            (scripts / "ok.py").write_text("x = 1\n", encoding="utf-8")

            entry = sw.SkillEntry(name="valid", path=d, kind="python")
            result = sw.SkillValidator.validate(entry)
            assert result.is_valid
            assert result.enabled is True
            assert result.error is None

    def test_invalid_python_syntax(self):
        with tempfile.TemporaryDirectory() as d:
            scripts = sw.Path(d) / "scripts"
            scripts.mkdir()
            (scripts / "broken.py").write_text("def foo(\n", encoding="utf-8")

            entry = sw.SkillEntry(name="broken", path=d, kind="python")
            result = sw.SkillValidator.validate(entry)
            assert not result.is_valid
            assert result.enabled is False
            assert result.error is not None


class TestSkillWatcher:

    def test_init(self):
        reg = sw.SkillRegistry()
        w = sw.SkillWatcher(skills_root="/tmp/nonexistent", registry=reg, interval=0.1)
        assert w._root == sw.Path("/tmp/nonexistent")
        assert w._registry is reg

    def test_watch_directory(self):
        with tempfile.TemporaryDirectory() as d:
            skill_dir = sw.Path(d) / "sample-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nversion: 0.2.0\n---\n# Sample Skill\n", encoding="utf-8"
            )

            reg = sw.SkillRegistry()
            w = sw.SkillWatcher(skills_root=d, registry=reg, interval=0.1)
            changes = w.scan_once()
            assert "sample-skill" in changes
            assert changes["sample-skill"] == "added"

    def test_on_change(self):
        with tempfile.TemporaryDirectory() as d:
            skill_dir = sw.Path(d) / "change-skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(
                "---\nversion: 0.1.0\n---\n# Change Test\n", encoding="utf-8"
            )

            reg = sw.SkillRegistry()
            w = sw.SkillWatcher(skills_root=d, registry=reg, interval=0.1)

            changes = w.scan_once()
            assert changes["change-skill"] == "added"

            skill_md.write_text(
                "---\nversion: 0.2.0\n---\n# Updated\n", encoding="utf-8"
            )
            changes2 = w.scan_once()
            assert changes2["change-skill"] == "modified"

            shutil.rmtree(str(skill_dir))
            changes3 = w.scan_once()
            assert changes3["change-skill"] == "removed"

    def test_available(self):
        reg = sw.SkillRegistry()
        from skill_watcher import create_watcher_for_ecosystem
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            watcher, registry = create_watcher_for_ecosystem(d)
            assert isinstance(watcher, sw.SkillWatcher)
            assert isinstance(registry, sw.SkillRegistry)
            watcher.stop()
