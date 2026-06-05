# Diagrama de Estados do Pipeline Reversa

## Máquina de Estados (Formal)

```
┌─────────────────────────────────────────────────────────────────┐
│                      PIPELINE STATE MACHINE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐     ┌──────────┐     ┌───────────┐     ┌────────┐ │
│  │ PENDING │────►│ RUNNING  │────►│ COMPLETED │────►│VALIDATED│ │
│  │   (0)   │     │   (1)    │     │   (2)     │     │  (3)   │ │
│  └─────────┘     └────┬─────┘     └─────┬─────┘     └───┬────┘ │
│                       │                  │                │      │
│                       │    ┌────────┐   │                │      │
│                       ├───►│ FAILED │◄──┘                │      │
│                       │    │  (4)   │                    │      │
│                       │    └───┬────┘                    │      │
│                       │        │                         │      │
│                       │        ▼                         │      │
│                       │  ┌───────────┐                   │      │
│                       └──►│ROLLED_BACK│◄──────────────────┘      │
│                          │   (5)     │                          │
│                          └───────────┘                          │
│                                                                  │
│  ┌─────────┐     ┌──────────┐                                    │
│  │ SKIPPED │────►│ BLOCKED  │────► RUNNING (após desbloqueio)    │
│  │   (6)   │     │   (7)    │                                    │
│  └─────────┘     └──────────┘                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Estados por Fase do Pipeline

### Fase 1: Scout (Mapeamento)

```
PENDING → RUNNING → COMPLETED → VALIDATED
                ↘ FAILED → ROLLED_BACK → RUNNING (retry)
```

### Fase 2: Archaeologist (Análise)

```
PENDING → RUNNING → COMPLETED → VALIDATED
         ↙           ↘
    BLOCKED          FAILED
    (dep: scout)      ↕
                    ROLLED_BACK → RUNNING (retry)
```

### Fase 3: Detective (Lógica de Negócio)

```
PENDING → RUNNING → COMPLETED → VALIDATED
         ↙           ↘
    BLOCKED          FAILED
    (dep: arch)
```

### Fase 4: Data Master (Dados)

```
PENDING → RUNNING → COMPLETED → VALIDATED
```

### Fase 5: Design System (UI/UX)

```
PENDING → RUNNING → COMPLETED → VALIDATED
```

### Fase 6: Writer (Documentação)

```
PENDING → RUNNING → COMPLETED → VALIDATED
```

### Fase 7: Reviewer (Qualidade)

```
PENDING → RUNNING → COMPLETED
                ↘ FAILED → ROLLED_BACK → RUNNING (review)
```

### Pipeline Completo

```
Scout → Arch → Detect → Data → Design → Write → Review
───────────────────────────────────────────────────────►
  Cada fase: PENDING → RUNNING → COMPLETED → VALIDATED
                                        ↘ FAILED → retry
```

## Tabela de Transições

| De | Para | Condição | Ação |
|----|------|----------|------|
| PENDING | RUNNING | Dependências satisfeitas | Iniciar processamento |
| RUNNING | COMPLETED | Sucesso | Salvar resultado |
| RUNNING | FAILED | Erro capturado | Registrar erro + stack |
| RUNNING | BLOCKED | Dep não resolvida | Aguardar dep |
| COMPLETED | VALIDATED | Revisão aprovada | Avançar pipeline |
| COMPLETED | FAILED | Revisão rejeitada | Registrar motivo |
| FAILED | RUNNING | Retry | Re-processar |
| FAILED | ROLLED_BACK | Rollback | Restaurar checkpoint |
| VALIDATED | RUNNING | Revisão necessária | Re-abrir fase |
| BLOCKED | RUNNING | Dep resolvida | Continuar |
| SKIPPED | — | Fase não aplicável | Avançar |
| QUALQUER | SKIPPED | Skip explícito | Pular fase |

## Schema SQLite

```sql
-- Tabela principal de estados
CREATE TABLE pipeline_states (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id TEXT NOT NULL,          -- ID do pipeline (UUID)
    phase       TEXT NOT NULL,           -- Nome da fase
    state       TEXT NOT NULL,           -- Estado atual
    previous    TEXT,                     -- Estado anterior
    started_at  TEXT NOT NULL,           -- ISO 8601
    ended_at    TEXT,                     -- ISO 8601
    duration_ms INTEGER,                 -- Milissegundos
    error       TEXT,                     -- Mensagem de erro
    metadata    TEXT DEFAULT '{}',        -- JSON context
    created_at  TEXT DEFAULT (datetime('now'))
);

-- Tabela de checkpoints
CREATE TABLE pipeline_checkpoints (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id TEXT NOT NULL,
    phase       TEXT NOT NULL,
    state       TEXT NOT NULL,
    snapshot    TEXT NOT NULL,            -- JSON com dados do checkpoint
    created_at  TEXT DEFAULT (datetime('now'))
);

-- Tabela de dependências entre fases
CREATE TABLE pipeline_dependencies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id TEXT NOT NULL,
    phase       TEXT NOT NULL,
    depends_on  TEXT NOT NULL,           -- Fase da qual depende
    resolved    INTEGER DEFAULT 0,       -- 0=pendente, 1=resolvida
    created_at  TEXT DEFAULT (datetime('now'))
);

-- Índices
CREATE INDEX idx_states_pipeline ON pipeline_states(pipeline_id);
CREATE INDEX idx_states_phase ON pipeline_states(phase);
CREATE INDEX idx_checkpoints_pipeline ON pipeline_checkpoints(pipeline_id);
```

## Exemplo de Uso

```python
# Criar pipeline
pipe = Pipeline("reversa-session-001")
pipe.add_phase("scout")      # PENDING
pipe.add_phase("archaeologist", depends_on=["scout"])

# Avançar scout
pipe.start("scout")          # RUNNING
# ... análise ...
pipe.complete("scout")       # COMPLETED
pipe.validate("scout")       # VALIDATED

# Archaeologist pode começar
pipe.start("archaeologist")  # RUNNING

# Verificar estado
pipe.status()
# Pipeline: reversa-session-001
#   scout:         VALIDATED ✓
#   archaeologist: RUNNING ⟳
#   detective:     BLOCKED 🔒 (dep: archaeologist)

# Rollback se necessário
pipe.rollback("archaeologist")
# archaeologist: ROLLED_BACK ← RUNNING

# Retry
pipe.retry("archaeologist")  # RUNNING
```
