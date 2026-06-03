---
name: hot-reload-skills
version: "1.0.0"
kind: python
category: system
affinity: {autoevolve: 0.95, manus-evolve: 0.90, code-graphrag: 0.80}
---

# Hot-Reload Skill System — Carregamento Dinamico sem Reinicializacao

## Origem
Extraido de **SandeClaw** (specs/architecture.md secao 2.3, PRD.md metricas).
SandeClaw usa sistema de plugins onde skills sao arquivos Markdown na pasta
`.agents/skills/` e o sistema detecta alteracoes em tempo real.

## Como Funciona
File watcher baseado em polling cross-platform que monitora o diretorio
de skills. A cada ciclo (2s default), compara mtime dos arquivos com
o estado conhecido e emite eventos (added/modified/removed).

```
skills/                     SkillWatcher (polling 2s)
  ├── skill-a/SKILL.md  ──>   ├── parse SKILL.md (frontmatter + metadata)
  ├── skill-b/SKILL.md  ──>   ├── validate Python (compile() sem executar)
  └── skill-c/SKILL.md  ──>   └── registry.register() / unregister()
                                      |
                              SkillRegistry (thread-safe)
                                      |
                              callbacks: on_add, on_remove, on_error
```

**Degradacao graciosa**: Se uma skill tem erro de sintaxe, e marcada com
`.error` e `.enabled=False`, mas o sistema continua operando com as demais.

## Valor para OpenCode
- **AutoEvolve/ManusEvolve**: Skills geradas entram em operacao imediatamente
- **Desenvolvimento**: Editar SKILL.md e ver efeito sem reiniciar o agente
- **Resiliencia**: Skill quebrada nao derruba o ecossistema (104+ skills)
- **Observabilidade**: Callbacks permitem log, metricas, alertas

## Uso
```python
from skills.hot_reload_skills.scripts.skill_watcher import (
    create_watcher_for_ecosystem, SkillRegistry
)

watcher, registry = create_watcher_for_ecosystem()
registry.on("on_add", lambda e: print(f"Nova skill: {e.name}"))
registry.on("on_error", lambda e: print(f"Erro em {e.name}: {e.error}"))

enabled = registry.list_enabled()
print(f"{len(enabled)} skills ativas")
```

## Ficheiros
- `scripts/skill_watcher.py` — implementacao completa (270 linhas)
  - `SkillRegistry` — registro thread-safe com callbacks
  - `SkillParser` — extrai metadados de SKILL.md
  - `SkillValidator` — valida sintaxe Python sem executar
  - `SkillWatcher` — polling cross-platform
