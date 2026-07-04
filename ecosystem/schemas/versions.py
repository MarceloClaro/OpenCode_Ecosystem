"""
Versionamento semântico para schemas de estado.

Formato: MAJOR.MINOR.PATCH
- MAJOR: Quebra de compatibilidade retroativa
- MINOR: Campo obrigatório adicionado, tipo relaxado
- PATCH: Campo opcional adicionado, documentação
"""

from __future__ import annotations

import re


class SemanticVersion:
    """Versão semântica MAJOR.MINOR.PATCH."""

    PATTERN = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

    def __init__(self, major: int, minor: int, patch: int):
        self.major = major
        self.minor = minor
        self.patch = patch

    @classmethod
    def parse(cls, version_str: str) -> SemanticVersion:
        """Parse de string de versão.

        Args:
            version_str: String no formato "MAJOR.MINOR.PATCH"

        Returns:
            SemanticVersion

        Raises:
            ValueError: Se formato inválido
        """
        match = cls.PATTERN.match(version_str.strip())
        if not match:
            raise ValueError(
                f"Versão inválida: '{version_str}'. "
                f"Formato esperado: MAJOR.MINOR.PATCH"
            )
        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
        )

    def bump_major(self) -> SemanticVersion:
        """Incrementa MAJOR (zera MINOR e PATCH)."""
        return SemanticVersion(self.major + 1, 0, 0)

    def bump_minor(self) -> SemanticVersion:
        """Incrementa MINOR (zera PATCH)."""
        return SemanticVersion(self.major, self.minor + 1, 0)

    def bump_patch(self) -> SemanticVersion:
        """Incrementa PATCH."""
        return SemanticVersion(self.major, self.minor, self.patch + 1)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return f"SemanticVersion({self.major}, {self.minor}, {self.patch})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
        )

    def __lt__(self, other: SemanticVersion) -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        return self.patch < other.patch

    def __le__(self, other: SemanticVersion) -> bool:
        return self < other or self == other

    def __gt__(self, other: SemanticVersion) -> bool:
        return not self <= other

    def __ge__(self, other: SemanticVersion) -> bool:
        return not self < other
