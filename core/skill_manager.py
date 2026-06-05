"""
core/skill_manager.py — Gerenciamento de Skills com DI.

Descoberta, carregamento e execução de skills do ecossistema.
Skills são instruções especializadas (.md) que guiam agentes na
execução de tarefas específicas.

Uso com DI (novo):
    container = Container.instance()
    mgr = SkillManager(container=container)
    mgr.discover()
    skill = mgr.get_skill("python-pro")

Uso legado (compatível):
    mgr = SkillManager()
    mgr.discover()
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from core.config import settings
from core.errors import SkillError, NotFoundError

logger = logging.getLogger(__name__)


@dataclass
class SkillMeta:
    """Metadados de uma skill extraídos do SKILL.md."""
    name: str
    description: str = ""
    file_path: Optional[Path] = None
    keywords: list[str] = field(default_factory=list)
    category: str = "general"
    version: str = "1.0.0"
    size_bytes: int = 0


@dataclass
class SkillInstance:
    """Representa uma skill carregada."""
    meta: SkillMeta
    content: str = ""
    loaded: bool = False


class SkillManager:
    """Gerenciador de skills do ecossistema.

    Responsável por:
    - Descobrir skills em diretórios do sistema
    - Carregar SKILL.md e extrair metadados
    - Matching por palavras-chave para trigger automático
    - Indexação para busca rápida
    """

    SKILL_FILENAME = "SKILL.md"
    # Padrão para extrair nome e descrição do frontmatter ou heading
    _HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
    _DESC_RE = re.compile(r'^description:\s*["\']?(.+?)["\']?$', re.MULTILINE)

    def __init__(self, container: Any = None) -> None:
        self._skills: dict[str, SkillInstance] = {}
        self._search_dirs: list[Path] = []
        self._keyword_index: dict[str, list[str]] = {}
        self._container = container

        # Auto-registro no Container DI
        if container is not None and not container.is_registered('skill_manager'):
            container.register('skill_manager', self)

    # ── Descoberta ─────────────────────────────────────────────────

    def add_search_dir(self, directory: str | Path) -> None:
        """Adiciona diretório para busca de skills."""
        path = Path(directory)
        if path.exists() and path.is_dir():
            self._search_dirs.append(path.resolve())
            logger.debug("Added skill search dir: %s", path)

    def discover(self, directories: Optional[list[str | Path]] = None) -> list[str]:
        """Descobre skills nos diretórios configurados.

        Args:
            directories: Diretórios adicionais para busca.

        Returns:
            Lista de nomes de skills encontradas.
        """
        if directories:
            for d in directories:
                self.add_search_dir(d)

        # Adiciona diretório padrão se vazio
        if not self._search_dirs:
            self.add_search_dir(settings.SKILLS_DIR)

        found: list[str] = []
        for search_dir in self._search_dirs:
            if not search_dir.exists():
                continue
            # Procura SKILL.md em subdiretórios (cada skill é um diretório)
            for skill_dir in search_dir.iterdir():
                if not skill_dir.is_dir():
                    continue
                skill_file = skill_dir / self.SKILL_FILENAME
                if not skill_file.exists():
                    continue
                name = skill_dir.name
                if name not in self._skills:
                    self._skills[name] = SkillInstance(
                        meta=SkillMeta(name=name, file_path=skill_file)
                    )
                    found.append(name)

        if found:
            logger.info("Discovered %d skills", len(found))
        return found

    # ── Carregamento ───────────────────────────────────────────────

    def load(self, name: str) -> bool:
        """Carrega o conteúdo e metadados de uma skill.

        Args:
            name: Nome da skill.

        Raises:
            NotFoundError: Se a skill não existir.
            SkillError: Se o arquivo SKILL.md não for encontrado.
        """
        skill = self._skills.get(name)
        if skill is None:
            raise NotFoundError(f"Skill '{name}' not found")

        if skill.loaded:
            return True

        path = skill.meta.file_path
        if path is None or not path.exists():
            raise SkillError(f"SKILL.md not found for '{name}' at {path}")

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            skill.content = content
            skill.meta.size_bytes = len(content.encode("utf-8"))

            # Extrai metadados
            self._extract_metadata(skill)

            skill.loaded = True
            logger.info(
                "Loaded skill '%s' (%s, %d bytes)",
                name, skill.meta.category, skill.meta.size_bytes,
            )
            return True

        except OSError as e:
            raise SkillError(f"Failed to read SKILL.md for '{name}': {e}") from e

    def load_all(self) -> int:
        """Carrega todas as skills descobertas."""
        count = 0
        for name in list(self._skills.keys()):
            try:
                if self.load(name):
                    count += 1
            except (SkillError, NotFoundError) as e:
                logger.warning("Skipping skill '%s': %s", name, e)
        logger.info("Loaded %d/%d skills", count, len(self._skills))
        return count

    def reload(self, name: str) -> bool:
        """Recarrega uma skill."""
        skill = self._skills.get(name)
        if skill:
            skill.loaded = False
            skill.content = ""
        return self.load(name)

    # ── Matching ───────────────────────────────────────────────────

    def match_skill(self, query: str, min_score: float = 0.3) -> list[tuple[str, float]]:
        """Encontra skills relevantes para uma consulta.

        Usa correspondência por palavras-chave e termos da descrição.
        Retorna lista de (nome, score) ordenada por relevância.

        Args:
            query: Texto da consulta.
            min_score: Score mínimo para incluir no resultado.

        Returns:
            Lista de tuplas (nome_da_skill, score) ordenada.
        """
        if not self._keyword_index:
            self._build_keyword_index()

        query_lower = query.lower()
        query_terms = set(re.findall(r"[a-z0-9-]+", query_lower))
        results: list[tuple[str, float]] = []

        for name, skill in self._skills.items():
            score = 0.0
            meta = skill.meta

            # Match por nome exato
            if name.lower() in query_lower:
                score += 0.5

            # Match por palavras-chave
            for kw in meta.keywords:
                if kw.lower() in query_lower:
                    score += 0.3

            # Match por termos individuais
            skill_terms = set(
                re.findall(r"[a-z0-9-]+", (name + " " + meta.description).lower())
            )
            common = query_terms & skill_terms
            if common:
                score += 0.1 * len(common)

            if score >= min_score:
                results.append((name, round(min(score, 1.0), 2)))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def find_best_skill(self, query: str) -> Optional[str]:
        """Encontra a skill mais relevante para uma consulta."""
        matches = self.match_skill(query)
        return matches[0][0] if matches else None

    # ── Consultas ──────────────────────────────────────────────────

    def get_skill(self, name: str) -> Optional[SkillInstance]:
        """Retorna uma skill pelo nome."""
        return self._skills.get(name)

    def get_content(self, name: str) -> Optional[str]:
        """Retorna o conteúdo bruto de uma skill."""
        skill = self._skills.get(name)
        return skill.content if skill and skill.loaded else None

    def list_skills(self, category: Optional[str] = None) -> list[SkillMeta]:
        """Lista metadados das skills, opcionalmente filtrados por categoria."""
        result = [s.meta for s in self._skills.values()]
        if category:
            result = [m for m in result if m.category == category]
        return sorted(result, key=lambda m: m.name)

    def get_categories(self) -> list[str]:
        """Lista categorias únicas de todas as skills."""
        cats: set[str] = set()
        for s in self._skills.values():
            if s.meta.category:
                cats.add(s.meta.category)
        return sorted(cats)

    @property
    def count(self) -> int:
        return len(self._skills)

    @property
    def loaded_count(self) -> int:
        return sum(1 for s in self._skills.values() if s.loaded)

    # ── Métodos Internos ───────────────────────────────────────────

    def _extract_metadata(self, skill: SkillInstance) -> None:
        """Extrai metadados do conteúdo da skill."""
        content = skill.content

        # Descrição (frontmatter)
        desc_match = self._DESC_RE.search(content)
        if desc_match:
            skill.meta.description = desc_match.group(1).strip()

        # Heading principal como fallback para descrição
        if not skill.meta.description:
            heading_match = self._HEADING_RE.search(content)
            if heading_match:
                skill.meta.description = heading_match.group(1).strip()

        # Palavras-chave do nome e descrição
        text = f"{skill.meta.name} {skill.meta.description}"
        skill.meta.keywords = list(set(
            re.findall(r"[a-zA-Z][a-zA-Z0-9-]{2,}", text)
        ))

        # Categoria (usa o diretório pai do search dir como categoria)
        if skill.meta.file_path:
            relative = skill.meta.file_path.parent.relative_to(
                skill.meta.file_path.parent.parent,
                walk_up=True,
            )
            skill.meta.category = relative.parts[0] if relative.parts else "general"

    def _build_keyword_index(self) -> None:
        """Constrói índice de palavras-chave para matching rápido."""
        self._keyword_index.clear()
        for name, skill in self._skills.items():
            for kw in skill.meta.keywords:
                kw_lower = kw.lower()
                if kw_lower not in self._keyword_index:
                    self._keyword_index[kw_lower] = []
                self._keyword_index[kw_lower].append(name)

    def __repr__(self) -> str:
        return (
            f"SkillManager(skills={self.count}, loaded={self.loaded_count}, "
            f"categories={len(self.get_categories())})"
        )
