# SPEC-COR-D2: Modelagem de Sistemas Fisicos (CORA-Eval)
Version: 1.0.0 | Status: verified | TDD: verified

## Objective
Suite TDD para D2 do CORA-Eval — validacao de leis fisicas classicas com integracao numerica e analitica.

## Acceptance Criteria
- [x] CT-1: Movimento Retilineo Uniforme — x = x0 + v*t validado para 100 tempos aleatorios
- [x] CT-2: Queda Livre — y = (1/2)gt^2 validado por integracao numerica (dt=0.001, erro < 1%)
- [x] CT-3: Conservacao de Energia — Pendulo simples (E_potencial = E_cinetica no ponto mais baixo)
- [x] CT-4: Analise Dimensional — [F] = M·L·T^-2 em F = ma (F = 5.0 * 9.81 = 49.05 N)
- [x] CT-5: Lei de Hooke — Linearidade F = -k·x com R^2 > 0.999 para 5 pontos
- [x] CT-6: Pendulo — Periodo T = 2 pi sqrt(L/g) e relacao T^2 proporcional a L
- [x] CT-7: Conservacao de Momento — Colisao elastica 1D (p_inicial = p_final)
- [x] CT-8: Gas Ideal — PV = nRT para 5 pares (T, V) com R = 8.314

## Test File
tests/test_d2_fisica.py
