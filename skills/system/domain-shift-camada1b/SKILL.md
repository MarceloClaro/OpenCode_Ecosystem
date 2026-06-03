---
name: domain-shift-camada1b
category: system
version: "1.0.0"
kind: python
description: >
  Deteccao de Domain Shift em corpora multi-institucionais. Distingue 'padrao real
  que evoluiu' de 'domain shift que invalida a comparacao' usando decomposicao em
  3 deltas de Jaccard (temporal, cross-inst, confundido) com limiares calibrados
  por bootstrap. Extensao da SPEC-008 Camada 1 — valida quando o corpus tem
  multiplas fontes e a composicao institucional muda ao longo do tempo. 
  Use quando: (1) corpus tem campo 'instituicao' nos metadados; (2) split temporal
  cego detecta queda de performance que pode ser domain shift em vez de overfitting;
  (3) precisa calibrar limiares de Jaccard especificos do dominio.
  NAO use quando o corpus tem fonte unica (split temporal cego basta).
version: "1.0"
spec: "SPEC-008-B"
dependencies: [SPEC-008, INTEGRIDADE.md]
category: system
tags: [validation, domain-shift, jaccard, bootstrap, multi-institutional, triangulacao]
author: "Marcelo Claro Laranjeira"
orcid: "0000-0001-8996-2887"
created: "2026-05-30"
last_updated: "2026-05-30"
status: "active"
tdd_suite: "article/evaluations/domain_shift_audit.py"
references_count: 25
---

# SPEC-008-B: Domain Shift Detection via Decomposicao Institucional

## 1. Objetivo

Detectar e quantificar domain shift em corpora multi-institucionais, distinguindo
"padrao real que evoluiu" de "mudanca de fonte que invalida a comparacao
temporal". Opera como **Camada 1B** entre o split temporal cego (Camada 1) e a
perturbacao adversaria (Camada 2) da SPEC-008.

## 2. Quando Usar

| Cenario | Usar Camada 1B? |
|---------|:---:|
| Corpus com campo `instituicao` nos metadados | ✅ Sim |
| Multiplas instituicoes no mesmo periodo | ✅ Sim |
| Nova instituicao entra apenas em T2 | ✅ Sim (critico!) |
| Corpus fonte unica, sem metadados de instituicao | ❌ Nao (split temporal basta) |
| Menos de 2 instituicoes por periodo | ❌ Nao (bootstrap degenerado) |

## 3. Pipeline

```
corpus ──▶ [C1: Split Temporal Cego] ──▶ temporal_score bruto
               │
               ▼
          [C1B: Decomposicao Institucional]
               │
               ├── Agrupar docs por (instituicao, periodo)
               ├── Extrair padroes P_{s,T}
               ├── Computar 3 deltas Jaccard:
               │     Δ_temporal(s) = J(P_{s,T1}, P_{s,T2})
               │     Δ_cross(s_a,s_b) = J(P_{s_a,T}, P_{s_b,T})  [distrib. nula]
               │     Δ_confundido(s_a,s_b) = J(P_{s_a,T1}, P_{s_b,T2})
               ├── Calibrar limiares via bootstrap (B=10000)
               ├── Classificar cada instituicao
               └── Identificar S_apenas_T1 e S_apenas_T2
               │
               ▼
          [C2: Perturbacao Adversaria] ──▶ robustness_score (por inst)
               │
               ▼
          [C3: Anotacao Humana Ativa]
               │
               ▼
          Relatorio de Transparencia (com secao Camada 1B)
```

## 4. Regra de Decisao

| Condicao | Diagnostico | Acao |
|----------|-------------|------|
| Δ_t > P99_null | Evidencia FORTE | Publicar com confianca (Cenario A) |
| Δ_t > P95_null | Evidencia MODERADA | Publicar com ressalva |
| Δ_t > μ_null + σ_null | Evidencia FRACA | Investigar; requer Camada 3 |
| Δ_t > μ_null | Insuficiente | Nao afirmar evolucao |
| Δ_t ≤ μ_null | Ausencia | Domain shift confirmado |
| s ∈ S_apenas_T2 | Sem baseline | Aguardar T3; validar isoladamente |

## 5. Limiares de Jaccard (CORPUS-ESPECIFICOS)

⚠️ **NAO use limiares fixos.** Calibre a partir dos seus dados.

Para o corpus simulado de 5 instituicoes juridicas (STF, STJ, TJ-SP, TRF-1, TRF-6):

| Nivel | Valor | Uso |
|-------|-------|-----|
| Moderado (P95 raw) | **0.215** | Publicacao com ressalva |
| Estrito (P99 raw) | **0.279** | Publicacao cientifica |
| Permissivo (μ+σ) | **0.135** | Triagem inicial |

Comparacao: o limiar heuristico de 0.70 da SPEC-008 original e 3.26x mais
conservador que o P95 calibrado e **nao deve ser usado** em corpora
multi-institucionais (geraria falsos negativos).

## 6. Script de Auditoria

```
python article/evaluations/domain_shift_audit.py
```

**Requisitos:** Python 3.8+, numpy, scipy (opcional para Clopper-Pearson).
**Output:** `domain_shift_audit_output.json` com dados completos para LaTeX.
**Seed:** 42 (fixa para reprodutibilidade).
**Hash:** `440dff2922b19f0f0e655a69ed78a971`.

## 7. Integracao com Cora-Debate

A Camada 1B estabelece o nivel de independencia da validacao. O Cora-Debate
(V1-V7) opera dentro desse nivel. Scores gerados em dominios com Camada 1B
aplicada recebem a anotacao `[validado-C1B:P95]` ou `[validado-C1B:P99]`
conforme o limiar utilizado.

## 8. Referencias Principais

| # | Referencia | DOI |
|:--:|------------|-----|
| 1 | Jaccard, P. (1901). Etude comparative de la distribution florale. | 10.5169/seals-266450 |
| 2 | Efron, B. (1979). Bootstrap Methods. Annals of Statistics, 7(1). | 10.1214/aos/1176344552 |
| 3 | Hendrycks & Gimpel (2017). OOD Detection. ICLR. | 10.48550/arxiv.1610.02136 |
| 4 | Ben-David et al. (2010). Learning from Different Domains. ML, 79. | 10.1007/s10994-009-5152-4 |
| 5 | Bergmeir & Benitez (2012). Cross-validation for time series. | 10.1016/j.ins.2011.12.028 |

Documento completo (27 laudas): `article/jaccard_domain_shift_audit.pdf`.
25 referencias com DOI verificavel.

## 9. Limitacoes

- Requer metadados de `instituicao` — sem isso, a decomposicao e impossivel
- Minimo de 2 instituicoes por periodo; idealmente ≥ 4 para bootstrap estavel
- Limiares sao especificos do corpus — precisam ser recalibrados para novos dominios
- Jaccard trata templates como independentes (co-ocorrencias sao ignoradas)
- Com mais documentos, Jaccard diminui (uniao cresce mais rapido que intersecao)
