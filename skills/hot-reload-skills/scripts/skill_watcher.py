"""
Hot-Reload Skill System — Carregamento dinamico de skills sem reinicializacao.

Extraido de SandeClaw (specs/architecture.md secao 2.3, PRD.md metricas).
File watcher sobre diretorio de skills + registry que atualiza em tempo real,
com degradacao graciosa quando uma skill tem erro de sintaxe.

Integracao OpenCode:
  - Skills do ecossistema (~104) sao carregadas estaticamente hoje
  - Com hot-reload, novas skills criadas por AutoEvolve/ManusEvolve
    entram em operacao imediatamente, sem reiniciar o agente
  - File watcher usa polling cross-platform (Windows/Linux/Mac)
  - Registry mantem estado atomico com lock para acesso thread-safe
"""

from __future__ import annotations

import os
import sys
import json
import time
import threading
import logging
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

DEFAULT_POLL_INTERVAL = 2.0
SKILL_MANIFEST_FILE = ".skill_manifest.json"


@dataclass
class SkillEntry:
    name: str
    path: str
    kind: str
    version: str = "0.1.0"
    enabled: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)
    loaded_at: float = 0.0
    error: str | None = None

    @property
    def is_valid(self) -> bool:
        return self.error is None


class SkillRegistry:
    """
    Registro thread-safe de skills carregaveis dinamicamente.

    Armazena metadados, estado de carregamento e erros.
    Suporta callbacks de eventos (on_add, on_remove, on_error).
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._skills: dict[str, SkillEntry] = {}
        self._callbacks: dict[str, list[Callable[[SkillEntry], None]]] = {
            "on_add": [],
            "on_remove": [],
            "on_update": [],
            "on_error": [],
        }

    def register(self, entry: SkillEntry) -> None:
        with self._lock:
            is_new = entry.name not in self._skills
            self._skills[entry.name] = entry
            event = "on_add" if is_new else "on_update"
        self._fire(event, entry)

    def unregister(self, name: str) -> None:
        with self._lock:
            entry = self._skills.pop(name, None)
        if entry:
            self._fire("on_remove", entry)

    def get(self, name: str) -> SkillEntry | None:
        with self._lock:
            return self._skills.get(name)

    def list_enabled(self) -> list[SkillEntry]:
        with self._lock:
            return [s for s in self._skills.values() if s.enabled]

    def list_all(self) -> list[SkillEntry]:
        with self._lock:
            return list(self._skills.values())

    def on(self, event: str, callback: Callable[[SkillEntry], None]) -> None:
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _fire(self, event: str, entry: SkillEntry) -> None:
        for cb in self._callbacks.get(event, []):
            try:
                cb(entry)
            except Exception:
                logger.exception("Erro em callback '%s' para skill '%s'", event, entry.name)

    def to_dict(self) -> dict[str, Any]:
        with self._lock:
            return {
                name: {
                    "path": e.path,
                    "kind": e.kind,
                    "version": e.version,
                    "enabled": e.enabled,
                    "loaded_at": e.loaded_at,
                    "error": e.error,
                }
                for name, e in self._skills.items()
            }


class SkillParser:
    """
    Extrai metadados de SKILL.md seguindo o padrao OpenCode.
    """

    @staticmethod
    def parse(skill_dir: Path) -> SkillEntry | None:
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None

        name = skill_dir.name
        content = skill_md.read_text(encoding="utf-8", errors="replace")

        metadata = SkillParser._extract_frontmatter(content) if content.startswith("---") else {}

        version = str(metadata.get("version", "0.1.0"))
        kind = SkillParser._detect_kind(skill_dir)

        return SkillEntry(
            name=name,
            path=str(skill_dir),
            kind=kind,
            version=version,
            metadata=metadata,
            loaded_at=time.time(),
        )

    @staticmethod
    def _extract_frontmatter(content: str) -> dict[str, Any]:
        try:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return json.loads(parts[1]) if parts[1].strip().startswith("{") else {}
        except json.JSONDecodeError:
            pass
        return {}

    @staticmethod
    def _detect_kind(skill_dir: Path) -> str:
        scripts = skill_dir / "scripts"
        if scripts.is_dir() and any(scripts.iterdir()):
            for f in scripts.iterdir():
                if f.suffix == ".py":
                    return "python"
                if f.suffix in (".ts", ".js"):
                    return "typescript"
        return "markdown"


class SkillValidator:
    """
    Valida skills Python sem executa-las — apenas checa sintaxe e importabilidade.
    Degradacao graciosa: skill com erro de sintaxe e marcada com .error mas
    nao interrompe o sistema.
    """

    @staticmethod
    def validate(entry: SkillEntry) -> SkillEntry:
        if entry.kind != "python":
            return entry

        skill_dir = Path(entry.path)
        scripts_dir = skill_dir / "scripts"
        if not scripts_dir.is_dir():
            return entry

        errors: list[str] = []
        for py_file in scripts_dir.glob("*.py"):
            try:
                source = py_file.read_text(encoding="utf-8")
                compile(source, str(py_file), "exec")
            except SyntaxError as exc:
                msg = f"{py_file.name}:{exc.lineno}: {exc.msg}"
                errors.append(msg)
                logger.warning("Skill '%s' — erro de sintaxe em %s", entry.name, msg)
            except Exception as exc:
                errors.append(f"{py_file.name}: {exc}")

        if errors:
            entry.error = "; ".join(errors)
            logger.error(
                "Skill '%s' carregada com %d erro(s) — desabilitada",
                entry.name,
                len(errors),
            )
            entry.enabled = False
        else:
            entry.error = None
            entry.enabled = True

        return entry


class SkillWatcher:
    """
    Observador de diretorio que detecta criacao/remocao/alteracao de skills.

    Usa polling (compativel com Windows e Linux sem dependencias extras).
    A cada ciclo, compara o estado do disco com o registry e emite eventos.
    """

    def __init__(
        self,
        skills_root: str,
        registry: SkillRegistry,
        interval: float = DEFAULT_POLL_INTERVAL,
    ) -> None:
        self._root = Path(skills_root)
        self._registry = registry
        self._interval = interval
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._known: dict[str, float] = {}

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="skill-watcher")
        self._thread.start()
        logger.info("SkillWatcher iniciado em %s (intervalo=%.1fs)", self._root, self._interval)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("SkillWatcher parado")

    def scan_once(self) -> dict[str, str]:
        """
        Varredura unica do diretorio de skills.
        Retorna {nome: acao} para cada skill detectada.
        """
        if not self._root.is_dir():
            logger.warning("Diretorio de skills nao encontrado: %s", self._root)
            return {}

        current: dict[str, float] = {}
        for entry in self._root.iterdir():
            if not entry.is_dir():
                continue
            skill_md = entry / "SKILL.md"
            if not skill_md.exists():
                continue
            current[entry.name] = skill_md.stat().st_mtime

        result: dict[str, str] = {}

        for name, mtime in current.items():
            if name not in self._known:
                result[name] = "added"
            elif mtime > self._known[name]:
                result[name] = "modified"

        for name in self._known:
            if name not in current:
                result[name] = "removed"

        self._known = current
        return result

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                changes = self.scan_once()
                for name, action in changes.items():
                    skill_dir = self._root / name
                    if action == "added":
                        self._load_skill(skill_dir)
                    elif action == "modified":
                        self._reload_skill(skill_dir)
                    elif action == "removed":
                        self._registry.unregister(name)
                        logger.info("Skill removida: %s", name)
            except Exception:
                logger.exception("Erro no ciclo de watcher")
            self._stop_event.wait(self._interval)

    def _load_skill(self, skill_dir: Path) -> None:
        entry = SkillParser.parse(skill_dir)
        if entry is None:
            logger.warning("Skill sem SKILL.md: %s", skill_dir)
            return
        entry = SkillValidator.validate(entry)
        self._registry.register(entry)
        status = "OK" if entry.is_valid else f"ERRO: {entry.error}"
        logger.info("Skill carregada: %s [%s]", entry.name, status)

    def _reload_skill(self, skill_dir: Path) -> None:
        entry = SkillParser.parse(skill_dir)
        if entry is None:
            return
        entry = SkillValidator.validate(entry)
        self._registry.register(entry)
        status = "OK" if entry.is_valid else f"ERRO: {entry.error}"
        logger.info("Skill recarregada: %s [%s]", entry.name, status)


def create_watcher_for_ecosystem(
    skills_root: str | None = None,
) -> tuple[SkillWatcher, SkillRegistry]:
    """
    Factory para o ecossistema OpenCode.
    Detecta automaticamente o diretorio de skills a partir de SKILLS_PATH.
    """
    if skills_root is None:
        skills_root = os.environ.get(
            "SKILLS_PATH",
            str(Path.home() / ".config" / "opencode" / "skills"),
        )
    registry = SkillRegistry()
    watcher = SkillWatcher(skills_root, registry)

    watcher.scan_once()
    for name in watcher._known:
        skill_dir = Path(skills_root) / name
        watcher._load_skill(skill_dir)

    watcher.start()
    return watcher, registry
