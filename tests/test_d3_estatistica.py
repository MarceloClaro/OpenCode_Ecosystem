# -*- coding: utf-8 -*-
"""
TDD Test Suite: D3 — Analise Estatistica e Inferencia (N2 + N3)
CORA-Eval Benchmark Tasks: D3-N2-01 a D3-N2-05, D3-N3-01 a D3-N3-05
Todas as verificacoes usam dados sinteticos com ground truth conhecido.
"""

import sys, math, random
from typing import List, Tuple

random.seed(42)

# ══════════════════════════════════════════════════════════════════════
# FUNCOES ESTATISTICAS IMPLEMENTADAS
# ══════════════════════════════════════════════════════════════════════

def mean(x: List[float]) -> float:
    return sum(x) / len(x)

def variance(x: List[float], ddof: int = 1) -> float:
    m = mean(x)
    return sum((xi - m) ** 2 for xi in x) / (len(x) - ddof)

def std(x: List[float], ddof: int = 1) -> float:
    return math.sqrt(variance(x, ddof))

def t_statistic(x: List[float], y: List[float]) -> float:
    """Estatistica t de Welch (variancias desiguais)."""
    m1, m2 = mean(x), mean(y)
    v1, v2 = variance(x), variance(y)
    n1, n2 = len(x), len(y)
    se = math.sqrt(v1/n1 + v2/n2)
    return (m1 - m2) / se if se > 0 else 0.0

def welch_df(x: List[float], y: List[float]) -> float:
    """Graus de liberdade de Welch-Satterthwaite."""
    v1, v2 = variance(x), variance(y)
    n1, n2 = len(x), len(y)
    num = (v1/n1 + v2/n2) ** 2
    den = (v1/n1)**2/(n1-1) + (v2/n2)**2/(n2-1)
    return num / den if den > 0 else 1.0

def cohens_d(x: List[float], y: List[float]) -> float:
    """Tamanho de efeito de Cohen."""
    pooled_sd = math.sqrt((variance(x) + variance(y)) / 2)
    return (mean(x) - mean(y)) / pooled_sd if pooled_sd > 0 else 0.0

def pearson_r(x: List[float], y: List[float]) -> float:
    """Coeficiente de correlacao de Pearson."""
    mx, my = mean(x), mean(y)
    num = sum((xi-mx)*(yi-my) for xi, yi in zip(x, y))
    den = math.sqrt(sum((xi-mx)**2 for xi in x) * sum((yi-my)**2 for yi in y))
    return num / den if den > 0 else 0.0

def r_squared(y_true: List[float], y_pred: List[float]) -> float:
    """Coeficiente de determinacao R^2."""
    ss_res = sum((yt - yp)**2 for yt, yp in zip(y_true, y_pred))
    ss_tot = sum((yt - mean(y_true))**2 for yt in y_true)
    return 1 - ss_res/ss_tot if ss_tot > 0 else 0.0

def linear_regression(x: List[float], y: List[float]) -> Tuple[float, float]:
    """Regressao linear simples: y = b0 + b1*x. Retorna (b0, b1)."""
    mx, my = mean(x), mean(y)
    num = sum((xi-mx)*(yi-my) for xi, yi in zip(x, y))
    den = sum((xi-mx)**2 for xi in x)
    b1 = num / den if den > 0 else 0.0
    b0 = my - b1 * mx
    return (b0, b1)

def bonferroni_correction(p_values: List[float]) -> List[float]:
    """Correcao de Bonferroni: p_adj = min(1, p * n)."""
    n = len(p_values)
    return [min(1.0, p * n) for p in p_values]

def benjamini_hochberg(p_values: List[float], alpha: float = 0.05) -> List[bool]:
    """FDR control via Benjamini-Hochberg."""
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    rejected = [False] * n
    for rank, (idx, p) in enumerate(indexed):
        threshold = (rank + 1) / n * alpha
        if p <= threshold:
            rejected[idx] = True
        else:
            break
    return rejected


# ══════════════════════════════════════════════════════════════════════
# N2 TESTS (Graduacao)
# ══════════════════════════════════════════════════════════════════════

def test_t_test_equal_means():
    """D3-N2-01: Teste t: duas amostras da mesma populacao -> p alto."""
    # Amostras da mesma N(10, 2)
    x = [10 + random.gauss(0, 2) for _ in range(50)]
    y = [10 + random.gauss(0, 2) for _ in range(50)]
    t = t_statistic(x, y)
    # |t| < 2 para amostras iguais (p > 0.05 tipicamente)
    assert abs(t) < 2.5, f"t={t:.3f} deveria ser pequeno para amostras iguais"
    print(f"  [D3-N2-01] Teste t amostras iguais: t={t:.3f}... PASS")
    return True

def test_t_test_different_means():
    """D3-N2-01: Teste t: amostras diferentes -> |t| grande, d grande."""
    x = [10 + random.gauss(0, 1) for _ in range(50)]
    y = [13 + random.gauss(0, 1) for _ in range(50)]  # diferenca de 3 SD
    t = t_statistic(x, y)
    d = cohens_d(x, y)
    assert abs(t) > 5, f"t={t:.3f} deveria ser grande"
    assert abs(d) > 2.0, f"Cohen d={d:.3f} deveria ser grande"
    print(f"  [D3-N2-01] Teste t diferentes: t={t:.1f}, d={d:.2f}... PASS")
    return True

def test_anova_oneway():
    """D3-N2-02: ANOVA one-way: 3 grupos com medias diferentes -> F grande."""
    random.seed(123)
    g1 = [10 + random.gauss(0, 1) for _ in range(30)]
    g2 = [12 + random.gauss(0, 1) for _ in range(30)]
    g3 = [15 + random.gauss(0, 1) for _ in range(30)]

    # F = MS_between / MS_within
    all_groups = [g1, g2, g3]
    grand_mean = mean([x for g in all_groups for x in g])
    ss_between = sum(len(g) * (mean(g) - grand_mean)**2 for g in all_groups)
    ss_within = sum(sum((x - mean(g))**2 for x in g) for g in all_groups)
    df_between = len(all_groups) - 1
    df_within = sum(len(g) for g in all_groups) - len(all_groups)
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    F = ms_between / ms_within

    assert F > 10, f"F={F:.1f} deveria ser grande (grupos diferentes)"
    print(f"  [D3-N2-02] ANOVA one-way: F={F:.1f}, ss_between={ss_between:.0f}... PASS")
    return True

def test_linear_regression_perfect():
    """D3-N2-03: Regressao linear: y = 2 + 3x + ruido -> recupera parametros."""
    random.seed(456)
    x = [i for i in range(50)]
    y = [2 + 3*xi + random.gauss(0, 2) for xi in x]
    b0, b1 = linear_regression(x, y)
    assert abs(b0 - 2) < 0.8, f"b0={b0:.2f}, esperado ~2"
    assert abs(b1 - 3) < 0.05, f"b1={b1:.2f}, esperado ~3"
    y_pred = [b0 + b1*xi for xi in x]
    r2 = r_squared(y, y_pred)
    assert r2 > 0.95, f"R^2={r2:.3f} deveria ser >0.95"
    print(f"  [D3-N2-03] Regressao: y={b0:.2f}+{b1:.3f}x, R^2={r2:.3f}... PASS")
    return True

def test_pearson_correlation():
    """D3-N2-04: Correlacao de Pearson: r ~ 1 para y = 2x, r ~ 0 para independentes."""
    random.seed(789)
    x = [random.gauss(0, 1) for _ in range(200)]
    # Perfeitamente correlacionado
    y_corr = [2*xi + random.gauss(0, 0.1) for xi in x]
    r_corr = pearson_r(x, y_corr)
    assert r_corr > 0.95, f"r={r_corr:.3f} deveria ser ~1"
    # Independente
    y_ind = [random.gauss(0, 1) for _ in range(200)]
    r_ind = pearson_r(x, y_ind)
    assert abs(r_ind) < 0.3, f"r={r_ind:.3f} deveria ser ~0"
    print(f"  [D3-N2-04] Pearson: r_corr={r_corr:.3f}, r_ind={r_ind:.3f}... PASS")
    return True

def test_multiple_comparison():
    """D3-N2-05 / D3-N3-04: Correcao de multiplas comparacoes."""
    # 20 testes, 2 verdadeiros positivos (p=0.001), 18 nulos (p~U(0,1))
    random.seed(101)
    p_values = [0.001, 0.001] + [random.random() for _ in range(18)]
    random.shuffle(p_values)

    # Bonferroni: nenhum falso positivo
    bonf_adj = bonferroni_correction(p_values)
    n_rejected_bonf = sum(1 for p in bonf_adj if p < 0.05)
    assert n_rejected_bonf <= 3, f"Bonferroni rejeitou {n_rejected_bonf} (muitos falsos positivos?)"

    # Benjamini-Hochberg: controla FDR
    bh_rej = benjamini_hochberg(p_values, alpha=0.05)
    n_rejected_bh = sum(bh_rej)
    # BH deve rejeitar os 2 verdadeiros + talvez alguns falsos (controlado)
    assert n_rejected_bh >= 2, f"BH rejeitou apenas {n_rejected_bh}"
    print(f"  [D3-N3-04] Multiplas comparacoes: Bonf={n_rejected_bonf}, BH={n_rejected_bh}... PASS")
    return True


# ══════════════════════════════════════════════════════════════════════
# N3 TESTS (Pos-Graduacao)
# ══════════════════════════════════════════════════════════════════════

def test_mcmc_metropolis_hastings():
    """D3-N3-01: MCMC Metropolis-Hastings para amostrar N(0,1)."""
    random.seed(2021)
    def target(x): return math.exp(-0.5 * x * x)  # N(0,1) nao-normalizada

    n_iter = 5000
    burn_in = 1000
    samples = []
    current = 0.0

    for i in range(n_iter + burn_in):
        proposal = current + random.gauss(0, 1.0)
        alpha = target(proposal) / (target(current) + 1e-10)
        if random.random() < min(1.0, alpha):
            current = proposal
        if i >= burn_in:
            samples.append(current)

    # Verifica convergencia: media ~ 0, std ~ 1
    sample_mean = mean(samples)
    sample_std = std(samples)
    assert abs(sample_mean) < 0.1, f"Media MCMC={sample_mean:.3f}, esperado ~0"
    assert abs(sample_std - 1.0) < 0.15, f"Std MCMC={sample_std:.3f}, esperado ~1"
    # Taxa de aceitacao tipica: 20-50%
    accept_rate = len(set(samples)) / len(samples)  # aproximacao
    print(f"  [D3-N3-01] MCMC: mean={sample_mean:.3f}, std={sample_std:.3f}... PASS")
    return True

def test_pca_variance_explained():
    """D3-N3-02: PCA — variancia explicada por componente.
    Dados: 2D com correlacao 0.9 na direcao (1,1)."""
    random.seed(303)
    n = 200
    # Gera dados correlacionados
    z1 = [random.gauss(0, 3) for _ in range(n)]   # PC1: alta variancia
    z2 = [random.gauss(0, 0.3) for _ in range(n)]  # PC2: baixa variancia
    # Rotaciona 45 graus
    x = [zi * 0.707 - zj * 0.707 for zi, zj in zip(z1, z2)]
    y = [zi * 0.707 + zj * 0.707 for zi, zj in zip(z1, z2)]

    # Covariancia manual
    mx, my = mean(x), mean(y)
    cov_xx = sum((xi-mx)**2 for xi in x) / (n-1)
    cov_yy = sum((yi-my)**2 for yi in y) / (n-1)
    cov_xy = sum((xi-mx)*(yi-my) for xi, yi in zip(x, y)) / (n-1)

    # Autovalores da matriz de covariancia 2x2
    trace = cov_xx + cov_yy
    det = cov_xx * cov_yy - cov_xy * cov_xy
    disc = math.sqrt(trace*trace - 4*det)
    lambda1 = (trace + disc) / 2
    lambda2 = (trace - disc) / 2

    var_explained_pc1 = lambda1 / (lambda1 + lambda2)
    # PC1 deve explicar a maioria da variancia (>70%)
    assert var_explained_pc1 > 0.70, f"PC1 explica {var_explained_pc1:.1%}"
    print(f"  [D3-N3-02] PCA: PC1={lambda1:.2f}, PC2={lambda2:.2f}, VarPC1={var_explained_pc1:.1%}... PASS")
    return True

def test_bootstrap_ci():
    """D3-N2-04 (ext): Bootstrap IC 95% para media.
    Populacao N(10, 2). Amostra n=30. IC deve conter 10."""
    random.seed(505)
    population_mean = 10.0
    sample = [random.gauss(population_mean, 2) for _ in range(30)]

    # Bootstrap: 1000 reamostragens
    n_boot = 1000
    boot_means = []
    for _ in range(n_boot):
        boot_sample = random.choices(sample, k=len(sample))
        boot_means.append(mean(boot_sample))

    boot_means.sort()
    ci_lower = boot_means[25]   # 2.5%
    ci_upper = boot_means[974]  # 97.5%

    assert ci_lower <= population_mean <= ci_upper, \
        f"IC=[{ci_lower:.2f}, {ci_upper:.2f}] nao contem media={population_mean}"
    print(f"  [D3-N2-04] Bootstrap IC 95%: [{ci_lower:.2f}, {ci_upper:.2f}] contem {population_mean}... PASS")
    return True


# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

def main():
    tests = [
        # N2
        ("t-test equal", test_t_test_equal_means),
        ("t-test different", test_t_test_different_means),
        ("ANOVA one-way", test_anova_oneway),
        ("Linear regression", test_linear_regression_perfect),
        ("Pearson correlation", test_pearson_correlation),
        ("Bootstrap CI", test_bootstrap_ci),
        # N3
        ("MCMC Metropolis-Hastings", test_mcmc_metropolis_hastings),
        ("PCA variance", test_pca_variance_explained),
        ("Multiple comparison", test_multiple_comparison),
    ]

    print("=" * 60)
    print("  TDD TEST SUITE: D3 — Estatistica (N2+N3)")
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
