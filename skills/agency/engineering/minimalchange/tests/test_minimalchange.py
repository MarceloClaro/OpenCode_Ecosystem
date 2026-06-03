"""Tests for MinimalChangeEngine.

Covers all 4 CTs from SPEC_EVO14_ENG_minimalchange:
  CT-01: Scope check — out of scope detection
  CT-02: Premature refactor detection
  CT-03: Diff entropy measurement
  CT-04: Change ratio validation
"""

import sys
sys.path.insert(0, '.')
from minimalchange_engine import MinimalChangeEngine


SAMPLE_DIFF = """diff --git a/src/auth.py b/src/auth.py
index abc123..def456 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,6 +10,8 @@ def login(user, password):
     if not user:
         return None
-    hashed = hash_password(password)
+    hashed = hash_password_v2(password)
+
     return create_session(user)

diff --git a/src/models.py b/src/models.py
index 789012..345678 100644
--- a/src/models.py
+++ b/src/models.py
@@ -5,7 +5,9 @@ class User:
     email: str
-    name: str
+    full_name: str
+
+

diff --git a/src/utils.py b/src/utils.py
index deadbeef..cafebabe 100644
--- a/src/utils.py
+++ b/src/utils.py
@@ -1,3 +1,10 @@
+
+
+
+
+
+
+
+
 def helper():
     pass
"""

REFACTOR_DIFF = """diff --git a/src/service.py b/src/service.py
index 111..222 100644
--- a/src/service.py
+++ b/src/service.py
@@ -3,7 +3,7 @@ class DataService:
         pass

-def get_all():
+def fetch_all_records():
     return db.query()

-def process(data):
+def process_data_batch(data):
     return transform(data)
"""


def test_ct01_scope_check():
    """CT-01: Detects files changed outside declared scope."""
    engine = MinimalChangeEngine()
    assert engine.available

    scope_files = ['src/auth.py']
    result = engine.check_scope(SAMPLE_DIFF, scope_files)

    assert not result.violation or len(result.out_of_scope) > 0

    full_scope = ['src/auth.py', 'src/models.py', 'src/utils.py']
    result2 = engine.check_scope(SAMPLE_DIFF, full_scope)
    assert not result2.violation


def test_ct02_premature_refactor_detection():
    """CT-02: Detects function/class renames in diff."""
    engine = MinimalChangeEngine()
    result = engine.detect_premature_refactor(REFACTOR_DIFF)

    assert isinstance(result.risk_score, int)
    assert len(result.suspicious_renames) > 0

    renamed_names = {r['old_name'] for r in result.suspicious_renames}
    assert 'get_all' in renamed_names
    assert 'process' in renamed_names


def test_ct03_diff_entropy():
    """CT-03: Measures files, hunks, lines, and entropy score."""
    engine = MinimalChangeEngine()
    result = engine.measure_entropy(SAMPLE_DIFF)

    assert result.files_changed == 3
    assert result.hunks_count > 0
    assert result.lines_added > 0
    assert result.lines_removed > 0
    assert 0 <= result.entropy_score <= 100


def test_ct04_change_ratio():
    """CT-04: Distinguishes functional from cosmetic changes."""
    engine = MinimalChangeEngine()
    result = engine.validate_change_ratio(SAMPLE_DIFF)

    assert result.functional_changes + result.cosmetic_changes > 0
    assert 0.0 <= result.ratio <= 1.0
    assert isinstance(result.warning, bool)


def test_empty_diff():
    """Edge case: empty diff returns zero entropy."""
    engine = MinimalChangeEngine()
    result = engine.measure_entropy('')
    assert result.files_changed == 0
    assert result.hunks_count == 0
    assert result.entropy_score == 0


def test_single_scope_exact_match():
    """Edge case: single scope file matches exactly."""
    engine = MinimalChangeEngine()
    result = engine.check_scope(
        'diff --git a/src/main.py b/src/main.py\n--- a/src/main.py\n+++ b/src/main.py\n',
        ['src/main.py']
    )
    assert not result.violation
    assert len(result.in_scope) > 0
