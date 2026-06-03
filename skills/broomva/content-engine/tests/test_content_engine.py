"""
TDD tests for content-engine compile-dna.py and compose-video.py scripts.
"""
import sys
from pathlib import Path
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))


class TestCompileDnaModule:
    """Tests for compile-dna.py script functions."""

    def test_module_imports(self):
        """compile-dna.py should be importable."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "compile_dna", SCRIPTS_DIR / "compile-dna.py"
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            pytest.fail(f"compile-dna.py failed to import: {e}")

    def test_hash_file_produces_deterministic_hash(self, tmp_path):
        """hash_file should produce consistent SHA-256 hashes."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "compile_dna", SCRIPTS_DIR / "compile-dna.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        h1 = mod.hash_file(test_file)
        h2 = mod.hash_file(test_file)
        assert h1 == h2
        assert len(h1) == 16

    def test_hash_file_different_content_produces_different_hash(self, tmp_path):
        """Different file content should produce different hashes."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "compile_dna", SCRIPTS_DIR / "compile-dna.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("hello")
        f2.write_text("world")
        assert mod.hash_file(f1) != mod.hash_file(f2)

    def test_discover_entities_finds_structure(self, tmp_path):
        """discover_entities should discover brand/character/style from directory."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "compile_dna", SCRIPTS_DIR / "compile-dna.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        brands_dir = tmp_path / "brand-assets" / "test-brand"
        brands_dir.mkdir(parents=True)
        (brands_dir / "hero.jpg").write_text("fake image")
        mod.BRAND_ASSETS = brands_dir.parent
        mod.CHARACTER_REFS = tmp_path / "character-refs"
        mod.STYLE_INSPIRATION = tmp_path / "style-inspiration"

        mod.CHARACTER_REFS.mkdir(parents=True, exist_ok=True)
        mod.STYLE_INSPIRATION.mkdir(parents=True, exist_ok=True)

        entities = mod.discover_entities(tmp_path)
        assert "test-brand" in entities["brands"]
        assert len(entities["brands"]["test-brand"]["assets"]) == 1

    def test_compile_brand_produces_frontmatter(self):
        """compile_brand should produce Markdown with YAML frontmatter."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "compile_dna", SCRIPTS_DIR / "compile-dna.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        data = {"assets": [], "hash": "abc123"}
        result = mod.compile_brand("test-brand", data, None, dry_run=True)
        assert result.startswith("---")
        assert 'name: "test-brand"' in result
        assert 'type: brand-dna' in result

    def test_needs_recompilation_new_file(self, tmp_path, monkeypatch):
        """needs_recompilation should return True for non-existent compiled file."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "compile_dna", SCRIPTS_DIR / "compile-dna.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        monkeypatch.setattr(mod, "COMPILED_DIR", tmp_path / "compiled")
        assert mod.needs_recompilation("nonexistent", "brands", "hash123")

    def test_run_lint_no_files(self, tmp_path, monkeypatch):
        """run_lint should return 0 when no compiled files exist."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "compile_dna", SCRIPTS_DIR / "compile-dna.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        monkeypatch.setattr(mod, "COMPILED_DIR", tmp_path / "compiled")
        (tmp_path / "compiled").mkdir(parents=True, exist_ok=True)
        result = mod.run_lint()
        assert result == 0


class TestComposeVideoModule:
    """Tests for compose-video.py script functions."""

    def test_module_imports(self):
        """compose-video.py should be importable."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "compose_video", SCRIPTS_DIR / "compose-video.py"
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            pytest.fail(f"compose-video.py failed to import: {e}")

    def test_parse_storyboard(self, tmp_path):
        """parse_storyboard should extract title and shots from markdown."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "compose_video", SCRIPTS_DIR / "compose-video.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sb = tmp_path / "storyboard.md"
        sb.write_text("""---
title: "Test Video"
brand: arcan-studio
aspect_ratio: 16:9
---

## Shot 1: Establishing
Cinematic wide shot of city at night.

## Shot 2: Character Introduction
Model walks through rain-soaked street.
""")
        result = mod.parse_storyboard(sb)
        assert result["meta"]["title"] == "Test Video"
        assert len(result["shots"]) == 2
        assert result["shots"][0]["name"] == "Shot 1: Establishing"

    def test_parse_storyboard_single_shot(self, tmp_path):
        """parse_storyboard should handle single-shot storyboards."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "compose_video", SCRIPTS_DIR / "compose-video.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        sb = tmp_path / "single.md"
        sb.write_text("""---
title: "Single Shot"
---

## Shot 1: Only
Simple description.
""")
        result = mod.parse_storyboard(sb)
        assert len(result["shots"]) == 1
        assert result["meta"]["title"] == "Single Shot"

    def test_inject_brand_into_prompt(self):
        """inject_brand_into_prompt should append visual style suffix."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "compose_video", SCRIPTS_DIR / "compose-video.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        brand_dna = {
            "mood": "cinematic",
            "lighting_type": "dramatic",
            "lighting_temp": "cool",
            "composition": "rule-of-thirds",
        }
        original = "A person walking down the street."
        result = mod.inject_brand_into_prompt(original, brand_dna)
        assert original in result
        assert "cinematic" in result
        assert "dramatic lighting" in result
        assert "rule-of-thirds composition" in result

    def test_inject_brand_into_prompt_empty_dna(self):
        """inject_brand_into_prompt should return original for empty brand DNA."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "compose_video", SCRIPTS_DIR / "compose-video.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.inject_brand_into_prompt("Test prompt.", {})
        assert result == "Test prompt."

    def test_load_brand_dna_nonexistent(self, tmp_path, monkeypatch):
        """load_brand_dna should return None for nonexistent brands."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "compose_video", SCRIPTS_DIR / "compose-video.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        monkeypatch.setattr(mod, "COMPILED_DIR", tmp_path / "compiled")
        result = mod.load_brand_dna("nonexistent")
        assert result is None
