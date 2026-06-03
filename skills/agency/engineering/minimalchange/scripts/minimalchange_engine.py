"""MinimalChangeEngine — Validates diffs for minimality and scope discipline.

Extracted from agency-agents/engineering/engineering-minimal-change-engineer.md
Round 14 Evolution — Agency Engineering Domain
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScopeCheck:
    in_scope: list[str]
    out_of_scope: list[str]
    violation: bool
    available: bool = True


@dataclass
class RefactorDetection:
    suspicious_renames: list[dict]
    risk_score: int
    available: bool = True


@dataclass
class DiffEntropy:
    files_changed: int
    hunks_count: int
    lines_added: int
    lines_removed: int
    entropy_score: int
    available: bool = True


@dataclass
class ChangeRatio:
    functional_changes: int
    cosmetic_changes: int
    ratio: float
    warning: bool
    available: bool = True


class MinimalChangeEngine:
    """Analyzes diffs for scope creep, premature refactoring, and noise."""

    COSMETIC_PATTERNS = [
        r'^[-+]\s*$',
        r'^[-+]\s*#',
        r'^[-+]\s*//',
        r'^[-+]\s*/\*',
        r'^[-+]\s*\*',
        r'^\+\s*$',
        r'^\+\s*import\s',
        r'^\+\s*from\s+\S+\s+import',
    ]

    RENAME_PATTERNS = [
        (r'^-(.*\b)(\w+)(\s*=.*)$', r'^\+(.*\b)(\w+)(\s*=.*)$'),
    ]

    DIFF_FILE_RE = re.compile(r'^diff --git a/(.+) b/(.+)$|^--- a/(.+)$|^\+\+\+ b/(.+)$')

    @property
    def available(self) -> bool:
        return True

    def check_scope(self, diff_text: str, scope_files: list[str]) -> ScopeCheck:
        touched_files: list[str] = []
        for line in diff_text.split('\n'):
            m = re.match(r'^diff --git a/(\S+) b/', line)
            if m:
                touched_files.append(m.group(1))
                continue
            m = re.match(r'^\+\+\+ b/(\S+)', line)
            if m:
                fname = m.group(1)
                if fname not in touched_files:
                    touched_files.append(fname)

        touched_set = {f.rstrip('/') for f in touched_files}
        scope_set = {s.rstrip('/') for s in scope_files}

        in_scope = sorted(touched_set & scope_set)
        out_of_scope = sorted(touched_set - scope_set)

        return ScopeCheck(
            in_scope=in_scope,
            out_of_scope=out_of_scope,
            violation=len(out_of_scope) > 0,
        )

    def detect_premature_refactor(self, diff_text: str) -> RefactorDetection:
        suspicious: list[dict] = []
        lines = diff_text.split('\n')
        risk_score = 0

        rename_pairs: list[tuple[str, str, int]] = []
        for i, line in enumerate(lines):
            m = re.match(r'^-\s*(.+)$', line)
            if m:
                old = m.group(1).strip()
                if re.match(r'^\s*(\w+)\s*=\s*', old):
                    for j in range(i + 1, min(i + 5, len(lines))):
                        m2 = re.match(r'^\+\s*(.+)$', lines[j])
                        if m2 and re.match(r'^\s*(\w+)\s*=\s*', m2.group(1).strip()):
                            rename_pairs.append((old, m2.group(1).strip(), i + 1))
                            break

            if re.match(r'^-\s*def\s+(\w+)', line):
                old_name = re.match(r'^-\s*def\s+(\w+)', line)
                for j in range(i + 1, min(i + 5, len(lines))):
                    m2 = re.match(r'^\+\s*def\s+(\w+)', lines[j])
                    if m2 and old_name:
                        if old_name.group(1) != m2.group(1):
                            suspicious.append({
                                'old_name': old_name.group(1),
                                'new_name': m2.group(1),
                                'line': i + 1,
                                'reason': 'Function renamed without clear justification',
                            })
                            risk_score += 20
                        break

            if re.match(r'^-\s*class\s+(\w+)', line):
                old_cls = re.match(r'^-\s*class\s+(\w+)', line)
                for j in range(i + 1, min(i + 5, len(lines))):
                    m2 = re.match(r'^\+\s*class\s+(\w+)', lines[j])
                    if m2 and old_cls:
                        if old_cls.group(1) != m2.group(1):
                            suspicious.append({
                                'old_name': old_cls.group(1),
                                'new_name': m2.group(1),
                                'line': i + 1,
                                'reason': 'Class renamed without clear justification',
                            })
                            risk_score += 25
                        break

        whitespace_changes = sum(
            1 for line in lines
            if (line.startswith('+') and line[1:].strip() == '')
            or (line.startswith('-') and line[1:].strip() == '')
        )
        risk_score += whitespace_changes * 2

        return RefactorDetection(
            suspicious_renames=suspicious,
            risk_score=min(risk_score, 100),
        )

    def measure_entropy(self, diff_text: str) -> DiffEntropy:
        files_changed = 0
        hunks_count = 0
        lines_added = 0
        lines_removed = 0

        for line in diff_text.split('\n'):
            if line.startswith('diff --git'):
                files_changed += 1
            if line.startswith('@@'):
                hunks_count += 1
            if line.startswith('+') and not line.startswith('+++'):
                lines_added += 1
            if line.startswith('-') and not line.startswith('---'):
                lines_removed += 1

        total_lines = lines_added + lines_removed
        if files_changed == 0:
            entropy = 0
        else:
            lines_per_file = total_lines / max(files_changed, 1)
            entropy = min(
                int((hunks_count * 10 + lines_per_file * files_changed) / 2),
                100,
            )

        return DiffEntropy(
            files_changed=files_changed,
            hunks_count=hunks_count,
            lines_added=lines_added,
            lines_removed=lines_removed,
            entropy_score=entropy,
        )

    def validate_change_ratio(self, diff_text: str) -> ChangeRatio:
        functional = 0
        cosmetic = 0

        for line in diff_text.split('\n'):
            if not (line.startswith('+') or line.startswith('-')):
                continue
            if line.startswith('+++') or line.startswith('---'):
                continue

            stripped = line[1:].strip()
            is_cosmetic = any(
                re.match(p, line) for p in self.COSMETIC_PATTERNS
            )
            if is_cosmetic or stripped == '':
                cosmetic += 1
            else:
                functional += 1

        total = functional + cosmetic
        ratio = functional / max(total, 1)
        return ChangeRatio(
            functional_changes=functional,
            cosmetic_changes=cosmetic,
            ratio=ratio,
            warning=ratio < 0.3,
        )
