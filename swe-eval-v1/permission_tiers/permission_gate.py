"""
Permission Tiers -- Modelo de permissoes com 4 niveis e aprovacao humana para comandos destrutivos.

Extende o sistema de permission: existente nos agentes OpenCode.
Integra-se com: agentes (frontmatter YAML), hooks do ecossistema.
"""

import hashlib
import json
import sqlite3
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from pathlib import Path
from typing import Optional


class PermissionTier(IntEnum):
    OBSERVER = 0
    CONTRIBUTOR = 1
    OPERATOR = 2
    ADMIN = 3


@dataclass
class CommandPolicy:
    pattern: str
    min_tier: PermissionTier
    requires_human_approval: bool
    description: str
    is_blocklist: bool = False


DEFAULT_POLICIES: list[CommandPolicy] = [
    CommandPolicy("rm -rf", PermissionTier.OPERATOR, True, "Remocao recursiva forcada"),
    CommandPolicy("rmdir /s", PermissionTier.OPERATOR, True, "Remocao recursiva de diretorio (Windows)"),
    CommandPolicy("del /f /s", PermissionTier.OPERATOR, True, "Delecao forcada recursiva (Windows)"),
    CommandPolicy("del /f /q", PermissionTier.OPERATOR, True, "Delecao silenciosa forcada (Windows)"),
    CommandPolicy("DROP TABLE", PermissionTier.OPERATOR, True, "Remocao de tabela do banco"),
    CommandPolicy("DROP DATABASE", PermissionTier.ADMIN, True, "Remocao de banco de dados"),
    CommandPolicy("TRUNCATE", PermissionTier.OPERATOR, True, "Truncamento de tabela"),
    CommandPolicy("DELETE FROM", PermissionTier.OPERATOR, True, "Delecao em massa sem WHERE"),
    CommandPolicy("git push --force", PermissionTier.OPERATOR, True, "Force push para remoto"),
    CommandPolicy("git reset --hard", PermissionTier.OPERATOR, True, "Reset hard do historico"),
    CommandPolicy("chmod 777", PermissionTier.OPERATOR, True, "Permissao total em arquivos"),
    CommandPolicy("icacls /grant", PermissionTier.OPERATOR, True, "Concessao de permissao (Windows)"),
    CommandPolicy("pip install", PermissionTier.CONTRIBUTOR, True, "Instalacao de pacotes Python"),
    CommandPolicy("npm install -g", PermissionTier.OPERATOR, True, "Instalacao global de pacotes npm"),
    CommandPolicy("shutdown", PermissionTier.ADMIN, True, "Desligamento do sistema"),
    CommandPolicy("reboot", PermissionTier.ADMIN, True, "Reinicializacao do sistema"),
    CommandPolicy("format", PermissionTier.ADMIN, True, "Formatacao de disco"),
    CommandPolicy("Set-ExecutionPolicy", PermissionTier.ADMIN, True, "Alteracao de politica de execucao"),
    CommandPolicy("sudo ", PermissionTier.ADMIN, True, "Execucao como superusuario"),
    CommandPolicy("eval(", PermissionTier.CONTRIBUTOR, True, "Execucao dinamica de codigo"),
    CommandPolicy("exec(", PermissionTier.CONTRIBUTOR, True, "Execucao dinamica de codigo"),
    CommandPolicy("__import__(", PermissionTier.CONTRIBUTOR, True, "Import dinamico"),
]


class AuditLogger:
    """Logger de auditoria para o sistema de permissoes."""

    SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS permission_audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        agent_name TEXT NOT NULL,
        agent_tier INTEGER NOT NULL,
        command TEXT NOT NULL,
        command_hash TEXT NOT NULL,
        matched_policy TEXT,
        was_destructive INTEGER NOT NULL DEFAULT 0,
        required_approval INTEGER NOT NULL DEFAULT 0,
        human_approved INTEGER DEFAULT NULL,
        result TEXT NOT NULL,
        duration_ms INTEGER,
        session_id TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_audit_agent ON permission_audit_log(agent_name);
    CREATE INDEX IF NOT EXISTS idx_audit_result ON permission_audit_log(result);
    CREATE INDEX IF NOT EXISTS idx_audit_session ON permission_audit_log(session_id);
    """

    def __init__(self, db_path: str = "permission_audit.db"):
        self.db_path = db_path
        with sqlite3.connect(db_path) as conn:
            conn.executescript(self.SCHEMA_SQL)

    def log(self, agent_name: str, agent_tier: int, command: str,
            matched_policy: Optional[str], was_destructive: bool,
            required_approval: bool, result: str, session_id: str,
            human_approved: Optional[bool] = None, duration_ms: int = 0):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO permission_audit_log
                (timestamp, agent_name, agent_tier, command, command_hash,
                 matched_policy, was_destructive, required_approval,
                 human_approved, result, duration_ms, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now(timezone.utc).isoformat(),
                agent_name, agent_tier,
                command[:500],
                hashlib.sha256(command.encode()).hexdigest()[:16],
                matched_policy,
                1 if was_destructive else 0,
                1 if required_approval else 0,
                1 if human_approved else (0 if human_approved is False else None),
                result, duration_ms, session_id
            ))

    def get_violations(self, agent_name: Optional[str] = None, limit: int = 50) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            if agent_name:
                rows = conn.execute(
                    """SELECT * FROM permission_audit_log
                       WHERE agent_name = ? AND result = 'BLOCKED'
                       ORDER BY timestamp DESC LIMIT ?""",
                    (agent_name, limit)
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT * FROM permission_audit_log
                       WHERE result = 'BLOCKED'
                       ORDER BY timestamp DESC LIMIT ?""",
                    (limit,)
                ).fetchall()

        cols = ["id", "timestamp", "agent_name", "agent_tier", "command",
                "command_hash", "matched_policy", "was_destructive",
                "required_approval", "human_approved", "result", "duration_ms", "session_id"]
        return [dict(zip(cols, r)) for r in rows]

    def get_stats(self, session_id: Optional[str] = None) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            where = f"WHERE session_id = '{session_id}'" if session_id else ""
            total = conn.execute(f"SELECT COUNT(*) FROM permission_audit_log {where}").fetchone()[0]
            blocked = conn.execute(f"SELECT COUNT(*) FROM permission_audit_log {where} AND result = 'BLOCKED'").fetchone()[0]
            approved = conn.execute(f"SELECT COUNT(*) FROM permission_audit_log {where} AND human_approved = 1").fetchone()[0]
            denied = conn.execute(f"SELECT COUNT(*) FROM permission_audit_log {where} AND human_approved = 0").fetchone()[0]
            return {
                "total_commands": total,
                "blocked": blocked,
                "human_approved": approved,
                "human_denied": denied,
                "approval_rate": approved / (approved + denied) if (approved + denied) > 0 else 0.0
            }


class PermissionGate:
    """Motor de controle de permissoes com tiers e aprovacao humana."""

    def __init__(self, policies: Optional[list[CommandPolicy]] = None,
                 auditor: Optional[AuditLogger] = None,
                 interactive: bool = True,
                 session_id: Optional[str] = None):
        self.policies = policies or DEFAULT_POLICIES
        self.auditor = auditor or AuditLogger()
        self.interactive = interactive
        self.session_id = session_id or f"session-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    def check_command(self, command: str, agent_name: str, agent_tier: int) -> dict:
        """Verifica se um comando pode ser executado pelo agente."""
        matched_policy = self._match_policy(command)

        if matched_policy and matched_policy.is_blocklist:
            self.auditor.log(agent_name, agent_tier, command,
                           matched_policy.description, True, False,
                           "BLOCKED", self.session_id)
            return {"allowed": False, "reason": f"Comando na blocklist: {matched_policy.description}"}

        if matched_policy is None:
            result = {"allowed": True, "reason": "Comando nao requer politica especial"}
            self.auditor.log(agent_name, agent_tier, command, None,
                           False, False, "ALLOWED", self.session_id)
            return result

        if agent_tier < matched_policy.min_tier:
            result = {
                "allowed": False,
                "reason": f"Tier insuficiente: {PermissionTier(agent_tier).name} < {matched_policy.min_tier.name}"
            }
            self.auditor.log(agent_name, agent_tier, command,
                           matched_policy.description, True, matched_policy.requires_human_approval,
                           "BLOCKED", self.session_id)
            return result

        if matched_policy.requires_human_approval:
            if self.interactive:
                approved = self._request_human_approval(agent_name, command, matched_policy.description)
                self.auditor.log(agent_name, agent_tier, command,
                               matched_policy.description, True, True,
                               "APPROVED" if approved else "DENIED",
                               self.session_id, human_approved=approved)
                if approved:
                    return {"allowed": True, "reason": "Aprovado por humano"}
                else:
                    return {"allowed": False, "reason": "Negado por humano"}
            else:
                self.auditor.log(agent_name, agent_tier, command,
                               matched_policy.description, True, True,
                               "PENDING_APPROVAL", self.session_id)
                return {"allowed": False, "reason": "Requer aprovacao humana (modo nao-interativo)"}

        self.auditor.log(agent_name, agent_tier, command,
                       matched_policy.description, True, False,
                       "ALLOWED", self.session_id)
        return {"allowed": True, "reason": f"Permitido (tier={PermissionTier(agent_tier).name})"}

    def _match_policy(self, command: str) -> Optional[CommandPolicy]:
        cmd_lower = command.lower()
        for policy in self.policies:
            if policy.pattern.lower() in cmd_lower:
                return policy
        return None

    def _request_human_approval(self, agent_name: str, command: str, description: str) -> bool:
        print(f"\n{'='*60}")
        print(f"  SOLICITACAO DE APROVACAO")
        print(f"  Agente: {agent_name}")
        print(f"  Comando: {command}")
        print(f"  Risco: {description}")
        print(f"{'='*60}")
        try:
            response = input("  Aprovar execucao? (y/N): ").strip().lower()
            return response in ("y", "yes", "sim", "s")
        except (EOFError, KeyboardInterrupt):
            return False

    def add_policy(self, policy: CommandPolicy):
        self.policies.append(policy)

    def load_policies_from_file(self, path: str):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for p in data.get("policies", []):
            self.policies.append(CommandPolicy(
                pattern=p["pattern"],
                min_tier=PermissionTier[p["min_tier"]],
                requires_human_approval=p.get("requires_human_approval", True),
                description=p.get("description", ""),
                is_blocklist=p.get("is_blocklist", False)
            ))


def generate_policies_json(output_path: str):
    """Exporta politicas padrao para JSON editavel."""
    policies = [{
        "pattern": p.pattern,
        "min_tier": p.min_tier.name,
        "requires_human_approval": p.requires_human_approval,
        "description": p.description,
        "is_blocklist": p.is_blocklist
    } for p in DEFAULT_POLICIES]
    Path(output_path).write_text(json.dumps({"policies": policies}, indent=2, ensure_ascii=False), encoding="utf-8")
