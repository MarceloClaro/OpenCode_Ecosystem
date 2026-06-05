"""
Registry v2.0 -- Registro versionado de skills com SemVer + SHA256 + assinatura.

Migracao do nexus/skills_registry.json (v1) para schema SQLite com integridade.
Integra-se com: nexus/skills_registry.py, agents/registry.json
"""

import hashlib
import json
import sqlite3
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

try:
    import semver
    HAS_SEMVER = True
except ImportError:
    HAS_SEMVER = False


@dataclass
class SkillManifest:
    name: str
    version: str
    semver: str
    sha256: str
    signature: str = ""
    public_key: str = ""
    author: str = "opencode-ecosystem"
    created: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    dependencies: dict = field(default_factory=dict)
    changelog: list = field(default_factory=list)
    permissions: list = field(default_factory=list)
    allowed_tools: list = field(default_factory=list)
    denied_tools: list = field(default_factory=list)
    human_approval_required: bool = False
    min_opencode_version: str = "1.14.0"
    skill_path: str = ""
    file_count: int = 0
    total_bytes: int = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SkillManifest":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class RegistryV2:
    """Registry v2.0 com SQLite, hashes e controle de versao."""

    SCHEMA_SQL = """
    CREATE TABLE IF NOT EXISTS skills (
        name TEXT PRIMARY KEY,
        version TEXT NOT NULL,
        semver TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        signature TEXT DEFAULT '',
        public_key TEXT DEFAULT '',
        author TEXT DEFAULT 'opencode-ecosystem',
        created TEXT NOT NULL,
        updated TEXT NOT NULL,
        dependencies TEXT DEFAULT '{}',
        changelog TEXT DEFAULT '[]',
        permissions TEXT DEFAULT '[]',
        allowed_tools TEXT DEFAULT '[]',
        denied_tools TEXT DEFAULT '[]',
        human_approval_required INTEGER DEFAULT 0,
        min_opencode_version TEXT DEFAULT '1.14.0',
        skill_path TEXT DEFAULT '',
        file_count INTEGER DEFAULT 0,
        total_bytes INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS skill_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_name TEXT NOT NULL,
        file_path TEXT NOT NULL,
        sha256 TEXT NOT NULL,
        file_bytes INTEGER DEFAULT 0,
        FOREIGN KEY (skill_name) REFERENCES skills(name)
    );

    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        skill_name TEXT NOT NULL,
        event_type TEXT NOT NULL,
        old_version TEXT,
        new_version TEXT,
        description TEXT,
        FOREIGN KEY (skill_name) REFERENCES skills(name)
    );

    CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(name);
    CREATE INDEX IF NOT EXISTS idx_audit_skill ON audit_log(skill_name);
    CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
    """

    def __init__(self, db_path: str = "skills_registry_v2.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(self.SCHEMA_SQL)

    def register_skill(self, skill_dir: str, manifest: Optional[SkillManifest] = None) -> SkillManifest:
        """Registra uma skill no registry v2 com hash de integridade."""
        skill_path = Path(skill_dir)
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill directory not found: {skill_dir}")

        if manifest is None:
            manifest = self._build_manifest(skill_path)

        manifest.sha256 = self._compute_tree_hash(skill_path)
        manifest.file_count, manifest.total_bytes = self._count_files(skill_path)
        manifest.skill_path = str(skill_path.absolute())

        self._validate_semver(manifest.semver)

        self._write_manifest_file(skill_path, manifest)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO skills
                (name, version, semver, sha256, signature, public_key, author,
                 created, updated, dependencies, changelog, permissions,
                 allowed_tools, denied_tools, human_approval_required,
                 min_opencode_version, skill_path, file_count, total_bytes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                manifest.name, manifest.version, manifest.semver, manifest.sha256,
                manifest.signature, manifest.public_key, manifest.author,
                manifest.created, manifest.updated,
                json.dumps(manifest.dependencies), json.dumps(manifest.changelog),
                json.dumps(manifest.permissions), json.dumps(manifest.allowed_tools),
                json.dumps(manifest.denied_tools),
                1 if manifest.human_approval_required else 0,
                manifest.min_opencode_version, manifest.skill_path,
                manifest.file_count, manifest.total_bytes
            ))

            self._register_files(conn, manifest.name, skill_path)
            self._log_event(conn, manifest.name, "REGISTER",
                          old_version=None, new_version=manifest.version,
                          description=f"Registered v{manifest.version}")

        return manifest

    def verify_integrity(self, skill_name: str) -> bool:
        """Verifica se a skill no disco bate com o hash registrado."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT sha256, skill_path FROM skills WHERE name = ?", (skill_name,)
            ).fetchone()

        if not row:
            return False

        stored_hash, skill_path = row
        current_hash = self._compute_tree_hash(Path(skill_path))
        return stored_hash == current_hash

    def get_manifest(self, skill_name: str) -> Optional[SkillManifest]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM skills WHERE name = ?", (skill_name,)
            ).fetchone()

        if not row:
            return None

        cols = [desc[0] for desc in conn.execute("SELECT * FROM skills LIMIT 0").description]
        data = dict(zip(cols, row))
        data["dependencies"] = json.loads(data["dependencies"])
        data["changelog"] = json.loads(data["changelog"])
        data["permissions"] = json.loads(data["permissions"])
        data["allowed_tools"] = json.loads(data["allowed_tools"])
        data["denied_tools"] = json.loads(data["denied_tools"])
        data["human_approval_required"] = bool(data["human_approval_required"])
        return SkillManifest.from_dict(data)

    def list_all(self) -> list[SkillManifest]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT name FROM skills ORDER BY name").fetchall()
        result: list[SkillManifest] = []
        for r in rows:
            m = self.get_manifest(r[0])
            if m is not None:
                result.append(m)
        return result

    def check_updates(self) -> list[dict]:
        """Verifica skills que precisam de atualizacao (hash mudou)."""
        stale = []
        for skill in self.list_all():
            if skill.skill_path and Path(skill.skill_path).exists():
                if not self.verify_integrity(skill.name):
                    stale.append({
                        "name": skill.name,
                        "current_version": skill.version,
                        "stored_hash": skill.sha256,
                        "current_hash": self._compute_tree_hash(Path(skill.skill_path)),
                        "action": "requires_resign"
                    })
        return stale

    def get_audit_trail(self, skill_name: str, limit: int = 50) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                """SELECT timestamp, event_type, old_version, new_version, description
                   FROM audit_log WHERE skill_name = ?
                   ORDER BY timestamp DESC LIMIT ?""",
                (skill_name, limit)
            ).fetchall()
        return [dict(zip(["timestamp", "event_type", "old_version", "new_version", "description"], r)) for r in rows]

    def _build_manifest(self, skill_path: Path) -> SkillManifest:
        manifest_file = skill_path / "skill.manifest.json"
        if manifest_file.exists():
            data = json.loads(manifest_file.read_text(encoding="utf-8"))
            return SkillManifest.from_dict(data)

        skill_md = skill_path / "SKILL.md"
        if not skill_md.exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_path}")

        name = skill_path.name
        return SkillManifest(name=name, version="0.1.0", semver="0.1.0", sha256="")

    def _compute_tree_hash(self, skill_path: Path) -> str:
        """SHA256 da arvore completa de arquivos da skill (exclui manifest)."""
        hasher = hashlib.sha256()
        for f in sorted(skill_path.rglob("*")):
            if f.is_file() and f.name != "skill.manifest.json":
                hasher.update(f.relative_to(skill_path).as_posix().encode())
                hasher.update(f.read_bytes())
        return hasher.hexdigest()

    def _count_files(self, skill_path: Path) -> tuple[int, int]:
        files = [f for f in skill_path.rglob("*") if f.is_file()]
        return len(files), sum(f.stat().st_size for f in files)

    def _register_files(self, conn: sqlite3.Connection, skill_name: str, skill_path: Path):
        conn.execute("DELETE FROM skill_files WHERE skill_name = ?", (skill_name,))
        for f in skill_path.rglob("*"):
            if f.is_file():
                conn.execute(
                    "INSERT INTO skill_files (skill_name, file_path, sha256, file_bytes) VALUES (?, ?, ?, ?)",
                    (skill_name, f.relative_to(skill_path).as_posix(),
                     hashlib.sha256(f.read_bytes()).hexdigest(), f.stat().st_size)
                )

    def _log_event(self, conn: sqlite3.Connection, skill_name: str, event_type: str,
                   old_version: Optional[str], new_version: Optional[str], description: str):
        conn.execute(
            "INSERT INTO audit_log (timestamp, skill_name, event_type, old_version, new_version, description) VALUES (?, ?, ?, ?, ?, ?)",
            (datetime.now(timezone.utc).isoformat(), skill_name, event_type,
             old_version, new_version, description)
        )

    @staticmethod
    def _validate_semver(version: str):
        if not HAS_SEMVER:
            return
        try:
            semver.Version.parse(version)
        except ValueError:
            raise ValueError(f"Invalid SemVer: {version}")

    @staticmethod
    def _write_manifest_file(skill_path: Path, manifest: SkillManifest):
        manifest_file = skill_path / "skill.manifest.json"
        manifest_file.write_text(
            json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8"
        )


def migrate_v1_to_v2(v1_registry_path: str, v2_db_path: str = "skills_registry_v2.db") -> int:
    """Migra do registry v1 (JSON) para v2 (SQLite)."""
    v1_data = json.loads(Path(v1_registry_path).read_text(encoding="utf-8"))
    registry = RegistryV2(v2_db_path)
    count = 0

    for skill_entry in v1_data if isinstance(v1_data, list) else v1_data.get("skills", []):
        name = skill_entry.get("name") or skill_entry.get("skill_name", "unknown")
        version = skill_entry.get("version", "0.1.0")
        manifest = SkillManifest(
            name=name, version=version, semver=version, sha256="migrated",
            skill_path=skill_entry.get("path", ""),
            file_count=skill_entry.get("file_count", 0),
            total_bytes=skill_entry.get("total_bytes", 0)
        )
        registry.register_skill(Path(skill_entry.get("path", ".")), manifest)
        count += 1

    return count
