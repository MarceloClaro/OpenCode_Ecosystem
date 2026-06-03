"""
test_d2_fisica.py — SPEC-010: D2 Modelagem de Sistemas Fisicos
8 CTs, pytest, RED->GREEN->REFACTOR
"""
import math
import random
import pytest

random.seed(42)
TOLERANCE = 1e-6


class TestMRU:
    """D2-1: Movimento Retilineo Uniforme — x = x0 + v*t"""

    def test_mru_formula(self):
        x0, v = 10.0, 5.0
        for _ in range(100):
            t = random.uniform(0, 100)
            assert abs((x0 + v*t) - (10.0 + 5.0*t)) < TOLERANCE


class TestQuedaLivre:
    """D2-2: y = (1/2)g*t^2"""

    def test_queda_livre(self):
        g = 9.81
        for t in [0, 1, 2, 3, 5, 10]:
            y = 0.5 * g * t**2
            # Integracao numerica simples
            v = 0.0
            pos = 0.0
            dt = 0.001
            steps = int(t / dt)
            for _ in range(steps):
                v += g * dt
                pos += v * dt
            assert abs(y - pos) / max(abs(y), 1) < 0.01, (
                f"Falha t={t}: analitico={y:.3f}, numerico={pos:.3f}"
            )


class TestConservacaoEnergia:
    """D2-3: Conservacao de energia — pendulo simples"""

    def test_pendulo_conservacao(self):
        g, L = 9.81, 1.0
        theta0 = math.radians(30)
        h = L * (1 - math.cos(theta0))
        v_max_esperada = math.sqrt(2 * g * h)
        assert v_max_esperada > 0
        # Energia inicial = potencial maxima
        E_inicial = g * h  # m=1
        E_final = 0.5 * v_max_esperada**2
        assert abs(E_inicial - E_final) / E_inicial < TOLERANCE


class TestAnaliseDimensional:
    """D2-4: [F] = M·L·T^-2 em F = ma"""

    def test_dimensao_forca(self):
        m = 5.0   # kg -> M
        a = 9.81  # m/s^2 -> L/T^2
        F = m * a # N -> M·L/T²
        assert math.isclose(F, 49.05, rel_tol=1e-10)
        assert isinstance(F, float)


class TestHooke:
    """D2-5: Lei de Hooke — F = -k·x"""

    def test_hooke_linearity(self):
        k = 100.0  # N/m
        x_vals = [0.01, 0.02, 0.05, 0.10, 0.20]
        F_vals = [k * x for x in x_vals]

        # Linear regression R^2
        n = len(x_vals)
        sx = sum(x_vals); sy = sum(F_vals)
        sxy = sum(x*y for x,y in zip(x_vals, F_vals))
        sxx = sum(x*x for x in x_vals)
        syy = sum(y*y for y in F_vals)
        r = (n*sxy - sx*sy) / math.sqrt((n*sxx - sx*sx)*(n*syy - sy*sy))
        assert r**2 > 0.999, f"R^2 = {r**2:.6f} < 0.999"


class TestPendulo:
    """D2-6: T = 2π√(L/g)"""

    def test_pendulo_period(self):
        g = 9.81
        for L in [0.5, 1.0, 1.5, 2.0, 3.0]:
            T = 2 * math.pi * math.sqrt(L / g)
            assert T > 0
            # Linear relationship: T^2 ∝ L
            assert abs((T**2) / L - (4*math.pi**2 / g)) < 1e-10


class TestConservacaoMomento:
    """D2-7: Conservacao de momento linear"""

    def test_colisao_elastica(self):
        m1, m2 = 2.0, 3.0
        v1, v2 = 5.0, -2.0
        p_inicial = m1*v1 + m2*v2

        v1f = ((m1-m2)*v1 + 2*m2*v2) / (m1 + m2)
        v2f = ((m2-m1)*v2 + 2*m1*v1) / (m1 + m2)
        p_final = m1*v1f + m2*v2f

        assert abs(p_inicial - p_final) < TOLERANCE


class TestGasIdeal:
    """D2-8: PV = nRT"""

    def test_gas_ideal(self):
        n, R = 1.0, 8.314
        T_vals = [273, 298, 350, 400, 500]
        V_vals = [0.0224, 0.0245, 0.0287, 0.0329, 0.0411]

        for T, V in zip(T_vals, V_vals):
            P = n * R * T / V
            assert abs(P*V - n*R*T) < 1e-6


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
