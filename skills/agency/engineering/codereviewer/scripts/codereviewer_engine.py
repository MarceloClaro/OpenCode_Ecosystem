"""CodeReviewer Engine — Rule-based code review analysis.

Extracted from agency-agents/engineering/engineering-code-reviewer.md
Round 14 Evolution — Agency Engineering Domain
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CyclomaticComplexity:
    total_score: int
    violations: list[dict]
    available: bool = True


@dataclass
class SmellReport:
    smells: list[dict]
    count: int
    available: bool = True


@dataclass
class SecurityIssues:
    issues: list[dict]
    critical_count: int
    available: bool = True


@dataclass
class DuplicationReport:
    duplicates: list[dict]
    duplicated_line_count: int
    available: bool = True


class CodeReviewer:
    """Analyzes source code for complexity, smells, security, and duplication."""

    COMPLEXITY_THRESHOLD = 10
    GOD_FUNCTION_LINES = 50
    MAX_PARAMS = 5
    MIN_NAME_LENGTH = 3

    INSECURE_PATTERNS = [
        (r'\beval\s*\(', 'eval() usage — arbitrary code execution risk', 'CRITICAL'),
        (r'\bexec\s*\(', 'exec() usage — arbitrary code execution risk', 'CRITICAL'),
        (r'\bos\.system\s*\(', 'os.system() — shell injection risk', 'HIGH'),
        (r'\bsubprocess\.(call|Popen)\s*\([^)]*shell\s*=\s*True',
         'subprocess with shell=True — shell injection risk', 'HIGH'),
        (r"(?i)(api[_-]?key|secret|password|token)\s*=\s*['\"][^'\"]{8,}['\"]",
         'Hardcoded secret/credential detected', 'HIGH'),
        (r'\bpickle\.(loads|load)\s*\(', 'pickle deserialization — RCE risk', 'MEDIUM'),
        (r'\byaml\.load\s*\(', 'yaml.load() without SafeLoader — RCE risk', 'MEDIUM'),
        (r'\binput\s*\(', 'input() may indicate unsanitized user input', 'LOW'),
    ]

    CODE_SMELL_PATTERNS = {
        'too_many_params': r'def\s+(\w+)\s*\([^)]*\)',
        'short_name': r'\bdef\s+(\w{1,2})\s*\(',
        'nested_conditionals': None,
    }

    @property
    def available(self) -> bool:
        return True

    def analyze_complexity(self, source: str) -> CyclomaticComplexity:
        branches = re.findall(
            r'\b(if|elif|for|while|except|and\b|or\b)\b', source
        )
        base = 1
        total = base + len(branches)
        violations: list[dict] = []

        func_pattern = re.compile(
            r'(?:^|\n)\s*def\s+(\w+)\s*\([^)]*\)\s*:', re.MULTILINE
        )
        funcs = list(func_pattern.finditer(source))
        for i, match in enumerate(funcs):
            start = match.end()
            end = (
                funcs[i + 1].start() if i + 1 < len(funcs) else len(source)
            )
            body = source[start:end]
            body_branches = len(re.findall(
                r'\b(if|elif|for|while|except|and\b|or\b)\b', body
            ))
            score = 1 + body_branches
            if score > self.COMPLEXITY_THRESHOLD:
                violations.append({
                    'name': match.group(1),
                    'line': source[:match.start()].count('\n') + 1,
                    'score': score,
                    'threshold': self.COMPLEXITY_THRESHOLD,
                })

        return CyclomaticComplexity(total_score=total, violations=violations)

    def detect_smells(self, source: str) -> SmellReport:
        smells: list[dict] = []
        lines = source.split('\n')

        func_pattern = re.compile(r'^\s*def\s+(\w+)\s*\(([^)]*)\)')
        func_starts: list[dict] = []
        for i, line in enumerate(lines):
            m = func_pattern.match(line)
            if m:
                func_starts.append({
                    'name': m.group(1), 'line': i + 1,
                    'params': m.group(2), 'end': None
                })

        for idx, fs in enumerate(func_starts):
            start = fs['line']
            end_line = None
            if idx + 1 < len(func_starts):
                end_line = func_starts[idx + 1]['line'] - 1
            else:
                end_line = len(lines)
            length = end_line - start
            if length > self.GOD_FUNCTION_LINES:
                smells.append({
                    'type': 'god_function',
                    'name': fs['name'],
                    'line': start,
                    'message': f'Function spans {length} lines (threshold: {self.GOD_FUNCTION_LINES})',
                })

            params = [p.strip() for p in fs['params'].split(',') if p.strip()]
            if len(params) > self.MAX_PARAMS:
                smells.append({
                    'type': 'too_many_params',
                    'name': fs['name'],
                    'line': start,
                    'message': f'Function has {len(params)} params (threshold: {self.MAX_PARAMS})',
                })

            if len(fs['name']) < self.MIN_NAME_LENGTH:
                smells.append({
                    'type': 'short_name',
                    'name': fs['name'],
                    'line': start,
                    'message': f'Function name too short ({len(fs["name"])} chars, min: {self.MIN_NAME_LENGTH})',
                })

        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if stripped.startswith('#'):
                continue
            depth = (len(line) - len(stripped)) // 4
            if depth > 4:
                smells.append({
                    'type': 'deep_nesting',
                    'name': f'line_{i + 1}',
                    'line': i + 1,
                    'message': f'Nesting depth {depth} exceeds recommended maximum of 4',
                })

        return SmellReport(smells=smells, count=len(smells))

    def detect_security_issues(self, source: str) -> SecurityIssues:
        issues: list[dict] = []
        critical_count = 0
        lines = source.split('\n')

        for pattern, description, severity in self.INSECURE_PATTERNS:
            for i, line in enumerate(lines):
                if re.search(pattern, line):
                    issues.append({
                        'line': i + 1,
                        'pattern': description,
                        'severity': severity,
                        'snippet': line.strip()[:120],
                    })
                    if severity == 'CRITICAL':
                        critical_count += 1

        return SecurityIssues(issues=issues, critical_count=critical_count)

    def detect_duplication(self, source: str) -> DuplicationReport:
        lines = source.split('\n')
        non_empty = [(i, line.strip()) for i, line in enumerate(lines)
                     if line.strip() and not line.strip().startswith('#')]
        duplicates: list[dict] = []
        seen: set[tuple[int, int]] = set()
        block_size = 5

        for i in range(len(non_empty) - block_size):
            for j in range(i + block_size, len(non_empty) - block_size + 1):
                block_a = tuple(
                    non_empty[k][1] for k in range(i, i + block_size)
                )
                block_b = tuple(
                    non_empty[k][1] for k in range(j, j + block_size)
                )
                if block_a == block_b and (i, j) not in seen:
                    seen.add((i, j))
                    duplicates.append({
                        'block_a': (non_empty[i][0] + 1, non_empty[i + block_size - 1][0] + 1),
                        'block_b': (non_empty[j][0] + 1, non_empty[j + block_size - 1][0] + 1),
                        'similarity': 1.0,
                        'lines': block_size,
                    })

        dup_lines = sum(d['lines'] * 2 for d in duplicates)
        return DuplicationReport(
            duplicates=duplicates, duplicated_line_count=dup_lines
        )
