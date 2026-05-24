---
name: mirofish-sync
description: Agente de sincronização MiroFish/BettaFish ↔ OpenCode. Monitora repos upstream (666ghj/MiroFish, 666ghj/BettaFish, bytedance/deer-flow), detecta novos padrões, extrai automaticamente via Reversa Scout e integra no ecossistema como P19+. Use quando precisar manter o ecossistema sincronizado com as últimas releases do MiroFish.
triggers: mirofish sync, sincronizar mirofish, atualizar mirofish, /mirofish-sync, sync mirofish, upstream sync, mf sync, mirofish update, bettafish update, deerflow update
pattern-id: P19
---

# MiroFish Sync Agent (P19)

Agente de sincronização bidirecional entre os repositórios upstream MiroFish/BettaFish/DeerFlow e o ecossistema OpenCode.

## Arquitetura

```
┌──────────────────────┐     ┌──────────────────────┐     ┌───────────────────┐
│  666ghj/MiroFish     │     │  666ghj/BettaFish    │     │  bytedance/deer-  │
│  (61K ⭐ · AGPL-3.0) │     │  (40.9K ⭐ · GPL-2.0) │     │  flow (MIT)       │
└──────────┬───────────┘     └──────────┬───────────┘     └────────┬──────────┘
           │                            │                           │
           └────────────────────────────┼───────────────────────────┘
                                        │
                          ┌─────────────▼─────────────┐
                          │    MiroFish Sync Agent     │
                          │    (P19 — Monitor+Sync)     │
                          │                            │
                          │  1. Monitor (GitHub API)    │
                          │  2. Diff (commits novos)    │
                          │  3. Extract (Reversa Scout) │
                          │  4. Integrate (P19+)        │
                          │  5. Register (code-graph)   │
                          └─────────────┬─────────────┘
                                        │
                          ┌─────────────▼─────────────┐
                          │   OpenCode Ecosystem       │
                          │   .reversa/mirofish_ver.   │
                          │   json + code-graph.db     │
                          └────────────────────────────┘
```

## Workflow

### Fase 1: MONITOR — Verificar mudanças upstream

1. Consulta GitHub API (`GET /repos/{owner}/{repo}/commits`) para os 3 repositórios
2. Compara `sha` do último commit com o registrado em `.reversa/mirofish_version.json`
3. Se há commits novos → Fase 2
4. Se não há → "Nenhuma atualização pendente"

### Fase 2: DIFF — Analisar o que mudou

1. Obtém a lista de arquivos modificados entre `last_synced_commit` e `HEAD`
2. Classifica mudanças por tipo:
   - `new_engine`: Novo diretório de engine (ex: `/PredictionEngine/`)
   - `new_pattern`: Novo padrão arquitetural detectável
   - `api_change`: Mudança em APIs existentes
   - `docs_only`: Apenas documentação
   - `security_fix`: Correção de segurança
   - `dependency`: Atualização de dependências

### Fase 3: EXTRACT — Extrair novos padrões

1. Para cada `new_engine` ou `new_pattern`:
   - Ativa o Reversa Scout para análise do novo código
   - Extrai a estrutura (classes, funções, fluxo de dados)
   - Gera especificação no padrão SKILL.md
2. Atribui número P19, P20, etc.

### Fase 4: INTEGRATE — Integrar no ecossistema

1. Cria diretório `skills/{nome}/` com:
   - `SKILL.md` (com padrão extraído)
   - `scripts/` (implementação Python)
   - `references/` (documentação complementar)
2. Registra em `.reversa/code-graph.db`
3. Atualiza `.reversa/pipeline.db`
4. Atualiza `mirofish_version.json`

### Fase 5: REPORT — Relatório de sincronização

1. Gera relatório Markdown com:
   - Mudanças detectadas
   - Padrões extraídos
   - Padrões ignorados (justificativa)
   - Próximos passos

## Comando

```
/mirofish-sync [--dry-run] [--force] [--repo=mirofish|bettafish|deerflow|all]
```

- `--dry-run`: Apenas verifica, não modifica
- `--force`: Re-extrai todos os padrões mesmo sem mudanças
- `--repo`: Filtra por repositório específico

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `scripts/mirofish_sync.py` | Motor principal de sincronização |
| `scripts/github_monitor.py` | Cliente da GitHub API |
| `scripts/pattern_extractor.py` | Extrator de padrões via Reversa Scout |
| `references/sync_protocol.md` | Protocolo detalhado de sincronização |
| `.reversa/mirofish_version.json` | Baseline de sincronização |
