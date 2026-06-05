---
name: state
description: >
  Gerencia a máquina de estados do pipeline Reversa. Permite visualizar,
  avançar e diagnosticar o estado de cada fase do pipeline de engenharia
  reversa com persistência automática.
usage: /state <subcommand> [args]
subcommands:
  - status: Mostra estado atual de todas as fases do pipeline
  - advance <phase> [state]: Avança fase para o próximo estado
  - retry <phase>: Tenta novamente fase com falha
  - log [phase]: Mostra histórico de transições
  - reset: Reseta todo o pipeline (requer confirmação)
examples:
  - /state status
  - /state advance scout completed
  - /state retry archaeologist
  - /state log scout
---

# /state

Comando de máquina de estados do pipeline Reversa.

## Subcomandos

### /state status

Exibe o mapa de estados atual do pipeline:

```
📊 Pipeline: reversa-20260517-abc123
─────────────────────────────────────────
Scout (scout):         VALIDATED     ✓  12s
Archaeologist (arch):  COMPLETED     ✓  45s
Detective (detect):    RUNNING       ⟳  23s
Data Master (data):    PENDING       ○
Design System (design): PENDING      ○
Writer (write):         BLOCKED      🔒  aguardando: design
Reviewer (review):      BLOCKED      🔒  aguardando: write

Progresso: 4/8 fases (50%)
Duração total: 1min 20s
Último erro: Nenhum
```

### /state advance <phase> [state]

Avança manualmente uma fase para um estado:

```
/state advance scout completed
  → scout: RUNNING → COMPLETED (2.3s)
  → archaeologist: BLOCKED → RUNNING (dep satisfeita)
```

### /state retry <phase>

Retenta fase que falhou:

```
/state retry archaeologist
  → arch: FAILED → ROLLED_BACK → RUNNING (retry #1)
```

### /state log [phase]

Histórico de transições:

```
/state log scout
  Histórico de scout:
  00:00:00 → PENDING        Criado
  00:00:01 → RUNNING        Iniciado
  00:00:03 → COMPLETED      Mapeamento concluído
  00:00:05 → VALIDATED      Revisão aprovada
```

### /state reset

Reinicia o pipeline do zero:

```
/state reset
  ⚠️ Confirma reset do pipeline 'reversa-20260517-abc123'?
  Todos os estados serão reiniciados.
  Digite /state reset --force para confirmar.

/state reset --force
  ✅ Pipeline resetado. Todas as fases em PENDING.
```

## Integração Automática

A máquina de estados é atualizada automaticamente quando:

- `/reversa start` → estado `PENDING` → `RUNNING`
- Agente conclui → `COMPLETED`
- Agente falha → `FAILED`
- Próximo agente inicia → dependência satisfeita
