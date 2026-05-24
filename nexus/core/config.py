# -*- coding: utf-8 -*-
"""core.config - Configuracao central do ecossistema OpenCode."""

import sys
from pathlib import Path
from pydantic import BaseModel, Field


class ScoringSettings(BaseModel):
    success_weight: float = 60.0
    base_bonus: float = 25.0
    error_penalty_factor: float = 30.0
    recent_bonus: float = 5.0
    default_score: float = 85.0


class HealthThresholds(BaseModel):
    healthy: int = 95
    attention: int = 85
    alert: int = 70
    critical: int = 0


class OutcomeLimits(BaseModel):
    max_outcomes_stored: int = 500
    max_learnings_stored: int = 200
    recent_outcomes_window: int = 100
    recent_outcomes_for_diagnosis: int = 50
    min_outcomes_for_trend: int = 20
    min_outcomes_for_pattern: int = 5
    min_errors_for_pattern: int = 3


class ConfidenceSettings(BaseModel):
    min_learning: float = 0.6
    reliable: float = 0.8
    unreliable: float = 0.4


class DefaultSettings(BaseModel):
    diagnosis: float = 85.0
    health_check_fallback: float = 70.0


class Settings(BaseModel):
    ECO_ROOT: Path = Field(default_factory=lambda: Path(__file__).parent.parent.parent.resolve())
    CACHE_DIR: Path = Field(default="")
    EVOLVE_DIR: Path = Field(default="")
    STATE_DIR: Path = Field(default="")
    scoring: ScoringSettings = Field(default_factory=ScoringSettings)
    health_thresholds: HealthThresholds = Field(default_factory=HealthThresholds)
    outcome_limits: OutcomeLimits = Field(default_factory=OutcomeLimits)
    confidence: ConfidenceSettings = Field(default_factory=ConfidenceSettings)
    defaults: DefaultSettings = Field(default_factory=DefaultSettings)

    def model_post_init(self, __context):
        if not self.CACHE_DIR:
            self.CACHE_DIR = self.ECO_ROOT / ".cache"
        if not self.EVOLVE_DIR:
            self.EVOLVE_DIR = self.ECO_ROOT / "evolution"
        if not self.STATE_DIR:
            self.STATE_DIR = self.ECO_ROOT / "nexus" / ".state"

    def state_path(self, name: str) -> Path:
        return self.STATE_DIR / f"{name}.json"

    def ensure_dirs(self):
        for d in [self.CACHE_DIR, self.EVOLVE_DIR, self.STATE_DIR]:
            d.mkdir(parents=True, exist_ok=True)


settings = Settings()


def initialize_core():
    """Inicializa o modulo core (cria diretorios, garante paths)."""
    settings.ensure_dirs()
    from core.container import Container
    from core.state import StateManager
    from core.events import EventBus

    Container.instance().register('state_manager', StateManager(settings.STATE_DIR))
    Container.instance().register('event_bus', EventBus())
    return settings
