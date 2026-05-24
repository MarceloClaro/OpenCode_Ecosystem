# SEEKER Migration Report - Injeção de Dependência (Fase 4)

## Resumo

Migração dos módulos `basis-research/core/` e `basis-research/agents/` para usar DI via `core/interfaces.py` (IStateManager, IEventBus). A arquitetura original usa singletons module-level e imports diretos — alvo principal de refatoração.

## Módulos Analisados (17)

### Core (7 módulos)

| Módulo | Risco | Complexidade | Status |
|--------|-------|-------------|--------|
| `core/llm.py` | BAIXO | 3/10 | Refatorado |
| `core/argument_tree.py` | MÉDIO | 6/10 | Refatorado |
| `core/database.py` | ALTO | 7/10 | Futuro |
| `core/utils.py` | BAIXO | 1/10 | Futuro |
| `core/keys.py` | MÉDIO | 3/10 | Futuro |
| `core/context.py` | MÉDIO | 5/10 | Futuro |
| `core/__init__.py` | MÉDIO | 4/10 | Futuro |

### Agentes (10 módulos)

| Agente | Ordem SDD | Ordem Real | Riscos |
|--------|-----------|-----------|--------|
| `agents/grounder.py` | #1 | #1 | Estado atual desconhecido (não relido nesta fase) |
| `agents/social.py` | #2 | #2 | Importa `core.llm` como singleton |
| `agents/historian.py` | #3 | #3 | Importa `core.llm` como singleton |
| `agents/gaper.py` | #4 | #6 | Discrepância de ordem com SDD |
| `agents/vision.py` | #5 | #4 (duplicado SDD) | SDD lista VISION duas vezes |
| `agents/theorist.py` | #6 | #5 | Importa `core.llm` como singleton |
| `agents/rude.py` | #7 | #7 | Revisão adversarial |
| `agents/synthesizer.py` | #8 | #8 | Produz argument tree final |
| `agents/thinker.py` | #9 | #9 | Análise aprofundada |
| `agents/scribe.py` | #10 | #10 | Geração de artefatos |

## Arquivos Criados (3)

### `seeker_interfaces.py`
Define 10 interfaces abstratas + 10 interfaces de agente específico:
- `ISeekerAgent` — contrato base
- `ILLMRouter` — router LLM com fallback Claude → Ollama
- `IArgumentTree` — árvore de argumentos persistente (14 métodos)
- `IDatabase` — persistência do pipeline (13 métodos)
- `IContextBuilder` — contexto específico por agente (10 métodos)
- `IPipelineOrchestrator` — orquestrador da pipeline (3 métodos)
- `ISourceHandler` — handler de fonte acadêmica (2 métodos)
- `IGrounderAgent` a `IScribeAgent` — interfaces específicas

### `seeker_llm_router.py`
`LLMClient` refatorado com DI:
- Aceita `state_manager: Optional[IStateManager]`, `event_bus: Optional[IEventBus]` no construtor
- Fallback chain preservada: Claude primary → Claude Haiku → Ollama primary → Ollama light
- Logging via `event_bus.publish()` quando disponível
- **Compatibilidade retroativa**: `get_client()` singleton + `call()` função de conveniência
- `_load_env()` movido para dentro da classe (não executa na importação)
- `_publish()` / `_state_get()` / `_state_set()` helpers internos

Mudanças em relação ao original (`core/llm.py`):
- Remove singleton module-level `_client` / `get_client()` como única via
- `ANTHROPIC_API_KEY` carregada sob demanda, não na importação
- Health check retorna status estruturado

### `seeker_argument_tree.py`
`TreeBuilder` refatorado com DI:
- Aceita `state_manager`, `event_bus`, `db_path`, `id_generator` opcionais no construtor
- `IDatabase` como dependência futura; fallback SQLite direto preservado
- `default_id_generator()` injetável (substitui `core.utils.generate_id`)
- `_publish()` notifica mutações via EventBus
- `add_historical()`, `add_external()`, `add_audit_note()` — novos métodos do Historian

Mudanças em relação ao original (`core/argument_tree.py`):
- `run_id` obrigatório no construtor (antes passado em cada método)
- IDs gerados via função injetável (não mais `core.utils.generate_id`)
- Fallback SQLite direto mantido para compatibilidade retroativa

## Discrepâncias SDD vs Implementação Real

| Item | SDD | Realidade |
|------|-----|-----------|
| Agentes | 12 (VISION duplicado) | ~10 únicos |
| Ordem agentes | grounder, social, historian, gaper, vision, theorist, vision, rude, thinker, synthesizer, scribe | grounder, social, historian, vision, theorist, gaper, rude, synthesizer, thinker, scribe |
| `research/` dir | Mencionado | Não existe — apenas `basis-research/` |
| Search pipeline | 4 eixos paralelos | Presente em `main.py` com estrutura `break1`/`break2` |

## Componentes Pendentes de Refatoração

### `core/database.py` — Risco ALTO (7/10)
- Module-level functions com `DB_PATH` fixo
- Acoplamento forte com SQLite (INSERT/UPDATE/SELECT diretos)
- Recomendação: extrair `IDatabase` completa e implementar `SqliteDatabase` concreto
- Bloqueio: `argument_tree.py` e `context.py` dependem dele

### `core/keys.py` — Risco MÉDIO (3/10)
- `_load_env()` executado na importação — side effect
- Recomendação: mover para classe `KeyManager` com DI, carregar sob demanda

### `core/context.py` — Risco MÉDIO (5/10)
- Constrói prompts específicos por agente
- Acoplado a `database.py` para buscar dados
- Recomendação: implementar `IContextBuilder` concreto com DI

### `agents/*.py` — Risco MÉDIO (4/10 cada)
- Todos importam `from core import llm` como singleton
- A pipeline em `main.py` usa lazy imports com `importlib`
- Recomendação: migrar gradualmente usando `LLMRouterAdapter`

## Estimativa de Horas Restantes

| Componente | Horas | Risco |
|-----------|-------|-------|
| `core/database.py` → `IDatabase` + `SqliteDatabase` | 4h | ALTO |
| `core/keys.py` → `KeyManager` | 1h | MÉDIO |
| `core/context.py` → `ContextBuilder` | 2h | MÉDIO |
| `agents/*.py` (10) — adapter DI | 5h | MÉDIO |
| `main.py` — pipeline com DI | 2h | MÉDIO |
| Testes | 4h | MÉDIO |
| **Total** | **18h** | |

## Risco Geral

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Singleton LLMClient quebra agentes existentes | ALTO | BAIXA | Adapter `get_client()` mantém compatibilidade |
| SQLite acoplamento em database.py | MÉDIO | ALTA | Refatoração futura; fallback preservado |
| Discrepância ordem agentes SDD vs real | BAIXO | ALTA | Documentado; não afeta DI |
| keys.py side effect na importação | MÉDIO | MÉDIA | Já mitigado no `seeker_llm_router.py` |
