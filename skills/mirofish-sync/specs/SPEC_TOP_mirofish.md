# SPEC_TOP_mirofish — MiroFishSyncEngine TDD Specification

**Skill:** mirofish-sync  
**Source:** scripts/mirofish_sync.py → MiroFishSyncEngine, GitHubMonitor, PatternClassifier  
**Framework:** pytest  
**Status:** Spec-Driven

---

## CT-1: test_init — Inicializacao do engine e baseline

**Objetivo:** Verificar que `MiroFishSyncEngine` inicializa com parametros
corretos, `SyncReport` vazio, e baseline carregada.

**Passos:**
1. Instanciar `MiroFishSyncEngine(dry_run=True, force=False)`
2. Verificar `engine.dry_run is True`, `engine.force is False`
3. Verificar `isinstance(engine.report, SyncReport)`
4. Verificar `engine.baseline is not None`

**Esperado:** Engine pronto para operacao com estado inicial valido.

---

## CT-2: test_check_updates — Verificacao de repositorio por mudancas

**Objetivo:** Confirmar que `check_repo()` retorna `SyncDiff` com
informacoes do repositorio consultado.

**Passos:**
1. Chamar `engine.check_repo("MiroFish", REPOS["MiroFish"])`
2. Verificar `isinstance(result, SyncDiff)`
3. Verificar `result.repo == "MiroFish"`

**Esperado:** Diff populado com nome do repositorio e acao definida.

---

## CT-3: test_parse_version — Classificacao de mudancas em arquivos

**Objetivo:** Validar que `PatternClassifier.classify()` detecta
arquivos Python em diretorios de engine como padroes extraiveis.

**Passos:**
1. Instanciar `PatternClassifier()`
2. Chamar `classify("BettaFish", [...])` com lista de arquivos modificados
3. Verificar que acao e lista de padroes sao retornados

**Esperado:** `action` definido e `patterns` e lista (pode ser vazia).

---

## CT-4: test_sync_report — Geracao de SyncReport completo

**Objetivo:** Garantir que `SyncReport` agrega corretamente dados de
multiplos repositorios, incluindo `repos_with_changes` e
`new_patterns_found`.

**Passos:**
1. Criar `SyncReport()` e popular `diffs` com `SyncDiff` contendo commits
2. Verificar `repos_checked`, `repos_with_changes`, `new_patterns_found`

**Esperado:** Campos do relatorio refletem dados populados.
