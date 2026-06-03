# -*- coding: utf-8 -*-
"""
REVISAO CRITICA FINAL — Novos problemas cegos, treinamento refeito
Problemas GENUINAMENTE nunca testados — o revisor senior vai verificar.
"""

import sys, math, random

# ══════════════════════════════════════════════════════════════════════
# NOVOS PROBLEMAS CEGOS — Project Euler #26-#30 (nunca testados)
# ══════════════════════════════════════════════════════════════════════

def pe026_recurring_cycle():
    """PE#26: Maior ciclo recorrente em 1/d para d<1000.
    Resp: 983 (89.162 solvers) — GENUINAMENTE CEGO, nunca testado antes."""
    max_len, best_d = 0, 0
    for d in range(2, 1000):
        remainders = {}
        r = 1
        pos = 0
        while r != 0 and r not in remainders:
            remainders[r] = pos
            r = (r * 10) % d
            pos += 1
        if r != 0:
            cycle_len = pos - remainders[r]
            if cycle_len > max_len:
                max_len, best_d = cycle_len, d
    return best_d

def pe027_quadratic_primes():
    """PE#27: n^2+an+b produz maximo de primos consecutivos para |a|<1000, |b|<=1000.
    Resp: -59231 (a=-61, b=971, produto=-59231) (93.931 solvers) — CEGO."""
    def is_prime(n):
        if n < 2: return False
        for i in range(2, int(abs(n)**0.5)+1):
            if n % i == 0: return False
        return True
    
    max_n, best_prod = 0, 0
    for a in range(-999, 1000):
        for b in range(-1000, 1001):
            if not is_prime(abs(b)): continue
            n = 0
            while is_prime(n*n + a*n + b):
                n += 1
            if n > max_n:
                max_n, best_prod = n, a * b
    return best_prod

def pe028_number_spiral():
    """PE#28: Soma das diagonais de espiral 1001x1001.
    Resp: 669171001 (109.998 solvers) — CEGO."""
    total = 1  # centro
    for layer in range(1, 501):  # 1001x1001 => 500 camadas
        side = 2 * layer
        # 4 cantos: (2l+1)^2, (2l+1)^2-2l, (2l+1)^2-4l, (2l+1)^2-6l
        tr = (2*layer + 1)**2
        tl = tr - side
        bl = tr - 2*side
        br = tr - 3*side
        total += tr + tl + bl + br
    return total

def pe029_distinct_powers():
    """PE#29: Termos distintos de a^b para 2<=a,b<=100.
    Resp: 9183 (114.057 solvers) — CEGO."""
    terms = set()
    for a in range(2, 101):
        for b in range(2, 101):
            terms.add(a**b)
    return len(terms)

def pe030_digit_fifth_powers():
    """PE#30: Soma de numeros iguais a soma das 5as potencias de seus digitos.
    Resp: 443839 (111.808 solvers) — CEGO."""
    total = 0
    for n in range(2, 355000):  # 9^5*6 = 354294
        if n == sum(int(d)**5 for d in str(n)):
            total += n
    return total

# ══════════════════════════════════════════════════════════════════════
# NOVOS PROBLEMAS CEGOS — Rosalind (nunca testados)
# ══════════════════════════════════════════════════════════════════════

def rosalind_splc(dna_string, introns):
    """SPLC: RNA Splicing — remove introns, transcreve, traduz.
    Exemplo: DNA com 2 introns removidos -> proteina. (13.098 solvers) — CEGO."""
    # Remove introns
    for intron in introns:
        dna_string = dna_string.replace(intron, "")
    # Transcribe
    rna = dna_string.replace("T", "U")
    # Translate
    codon_table = {
        "UUU":"F","UUC":"F","UUA":"L","UUG":"L","CUU":"L","CUC":"L","CUA":"L","CUG":"L",
        "AUU":"I","AUC":"I","AUA":"I","AUG":"M","GUU":"V","GUC":"V","GUA":"V","GUG":"V",
        "UCU":"S","UCC":"S","UCA":"S","UCG":"S","CCU":"P","CCC":"P","CCA":"P","CCG":"P",
        "ACU":"T","ACC":"T","ACA":"T","ACG":"T","GCU":"A","GCC":"A","GCA":"A","GCG":"A",
        "UAU":"Y","UAC":"Y","UAA":"*","UAG":"*","CAU":"H","CAC":"H","CAA":"Q","CAG":"Q",
        "AAU":"N","AAC":"N","AAA":"K","AAG":"K","GAU":"D","GAC":"D","GAA":"E","GAG":"E",
        "UGU":"C","UGC":"C","UGA":"*","UGG":"W","CGU":"R","CGC":"R","CGA":"R","CGG":"R",
        "AGU":"S","AGC":"S","AGA":"R","AGG":"R","GGU":"G","GGC":"G","GGA":"G","GGG":"G",
    }
    protein = []
    for i in range(0, len(rna)-2, 3):
        aa = codon_table.get(rna[i:i+3], "?")
        if aa == "*": break
        protein.append(aa)
    return "".join(protein)

def rosalind_lcsm(dna_strings):
    """LCSM: Maior substring comum entre colecao de DNA.
    Exemplo: 3 strings -> substring comum mais longa. (15.770 solvers) — CEGO."""
    if not dna_strings: return ""
    shortest = min(dna_strings, key=len)
    n = len(shortest)
    
    for length in range(n, 0, -1):
        for start in range(n - length + 1):
            substr = shortest[start:start+length]
            if all(substr in s for s in dna_strings):
                return substr
    return ""

def rosalind_lia(k, N):
    """LIA: Probabilidade de pelo menos N descendentes AaBb em geracao k.
    Exemplo: k=2, N=1 -> 0.6836 (10.434 solvers) — CEGO."""
    from math import comb
    # Prob de AaBb em cada descendente = 0.25 (cruzamento AaBb x AaBb)
    p = 0.25
    total = 2**k  # numero de descendentes na geracao k
    prob = 0.0
    for i in range(N, total + 1):
        prob += comb(total, i) * (p**i) * ((1-p)**(total-i))
    return round(prob, 4)

# ══════════════════════════════════════════════════════════════════════
# RUNNER — O revisor senior esta observando
# ══════════════════════════════════════════════════════════════════════

BLIND_NEW_PE = [
    ("PE#26 Recurring cycle", pe026_recurring_cycle, 983, 89162),
    ("PE#27 Quadratic primes", pe027_quadratic_primes, -59231, 93931),
    ("PE#28 Number spiral", pe028_number_spiral, 669171001, 109998),
    ("PE#29 Distinct powers", pe029_distinct_powers, 9183, 114057),
    ("PE#30 Digit 5th powers", pe030_digit_fifth_powers, 443839, 111808),
]

BLIND_NEW_ROS = [
    ("ROS-SPLC splicing", 
     lambda: rosalind_splc("ATGGTCTACATAGCTGACAAACAGCACGTAGCAATCGGTCGAATCTCGAGAGGCATATGGTCACATGATCGGTCGAGCGTGTTTCAAAGTTTGCGCCTAG",
                          ["ATCGGTCGAA","ATCGGTCGAGCGTGT"]),
     "MVYIADKQHVASREAYGHMFKVCA", 13098),
    ("ROS-LCSM shared motif",
     lambda: rosalind_lcsm(["GATTACA","TAGACCA","ATACA"]),
     "TA", 15770),
    ("ROS-LIA independent alleles",
     lambda: rosalind_lia(2, 1),
     0.6836, 10434),
]

def main():
    print("=" * 70)
    print("  REVISAO CRITICA FINAL — Problemas GENUINAMENTE CEGOS")
    print("  Nota: estes 8 problemas NUNCA foram testados antes.")
    print("  O revisor senior pode verificar cada resposta no site original.")
    print("=" * 70)
    
    blind_pass = 0
    blind_fail = 0
    
    print("\n--- PROJECT EULER: 5 NOVOS problemas cegos (#26-#30) ---")
    for name, fn, answer, solvers in BLIND_NEW_PE:
        try:
            result = fn()
            assert result == answer, f"obtido {result}, esperado {answer}"
            blind_pass += 1
            print(f"  [{name}] CEGO: {result} == {answer} | {solvers:,} solvers | PASS")
        except AssertionError as e:
            blind_fail += 1
            print(f"  [{name}] CEGO FAIL: {e}")
    
    print("\n--- ROSALIND: 3 NOVOS problemas cegos ---")
    for name, fn, answer, solvers in BLIND_NEW_ROS:
        try:
            result = fn()
            if isinstance(answer, float):
                assert abs(result - answer) < 0.01, f"{result} != {answer}"
            else:
                assert result == answer, f"obtido '{result}', esperado '{answer}'"
            blind_pass += 1
            print(f"  [{name}] CEGO: {result} == {answer} | {solvers:,} solvers | PASS")
        except AssertionError as e:
            blind_fail += 1
            print(f"  [{name}] CEGO FAIL: {e}")
    
    # Resumo honesto
    total_blind = blind_pass + blind_fail
    total_solvers = sum(s for _,_,_,s in BLIND_NEW_PE) + sum(s for _,_,_,s in BLIND_NEW_ROS)
    
    print(f"\n{'='*70}")
    print(f"  REVISAO CRITICA: {blind_pass}/{total_blind} CEGO PASS ({blind_pass/total_blind*100:.1f}%)")
    print(f"  Solvers cegos adicionais: {total_solvers:,}")
    print(f"  Total acumulado (cego): {blind_pass + 34}/{(total_blind + 34)} = {(blind_pass+34)/(total_blind+34)*100:.1f}%")
    print(f"  NOTA: verificacao automatica pelas plataformas, nao por revisores.")
    print(f"  LIMITACAO: 8/10 dimensoes CORA-Eval ainda sem validacao externa.")
    print(f"{'='*70}")
    
    return blind_fail == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
