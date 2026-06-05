# -*- coding: utf-8 -*-
"""
ECOSYSTEM CONFIG v5.0 - Centralized configuration
All paths derived from ECO_ROOT env var or parent directory discovery.
"""
import os
from pathlib import Path

# Root discovery: env var -> cwd parent -> hardcoded fallback
def _find_root():
    env = os.environ.get("ECO_ROOT")
    if env:
        return Path(env)
    # Try parent directories from current script location
    p = Path(__file__).resolve()
    for _ in range(6):
        p = p.parent
        if (p / "nexus").exists() and (p / "skills").exists():
            return p
    return Path(r"C:\Users\marce\.config\opencode")

ECO_ROOT = _find_root()
EVOLVE_DIR = ECO_ROOT / ".evolve"
SKILLS_DIR = ECO_ROOT / "skills"
NEXUS_DIR = ECO_ROOT / "nexus"
NEXUS_SCRIPTS = NEXUS_DIR / "scripts"
PLUGINS_DIR = ECO_ROOT / "plugins"
DOCLING_DIR = ECO_ROOT / "docling"
PDF_WATCH_DIRS = [
    ECO_ROOT.parent / "Downloads",
    ECO_ROOT / "documents",
    ECO_ROOT / "papers",
]

# Health thresholds
HEALTH_THRESHOLDS = {"healthy": 95, "attention": 85, "alert": 70, "critical": 0}

# Dynamic scoring weights
SCORING_SUCCESS_WEIGHT = 80.0
SCORING_BASE_BONUS = 15.0
SCORING_ERROR_PENALTY_FACTOR = 30.0
SCORING_RECENT_BONUS = 5.0
SCORING_DEFAULT_SCORE = 85.0

# Cross-validation affinity thresholds
AFFINITY_MIN_REPORT = 0.0
AFFINITY_LOW = 0.7
AFFINITY_MEDIUM = 0.8
AFFINITY_HIGH = 0.85
AFFINITY_VERY_HIGH = 0.9
AFFINITY_PERFECT = 0.95

# Performance thresholds
PERFORMANCE_DEGRADATION_FACTOR = 1.5
PERFORMANCE_SLOW_THRESHOLD = 2.0

# Outcome limits
MAX_OUTCOMES_STORED = 1000
MAX_LEARNINGS_STORED = 500
RECENT_OUTCOMES_WINDOW = 100
RECENT_OUTCOMES_FOR_DIAGNOSIS = 50
MIN_OUTCOMES_FOR_TREND = 10
MIN_OUTCOMES_FOR_PATTERN = 3
MIN_ERRORS_FOR_PATTERN = 2

# Confidence thresholds
CONFIDENCE_MIN_LEARNING = 0.6
CONFIDENCE_RELIABLE = 0.7
CONFIDENCE_UNRELIABLE = 0.5

# Default scores
DEFAULT_HEALTH_CHECK_SCORE = 85.0
DEFAULT_DIAGNOSIS_SCORE = 85.0
DEFAULT_HEALTH_CHECK_FALLBACK = 50.0

# State file paths
def state_path(name):
    EVOLVE_DIR.mkdir(parents=True, exist_ok=True)
    return EVOLVE_DIR / f"{name}.json"

MEMORY_PATH = state_path("memory")
STATE_PATH = state_path("ecosystem-state")
DYNAMIC_SCORES_PATH = state_path("dynamic-scores")
HEALTH_PATH = state_path("health")
OUTCOMES_PATH = state_path("outcomes")
LEARNINGS_PATH = state_path("learnings")
DISCOVERIES_PATH = state_path("discoveries")
INSTALLED_PATH = state_path("installed")
SYNC_STATUS_PATH = state_path("sync-status")
DOCLING_INDEX_PATH = state_path("docling_index")
MANUS_STATE_PATH = state_path("manus-state")

# Ensure directories exist
for d in [EVOLVE_DIR, SKILLS_DIR, NEXUS_DIR, NEXUS_SCRIPTS]:
    d.mkdir(parents=True, exist_ok=True)


import gzip, json


def _ensure_type(val, t, name=""):
    if not isinstance(val, t):
        raise TypeError(f"{name} must be {t.__name__}, got {type(val).__name__}")


# --- Compressed state helpers ---
def load_state(path, default=None):
    """Load JSON state with automatic .gz fallback."""
    _ensure_type(path, Path, "path")
    if default is not None:
        _ensure_type(default, dict, "default")
    gz_path = path.with_suffix(".json.gz")
    src = gz_path if gz_path.exists() else path
    if not src.exists():
        return default if default is not None else {}
    if src.suffix == ".gz":
        with gzip.open(src, "rt", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(src.read_text(encoding="utf-8"))

def save_state(path, data):
    """Save JSON state as .gz for space efficiency."""
    _ensure_type(path, Path, "path")
    _ensure_type(data, dict, "data")
    path.parent.mkdir(parents=True, exist_ok=True)
    gz_path = path.with_suffix(".json.gz")
    with gzip.open(gz_path, "wt", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    if path.exists():
        path.unlink()
