---
title: "Principio de Integridade e Auditabilidade"
version: "1.0"
status: "OBRIGATORIO — Transversal a todo o Ecossistema"
scope: "Analise, Producao, Documentacao, Comunicacao, Evolucao"
last_updated: "2026-05-30"
---

# Integridade e Auditabilidade — Principio Transversal Obrigatorio

## Fundamentacao

A credibilidade do OpenCode Ecosystem depende de uma unica coisa: **toda afirmacao deve ser verificavel**. Sem verificabilidade, nao ha ciencia. Sem transparencia, nao ha confianca. Este documento estabelece o principio de integridade como obrigacao transversal a todas as faces do projeto.

---

## Os 8 Raciocinios de Integridade

Aplicaveis a toda analise, producao, documentacao e comunicacao do ecossistema.

### R-I1 — Empirico-Verificacionista
**Definicao:** Toda afirmacao factual deve estar ancorada em evidencia verificavel. Nenhum numero pode ser apresentado sem que sua origem seja rastreavel.

**Aplicacao:**
- Documentacao: cada metrica cita o arquivo/script que a produziu
- Artigos: cada alegacao referencia fonte com DOI ou caminho no repositorio
- README: todos os numeros sao verificaveis contra o codigo

**Violacao tipica:** "O sistema tem 125 agentes" sem especificar onde estao definidos.

### R-I2 — Falsificabilidade
**Definicao:** Toda afirmacao deve ser estruturada de forma que possa ser falseada. "O sistema melhora continuamente" nao e falseavel. "O score medio subiu de 85 para 96 em 17 iteracoes" e falseavel.

**Aplicacao:**
- Hipotesses sao declaradas com condicoes de refutacao explicitas
- Scores incluem intervalo de confianca ou desvio padrao
- Afirmacoes qualitativas requerem criterio de verificacao

**Violacao tipica:** "O ecossistema produz artigos de excelencia internacional."

### R-I3 — Distincao Medido-vs-Projetado
**Definicao:** Separar explicitamente o que foi medido do que foi projetado, estimado ou auto-avaliado.

**Aplicacao:**
- Metricas auto-reportadas usam o rotulo `[auto-reportado]`
- Metricas externas citam a fonte com data de acesso
- Projecoes usam o rotulo `[projetado]` com metodologia

**Violacao tipica:** Apresentar score Qualis A1 96/100 como se fosse avaliacao externa da CAPES.

### R-I4 — Rastreabilidade Forense
**Definicao:** Um terceiro deve conseguir reproduzir o caminho completo de qualquer resultado — dos dados brutos ao numero final.

**Aplicacao:**
- Pipeline outputs incluem hash dos inputs
- Seeds aleatorias sao documentadas
- Comandos de execucao sao explicitos e reproduziveis

**Violacao tipica:** Reportar um score sem explicar como ele foi calculado.

### R-I5 — Contraprova Independente
**Definicao:** Resultados criticos devem ser validados por metodo independente. Se o Cora-Debate atribui confianca 0.98, uma segunda abordagem (ex: validacao humana em amostra) deve existir.

**Aplicacao:**
- Scores do Cora-Debate: amostra de 10% validada manualmente
- Correlacoes Pearson: comparadas com Spearman para robustez
- AutoEvolve scores: validadas por revisao humana periodica

**Violacao tipica:** Confiar exclusivamente em metricas auto-geradas.

### R-I6 — Origem de Dados (Provenance)
**Definicao:** Todo numero carrega metadados de origem: quem gerou, quando, com qual metodo, com quais parametros.

**Aplicacao:**
- Tabelas incluem coluna `[Origem]` com caminho do script ou fonte
- Graficos incluem nota de rodape sobre proveniencia dos dados
- JSON outputs incluem campo `provenance` com timestamp e hash

**Violacao tipica:** Tabela de metricas sem indicacao de como foram obtidas.

### R-I7 — Nivel de Confianca Explicito
**Definicao:** Toda afirmacao carrega um nivel de confianca explicito (escala 0-1), com justificativa.

**Aplicacao:**
- `[confianca: 0.98]` — verificado por 2 metodos independentes
- `[confianca: 0.70]` — auto-reportado, sem verificacao externa
- `[confianca: 0.50]` — estimativa baseada em extrapolacao

**Violacao tipica:** Apresentar todos os numeros com mesma aparencia de certeza.

### R-I8 — Correcao por Vies de Auto-Avaliacao
**Definicao:** Quando o sistema avalia a si mesmo, um fator de correcao deve ser aplicado ou a limitacao deve ser explicitamente declarada.

**Aplicacao:**
- Scores de auto-avaliacao incluem nota: "Este score e gerado pelo proprio sistema e nao constitui validacao externa."
- Comparacoes com benchmarks externos sao preferidas sobre scores internos
- Metricas de performance usam benchmarks estabelecidos quando disponiveis

**Violacao tipica:** Badge "Qualis A1 96/100" sem contexto de que e auto-atribuido.

---

## Regras de Aplicacao por Face do Projeto

### Face 1 — Analise (SEEKER, pesquisas, dados)

| Regra | Descricao |
|-------|-----------|
| A1 | Toda analise cita a fonte dos dados (DOI, URL, arquivo) com data de acesso |
| A2 | Correlacoes reportam p-valor e intervalo de confianca, nao apenas r |
| A3 | Outliers sao documentados, nao removidos silenciosamente |
| A4 | Seeds aleatorias sao explicitas nos scripts de analise |
| A5 | Resultados negativos sao reportados com o mesmo destaque que positivos |

### Face 2 — Producao (MASWOS, artigos, codigo)

| Regra | Descricao |
|-------|-----------|
| P1 | Toda alegacao no texto referencia fonte via TSAC |
| P2 | Palavras banidas (87) sao detectadas e removidas automaticamente |
| P3 | Score Qualis A1 e rotulado como `[auto-reportado]` |
| P4 | Figuras e tabelas incluem proveniencia dos dados |
| P5 | O metodo de geracao e documentado no proprio artigo |

### Face 3 — Documentacao (README, docs/, tdd-docs/)

| Regra | Descricao |
|-------|-----------|
| D1 | Numeros no README sao verificaveis contra arquivos no repositorio |
| D2 | Badges e metricas incluem nota sobre metodo de medicao |
| D3 | Toda secao de documentacao cita o commit/versao a que se refere |
| D4 | Superlativos ("excelente", "revolucionario", "melhor") sao proibidos |
| D5 | Limitacoes conhecidas sao declaradas em secao dedicada |

### Face 4 — Comunicacao (CLI, outputs, respostas ao usuario)

| Regra | Descricao |
|-------|-----------|
| C1 | Respostas ao usuario sao factuais, sem hipoteses nao declaradas |
| C2 | Incertezas sao comunicadas explicitamente ("Nao tenho certeza, mas...") |
| C3 | Outputs incluem proveniencia quando relevante |
| C4 | Nenhum caractere CJK na saida ao usuario (regra existente) |
| C5 | Autoconfianca do sistema nao e superestimada na comunicacao |

### Face 5 — Evolucao (AutoEvolve, ciclos, registro historico)

| Regra | Descricao |
|-------|-----------|
| E1 | Cada ciclo documenta: o que mudou, por que, com qual evidencia de melhoria |
| E2 | Scores de evolucao incluem metodo de calculo e limitacoes |
| E3 | Regressoes sao documentadas com a mesma transparencia que melhorias |
| E4 | O registro historico e imutavel — correcoes sao aditivas, nao substitutivas |
| E5 | Skills geradas automaticamente sao rotuladas como `[auto-gerada]` |

---

## Matriz de Conformidade

| Face | Regras | Auditor | Frequencia |
|------|:------:|---------|:----------:|
| Analise | 5 (A1-A5) | Cora-Debate V3 + V5 | A cada execucao |
| Producao | 5 (P1-P5) | TSAC + ptbr_corrector + Banca | A cada artigo |
| Documentacao | 5 (D1-D5) | Revisao manual | A cada release |
| Comunicacao | 5 (C1-C5) | ptbr_corrector + self-check | A cada resposta |
| Evolucao | 5 (E1-E5) | Auditoria de ciclo | A cada iteracao |

---

## Implementacao

### Checklist de Integridade (aplicar antes de qualquer commit publico)

```
[ ] Numeros no README conferem com arquivos no repositorio?
[ ] Scores auto-reportados estao explicitamente rotulados?
[ ] Badges incluem contexto sobre metodo de medicao?
[ ] Secao de Limitacoes esta atualizada?
[ ] Superlativos foram removidos ou justificados?
[ ] Toda alegacao factual tem origem rastreavel?
[ ] Dados de fontes externas tem data de acesso?
[ ] Seeds e parametros de execucao estao documentados?
[ ] Resultados negativos ou limitacoes estao visiveis?
[ ] ptbr_corrector.py executado (0 CJK)?
```

### Script de Verificacao

```bash
# Executar antes de cada commit publico
python criador-artigo/banca/ptbr_corrector.py  # CJK check
python scripts/audit_integridade.py             # Integrity audit (a criar)
grep -r "excelente\|revolucionario\|incrivel\|melhor" README.md docs/  # Superlativos
```

---

<div align="center">

**Principio de Integridade e Auditabilidade v1.0** · Obrigatorio para todo o ecossistema

*"Toda afirmacao deve ser verificavel. Sem verificabilidade, nao ha ciencia."*

Autor: Marcelo Claro Laranjeira — [ORCID: 0000-0001-8996-2887](https://orcid.org/0000-0001-8996-2887)

Professor / Pedagogo — Secretaria de Educacao, Prefeitura Municipal de Crateus, Ceara, Brasil

</div>
