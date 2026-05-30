---
title: "Qualis A1 Scoring Engine"
version: "4.6"
criteria: 10
weights: [25, 20, 15, 15, 10, 10, 5]
threshold: 95
---

# Qualis A1 Scoring Engine

## Critérios de Pontuação

| # | Critério | Peso | Máximo | Descrição |
|:--:|----------|:----:|:------:|-----------|
| 1 | Originalidade | 25% | 25 | Contribuição inédita ao campo |
| 2 | Metodologia | 20% | 20 | Rigor metodológico e reprodutibilidade |
| 3 | Revisão de Literatura | 15% | 15 | Cobertura e atualidade das referências |
| 4 | Resultados | 15% | 15 | Clareza e validade dos achados |
| 5 | Discussão | 10% | 10 | Interpretação e implicações |
| 6 | Formatação ABNT | 10% | 10 | Conformidade com normas |
| 7 | Relevância | 5% | 5 | Impacto potencial no campo |

## Algoritmo de Scoring

```
┌──────────────────────────────────────────────────────────────────┐
│                    AUTO_SCORE_QUALIS.py                           │
│                                                                   │
│  INPUT: artigo.pdf                                                │
│     │                                                             │
│     ▼                                                             │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  EXTRAIR métricas:                                       │    │
│  │  ├── Originalidade: Cora-Debate V7 (PlagCheck)           │    │
│  │  ├── Metodologia: Cora-Debate V4 (Stats) + V1 (Logic)    │    │
│  │  ├── Literatura: Cora-Debate V3 (CrossRef)               │    │
│  │  ├── Resultados: Cora-Debate V5 (Cross-Correlation)      │    │
│  │  ├── Discussão: Cora-Debate V6 (Completeness)            │    │
│  │  ├── Formatação: ABNT Checker + CJK Detector             │    │
│  │  └── Relevância: PhD Auditor (Sensitivity)               │    │
│  └──────────────────────────────────────────────────────────┘    │
│     │                                                             │
│     ▼                                                             │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  CALCULAR score:                                         │    │
│  │  S = Σ(wᵢ × cᵢ)  onde wᵢ = peso, cᵢ = nota              │    │
│  └──────────────────────────────────────────────────────────┘    │
│     │                                                             │
│     ▼                                                             │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  S ≥ 95?                                                  │    │
│  │    ├── SIM → EXPORT (LaTeX/PDF) + EVOLVE                  │    │
│  │    └── NÃO → LOOP_BACK (Correção Iterativa)               │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

## Escala de Conversão

| Score | Classificação Qualis | Significado |
|:-----:|:--------------------:|-------------|
| 95-100 | A1 | Excelência internacional |
| 85-94 | A2 | Alta qualidade |
| 75-84 | B1 | Boa qualidade |
| 65-74 | B2 | Qualidade mediana |
| 55-64 | B3 | Abaixo da média |
| 0-54 | C | Não recomendado |

## Histórico de Scores

| Artigo | Score | Ciclos | Tempo | Data |
|--------|:-----:|:------:|:-----:|------|
| Impacto da IA no Mercado de Trabalho | 95/100 | 4 | 12min | 2026-05-20 |
| QML Medical Imaging HAM10000 | 97/100 | 3 | 8min | 2026-05-21 |
| Cross-Validation 50 Indicadores | 94/100 | 5 | 15min | 2026-05-22 |
| Artigo ABNT Expandido 40p | 96/100 | 2 | 10min | 2026-05-23 |
| Geometria Simplética | 100/100 | 1 | 5min | 2026-05-24 |

## Evolução do Score Médio

```
100 ┤                                    ●──●
 95 ┤              ●──●────●────●───●───●
 90 ┤        ●────●
 85 ┤   ●───●
 80 ┤
 75 ┤
     └───┬────┬────┬────┬────┬────┬────┬────
        v3.5 v4.0 v4.2 v4.2.1 v4.2.2 v4.2.3 v4.6
            86.5 → 90 → 92 → 93 → 94 → 95 → 96
```

## Configuração

```bash
python criador-artigo/banca/AUTO_SCORE_QUALIS.py \
  --input artigo.pdf \
  --threshold 95 \
  --max-iterations 10 \
  --cora-debate all \
  --output-audit audit_trail.json
```
