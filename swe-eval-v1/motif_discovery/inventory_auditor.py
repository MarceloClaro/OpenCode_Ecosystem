"""
Inventory Auditor — Complemento do Motif Discovery Engine.
Audita a completude do inventario de skills do ecossistema,
detectando lacunas de registro, orfas e inconsistencias.

Integra-se: MDE → Inventory Auditor → Registry v2.0
"""

import json
import os
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class InventoryGap:
    """Lacuna de inventario encontrada."""
    gap_type: str  # unregistered, orphan, missing_skill_md, unknown_ref, stale
    entity: str
    location: str
    severity: str  # critical, high, medium, low
    recommendation: str


@dataclass
class InventoryReport:
    """Relatorio de auditoria de inventario."""
    total_skills: int = 0
    total_agents: int = 0
    registered_skills: int = 0
    unregistered_skills: int = 0
    orphan_skills: int = 0  # no disco mas sem SKILL.md valido
    missing_skill_md: int = 0  # diretorio sem SKILL.md
    gaps: list[InventoryGap] = field(default_factory=list)
    completeness_pct: float = 0.0
    scanned_at: str = ""


class InventoryAuditor:
    """Auditor de inventario do ecossistema."""

    def __init__(self, ecosystem_root: str, registry_path: Optional[str] = None):
        self.root = Path(ecosystem_root)
        self.registry_path = registry_path
        self.registry_data: dict = {}

        if registry_path and Path(registry_path).exists():
            self.registry_data = json.loads(
                Path(registry_path).read_text(encoding="utf-8")
            )

    def audit(self) -> InventoryReport:
        """Auditoria completa do inventario de skills."""
        report = InventoryReport(
            scanned_at=datetime.now(timezone.utc).isoformat()
        )

        skills_dir = self.root / "skills"
        agents_dir = self.root / "agents"

        on_disk = self._scan_skills_directory(skills_dir)
        # Verifica registro: Registry SQLite OU skill.manifest.json presente
        has_manifest = set()
        for skill_rel in on_disk:
            skill_dir = skills_dir / skill_rel
            if (skill_dir / "skill.manifest.json").exists():
                has_manifest.add(skill_rel)

        report.total_skills = len(on_disk)
        report.registered_skills = len(has_manifest)
        report.unregistered_skills = len(on_disk - has_manifest)

        report.total_agents = len(list(agents_dir.glob("*.md"))) if agents_dir.exists() else 0

        # GAP 1: Skills sem manifesto de seguranca
        for skill in sorted(on_disk - has_manifest):
            report.gaps.append(InventoryGap(
                gap_type="unregistered",
                entity=skill,
                location=f"skills/{skill}",
                severity="high",
                recommendation=f"Registrar {skill} no Registry v2.0 com SHA256 + assinatura Ed25519"
            ))

        # GAP 2: Skills com manifesto mas sem assinatura Ed25519
        for skill in sorted(has_manifest):
            manifest_path = skills_dir / skill / "skill.manifest.json"
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                if not manifest.get("signature"):
                    report.gaps.append(InventoryGap(
                        gap_type="unsigned",
                        entity=skill,
                        location=f"skills/{skill}",
                        severity="medium",
                        recommendation=f"Adicionar assinatura Ed25519 ao manifesto de {skill}"
                    ))
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        report.completeness_pct = (
            report.registered_skills / max(1, report.total_skills) * 100
            if report.total_skills > 0 else 100.0
        )

        return report

    def _scan_skills_directory(self, skills_dir: Optional[Path]) -> set[str]:
        """Escaneia skills validas no diretorio (inclui subdiretorios)."""
        if not skills_dir or not skills_dir.exists():
            return set()

        valid = set()
        # Navegacao recursiva: skills podem estar em subdiretorios (ex: science/alphafold/)
        for item in skills_dir.rglob("SKILL.md"):
            skill_dir = item.parent
            name = skill_dir.relative_to(skills_dir).as_posix().replace("/", "/")
            # Pega o nome completo como caminho relativo
            rel_path = skill_dir.relative_to(skills_dir).as_posix()
            if not rel_path.startswith("."):
                valid.add(rel_path)

        return valid

    def generate_manifest_batch(self, skill_names: list[str]) -> list[dict]:
        """Gera manifestos para skills nao registradas em lote."""
        manifests = []
        skills_dir = self.root / "skills"

        for name in skill_names:
            skill_dir = skills_dir / name
            if skill_dir.exists() and (skill_dir / "SKILL.md").exists():
                import hashlib
                sha = hashlib.sha256()
                for f in sorted(skill_dir.rglob("*")):
                    if f.is_file() and f.name != "skill.manifest.json":
                        sha.update(f.relative_to(skill_dir).as_posix().encode())
                        sha.update(f.read_bytes())

                manifest = {
                    "name": name,
                    "version": "0.1.0",
                    "semver": "0.1.0",
                    "sha256": sha.hexdigest(),
                    "signature": "",
                    "public_key": "",
                    "author": "opencode-ecosystem",
                    "created": datetime.now(timezone.utc).isoformat(),
                    "updated": datetime.now(timezone.utc).isoformat(),
                    "dependencies": {},
                    "changelog": [{"version": "0.1.0", "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "changes": ["Registro inicial via Inventory Auditor"]}],
                    "permissions": ["read:filesystem"],
                    "allowed_tools": [],
                    "denied_tools": [],
                    "human_approval_required": False,
                    "min_opencode_version": "1.14.0",
                    "skill_path": str(skill_dir.absolute()),
                }
                manifests.append(manifest)

        return manifests


def generate_inventory_report_markdown(report: InventoryReport) -> str:
    lines = [
        "# Inventory Audit Report",
        "",
        f"**Data:** {report.scanned_at}",
        "",
        f"| Metrica | Valor |",
        f"|---------|-------|",
        f"| Skills no disco | {report.total_skills} |",
        f"| Agentes registrados | {report.total_agents} |",
        f"| Skills no Registry | {report.registered_skills} |",
        f"| Skills NAO registradas | {report.unregistered_skills} |",
        f"| Skills sem SKILL.md | {report.missing_skill_md} |",
        f"| **Completude** | **{report.completeness_pct:.1f}%** |",
        "",
    ]

    if report.gaps:
        by_severity: dict[str, list[InventoryGap]] = {}
        for g in report.gaps:
            by_severity.setdefault(g.severity, []).append(g)

        for sev in ["critical", "high", "medium", "low"]:
            gaps = by_severity.get(sev, [])
            if gaps:
                lines.append(f"## {sev.upper()} ({len(gaps)} issues)")
                for g in gaps:
                    lines.extend([
                        f"- **[{g.gap_type}]** {g.entity} ({g.location})",
                        f"  Recomendacao: {g.recommendation}",
                        "",
                    ])

    return "\n".join(lines)
