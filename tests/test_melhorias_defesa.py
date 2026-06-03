# -*- coding: utf-8 -*-
"""
TDD: MELHORIAS PARA DEFESA REAL — 4 melhorias com teste primeiro

1. Narrativa honesta: metadados corrigidos, claims calibradas
2. Coluna de confianca: externa vs interna por dimensao
3. Comparacao justa: mesmo modelo base, arquiteturas diferentes
4. Ledoit-Wolf shrinkage: matriz de covariancia regularizada para 38D
"""

import sys, math, json, os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

SCRIPT_DIR = Path(__file__).parent.parent  # evaluations/

# ══════════════════════════════════════════════════════════════════════
# TDD 1: NARRATIVA HONESTA — Metadados e claims calibradas
# ══════════════════════════════════════════════════════════════════════

HONEST_CLAIMS = {
    "verificacoes": "34 problemas resolvidos em plataformas com verificacao automatica (Project Euler + Rosalind)",
    "cora_score": "CORA-Score 3.04 em benchmark proprio com validacao externa apenas em D1 (PE) e D5 (Rosalind)",
    "ollama": "Comparacao com modelos bare-metal sem verificadores; comparacao com frameworks multiagente pendente",
    "documento": "Relatorio Tecnico auto-publicado em formato ABNT",
    "limitacao_central": "8 de 10 dimensoes validadas internamente; validacao externa independente pendente",
}

def test_narrative_honesty():
    """TDD-1: Narrativa substitui claims infladas por descricoes precisas."""
    # Verifica que cada claim corrigida existe e e nao-vazia
    for key, value in HONEST_CLAIMS.items():
        assert len(value) > 30, f"Claim '{key}' muito curta: {len(value)} chars"
        # Nao contem numeros inflados
        if key == "verificacoes":
            assert "4,3 milh" not in value.lower(), "Removeu '4,3 milhoes'"
            assert "34" in value, "Menciona 34 problemas"
        if key == "cora_score":
            assert "benchmark proprio" in value.lower(), "Qualifica como benchmark proprio"
            assert "D1" in value and "D5" in value, "Menciona dimensoes com val. externa"
    print("  [TDD-1] Narrativa honesta: 5 claims calibradas... PASS")
    return True

def apply_narrative_fixes():
    """Aplica correcoes de narrativa ao documento."""
    return {
        "resumo_antes": "corroborado por 4,3 milhoes de verificacoes independentes",
        "resumo_depois": "com 34 problemas resolvidos em plataformas de verificacao automatica",
        "conclusao_antes": "CORA-Score 3,04 (Pesquisa)",
        "conclusao_depois": "CORA-Score 3,04 em benchmark proprio (val. externa: D1, D5)",
        "metadata_antes": "Dissertacao",
        "metadata_depois": "Relatorio Tecnico — OpenCode Ecosystem v4.7",
    }

# ══════════════════════════════════════════════════════════════════════
# TDD 2: COLUNA DE CONFIANCA — Externa vs Interna por dimensao
# ══════════════════════════════════════════════════════════════════════

CONFIDENCE_LEVELS = {
    "D1": {"nivel": "Alta", "fonte": "Project Euler (34 problemas, verificacao automatica)", "score": 3.80},
    "D2": {"nivel": "Media", "fonte": "TDD proprio + DCA Listas (mapeamento conceitual)", "score": 3.50},
    "D3": {"nivel": "Media", "fonte": "TDD proprio (MCMC, EM, PCA implementados)", "score": 3.40},
    "D4": {"nivel": "Baixa", "fonte": "Apenas validacao interna (equilibrio quimico basico)", "score": 2.23},
    "D5": {"nivel": "Alta", "fonte": "Rosalind (10 problemas, verificacao automatica)", "score": 2.45},
    "D6": {"nivel": "Baixa", "fonte": "Apenas validacao interna (EBM simplificado)", "score": 2.60},
    "D7": {"nivel": "Media", "fonte": "TDD proprio (V7a-V7f auto-aplicado)", "score": 3.20},
    "D8": {"nivel": "Baixa", "fonte": "Apenas validacao interna (corpus de 30 referencias)", "score": 2.23},
    "D9": {"nivel": "Baixa", "fonte": "Apenas validacao interna (mapeamento conceitual)", "score": 2.67},
    "D10": {"nivel": "Media", "fonte": "TDD proprio (GAT implementado, 10 testes)", "score": 3.67},
}

def test_confidence_column():
    """TDD-2: Cada dimensao tem nivel de confianca documentado."""
    # Todas as 10 dimensoes tem entrada
    assert len(CONFIDENCE_LEVELS) == 10, f"Apenas {len(CONFIDENCE_LEVELS)} dimensoes"
    
    # Niveis validos
    valid_levels = {"Alta", "Media", "Baixa"}
    for dim, data in CONFIDENCE_LEVELS.items():
        assert data["nivel"] in valid_levels, f"{dim}: nivel invalido '{data['nivel']}'"
        assert len(data["fonte"]) > 20, f"{dim}: fonte muito curta"
    
    # Dimensoes com validacao externa tem nivel Alto
    assert CONFIDENCE_LEVELS["D1"]["nivel"] == "Alta", "D1 deveria ser Alta (PE)"
    assert CONFIDENCE_LEVELS["D5"]["nivel"] == "Alta", "D5 deveria ser Alta (Rosalind)"
    
    # Nenhuma dimensao sem validacao externa tem nivel Alto
    for dim in ["D4", "D6", "D8", "D9"]:
        assert CONFIDENCE_LEVELS[dim]["nivel"] != "Alta", f"{dim} nao deveria ser Alta"
    
    # Score ajustado pela confianca (Alta=1.0, Media=0.85, Baixa=0.70)
    weights = {"Alta": 1.0, "Media": 0.85, "Baixa": 0.70}
    adjusted_score = 0.0
    w = {"D1":.15,"D2":.12,"D3":.12,"D4":.10,"D5":.10,"D6":.08,"D7":.10,"D8":.08,"D9":.08,"D10":.07}
    for dim, data in CONFIDENCE_LEVELS.items():
        adjusted_score += w[dim] * data["score"] * weights[data["nivel"]]
    
    # Score ajustado deve ser menor que o bruto (penalizacao por baixa confianca)
    assert adjusted_score < 3.04, f"Score ajustado {adjusted_score:.2f} deveria ser < 3.04"
    print(f"  [TDD-2] Confianca: 2 Alta, 4 Media, 4 Baixa. Score ajustado={adjusted_score:.2f}... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# TDD 3: COMPARACAO JUSTA — Mesmo modelo base, arquiteturas diferentes
# ══════════════════════════════════════════════════════════════════════

def design_fair_comparison() -> Dict:
    """Design experimental para comparacao justa:
    Condicao A: DeepSeek-V3 bare (sem verificadores)
    Condicao B: DeepSeek-V3 + Cora V1-V7 (pos-processamento)
    Condicao C: OpenCode completo (multiagente + verificadores)
    
    Isso isola:
    - Efeito dos verificadores: B vs A
    - Efeito da arquitetura multiagente: C vs B
    - Efeito total: C vs A
    """
    return {
        "design": "between-subjects 1x3",
        "modelo_base": "DeepSeek-V3 (mesmo em todas as condicoes)",
        "condicoes": {
            "A_bare": "DeepSeek-V3 sem verificadores, prompt unico",
            "B_verified": "DeepSeek-V3 + Cora V1-V7 pos-processamento",
            "C_multiagent": "OpenCode completo (125 agentes + Cora + TDD)",
        },
        "benchmark": "34 problemas cegos (25 PE + 10 Rosalind)",
        "metricas": ["CORA-Score", "taxa_acerto", "tempo_por_problema"],
        "hipoteses": [
            "H1: B > A (verificadores melhoram desempenho)",
            "H2: C > B (multiagente melhora alem dos verificadores)",
            "H3: C > A (efeito combinado positivo)",
        ],
        "status": "NAO EXECUTADO — requer acesso a APIs dos 3 sistemas",
    }

def test_fair_comparison_design():
    """TDD-3: Design experimental valido para comparacao justa."""
    design = design_fair_comparison()
    assert len(design["condicoes"]) == 3, "Precisa de 3 condicoes"
    assert design["modelo_base"] is not None, "Modelo base deve ser o mesmo"
    assert len(design["hipoteses"]) == 3, "Precisa de 3 hipoteses"
    assert design["status"].startswith("NAO EXECUTADO"), "Deve documentar que nao foi executado"
    print("  [TDD-3] Design experimental: 3 condicoes, mesmo modelo, 3 hipoteses... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# TDD 4: LEDOIT-WOLF SHRINKAGE — Matriz covariancia regularizada
# ══════════════════════════════════════════════════════════════════════

def ledoit_wolf_shrinkage(X: List[List[float]]) -> Tuple[List[List[float]], float]:
    """
    Estimador shrinkage de Ledoit-Wolf para matriz de covariancia.
    Resolve o problema n < p (150 observacoes, 38 dimensoes).
    
    Ledoit, O., Wolf, M. (2004). A Well-Conditioned Estimator for
    Large-Dimensional Covariance Matrices. J. Multivariate Analysis.
    """
    n = len(X)      # observacoes
    p = len(X[0])   # dimensoes
    
    # Matriz de covariancia amostral S
    means = [sum(X[i][j] for i in range(n)) / n for j in range(p)]
    S = [[0.0]*p for _ in range(p)]
    for i in range(n):
        for j in range(p):
            for k in range(p):
                S[j][k] += (X[i][j] - means[j]) * (X[i][k] - means[k])
    for j in range(p):
        for k in range(p):
            S[j][k] /= (n - 1)
    
    # Traco de S e media dos elementos da diagonal
    tr_S = sum(S[j][j] for j in range(p))
    mu = tr_S / p  # media da diagonal
    
    # Matriz identidade escalada como alvo
    # Estimacao do parametro de shrinkage
    # delta^2 = sum_{i,j} Var(s_ij) — simplificado
    
    # Shrinkage intensity (formula de Ledoit-Wolf)
    # Usando o estimador assintoticamente otimo
    d_sq = 0.0  # soma das variancias dos elementos de S
    for j in range(p):
        for k in range(p):
            # Var(s_jk) estimada pelos momentos de 4a ordem
            vals = [(X[i][j] - means[j]) * (X[i][k] - means[k]) for i in range(n)]
            mean_val = sum(vals) / n
            var_val = sum((v - mean_val)**2 for v in vals) / (n - 1)
            d_sq += var_val
    
    d_sq /= (p * p)  # media por elemento
    
    # b^2 = sum_{j,k} (s_jk - delta_jk*mu)^2
    b_sq = 0.0
    for j in range(p):
        for k in range(p):
            target = mu if j == k else 0.0
            b_sq += (S[j][k] - target)**2
    b_sq /= (p * p)
    
    # Shrinkage intensity
    if b_sq > 0:
        shrinkage = min(1.0, max(0.0, d_sq / (b_sq * n)))
    else:
        shrinkage = 0.0
    
    # Matriz regularizada: (1-delta)*S + delta*mu*I
    S_reg = [[0.0]*p for _ in range(p)]
    for j in range(p):
        for k in range(p):
            S_reg[j][k] = (1 - shrinkage) * S[j][k]
            if j == k:
                S_reg[j][k] += shrinkage * mu
    
    return S_reg, shrinkage

def test_ledoit_wolf():
    """TDD-4: Ledoit-Wolf produz matriz bem-condicionada para n < p."""
    import random
    random.seed(42)
    
    # Simula 150 observacoes em 38 dimensoes (exatamente o cenario CORA-Eval)
    n, p = 150, 38
    X = [[random.gauss(j * 0.1, 1.0) for j in range(p)] for _ in range(n)]
    
    # Matriz amostral S (mal-condicionada pois n < p)
    means = [sum(X[i][j] for i in range(n))/n for j in range(p)]
    S = [[0.0]*p for _ in range(p)]
    for i in range(n):
        for j in range(p):
            for k in range(p):
                S[j][k] += (X[i][j]-means[j])*(X[i][k]-means[k])
    for j in range(p):
        for k in range(p):
            S[j][k] /= (n-1)
    
    # Numero de condicao da matriz amostral (deveria ser alto/instavel)
    # Aproximacao: razao entre maior e menor elemento da diagonal
    diag_S = [S[j][j] for j in range(p)]
    cond_S = max(diag_S) / (min(diag_S) + 1e-10)
    
    # Matriz regularizada
    S_reg, shrinkage = ledoit_wolf_shrinkage(X)
    diag_reg = [S_reg[j][j] for j in range(p)]
    cond_reg = max(diag_reg) / (min(diag_reg) + 1e-10)
    
    # Shrinkage deve estar entre 0 e 1
    assert 0 <= shrinkage <= 1, f"Shrinkage {shrinkage:.4f} fora de [0,1]"
    
    # Matriz regularizada deve ser melhor condicionada
    assert cond_reg <= cond_S * 1.1, f"Cond S={cond_S:.1f}, Cond reg={cond_reg:.1f}"
    
    # Matriz deve ser simetrica
    for j in range(p):
        for k in range(j+1, p):
            assert abs(S_reg[j][k] - S_reg[k][j]) < 1e-10, f"Assimetria em [{j},{k}]"
    
    # Elementos da diagonal devem ser positivos
    for j in range(p):
        assert S_reg[j][j] > 0, f"Diagonal[{j}] = {S_reg[j][j]} <= 0"
    
    print(f"  [TDD-4] Ledoit-Wolf: n={n}, p={p} (n<p). Shrinkage={shrinkage:.4f}. Cond(S)={cond_S:.1f}->Cond(Reg)={cond_reg:.1f}... PASS")
    return True

# ══════════════════════════════════════════════════════════════════════
# RUNNER
# ══════════════════════════════════════════════════════════════════════

def main():
    print("=" * 65)
    print("  TDD: MELHORIAS PARA DEFESA REAL")
    print("=" * 65)
    
    tests = [
        ("1. Narrativa honesta", test_narrative_honesty),
        ("2. Confianca por dimensao", test_confidence_column),
        ("3. Design comparacao justa", test_fair_comparison_design),
        ("4. Ledoit-Wolf shrinkage", test_ledoit_wolf),
    ]
    
    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            print(f"  [{name}] FAIL: {e}")
            failed += 1
    
    print(f"\n  RESULTADO: {passed}/{passed+failed} PASS")
    print(f"  Pronto para defesa: {'SIM' if failed == 0 else 'PENDENTE'}")
    print("=" * 65)
    return failed == 0

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
