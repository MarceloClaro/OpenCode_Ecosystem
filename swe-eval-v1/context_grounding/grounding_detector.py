"""
Context Grounding / API Hallucination Detection -- Extensao do Cora-Debate V6.

Detecta quando o agente inventa APIs, importa bibliotecas inexistentes
ou ignora restricoes arquiteturais documentadas.
Integra-se com: Cora-Debate V6, DecisionNode, RegistryV2.
"""

import ast
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class HallucinationType(Enum):
    API_IMPORT = "api_import"
    API_METHOD = "api_method"
    API_SIGNATURE = "api_signature"
    ARCH_VIOLATION = "arch_violation"
    CONSTRAINT_IGNORE = "constraint_ignore"
    CONTEXT_BLIND = "context_blind"


@dataclass
class HallucinationFinding:
    htype: HallucinationType
    description: str
    file_path: str
    line: int
    evidence: str
    suggestion: str


@dataclass
class GroundingReport:
    score: float
    imports_valid: int = 0
    imports_total: int = 0
    hallucinations: list[HallucinationFinding] = field(default_factory=list)
    arch_violations: list[HallucinationFinding] = field(default_factory=list)
    passed: bool = False

    @property
    def grade(self) -> str:
        if self.score >= 90:
            return "Excelente"
        elif self.score >= 70:
            return "Bom"
        elif self.score >= 50:
            return "Regular"
        return "Ruim"


class DependencyIndexer:
    """Indexa dependencias reais do projeto."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.dependencies: dict[str, dict] = {}
        self._index()

    def _index(self):
        self._index_python()
        self._index_javascript()

    def _index_python(self):
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            for line in req_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    pkg = re.split(r"[=<>~!]", line)[0].strip().lower()
                    self.dependencies[pkg] = {"source": "requirements.txt", "version": line}

        setup_file = self.project_root / "setup.py"
        if setup_file.exists():
            content = setup_file.read_text(encoding="utf-8")
            for match in re.finditer(r"['\"]([^'\"]+)['\"]", content):
                pkg = match.group(1).lower()
                if pkg not in self.dependencies:
                    self.dependencies[pkg] = {"source": "setup.py", "version": "unknown"}

    def _index_javascript(self):
        pkg_file = self.project_root / "package.json"
        if pkg_file.exists():
            data = json.loads(pkg_file.read_text(encoding="utf-8"))
            for dep_type in ("dependencies", "devDependencies"):
                for name, version in data.get(dep_type, {}).items():
                    self.dependencies[name.lower()] = {"source": "package.json", "version": version}

    def has_dependency(self, name: str) -> bool:
        return name.lower() in self.dependencies

    def get_available_modules(self) -> set[str]:
        modules = set()
        for dep in self.dependencies:
            modules.add(dep)
            modules.add(dep.replace("-", "_"))
        modules.update({"os", "sys", "json", "re", "math", "datetime", "pathlib",
                       "collections", "itertools", "functools", "typing", "abc", "hashlib",
                       "subprocess", "logging", "unittest", "pytest", "io", "csv", "sqlite3"})
        return modules


class APIImportValidator:
    """Valida imports contra dependencias reais do projeto."""

    def __init__(self, indexer: DependencyIndexer):
        self.indexer = indexer
        self.stdlib_modules = {"os", "sys", "json", "re", "math", "datetime", "pathlib",
                              "collections", "itertools", "functools", "typing", "abc", "hashlib",
                              "subprocess", "logging", "unittest", "pytest", "io", "csv", "sqlite3",
                              "enum", "dataclasses", "copy", "textwrap", "argparse", "configparser",
                              "shutil", "tempfile", "glob", "fnmatch", "traceback", "warnings",
                              "contextlib", "asyncio", "threading", "multiprocessing", "queue",
                              "socket", "http", "urllib", "xml", "html", "email", "uuid", "random",
                              "statistics", "decimal", "fractions", "base64", "binascii", "struct",
                              "pickle", "zipfile", "tarfile", "gzip", "bz2", "lzma"}

    def validate_file(self, filepath: str) -> list[HallucinationFinding]:
        findings = []
        try:
            tree = ast.parse(Path(filepath).read_text(encoding="utf-8"))
        except (SyntaxError, FileNotFoundError):
            return findings

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    findings.extend(self._check_import(alias.name, filepath, node.lineno))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    findings.extend(self._check_import(node.module, filepath, node.lineno))

        return findings

    def _check_import(self, module_name: str, filepath: str, lineno: int) -> list[HallucinationFinding]:
        findings = []
        top_module = module_name.split(".")[0].lower()

        if top_module in self.stdlib_modules:
            return findings

        if not self.indexer.has_dependency(top_module):
            findings.append(HallucinationFinding(
                htype=HallucinationType.API_IMPORT,
                description=f"Modulo '{top_module}' importado mas nao listado em dependencias",
                file_path=filepath,
                line=lineno,
                evidence=f"import {module_name}",
                suggestion=f"Adicione '{top_module}' ao requirements.txt ou package.json, ou verifique se eh modulo interno"
            ))
        return findings


class ArchitectureChecker:
    """Verifica aderencia a decisoes arquiteturais registradas no DecisionNode."""

    def __init__(self, decisions_path: Optional[str] = None):
        self.decisions: list[dict] = []
        if decisions_path:
            self.load_decisions(decisions_path)

    def load_decisions(self, path: str):
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            self.decisions = data if isinstance(data, list) else data.get("decisions", [])
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def add_decision(self, decision_id: str, rule: str, constraint: str):
        self.decisions.append({"id": decision_id, "rule": rule, "constraint": constraint})

    def check_file(self, filepath: str) -> list[HallucinationFinding]:
        findings = []
        try:
            content = Path(filepath).read_text(encoding="utf-8")
        except FileNotFoundError:
            return findings

        for decision in self.decisions:
            if decision.get("rule") == "Repository Pattern":
                if "execute(" in content.lower() or "cursor." in content.lower() or "conn." in content.lower():
                    if "Repository" not in content and "Repo" not in content:
                        findings.append(HallucinationFinding(
                            htype=HallucinationType.ARCH_VIOLATION,
                            description=f"Violacao do padrao Repository: SQL direto detectado",
                            file_path=filepath,
                            line=0,
                            evidence=f"DecisionNode: {decision['id']}",
                            suggestion="Use a camada Repository para acesso a dados"
                        ))

            if decision.get("rule") == "Layered Architecture":
                if "from infrastructure" in content and "domain" in content:
                    findings.append(HallucinationFinding(
                        htype=HallucinationType.ARCH_VIOLATION,
                        description="Dominio importando de infraestrutura -- violacao de camadas",
                        file_path=filepath,
                        line=0,
                        evidence=f"DecisionNode: {decision['id']}",
                        suggestion="Inverta a dependencia: infraestrutura implementa interfaces do dominio"
                    ))

        return findings


class GroundingScorer:
    """Calcula score de grounding (0-100)."""

    def calculate(self, imports_valid: int, imports_total: int,
                  arch_violations: int, max_expected_violations: int = 10,
                  files_referenced: int = 0, files_should_reference: int = 0,
                  constraints_respected: int = 0, constraints_total: int = 0) -> float:
        score = 0.0

        if imports_total > 0:
            score += (imports_valid / imports_total) * 40

        score += max(0, (1 - arch_violations / max(max_expected_violations, 1))) * 30

        if files_should_reference > 0:
            score += (files_referenced / files_should_reference) * 20

        if constraints_total > 0:
            score += (constraints_respected / constraints_total) * 10

        return min(100, round(score, 1))


class CoraV6GroundingExtension:
    """Extensao do verificador V6 do Cora-Debate para grounding de codigo."""

    def __init__(self, project_root: str, decisions_path: Optional[str] = None):
        self.indexer = DependencyIndexer(project_root)
        self.import_validator = APIImportValidator(self.indexer)
        self.arch_checker = ArchitectureChecker(decisions_path)
        self.scorer = GroundingScorer()

    def verify(self, agent_output: dict, context: dict) -> GroundingReport:
        """Verifica grounding de uma saida de agente."""
        report = GroundingReport(score=0.0)

        code_files = agent_output.get("files_modified", []) + agent_output.get("files_created", [])
        if not code_files:
            code_files = context.get("code_files", [])

        for filepath in code_files:
            if not Path(filepath).exists():
                continue
            report.hallucinations.extend(self.import_validator.validate_file(filepath))
            report.arch_violations.extend(self.arch_checker.check_file(filepath))

        report.imports_total = max(1, len(code_files))
        report.imports_valid = report.imports_total - len(
            [h for h in report.hallucinations if h.htype == HallucinationType.API_IMPORT]
        )

        report.score = self.scorer.calculate(
            imports_valid=report.imports_valid,
            imports_total=report.imports_total,
            arch_violations=len(report.arch_violations),
        )
        report.passed = report.score >= 80

        return report

    def verify_directory(self, directory: str) -> GroundingReport:
        """Verifica grounding de todos arquivos Python em um diretorio."""
        all_hallucinations = []
        all_violations = []
        total_files = 0
        valid_files = 0

        for py_file in Path(directory).rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
            total_files += 1
            findings = self.import_validator.validate_file(str(py_file))
            if not any(f.htype == HallucinationType.API_IMPORT for f in findings):
                valid_files += 1
            all_hallucinations.extend(findings)
            all_violations.extend(self.arch_checker.check_file(str(py_file)))

        report = GroundingReport(
            score=0.0,
            imports_valid=valid_files,
            imports_total=max(1, total_files),
            hallucinations=all_hallucinations,
            arch_violations=all_violations,
        )
        report.score = self.scorer.calculate(
            imports_valid=valid_files,
            imports_total=max(1, total_files),
            arch_violations=len(all_violations),
        )
        report.passed = report.score >= 80
        return report


def generate_grounding_report_markdown(report: GroundingReport) -> str:
    lines = [
        "# Grounding Report",
        "",
        f"| Metrica | Valor |",
        f"|---------|-------|",
        f"| **Grounding Score** | **{report.score}/100** |",
        f"| Nota | {report.grade} |",
        f"| Imports validos | {report.imports_valid}/{report.imports_total} |",
        f"| APIs alucinadas | {len(report.hallucinations)} |",
        f"| Violacoes arquiteturais | {len(report.arch_violations)} |",
        f"| Status | {'PASS' if report.passed else 'FAIL'} |",
        "",
    ]

    if report.hallucinations:
        lines.append("## APIs Potencialmente Alucinadas")
        for h in report.hallucinations:
            lines.extend([
                f"- **[{h.htype.value}]** {h.description}",
                f"  - Arquivo: `{h.file_path}:{h.line}`",
                f"  - Evidencia: {h.evidence}",
                f"  - Sugestao: {h.suggestion}",
                "",
            ])

    if report.arch_violations:
        lines.append("## Violacoes Arquiteturais")
        for v in report.arch_violations:
            lines.extend([
                f"- **[{v.htype.value}]** {v.description}",
                f"  - Arquivo: `{v.file_path}:{v.line}`",
                f"  - Evidencia: {v.evidence}",
                f"  - Sugestao: {v.suggestion}",
                "",
            ])

    return "\n".join(lines)
