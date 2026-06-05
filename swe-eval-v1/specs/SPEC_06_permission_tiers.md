# SPEC-06: Permission Tiers + Audit Log (P0)

> Lacuna 6: Niveis de aprovacao para comandos destrutivos + log de auditoria

## Tiers de Permissao

```
┌─────────────────────────────────────────────────────────┐
│ TIER  │ Nome         │ Permissoes                       │
├─────────────────────────────────────────────────────────┤
│   0   │ Observer     │ read-only: arquivos, git status   │
│   1   │ Contributor  │ read + write arquivos, git add    │
│   2   │ Operator     │ read + write + executar testes    │
│   3   │ Admin        │ bypass: requer confirmacao humana │
└─────────────────────────────────────────────────────────┘
```

## Comandos Destrutivos (requerem aprovacao humana)

| Comando | Nivel Minimo | Aprovacao |
|---------|-------------|-----------|
| `rm -rf`, `del /f /s` | Operator | SIM (humana) |
| `DROP TABLE`, `DELETE FROM` sem WHERE | Operator | SIM (humana) |
| `git push --force` | Operator | SIM (humana) |
| `git reset --hard` | Operator | SIM (humana) |
| `chmod 777`, `icacls /grant` | Operator | SIM (humana) |
| `pip install`, `npm install -g` | Contributor | SIM (humana) |
| Acesso a `.env`, `.key`, `.secret` | Operator | SIM (humana) |
| `shutdown`, `reboot` | Admin | SIM (humana) |
| `curl`/`wget` para dominio desconhecido | Operator | SIM (humana) |
| `eval()`, `exec()` dinamico | Contributor | SIM (humana) |

## Fluxo de Aprovacao

```
Comando interceptado pelo Hook
      │
      ▼
[1] Comando na blocklist? ──── SIM ──► BLOQUEADO (sem possibilidade de bypass)
      │ NAO
      ▼
[2] Tier do agente >= tier minimo do comando? ── NAO ─► BLOQUEADO (insufficient tier)
      │ SIM
      ▼
[3] Comando requer aprovacao humana? ── NAO ──► EXECUTA
      │ SIM
      ▼
[4] Exibe prompt: "Agente X quer executar: <comando>. Aprovar? (y/N)"
      │
      ├── NAO ──► BLOQUEADO (human denied) + LOG
      │
      └── SIM ──► EXECUTA + LOG (who, what, when, result)
```

## Estrutura do Audit Log

```sql
CREATE TABLE permission_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    agent_tier INTEGER NOT NULL,
    command TEXT NOT NULL,
    command_hash TEXT NOT NULL,
    was_destructive INTEGER NOT NULL DEFAULT 0,
    required_approval INTEGER NOT NULL DEFAULT 0,
    human_approved INTEGER DEFAULT NULL,
    result TEXT NOT NULL,
    duration_ms INTEGER,
    session_id TEXT NOT NULL
);
```
