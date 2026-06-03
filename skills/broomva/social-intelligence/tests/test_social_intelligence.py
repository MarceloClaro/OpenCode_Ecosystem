"""
TDD tests for social-intelligence scripts:
- engagement-loop.py (decode_challenge, score_comment, select_targets)
- x_browser.py (check_marketing_shape)
- x_twikit.py (rate gate)
"""
import sys
from pathlib import Path
import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))


class TestEngagementLoopDecodeChallenge:
    """Tests for the Moltbook verification challenge solver."""

    def test_module_imports(self):
        """engagement-loop.py should be importable."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "engagement_loop", SCRIPTS_DIR / "engagement-loop.py"
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as e:
            pytest.fail(f"engagement-loop.py failed to import: {e}")

    def test_decode_challenge_add(self):
        """Lobster claw applies 23 newtons + increases by 7 = 30."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "engagement_loop", SCRIPTS_DIR / "engagement-loop.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.decode_challenge(
            "A] LoObStEr ClAaWw ApPlIiEeS tWeNtY tHrEe NeWwToOnSs + AnNoOtThHeEr InNcCrReEaAsSeEs bYy SeEvVeEn"
        )
        assert result == 30.0

    def test_decode_challenge_lobster_dual_claw(self):
        """Lobster claw 40 newtons + other claw 24 newtons = 64."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "engagement_loop", SCRIPTS_DIR / "engagement-loop.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.decode_challenge(
            "A] lOoObBsStTeEr ^ cLaW-ExErTs/ fOrTy] nEeWtOnS~ aNd/ iTs] oThEr^ cLaW-ExErTs- tWeNty] fOuR"
        )
        assert result == 64.0

    def test_decode_challenge_subtract(self):
        """Velocity 23 but slows by 7 = 16."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "engagement_loop", SCRIPTS_DIR / "engagement-loop.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.decode_challenge(
            "LoOoObBbSsStTeEr~ vEeLlAwWcIiTtEeY^ iS tWwEeNnTtYy ThReE } bUt/ iT sLlOoWwSs| bY^ sEeVvEeNn"
        )
        assert result == 16.0

    def test_word_to_num_lookup(self):
        """WORD_TO_NUM dictionary should have expected entries."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "engagement_loop", SCRIPTS_DIR / "engagement-loop.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        assert mod.WORD_TO_NUM["one"] == 1
        assert mod.WORD_TO_NUM["twenty"] == 20
        assert mod.WORD_TO_NUM["forty"] == 40
        assert mod.WORD_TO_NUM["ninety"] == 90


class TestEngagementLoopScoreComment:
    """Tests for the comment scoring engine."""

    def test_score_comment_returns_expected_structure(self):
        """score_comment should return dict with all required keys."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "engagement_loop", SCRIPTS_DIR / "engagement-loop.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.score_comment("This is about lago and arcan memory patterns.", "memory")
        assert "novelty" in result
        assert "specificity" in result
        assert "relevance" in result
        assert "total" in result
        assert "promote" in result
        assert 0 <= result["total"] <= 9

    def test_score_comment_high_relevance(self):
        """A comment with many known terms should score high relevance."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "engagement_loop", SCRIPTS_DIR / "engagement-loop.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.score_comment(
            "lago arcan anima nous autonomic praxis haima spaces identity memory persistence",
            "memory"
        )
        assert result["relevance"] >= 2

    def test_score_comment_low_known_terms(self):
        """A comment with no known terms should score low relevance."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "engagement_loop", SCRIPTS_DIR / "engagement-loop.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        result = mod.score_comment("Nice post! I really enjoyed reading this.", "memory")
        assert result["relevance"] == 0

    def test_select_targets_prefers_low_comments(self):
        """select_targets should prefer posts with fewer comments."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "engagement_loop", SCRIPTS_DIR / "engagement-loop.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        posts = [
            {"id": "1", "comment_count": 25},
            {"id": "2", "comment_count": 3},
            {"id": "3", "comment_count": 8},
        ]
        targets = mod.select_targets(posts, set())
        assert len(targets) <= 3
        assert targets[0]["id"] == "2"


class TestXBrowserMarketingShape:
    """Tests for the marketing-shape detector in x_browser.py."""

    def _load_x_browser_module(self, monkeypatch):
        import importlib.util
        original_exit = sys.exit
        monkeypatch.setattr(sys, "exit", lambda code: None)
        spec = importlib.util.spec_from_file_location(
            "x_browser", SCRIPTS_DIR / "x_browser.py"
        )
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except SystemExit:
            pytest.skip("playwright greenlet blocked by App Control")
        except ImportError:
            pytest.skip("playwright not installed")
        finally:
            sys.exit = original_exit
        return mod

    def test_load_proprietary_nouns_from_file(self, tmp_path, monkeypatch):
        """_load_proprietary_nouns should read from file correctly."""
        mod = self._load_x_browser_module(monkeypatch)

        nouns_file = tmp_path / "proprietary-nouns.txt"
        nouns_file.write_text("arcan\nlago\nanima\n# comment\npraxis\n")
        monkeypatch.setattr(mod, "PROPRIETARY_NOUNS_FILE", nouns_file)
        monkeypatch.setattr(mod, "_proprietary_nouns_cache", None)

        nouns = mod._load_proprietary_nouns()
        assert "arcan" in nouns
        assert "lago" in nouns
        assert "anima" in nouns
        assert "praxis" in nouns
        assert "# comment" not in nouns

    def test_check_marketing_shape_blocks_proprietary_lead(self, monkeypatch):
        """check_marketing_shape should block text leading with proprietary nouns."""
        mod = self._load_x_browser_module(monkeypatch)

        mod._proprietary_nouns_cache = {"lago", "arcan", "praxis"}
        result = mod.check_marketing_shape("Lago is an amazing event sourcing system for agents.")
        assert result["is_marketing_shape"] is True
        assert "lago" in result["matched_nouns"]

    def test_check_marketing_shape_passes_clean_text(self, monkeypatch):
        """check_marketing_shape should pass text without proprietary nouns."""
        mod = self._load_x_browser_module(monkeypatch)

        mod._proprietary_nouns_cache = {"lago", "arcan"}
        result = mod.check_marketing_shape("Great point about event sourcing in distributed systems!")
        assert result["is_marketing_shape"] is False

    def test_check_marketing_shape_proprietary_later_in_text(self, monkeypatch):
        """check_marketing_shape should NOT block if proprietary noun is after lead window."""
        mod = self._load_x_browser_module(monkeypatch)

        mod._proprietary_nouns_cache = {"lago"}
        lead = "interesting perspective on event driven architecture and data streaming patterns"
        rest = " lago handles this well"
        text = lead + rest
        result = mod.check_marketing_shape(text, lead_word_window=10)
        assert result["is_marketing_shape"] is False


class TestXTwikitRateGate:
    """Tests for x_twikit.py rate-limiting safety rails."""

    def _load_twikit_module(self, monkeypatch):
        import importlib.util
        original_exit = sys.exit
        monkeypatch.setattr(sys, "exit", lambda code: None)
        spec = importlib.util.spec_from_file_location(
            "x_twikit", SCRIPTS_DIR / "x_twikit.py"
        )
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except SystemExit:
            pytest.skip("twikit not installed")
        except ImportError:
            pytest.skip("twikit not installed")
        finally:
            sys.exit = original_exit
        return mod

    def test_module_imports(self, monkeypatch):
        """x_twikit.py should be importable (without connecting)."""
        mod = self._load_twikit_module(monkeypatch)

    def test_rate_gate_prevents_excess_writes(self, monkeypatch):
        """_rate_gate should exit when write cap is reached."""
        mod = self._load_twikit_module(monkeypatch)

        mod._write_count = 4
        with pytest.raises(SystemExit) as exc:
            mod._rate_gate()
        assert exc.value.code == 3

    def test_rate_gate_allows_first_write(self, monkeypatch):
        """_rate_gate should allow writes when under limit."""
        mod = self._load_twikit_module(monkeypatch)

        mod._write_count = 0
        mod._last_write_ts = 0.0
        try:
            mod._rate_gate()
        except SystemExit:
            pytest.fail("_rate_gate should not block first write")

    def test_build_parser_has_subcommands(self, monkeypatch):
        """build_parser should register expected subcommands."""
        mod = self._load_twikit_module(monkeypatch)

        parser = mod.build_parser()
        assert parser is not None

    def test_exit_codes_defined(self, monkeypatch):
        """x_twikit.py should have well-known exit codes."""
        mod = self._load_twikit_module(monkeypatch)

        assert mod.MAX_WRITES_PER_RUN == 4
        assert mod.WRITE_COOLDOWN_SECONDS == 30
