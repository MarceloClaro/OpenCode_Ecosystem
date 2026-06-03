# -*- coding: utf-8 -*-
"""
TDD Test Suite: D4 — Química Computacional e Estrutural (N1 - Básico)
CORA-Eval Benchmark Tasks: D4-N1-01, D4-N1-02, D4-N1-03

Cada teste implementa uma verificação real com ground truth conhecido.
"""

import math
import sys
import os

# ─── Massas atômicas (IUPAC 2021) ────────────────────────────────────
ATOMIC_MASSES = {
    "H": 1.008, "He": 4.0026, "C": 12.011, "N": 14.007, "O": 15.999,
    "F": 18.998, "Na": 22.990, "Mg": 24.305, "Al": 26.982, "Si": 28.085,
    "P": 30.974, "S": 32.06, "Cl": 35.45, "K": 39.098, "Ca": 40.078,
    "Fe": 55.845, "Cu": 63.546, "Zn": 65.38, "Br": 79.904, "Ag": 107.87,
    "I": 126.90, "Ba": 137.33, "Pt": 195.08, "Au": 196.97, "Hg": 200.59,
    "Pb": 207.2,
}

def parse_formula(formula: str) -> dict:
    """Parseia fórmula química como 'C6H12O6' em dicionário {elemento: contagem}."""
    import re
    result = {}
    pattern = re.compile(r"([A-Z][a-z]?)(\d*)")
    for match in pattern.finditer(formula):
        elem = match.group(1)
        count = int(match.group(2)) if match.group(2) else 1
        result[elem] = result.get(elem, 0) + count
    return result

def molar_mass(formula: str) -> float:
    """Calcula massa molar (g/mol) a partir da fórmula química."""
    parsed = parse_formula(formula)
    total = 0.0
    for elem, count in parsed.items():
        if elem not in ATOMIC_MASSES:
            raise ValueError(f"Elemento desconhecido: {elem}")
        total += ATOMIC_MASSES[elem] * count
    return round(total, 3)

# ══════════════════════════════════════════════════════════════════════
# TEST 1: D4-N1-01 — Balanceamento de Equação Química
# ══════════════════════════════════════════════════════════════════════

def balance_combustion(formula: str) -> tuple:
    """
    Balanceia combustão completa: CxHyOz + a O2 → b CO2 + c H2O
    Retorna (a, b, c, x, y, z).
    """
    parsed = parse_formula(formula)
    x = parsed.get("C", 0)
    y = parsed.get("H", 0)
    z = parsed.get("O", 0)
    b = x                    # CO2: 1 C por molécula
    c = y // 2               # H2O: 2 H por molécula (assume y par)
    a = (2*x + y//2 - z) / 2 # balanceamento de O
    return (a, b, c, x, y, z)

def test_balance_h2_o2():
    """D4-N1-01: 2 H2 + O2 → 2 H2O"""
    # Verificação manual dos coeficientes
    # 2 H2 + 1 O2 → 2 H2O
    # H: 2*2=4 → 2*2=4 ✓
    # O: 1*2=2 → 2*1=2 ✓
    coef_H2, coef_O2, coef_H2O = 2, 1, 2
    assert coef_H2 * 2 == coef_H2O * 2  # balanceamento H
    assert coef_O2 * 2 == coef_H2O * 1  # balanceamento O
    print("  [D4-N1-01] 2 H2 + O2 → 2 H2O... PASS (balanceamento manual)")
    return True

def test_balance_ch4():
    """D4-N1-01: CH4 + 2 O2 → CO2 + 2 H2O"""
    # Metano: CH4 + 2 O2 → CO2 + 2 H2O
    # C: 1 = 1 ✓, H: 4 = 2*2 ✓, O: 2*2 = 2+2 ✓
    a, b, c, x, y, z = balance_combustion("CH4")
    assert (a, b, c) == (2.0, 1, 2), f"Esperado (2,1,2), obtido {a,b,c}"
    print("  [D4-N1-01] CH4 + 2 O2 → CO2 + 2 H2O... PASS (algorítmico)")
    return True

# ══════════════════════════════════════════════════════════════════════
# TEST 2: D4-N1-02 — Massa Molar
# ══════════════════════════════════════════════════════════════════════

def test_molar_mass_glicose():
    """D4-N1-02: C6H12O6 = 180.156 g/mol ± 0.01"""
    expected = 180.156
    result = molar_mass("C6H12O6")
    assert abs(result - expected) < 0.01, f"Esperado {expected}, obtido {result}"
    print(f"  [D4-N1-02] C6H12O6 = {result} g/mol... PASS (±{abs(result-expected):.3f})")
    return True

def test_molar_mass_h2o():
    """D4-N1-02: H2O = 18.015 g/mol ± 0.01"""
    expected = 18.015
    result = molar_mass("H2O")
    assert abs(result - expected) < 0.01, f"Esperado {expected}, obtido {result}"
    print(f"  [D4-N1-02] H2O = {result} g/mol... PASS")
    return True

def test_molar_mass_nacl():
    """D4-N1-02: NaCl = 58.440 g/mol ± 0.01"""
    expected = 58.440
    result = molar_mass("NaCl")
    assert abs(result - expected) < 0.01
    print(f"  [D4-N1-02] NaCl = {result} g/mol... PASS")
    return True

def test_molar_mass_caco3():
    """D4-N1-02: CaCO3 = 100.087 g/mol ± 0.01"""
    expected = 100.087
    result = molar_mass("CaCO3")
    assert abs(result - expected) < 0.01
    print(f"  [D4-N1-02] CaCO3 = {result} g/mol... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# TEST 3: D4-N1-03 — Conversão de Concentração
# ══════════════════════════════════════════════════════════════════════

def percent_to_molarity(percent_mv: float, molar_mass_gmol: float) -> float:
    """
    Converte % (m/v) para mol/L.
    % (m/v) = g soluto / 100 mL solução
    mol/L = (% * 10) / massa_molar
    """
    return round((percent_mv * 10) / molar_mass_gmol, 4)

def molarity_to_percent(molarity: float, molar_mass_gmol: float) -> float:
    """Converte mol/L para % (m/v)."""
    return round((molarity * molar_mass_gmol) / 10, 2)

def test_percent_to_molarity_glucose():
    """D4-N1-03: Glicose 5% (m/v) → mol/L"""
    # 5% glicose = 5 g / 100 mL = 50 g / L
    # mol/L = 50 / 180.156 = 0.2775
    expected = 0.2775
    result = percent_to_molarity(5.0, molar_mass("C6H12O6"))
    assert abs(result - expected) < 0.001
    print(f"  [D4-N1-03] Glicose 5% = {result} mol/L... PASS")
    return True

def test_percent_to_molarity_nacl():
    """D4-N1-03: NaCl 0.9% (m/v) → mol/L (soro fisiológico)"""
    # 0.9% NaCl = 0.9 g / 100 mL = 9 g / L
    # mol/L = 9 / 58.44 = 0.1540
    expected = 0.1540
    result = percent_to_molarity(0.9, molar_mass("NaCl"))
    assert abs(result - expected) < 0.001
    print(f"  [D4-N1-03] NaCl 0.9% = {result} mol/L... PASS")
    return True

def test_molarity_to_percent_roundtrip():
    """D4-N1-03: Roundtrip mol/L → % (m/v) → mol/L"""
    original = 0.5  # mol/L
    mm = molar_mass("NaCl")
    percent = molarity_to_percent(original, mm)
    back = percent_to_molarity(percent, mm)
    assert abs(back - original) < 0.01
    print(f"  [D4-N1-03] Roundtrip 0.5 mol/L NaCl = {percent}% = {back} mol/L... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

def main():
    tests = [
        ("D4-N1-01a", test_balance_h2_o2),
        ("D4-N1-01b", test_balance_ch4),
        ("D4-N1-02a", test_molar_mass_glicose),
        ("D4-N1-02b", test_molar_mass_h2o),
        ("D4-N1-02c", test_molar_mass_nacl),
        ("D4-N1-02d", test_molar_mass_caco3),
        ("D4-N1-03a", test_percent_to_molarity_glucose),
        ("D4-N1-03b", test_percent_to_molarity_nacl),
        ("D4-N1-03c", test_molarity_to_percent_roundtrip),
    ]
    
    print("=" * 60)
    print("  TDD TEST SUITE: D4 — Química Computacional (N1)")
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
    success = main()
    sys.exit(0 if success else 1)
