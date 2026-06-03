"""Tests for GitWorkflowEngine.

Covers all 4 CTs from SPEC_EVO14_ENG_gitworkflow:
  CT-01: Branch name validation
  CT-02: Conventional commit validation
  CT-03: Non-atomic commit detection
  CT-04: Merge strategy analysis
"""

import sys
sys.path.insert(0, '.')
from gitworkflow_engine import GitWorkflowEngine


def test_ct01_branch_name_validation():
    """CT-01: Validates branch names with category and ticket."""
    engine = GitWorkflowEngine()
    assert engine.available

    valid = engine.validate_branch_name('feat/SCRUM-123-add-login')
    assert valid.valid
    assert valid.category == 'feat'
    assert valid.ticket == 'SCRUM-123'

    no_cat = engine.validate_branch_name('SCRUM-123-login')
    assert not no_cat.valid

    no_ticket = engine.validate_branch_name('feat/add-login')
    assert not no_ticket.valid

    invalid_cat = engine.validate_branch_name('unknown/SCRUM-123-foo')
    assert not invalid_cat.valid


def test_ct02_commit_message_validation():
    """CT-02: Validates Conventional Commit messages."""
    engine = GitWorkflowEngine()

    valid = engine.validate_commit_message('fix(auth): resolve token expiry on refresh')
    assert valid.valid
    assert valid.type == 'fix'
    assert valid.scope == 'auth'
    assert not valid.breaking
    assert valid.description == 'resolve token expiry on refresh'

    breaking = engine.validate_commit_message('feat(api)!: drop support for legacy endpoint')
    assert breaking.valid
    assert breaking.type == 'feat'
    assert breaking.breaking

    invalid = engine.validate_commit_message('fixed the login bug')
    assert not invalid.valid
    assert 'Not a valid Conventional Commit' in invalid.errors[0]


def test_ct03_non_atomic_commits():
    """CT-03: Detects non-atomic commits spanning many files/domains."""
    engine = GitWorkflowEngine()

    commits = [
        {'hash': 'a1', 'files': ['src/auth.py', 'tests/test_auth.py']},
        {'hash': 'b2', 'files': [
            'src/models.py', 'src/views.py', 'src/utils.py',
            'src/api/handlers.py', 'src/db/migrations/001.py',
            'src/db/models.py', 'frontend/App.jsx', 'frontend/api.js',
            'frontend/styles.css', 'docs/api.md'
        ]},
        {'hash': 'c3', 'files': [
            'package.json', 'src/auth.py', 'src/models.py',
            'src/views.py', 'src/api/handlers.py', 'frontend/App.jsx',
            'frontend/api.js', 'docs/api.md', 'Dockerfile'
        ]},
    ]

    result = engine.detect_non_atomic(commits)
    assert len(result.non_atomic) > 0
    assert result.score < 1.0

    atomic = engine.detect_non_atomic([
        {'hash': 'd4', 'files': ['src/auth.py', 'src/auth_utils.py']},
    ])
    assert len(atomic.non_atomic) == 0
    assert atomic.score == 1.0


def test_ct04_merge_strategy_analysis():
    """CT-04: Analyzes git log for merge strategies."""
    engine = GitWorkflowEngine()

    merge_log = """Merge pull request #1 from feature/login
Merge pull request #2 from feature/signup
Merge pull request #3 from feature/dashboard
"""
    result = engine.analyze_merge_strategy(merge_log)
    assert result.strategy_detected in ('merge', 'squash', 'rebase_or_fast_forward', 'mixed')
    assert len(result.recommendation) > 0

    squash_log = """
Squash merge feature/login (#1)
Squash merge feature/signup (#2)
"""
    result2 = engine.analyze_merge_strategy(squash_log)
    assert result2.strategy_detected == 'squash'


def test_zero_commits():
    """Edge case: empty commit list has perfect score."""
    engine = GitWorkflowEngine()
    result = engine.detect_non_atomic([])
    assert result.score == 1.0
    assert len(result.non_atomic) == 0


def test_multiple_categories():
    """Edge case: all valid categories accepted."""
    engine = GitWorkflowEngine()
    for cat in ['feat', 'fix', 'chore', 'docs', 'refactor', 'test',
                'style', 'perf', 'ci', 'build', 'revert']:
        result = engine.validate_branch_name(f'{cat}/TICKET-1-something')
        assert result.valid, f'Category {cat} should be valid'
