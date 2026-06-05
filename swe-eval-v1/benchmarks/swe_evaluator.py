"""
SWE Process Benchmark -- Avaliacao do ciclo completo de engenharia de software.

Complementa o CORA-Eval com 6 dimensoes de processo de engenharia.
Integra-se com: CORA-Eval, SpecDriftDetector, Cora-Debate.
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SWETask:
    id: str
    name: str
    description: str
    difficulty: str
    expected_artifacts: list[str] = field(default_factory=list)
    validation: dict = field(default_factory=dict)
    time_limit_seconds: int = 3600


@dataclass
class SWEMetrics:
    d1_spec_completeness: float = 0.0
    d2_artifact_consistency: float = 0.0
    d3_correction_rate: float = 0.0
    d4_decision_stability: float = 0.0
    d5_audit_trail_quality: float = 0.0
    d6_implementation_fidelity: float = 0.0

    corrections_per_phase: dict = field(default_factory=dict)
    decisions_total: int = 0
    decisions_stable: int = 0
    traceable_decisions: int = 0

    @property
    def total_score(self) -> float:
        weights = [0.20, 0.20, 0.15, 0.15, 0.15, 0.15]
        scores = [
            self.d1_spec_completeness,
            self.d2_artifact_consistency,
            self.d3_correction_rate,
            self.d4_decision_stability,
            self.d5_audit_trail_quality,
            self.d6_implementation_fidelity,
        ]
        return round(sum(w * s for w, s in zip(weights, scores)), 1)

    @property
    def grade(self) -> str:
        s = self.total_score
        if s >= 90: return "A"
        if s >= 80: return "B"
        if s >= 70: return "C"
        if s >= 60: return "D"
        return "F"


@dataclass
class SWEResult:
    task: SWETask
    metrics: SWEMetrics = field(default_factory=SWEMetrics)
    artifacts_produced: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
    passed: bool = False


DEFAULT_TASKS: list[dict] = [
    {
        "id": "SWE-001",
        "name": "REST API CRUD",
        "description": "Implementar API REST para gerenciamento de usuarios com autenticacao JWT",
        "difficulty": "N1",
        "expected_artifacts": ["spec.md", "plan.md", "tasks.md", "api.py", "test_api.py"],
        "validation": {
            "endpoints": ["POST /auth/login", "GET /users", "POST /users", "PUT /users/:id", "DELETE /users/:id"],
            "constraints": ["JWT expiration <= 24h", "password min 8 chars", "email unique"],
            "test_coverage_min": 80
        }
    },
    {
        "id": "SWE-002",
        "name": "Database Migration",
        "description": "Migrar schema de SQLite para PostgreSQL mantendo compatibilidade",
        "difficulty": "N2",
        "expected_artifacts": ["spec.md", "plan.md", "migration.sql", "test_migration.py"],
        "validation": {"constraints": ["zero downtime", "rollback plan", "data integrity check"]}
    },
    {
        "id": "SWE-003",
        "name": "Refactoring com Spec",
        "description": "Refatorar modulo legado de 500 linhas para 5 modulos com spec-driven",
        "difficulty": "N3",
        "expected_artifacts": ["spec.md", "plan.md", "tasks.md", "refactored/", "tests/"],
        "validation": {"constraints": ["comportamento identico", "cobertura >= 80%", "complexidade ciclomatica < 10"]}
    },
    {
        "id": "SWE-004",
        "name": "Greenfield com SDD+TDD",
        "description": "Construir sistema de notificacoes do zero usando SDD+TDD completo",
        "difficulty": "N3",
        "expected_artifacts": ["spec.md", "plan.md", "tasks.md", "notifier/", "tests/", "adr/"],
        "validation": {"constraints": ["TDD red-green-refactor", "spec como unica fonte da verdade", "ADR para cada decisao"]}
    },
    {
        "id": "SWE-005",
        "name": "Bug Fix com Traceability",
        "description": "Corrigir 3 bugs criticos com rastreabilidade completa bug->spec->fix->test",
        "difficulty": "N2",
        "expected_artifacts": ["bug_report.md", "fix_spec.md", "fix_plan.md", "patched/", "regression_tests/"],
        "validation": {"constraints": ["cada fix rastreado a um bug", "testes de regressao", "spec atualizada"]}
    }
]


class SWEEvaluator:
    """Avaliador de processos de engenharia de software."""

    def __init__(self, tasks: Optional[list[dict]] = None):
        self.tasks = [SWETask(**t) for t in (tasks or DEFAULT_TASKS)]

    def evaluate_artifacts(self, task: SWETask, artifact_dir: str) -> SWEMetrics:
        """Avalia artefatos produzidos contra dimensoes do benchmark."""
        metrics = SWEMetrics()
        artifact_path = Path(artifact_dir)

        produced = [f.name for f in artifact_path.iterdir()] if artifact_path.exists() else []
        expected_set = set(a.lower() for a in task.expected_artifacts)
        produced_set = set(p.lower() for p in produced)

        if expected_set:
            metrics.d1_spec_completeness = len(produced_set & expected_set) / len(expected_set) * 100

        spec_file = artifact_path / "spec.md"
        plan_file = artifact_path / "plan.md"
        tasks_file = artifact_path / "tasks.md"

        metrics.d2_artifact_consistency = self._check_consistency(spec_file, plan_file, tasks_file)
        metrics.d4_decision_stability = self._check_stability(artifact_path)
        metrics.d5_audit_trail_quality = self._check_audit_trail(artifact_path)
        metrics.d6_implementation_fidelity = self._check_fidelity(task, artifact_path)

        return metrics

    def _check_consistency(self, spec_file: Path, plan_file: Path, tasks_file: Path) -> float:
        score = 0.0
        pairs = 0

        if spec_file.exists() and plan_file.exists():
            pairs += 1
            spec_content = spec_file.read_text(encoding="utf-8").lower()
            plan_content = plan_file.read_text(encoding="utf-8").lower()
            spec_keywords = self._extract_keywords(spec_content)
            plan_keywords = self._extract_keywords(plan_content)
            if spec_keywords:
                overlap = len(spec_keywords & plan_keywords) / len(spec_keywords)
                score += overlap * 100

        if plan_file.exists() and tasks_file.exists():
            pairs += 1
            plan_content = plan_file.read_text(encoding="utf-8").lower()
            tasks_content = tasks_file.read_text(encoding="utf-8").lower()
            plan_keywords = self._extract_keywords(plan_content)
            tasks_keywords = self._extract_keywords(tasks_content)
            if plan_keywords:
                overlap = len(plan_keywords & tasks_keywords) / len(plan_keywords)
                score += overlap * 100

        return score / max(1, pairs)

    def _check_stability(self, artifact_path: Path) -> float:
        adr_dir = artifact_path / "adr"
        if not adr_dir.exists():
            return 0.0

        adrs = list(adr_dir.glob("*.md"))
        if not adrs:
            return 0.0

        stable = sum(1 for a in adrs if "deprecated" not in a.name.lower())
        return stable / len(adrs) * 100

    def _check_audit_trail(self, artifact_path: Path) -> float:
        decisions_file = artifact_path / "decisions.json"
        if not decisions_file.exists():
            spec_file = artifact_path / "spec.md"
            if spec_file.exists():
                content = spec_file.read_text(encoding="utf-8").lower()
                trace_count = content.count("decis") + content.count("adr") + content.count("decision")
                return min(100, trace_count * 10)
            return 0.0

        try:
            decisions = json.loads(decisions_file.read_text(encoding="utf-8"))
            if not decisions:
                return 0.0
            traceable = sum(1 for d in decisions if isinstance(d, dict) and d.get("rationale"))
            return traceable / len(decisions) * 100
        except json.JSONDecodeError:
            return 0.0

    def _check_fidelity(self, task: SWETask, artifact_path: Path) -> float:
        constraints = task.validation.get("constraints", [])
        if not constraints:
            return 100.0

        verified = 0
        for py_file in artifact_path.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore").lower()
            for constraint in constraints:
                if any(word in content for word in constraint.lower().split()[:3]):
                    verified += 1

        return min(100, verified / len(constraints) * 100)

    @staticmethod
    def _extract_keywords(text: str) -> set[str]:
        stopwords = {"de", "do", "da", "em", "no", "na", "para", "com", "que",
                     "um", "uma", "os", "as", "o", "a", "e", "ou", "se", "nao"}
        words = set(w for w in text.split() if len(w) > 3 and w not in stopwords)
        return set(list(words)[:50])

    def run_benchmark(self, artifact_dir: str, task_ids: Optional[list[str]] = None) -> list[SWEResult]:
        """Executa benchmark completo."""
        results = []
        target_tasks = [t for t in self.tasks if task_ids is None or t.id in task_ids]

        for task in target_tasks:
            start = time.time()
            task_artifact_dir = str(Path(artifact_dir) / task.id)

            try:
                metrics = self.evaluate_artifacts(task, task_artifact_dir)
                errors = []
                if metrics.d1_spec_completeness < 50:
                    errors.append(f"D1: Spec completeness baixa ({metrics.d1_spec_completeness:.0f}%)")
                if metrics.total_score < 60:
                    errors.append(f"Score total insuficiente ({metrics.total_score:.0f})")
            except Exception as e:
                metrics = SWEMetrics()
                errors = [str(e)]

            elapsed = time.time() - start

            result = SWEResult(
                task=task,
                metrics=metrics,
                artifacts_produced=[str(p) for p in Path(task_artifact_dir).iterdir()] if Path(task_artifact_dir).exists() else [],
                elapsed_seconds=round(elapsed, 1),
                errors=errors,
                passed=len(errors) == 0 and metrics.total_score >= 60
            )
            results.append(result)

        return results


def generate_benchmark_report(results: list[SWEResult]) -> str:
    lines = [
        "# SWE Process Benchmark Report",
        "",
        f"| Tarefa | Dificuldade | Score | Grade | Spec Compl. | Consist. | Fidelity | Status |",
        f"|--------|------------|-------|-------|-------------|----------|----------|--------|",
    ]

    for r in results:
        m = r.metrics
        lines.append(
            f"| {r.task.id} | {r.task.difficulty} | {m.total_score:.0f} | {m.grade} | "
            f"{m.d1_spec_completeness:.0f}% | {m.d2_artifact_consistency:.0f}% | "
            f"{m.d6_implementation_fidelity:.0f}% | {'PASS' if r.passed else 'FAIL'} |"
        )

    total_score = sum(r.metrics.total_score for r in results) / max(1, len(results))
    passed_count = sum(1 for r in results if r.passed)

    lines.extend([
        "",
        f"## Resumo",
        f"- Tarefas executadas: {len(results)}",
        f"- Tarefas aprovadas: {passed_count}/{len(results)}",
        f"- **SWE-Score medio: {total_score:.1f}/100**",
        f"- Tempo total: {sum(r.elapsed_seconds for r in results):.0f}s",
    ])

    return "\n".join(lines)


def load_tasks(tasks_path: str) -> list[dict]:
    return json.loads(Path(tasks_path).read_text(encoding="utf-8"))
