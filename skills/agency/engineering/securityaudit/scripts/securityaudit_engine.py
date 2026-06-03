"""SecurityAuditEngine — Static security analysis for source code.

Extracted from agency-agents/engineering/engineering-security-engineer.md
Round 14 Evolution — Agency Engineering Domain
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SecretsReport:
    secrets: list[dict]
    count: int
    available: bool = True


@dataclass
class InjectionReport:
    vulnerabilities: list[dict]
    count: int
    available: bool = True


@dataclass
class XSSReport:
    vulnerabilities: list[dict]
    count: int
    available: bool = True


@dataclass
class AuthAudit:
    issues: list[dict]
    score: int
    available: bool = True


class SecurityAuditEngine:
    """Detects secrets, injection vulnerabilities, XSS, and auth weaknesses."""

    SECRET_PATTERNS = [
        (r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{16,})['\"]",
         'API key hardcoded'),
        (r"(?i)(secret|password|passwd)\s*[:=]\s*['\"]([^'\"]{4,})['\"]",
         'Secret/password hardcoded'),
        (r"(?i)(token|auth[_-]?token)\s*[:=]\s*['\"]([a-zA-Z0-9_\-\.]{12,})['\"]",
         'Auth token hardcoded'),
        (r'(?i)(ghp|github[_-]?pat)[_a-z0-9]{20,}',
         'GitHub personal access token'),
        (r'(?i)sk-[a-zA-Z0-9]{32,}',
         'OpenAI API key pattern'),
        (r'(?i)-----BEGIN\s+(RSA|EC|DSA|OPENSSH)\s+PRIVATE\s+KEY-----',
         'Private key embedded in source'),
        (r'(?i)jdbc:[^:]+://[^/]+/[^\s\'"]+',
         'JDBC connection string may contain credentials'),
        (r'(?i)mongodb(?:\+srv)?://[^/]+/[^\s\'"]+',
         'MongoDB connection string may contain credentials'),
    ]

    SQLI_PATTERNS = [
        (r'(?i)(?:execute|cursor\.execute)\s*\(\s*f["\']',
         'f-string used in SQL execution — SQL injection risk'),
        (r'(?i)["\']\s*SELECT\s+.+\s*FROM\s+.+\s*WHERE\s+.+\{\s*\w+\s*\}',
         'String interpolation in SQL WHERE clause'),
        (r'(?i)["\']\s*(?:INSERT|UPDATE|DELETE)\s+.+\{\s*\w+\s*\}',
         'String interpolation in SQL DML statement'),
        (r'(?i)\.format\s*\(\s*.*\)\s*\)?\s*$',
         '.format() near SQL execute — injection risk'),
        (r'(?i)["\']\s*SELECT\s+.+\+.*\+',
         'String concatenation in SQL query'),
    ]

    XSS_SINKS = [
        (r'\.innerHTML\s*=', 'innerHTML assignment — XSS sink'),
        (r'dangerouslySetInnerHTML', 'React dangerouslySetInnerHTML — XSS sink'),
        (r'document\.write\s*\(', 'document.write() — XSS sink'),
        (r'\.outerHTML\s*=', 'outerHTML assignment — XSS sink'),
        (r'(?i)eval\s*\(\s*.*\+', 'eval with concatenation — potential XSS/RCE'),
        (r'insertAdjacentHTML\s*\(', 'insertAdjacentHTML — XSS sink'),
    ]

    AUTH_PATTERNS = [
        (r"(?i)password\s*==\s*['\"]",
         'Plaintext password comparison', 'HIGH'),
        (r'(?i)jwt\.(sign|encode)\s*\([^)]*,\s*[^,)]*\)',
         'JWT — check for expiration', 'MEDIUM'),
        (r"(?i)set_?cookie\s*\([^)]*httponly\s*=\s*false",
         'Cookie set without HttpOnly flag', 'HIGH'),
        (r"(?i)set_?cookie\s*\([^)]*secure\s*=\s*false",
         'Cookie set without Secure flag', 'HIGH'),
        (r'(?i)session\[.+\]\s*=',
         'Session variable assignment — ensure server-side validation', 'LOW'),
        (r'(?i)(?:hashlib\.|hash\s*=|=\s*)?md5\s*\(',
         'MD5 used for password hashing — use bcrypt/argon2', 'HIGH'),
        (r'(?i)(?:hashlib\.|hash\s*=|=\s*)?sha1\s*\(',
         'SHA1 used for password hashing — use bcrypt/argon2', 'HIGH'),
    ]

    @property
    def available(self) -> bool:
        return True

    def detect_secrets(self, source: str) -> SecretsReport:
        secrets: list[dict] = []
        lines = source.split('\n')

        for i, line in enumerate(lines):
            for pattern, description in self.SECRET_PATTERNS:
                if re.search(pattern, line):
                    secrets.append({
                        'line': i + 1,
                        'variable': self._extract_variable(line),
                        'pattern': description,
                        'severity': 'HIGH',
                    })
                    break

        return SecretsReport(secrets=secrets, count=len(secrets))

    def detect_sql_injection(self, source: str) -> InjectionReport:
        vulnerabilities: list[dict] = []
        lines = source.split('\n')

        for i, line in enumerate(lines):
            for pattern, description in self.SQLI_PATTERNS:
                if re.search(pattern, line):
                    vulnerabilities.append({
                        'line': i + 1,
                        'type': 'sql_injection',
                        'snippet': line.strip()[:150],
                        'severity': 'HIGH',
                    })
                    break

        return InjectionReport(
            vulnerabilities=vulnerabilities, count=len(vulnerabilities)
        )

    def detect_xss(self, source: str) -> XSSReport:
        vulnerabilities: list[dict] = []
        lines = source.split('\n')

        for i, line in enumerate(lines):
            for pattern, description in self.XSS_SINKS:
                if re.search(pattern, line):
                    context = 'DOM'
                    if 'React' in source or 'jsx' in source.lower():
                        context = 'React'
                    elif 'angular' in source.lower():
                        context = 'Angular'
                    vulnerabilities.append({
                        'line': i + 1,
                        'sink': description,
                        'context': context,
                        'severity': 'MEDIUM',
                    })
                    break

        return XSSReport(vulnerabilities=vulnerabilities, count=len(vulnerabilities))

    def audit_authentication(self, source: str) -> AuthAudit:
        issues: list[dict] = []
        lines = source.split('\n')

        for i, line in enumerate(lines):
            for pattern, description, severity in self.AUTH_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'line': i + 1,
                        'category': 'authentication',
                        'description': description,
                        'severity': severity,
                    })
                    break

        score = max(0, 100 - len(issues) * 10)
        return AuthAudit(issues=issues, score=score)

    def _extract_variable(self, line: str) -> str:
        m = re.match(r'\s*(\w+(?:\s*[:=]\s*)?)', line)
        if m:
            return m.group(1).rstrip(' =:').strip()
        return 'unknown'
