# SPEC-05: ArtifactSyncEngine (P2)

> Lacuna 5: Sincronizacao bidirecional spec↔plan↔tasks↔tests↔code com invalidação em cascata

## Grafo de Dependencias

```
    spec.md ◄──────────────────────────────────────┐
      │                                             │
      ├──► plan.md                                  │
      │     │                                       │
      │     ├──► tasks.md                           │
      │     │     │                                 │
      │     │     ├──► impl/auth.py                  │
      │     │     │     │                           │
      │     │     │     └──► tests/test_auth.py      │
      │     │     │                                 │
      │     │     ├──► impl/database.py              │
      │     │     │     │                           │
      │     │     │     └──► tests/test_db.py        │
      │     │     │                                 │
      │     │     └──► impl/api.py                   │
      │     │           │                           │
      │     │           └──► tests/test_api.py       │
      │     │                                       │
      │     └──► ADR (DecisionNode)                  │
      │                                             │
      └──► contracts.json ──────────────────────────┘
```

## Regras de Invalidacao

| Evento | Artefatos Invalidados | Acao |
|--------|----------------------|------|
| spec.md modificado | plan.md, tasks.md, contracts.json | Regenerar plan e tasks |
| plan.md modificado | tasks.md | Regenerar tasks |
| tasks.md modificado | -- | Apenas sync status |
| codigo modificado (sem spec) | contracts.json | Marcar spec como "potencialmente desatualizada" |
| teste falha | contracts.json | Alerta: spec ou codigo precisa correcao |
| ADR alterada | plan.md, tasks.md | Re-avaliar impacto |

## Estados de Sincronizacao

```
┌────────────────────────────────────────────┐
│ ESTADO          │ Significado              │
├────────────────────────────────────────────┤
│ SYNCED          │ Artefato alinhado        │
│ STALE           │ Fonte mudou, precisa reg │
│ REGENERATING    │ Sendo reconstruido       │
│ CONFLICT        │ Mudanca em ambos os lados│
│ ORPHAN          │ Fonte foi removida       │
└────────────────────────────────────────────┘
```

## API do SyncEngine

```python
class ArtifactSyncEngine:
    def register_artifact(self, path: str, artifact_type: str) -> None
    def set_dependency(self, source: str, target: str) -> None
    def mark_modified(self, path: str) -> list[str]  # retorna artefatos invalidados
    def get_status(self, path: str) -> SyncStatus
    def regenerate(self, path: str) -> bool
    def validate_chain(self, root_spec: str) -> ValidationReport
```
