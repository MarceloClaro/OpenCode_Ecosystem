# Template de Relatório do Swarm Review

> Inspirado pelo ReportAgent ReACT pattern do MiroFish.

---

````markdown
# 🧠 Swarm Review Report

**Data:** YYYY-MM-DD
**Alvo:** [caminho/arquivo, PR #, commit hash]
**Enxame:** 🛡️ Segurança ⚡ Performance 🏗️ Arquitetura
**Modo:** [quick | full]

---

## 📊 Sumário Executivo

**Score Geral:** [0-100]/100
**Veredito:** ✅ APROVADO | ⚠️ APROVADO COM RESSALVAS | ❌ REQUER MUDANÇAS | 🚫 BLOQUEADO

| Métrica | Valor |
|---------|-------|
| Total de achados | [N] |
| 🔴 Críticos | [N] |
| 🟡 Importantes | [N] |
| 🔵 Sugestões | [N] |
| 🟢 Confirmados | [N] |
| 🟡 Inferidos | [N] |
| 🔴 Lacunas | [N] |

**Resumo:** [2-3 frases sobre o estado geral do código revisado]

---

## 🛡️ Perspectiva: Segurança

**Agente:** Analista de Segurança Sênior
**Viés:** -0.4 | **Peso:** 1.3
**Achados:** [N] (🔴 [N] Críticos, 🟡 [N] Importantes, 🔵 [N] Sugestões)

### 🔴 Críticos
| # | Arquivo | Achado | Recomendação | Confiança |
|---|---------|--------|-------------|-----------|
| 1 | [path:line] | [descrição] | [recomendação] | 🟢/🟡/🔴 |

### 🟡 Importantes
| # | Arquivo | Achado | Recomendação | Confiança |
|---|---------|--------|-------------|-----------|

### 🔵 Sugestões
| # | Arquivo | Achado | Recomendação | Confiança |
|---|---------|--------|-------------|-----------|

---

## ⚡ Perspectiva: Performance

**Agente:** Engenheira de Performance Sênior
**Viés:** -0.2 | **Peso:** 1.0
**Achados:** [N] (🔴 [N] Críticos, 🟡 [N] Importantes, 🔵 [N] Sugestões)

### 🔴 Críticos
| # | Arquivo | Achado | Recomendação | Confiança |
|---|---------|--------|-------------|-----------|

### 🟡 Importantes
| # | Arquivo | Achado | Recomendação | Confiança |
|---|---------|--------|-------------|-----------|

### 🔵 Sugestões
| # | Arquivo | Achado | Recomendação | Confiança |
|---|---------|--------|-------------|-----------|

---

## 🏗️ Perspectiva: Arquitetura

**Agente:** Arquiteta de Sistemas Sênior
**Viés:** +0.1 | **Peso:** 1.1
**Achados:** [N] (🔴 [N] Críticos, 🟡 [N] Importantes, 🔵 [N] Sugestões)

### 🔴 Críticos
| # | Arquivo | Achado | Recomendação | Confiança |
|---|---------|--------|-------------|-----------|

### 🟡 Importantes
| # | Arquivo | Achado | Recomendação | Confiança |
|---|---------|--------|-------------|-----------|

### 🔵 Sugestões
| # | Arquivo | Achado | Recomendação | Confiança |
|---|---------|--------|-------------|-----------|

---

## 💬 Debate & Consenso

### Conflitos Resolvidos
| Conflito | Agentes | Resolução | Decisor |
|----------|---------|-----------|---------|
| [issue] | [agentes] | [decisão] | [quem venceu] |

### Conflitos Não Resolvidos (🔴 Lacunas)
| Conflito | Agentes | Motivo | Ação Necessária |
|----------|---------|--------|----------------|
| [issue] | [agentes] | [por que não resolveu] | [validação humana] |

### Sinergias Identificadas
| Sinergia | Agentes | Achado Combinado | Prioridade |
|----------|---------|-----------------|------------|
| [descrição] | [agentes] | [achado consolidado] | 🔴/🟡/🔵 |

---

## 🎯 Recomendações Prioritárias

### Deve Corrigir (🔴)
1. **[Segurança]** [descrição] — [arquivo] — [confiança]
2. **[Performance]** [descrição] — [arquivo] — [confiança]

### Deveria Corrigir (🟡)
1. **[Arquitetura]** [descrição] — [arquivo] — [confiança]

### Sugestões (🔵)
1. **[Performance]** [descrição] — [arquivo] — [confiança]

---

## ✅ O Que Está Bom

- [ ] [ponto positivo identificado por agente X]
- [ ] [ponto positivo identificado por agente Y]
- [ ] [padrão que todos os agentes elogiaram]

---

## 📋 Métricas de Qualidade

| Dimensão | Achados | Score Parcial |
|----------|---------|--------------|
| 🛡️ Segurança | [N] | [0-100] |
| ⚡ Performance | [N] | [0-100] |
| 🏗️ Arquitetura | [N] | [0-100] |
| **Geral** | **[N]** | **[0-100]** |

### Cálculo do Score
```
Score = 100 - (critical_count × 15) - (important_count × 5) - (suggestion_count × 1)
Score final: [N]/100
```

### Legenda
| Score | Veredito |
|-------|----------|
| 90-100 | ✅ Excelente |
| 70-89 | ⚠️ Aceitável com ressalvas |
| 50-69 | ❌ Requer mudanças |
| 0-49 | 🚫 Bloqueado |

---

*Relatório gerado pelo Swarm Review Engine v1.0 — Padrão MiroFish OASIS*
*Agentes: 🛡️ Segurança · ⚡ Performance · 🏗️ Arquitetura*
````
