"""
ArtifactSyncEngine -- Sincronizacao bidirecional spec↔plan↔tasks↔tests↔code.

Mantem artefatos alinhados com invalidação em cascata e regeneracao seletiva.
Integra-se com: SDD+TDD Pipeline, DecisionNode, SpecDriftDetector.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class SyncStatus(Enum):
    SYNCED = "synced"
    STALE = "stale"
    REGENERATING = "regenerating"
    CONFLICT = "conflict"
    ORPHAN = "orphan"


class ArtifactType(Enum):
    SPEC = "spec"
    PLAN = "plan"
    TASKS = "tasks"
    CODE = "code"
    TEST = "test"
    ADR = "adr"
    CONTRACT = "contract"


INVALIDATION_RULES: dict[ArtifactType, list[ArtifactType]] = {
    ArtifactType.SPEC: [ArtifactType.PLAN, ArtifactType.TASKS, ArtifactType.CONTRACT],
    ArtifactType.PLAN: [ArtifactType.TASKS],
    ArtifactType.TASKS: [],
    ArtifactType.CODE: [ArtifactType.CONTRACT],
    ArtifactType.TEST: [ArtifactType.CONTRACT],
    ArtifactType.ADR: [ArtifactType.PLAN, ArtifactType.TASKS],
    ArtifactType.CONTRACT: [],
}


@dataclass
class ArtifactNode:
    path: str
    artifact_type: ArtifactType
    status: SyncStatus = SyncStatus.SYNCED
    hash: str = ""
    dependencies: list[str] = field(default_factory=list)
    dependents: list[str] = field(default_factory=list)
    last_modified: str = ""
    last_synced: str = ""


@dataclass
class ValidationReport:
    root_spec: str
    total_artifacts: int = 0
    synced_count: int = 0
    stale_count: int = 0
    conflict_count: int = 0
    orphan_count: int = 0
    issues: list[str] = field(default_factory=list)

    @property
    def is_healthy(self) -> bool:
        return self.conflict_count == 0 and self.orphan_count == 0

    @property
    def sync_percentage(self) -> float:
        if self.total_artifacts == 0:
            return 100.0
        return round(self.synced_count / self.total_artifacts * 100, 1)


class ArtifactSyncEngine:
    """Motor de sincronizacao de artefatos com grafo de dependencias."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.graph: dict[str, ArtifactNode] = {}

    def register_artifact(self, path: str, artifact_type: ArtifactType) -> ArtifactNode:
        abs_path = str(self.project_root / path)
        node = ArtifactNode(
            path=abs_path,
            artifact_type=artifact_type,
            hash=self._compute_hash(abs_path),
            last_modified=self._get_mtime(abs_path),
            last_synced=datetime.now(timezone.utc).isoformat()
        )
        self.graph[abs_path] = node
        return node

    def set_dependency(self, source_path: str, target_path: str):
        """Estabelece dependencia: target depende de source."""
        source = str(self.project_root / source_path)
        target = str(self.project_root / target_path)

        if source not in self.graph:
            self.register_artifact(source_path, self._guess_type(source_path))
        if target not in self.graph:
            self.register_artifact(target_path, self._guess_type(target_path))

        self.graph[source].dependents.append(target)
        self.graph[target].dependencies.append(source)

    def mark_modified(self, path: str) -> list[str]:
        """Marca artefato como modificado e retorna lista de artefatos invalidados."""
        abs_path = str(self.project_root / path)
        if abs_path not in self.graph:
            return []

        current_hash = self._compute_hash(abs_path)
        node = self.graph[abs_path]

        if current_hash == node.hash:
            return []

        node.hash = current_hash
        node.last_modified = self._get_mtime(abs_path)

        invalidated = self._invalidate_cascade(abs_path, set())
        return list(invalidated)

    def get_status(self, path: str) -> SyncStatus:
        abs_path = str(self.project_root / path)
        node = self.graph.get(abs_path)
        return node.status if node else SyncStatus.ORPHAN

    def validate_chain(self, root_spec: str) -> ValidationReport:
        """Valida a cadeia completa a partir de uma spec raiz."""
        abs_root = str(self.project_root / root_spec)
        report = ValidationReport(root_spec=root_spec)

        visited = set()
        self._collect_chain(abs_root, visited)

        for path in visited:
            report.total_artifacts += 1
            node = self.graph.get(path)
            if not node:
                report.orphan_count += 1
                report.issues.append(f"ORFAO: {path} nao encontrado no grafo")
                continue

            if not Path(path).exists():
                report.orphan_count += 1
                report.issues.append(f"ORFAO: {path} nao existe no disco")
                continue

            current_hash = self._compute_hash(path)
            if current_hash != node.hash:
                node.status = SyncStatus.STALE
                report.stale_count += 1
                report.issues.append(f"STALE: {path} -- hash mudou desde ultimo sync")
            else:
                report.synced_count += 1

        return report

    def regenerate(self, path: str) -> bool:
        """Marca artefato para regeneracao. Delegacao para o agente."""
        abs_path = str(self.project_root / path)
        if abs_path in self.graph:
            self.graph[abs_path].status = SyncStatus.REGENERATING
            return True
        return False

    def resolve_conflicts(self, path: str) -> bool:
        """Resolve conflito marcando o artefato como synced com o hash atual."""
        abs_path = str(self.project_root / path)
        if abs_path in self.graph:
            node = self.graph[abs_path]
            node.hash = self._compute_hash(abs_path)
            node.status = SyncStatus.SYNCED
            node.last_synced = datetime.now(timezone.utc).isoformat()
            return True
        return False

    def export_graph(self) -> dict:
        """Exporta o grafo para dict serializavel."""
        return {
            "artifacts": {
                path: {
                    "type": node.artifact_type.value,
                    "status": node.status.value,
                    "hash": node.hash,
                    "dependencies": node.dependencies,
                    "dependents": node.dependents,
                    "last_modified": node.last_modified,
                    "last_synced": node.last_synced,
                }
                for path, node in self.graph.items()
            }
        }

    def import_graph(self, data: dict):
        for path, info in data.get("artifacts", {}).items():
            self.graph[path] = ArtifactNode(
                path=path,
                artifact_type=ArtifactType(info["type"]),
                status=SyncStatus(info["status"]),
                hash=info["hash"],
                dependencies=info.get("dependencies", []),
                dependents=info.get("dependents", []),
                last_modified=info.get("last_modified", ""),
                last_synced=info.get("last_synced", ""),
            )

    def _invalidate_cascade(self, abs_path: str, visited: set) -> set:
        if abs_path in visited:
            return visited
        visited.add(abs_path)

        node = self.graph.get(abs_path)
        if not node:
            return visited

        artifact_type = node.artifact_type
        for dependent_path in node.dependents:
            if dependent_path in self.graph:
                self.graph[dependent_path].status = SyncStatus.STALE
            self._invalidate_cascade(dependent_path, visited)

        for target_type in INVALIDATION_RULES.get(artifact_type, []):
            for dep_path in node.dependents:
                dep = self.graph.get(dep_path)
                if dep and dep.artifact_type == target_type:
                    dep.status = SyncStatus.STALE
                    self._invalidate_cascade(dep_path, visited)

        return visited

    def _collect_chain(self, abs_path: str, visited: set):
        if abs_path in visited or abs_path not in self.graph:
            return
        visited.add(abs_path)
        for dep in self.graph[abs_path].dependents:
            self._collect_chain(dep, visited)

    @staticmethod
    def _compute_hash(filepath: str) -> str:
        p = Path(filepath)
        if not p.exists():
            return ""
        return hashlib.sha256(p.read_bytes()).hexdigest()[:16]

    @staticmethod
    def _get_mtime(filepath: str) -> str:
        p = Path(filepath)
        if not p.exists():
            return ""
        return datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).isoformat()

    @staticmethod
    def _guess_type(path: str) -> ArtifactType:
        name = Path(path).name.lower()
        if "spec" in name:
            return ArtifactType.SPEC
        if "plan" in name:
            return ArtifactType.PLAN
        if "task" in name:
            return ArtifactType.TASKS
        if name.endswith(".py") and "test" in name:
            return ArtifactType.TEST
        if name.endswith(".py") or name.endswith(".ts") or name.endswith(".js"):
            return ArtifactType.CODE
        if "adr" in name or "decision" in name:
            return ArtifactType.ADR
        return ArtifactType.CODE


def auto_wire_sdd_pipeline(engine: ArtifactSyncEngine, specs_dir: str = "specs"):
    """Configura automaticamente o grafo para um pipeline SDD padrao."""
    spec_files = list(Path(specs_dir).glob("*.md")) if Path(specs_dir).exists() else []

    for spec_file in spec_files:
        spec_path = str(spec_file)
        base = spec_file.stem

        plan_path = f"plan_{base}.md"
        tasks_path = f"tasks_{base}.md"
        code_path = f"src/{base}/"
        test_path = f"tests/test_{base}/"

        engine.register_artifact(spec_path, ArtifactType.SPEC)
        engine.register_artifact(plan_path, ArtifactType.PLAN)
        engine.register_artifact(tasks_path, ArtifactType.TASKS)
        engine.register_artifact(code_path, ArtifactType.CODE)
        engine.register_artifact(test_path, ArtifactType.TEST)

        engine.set_dependency(spec_path, plan_path)
        engine.set_dependency(plan_path, tasks_path)
        engine.set_dependency(tasks_path, code_path)
        engine.set_dependency(code_path, test_path)
        engine.set_dependency(spec_path, test_path)
