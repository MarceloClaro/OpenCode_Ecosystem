---
name: spec-012-d3-estatistica
description: "Suite TDD para D3 (Raciocinio Estatistico) do CORA-Eval. 9 testes em niveis N2-N3: Teste t (2), ANOVA, Regressao Linear, Correlacao de Pearson, Bootstrap, MCMC, PCA, Correcao Multiplas Comparacoes. 11 funcoes implementadas. Validacao via TDD com dados sinteticos seed 42."
spec: "SPEC-012"
version: "1.1"
category: research
tags: [cora-eval, d3, estatistica, tdd, validacao]
dependencies: [SPEC-001, CORA-Eval]
tdd_suite: "artigo/evaluations/tests/test_d3_estatistica.py"
ct_count: 9
status: active
---

# SPEC-012 — Suite D3: Raciocínio Estatístico

## Objetivo
Validar a capacidade de raciocínio estatístico formal (D3 do CORA-Eval)
via 9 testes automatizados com dados sintéticos (seed 42),
abrangendo níveis N2 (Métodos Clássicos) e N3 (Métodos Avançados).

> ⚠️ **Nota de Auditoria (2026-05-31):** O SKILL.md original listava 10 CTs e 18 funções,
> mas o código real contém **9 testes** e **11 funções**. Os CTs D3-N3-03 (Inferência Bayesiana)
> e D3-N3-05 (Regressão Gaussiana GP) não estão implementados. As funções `shapiro_wilk`,
> `kde`, `metropolis_hastings`, `pca_explained_variance`, `bayesian_update`,
> `spectral_clustering` e `gaussian_process_regression` estão listadas mas não existem
> no código (os testes implementam a lógica inline). Esta versão 1.1 corrige o registro
> para refletir fielmente o código real.

## CTs (Testes Reais)

| CT | Descrição | Nível | Funções Cobertas |
|:--:|-----------|:-----:|-----------------|
| D3-N2-01a | Teste t — amostras da mesma população: \|t\| pequeno (p > 0.05) | N2 | `t_statistic` |
| D3-N2-01b | Teste t — amostras diferentes: \|t\| grande, Cohen's d grande | N2 | `t_statistic`, `cohens_d` |
| D3-N2-02 | ANOVA one-way — F grande entre 3 grupos com médias diferentes | N2 | `mean`, `variance` |
| D3-N2-03 | Regressão linear — y = 2 + 3x + ruído: recupera b₀, b₁, R² > 0.95 | N2 | `linear_regression`, `r_squared`, `mean` |
| D3-N2-04a | Correlação de Pearson — r ≈ 1 (correlacionado), r ≈ 0 (independente) | N2 | `pearson_r` |
| D3-N2-04b | Bootstrap IC 95% — IC bootstrap contém média populacional | N2 | `mean` |
| D3-N3-01 | MCMC Metropolis-Hastings — amostragem N(0,1): média ≈ 0, std ≈ 1 | N3 | `mean`, `std` (inline MCMC) |
| D3-N3-02 | PCA — variância explicada: PC1 > 70% em dados 2D correlacionados | N3 | `mean` (inline autovalores) |
| D3-N3-04 | Correção MCP — Bonferroni (sem falsos positivos) + BH (FDR controlado) | N3 | `bonferroni_correction`, `benjamini_hochberg` |

## Funções Implementadas (11)

| Função | Descrição | Testada em |
|--------|-----------|:----------:|
| `mean(x)` | Média aritmética | Todos |
| `variance(x, ddof=1)` | Variância amostral | D3-N2-01, D3-N2-02 |
| `std(x, ddof=1)` | Desvio padrão amostral | D3-N3-01 |
| `t_statistic(x, y)` | Estatística t de Welch (variâncias desiguais) | D3-N2-01a, D3-N2-01b |
| `welch_df(x, y)` | Graus de liberdade de Welch-Satterthwaite | (definida mas não testada explicitamente) |
| `cohens_d(x, y)` | Tamanho de efeito de Cohen (d) | D3-N2-01b |
| `pearson_r(x, y)` | Coeficiente de correlação de Pearson | D3-N2-04a |
| `r_squared(y_true, y_pred)` | Coeficiente de determinação R² | D3-N2-03 |
| `linear_regression(x, y)` | Regressão linear simples: retorna (b₀, b₁) | D3-N2-03 |
| `bonferroni_correction(p_values)` | Correção de Bonferroni: p_adj = min(1, p × n) | D3-N3-04 |
| `benjamini_hochberg(p_values, alpha=0.05)` | FDR control via Benjamini-Hochberg | D3-N3-04 |

## CTs Pendentes (Não Implementados)

| CT | Descrição | Prioridade |
|:--:|-----------|:----------:|
| D3-N3-03 | Inferência Bayesiana — atualização de prior com likelihood normal | Média |
| D3-N3-05 | Regressão Gaussiana (GP) — predição com kernel RBF e incerteza calibrada | Baixa |

## Execução
```bash
python artigo/evaluations/tests/test_d3_estatistica.py
```

## Integração CORA-Eval
D3 cobre métodos estatísticos clássicos (N2) e computacionais (N3) com dados
sintéticos reproduzíveis via seed 42. Preenche a lacuna de validação
estatística do CORA-Eval.
