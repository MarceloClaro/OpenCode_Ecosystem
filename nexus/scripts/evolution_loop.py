# -*- coding: utf-8 -*-
"""
evolution_loop.py — Re-export do canonical nexus/evolution_loop.py (DI v5.0).

Este arquivo é mantido para compatibilidade retroativa com imports de scripts
em nexus/scripts/ que fazem:
    from evolution_loop import EvolutionLoopRunner, ...

O código fonte real consolidado está em nexus/evolution_loop.py.
Consolidado em R40 para eliminar redundância (3 versões → 1).
"""

import sys
from pathlib import Path

# Garante que o workspace esta no path para importar nexus.evolution_loop
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from nexus.evolution_loop import (  # noqa: E402, F401
    OutcomeRecord,
    LearningRecord,
    EvolutionCycle,
    FeedbackLoopEngine,
    SocialDiagnosisEngine,
    EvolutionLoopRunner,
    main,
)
