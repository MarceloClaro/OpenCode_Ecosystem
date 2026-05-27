# PLANO DE INTEGRAÇÃO — ASI-Evolve + OpenCode Ecosystem
## Micro-Versionamento Autônomo (Cora-4.0.x) via ASI-Evolve Loop

**Data:** 26/05/2026 | **Fonte:** https://github.com/GAIR-NLP/ASI-Evolve

---

## 1. ANÁLISE DO ASI-Evolve

### 1.1 Arquitetura

```
┌──────────────────────────────────────────────────┐
│              ASI-Evolve Core Loop                 │
│                                                   │
│  LEARN ──→ DESIGN ──→ EXPERIMENT ──→ ANALYZE ──┐ │
│    ▲                                            │ │
│    └────────────────────────────────────────────┘ │
│                                                   │
│  Agentes: Researcher   Engineer   Analyzer        │
│  Memória: Cognition Store + Experiment Database   │
└──────────────────────────────────────────────────┘
```

### 1.2 O que o ASI-Evolve já provou

| Domínio | Resultado | Ganho |
|---------|-----------|:-----:|
| Neural Architecture | 105 arquiteturas SOTA | +0.97 pts |
| Data Curation | Pipeline evolutivo | +18 pts MMLU |
| RL Algorithm Design | Mecanismos matemáticos novos | +12.5 pts |
| Biomedical DTI | Arquitetura cold-start | +6.94 AUROC |

**Todos autonômos — zero intervenção humana após o seed inicial.**

---

## 2. OPORTUNIDADES DE INTEGRAÇÃO

### 2.1 Mapeamento ASI-Evolve → OpenCode

| ASI-Evolve | OpenCode Ecosystem |
|-----------|-------------------|
| **Researcher** (lê DB, propõe candidato) | `definitive_orchestrator.py` — classifica, seleciona agentes |
| **Engineer** (executa, coleta métricas) | `cross_validation.py` + `exhaustive_sweep.py` — testa combinações |
| **Analyzer** (destila lições) | `active_taxonomy.py` — ajusta pesos, registra padrões |
| **Cognition Store** | REASONING_REGISTRY + memory.json — conhecimento catalogado |
| **Experiment Database** | `micro_versions.json` + `evals/*.json` — histórico de tentativas |
| **Parent Selection (UCB1)** | Q-Score UCB1 do Cora-Debate — já implementado! |
| **MAP-Elites** | 19 domínios como "ilhas" de nicho — paralelo direto |

### 2.2 O Loop de Micro-Versionamento (Proposto)

```
┌─────────────────────────────────────────────────────────┐
│  GATILHO: exhaustive_sweep detecta gap (ex: func_eq 80%) │
│                         ↓                               │
│  PASSO 1: ASI-Evolve Researcher analisa o gap           │
│           → consulta Cognition Store (DCA, IMO)          │
│           → propõe N candidatos de correção              │
│                         ↓                               │
│  PASSO 2: ASI-Evolve Engineer testa cada candidato      │
│           → roda cross_validation.py                     │
│           → coleta métricas (PCI, ECE, Wilcoxon)         │
│                         ↓                               │
│  PASSO 3: ASI-Evolve Analyzer destila resultados        │
│           → identifica a melhor correção                 │
│           → registra lição na active_taxonomy            │
│           → gera micro-versão (Cora-4.0.1)              │
│                         ↓                               │
│  PASSO 4: Loop reinicia se PCI < 95 ou ECE > 0.15      │
└─────────────────────────────────────────────────────────┘
```

---

## 3. IMPLEMENTAÇÃO

### 3.1 Micro-Versionamento (já implementado)

```python
# definitive_orchestrator.py — _micro_version_bump()
# Cada correção gera Cora-4.0.x automaticamente

{
  "timestamp": "2026-05-26T22:45:00",
  "type": "r23_activation_boost",
  "details": "R23 prob 0.70->0.85, deactivations 16/50->4/50",
  "version": "4.0.1"
}
```

### 3.2 Cognition Store (seed com conhecimento DCA)

O ASI-Evolve Cognition Store será semeado com:
1. **7 exercícios DCA Módulo 1** — todos resolvidos (PCI 100)
2. **7 problemas DCA Listas 1+2** — com padrões R209-R212
3. **10 problemas IMO** — com métricas de validação
4. **Padrões geométricos R205-R208** — Darboux, Kähler, Hopf, S²
5. **Resultados do exhaustive sweep** — 1.225 combinações testadas

### 3.3 Experiment Database (rastreamento de tentativas)

Cada iteração do ASI-Evolve registra:
```json
{
  "id": "exp_042",
  "motivation": "R23 deactivated 16/50 in functional_equation",
  "hypothesis": "Boost R23 activation prob from 0.70 to 0.85",
  "code_change": "exhaustive_sweep.py:150",
  "result": {
    "pci_before": 80,
    "pci_after": 88,
    "ece_before": 0.25,
    "ece_after": 0.22,
    "wilcoxon_p": 0.03
  },
  "analysis": "R23 boost improved functional_equation by +8pts. Generalized to inequality (+4pts).",
  "version": "4.0.1"
}
```

---

## 4. FLUXO DE MICRO-VERSÕES

### 4.1 Gatilhos de evolução

| Gatilho | Condição | Ação |
|---------|----------|------|
| **GAP_DOMINIO** | PCI < 85 em algum domínio | Researcher: analisa reasoning gap |
| **ECE_ALTO** | ECE > 0.20 | Researcher: propõe ajuste de calibração |
| **DESATIVACAO** | Agente desativado > 30% | Researcher: revisa threshold de ativação |
| **NOVO_PADRAO** | Creative Leap detecta par cross-domain | Researcher: propõe novo raciocínio |
| **CONTRA_PROVA** | Artigo detecta limitação | Researcher: projeto de correção |

### 4.2 Versões projetadas

| Cora | Gap | Correção | PCI Meta |
|:----:|-----|----------|:---:|
| 4.0.1 | R23 16/50 deactivations | Boost prob: 0.70→0.85 | 88→92 |
| 4.0.2 | func_equation 80% | +10 training problems | 80→90 |
| 4.0.3 | ECE 0.25 | Platt scaling integrated | 0.25→0.12 |
| 4.0.4 | R34 generalization | Refine heuristic | 80→88 |
| 4.0.5 | Auto-improve todos | ASI-Evolve loop completo | 92→96 |
| 4.1.0 | Lean 4 integration | Formal back-end | 96→99 |

---

## 5. COMPARAÇÃO: ASI-Evolve vs AutoEvolve (OpenCode)

| Dimensão | AutoEvolve (OpenCode) | ASI-Evolve (GAIR-NLP) |
|----------|----------------------|----------------------|
| **Escopo** | Skills e plugins | Experimentos científicos |
| **Loop** | SENSE→INSTALL→EVOLVE | LEARN→DESIGN→EXPERIMENT→ANALYZE |
| **Memória** | memory.json | Cognition Store + Experiment DB |
| **Agentes** | 1 (monolítico) | 3 (Researcher, Engineer, Analyzer) |
| **Seleção** | Regras fixas | UCB1, greedy, MAP-Elites |
| **Domínios** | Software | Qualquer (física, bio, ML) |
| **Resultados** | Skills novas | Artigos publicáveis |
| **Sinergia** | Pode EVOLUIR o AutoEvolve | Pode ser INVOCADO pelo AutoEvolve |

---

## 6. ARQUITETURA FINAL (OpenCode + ASI-Evolve)

```
┌─────────────────────────────────────────────────────────────┐
│               OpenCode Ecosystem v4.6.1                      │
│                                                              │
│  ┌──────────────────┐     ┌─────────────────────────────┐    │
│  │ definitive_      │────→│ ASI-Evolve Integration      │    │
│  │ orchestrator.py  │     │                             │    │
│  │                  │     │  GAP_DETECTED?              │    │
│  │  Classify        │     │    │                        │    │
│  │  Select Agents   │     │    ├──→ Researcher          │    │
│  │  7-Fase Pipeline │     │    │   (analisa cognition)  │    │
│  │  Platt Scale     │     │    │                        │    │
│  │  PCI Report      │     │    ├──→ Engineer            │    │
│  └──────────────────┘     │    │   (cross_validate)      │    │
│                            │    │                        │    │
│  ┌──────────────────┐     │    ├──→ Analyzer            │    │
│  │ AutoEvolve       │     │    │   (destila lições)     │    │
│  │ (skills/plugins) │     │    │                        │    │
│  └──────────────────┘     │    └──→ Micro-Version Bump  │    │
│                            │        (Cora-4.0.1, .2...) │    │
│  ┌──────────────────┐     └─────────────────────────────┘    │
│  │ Cora-Debate      │                                        │
│  │ (38/38 validado) │                                        │
│  └──────────────────┘                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. PRÓXIMOS PASSOS

1. **Instalar ASI-Evolve** como submodule no repositório
2. **Semear Cognition Store** com conhecimento DCA + IMO
3. **Conectar Engineer** ao `cross_validation.py` e `exhaustive_sweep.py`
4. **Ativar loop** para resolver os 4 gaps identificados
5. **Monitorar** micro-versões geradas automaticamente

---

*Plano de integração — OpenCode Ecosystem v4.6.1 + ASI-Evolve — 26/05/2026*
