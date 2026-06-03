# -*- coding: utf-8 -*-
"""
TDD Test Suite: D6 — Geociências e Modelagem Climática (N1 - Básico)
CORA-Eval Benchmark Tasks: D6-N1-01, D6-N1-02, D6-N1-03
"""

import sys

# ─── Classificação de rochas ──────────────────────────────────────────

ROCK_CLASSIFICATION = {
    "granito":  ("ígnea", "intrusiva"),
    "basalto":  ("ígnea", "extrusiva"),
    "obsidiana":("ígnea", "extrusiva"),
    "arenito":  ("sedimentar", "clástica"),
    "calcário": ("sedimentar", "química"),
    "mármore":  ("metamórfica", "não foliada"),
    "xisto":    ("metamórfica", "foliada"),
    "gnaisse":  ("metamórfica", "foliada"),
    "ardósia":  ("metamórfica", "foliada"),
    "carvão":   ("sedimentar", "orgânica"),
}

def classify_rock(name: str) -> str:
    """Classifica rocha por tipo e subtipo."""
    name = name.lower().strip()
    if name in ROCK_CLASSIFICATION:
        tipo, subtipo = ROCK_CLASSIFICATION[name]
        return f"{tipo} {subtipo}"
    return "desconhecida"

# ─── Conversão de temperatura ─────────────────────────────────────────

def celsius_to_kelvin(c: float) -> float:
    """°C → K: K = °C + 273.15"""
    return round(c + 273.15, 2)

def kelvin_to_celsius(k: float) -> float:
    """K → °C: °C = K - 273.15"""
    return round(k - 273.15, 2)

def celsius_to_fahrenheit(c: float) -> float:
    """°C → °F: °F = 1.8*°C + 32"""
    return round(1.8 * c + 32, 2)

def fahrenheit_to_celsius(f: float) -> float:
    """°F → °C: °C = (°F - 32) / 1.8"""
    return round((f - 32) / 1.8, 2)

# ─── Camadas atmosféricas ─────────────────────────────────────────────

ATMOSPHERIC_LAYERS = [
    ("Troposfera",   0, 12),
    ("Estratosfera", 12, 50),
    ("Mesosfera",    50, 85),
    ("Termosfera",   85, 600),
    ("Exosfera",     600, 10000),
]

def get_atmospheric_layer(altitude_km: float) -> str:
    """Identifica camada atmosférica por altitude (km)."""
    for name, low, high in ATMOSPHERIC_LAYERS:
        if low <= altitude_km < high:
            return name
    return "Espaço exterior"

# ══════════════════════════════════════════════════════════════════════
# TEST 1: D6-N1-01 — Classificação de Rochas
# ══════════════════════════════════════════════════════════════════════

def test_granite_igneous_intrusive():
    """D6-N1-01: Granito = ígnea intrusiva"""
    result = classify_rock("Granito")
    assert result == "ígnea intrusiva", f"Obtido {result}"
    print("  [D6-N1-01] Granito → ígnea intrusiva... PASS")
    return True

def test_basalt_extrusive():
    """D6-N1-01: Basalto = ígnea extrusiva"""
    assert classify_rock("basalto") == "ígnea extrusiva"
    print("  [D6-N1-01] Basalto → ígnea extrusiva... PASS")
    return True

def test_limestone_sedimentary():
    """D6-N1-01: Calcário = sedimentar química"""
    assert classify_rock("calcário") == "sedimentar química"
    print("  [D6-N1-01] Calcário → sedimentar química... PASS")
    return True

def test_marble_metamorphic():
    """D6-N1-01: Mármore = metamórfica não foliada"""
    assert classify_rock("mármore") == "metamórfica não foliada"
    print("  [D6-N1-01] Mármore → metamórfica não foliada... PASS")
    return True

def test_rock_cycle_completeness():
    """D6-N1-01: Verifica que os 3 tipos estão representados"""
    tipos = set()
    for name in ROCK_CLASSIFICATION:
        tipos.add(ROCK_CLASSIFICATION[name][0])
    assert tipos == {"ígnea", "sedimentar", "metamórfica"}
    print("  [D6-N1-01] Ciclo das rochas: 3 tipos presentes... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# TEST 2: D6-N1-02 — Conversão de Temperatura
# ══════════════════════════════════════════════════════════════════════

def test_celsius_to_kelvin_zero():
    """D6-N1-02: 0 °C = 273.15 K"""
    assert celsius_to_kelvin(0) == 273.15
    print("  [D6-N1-02] 0 °C = 273.15 K... PASS")
    return True

def test_kelvin_to_celsius():
    """D6-N1-02: 373.15 K = 100 °C (ebulição da água)"""
    assert kelvin_to_celsius(373.15) == 100.0
    print("  [D6-N1-02] 373.15 K = 100 °C... PASS")
    return True

def test_celsius_to_fahrenheit():
    """D6-N1-02: 100 °C = 212 °F"""
    assert celsius_to_fahrenheit(100) == 212.0
    print("  [D6-N1-02] 100 °C = 212 °F... PASS")
    return True

def test_fahrenheit_to_celsius():
    """D6-N1-02: 32 °F = 0 °C"""
    assert fahrenheit_to_celsius(32) == 0.0
    print("  [D6-N1-02] 32 °F = 0 °C... PASS")
    return True

def test_roundtrip_kelvin():
    """D6-N1-02: Roundtrip K → °C → K"""
    original = 300.0
    assert abs(celsius_to_kelvin(kelvin_to_celsius(original)) - original) < 0.01
    print("  [D6-N1-02] Roundtrip K↔°C consistente... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# TEST 3: D6-N1-03 — Camadas Atmosféricas
# ══════════════════════════════════════════════════════════════════════

def test_troposphere():
    """D6-N1-03: 5 km → Troposfera (0-12 km)"""
    assert get_atmospheric_layer(5) == "Troposfera"
    print("  [D6-N1-03] 5 km → Troposfera... PASS")
    return True

def test_stratosphere():
    """D6-N1-03: 30 km → Estratosfera (12-50 km)"""
    assert get_atmospheric_layer(30) == "Estratosfera"
    print("  [D6-N1-03] 30 km → Estratosfera... PASS")
    return True

def test_mesosphere():
    """D6-N1-03: 70 km → Mesosfera (50-85 km)"""
    assert get_atmospheric_layer(70) == "Mesosfera"
    print("  [D6-N1-03] 70 km → Mesosfera... PASS")
    return True

def test_thermosphere():
    """D6-N1-03: 400 km → Termosfera (85-600 km), órbita ISS"""
    assert get_atmospheric_layer(400) == "Termosfera"
    print("  [D6-N1-03] 400 km (ISS) → Termosfera... PASS")
    return True

def test_boundary_tropopause():
    """D6-N1-03: 12 km (tropopausa) → Estratosfera"""
    assert get_atmospheric_layer(12) == "Estratosfera"
    print("  [D6-N1-03] 12 km (tropopausa) → Estratosfera... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

def main():
    tests = [
        ("D6-N1-01a", test_granite_igneous_intrusive),
        ("D6-N1-01b", test_basalt_extrusive),
        ("D6-N1-01c", test_limestone_sedimentary),
        ("D6-N1-01d", test_marble_metamorphic),
        ("D6-N1-01e", test_rock_cycle_completeness),
        ("D6-N1-02a", test_celsius_to_kelvin_zero),
        ("D6-N1-02b", test_kelvin_to_celsius),
        ("D6-N1-02c", test_celsius_to_fahrenheit),
        ("D6-N1-02d", test_fahrenheit_to_celsius),
        ("D6-N1-02e", test_roundtrip_kelvin),
        ("D6-N1-03a", test_troposphere),
        ("D6-N1-03b", test_stratosphere),
        ("D6-N1-03c", test_mesosphere),
        ("D6-N1-03d", test_thermosphere),
        ("D6-N1-03e", test_boundary_tropopause),
    ]
    
    print("=" * 60)
    print("  TDD TEST SUITE: D6 — Geociências (N1)")
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
