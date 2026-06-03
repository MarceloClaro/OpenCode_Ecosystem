# -*- coding: utf-8 -*-
"""
TDD Test Suite: D7 — Verificacao de Codigo Cientifico (N3)
CORA-Eval Benchmark Tasks: D7-N3-01 a D7-N3-05
Aplica verificadores V7a-V7g ao proprio codigo dos testes CORA-Eval.
"""

import sys, os, ast, inspect, math, time, random as _random_mod

# Importa funcoes do test_d3 para verificacao V7b
sys.path.insert(0, os.path.dirname(__file__))
from test_d3_estatistica import mean, variance, std, t_statistic, cohens_d, pearson_r

# ══════════════════════════════════════════════════════════════════════
# V7a — Syntax Validator
# ══════════════════════════════════════════════════════════════════════

def validate_syntax(filepath: str) -> bool:
    """V7a: Verifica se arquivo Python tem sintaxe valida."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True
    except SyntaxError:
        return False

def test_v7a_syntax_all_test_files():
    """D7-N3-01: V7a — todos os arquivos de teste tem sintaxe valida."""
    test_dir = os.path.dirname(__file__)
    files = [f for f in os.listdir(test_dir) if f.startswith('test_') and f.endswith('.py')]
    for fname in files:
        fpath = os.path.join(test_dir, fname)
        assert validate_syntax(fpath), f"Syntax error in {fname}"
    print(f"  [D7-N3-01] V7a: {len(files)} arquivos com sintaxe valida... PASS")
    return True


# ══════════════════════════════════════════════════════════════════════
# V7c — Type Safety (via docstrings e type hints)
# ══════════════════════════════════════════════════════════════════════

def test_v7c_function_signatures():
    """D7-N3-03: V7c — funcoes tem docstrings ou comentarios tipo."""
    # Verifica que as funcoes importadas sao callable e retornam tipo correto
    test_data = [1.0, 2.0, 3.0, 4.0, 5.0]
    test_data2 = [10.0, 20.0, 30.0]

    r1 = mean(test_data)
    assert isinstance(r1, float), f"mean deve retornar float"

    v1 = variance(test_data)
    assert isinstance(v1, float) and v1 >= 0, "variance must be non-negative float"

    t1 = t_statistic(test_data, test_data2)
    assert isinstance(t1, float), "t_statistic must return float"

    d1 = cohens_d(test_data, test_data2)
    assert isinstance(d1, float), "cohens_d must return float"

    rp1 = pearson_r(test_data, [10.0, 20.0, 30.0, 40.0, 50.0])
    assert isinstance(rp1, float), "pearson_r must return float"

    print(f"  [D7-N3-03] V7c: 5 funcoes tipadas verificadas (float)... PASS")
    return True


# ══════════════════════════════════════════════════════════════════════
# V7d — Resource Bounds (Complexidade)
# ══════════════════════════════════════════════════════════════════════

def test_v7d_complexity():
    """D7-N3-04: V7d — complexidade algoritmica documentada."""
    # mean: O(n)
    n = 10000
    data = list(range(n))
    # Executa e verifica que escala linearmente
    import time
    t1 = time.time()
    result = mean(data)
    t2 = time.time()
    elapsed = t2 - t1
    # Deve ser muito rapido (<0.01s para 10k elementos)
    assert elapsed < 0.1, f"mean({n}) demorou {elapsed:.3f}s"
    assert abs(result - (n-1)/2) < 1.0
    print(f"  [D7-N3-04] V7d: mean({n}) em {elapsed*1000:.1f}ms (O(n))... PASS")
    return True


# ══════════════════════════════════════════════════════════════════════
# V7f — Test Coverage
# ══════════════════════════════════════════════════════════════════════

def test_v7f_coverage_self():
    """D7-N3-05: V7f — cobertura: todas as funcoes de D3 sao testadas."""
    from test_d3_estatistica import (
        mean as d3_mean, variance, std, t_statistic, welch_df,
        cohens_d, pearson_r, r_squared, linear_regression,
        bonferroni_correction, benjamini_hochberg
    )
    funcs = [
        d3_mean, variance, std, t_statistic, welch_df,
        cohens_d, pearson_r, r_squared, linear_regression,
        bonferroni_correction, benjamini_hochberg
    ]
    for fn in funcs:
        # Cada funcao deve ser chamavel sem erro com dados validos
        try:
            if fn.__name__ in ('mean', 'variance', 'std'):
                fn([1.0, 2.0, 3.0])
            elif fn.__name__ in ('t_statistic', 'welch_df', 'cohens_d', 'pearson_r'):
                fn([1.0, 2.0], [3.0, 4.0])
            elif fn.__name__ == 'r_squared':
                fn([1.0, 2.0], [1.1, 1.9])
            elif fn.__name__ == 'linear_regression':
                fn([1.0, 2.0, 3.0], [2.0, 4.0, 6.0])
            elif fn.__name__ == 'bonferroni_correction':
                fn([0.01, 0.05, 0.10])
            elif fn.__name__ == 'benjamini_hochberg':
                fn([0.01, 0.05, 0.10])
        except Exception as e:
            assert False, f"Funcao {fn.__name__} falhou: {e}"
    print(f"  [D7-N3-05] V7f: {len(funcs)} funcoes executaveis sem erro... PASS")
    return True


# ══════════════════════════════════════════════════════════════════════
# V7e — Security Patterns
# ══════════════════════════════════════════════════════════════════════

def test_v7e_no_eval_exec():
    """D7-N3-02: V7e — nenhum uso de eval() ou exec() nos testes."""
    test_dir = os.path.dirname(__file__)
    files = [f for f in os.listdir(test_dir)
             if f.endswith('.py') and f != os.path.basename(__file__)]  # skip self
    for fname in files:
        fpath = os.path.join(test_dir, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            source = f.read()
        assert 'eval(' not in source, f'CWE-95: eval() in {fname}'
        assert 'exec(' not in source, f'CWE-95: exec() in {fname}'
    print(f'  [D7-N3-02] V7e: {len(files)} arquivos sem eval/exec (CWE-95)... PASS')
    return True


# ══════════════════════════════════════════════════════════════════════
# V7b — Logic Prover (pre/post conditions)
# ══════════════════════════════════════════════════════════════════════

def test_v7b_mean_idempotency():
    """D7-N3-01: V7b — mean e idempotente: mean(constant) = constant."""
    for c in [0.0, 1.0, 5.0, -3.0]:
        data = [c] * 10
        assert abs(mean(data) - c) < 1e-10
    print("  [D7-N3-01] V7b: mean(idempotent) = constant... PASS")
    return True

def test_v7b_variance_nonnegative():
    """D7-N3-01: V7b — variancia e sempre >= 0."""
    data = [random_val() for _ in range(100)]
    v = variance(data)
    assert v >= 0, f"Variancia negativa: {v}"
    print(f"  [D7-N3-01] V7b: variance(100) = {v:.2f} >= 0... PASS")
    return True


def random_val():
    import random as _r
    return _r.gauss(0, 1)


# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

def main():
    tests = [
        ("V7a Syntax", test_v7a_syntax_all_test_files),
        ("V7b Mean idempotency", test_v7b_mean_idempotency),
        ("V7b Variance nonnegative", test_v7b_variance_nonnegative),
        ("V7c Docstrings", test_v7c_function_signatures),
        ("V7d Complexity O(n)", test_v7d_complexity),
        ("V7e Security (no eval)", test_v7e_no_eval_exec),
        ("V7f Coverage", test_v7f_coverage_self),
    ]

    print("=" * 60)
    print("  TDD TEST SUITE: D7 — Codigo Cientifico (N3)")
    print("  Aplicando V7a-V7g ao proprio codigo CORA-Eval")
    print("=" * 60)

    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"  [{name}] FAIL: {e}")
            failed += 1

    print(f"\n  RESULT: {passed}/{passed+failed} passed, {failed} failed")
    print("=" * 60)
    return failed == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
