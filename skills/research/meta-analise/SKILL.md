---
name: meta-analise
description: "Skill de meta-análise: síntese quantitativa de efeitos, forest plot, heterogeneidade (I²), viés de publicação (funnel plot), meta-regressão, subgrupos, PRISMA."
spec: "SPEC-079"
version: "1.0"
category: research
tags: [metodo, meta-analise, sintese-quantitativa, effect-size, forest-plot, funnel-plot, prisma, heterogeneidade]
dependencies: [SPEC-079]
tdd_suite: "tests/test_r34_meta_analise.py"
ct_count: 8
status: active
---

# SPEC-079 — Skill: Meta-análise (Síntese Quantitativa)

## Objetivo
Prover protocolos operacionais para condução de meta-análise: cálculo de effect size, modelos de efeito fixo e aleatório, heterogeneidade, viés de publicação, meta-regressão e apresentação gráfica (forest plot, funnel plot).

## CTs
| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SKILL.md existe com frontmatter | ✅ |
| CT-02 | Template: Cálculo de Effect Size (OR, RR, MD, SMD) | ✅ |
| CT-03 | Template: Forest Plot (execução e interpretação) | ✅ |
| CT-04 | Template: Heterogeneidade (I², Q de Cochrane, τ²) | ✅ |
| CT-05 | Template: Viés de Publicação (funnel plot, Egger, Trim and Fill) | ✅ |
| CT-06 | Template: Modelos de Efeito (Fixo vs. Aleatório) | ✅ |
| CT-07 | Template: Meta-regressão e Análise de Subgrupos | ✅ |
| CT-08 | Template: PRISMA 2020 Checklist | ✅ |

## Template 1: Cálculo de Effect Size

### Tipos de Effect Size
| Tipo | Medida | Uso Típico | Fórmula |
|:-----|:-------|:------------|:--------|
| Dicotômico | Odds Ratio (OR) | Caso-controle | (a/c) / (b/d) |
| Dicotômico | Risk Ratio (RR) | Coorte | a/(a+b) / c/(c+d) |
| Dicotômico | Risk Difference (RD) | EAPV | a/(a+b) - c/(c+d) |
| Contínuo | Mean Difference (MD) | Mesma escala | M₁ - M₂ |
| Contínuo | Std. Mean Difference (SMD) | Escalas diferentes | (M₁-M₂)/SD_pooled |
| Contínuo | Hedges' g | Pequenas amostras | SMD × (1 - 3/(4n-9)) |
| Tempo | Hazard Ratio (HR) | Sobrevida | log-rank O/E |

### Procedimento de Extração
1. Identificar desfecho principal de cada estudo
2. Extrair: n por grupo, média/DP (contínuo) ou tabela 2×2 (dicotômico)
3. Calcular effect size individual com IC 95%
4. Converter para escala comum (ex.: OR → logOR para normalidade)

## Template 2: Forest Plot

### Componentes do Forest Plot
```
Estudo          |   ES (IC 95%)   |  Peso (%)
----------------|-----------------|----------
Estudo 1 (2023) |  0.72 (0.45-1.15)|  15.2
Estudo 2 (2024) |  0.85 (0.62-1.16)|  22.4
Estudo 3 (2025) |  0.61 (0.38-0.98)|  12.8
Estudo 4 (2025) |  0.78 (0.55-1.10)|  18.6
Estudo 5 (2026) |  0.69 (0.48-0.99)|  16.0
----------------|-----------------|----------
Pooled (REML)   |  0.73 (0.62-0.86)| 100.0
Heterogeneidade: I² = 12.3%, τ² = 0.004, Q = 4.56 (p = 0.335)
```

### Interpretação
- ES < 1 (dicotômico): fator protetor; ES > 1: fator de risco
- IC 95% que não cruza 1 (dicotômico) ou 0 (contínuo): significativo
- I² < 25%: baixa heterogeneidade; 25-50%: moderada; > 50%: alta
- Peso: proporção de cada estudo no pooled effect

## Template 3: Heterogeneidade (I², Q de Cochrane, τ²)

### Medidas de Heterogeneidade
1. **Q de Cochrane**: χ² = Σ w_i (y_i - μ)²
   - p < 0.10: heterogeneidade significativa
   - Limitação: baixo poder com poucos estudos

2. **I²**: (Q - df) / Q × 100%
   - 0-25%: baixa (não se preocupe)
   - 25-50%: moderada (explique possíveis fontes)
   - 50-75%: substancial (investigue causas)
   - > 75%: considerável (considere não combinar)

3. **τ²** (entre-estudos)
   - REML: estimativa preferida (Harville, 1977)
   - DerSimonian-Laird: método clássico
   - Q-profile: IC para τ² (Viechtbauer, 2007)

### Árvore de Decisão de Heterogeneidade
```
I² < 25% → Efeito fixo (Mantel-Haenszel)
25% ≤ I² ≤ 50% → Efeito aleatório (REML); investigar fontes
I² > 50% → Efeito aleatório; meta-regressão; subgrupos
I² > 75% → Não combinar → Síntese narrativa (SWiM)
```

## Template 4: Viés de Publicação

### Métodos de Detecção
1. **Funnel Plot** (gráfico de funil)
   - Eixo Y: precisão (1/SE) ou tamanho amostral
   - Eixo X: effect size
   - Assimetria → viés de publicação
   - Interpretação: faltam estudos pequenos com efeito nulo/negativo

2. **Egger Test**: regressão linear de SE sobre effect size
   - p < 0.10: assimetria significativa

3. **Begg Rank Test**: correlação de Kendall entre effect size e variância
   - Menor poder que Egger, mas mais robusto

4. **Trim and Fill**: estimar quantos estudos faltam e ajustar
   - Remove (trim) estudos assimétricos
   - Estima o pooled effect ajustado
   - Adiciona (fill) estudos imputados para simetria

## Referências da Skill
- Cochrane Collaboration. (2024). Chapter 10: Meta-analyses. *Cochrane Handbook* v6.5.
- Dwivedi, A. (2026). FRAMES: Framework for Approaches and Methods in Evidence Synthesis. *PeerJ*, 14, e20897.
- Page, M.J. et al. (2021). PRISMA 2020 statement. *BMJ*, 372, n71.
- DerSimonian, R. & Laird, N. (1986). Meta-analysis in clinical trials. *Control Clin Trials*, 7(3), 177-188.
- Higgins, J.P.T. et al. (2003). Measuring inconsistency in meta-analyses. *BMJ*, 327, 557-560.
- Egger, M. et al. (1997). Bias in meta-analysis. *BMJ*, 315, 629-634.
- Borenstein, M. et al. (2021). *Introduction to Meta-Analysis* (2nd ed.). Wiley.
- Viechtbauer, W. (2010). Meta-analyses in R with metafor. *J Stat Softw*, 36(3), 1-48.
