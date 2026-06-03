# SPEC_TOP_hotreload — SkillWatcher TDD Specification

**Skill:** hot-reload-skills  
**Source:** scripts/skill_watcher.py → SkillWatcher, SkillRegistry, SkillParser, SkillValidator  
**Framework:** pytest  
**Status:** Spec-Driven

---

## CT-1: test_init — Inicializacao de SkillRegistry e SkillWatcher

**Objetivo:** Verificar que `SkillRegistry` inicia vazio e `SkillWatcher`
configura corretamente `_root`, `_registry` e `_interval`.

**Passos:**
1. Instanciar `SkillRegistry()` e verificar `list_all() == []`
2. Instanciar `SkillWatcher(skills_root, registry, interval=0.1)`
3. Verificar `watcher._root == Path(skills_root)`
4. Verificar `watcher._registry is registry`

**Esperado:** Objetos inicializados com estado limpo.

---

## CT-2: test_watch_directory — scan_once detecta skills

**Objetivo:** Confirmar que `scan_once()` detecta criacao de skill em
diretorio com `SKILL.md`.

**Passos:**
1. Criar diretorio temporario com subdir `sample-skill/SKILL.md`
2. Chamar `scan_once()`
3. Verificar que `"sample-skill" in changes` e acao == `"added"`

**Esperado:** Skill detectada como "added".

---

## CT-3: test_on_change — Ciclo add → modify → remove

**Objetivo:** Validar o ciclo completo de eventos: adicao, modificacao e
remocao de skills via `scan_once()`.

**Passos:**
1. Criar skill com SKILL.md versao 0.1.0 → scan_once → "added"
2. Atualizar SKILL.md para versao 0.2.0 → scan_once → "modified"
3. Remover diretorio da skill → scan_once → "removed"

**Esperado:** Tres eventos distintos detectados em sequencia.

---

## CT-4: test_available — SkillValidator marca skill com erro de sintaxe

**Objetivo:** Garantir que `SkillValidator.validate()` detecta erro de
sintaxe Python e desabilita a skill sem lancar excecao.

**Passos:**
1. Criar `scripts/broken.py` com `def foo(`
2. Criar `SkillEntry(kind="python")` e validar
3. Verificar `entry.is_valid == False` e `entry.enabled == False`

**Esperado:** Skill marcada com erro, nao interrompe o sistema.
