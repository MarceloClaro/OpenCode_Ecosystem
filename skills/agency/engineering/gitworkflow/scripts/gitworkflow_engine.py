"""GitWorkflowEngine — Validates Git branches, commits, and merge strategies.

Extracted from agency-agents/engineering/engineering-git-workflow-master.md
Round 14 Evolution — Agency Engineering Domain
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BranchValidation:
    valid: bool
    category: str
    ticket: str
    errors: list[str]
    available: bool = True


@dataclass
class CommitValidation:
    valid: bool
    type: str
    scope: str
    breaking: bool
    description: str
    errors: list[str]
    available: bool = True


@dataclass
class AtomicityReport:
    non_atomic: list[dict]
    score: float
    available: bool = True


@dataclass
class MergeStrategyReport:
    strategy_detected: str
    recommendation: str
    issues: list[str]
    available: bool = True


class GitWorkflowEngine:
    """Validates Git branch names, commit messages, and atomicity."""

    VALID_CATEGORIES = {
        'feat', 'fix', 'chore', 'docs', 'refactor', 'test',
        'style', 'perf', 'ci', 'build', 'revert', 'hotfix',
        'release', 'wip', 'experiment',
    }

    CONVENTIONAL_COMMIT_RE = re.compile(
        r'^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s+(?P<description>.+)$'
    )

    TICKET_RE = re.compile(r'(?:[A-Z]+-\d+|#\d+)')

    @property
    def available(self) -> bool:
        return True

    def validate_branch_name(self, branch_name: str) -> BranchValidation:
        errors: list[str] = []
        category = ''
        ticket = ''

        parts = branch_name.split('/')
        if len(parts) < 2:
            errors.append('Branch name must have format: category/description')
        else:
            category = parts[0].lower()
            if category not in self.VALID_CATEGORIES:
                errors.append(
                    f'Invalid category "{category}". Valid: {sorted(self.VALID_CATEGORIES)}'
                )

            rest = '/'.join(parts[1:])
            ticket_match = self.TICKET_RE.search(rest)
            if ticket_match:
                ticket = ticket_match.group(0)
            else:
                errors.append('No ticket reference found (e.g., SCRUM-123 or #456)')

        if '/' not in branch_name:
            errors.append('Branch name must contain at least one / separator')

        return BranchValidation(
            valid=len(errors) == 0,
            category=category,
            ticket=ticket,
            errors=errors,
        )

    def validate_commit_message(self, message: str) -> CommitValidation:
        errors: list[str] = []
        m = self.CONVENTIONAL_COMMIT_RE.match(message.strip())
        if not m:
            return CommitValidation(
                valid=False,
                type='',
                scope='',
                breaking=False,
                description='',
                errors=['Not a valid Conventional Commit format. Expected: type(scope): description'],
            )

        commit_type = m.group('type')
        scope = m.group('scope') or ''
        breaking = m.group('breaking') is not None
        description = m.group('description').strip()

        if commit_type not in self.VALID_CATEGORIES:
            errors.append(f'Unknown type "{commit_type}". Valid: {sorted(self.VALID_CATEGORIES)}')

        if len(description) < 5:
            errors.append('Description too short (min 5 characters)')

        if breaking and '!' not in message[:message.index(':')]:
            errors.append('Breaking change marker "!" should appear before ":"')

        return CommitValidation(
            valid=len(errors) == 0,
            type=commit_type,
            scope=scope,
            breaking=breaking,
            description=description,
            errors=errors,
        )

    def detect_non_atomic(self, commits: list[dict]) -> AtomicityReport:
        non_atomic: list[dict] = []
        total = max(len(commits), 1)

        for commit in commits:
            files = commit.get('files', [])
            domains: set[str] = set()

            for f in files:
                parts = f.split('/')
                if len(parts) > 1:
                    domains.add(parts[0])
                elif len(parts) == 1:
                    ext = f.rsplit('.', 1)[-1] if '.' in f else f
                    domains.add(ext)

            reasons: list[str] = []
            if len(domains) > 3:
                reasons.append(f'Touches {len(domains)} distinct domains')
            if len(files) > 15:
                reasons.append(f'Touches {len(files)} files')
            if len(files) > 3 and len(domains) == 1:
                pass
            elif len(files) > 8:
                reasons.append('Large commit spanning many files')

            if reasons:
                non_atomic.append({
                    'hash': commit.get('hash', 'unknown'),
                    'files_count': len(files),
                    'domains': sorted(domains),
                    'reason': '; '.join(reasons),
                })

        score = 1.0 - (len(non_atomic) / total)
        return AtomicityReport(non_atomic=non_atomic, score=round(score, 2))

    def analyze_merge_strategy(self, git_log: str) -> MergeStrategyReport:
        lines = git_log.strip().split('\n')
        merge_count = 0
        squash_count = 0
        rebase_count = 0
        issues: list[str] = []

        for line in lines:
            if 'Merge' in line and 'pull request' in line.lower():
                merge_count += 1
            if 'Squash' in line:
                squash_count += 1

        if merge_count > 0 and squash_count == 0:
            strategy = 'merge'
            if merge_count > 10:
                issues.append('Heavy use of merge commits may clutter history')
        elif squash_count > merge_count:
            strategy = 'squash'
            if squash_count > 20:
                issues.append('Many squash commits — consider grouping related work')
        else:
            strategy = 'mixed'

        if merge_count == 0 and squash_count == 0:
            strategy = 'rebase_or_fast_forward'
            recommendation = (
                'Linear history detected. Ensure merge commits are used '
                'for significant feature integrations.'
            )
        elif strategy == 'merge':
            recommendation = (
                'Consider using squash merges for feature branches to '
                'maintain a cleaner mainline history.'
            )
        elif strategy == 'squash':
            recommendation = (
                'Squash strategy in use. Good for clean history. Consider '
                'preserving context in merge commits for large features.'
            )
        else:
            recommendation = (
                'Mixed strategy detected. Standardize on one strategy '
                '(squash for features, merge for releases).'
            )

        return MergeStrategyReport(
            strategy_detected=strategy,
            recommendation=recommendation,
            issues=issues,
        )
