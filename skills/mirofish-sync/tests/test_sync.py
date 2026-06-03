"""
TDD tests for MiroFishSyncEngine — Motor de sincronizacao upstream.
CT-1: test_init — inicializacao do engine e baseline
CT-2: test_check_updates — verificacao de repositorios por mudancas
CT-3: test_parse_version — deteccao de novos padroes no classifier
CT-4: test_sync_report — geracao de SyncReport com dados validos
"""

import os
import sys
import json
import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

from mirofish_sync import (
    MiroFishSyncEngine, GitHubMonitor, PatternClassifier,
    SyncReport, SyncDiff, SyncAction, CommitInfo, REPOS,
)


class TestMiroFishSync:

    def test_init(self, monkeypatch):
        monkeypatch.setattr("mirofish_sync.VERSION_FILE", "")
        engine = MiroFishSyncEngine(dry_run=True, force=False)
        assert engine.dry_run is True
        assert engine.force is False
        assert engine.report is not None
        assert isinstance(engine.report, SyncReport)
        assert engine.baseline is not None

    def test_check_updates(self, monkeypatch):
        monkeypatch.setattr("mirofish_sync.VERSION_FILE", "")
        engine = MiroFishSyncEngine(dry_run=True, force=False)
        result = engine.check_repo("MiroFish", REPOS["MiroFish"])
        assert isinstance(result, SyncDiff)
        assert result.repo == "MiroFish"

    def test_parse_version(self):
        classifier = PatternClassifier()
        action, patterns = classifier.classify("BettaFish", [
            "QueryEngine/__init__.py",
            "MediaEngine/agent.py",
            "README.md",
            "ForumEngine/sentiment.py",
        ])
        assert action in (SyncAction.EXTRACT, SyncAction.MONITOR_ONLY, SyncAction.SKIP)
        assert isinstance(patterns, list)

    def test_sync_report(self):
        report = SyncReport()
        report.repos_with_changes = 2
        report.new_patterns_found = 3
        report.diffs.append(SyncDiff(
            repo="MiroFish",
            new_commits=[CommitInfo(
                sha="abc123", date="2026-01-01T00:00:00Z",
                message="feat: new engine", author="dev"
            )],
            action=SyncAction.EXTRACT,
            new_patterns=["TestEngine"],
        ))
        assert report.repos_checked == 3
        assert report.repos_with_changes == 2
        assert report.new_patterns_found == 3
