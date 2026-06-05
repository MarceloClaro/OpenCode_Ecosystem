"""
Secure Loader -- Carregador de skills com verificacao de integridade e assinatura.

Implementa o fluxo de carga segura com modo DEV e modo SECURE.
Integra-se com: RegistryV2, sistema de hooks do OpenCode.
"""

import hashlib
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from .registry_v2 import RegistryV2, SkillManifest


class LoadMode(Enum):
    DEV = "dev"
    SECURE = "secure"


class LoadResult(Enum):
    OK = "ok"
    NO_MANIFEST = "no_manifest"
    INTEGRITY_FAILURE = "integrity_failure"
    UNTRUSTED_SOURCE = "untrusted_source"
    POLICY_VIOLATION = "policy_violation"
    VERSION_MISMATCH = "version_mismatch"


@dataclass
class SecureLoadReport:
    skill_name: str
    result: LoadResult
    manifest: Optional[SkillManifest] = None
    warnings: list[str] = field(default_factory=list)
    blocked: bool = False


class SecureLoader:
    """Carregador de skills com verificacao de integridade."""

    DESTRUCTIVE_COMMANDS = [
        "rm -rf", "rmdir /s", "del /f /s", "del /f /q",
        "DROP TABLE", "DROP DATABASE", "TRUNCATE",
        "git push --force", "git reset --hard",
        "chmod 777", "icacls /grant",
        "shutdown", "reboot", "format",
    ]

    def __init__(self, registry: RegistryV2, mode: LoadMode = LoadMode.DEV,
                 min_tier: int = 0, trusted_keys: Optional[list[str]] = None):
        self.registry = registry
        self.mode = mode
        self.min_tier = min_tier
        self.trusted_keys = trusted_keys or []

    def load_skill(self, skill_dir: str) -> SecureLoadReport:
        """Carrega uma skill com verificacao em 5 etapas."""
        skill_path = Path(skill_dir)
        skill_name = skill_path.name

        manifest_file = skill_path / "skill.manifest.json"
        if not manifest_file.exists():
            if self.mode == LoadMode.SECURE:
                return SecureLoadReport(
                    skill_name=skill_name,
                    result=LoadResult.NO_MANIFEST,
                    warnings=["Manifesto ausente em modo SECURE"],
                    blocked=True
                )
            return SecureLoadReport(
                skill_name=skill_name,
                result=LoadResult.NO_MANIFEST,
                warnings=["Manifesto ausente -- carregado em modo DEV sem verificacao"]
            )

        manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
        manifest = SkillManifest.from_dict(manifest_data)

        current_hash = self._compute_tree_hash(skill_path)
        if manifest.sha256 != current_hash:
            return SecureLoadReport(
                skill_name=skill_name,
                result=LoadResult.INTEGRITY_FAILURE,
                manifest=manifest,
                warnings=[f"Hash mismatch: stored={manifest.sha256[:16]}... current={current_hash[:16]}..."],
                blocked=True
            )

        if manifest.signature:
            if not self._verify_signature(manifest, skill_path):
                return SecureLoadReport(
                    skill_name=skill_name,
                    result=LoadResult.UNTRUSTED_SOURCE,
                    manifest=manifest,
                    warnings=["Assinatura invalida ou chave nao confiavel"],
                    blocked=True
                )

        policy_violations = self._check_policy(manifest, skill_path)
        if policy_violations:
            return SecureLoadReport(
                skill_name=skill_name,
                result=LoadResult.POLICY_VIOLATION,
                manifest=manifest,
                warnings=policy_violations,
                blocked=True
            )

        warnings = []
        if manifest.min_opencode_version:
            current = self._get_opencode_version()
            if current and self._version_less_than(current, manifest.min_opencode_version):
                warnings.append(
                    f"Skill requer OpenCode >= {manifest.min_opencode_version}, "
                    f"versao atual: {current}"
                )
                if self.mode == LoadMode.SECURE:
                    return SecureLoadReport(
                        skill_name=skill_name,
                        result=LoadResult.VERSION_MISMATCH,
                        manifest=manifest,
                        warnings=warnings,
                        blocked=True
                    )

        return SecureLoadReport(
            skill_name=skill_name,
            result=LoadResult.OK,
            manifest=manifest,
            warnings=warnings
        )

    def load_all_project_skills(self, project_root: str) -> list[SecureLoadReport]:
        """Carrega todas as skills de um projeto com verificacao."""
        reports = []
        project_path = Path(project_root)
        skill_dirs = [
            project_path / ".claude" / "skills",
            project_path / ".agents" / "skills",
            project_path / ".codex" / "skills",
        ]

        for skill_dir in skill_dirs:
            if skill_dir.exists():
                for skill_path in skill_dir.iterdir():
                    if skill_path.is_dir() and (skill_path / "SKILL.md").exists():
                        reports.append(self.load_skill(str(skill_path)))

        return reports

    def _compute_tree_hash(self, skill_path: Path) -> str:
        hasher = hashlib.sha256()
        for f in sorted(skill_path.rglob("*")):
            if f.is_file() and f.name != "skill.manifest.json":
                hasher.update(f.relative_to(skill_path).as_posix().encode())
                hasher.update(f.read_bytes())
        return hasher.hexdigest()

    def _verify_signature(self, manifest: SkillManifest, skill_path: Path) -> bool:
        if manifest.public_key not in self.trusted_keys and self.trusted_keys:
            return False
        try:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
            from cryptography.exceptions import InvalidSignature

            key_bytes = bytes.fromhex(manifest.public_key) if all(c in "0123456789abcdef" for c in manifest.public_key.lower()) else manifest.public_key.encode()
            public_key = Ed25519PublicKey.from_public_bytes(key_bytes[:32])
            sig_bytes = bytes.fromhex(manifest.signature)
            public_key.verify(sig_bytes, manifest.sha256.encode())
            return True
        except Exception:
            return False

    def _check_policy(self, manifest: SkillManifest, skill_path: Path) -> list[str]:
        violations = []
        for denied in manifest.denied_tools:
            for f in skill_path.rglob("*"):
                if f.is_file():
                    content = f.read_text(errors="ignore")
                    if denied in content:
                        violations.append(f"Ferramenta negada '{denied}' encontrada em {f.name}")
        return violations

    @staticmethod
    def _get_opencode_version() -> Optional[str]:
        try:
            import subprocess
            result = subprocess.run(["opencode", "--version"], capture_output=True, text=True, timeout=5)
            return result.stdout.strip()
        except Exception:
            return None

    @staticmethod
    def _version_less_than(v1: str, v2: str) -> bool:
        def parse(v: str) -> tuple:
            parts = v.replace("v", "").split(".")
            return tuple(int(p) for p in parts[:3])
        try:
            return parse(v1) < parse(v2)
        except Exception:
            return False
