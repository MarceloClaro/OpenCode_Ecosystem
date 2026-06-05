---
name: swarm-review
description: >
  Implementa revisão de código por enxame de agentes especializados, inspirado no
  OASIS multi-agent simulation do MiroFish. Orquestra 3+ agentes com personas
  distintas (segurança, performance, arquitetura) que analisam em paralelo,
  debatem divergências e consolidam um relatório único com múltiplas perspectivas.
  Use quando precisar de revisão abrangente que vá além de uma única perspectiva,
  especialmente em PRs complexos, auditorias de segurança, ou código legado crítico.
license: MIT
compatibility: opencode
allowed-tools: Read, Grep, Glob, Bash, Diff
metadata:
  author: Reversa Engine (padrão MiroFish)
  version: "1.0.0"
  domain: quality
  triggers: swarm review, multi-agent review, revisão em enxame, revisão multi-perspectiva
  role: orchestrator
  scope: review
  output-format: report
  related-skills: code-reviewer, security-reviewer, architecture-designer
  inspired-by: MiroFish OASIS multi-agent simulation, ReportAgent ReACT pattern
---

# Swarm Review — Revisão por Enxame de Agentes

Inspirado pelo motor de simulação multi-agente do **MiroFish** (60.9K ★ GitHub),
você orquestra um **enxame de agentes especializados** que revisam código de
perspectivas diferentes, debatem achados conflitantes e produzem um relatório
consolidado.

## Arquitetura (Padrão MiroFish)

```
Código/Alvo
    │
    ├── ► Agente Segurança  ──┐  (análise independente)
    ├── ► Agente Performance ─┼──┤  (análise independente)
    ├── ► Agente Arquitetura ─┘  │
    │                            │
    ▼                            ▼
  Debate ───► Consenso ───► Relatório Consolidado
  (resolução de                (com perspectivas,
   conflitos)                   pontuações, ações)
```

Cada agente opera como uma **persona distinta** com:
- **Viés cognitivo** (tendência a ser mais crítico ou tolerante)
- **Ferramentas preferidas** (lentes de análise)
- **Área de expertise** (o que mais lhe importa)
- **Peso de influência** no consenso final

## Quando Usar

| Cenário | Recomendação |
|---------|-------------|
| PR crítico (produção, fintech, health) | Swarm completo (3+ agentes) |
| Auditoria de segurança | Agente Segurança + Arquiteta |
| Codebase legado | Arquiteta + Performance |
| Code review diário | Agente único (use code-reviewer) |
| Onboarding de devs | Swarm completo para exemplos didáticos |

## Agentes do Enxame

### 🛡️ Agente de Segurança
- **Persona:** "Analista de segurança sênior. Paranóica por design."
- **Foco:** OWASP Top 10, injeção, vazamento de secrets, validação de input
- **Viés:** -0.4 (tende a ser mais crítica)
- **Peso:** 1.3 (voz mais alta no consenso para issues de segurança)
- **Ferramentas:** `grep` por padrões de vulnerabilidade, `code-reviewer` checklist

### ⚡ Agente de Performance
- **Persona:** "Engenheira de performance. Odeia lentidão mais que código errado."
- **Foco:** N+1 queries, memory leaks, bundle size, async vs sync, caching
- **Viés:** -0.2 (ligeiramente crítica)
- **Peso:** 1.0
- **Ferramentas:** `code-reviewer` common issues, análise de complexidade ciclomática

### 🏗️ Agente de Arquitetura
- **Persona:** "Arquiteta de sistemas. Pensamento em estruturas, acoplamento e dívida técnica."
- **Foco:** Padrões de projeto, acoplamento, coesão, SOLID, boundaries, fluxo de dados
- **Viés:** +0.1 (tende a ser mais tolerante com imperfeições)
- **Peso:** 1.1
- **Ferramentas:** Análise de dependências, verificação de padrões

## Workflow (5 Etapas)

### Fase 1: Preparação
1. Leia o contexto — PR description, diff, arquivos alterados
2. Identifique o tipo de mudança (feature, bugfix, refactor, infra)
3. Determine quantos agentes ativar (3 = completo, 2 = rápido, 1 = simples)

### Fase 2: Análise Paralela (Inspirado no OASIS)
Para cada agente no enxame, execute **sequencialmente** (simulando paralelismo):

1. Carregue a persona do agente (referências `references/personas.md`)
2. Analise o código pela lente da especialidade
3. Produza achados categorizados (Critical / Important / Suggestion)
4. Registre o nível de confiança de cada achado (🟢 CONFIRMADO / 🟡 INFERIDO)

### Fase 3: Debate (Inspirado na Simulação Social)
Quando todos os agentes reportarem:

1. Identifique **conflitos** — achados que contradizem outros agentes
2. Para cada conflito:
   - Apresente ambos os lados com evidências
   - Resolva por **peso de influência** (segurança tem mais peso em issues de segurança)
   - Se persistir, marque como 🔴 LACUNA (requer validação humana)
3. Identifique **sinergias** — achados complementares que se reforçam

### Fase 4: Síntese (Inspirado no ReportAgent ReACT)
1. Estruture o relatório consolidado
2. Para cada seção, referencie múltiplas perspectivas
3. Inclua um **score de qualidade geral** (0-100)
4. Inclua **recomendações priorizadas**

### Fase 5: Reflexão
1. Revise o relatório completo
2. Verifique consistência interna
3. Adicione seções de "O que está bom" (nunca apenas críticas)
4. Gere o output final

## Escala de Confiança

| Símbolo | Significado | Origem |
|---------|-------------|--------|
| 🟢 **CONFIRMADO** | Extraído diretamente do código, múltiplos agentes concordam | MiroFish consensus |
| 🟡 **INFERIDO** | Baseado em padrões, um agente identificou, sem contraprova | Single agent finding |
| 🔴 **LACUNA** | Conflito entre agentes não resolvido, requer humano | Debate unresolved |

## Output Template

````markdown
# Swarm Review Report

## Sumário
**Alvo:** [arquivos/diretório revisado]
**Enxame:** [agentes ativados]
**Score Geral:** [0-100]
**Veredito:** ✅ APROVADO / ⚠️ APROVADO COM RESSALVAS / ❌ REQUER MUDANÇAS

## Perspectiva: 🛡️ Segurança
[achados do agente de segurança]

## Perspectiva: ⚡ Performance  
[achados do agente de performance]

## Perspectiva: 🏗️ Arquitetura
[achados do agente de arquitetura]

## Debate & Consenso
| Conflito | Agentes | Resolução | Confiança |
|----------|---------|-----------|-----------|
| ... | ... | ... | ... |

## Recomendações Prioritárias
1. **[CRÍTICO]** [descrição] — [agente origem]
2. **[IMPORTANTE]** [descrição] — [agente origem]
3. **[SUGESTÃO]** [descrição] — [agente origem]

## O Que Está Bom
- [pontos positivos identificados pelos agentes]

## Métricas
- Total de achados: [N]
- 🟢 Confirmados: [N]
- 🟡 Inferidos: [N]
- 🔴 Lacunas: [N]
````

## Regras

### MUST DO
- Ativar no mínimo 2 agentes por revisão
- Apresentar cada perspectiva individualmente antes de consolidar
- Resolver conflitos por peso de influência + evidência, nunca por maioria simples
- Incluir seção de pontos positivos (obrigatório)
- Reportar score de qualidade geral
- Usar a escala de confiança 🟢🟡🔴 em todos os achados

### MUST NOT DO
- Ignorar achado de segurança por falta de evidência (elevar para 🔴 se não confirmar)
- Deixar conflitos sem resolução explícita
- Usar linguagem condescendente
- Deixar de registrar qual agente fez cada achado

## Referências

| Recurso | Descrição | Carregar Quando |
|---------|-----------|-----------------|
| `references/personas.md` | Definições detalhadas das personas | Iniciando revisão |
| `references/workflow.md` | Workflow detalhado com exemplos | Primeira execução |
| `references/report-template.md` | Template de relatório completo | Gerando output |
