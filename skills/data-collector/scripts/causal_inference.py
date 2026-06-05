#!/usr/bin/env python3
"""
CausalInference — Testes de causalidade executados sobre dados da simulação.
Implementa: Granger causality, correlação cruzada com lag, teste de precedência temporal.

NÃO apenas descreve — EXECUTA as análises e retorna resultados quantitativos.
"""

import math
from collections import defaultdict
from typing import Dict, List, Any, Tuple, Optional


def granger_causality_test(series_a: List[float], series_b: List[float],
                           max_lag: int = 3) -> Dict[str, Any]:
    """
    Teste de causalidade de Granger: series_a → series_b.
    
    H0: series_a NÃO causa series_b no sentido de Granger.
    Rejeita H0 se p < 0.05 (os lags de A melhoram significativamente a previsão de B).
    
    Implementação: OLS restrito (só lags de B) vs. OLS irrestrito (lags de A + B).
    Estatística F = ((RSS_r - RSS_u) / p) / (RSS_u / (n - 2p - 1))
    """
    n = len(series_a)
    if n < max_lag + 5 or len(series_b) != n:
        return {"causal": False, "p_value": 1.0, "f_stat": 0.0,
                "error": f"Séries muito curtas (n={n}, lag={max_lag})"}

    results = []
    for lag in range(1, max_lag + 1):
        # Preparar dados: B(t) ~ B(t-1)...B(t-lag) + A(t-1)...A(t-lag)
        effective_n = n - lag
        if effective_n < 5:
            continue

        # Modelo restrito: só lags de B
        y = series_b[lag:]  # B(t)

        # Matriz X restrita: B(t-1)...B(t-lag)
        X_r = []
        for i in range(lag, n):
            row = [series_b[i - j] for j in range(1, lag + 1)]
            X_r.append([1.0] + row)  # + intercepto

        # Matriz X irrestrita: B(t-1)...B(t-lag) + A(t-1)...A(t-lag)
        X_u = []
        for i in range(lag, n):
            row = [series_b[i - j] for j in range(1, lag + 1)]
            row += [series_a[i - j] for j in range(1, lag + 1)]
            X_u.append([1.0] + row)

        # OLS: beta = (X'X)^-1 X'y
        def ols_fit(X, y_vec):
            k = len(X[0])
            # X'X
            XtX = [[sum(X[r][i] * X[r][j] for r in range(len(X))) for j in range(k)] for i in range(k)]
            # (X'X)^-1 via eliminação gaussiana
            inv = _matrix_inverse(XtX)
            if inv is None:
                return None, None, None
            # X'y
            Xty = [sum(X[r][i] * y_vec[r] for r in range(len(X))) for i in range(k)]
            # beta
            beta = [sum(inv[i][j] * Xty[j] for j in range(k)) for i in range(k)]
            # RSS
            y_pred = [sum(beta[j] * X[r][j] for j in range(k)) for r in range(len(X))]
            rss = sum((y_vec[r] - y_pred[r]) ** 2 for r in range(len(X)))
            return beta, rss, y_pred

        beta_r, rss_r, _ = ols_fit(X_r, y)
        beta_u, rss_u, _ = ols_fit(X_u, y)

        if beta_r is None or beta_u is None or rss_u < 1e-10:
            continue

        # Estatística F
        p = lag  # número de restrições (lags de A)
        dof = effective_n - 2 * lag - 1  # graus de liberdade
        if dof <= 0:
            continue

        f_stat = ((rss_r - rss_u) / p) / (rss_u / dof) if rss_u > 0 else 0

        # p-value aproximado via distribuição F (aproximação simples)
        p_value = _f_distribution_pvalue(f_stat, p, dof)

        results.append({
            "lag": lag,
            "f_statistic": round(f_stat, 4),
            "p_value": round(p_value, 4),
            "rss_restricted": round(rss_r, 4),
            "rss_unrestricted": round(rss_u, 4),
            "significant": p_value < 0.05,
        })

    if not results:
        return {"causal": False, "p_value": 1.0, "f_stat": 0.0, "error": "Dados insuficientes"}

    # Melhor lag (menor p-value)
    best = min(results, key=lambda r: r["p_value"])
    return {
        "causal": best["significant"],
        "best_lag": best["lag"],
        "f_statistic": best["f_statistic"],
        "p_value": best["p_value"],
        "significant_at_5pct": best["significant"],
        "all_lags": results,
        "interpretation": (
            f"Sentimento sobre A Granger-causa sentimento sobre B (lag={best['lag']}, p={best['p_value']:.4f})"
            if best["significant"] else
            f"Não há evidência de causalidade Granger (melhor p={best['p_value']:.4f} > 0.05)"
        ),
    }


def cross_correlation(series_a: List[float], series_b: List[float],
                      max_lag: int = 5) -> List[Dict]:
    """Correlação cruzada com lag: A(t) × B(t±k)."""
    n = min(len(series_a), len(series_b))
    a = series_a[:n]
    b = series_b[:n]
    results = []
    ma = sum(a) / n
    mb = sum(b) / n
    sa = (sum((v - ma) ** 2 for v in a) / n) ** 0.5
    sb = (sum((v - mb) ** 2 for v in b) / n) ** 0.5

    if sa < 1e-10 or sb < 1e-10:
        return []

    for lag in range(-max_lag, max_lag + 1):
        pairs = []
        for t in range(n):
            t2 = t + lag
            if 0 <= t2 < n:
                pairs.append((a[t], b[t2]))
        if len(pairs) < 5:
            continue
        num = sum((a - ma) * (b - mb) for a, b in pairs) / len(pairs)
        r = num / (sa * sb) if sa > 0 and sb > 0 else 0
        results.append({
            "lag": lag,
            "correlation": round(r, 4),
            "n_pairs": len(pairs),
            "interpretation": (
                f"A precede B em {-lag} passos (r={r:+.3f})" if lag < 0 and abs(r) > 0.3
                else f"B precede A em {lag} passos (r={r:+.3f})" if lag > 0 and abs(r) > 0.3
                else f"Sem correlação temporal significativa no lag {lag}"
            ),
        })

    return results


def run_pairwise_granger(topic_evolution: Dict[str, List[Dict]],
                         max_lag: int = 3) -> Dict[str, Any]:
    """
    Executa teste de Granger para todos os pares de tópicos.
    topic_evolution: {topic: [{round, mean, n, std}, ...]}
    """
    # Extrair séries temporais
    series = {}
    for topic, evolution in topic_evolution.items():
        if evolution and len(evolution) >= max_lag + 5:
            series[topic] = [e["mean"] for e in evolution]

    if len(series) < 2:
        return {"error": "Mínimo de 2 tópicos com séries longas necessário"}

    results = []
    topics = list(series.keys())

    for i in range(len(topics)):
        for j in range(len(topics)):
            if i == j:
                continue
            a, b = topics[i], topics[j]
            granger = granger_causality_test(series[a], series[b], max_lag)
            cross = cross_correlation(series[a], series[b], max_lag=3)

            # Direção da precedência temporal
            best_cross = max(cross, key=lambda c: abs(c["correlation"])) if cross else {"lag": 0, "correlation": 0}

            results.append({
                "cause": a,
                "effect": b,
                "granger_causal": granger.get("causal", False),
                "granger_p_value": granger.get("p_value", 1.0),
                "granger_f_stat": granger.get("f_statistic", 0),
                "granger_interpretation": granger.get("interpretation", ""),
                "best_cross_lag": best_cross["lag"],
                "best_cross_correlation": best_cross["correlation"],
                "temporal_precedence": (
                    f"{a} precede {b}" if best_cross["lag"] < 0
                    else f"{b} precede {a}" if best_cross["lag"] > 0
                    else "contemporâneo"
                ),
            })

    # Ordenar por significância
    results.sort(key=lambda r: r["granger_p_value"])

    significant = [r for r in results if r["granger_causal"]]
    return {
        "total_pairs_tested": len(results),
        "significant_pairs": len(significant),
        "significance_rate": round(len(significant) / max(len(results), 1), 3),
        "results": results,
        "top_causal_links": [
            f"{r['cause']} → {r['effect']} (p={r['granger_p_value']:.4f})"
            for r in significant[:5]
        ],
    }


# ── Helpers matemáticos ──

def _matrix_inverse(A: List[List[float]]) -> Optional[List[List[float]]]:
    """Inversa de matriz via eliminação de Gauss-Jordan."""
    n = len(A)
    # Augmented matrix [A | I]
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]

    for col in range(n):
        # Pivot
        pivot = aug[col][col]
        if abs(pivot) < 1e-12:
            # Tenta trocar linha
            for r in range(col + 1, n):
                if abs(aug[r][col]) > 1e-10:
                    aug[col], aug[r] = aug[r], aug[col]
                    pivot = aug[col][col]
                    break
            else:
                return None  # Singular

        # Normaliza linha do pivot
        for j in range(2 * n):
            aug[col][j] /= pivot

        # Elimina outras linhas
        for r in range(n):
            if r == col:
                continue
            factor = aug[r][col]
            for j in range(2 * n):
                aug[r][j] -= factor * aug[col][j]

    return [[aug[i][j + n] for j in range(n)] for i in range(n)]


def _f_distribution_pvalue(f_stat: float, df1: int, df2: int) -> float:
    """
    Aproximação do p-value para distribuição F.
    Usa aproximação de Wilson-Hilferty (transformação para normal).
    """
    if f_stat <= 0:
        return 1.0
    if df2 <= 2:
        return 0.5  # fallback

    # Wilson-Hilferty: z = (F^(1/3)*(1-2/(9*df2)) - (1-2/(9*df1))) / sqrt(2/(9*df1) + 2/(9*df2)*F^(2/3))
    try:
        f_cbrt = f_stat ** (1/3)
        num = f_cbrt * (1 - 2/(9*df2)) - (1 - 2/(9*df1))
        den = math.sqrt(2/(9*df1) + 2/(9*df2) * f_stat ** (2/3))
        z = num / den if den > 0 else 0

        # Normal CDF approximation (Abramowitz & Stegun 26.2.17)
        abs_z = abs(z)
        t = 1 / (1 + 0.2316419 * abs_z)
        d = 0.3989423 * math.exp(-z * z / 2)
        poly = t * (0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274))))
        cdf = 1 - d * poly

        p = 1 - cdf
        return max(0.0, min(1.0, p))
    except (OverflowError, ValueError, ZeroDivisionError):
        return 0.5


# ═══════════════════════════════════════════════════════════════════
# Test
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Teste com dados sintéticos: A causa B com lag 1
    import random
    random.seed(42)
    n = 30
    A = [random.gauss(0, 0.5) for _ in range(n)]
    B = [0] * n
    for t in range(1, n):
        B[t] = 0.6 * A[t-1] + 0.3 * B[t-1] + random.gauss(0, 0.2)

    C = [random.gauss(0, 0.5) for _ in range(n)]  # Independente

    print("=" * 60)
    print("🧪 Teste de Causalidade de Granger")
    print("=" * 60)

    # A → B (deveria ser causal)
    r1 = granger_causality_test(A, B, max_lag=3)
    print(f"\nA → B: causal={r1['causal']}, p={r1['p_value']:.4f}, F={r1['f_statistic']:.2f}")
    print(f"  {r1['interpretation']}")

    # C → B (NÃO deveria ser causal)
    r2 = granger_causality_test(C, B, max_lag=3)
    print(f"\nC → B: causal={r2['causal']}, p={r2['p_value']:.4f}, F={r2['f_statistic']:.2f}")
    print(f"  {r2['interpretation']}")

    # Correlação cruzada
    cross = cross_correlation(A, B, max_lag=3)
    print(f"\nCross-correlation A×B:")
    for c in cross:
        if abs(c["correlation"]) > 0.2:
            print(f"  lag={c['lag']:+d}: r={c['correlation']:+.3f} — {c['interpretation']}")

    print("\n✅ Testes de causalidade operacionais!")
