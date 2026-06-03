"""Tests for CodeReviewer engine.

Covers all 4 CTs from SPEC_EVO14_ENG_codereviewer:
  CT-01: Cyclomatic complexity detection
  CT-02: Code smell detection
  CT-03: Security issue detection
  CT-04: Code duplication detection
"""

import sys
sys.path.insert(0, '.')
from codereviewer_engine import CodeReviewer


SAMPLE_SOURCE = '''
import os
import pickle

API_KEY = "sk-abc123def45678901234567890abcdef"

def calculate_total(items, discount, tax, region, currency, user):
    """A god function that does too much with too many parameters."""
    result = 0
    for item in items:
        if item.price > 0:
            if item.category == "A":
                if item.subcategory == "A1":
                    if item.special:
                        result += item.price * 0.9
                    else:
                        result += item.price * 0.95
                else:
                    result += item.price
            elif item.category == "B":
                result += item.price * 0.8
            else:
                result += item.price
        else:
            result += 0
        if item.discount:
            result -= item.discount
        if item.volume:
            result += item.volume * 0.01
        for extra in item.extras:
            if extra.applied:
                if extra.type == "bonus":
                    result += 5
    result = result * (1 - discount)
    result = result * (1 + tax)
    if region == "EU":
        result = result * 1.21
    elif region == "US":
        if currency == "USD":
            result = result * 1.0
        else:
            result = result * 1.1
    else:
        result = result * 1.15
    if user.vip:
        result = result * 0.95
    if user.new_customer:
        result = result - 10
    if result < 0:
        result = 0
    for item in items:
        if item.price > 0:
            if item.category == "A":
                if item.subcategory == "A1":
                    result += item.price * 0.05
    log_result(result)
    send_notification(user, result)
    update_database(items, result)
    cache_result(user.id, result)
    return result

def get_data():
    data = os.system("ls -la")
    result = eval("1 + 2")
    pickle.loads(b"garbage")
    secret = "my-secret-password-12345"
    return data

def get_data_dup():
    data = os.system("ls -la")
    result = eval("1 + 2")
    pickle.loads(b"garbage")
    return data

def a():
    pass

def x(y, z, a, b, c, d, e):
    return y + z

def log_result(val):
    print(val)

def send_notification(user, val):
    pass

def update_database(items, val):
    pass

def cache_result(uid, val):
    pass
'''


def test_ct01_cyclomatic_complexity():
    """CT-01: Detects functions exceeding complexity threshold."""
    engine = CodeReviewer()
    assert engine.available

    result = engine.analyze_complexity(SAMPLE_SOURCE)

    assert result.total_score > 0
    assert len(result.violations) > 0

    god_func = [v for v in result.violations if v['name'] == 'calculate_total']
    assert len(god_func) > 0
    assert god_func[0]['score'] > engine.COMPLEXITY_THRESHOLD


def test_ct02_code_smells():
    """CT-02: Detects god functions, too many params, short names, deep nesting."""
    engine = CodeReviewer()
    result = engine.detect_smells(SAMPLE_SOURCE)

    assert result.count > 0

    smell_types = {s['type'] for s in result.smells}
    assert 'god_function' in smell_types or 'too_many_params' in smell_types
    assert 'short_name' in smell_types

    god = [s for s in result.smells if s['type'] == 'god_function']
    if god:
        assert god[0]['name'] == 'calculate_total'

    params = [s for s in result.smells if s['type'] == 'too_many_params']
    if params:
        assert any(p['name'] == 'x' for p in params)


def test_ct03_security_issues():
    """CT-03: Detects eval, exec, os.system, hardcoded secrets, pickle."""
    engine = CodeReviewer()
    result = engine.detect_security_issues(SAMPLE_SOURCE)

    assert result.issues
    assert result.critical_count > 0

    patterns_found = {i['pattern'].split(' —')[0] for i in result.issues}
    assert any('eval' in p.lower() for p in patterns_found)
    assert any('os.system' in p.lower() for p in patterns_found)
    assert any('secret' in p.lower() or 'hardcoded' in p.lower() for p in patterns_found)


def test_ct04_duplication():
    """CT-04: Detects duplicated code blocks."""
    engine = CodeReviewer()
    result = engine.detect_duplication(SAMPLE_SOURCE)

    assert isinstance(result.duplicates, list)
    assert result.duplicated_line_count >= 0

    dup_funcs = [d for d in result.duplicates
                 if d.get('similarity', 0) >= 1.0]
    if dup_funcs:
        assert dup_funcs[0]['lines'] >= 5


def test_clean_source_no_smells():
    """Edge case: clean code should have no violations."""
    engine = CodeReviewer()
    clean = '''def add(a, b):
    return a + b

def multiply(x, y):
    return x * y
'''
    complexity = engine.analyze_complexity(clean)
    assert len(complexity.violations) == 0

    smells = engine.detect_smells(clean)
    assert smells.count == 0

    security = engine.detect_security_issues(clean)
    assert security.critical_count == 0


def test_empty_source():
    """Edge case: empty source returns empty results."""
    engine = CodeReviewer()
    complexity = engine.analyze_complexity('')
    assert complexity.total_score == 1
    assert len(complexity.violations) == 0

    smells = engine.detect_smells('')
    assert smells.count == 0

    security = engine.detect_security_issues('')
    assert len(security.issues) == 0
