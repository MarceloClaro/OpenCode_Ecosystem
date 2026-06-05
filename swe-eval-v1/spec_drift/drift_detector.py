"""
SpecDriftDetector -- Deteccao automatica de divergencia entre especificacao e implementacao.

Compara specs (markdown) com codigo (Python/TypeScript) usando AST diff e
contratos de teste como ground truth.
Integra-se com: SDD+TDD Pipeline, Cora-Debate V6, DecisionNode.
"""

import ast
import hashlib
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class DriftSeverity(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass
class DriftFinding:
    severity: DriftSeverity
    description: str
    spec_reference: str
    code_location: str
    expected: str
    actual: str


@dataclass
class Contract:
    method: str
    path: str
    response_fields: list[str] = field(default_factory=list)
    request_fields: list[str] = field(default_factory=list)
    types: dict = field(default_factory=dict)
    constraints: list[str] = field(default_factory=list)
    error_codes: list[int] = field(default_factory=list)
    source_line: int = 0


@dataclass
class DriftReport:
    spec_path: str
    code_paths: list[str]
    findings: list[DriftFinding] = field(default_factory=list)
    contracts_found: int = 0
    contracts_matched: int = 0
    contracts_mismatched: int = 0

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == DriftSeverity.CRITICAL)

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == DriftSeverity.WARNING)

    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == DriftSeverity.INFO)

    @property
    def drift_score(self) -> int:
        return self.critical_count * 10 + self.warning_count * 3 + self.info_count * 1

    @property
    def passed(self) -> bool:
        return self.critical_count == 0 and self.drift_score <= 10


class ContractExtractor:
    """Extrai contratos de especificacao a partir de arquivos markdown."""

    ENDPOINT_PATTERN = re.compile(
        r'(?:endpoint|rota|route|método|method)\s*[`]?(GET|POST|PUT|DELETE|PATCH)\s+(/[^\s`]+)[`]?',
        re.IGNORECASE
    )
    RESPONSE_FIELD_PATTERN = re.compile(
        r'(?:retorna|campo|field|response)[^.]*?[`"](\w+)[`"]',
        re.IGNORECASE
    )
    CONSTRAINT_PATTERN = re.compile(
        r'(?:deve|must|should|obrigatório|required|restrição|constraint)[^.]*?[`"]?([^`"\n]+)[`"]?',
        re.IGNORECASE
    )

    def extract_contracts(self, spec_path: str) -> list[Contract]:
        content = Path(spec_path).read_text(encoding="utf-8")
        contracts = []

        for line_no, line in enumerate(content.split("\n"), 1):
            match = self.ENDPOINT_PATTERN.search(line)
            if match:
                method, path = match.group(1).upper(), match.group(2)
                contract = Contract(method=method, path=path, source_line=line_no)

                context_start = max(0, line_no - 10)
                context_end = min(len(content.split("\n")), line_no + 10)
                context = "\n".join(content.split("\n")[context_start:context_end])

                contract.response_fields = self.RESPONSE_FIELD_PATTERN.findall(context)
                contract.constraints = [c.strip() for c in self.CONSTRAINT_PATTERN.findall(context)]
                contracts.append(contract)

        return contracts


class ASTComparator:
    """Compara AST do codigo com contratos extraidos da spec."""

    def compare(self, contracts: list[Contract], code_paths: list[str]) -> list[DriftFinding]:
        findings = []
        code_ast = self._build_code_index(code_paths)

        for contract in contracts:
            findings.extend(self._check_endpoint_exists(contract, code_ast))
            findings.extend(self._check_response_fields(contract, code_ast))
            findings.extend(self._check_constraints(contract, code_ast))

        findings.extend(self._check_undocumented_endpoints(contracts, code_ast))
        return findings

    def _build_code_index(self, code_paths: list[str]) -> dict:
        index = {"routes": {}, "functions": {}, "classes": {}}
        for code_path in code_paths:
            try:
                tree = ast.parse(Path(code_path).read_text(encoding="utf-8"))
                index = self._walk_ast(tree, code_path, index)
            except SyntaxError:
                pass
        return index

    def _walk_ast(self, tree: ast.AST, filepath: str, index: dict) -> dict:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                decorators = [d for d in (self._get_decorator_name(d) for d in node.decorator_list) if d is not None]
                for dec in decorators:
                    if "route" in dec.lower() or "get" in dec.lower() or "post" in dec.lower():
                        route_info = self._extract_route_info(node, decorators)
                        if route_info:
                            index["routes"][f"{route_info['method']}:{route_info['path']}"] = {
                                "file": filepath,
                                "line": node.lineno,
                                "name": node.name,
                                "returns": self._extract_return_fields(node)
                            }
                index["functions"][f"{filepath}:{node.name}"] = {
                    "file": filepath, "line": node.lineno,
                    "args": [a.arg for a in node.args.args],
                    "returns": self._extract_return_fields(node)
                }
        return index

    def _get_decorator_name(self, decorator) -> Optional[str]:
        if isinstance(decorator, ast.Name):
            return decorator.id
        if isinstance(decorator, ast.Attribute):
            return decorator.attr
        if isinstance(decorator, ast.Call):
            return self._get_decorator_name(decorator.func)
        return None

    def _extract_route_info(self, node: ast.FunctionDef, decorators: list[str]) -> Optional[dict]:
        for dec in node.decorator_list:
            if isinstance(dec, ast.Call):
                for keyword in dec.keywords:
                    if keyword.arg == "methods":
                        if isinstance(keyword.value, ast.List):
                            methods = [self._get_constant_value(e) for e in keyword.value.elts]
                            path = self._get_constant_value(dec.args[0]) if dec.args else "/"
                            return {"method": methods[0] if methods else "GET", "path": path}
        return None

    def _get_constant_value(self, node) -> str:
        if isinstance(node, ast.Constant):
            return str(node.value)
        return "unknown"

    def _extract_return_fields(self, node: ast.FunctionDef) -> list[str]:
        fields = []
        for child in ast.walk(node):
            if isinstance(child, ast.Return) and child.value:
                if isinstance(child.value, ast.Dict):
                    for key in child.value.keys:
                        if isinstance(key, ast.Constant):
                            fields.append(str(key.value))
        return fields

    def _check_endpoint_exists(self, contract: Contract, index: dict) -> list[DriftFinding]:
        key = f"{contract.method}:{contract.path}"
        if key not in index["routes"]:
            return [DriftFinding(
                severity=DriftSeverity.CRITICAL,
                description=f"Endpoint {contract.method} {contract.path} definido na spec mas nao encontrado no codigo",
                spec_reference=f"linha {contract.source_line}",
                code_location="N/A",
                expected=f"{contract.method} {contract.path}",
                actual="nao implementado"
            )]
        return []

    def _check_response_fields(self, contract: Contract, index: dict) -> list[DriftFinding]:
        findings = []
        key = f"{contract.method}:{contract.path}"
        route = index["routes"].get(key)
        if not route or not contract.response_fields:
            return findings

        for field in contract.response_fields:
            if field not in route.get("returns", []):
                findings.append(DriftFinding(
                    severity=DriftSeverity.WARNING,
                    description=f"Campo '{field}' especificado na resposta mas nao encontrado no codigo",
                    spec_reference=f"linha {contract.source_line}",
                    code_location=f"{route['file']}:{route['line']}",
                    expected=f"campo '{field}' presente",
                    actual=f"campos retornados: {route.get('returns', [])}"
                ))
        return findings

    def _check_constraints(self, contract: Contract, index: dict) -> list[DriftFinding]:
        findings = []
        key = f"{contract.method}:{contract.path}"
        route = index["routes"].get(key)
        if not route or not contract.constraints:
            return findings

        for constraint in contract.constraints:
            func_body = self._get_function_body(route["file"], route["name"])
            if func_body and not any(c.lower() in func_body.lower() for c in self._constraint_keywords(constraint)):
                findings.append(DriftFinding(
                    severity=DriftSeverity.WARNING,
                    description=f"Restricao '{constraint[:80]}...' nao verificada no codigo",
                    spec_reference=f"linha {contract.source_line}",
                    code_location=f"{route['file']}:{route['line']}",
                    expected=f"validacao de: {constraint[:60]}",
                    actual="validacao ausente"
                ))
        return findings

    def _check_undocumented_endpoints(self, contracts: list[Contract], index: dict) -> list[DriftFinding]:
        findings = []
        spec_keys = {f"{c.method}:{c.path}" for c in contracts}
        for key, route in index["routes"].items():
            if key not in spec_keys:
                findings.append(DriftFinding(
                    severity=DriftSeverity.INFO,
                    description=f"Endpoint {key} existe no codigo mas nao esta documentado na spec",
                    spec_reference="N/A",
                    code_location=f"{route['file']}:{route['line']}",
                    expected="documentado na spec",
                    actual="apenas no codigo"
                ))
        return findings

    def _get_function_body(self, filepath: str, func_name: str) -> Optional[str]:
        try:
            tree = ast.parse(Path(filepath).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == func_name:
                    return ast.unparse(node)
        except (SyntaxError, FileNotFoundError):
            pass
        return None

    def _constraint_keywords(self, constraint: str) -> list[str]:
        return [w for w in constraint.lower().split() if len(w) > 3]


class BehaviorHasher:
    """Gera hash de comportamento baseado nos testes."""

    def hash_behavior(self, test_output: str) -> str:
        return hashlib.sha256(test_output.encode()).hexdigest()[:16]

    def compare_hashes(self, expected_hash: str, actual_hash: str) -> bool:
        return expected_hash == actual_hash


class SpecDriftDetector:
    """Motor principal de deteccao de drift spec↔codigo."""

    def __init__(self):
        self.extractor = ContractExtractor()
        self.comparator = ASTComparator()
        self.hasher = BehaviorHasher()

    def analyze(self, spec_path: str, code_paths: list[str]) -> DriftReport:
        report = DriftReport(spec_path=spec_path, code_paths=code_paths)

        contracts = self.extractor.extract_contracts(spec_path)
        report.contracts_found = len(contracts)

        if not contracts:
            report.findings.append(DriftFinding(
                severity=DriftSeverity.INFO,
                description="Nenhum contrato extraido da spec",
                spec_reference=spec_path,
                code_location="N/A",
                expected="Contratos de endpoint documentados",
                actual="Nenhum contrato encontrado"
            ))
            return report

        findings = self.comparator.compare(contracts, code_paths)
        report.findings = findings
        report.contracts_matched = sum(1 for c in contracts if not any(
            f.code_location != "N/A" and c.method in f.description and c.path in f.description
            for f in findings if f.severity == DriftSeverity.CRITICAL
        ))
        report.contracts_mismatched = report.contracts_found - report.contracts_matched

        return report

    def ci_gate(self, report: DriftReport, max_warnings: int = 5) -> tuple[bool, str]:
        if report.critical_count > 0:
            return False, f"BLOCKED: {report.critical_count} divergencias criticas encontradas"
        if report.warning_count > max_warnings:
            return False, f"BLOCKED: {report.warning_count} warnings excedem limite de {max_warnings}"
        if report.drift_score > 10:
            return False, f"BLOCKED: drift score {report.drift_score} > 10"
        return True, f"PASS: drift score {report.drift_score} dentro do limite"


def generate_drift_report_markdown(report: DriftReport) -> str:
    lines = [
        f"# Drift Report: {Path(report.spec_path).name}",
        "",
        f"| Metrica | Valor |",
        f"|---------|-------|",
        f"| Contratos encontrados | {report.contracts_found} |",
        f"| Contratos correspondidos | {report.contracts_matched} |",
        f"| Contratos divergentes | {report.contracts_mismatched} |",
        f"| Divergencias criticas | {report.critical_count} |",
        f"| Warnings | {report.warning_count} |",
        f"| Informacoes | {report.info_count} |",
        f"| **Drift Score** | **{report.drift_score}** |",
        f"| Status | {'PASS' if report.passed else 'FAIL'} |",
        "",
    ]

    if report.findings:
        lines.append("## Divergencias Encontradas")
        lines.append("")
        for i, f in enumerate(report.findings, 1):
            severity_icon = {"critical": "CRITICAL", "warning": "WARNING", "info": "INFO"}
            lines.extend([
                f"### {i}. [{severity_icon.get(f.severity.value, f.severity.value)}] {f.description}",
                f"- **Spec:** {f.spec_reference}",
                f"- **Codigo:** {f.code_location}",
                f"- **Esperado:** {f.expected}",
                f"- **Encontrado:** {f.actual}",
                "",
            ])

    return "\n".join(lines)
