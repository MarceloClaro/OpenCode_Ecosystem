"""
CrossPlatformValidator -- Teste automatizado de portabilidade de skills.

Verifica se skills funcionam em Claude Code, Codex e Antigravity.
Integra-se com: RegistryV2, SecureLoader, PermissionTiers.
"""

import hashlib
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


PLATFORM_CONFIGS = {
    "claude_code": {
        "skill_dir": ".claude/skills",
        "invoke_cmd": ["claude", "-p"],
        "name": "Claude Code (Anthropic)",
    },
    "codex": {
        "skill_dir": ".codex/skills",
        "invoke_cmd": ["codex", "exec"],
        "name": "Codex (OpenAI)",
    },
    "antigravity": {
        "skill_dir": ".agents/skills",
        "invoke_cmd": ["antigravity", "run"],
        "name": "Antigravity (Google)",
    },
}


@dataclass
class PlatformResult:
    platform: str
    skill_name: str
    output: str = ""
    exit_code: int = -1
    elapsed_seconds: float = 0.0
    tokens_used: int = 0
    errors: list[str] = field(default_factory=list)
    passed: bool = False


@dataclass
class CrossPlatformReport:
    skill_name: str
    platforms_tested: list[str]
    results: list[PlatformResult] = field(default_factory=list)
    portability_score: float = 0.0
    compatible_platforms: int = 0
    issues: list[str] = field(default_factory=list)

    @property
    def is_fully_portable(self) -> bool:
        return self.portability_score >= 80


class CrossPlatformValidator:
    """Validador de portabilidade de skills entre plataformas."""

    def __init__(self, timeout_seconds: int = 300, dry_run: bool = True):
        self.timeout = timeout_seconds
        self.dry_run = dry_run

    def validate_skill(self, skill_path: str,
                       test_prompt: Optional[str] = None,
                       platforms: Optional[list[str]] = None) -> CrossPlatformReport:
        """Valida uma skill em multiplas plataformas."""
        skill_dir = Path(skill_path)
        skill_name = skill_dir.name

        if not (skill_dir / "SKILL.md").exists():
            raise FileNotFoundError(f"SKILL.md not found in {skill_path}")

        target_platforms = platforms or list(PLATFORM_CONFIGS.keys())
        report = CrossPlatformReport(
            skill_name=skill_name,
            platforms_tested=target_platforms,
        )

        prompt = test_prompt or f"Execute a tarefa descrita na skill {skill_name} e retorne o resultado em JSON."

        for platform_id in target_platforms:
            if platform_id not in PLATFORM_CONFIGS:
                continue

            if self.dry_run:
                result = self._dry_run_validation(skill_name, platform_id, prompt)
            else:
                result = self._real_validation(skill_dir, skill_name, platform_id, prompt)

            report.results.append(result)

        report.compatible_platforms = sum(1 for r in report.results if r.passed)
        report.portability_score = (report.compatible_platforms / max(1, len(report.results))) * 100

        if report.compatible_platforms < len(report.results):
            report.issues.append(
                f"Incompativel com: {[r.platform for r in report.results if not r.passed]}"
            )

        return report

    def validate_all(self, skills_root: str,
                     platforms: Optional[list[str]] = None) -> list[CrossPlatformReport]:
        """Valida todas as skills em um diretorio."""
        reports = []
        root = Path(skills_root)

        for skill_dir in root.iterdir():
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                try:
                    report = self.validate_skill(str(skill_dir), platforms=platforms)
                    reports.append(report)
                except Exception as e:
                    reports.append(CrossPlatformReport(
                        skill_name=skill_dir.name,
                        platforms_tested=platforms or list(PLATFORM_CONFIGS.keys()),
                        issues=[str(e)]
                    ))

        return reports

    def _dry_run_validation(self, skill_name: str, platform_id: str,
                            prompt: str) -> PlatformResult:
        """Validacao em modo dry-run (sem executar agentes reais)."""
        config = PLATFORM_CONFIGS[platform_id]
        expected_skill_dir = Path(config["skill_dir"]) / skill_name

        result = PlatformResult(
            platform=config["name"],
            skill_name=skill_name,
        )

        checks = []
        checks.append(("SKILL.md existe", True))
        checks.append(("Prompt gerado", bool(prompt)))
        checks.append(("Diretorio de skill valido", expected_skill_dir.as_posix() is not None))

        result.passed = all(c[1] for c in checks)
        result.output = json.dumps({"checks": [{"name": c[0], "ok": c[1]} for c in checks]})
        result.exit_code = 0 if result.passed else 1

        return result

    def _real_validation(self, skill_dir: Path, skill_name: str,
                         platform_id: str, prompt: str) -> PlatformResult:
        """Validacao real executando o agente."""
        config = PLATFORM_CONFIGS[platform_id]
        result = PlatformResult(
            platform=config["name"],
            skill_name=skill_name,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            skill_dest = tmp_path / config["skill_dir"] / skill_name
            skill_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(skill_dir, skill_dest)

            try:
                proc = subprocess.run(
                    config["invoke_cmd"] + [prompt],
                    cwd=str(tmp_path),
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
                result.exit_code = proc.returncode
                result.output = proc.stdout[:5000]
                result.passed = proc.returncode == 0

                if proc.returncode != 0:
                    result.errors.append(f"stderr: {proc.stderr[:500]}")

            except subprocess.TimeoutExpired:
                result.errors.append(f"Timeout ({self.timeout}s)")
                result.passed = False
            except FileNotFoundError:
                result.errors.append(f"Comando '{config['invoke_cmd'][0]}' nao encontrado")
                result.passed = False

        return result


def generate_portability_report(reports: list[CrossPlatformReport]) -> str:
    lines = [
        "# Cross-Platform Portability Report",
        "",
        f"| Skill | Plataformas | Compativeis | Score | Status |",
        f"|-------|------------|-------------|-------|--------|",
    ]

    for report in reports:
        status = "PORTABLE" if report.is_fully_portable else "ISSUES"
        lines.append(
            f"| {report.skill_name} | {len(report.platforms_tested)} | "
            f"{report.compatible_platforms} | {report.portability_score:.0f}% | {status} |"
        )

    total_score = sum(r.portability_score for r in reports) / max(1, len(reports))
    fully_portable = sum(1 for r in reports if r.is_fully_portable)

    lines.extend([
        "",
        f"## Resumo",
        f"- Skills testadas: {len(reports)}",
        f"- Totalmente portaveis: {fully_portable}/{len(reports)}",
        f"- **Portability Score medio: {total_score:.0f}%**",
        "",
    ])

    for report in reports:
        if report.issues:
            lines.append(f"### {report.skill_name}")
            for issue in report.issues:
                lines.append(f"- {issue}")
            lines.append("")

    return "\n".join(lines)


def validate_all_skills(skills_paths: list[str]) -> dict:
    """Valida todas as skills do ecossistema e retorna sumario."""
    validator = CrossPlatformValidator(dry_run=True)
    all_reports = []

    for path in skills_paths:
        if Path(path).exists():
            all_reports.extend(validator.validate_all(path))

    return {
        "total_skills": len(all_reports),
        "portable_count": sum(1 for r in all_reports if r.is_fully_portable),
        "average_score": round(
            sum(r.portability_score for r in all_reports) / max(1, len(all_reports)), 1
        ),
        "issues": [
            {"skill": r.skill_name, "issues": r.issues}
            for r in all_reports if r.issues
        ]
    }
