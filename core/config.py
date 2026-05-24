"""
core/config.py v1.0 — Pydantic Settings Centralizados.

Substitui ecosystem_config.py com validação de schema, tipos explícitos
e carregamento por ambiente (env vars, .env file, defaults).

Uso:
    from core.config import settings

    # Acessar qualquer config
    settings.ECO_ROOT
    settings.HEALTH_THRESHOLDS.healthy
    settings.state_path("health")
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ── Health Thresholds ──────────────────────────────────────────────
class HealthThresholds(BaseModel):
    healthy: int = 95
    attention: int = 85
    alert: int = 70
    critical: int = 0


# ── Affinity Thresholds ────────────────────────────────────────────
class AffinityThresholds(BaseModel):
    min_report: float = 0.0
    low: float = 0.7
    medium: float = 0.8
    high: float = 0.85
    very_high: float = 0.9
    perfect: float = 0.95


# ── Scoring Config ─────────────────────────────────────────────────
class ScoringConfig(BaseModel):
    success_weight: float = 80.0
    base_bonus: float = 15.0
    error_penalty_factor: float = 30.0
    recent_bonus: float = 5.0
    default_score: float = 85.0


# ── Outcome Limits ─────────────────────────────────────────────────
class OutcomeLimits(BaseModel):
    max_outcomes_stored: int = 1000
    max_learnings_stored: int = 500
    recent_outcomes_window: int = 100
    recent_outcomes_for_diagnosis: int = 50
    min_outcomes_for_trend: int = 10
    min_outcomes_for_pattern: int = 3
    min_errors_for_pattern: int = 2


# ── Confidence Thresholds ──────────────────────────────────────────
class ConfidenceConfig(BaseModel):
    min_learning: float = 0.6
    reliable: float = 0.7
    unreliable: float = 0.5


# ── Default Scores ─────────────────────────────────────────────────
class DefaultScores(BaseModel):
    health_check: float = 85.0
    diagnosis: float = 85.0
    health_check_fallback: float = 50.0


# ── Performance Thresholds ─────────────────────────────────────────
class PerformanceConfig(BaseModel):
    degradation_factor: float = 1.5
    slow_threshold: float = 2.0


# ── PDF Watch Dirs ─────────────────────────────────────────────────
class PDFConfig(BaseModel):
    watch_dirs: list[str] = []


# ── Settings Principal ─────────────────────────────────────────────
class OpenCodeSettings(BaseSettings):
    """Configuração central do ecossistema OpenCode.

    Carrega de:
    1. Variáveis de ambiente (ECO_ROOT, etc.)
    2. Arquivo .env em ECO_ROOT
    3. Defaults hardcoded
    """

    model_config = SettingsConfigDict(
        env_prefix="ECO_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )

    # ── Root Path ──────────────────────────────────────────────────
    root: str = Field(
        default="",
        description="Raiz do workspace (ECO_ROOT). Auto-descoberta se vazia.",
    )

    # ── Subconfigs ─────────────────────────────────────────────────
    health_thresholds: HealthThresholds = HealthThresholds()
    affinity: AffinityThresholds = AffinityThresholds()
    scoring: ScoringConfig = ScoringConfig()
    outcome_limits: OutcomeLimits = OutcomeLimits()
    confidence: ConfidenceConfig = ConfidenceConfig()
    defaults: DefaultScores = DefaultScores()
    performance: PerformanceConfig = PerformanceConfig()

    # ── Watched PDF dirs ───────────────────────────────────────────
    pdf_watch_dirs: list[str] = Field(default_factory=list)

    # ── Validação: descobre root se não informado ──────────────────
    @field_validator("root", mode="before")
    @classmethod
    def resolve_root(cls, v: str) -> str:
        if v:
            return v
        # Auto-descoberta: sobe do diretório deste arquivo
        p = Path(__file__).resolve()
        for _ in range(6):
            p = p.parent
            if (p / "nexus").exists() and (p / "skills").exists():
                return str(p)
        # Fallback hardcoded
        return r"C:\Users\marce\.config\opencode"

    # ── Propriedades derivadas (path helpers) ──────────────────────
    @property
    def ECO_ROOT(self) -> Path:
        return Path(self.root)

    @property
    def EVOLVE_DIR(self) -> Path:
        return self.ECO_ROOT / ".evolve"

    @property
    def SKILLS_DIR(self) -> Path:
        return self.ECO_ROOT / "skills"

    @property
    def NEXUS_DIR(self) -> Path:
        return self.ECO_ROOT / "nexus"

    @property
    def NEXUS_SCRIPTS(self) -> Path:
        return self.NEXUS_DIR / "scripts"

    @property
    def PLUGINS_DIR(self) -> Path:
        return self.ECO_ROOT / "plugins"

    @property
    def STATE_DIR(self) -> Path:
        """Diretório de estados persistentes (JSON files)."""
        return self.EVOLVE_DIR / "state"

    @property
    def CORE_DIR(self) -> Path:
        return self.ECO_ROOT / "core"

    @property
    def CACHE_DIR(self) -> Path:
        return self.ECO_ROOT / "cache"

    def state_path(self, name: str) -> Path:
        """Retorna Path para arquivo de estado .json em .evolve/."""
        self.EVOLVE_DIR.mkdir(parents=True, exist_ok=True)
        return self.EVOLVE_DIR / f"{name}.json"

    def state_db_path(self) -> Path:
        """Retorna Path para o banco SQLite de estado em .evolve/."""
        self.EVOLVE_DIR.mkdir(parents=True, exist_ok=True)
        return self.EVOLVE_DIR / "state.db"

    def ensure_dirs(self) -> None:
        """Garante que diretórios essenciais existam."""
        for d in [self.EVOLVE_DIR, self.SKILLS_DIR, self.NEXUS_DIR,
                  self.NEXUS_SCRIPTS, self.CORE_DIR, self.CACHE_DIR, self.STATE_DIR]:
            d.mkdir(parents=True, exist_ok=True)


# ── Singleton de configuração ──────────────────────────────────────
settings = OpenCodeSettings()
settings.ensure_dirs()
