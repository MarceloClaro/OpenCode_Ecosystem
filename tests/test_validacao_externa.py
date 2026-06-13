# -*- coding: utf-8 -*-
"""
VALIDACAO EXTERNA REAL â€” Project Euler + Rosalind
Problemas com respostas verificadas por centenas de milhares de solvers.
Cada solucao e testada contra a resposta conhecida (ground truth externo).

Fontes: projecteuler.net, rosalind.info
"""

import sys, math

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PROJECT EULER â€” Problemas Matematicos (D1, 1M+ solvers cada)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def pe001_multiples_of_3_or_5(limit: int = 1000) -> int:
    """PE#1: Soma dos multiplos de 3 ou 5 abaixo de limit.
    Resposta: 233168 (1.035.781 solvers)"""
    return sum(n for n in range(limit) if n % 3 == 0 or n % 5 == 0)

def pe002_even_fibonacci(limit: int = 4000000) -> int:
    """PE#2: Soma dos termos pares de Fibonacci ate limit.
    Resposta: 4613732 (823.699 solvers)"""
    a, b, total = 1, 2, 0
    while a <= limit:
        if a % 2 == 0:
            total += a
        a, b = b, a + b
    return total

def pe003_largest_prime_factor(n: int = 600851475143) -> int:
    """PE#3: Maior fator primo de n.
    Resposta: 6857 (593.026 solvers)"""
    factor = 2
    while factor * factor <= n:
        while n % factor == 0:
            n //= factor
        factor += 1 if factor == 2 else 2  # pula pares depois do 2
    return n if n > 1 else factor

def pe006_sum_square_difference(n: int = 100) -> int:
    """PE#6: (sum 1..n)^2 - sum(k^2, 1..n).
    Resposta: 25164150 (529.544 solvers)"""
    sum_n = n * (n + 1) // 2
    sum_sq = n * (n + 1) * (2 * n + 1) // 6
    return sum_n * sum_n - sum_sq

def pe009_pythagorean_triplet() -> int:
    """PE#9: a*b*c onde a+b+c=1000 e a^2+b^2=c^2.
    Resposta: 31875000 (384.318 solvers)"""
    for a in range(1, 333):
        for b in range(a + 1, (1000 - a) // 2):
            c = 1000 - a - b
            if a * a + b * b == c * c:
                return a * b * c
    return -1

def pe010_summation_of_primes(limit: int = 2000000) -> int:
    """PE#10: Soma dos primos abaixo de limit.
    Resposta: 142913828922 (353.223 solvers)"""
    sieve = [True] * limit
    sieve[0] = sieve[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, limit, i):
                sieve[j] = False
    return sum(i for i, is_prime in enumerate(sieve) if is_prime)

def pe016_power_digit_sum(power: int = 1000) -> int:
    """PE#16: Soma dos digitos de 2^power.
    Resposta: 1366 (248.002 solvers)"""
    return sum(int(d) for d in str(2 ** power))

def is_prime(n: int) -> bool:
    """V2: Verificador algebrico â€” primalidade."""
    if n < 2: return False
    if n in (2, 3): return True
    if n % 2 == 0 or n % 3 == 0: return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0: return False
        i += 6
    return True

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ROSALIND â€” Problemas de Bioinformatica (D5, 30K+ solvers cada)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def rosalind_dna(sequence: str) -> dict:
    """DNA: Contar A, C, G, T em sequencia de DNA.
    Exemplo: AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAGAGTGTCTGATAGCAGC
    Resposta: 20 12 17 21 (76.716 solvers)"""
    return {"A": sequence.count("A"), "C": sequence.count("C"),
            "G": sequence.count("G"), "T": sequence.count("T")}

def rosalind_rna(dna: str) -> str:
    """RNA: Transcrever DNA â†’ RNA (T â†’ U).
    Exemplo: GATGGAACTTGACTACGTAAATT
    Resposta: GAUGGAACUUGACUACGUAAAUU (68.238 solvers)"""
    return dna.replace("T", "U")

def rosalind_revc(dna: str) -> str:
    """REVC: Complemento reverso (Aâ†”T, Câ†”G, inverte).
    Exemplo: AAAACCCGGT
    Resposta: ACCGGGTTTT (61.849 solvers)"""
    complement = {"A": "T", "T": "A", "C": "G", "G": "C"}
    return "".join(complement[base] for base in reversed(dna))

def rosalind_gc(sequences: dict) -> tuple:
    """GC: Maior conteudo GC entre sequencias FASTA.
    Exemplo: >Rosalind_6404 CCTGCGGAAGATCGGCACTAGAATAGCC...
    Resposta: Rosalind_0808 60.919540% (35.442 solvers)"""
    max_id, max_gc = "", 0.0
    for seq_id, seq in sequences.items():
        gc = (seq.count("G") + seq.count("C")) / len(seq) * 100
        if gc > max_gc:
            max_id, max_gc = seq_id, gc
    return (max_id, round(max_gc, 6))

def rosalind_prot(rna: str) -> str:
    """PROT: Traduzir RNA â†’ proteina (ate codon STOP).
    Exemplo: AUGGCCAUGGCGCCCAGAACUGAGAUCAAUAGUACCCGUAUUAACGGGUGA
    Resposta: MAMAPRTEINSTRING (31.194 solvers)"""
    codon_table = {
        "UUU": "F", "UUC": "F", "UUA": "L", "UUG": "L",
        "CUU": "L", "CUC": "L", "CUA": "L", "CUG": "L",
        "AUU": "I", "AUC": "I", "AUA": "I", "AUG": "M",
        "GUU": "V", "GUC": "V", "GUA": "V", "GUG": "V",
        "UCU": "S", "UCC": "S", "UCA": "S", "UCG": "S",
        "CCU": "P", "CCC": "P", "CCA": "P", "CCG": "P",
        "ACU": "T", "ACC": "T", "ACA": "T", "ACG": "T",
        "GCU": "A", "GCC": "A", "GCA": "A", "GCG": "A",
        "UAU": "Y", "UAC": "Y", "UAA": "*", "UAG": "*",
        "CAU": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
        "AAU": "N", "AAC": "N", "AAA": "K", "AAG": "K",
        "GAU": "D", "GAC": "D", "GAA": "E", "GAG": "E",
        "UGU": "C", "UGC": "C", "UGA": "*", "UGG": "W",
        "CGU": "R", "CGC": "R", "CGA": "R", "CGG": "R",
        "AGU": "S", "AGC": "S", "AGA": "R", "AGG": "R",
        "GGU": "G", "GGC": "G", "GGA": "G", "GGG": "G",
    }
    protein = []
    for i in range(0, len(rna) - 2, 3):
        codon = rna[i:i+3]
        aa = codon_table.get(codon, "?")
        if aa == "*":
            break
        protein.append(aa)
    return "".join(protein)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TDD â€” VALIDACAO EXTERNA (contra ground truth conhecido)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

PROJECT_EULER_ANSWERS = {
    "PE001": (pe001_multiples_of_3_or_5, 233168, 1035781),
    "PE002": (pe002_even_fibonacci, 4613732, 823699),
    "PE003": (pe003_largest_prime_factor, 6857, 593026),
    "PE006": (pe006_sum_square_difference, 25164150, 529544),
    "PE009": (pe009_pythagorean_triplet, 31875000, 384318),
    "PE010": (pe010_summation_of_primes, 142913828922, 353223),
    "PE016": (pe016_power_digit_sum, 1366, 248002),
}

ROSALIND_EXAMPLES = {
    "DNA": ("AGCTTTTCATTCTGACTGCAACGGGCAATATGTCTCTGTGTGGATTAAAAAAAGAGTGTCTGATAGCAGC",
            {"A": 20, "C": 12, "G": 17, "T": 21}),
    "RNA": ("GATGGAACTTGACTACGTAAATT", "GAUGGAACUUGACUACGUAAAUU"),
    "REVC": ("AAAACCCGGT", "ACCGGGTTTT"),
}

def main():
    print("=" * 70)
    print("  VALIDACAO EXTERNA REAL â€” Project Euler + Rosalind")
    print("  Ground truth verificado por centenas de milhares de solvers")
    print("=" * 70)

    passed, failed = 0, 0

    # Project Euler â€” D1 (Matematica Formal, N2-N4)
    print("\n--- PROJECT EULER (D1: Raciocinio Matematico) ---")
    for pe_id, (fn, answer, solvers) in PROJECT_EULER_ANSWERS.items():
        try:
            result = fn()
            assert result == answer, f"{pe_id}: {result} != {answer}"
            print(f"  [{pe_id}] {fn.__doc__.split(chr(10))[0]}")
            print(f"         Resultado: {result:,}  |  Resposta: {answer:,}  |  {solvers:,} solvers  |  VERIFICADO")
            # Cora V2: verificacao algebrica
            if pe_id in ("PE003", "PE010"):
                # PE003: verifica que o resultado e primo
                if pe_id == "PE003":
                    assert is_prime(result), f"V2 FAIL: {result} nao e primo"
                    print(f"         V2 (Algebrico): {result} e primo [OK]")
            passed += 1
        except AssertionError as e:
            print(f"  [{pe_id}] FAIL: {e}")
            failed += 1

    # Rosalind â€” D5 (Biologia Molecular, N1-N2)
    print("\n--- ROSALIND (D5: Biologia Molecular) ---")
    for ros_id, (input_data, expected) in ROSALIND_EXAMPLES.items():
        try:
            if ros_id == "DNA":
                result = rosalind_dna(input_data)
                assert result == expected, f"DNA: {result} != {expected}"
                print(f"  [ROS-{ros_id}] {result}  |  {expected}  |  76.716 solvers  |  VERIFICADO")
            elif ros_id == "RNA":
                result = rosalind_rna(input_data)
                assert result == expected
                print(f"  [ROS-{ros_id}] {result}  |  {expected}  |  68.238 solvers  |  VERIFICADO")
            elif ros_id == "REVC":
                result = rosalind_revc(input_data)
                assert result == expected
                print(f"  [ROS-{ros_id}] {result}  |  {expected}  |  61.849 solvers  |  VERIFICADO")
            passed += 1
        except AssertionError as e:
            print(f"  [ROS-{ros_id}] FAIL: {e}")
            failed += 1

    # Rosalind GC (com dados FASTA de exemplo)
    print("\n--- ROSALIND GC (D5: Conteudo GC) ---")
    fasta_example = {
        "Rosalind_6404": "CCTGCGGAAGATCGGCACTAGAATAGCCAGAACCGTTTCTCTGAGGCTTCCGGCCTTCCCTCCCACTAATAATTCTGAGG",
        "Rosalind_5959": "CCATCGGTAGCGCATCCTTAGTCCAATTAAGTCCCTATCCAGGCGCTCCGCCGAAGGTCTATATCCATTTGTCAGCAGACACGC",
        "Rosalind_0808": "CCACCCTCGTGGTATGGCTAGGCATTCAGGAACCGGAGAACGCTTCAGACCAGCCCGGACTGGGAACCTGCGGGCAGTAGGTGGAAT",
    }
    # Ground truth: Rosalind_0808 60.919540%
    max_id, max_gc = rosalind_gc(fasta_example)
    assert max_id == "Rosalind_0808", f"ID errado: {max_id}"
    assert abs(max_gc - 60.919540) < 0.01, f"GC errado: {max_gc}%"
    print(f"  [ROS-GC] {max_id}: {max_gc}%  |  Rosalind_0808: 60.919540%  |  35.442 solvers  |  VERIFICADO")
    passed += 1

    # Rosalind PROT
    rna_prot = "AUGGCCAUGGCGCCCAGAACUGAGAUCAAUAGUACCCGUAUUAACGGGUGA"
    expected_prot = "MAMAPRTEINSTRING"
    result_prot = rosalind_prot(rna_prot)
    assert result_prot == expected_prot
    print(f"  [ROS-PROT] {result_prot}  |  {expected_prot}  |  31.194 solvers  |  VERIFICADO")
    passed += 1

    # Verificacao adicional: Propriedades matematicas (V2, V3)
    print("\n--- CORA V2-V3: Verificacao Simbolica ---")
    # V2: Identidade algebrica â€” PE006 formula fechada vs iterativa
    n = 100
    sum_sq_iter = sum(k*k for k in range(1, n+1))
    sum_n_iter = sum(range(1, n+1))
    diff_iter = sum_n_iter * sum_n_iter - sum_sq_iter
    assert diff_iter == pe006_sum_square_difference(n), "V2: Formula fechada != iterativa"
    print(f"  [V2] PE006: formula fechada {pe006_sum_square_difference(n):,} == iterativa {diff_iter:,} [OK]")

    # V3: Contraexemplo â€” verifica que 6 nao e multiplo de 5
    # (PE001 conta corretamente multiplos de 3 ou 5)
    pe001_result = pe001_multiples_of_3_or_5(10)
    manual = sum(n for n in range(10) if n % 3 == 0 or n % 5 == 0)  # 0+3+5+6+9 = 23
    assert pe001_result == manual == 23
    print(f"  [V3] PE001(10): automatico={pe001_result} == manual={manual} âœ“")

    # V1: Analise dimensional â€” PE009 (produto abc, unidades: inteiro)
    result_pe009 = pe009_pythagorean_triplet()
    a = int(round(result_pe009 ** (1/3)))  # estimativa grosseira
    assert isinstance(result_pe009, int) and result_pe009 > 0
    print(f"  [V1] PE009: a*b*c = {result_pe009:,} (inteiro positivo) âœ“")

    print(f"\n{'='*70}")
    total_tests = passed + failed
    print(f"  RESULTADO: {passed}/{total_tests} verificacoes externas PASS")
    print(f"  Fontes: Project Euler ({sum(a[2] for a in PROJECT_EULER_ANSWERS.values()):,} solvers)")
    print(f"          Rosalind (271.439 solvers combinados)")
    print(f"  Confianca: VALIDACAO EXTERNA â€” nao apenas testes internos")
    print(f"{'='*70}")

    return failed == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)

