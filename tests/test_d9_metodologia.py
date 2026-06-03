"""
test_d9_metodologia.py — SPEC-011: D9 Desenho Experimental e Metodologia
8 CTs, pytest, RED->GREEN->REFACTOR
"""
import math
import random
import pytest
from scipy import stats
import numpy as np

random.seed(42)
np.random.seed(42)


class TestANOVA:
    """D9-1: ANOVA one-way — F significativo com grupos diferentes"""

    def test_anova_significant(self):
        g1 = np.random.normal(10, 1, 30)
        g2 = np.random.normal(15, 1, 30)
        g3 = np.random.normal(12, 1, 30)
        F_stat, p_value = stats.f_oneway(g1, g2, g3)
        assert p_value < 0.001, f"ANOVA deveria ser significativa, p={p_value:.4f}"

    def test_anova_not_significant(self):
        g1 = np.random.normal(10, 1, 30)
        g2 = np.random.normal(10, 1, 30)
        g3 = np.random.normal(10, 1, 30)
        _, p_value = stats.f_oneway(g1, g2, g3)
        assert p_value > 0.05, f"ANOVA nao deveria ser significativa, p={p_value:.4f}"


class TestTTest:
    """D9-2: Teste t — rejeita H0 com diferenca grande"""

    def test_ttest_significant(self):
        g1 = np.random.normal(10, 1, 30)
        g2 = np.random.normal(14, 1, 30)  # diferenca de 4 desvios-padrao
        t_stat, p_value = stats.ttest_ind(g1, g2)
        assert p_value < 0.001

    def test_ttest_not_significant(self):
        g1 = np.random.normal(10, 1, 30)
        g2 = np.random.normal(10.1, 1, 30)
        _, p_value = stats.ttest_ind(g1, g2)
        assert p_value > 0.05


class TestRandomization:
    """D9-3: Randomizacao — grupos nao diferem antes do tratamento"""

    def test_random_assignment(self):
        """Randomizacao deve produzir grupos comparaveis"""
        population = np.random.normal(100, 15, 60)
        np.random.shuffle(population)
        g1 = population[:30]
        g2 = population[30:]
        _, p_value = stats.ttest_ind(g1, g2)
        assert p_value > 0.05, f"Grupos randomizados diferem: p={p_value:.4f}"


class TestCohenD:
    """D9-4: Cohen's d — tamanho de efeito"""

    def cohens_d(self, x, y):
        nx, ny = len(x), len(y)
        pooled_std = math.sqrt(
            ((nx-1)*np.var(x, ddof=1) + (ny-1)*np.var(y, ddof=1)) / (nx+ny-2)
        )
        return abs(np.mean(x) - np.mean(y)) / pooled_std

    def test_large_effect(self):
        g1 = np.random.normal(10, 1, 50)
        g2 = np.random.normal(14, 1, 50)
        d = self.cohens_d(g1, g2)
        assert d > 0.8, f"Cohen's d={d:.2f}, esperado > 0.8 (large effect)"

    def test_small_effect(self):
        g1 = np.random.normal(10, 1, 50)
        g2 = np.random.normal(10.3, 1, 50)
        d = self.cohens_d(g1, g2)
        assert d < 0.5, f"Cohen's d={d:.2f}, esperado < 0.5 (small effect)"


class TestStatisticalPower:
    """D9-5: Poder estatistico"""

    def _power_ttest(self, d, n, alpha=0.05):
        """Manual power calculation using non-central t distribution"""
        nc = d * math.sqrt(n / 2)
        df = 2*n - 2
        t_crit = stats.t.ppf(1 - alpha/2, df)
        power = 1 - stats.nct.cdf(t_crit, df, nc) + stats.nct.cdf(-t_crit, df, nc)
        return power

    def test_power_adequate(self):
        power = self._power_ttest(d=0.5, n=30)
        assert power > 0.4, f"Poder={power:.3f} para d=0.5, n=30"

    def test_power_increases_with_n(self):
        p30 = self._power_ttest(d=0.5, n=30)
        p100 = self._power_ttest(d=0.5, n=100)
        assert p100 > p30, "Poder deveria aumentar com n"


class TestNormality:
    """D9-6: Shapiro-Wilk detecta nao-normalidade"""

    def test_shapiro_normal(self):
        data = np.random.normal(0, 1, 100)
        _, p = stats.shapiro(data)
        assert p > 0.05, f"Normal deveria ter p>0.05, p={p:.4f}"

    def test_shapiro_exponential(self):
        data = np.random.exponential(1, 100)
        _, p = stats.shapiro(data)
        assert p < 0.05, f"Exponencial deveria ter p<0.05, p={p:.4f}"


class TestErrorPropagation:
    """D9-7: Propagacao de erros"""

    def test_error_propagation(self):
        x, y = 10.0, 5.0
        dx, dy = 0.1, 0.1

        def f(x, y): return x * y

        # Derivadas parciais numericas
        h = 1e-6
        dfdx = (f(x+h, y) - f(x-h, y)) / (2*h)
        dfdy = (f(x, y+h) - f(x, y-h)) / (2*h)

        dz = math.sqrt((dfdx * dx)**2 + (dfdy * dy)**2)
        expected = math.sqrt((y*dx)**2 + (x*dy)**2)

        assert abs(dz - expected) / expected < 1e-4, f"dz={dz:.4f}, expected={expected:.4f}"


class TestFactorialDesign:
    """D9-8: Delineamento fatorial 2²"""

    def test_factorial_2x2(self):
        data = {
            (25, 6.0): [10, 12, 11],
            (25, 8.0): [8, 9, 7],
            (37, 6.0): [15, 16, 14],
            (37, 8.0): [18, 20, 19],
        }

        A_low = [v for (T, pH), vals in data.items() if T == 25 for v in vals]
        A_high = [v for (T, pH), vals in data.items() if T == 37 for v in vals]
        B_low = [v for (T, pH), vals in data.items() if pH == 6.0 for v in vals]
        B_high = [v for (T, pH), vals in data.items() if pH == 8.0 for v in vals]

        effect_A = np.mean(A_high) - np.mean(A_low)
        effect_B = np.mean(B_high) - np.mean(B_low)

        # Manual calc: A_low mean=(11+8+9)/3=9.33, A_high mean=(15+18+19)/3=17.33
        assert effect_A > 0, "Temperatura mais alta aumenta atividade"
        assert 6.0 < effect_A < 10.0, f"Efeito A={effect_A:.2f}"

        # pH effect is weaker: B_low mean=13.0, B_high mean=13.5
        assert abs(effect_B) < 3.0, f"Efeito B={effect_B:.2f} deveria ser menor"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
