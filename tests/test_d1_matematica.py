"""
test_d1_matematica.py — SPEC-009: D1 Raciocinio Matematico Formal
8 CTs, pytest, RED->GREEN->REFACTOR
"""
import math
import random
import pytest

random.seed(42)

class TestPythagoras:
    """D1-1: Teorema de Pitagoras — identidade a^2 + b^2 = c^2"""

    def test_triplas_pitagoricas(self):
        triplas = [(3,4,5), (5,12,13), (8,15,17), (7,24,25), (20,21,29)]
        for a, b, c in triplas:
            assert a**2 + b**2 == c**2, f"Falha: {a}²+{b}² ≠ {c}²"

    def test_tripla_aleatoria(self):
        for _ in range(100):
            m, n = random.randint(2, 50), random.randint(1, 50)
            if m <= n: m, n = n, m
            a = m**2 - n**2
            b = 2*m*n
            c = m**2 + n**2
            assert abs(a**2 + b**2 - c**2) < 1e-10


class TestGaussSum:
    """D1-2: Soma de Gauss — n(n+1)/2"""

    def test_gauss_formula(self):
        for n in range(1, 1001):
            expected = n * (n + 1) // 2
            computed = sum(range(1, n + 1))
            assert computed == expected, f"Falha para n={n}"

    def test_edge_cases(self):
        assert 0 * 1 // 2 == 0  # n=0
        assert 1 * 2 // 2 == 1  # n=1


class TestFactorial:
    """D1-3: Fatorial — definicao recursiva"""

    def factorial_recursive(self, n):
        if n <= 1: return 1
        return n * self.factorial_recursive(n - 1)

    def test_vs_math_factorial(self):
        for n in range(21):
            assert self.factorial_recursive(n) == math.factorial(n)

    def test_factorial_properties(self):
        assert math.factorial(0) == 1
        assert math.factorial(5) == 120
        assert math.factorial(10) == 3628800


class TestFibonacci:
    """D1-4: Fibonacci — formula de Binet"""

    def fib_iterative(self, n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    def fib_binet(self, n):
        phi = (1 + math.sqrt(5)) / 2
        psi = (1 - math.sqrt(5)) / 2
        return int((phi**n - psi**n) / math.sqrt(5))

    def test_binet_matches_iterative(self):
        for n in range(1, 31):
            assert self.fib_iterative(n) == self.fib_binet(n), f"Falha n={n}"

    def test_known_values(self):
        assert self.fib_iterative(0) == 0
        assert self.fib_iterative(10) == 55
        assert self.fib_iterative(20) == 6765


class TestPrimes:
    """D1-5: Crivo de Eratostenes"""

    def sieve(self, n):
        is_prime = [True] * (n + 1)
        is_prime[0] = is_prime[1] = False
        for i in range(2, int(n**0.5) + 1):
            if is_prime[i]:
                for j in range(i*i, n + 1, i):
                    is_prime[j] = False
        return [i for i in range(n + 1) if is_prime[i]]

    def test_primes_up_to_100(self):
        known = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]
        assert self.sieve(100)[:25] == known[:25]

    def test_count_primes_up_to_1000(self):
        # 168 primos ate 1000
        assert len(self.sieve(1000)) == 168


class TestGCD:
    """D1-6: MDC — algoritmo de Euclides"""

    def euclid(self, a, b):
        while b:
            a, b = b, a % b
        return a

    def test_vs_math_gcd(self):
        for _ in range(1000):
            a = random.randint(1, 10000)
            b = random.randint(1, 10000)
            assert self.euclid(a, b) == math.gcd(a, b)

    def test_known_pairs(self):
        assert self.euclid(48, 18) == 6
        assert self.euclid(1071, 462) == 21


class TestTrigonometry:
    """D1-7: sin^2 + cos^2 = 1"""

    def test_pythagorean_identity(self):
        for _ in range(1000):
            theta = random.uniform(-10*math.pi, 10*math.pi)
            result = math.sin(theta)**2 + math.cos(theta)**2
            assert abs(result - 1.0) < 1e-10, f"Falha theta={theta}: {result}"


class TestDerivative:
    """D1-8: (x^n)' = n x^(n-1) via limite"""

    def numerical_derivative(self, f, x, h=1e-7):
        return (f(x + h) - f(x - h)) / (2*h)

    def test_power_rule(self):
        for n in [1, 2, 3, 4, 5, 7, 10]:
            x = random.uniform(1, 5)
            analytic = n * x**(n-1)
            numeric = self.numerical_derivative(lambda t: t**n, x)
            assert abs(numeric - analytic) / abs(analytic) < 1e-5, (
                f"Falha: d/dx x^{n} em x={x}: analitico={analytic}, numerico={numeric}"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
