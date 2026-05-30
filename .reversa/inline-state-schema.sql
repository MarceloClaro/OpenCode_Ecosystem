-- Schema para Machine States (P3) do Pipeline Reversa
-- Inspirado pelo MiroFish SimulationStatus + Project

CREATE TABLE IF NOT EXISTS pipeline_states (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id TEXT NOT NULL,
    phase       TEXT NOT NULL,
    state       TEXT NOT NULL DEFAULT 'PENDING',
    previous    TEXT,
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    duration_ms INTEGER,
    error       TEXT,
    metadata    TEXT DEFAULT '{}',
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pipeline_checkpoints (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id TEXT NOT NULL,
    phase       TEXT NOT NULL,
    state       TEXT NOT NULL,
    snapshot    TEXT NOT NULL,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS pipeline_dependencies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    pipeline_id TEXT NOT NULL,
    phase       TEXT NOT NULL,
    depends_on  TEXT NOT NULL,
    resolved    INTEGER DEFAULT 0,
    created_at  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_states_pipeline ON pipeline_states(pipeline_id);
CREATE INDEX IF NOT EXISTS idx_states_phase ON pipeline_states(phase);
CREATE INDEX IF NOT EXISTS idx_checkpoints_pipeline ON pipeline_checkpoints(pipeline_id);

-- Seed: registro simbólico inicial para demonstrar funcionamento
INSERT INTO pipeline_states (pipeline_id, phase, state, started_at, metadata)
VALUES ('demo-initialization', 'system', 'COMPLETED', datetime('now'),
        '{"event": "Machine States schema created", "date": "2026-05-17"}');
