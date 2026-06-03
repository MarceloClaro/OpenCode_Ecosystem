# -*- coding: utf-8 -*-
"""
TDD Test Suite: D5 — Biologia Molecular e Genômica (N1 - Básico)
CORA-Eval Benchmark Tasks: D5-N1-01, D5-N1-02, D5-N1-03
"""

import sys

# ─── Tabela de código genético padrão ────────────────────────────────
CODON_TABLE = {
    "UUU": "Fenilalanina", "UUC": "Fenilalanina",
    "UUA": "Leucina", "UUG": "Leucina",
    "CUU": "Leucina", "CUC": "Leucina", "CUA": "Leucina", "CUG": "Leucina",
    "AUU": "Isoleucina", "AUC": "Isoleucina", "AUA": "Isoleucina",
    "AUG": "Metionina",  # também códon de início
    "GUU": "Valina", "GUC": "Valina", "GUA": "Valina", "GUG": "Valina",
    "UCU": "Serina", "UCC": "Serina", "UCA": "Serina", "UCG": "Serina",
    "CCU": "Prolina", "CCC": "Prolina", "CCA": "Prolina", "CCG": "Prolina",
    "ACU": "Treonina", "ACC": "Treonina", "ACA": "Treonina", "ACG": "Treonina",
    "GCU": "Alanina", "GCC": "Alanina", "GCA": "Alanina", "GCG": "Alanina",
    "UAU": "Tirosina", "UAC": "Tirosina",
    "UAA": "STOP", "UAG": "STOP",
    "CAU": "Histidina", "CAC": "Histidina",
    "CAA": "Glutamina", "CAG": "Glutamina",
    "AAU": "Asparagina", "AAC": "Asparagina",
    "AAA": "Lisina", "AAG": "Lisina",
    "GAU": "Ácido Aspártico", "GAC": "Ácido Aspártico",
    "GAA": "Ácido Glutâmico", "GAG": "Ácido Glutâmico",
    "UGU": "Cisteína", "UGC": "Cisteína",
    "UGA": "STOP",
    "UGG": "Triptofano",
    "CGU": "Arginina", "CGC": "Arginina", "CGA": "Arginina", "CGG": "Arginina",
    "AGU": "Serina", "AGC": "Serina",
    "AGA": "Arginina", "AGG": "Arginina",
    "GGU": "Glicina", "GGC": "Glicina", "GGA": "Glicina", "GGG": "Glicina",
}

# ─── Funções implementadas ────────────────────────────────────────────

def transcribe(dna: str) -> str:
    """Transcreve DNA → RNA: T → U."""
    return dna.replace("T", "U").replace("t", "u")

def translate_codon(codon: str) -> str:
    """Traduz 1 códon → aminoácido."""
    return CODON_TABLE.get(codon.upper(), "DESCONHECIDO")

def translate(rna: str) -> list:
    """Traduz RNA → cadeia de aminoácidos (códons de 3 em 3)."""
    result = []
    for i in range(0, len(rna) - 2, 3):
        aa = translate_codon(rna[i:i+3])
        if aa == "STOP":
            break
        result.append(aa)
    return result

def gc_content(sequence: str) -> float:
    """Calcula %GC de uma sequência de DNA ou RNA."""
    seq = sequence.upper()
    gc = seq.count("G") + seq.count("C")
    total = len(seq)
    if total == 0:
        return 0.0
    return round(gc / total * 100, 2)

# ══════════════════════════════════════════════════════════════════════
# TEST 1: D5-N1-01 — Transcrição DNA → RNA
# ══════════════════════════════════════════════════════════════════════

def test_transcribe_atgcgt():
    """D5-N1-01: ATGCGT → AUGCGU"""
    result = transcribe("ATGCGT")
    assert result == "AUGCGU", f"Esperado AUGCGU, obtido {result}"
    print("  [D5-N1-01] ATGCGT → AUGCGU... PASS")
    return True

def test_transcribe_gattaca():
    """D5-N1-01: GATTACA → GAUUACA"""
    result = transcribe("GATTACA")
    assert result == "GAUUACA", f"Esperado GAUUACA, obtido {result}"
    print("  [D5-N1-01] GATTACA → GAUUACA... PASS")
    return True

def test_transcribe_no_t():
    """D5-N1-01: Sequência sem T permanece igual"""
    result = transcribe("GCGCGC")
    assert result == "GCGCGC"
    print("  [D5-N1-01] GCGCGC → GCGCGC (sem T)... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# TEST 2: D5-N1-02 — Tradução Códon → Aminoácido
# ══════════════════════════════════════════════════════════════════════

def test_translate_aug():
    """D5-N1-02: AUG → Metionina (códon de início)"""
    result = translate_codon("AUG")
    assert result == "Metionina", f"Esperado Metionina, obtido {result}"
    print("  [D5-N1-02] AUG → Metionina... PASS")
    return True

def test_translate_ugg():
    """D5-N1-02: UGG → Triptofano (único códon para Trp)"""
    result = translate_codon("UGG")
    assert result == "Triptofano"
    print("  [D5-N1-02] UGG → Triptofano... PASS")
    return True

def test_translate_stop():
    """D5-N1-02: UAA, UAG, UGA → STOP"""
    for codon in ["UAA", "UAG", "UGA"]:
        assert translate_codon(codon) == "STOP", f"{codon} deveria ser STOP"
    print("  [D5-N1-02] UAA/UAG/UGA → STOP... PASS")
    return True

def test_translate_full_sequence():
    """D5-N1-02: AUG GCC UGG UAA → Met-Ala-Trp (STOP)"""
    result = translate("AUGGCCUGGUAA")
    assert result == ["Metionina", "Alanina", "Triptofano"], f"Obtido {result}"
    print("  [D5-N1-02] AUG-GCC-UGG-UAA → Met-Ala-Trp... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# TEST 3: D5-N1-03 — Conteúdo %GC
# ══════════════════════════════════════════════════════════════════════

def test_gc_atgcgcat():
    """D5-N1-03: ATGCGCAT → 50% GC (4/8 = G ou C)"""
    result = gc_content("ATGCGCAT")
    assert result == 50.0, f"Esperado 50.0%, obtido {result}%"
    print(f"  [D5-N1-03] ATGCGCAT = {result}% GC... PASS")
    return True

def test_gc_all_gc():
    """D5-N1-03: GGGCCC → 100% GC"""
    result = gc_content("GGGCCC")
    assert result == 100.0
    print(f"  [D5-N1-03] GGGCCC = {result}% GC... PASS")
    return True

def test_gc_all_at():
    """D5-N1-03: ATATAT → 0% GC"""
    result = gc_content("ATATAT")
    assert result == 0.0
    print(f"  [D5-N1-03] ATATAT = {result}% GC... PASS")
    return True

def test_gc_ecoli_promoter():
    """D5-N1-03: Promotor TTGACA (E. coli -35) → 33.33% GC"""
    result = gc_content("TTGACA")
    assert abs(result - 33.33) < 1.0
    print(f"  [D5-N1-03] TTGACA = {result}% GC... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

def main():
    tests = [
        ("D5-N1-01a", test_transcribe_atgcgt),
        ("D5-N1-01b", test_transcribe_gattaca),
        ("D5-N1-01c", test_transcribe_no_t),
        ("D5-N1-02a", test_translate_aug),
        ("D5-N1-02b", test_translate_ugg),
        ("D5-N1-02c", test_translate_stop),
        ("D5-N1-02d", test_translate_full_sequence),
        ("D5-N1-03a", test_gc_atgcgcat),
        ("D5-N1-03b", test_gc_all_gc),
        ("D5-N1-03c", test_gc_all_at),
        ("D5-N1-03d", test_gc_ecoli_promoter),
    ]
    
    print("=" * 60)
    print("  TDD TEST SUITE: D5 — Biologia Molecular (N1)")
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
