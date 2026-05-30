# Workflow Detalhado do Swarm Review

> Inspirado pelo pipeline do MiroFish:
> `Seed → Graph → Environment → Simulation (Twitter+Reddit) → Report → Deep Interaction`
>
> Adaptado como:
> `Contexto → Análise Paralela → Debate → Síntese → Reflexão`

---

## Fase 1: Preparação (Seed)

### Passo 1.1 — Coletar Contexto
Leia o alvo da revisão:
- PR description / commit message
- Diff completo das alterações
- Arquivos modificados (leia os que não conhece)
- Testes associados (se existirem)

### Passo 1.2 — Classificar a Mudança

| Tipo | Gatilho | Profundidade |
|------|---------|-------------|
| 🐛 Bugfix | "fix:", "bug:" | 2 agentes (segurança + arquitetura) |
| ✨ Feature | "feat:", "feature:" | 3 agentes (completo) |
| ♻️ Refactor | "refactor:", "refactoring" | 2 agentes (perf + arquitetura) |
| 🔧 Config/Infra | "chore:", "ci:", "infra" | 1-2 agentes |
| 🚀 Release | "release:", "major" | 3 agentes + revisão manual obrigatória |

### Passo 1.3 — Montar Enxame
Ative os agentes baseado na classificação. Para cada agente:
- Leia sua persona (`references/personas.md`)
- Aplique seu viés e checklist
- Registre o prompt de análise (cada agente recebe o mesmo contexto mas interpreta diferente)

---

## Fase 2: Análise Paralela (Graph → Environment)

Execute cada agente **sequencialmente** (simulando paralelismo neste ambiente):

### Para cada agente no enxame:

```
1. CARREGUE persona (viés, foco, ferramentas)
2. ANALISE cada arquivo na lente da especialidade
3. IDENTIFIQUE achados (use o checklist da persona)
4. CLASSIFIQUE severidade (CRÍTICO / Importante / Sugestão)
5. REGISTRE confiança (🟢 CONFIRMADO se evidência direta, 🟡 INFERIDO se padrão)
6. PRODUZA output no formato da persona
```

### Exemplo de Prompt Interno para Agente de Segurança:

```
"Você é o Agente de Segurança. Seu viés é -0.4 (tendenciosa a achar problemas).
Analise o código abaixo pela lente de OWASP Top 10. Use grep para procurar
padrões suspeitos. Reporte APENAS achados objetivos com evidência."

[Código/Diff aqui]

"Checklist para este arquivo: SQL injection, XSS, hardcoded secrets, 
validação de input. Reporte cada achado com severidade e confiança."
```

---

## Fase 3: Debate (Simulation)

Quando todos os agentes concluírem, rode a **rodada de debate**:

### Passo 3.1 — Coletar Achados
Reúna todos os achados em uma tabela unificada:

| ID | Agente | Achado | Severidade | Confiança |
|----|--------|--------|-----------|-----------|
| S1 | Segurança | SQL injection em login | 🔴 Crítico | 🟢 Confirmado |
| P2 | Performance | N+1 query em users/list | 🟡 Importante | 🟢 Confirmado |
| A3 | Arquitetura | Service layer anêmico | 🔵 Sugestão | 🟡 Inferido |

### Passo 3.2 — Identificar Conflitos
Para cada par de achados que se sobrepõem ou contradizem:

```
CONFLITO: Agente Segurança diz "use prepared statements" (🟢)
          Agente Performance diz "prepared statements são mais lentos" (🟡)

RESOLUÇÃO: Segurança tem peso 1.3 em issues de segurança → prevalece.
           Performance pode sugerir caching como compensação.

REGRA: Segurança sempre vence em issues de segurança.
```

### Passo 3.3 — Identificar Sinergias
Quando achados de agentes diferentes se complementam:

```
SINERGIA: Segurança → "Input não validado em upload"
          Arquitetura → "Serviço de upload sem camada de sanitização"

→ Achado combinado: "Implementar sanitization layer no upload service"
→ Prioridade: CRÍTICO (reforçado por 2 agentes)
```

### Passo 3.4 — Calcular Score
```
Score = 100 - (critical_count * 15) - (important_count * 5) - (suggestion_count * 1)
Score = max(0, min(100, score))

Faixas:
- 90-100: ✅ Excelente
- 70-89:  ⚠️ Aceitável com ressalvas
- 50-69:  ❌ Requer mudanças
- 0-49:   🚫 Bloqueado
```

---

## Fase 4: Síntese (Report)

Estruture o relatório consolidado seguindo o template.

### Estrutura do Relatório:

```markdown
1. Sumário Executivo
   - Alvo, enxame, score, veredito
   - 2-3 frases de visão geral

2. Perspectivas Individuais
   - Cada agente com seus achados (na íntegra)
   - Preservar o tom/personalidade de cada um

3. Consenso Consolidado
   - Achados que todos concordam
   - Achados que apenas um agente viu mas são válidos

4. Recomendações Priorizadas
   - Lista única com prioridade e agente origem

5. Métricas
   - Contagem total, por severidade, por agente
   - Score geral
```

---

## Fase 5: Reflexão (Deep Interaction)

Antes de finalizar:

1. **Auto-revisão:** Leia o relatório completo como se fosse um leitor externo
2. **Consistência:** Achados conflitantes foram todos resolvidos?
3. **Tom:** O relatório é construtivo? Tem pontos positivos?
4. **Ações:** Cada recomendação é acionável?
5. **Lacunas:** Algo que você gostaria de ter investigado mas não teve contexto?

Ajuste o relatório com base na reflexão.

---

## Pipeline Completo (Visão MiroFish)

```
┌─────────────┐    ┌──────────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│  Seed       │    │  Graph       │    │ Environ  │    │ Simul    │    │ Report    │
│  (Contexto) │───►│  (Análise    │───►│  (Debate │───►│  (Consol │───►│  (Relatório│
│             │    │   Paralela)  │    │   Estrutu│    │  idação) │    │   Final)  │
└─────────────┘    └──────────────┘    └──────────┘    └──────────┘    └───────────┘
      │                   │                  │               │               │
      │ PR/diff          │ 3 agentes        │ Resolução     │ Template     │ Auto-review
      │ arquivos         │ independentes    │ de conflitos  │ markdown     │ + polish
      └──────────────────┴──────────────────┴───────────────┴──────────────┴──────────
```
