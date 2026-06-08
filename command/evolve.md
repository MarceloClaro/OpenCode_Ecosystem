<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

---
description: Ativa o pipeline de evolução autônoma do OpenCode. SENSE → DISCOVER → INSTALL → VERIFY → EVOLVE → LEARN. O ecossistema evolui sozinho. Subcomandos: status, discover, install, verify, update, learn.
---

# /evolve — Pipeline de Evolução Autônoma v5.1

O ecossistema OpenCode evolui sozinho. O pipeline `/evolve` orquestra 6 fases que mantêm skills, plugins, MCPs e agentes atualizados, validados e otimizados.

```
SENSE → DISCOVER → INSTALL → VERIFY → EVOLVE → LEARN
```

## Subcomandos

### `/evolve`
Pipeline completo. Executa todas as 6 fases em sequência (fail-soft). Ideal para manutenção periódica.

### `/evolve status`
Diagnóstico rápido do ecossistema. Exibe:
- Health score, total de skills, plugins, binários
- Resultado dos 10 CTs SPEC-026
- Última sessão registrada

### `/evolve discover`
Busca novas skills no GitHub Trending:
- `topics/agent-skills` e `topics/claude-code-skills`
- Top 10 ordenados por stars
- Filtra skills já instaladas
- **Não instala automaticamente**

### `/evolve install <N>`
Instala a N-ésima skill da última descoberta.
- Valida stars >= 10 (segurança)
- Baixa SKILL.md e registra em `installed.json`

### `/evolve verify`
Validação completa:
- SPEC-025: frontmatter YAML (161 skills)
- SPEC-026: pipeline health (10 CTs)
- Binários: `browser-use doctor`, `ralph-tui --version`
- MCPs: conectividade

### `/evolve update`
Manutenção do ecossistema:
- Remove órfãos (404)
- Consolida duplicatas
- Atualiza skills com versão nova

### `/evolve learn`
Persiste aprendizados da sessão:
- Métricas de ferramentas (frequência, latência, erros)
- Ranking de utilidade das skills
- Atualiza `memory.json`

## Agentes do Pipeline

| Agente | Arquivo | Função |
|--------|---------|--------|
| `autoevolve` | `agents/autoevolve.md` | Orquestrador principal + subcommand router |
| `evolve-state` | `skills/system/evolve-state.md` | Persistência de estado e ranking |
| `self-healer` | MCP `self-healer` | Diagnóstico e reparo automático |
| `manus-evolve` | `plugins/manus-evolve.ts` | PlanAct Engine v2.2 (TypeScript) |
| `manus-bridge` | `nexus/scripts/manus_evolve_bridge.py` | Bridge TypeScript↔Python |

## Test Suites Integradas

| Suite | Comando | CTs |
|-------|---------|-----|
| SPEC-025 | `python specs/test_frontmatter_validator.py` | 161 skills |
| SPEC-026 | `python specs/test_evolve_pipeline.py` | 10 CTs |
| SPEC-027 | `python specs/test_evolve_e2e.py` | 8 CTs E2E |

## Exemplos

```bash
# Ver saúde do ecossistema
/evolve status

# Buscar novidades no GitHub
/evolve discover

# Instalar a 3ª skill descoberta
/evolve install 3

# Validar tudo (frontmatter + pipeline + binários)
/evolve verify

# Pipeline completo (manutenção semanal)
/evolve
```

## Regras de Segurança

| Regra | Descrição |
|-------|-----------|
| Stars mínimos | Skills < 10 stars exigem revisão manual |
| Backup | Todo update faz backup em `.evolve/ecosystem_backup/` |
| Dry-run | `/evolve install` e `/evolve update` mostram diff antes de aplicar |
| Sem sobrescrita | Skills modificadas pelo usuário nunca são sobrescritas |
| .gitignore | `.evolve/` não é commitado (dados locais) |

## Estado do Ecossistema

| Métrica | Valor |
|---------|-------|
| Skills totais | 161 |
| Skills externas | 8 (installed.json) |
| Plugins | 12 |
| MCPs | 46 |
| Evolution rounds | 18 |
| Health score | 100/100 |
| CTs SPEC-026 | 10/10 PASS |
