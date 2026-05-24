# -*- coding: utf-8 -*-
"""
EVOLUTION LOOP v5.0 - Feedback Loop Real + Aprendizado Continuo
Conecta todos os modulos do ecossistema em ciclo fechado:
  Sync Orchestrator -> Health Check -> SocialAlgorithms (auto-healing)
  -> AutoSwarmBuilder (task decomposition) -> Context Offload (state)
  -> Learn From Outcomes -> Manus Evolve -> Skill Generation
  -> PDF Pipeline -> Knowledge Extraction -> Back to Sync

Arquitetura de feedback:
  1. DETECT: Monitora health de todos os componentes
  2. DIAGNOSE: Usa SocialAlgorithms para diagnosticar problemas
  3. HEAL: Aplica correcoes via padroes sociais (debate, council, RAS)
  4. LEARN: Registra outcomes e atualiza behavioral fingerprints
  5. EVOLVE: Gera novas skills baseadas em padroes de sucesso
  6. INTEGRATE: PDF pipeline extrai conhecimento -> alimenta ecossistema

Autor: Ecossistema OpenCode v5.0
Modelo: big-pickle
"""

import json
import os
import sys
import time
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field

# Garante que o workspace esta no path para importar core
BASE_DIR = Path(__file__).parent.parent.parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.config import settings
from core import initialize_core
from core.container import Container

def _sm():
    """Lazy resolve state_manager after initialize_core()."""
    return Container.instance().resolve('state_manager')

# â”€â”€ Paths (from settings) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BASE_DIR = settings.ECO_ROOT
EVOLVE_DIR = settings.EVOLVE_DIR
STATE_PATH = settings.state_path("ecosystem-state")
MEMORY_PATH = settings.state_path("memory")
OUTCOMES_PATH = settings.state_path("outcomes")
LEARNING_PATH = settings.state_path("learnings")

# â”€â”€ Limits (from settings) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
MAX_OUTCOMES_STORED = settings.outcome_limits.max_outcomes_stored
MAX_LEARNINGS_STORED = settings.outcome_limits.max_learnings_stored
RECENT_OUTCOMES_WINDOW = settings.outcome_limits.recent_outcomes_window
RECENT_OUTCOMES_FOR_DIAGNOSIS = settings.outcome_limits.recent_outcomes_for_diagnosis
MIN_OUTCOMES_FOR_TREND = settings.outcome_limits.min_outcomes_for_trend
MIN_OUTCOMES_FOR_PATTERN = settings.outcome_limits.min_outcomes_for_pattern
MIN_ERRORS_FOR_PATTERN = settings.outcome_limits.min_errors_for_pattern

# â”€â”€ Confidence (from settings) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CONFIDENCE_MIN_LEARNING = settings.confidence.min_learning
CONFIDENCE_RELIABLE = settings.confidence.reliable
CONFIDENCE_UNRELIABLE = settings.confidence.unreliable

# â”€â”€ Default scores (from settings) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
DEFAULT_DIAGNOSIS_SCORE = settings.defaults.diagnosis
DEFAULT_HEALTH_CHECK_FALLBACK = settings.defaults.health_check_fallback

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, str(BASE_DIR / "nexus" / "scripts"))

# ============================================================
# Data Models
# ============================================================

@dataclass
class OutcomeRecord:
    """Registro de outcome de uma execucao do ecossistema."""
    timestamp: str
    component: str
    action: str
    success: bool
    score: float
    duration_ms: float
    context_summary: str = ""
    error: str = ""
    learnings: list = field(default_factory=list)

@dataclass
class LearningRecord:
    """Registro de aprendizado extraido de outcomes."""
    timestamp: str
    pattern: str
    confidence: float
    source_outcomes: list = field(default_factory=list)
    applied_to: list = field(default_factory=list)
    effectiveness: float = 0.0
    category: str = ""  # healing, optimization, skill_generation, pdf_extraction

@dataclass
class EvolutionCycle:
    """Ciclo completo de evolucao."""
    cycle_id: str
    timestamp: str
    phase: str  # detect, diagnose, heal, learn, evolve, integrate
    health_before: float = 0.0
    health_after: float = 0.0
    actions_taken: list = field(default_factory=list)
    outcomes: list = field(default_factory=list)
    learnings_generated: int = 0
    skills_generated: int = 0
    pdfs_processed: int = 0
    duration_ms: float = 0.0

# ============================================================
# Feedback Loop Engine
# ============================================================

class FeedbackLoopEngine:
    """
    Core feedback loop that connects all ecosystem modules.
    
    Pipeline:
    1. DETECT -> Health monitoring from sync_orchestrator
    2. DIAGNOSE -> SocialAlgorithms for multi-agent diagnosis
    3. HEAL -> Auto-healing via social patterns
    4. LEARN -> Outcome tracking and pattern extraction
    5. EVOLVE -> Skill generation from learned patterns
    6. INTEGRATE -> PDF pipeline feeds knowledge back
    """

    def __init__(self):
        self.outcomes: list[OutcomeRecord] = []
        self.learnings: list[LearningRecord] = []
        self.cycles: list[EvolutionCycle] = []
        self._load_state()

    def _load_state(self):
        """Load persisted outcomes and learnings via state_manager."""
        outcomes_data = _sm().get("outcomes", default={})
        if outcomes_data:
            try:
                self.outcomes = [OutcomeRecord(**o) for o in outcomes_data.get("outcomes", [])]
            except (TypeError, KeyError):
                pass
        learnings_data = _sm().get("learnings", default={})
        if learnings_data:
            try:
                self.learnings = [LearningRecord(**l) for l in learnings_data.get("learnings", [])]
            except (TypeError, KeyError):
                pass

    def _save_state(self):
        """Persist outcomes and learnings via state_manager."""
        outcomes_data = {
            "outcomes": [o.__dict__ for o in self.outcomes[-MAX_OUTCOMES_STORED:]],
            "total_records": len(self.outcomes),
            "last_updated": datetime.now().isoformat()
        }
        _sm().set("outcomes", outcomes_data)
        learnings_data = {
            "learnings": [l.__dict__ for l in self.learnings[-MAX_LEARNINGS_STORED:]],
            "total_records": len(self.learnings),
            "last_updated": datetime.now().isoformat()
        }
        _sm().set("learnings", learnings_data)

    def record_outcome(self, component: str, action: str, success: bool,
                       score: float, duration_ms: float, context: str = "",
                       error: str = "", learnings: list = None) -> OutcomeRecord:
        """Record an outcome from any ecosystem component."""
        record = OutcomeRecord(
            timestamp=datetime.now().isoformat(),
            component=component,
            action=action,
            success=success,
            score=score,
            duration_ms=duration_ms,
            context_summary=context[:500],
            error=error[:500],
            learnings=learnings or []
        )
        self.outcomes.append(record)
        self._save_state()
        return record

    def extract_learnings(self, min_confidence: float = CONFIDENCE_MIN_LEARNING) -> list[LearningRecord]:
        """Extract learning patterns from recent outcomes."""
        new_learnings = []
        recent = self.outcomes[-RECENT_OUTCOMES_WINDOW:]
        if not recent:
            return []

        # Pattern 1: Success rate by component
        comp_stats = {}
        for o in recent:
            if o.component not in comp_stats:
                comp_stats[o.component] = {"success": 0, "total": 0, "scores": []}
            comp_stats[o.component]["total"] += 1
            if o.success:
                comp_stats[o.component]["success"] += 1
            comp_stats[o.component]["scores"].append(o.score)

        for comp, stats in comp_stats.items():
            if stats["total"] >= MIN_OUTCOMES_FOR_PATTERN:
                success_rate = stats["success"] / stats["total"]
                avg_score = sum(stats["scores"]) / len(stats["scores"])
                if success_rate >= min_confidence:
                    learning = LearningRecord(
                        timestamp=datetime.now().isoformat(),
                        pattern=f"component_reliable:{comp}",
                        confidence=success_rate,
                        source_outcomes=[o.timestamp for o in recent if o.component == comp],
                        category="optimization",
                        effectiveness=avg_score
                    )
                    new_learnings.append(learning)
                    logger.info(f"Learning: {comp} reliability = {success_rate:.2f} (avg score: {avg_score:.1f})")
                elif success_rate < CONFIDENCE_UNRELIABLE:
                    learning = LearningRecord(
                        timestamp=datetime.now().isoformat(),
                        pattern=f"component_unreliable:{comp}",
                        confidence=1.0 - success_rate,
                        source_outcomes=[o.timestamp for o in recent if o.component == comp and not o.success],
                        category="healing",
                        effectiveness=avg_score
                    )
                    new_learnings.append(learning)
                    logger.warning(f"Learning: {comp} unreliable = {success_rate:.2f}")

        # Pattern 2: Common error patterns
        errors = [o for o in recent if not o.success and o.error]
        if errors:
            error_types = {}
            for e in errors:
                etype = e.error[:50]
                error_types[etype] = error_types.get(etype, 0) + 1
            for etype, count in error_types.items():
                if count >= MIN_ERRORS_FOR_PATTERN:
                    learning = LearningRecord(
                        timestamp=datetime.now().isoformat(),
                        pattern=f"recurring_error:{etype}",
                        confidence=min(count / 5.0, 1.0),
                        source_outcomes=[e.timestamp for e in errors if e.error[:50] == etype],
                        category="healing"
                    )
                    new_learnings.append(learning)

        # Pattern 3: Duration trends (performance degradation)
        if len(recent) >= MIN_OUTCOMES_FOR_TREND:
            first_half = recent[:len(recent)//2]
            second_half = recent[len(recent)//2:]
            avg_first = sum(o.duration_ms for o in first_half) / len(first_half)
            avg_second = sum(o.duration_ms for o in second_half) / len(second_half)
            if avg_second > avg_first * 1.5:
                learning = LearningRecord(
                    timestamp=datetime.now().isoformat(),
                    pattern=f"performance_degradation:{avg_first:.0f}ms->{avg_second:.0f}ms",
                    confidence=0.7,
                    category="optimization"
                )
                new_learnings.append(learning)

        self.learnings.extend(new_learnings)
        self._save_state()
        return new_learnings

    def get_healing_recommendations(self) -> list[dict]:
        """Get healing recommendations based on learnings."""
        recommendations = []
        healing_learnings = [l for l in self.learnings if l.category == "healing"]
        for l in healing_learnings[-10:]:
            if "unreliable" in l.pattern:
                comp = l.pattern.split(":")[1]
                recommendations.append({
                    "type": "component_repair",
                    "component": comp,
                    "action": f"Run diagnostic on {comp}, check headers and dependencies",
                    "confidence": l.confidence,
                    "learning_pattern": l.pattern
                })
            elif "recurring_error" in l.pattern:
                recommendations.append({
                    "type": "error_pattern_fix",
                    "action": f"Address recurring error: {l.pattern.split(':', 1)[1]}",
                    "confidence": l.confidence,
                    "learning_pattern": l.pattern
                })
            elif "degradation" in l.pattern:
                recommendations.append({
                    "type": "performance_optimization",
                    "action": f"Investigate performance: {l.pattern.split(':', 1)[1]}",
                    "confidence": l.confidence
                })
        return recommendations

    def get_skill_generation_candidates(self) -> list[dict]:
        """Identify opportunities for new skill generation."""
        candidates = []
        optimization_learnings = [l for l in self.learnings if l.category == "optimization" and l.confidence >= CONFIDENCE_RELIABLE]
        for l in optimization_learnings[-5:]:
            if "reliable" in l.pattern:
                comp = l.pattern.split(":")[1]
                candidates.append({
                    "skill_type": "optimization",
                    "source_component": comp,
                    "rationale": f"Component {comp} shows high reliability ({l.confidence:.2f}), extract as reusable skill",
                    "confidence": l.confidence
                })
        # Look for gaps in ecosystem coverage
        state = _sm().get("ecosystem-state", default={})
        if state:
            components = state.get("components", {})
            low_score = [n for n, c in components.items() if c.get("score", 100) < 70]
            if low_score:
                candidates.append({
                    "skill_type": "improvement",
                    "target_components": low_score[:5],
                    "rationale": f"Components with low scores need improvement skills",
                    "confidence": 0.8
                })
        return candidates

    def get_cycle_summary(self) -> dict:
        """Get summary of evolution cycles."""
        if not self.cycles:
            return {"total_cycles": 0}
        recent = self.cycles[-10:]
        return {
            "total_cycles": len(self.cycles),
            "recent_avg_health_improvement": sum(c.health_after - c.health_before for c in recent) / len(recent),
            "total_learnings": len(self.learnings),
            "total_outcomes": len(self.outcomes),
            "last_cycle_phase": self.cycles[-1].phase,
            "last_cycle_health": self.cycles[-1].health_after
        }

    def get_outcomes_paginated(self, page: int = 1, page_size: int = 20) -> dict:
        """Get outcomes with pagination support."""
        total = len(self.outcomes)
        total_pages = max(1, (total + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = self.outcomes[start:end]
        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "outcomes": [o.__dict__ for o in page_items]
        }

    def get_learnings_paginated(self, page: int = 1, page_size: int = 20) -> dict:
        """Get learnings with pagination support."""
        total = len(self.learnings)
        total_pages = max(1, (total + page_size - 1) // page_size)
        start = (page - 1) * page_size
        end = start + page_size
        page_items = self.learnings[start:end]
        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "learnings": [l.__dict__ for l in page_items]
        }

    def rotate_outcomes(self, max_keep: int = None) -> int:
        """Remove oldest outcomes beyond max_keep limit. Returns count removed."""
        limit = max_keep or MAX_OUTCOMES_STORED
        if len(self.outcomes) <= limit:
            return 0
        removed = len(self.outcomes) - limit
        self.outcomes = self.outcomes[-limit:]
        self._save_state()
        return removed

    def rotate_learnings(self, max_keep: int = None) -> int:
        """Remove oldest learnings beyond max_keep limit. Returns count removed."""
        limit = max_keep or MAX_LEARNINGS_STORED
        if len(self.learnings) <= limit:
            return 0
        removed = len(self.learnings) - limit
        self.learnings = self.learnings[-limit:]
        self._save_state()
        return removed

# ============================================================
# Integration with SocialAlgorithms for Diagnosis
# ============================================================

class SocialDiagnosisEngine:
    """
    Uses SocialAlgorithms to diagnose ecosystem issues.
    Multiple agents analyze the same problem from different perspectives.
    """

    def __init__(self, feedback_loop: FeedbackLoopEngine):
        self.fb = feedback_loop
        self._setup_agents()

    def _setup_agents(self):
        """Create diagnostic agents."""
        self.agents = {
            "security_analyst": lambda task, **kw: self._security_analysis(task),
            "performance_analyst": lambda task, **kw: self._performance_analysis(task),
            "reliability_analyst": lambda task, **kw: self._reliability_analysis(task),
            "integration_analyst": lambda task, **kw: self._integration_analysis(task),
        }

    def _security_analysis(self, task: str) -> str:
        """Analyze from security perspective."""
        issues = []
        # Check for hardcoded credentials, unsafe file operations
        for comp_dir in [BASE_DIR / "nexus" / "scripts", BASE_DIR / "plugins"]:
            if comp_dir.exists():
                for f in comp_dir.glob("*.py"):
                    try:
                        c = f.read_text(encoding="utf-8").lower()
                        if "password" in c or "secret" in c or "api_key" in c:
                            issues.append(f"Potential credential in {f.name}")
                    except Exception:
                        pass
        return f"Security: {len(issues)} issues found. " + "; ".join(issues[:3]) if issues else "Security: No issues found"

    def _performance_analysis(self, task: str) -> str:
        """Analyze from performance perspective."""
        recent = self.fb.outcomes[-50:]
        if not recent:
            return "Performance: Insufficient data"
        avg_duration = sum(o.duration_ms for o in recent) / len(recent)
        slow = [o for o in recent if o.duration_ms > avg_duration * 2]
        return f"Performance: avg={avg_duration:.0f}ms, {len(slow)} slow operations detected"

    def _reliability_analysis(self, task: str) -> str:
        """Analyze from reliability perspective."""
        recent = self.fb.outcomes[-50:]
        if not recent:
            return "Reliability: Insufficient data"
        success_rate = sum(1 for o in recent if o.success) / len(recent)
        failures = [o for o in recent if not o.success]
        return f"Reliability: {success_rate:.1%} success rate, {len(failures)} failures in last 50 operations"

    def _integration_analysis(self, task: str) -> str:
        """Analyze from integration perspective."""
        issues = []
        # Check if all new modules are importable
        modules = ["social_algorithms", "auto_swarm_builder", "aop_service_discovery",
                   "context_offload", "nexus_integration"]
        for mod in modules:
            mod_path = BASE_DIR / "nexus" / "scripts" / f"{mod}.py"
            if not mod_path.exists():
                issues.append(f"Missing module: {mod}")
        return f"Integration: {len(issues)} issues. " + "; ".join(issues) if issues else "Integration: All modules present"

    def run_diagnosis(self, task: str = "Full ecosystem health check") -> dict:
        """Run multi-agent diagnosis using SocialAlgorithms pattern."""
        from social_algorithms import Agent, SocialAlgorithms, SocialAlgorithmType

        agents = [Agent(name, fn) for name, fn in self.agents.items()]

        def consensus_algorithm(agents, task, **kw):
            results = {}
            for agent in agents:
                results[agent.name] = agent.run(task)
            return results

        sa = SocialAlgorithms(
            name="ecosystem-diagnosis",
            agents=agents,
            social_algorithm=consensus_algorithm,
        )

        result = sa.run(task)

        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "success": result.success,
            "analyses": result.final_outputs,
            "communication_log": result.communication_log
        }

        # Record outcome
        self.fb.record_outcome(
            component="social_diagnosis",
            action="multi_agent_diagnosis",
            success=result.success,
            score=DEFAULT_DIAGNOSIS_SCORE,
            duration_ms=result.execution_time * 1000,
            context=f"Diagnosed {len(result.final_outputs)} perspectives"
        )

        return diagnosis

# ============================================================
# Main Evolution Loop Runner
# ============================================================

class EvolutionLoopRunner:
    """
    Runs the complete evolution cycle:
    DETECT -> DIAGNOSE -> HEAL -> LEARN -> EVOLVE -> INTEGRATE
    """

    def __init__(self):
        self.fb = FeedbackLoopEngine()
        self.diagnosis = SocialDiagnosisEngine(self.fb)

    def run_cycle(self, cycle_id: str = None) -> EvolutionCycle:
        """Execute one complete evolution cycle."""
        start = time.time()
        cid = cycle_id or f"cycle-{int(time.time())}"

        cycle = EvolutionCycle(
            cycle_id=cid,
            timestamp=datetime.now().isoformat(),
            phase="detect"
        )

        try:
            # Phase 1: DETECT - Run sync orchestrator health check
            logger.info(f"[{cid}] Phase 1: DETECT - Running health check")
            cycle.phase = "detect"
            health_before = self._run_health_check()
            cycle.health_before = health_before
            cycle.actions_taken.append(f"Health check: {health_before:.1f}")

            # Phase 2: DIAGNOSE - Multi-agent diagnosis
            logger.info(f"[{cid}] Phase 2: DIAGNOSE - Multi-agent analysis")
            cycle.phase = "diagnose"
            diagnosis = self.diagnosis.run_diagnosis()
            cycle.actions_taken.append(f"Diagnosis: {len(diagnosis.get('analyses', {}))} perspectives")

            # Phase 3: HEAL - Apply healing based on diagnosis
            logger.info(f"[{cid}] Phase 3: HEAL - Auto-repair")
            cycle.phase = "heal"
            healing_actions = self._apply_healing(diagnosis)
            cycle.actions_taken.extend(healing_actions)

            # Phase 4: LEARN - Extract learnings from outcomes
            logger.info(f"[{cid}] Phase 4: LEARN - Pattern extraction")
            cycle.phase = "learn"
            new_learnings = self.fb.extract_learnings()
            cycle.learnings_generated = len(new_learnings)
            cycle.actions_taken.append(f"Learnings extracted: {len(new_learnings)}")

            # Phase 5: EVOLVE - Generate skill candidates
            logger.info(f"[{cid}] Phase 5: EVOLVE - Skill generation")
            cycle.phase = "evolve"
            skill_candidates = self.fb.get_skill_generation_candidates()
            cycle.skills_generated = len(skill_candidates)
            cycle.actions_taken.append(f"Skill candidates: {len(skill_candidates)}")

            # Phase 6: INTEGRATE - PDF pipeline check
            logger.info(f"[{cid}] Phase 6: INTEGRATE - PDF knowledge extraction")
            cycle.phase = "integrate"
            pdfs_processed = self._run_pdf_pipeline()
            cycle.pdfs_processed = pdfs_processed
            cycle.actions_taken.append(f"PDFs processed: {pdfs_processed}")

            # Record cycle outcome
            duration = (time.time() - start) * 1000
            self.fb.record_outcome(
                component="evolution_loop",
                action=f"cycle_{cid}",
                success=True,
                score=DEFAULT_DIAGNOSIS_SCORE,
                duration_ms=duration,
                context=f"Phase: integrate, Actions: {len(cycle.actions_taken)}"
            )

        except Exception as e:
            duration = (time.time() - start) * 1000
            self.fb.record_outcome(
                component="evolution_loop",
                action=f"cycle_{cid}",
                success=False,
                score=0.0,
                duration_ms=duration,
                error=str(e)
            )
            cycle.actions_taken.append(f"ERROR: {str(e)}")

        cycle.duration_ms = (time.time() - start) * 1000
        cycle.health_after = self._run_health_check()
        self.fb.cycles.append(cycle)

        return cycle

    def _run_health_check(self) -> float:
        """Run sync orchestrator health check."""
        try:
            sys.path.insert(0, str(BASE_DIR / "nexus" / "scripts"))
            from sync_orchestrator import SyncOrchestrator
            orch = SyncOrchestrator()
            state = orch.run_full_sync()
            orch.save_state(state)
            return state.health_score
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return DEFAULT_HEALTH_CHECK_FALLBACK

    def _apply_healing(self, diagnosis: dict) -> list:
        """Apply healing actions based on diagnosis."""
        actions = []
        recommendations = self.fb.get_healing_recommendations()
        for rec in recommendations[:5]:
            if rec["type"] == "component_repair":
                comp = rec["component"]
                # Check if component file exists and has proper headers
                skill_path = BASE_DIR / "skills"
                for f in skill_path.rglob(f"*{comp}*"):
                    if f.is_file() and f.suffix == ".md":
                        content = f.read_text(encoding="utf-8")
                        if "big-pickle" not in content.lower():
                            # Fix header
                            new_content = f"<!-- SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL -->\n<!-- Modelo: big-pickle -->\n\n{content}"
                            f.write_text(new_content, encoding="utf-8")
                            actions.append(f"Fixed header for {f.name}")
            elif rec["type"] == "error_pattern_fix":
                actions.append(f"Flagged error pattern for review: {rec['action']}")
        if not recommendations:
            actions.append("No healing actions needed - system healthy")
        return actions

    def _run_pdf_pipeline(self) -> int:
        """Process PDFs using Docling Adapter for advanced extraction."""
        try:
            from docling_adapter import DoclingAdapter, DoclingSkillGenerator
            adapter = DoclingAdapter()
            generator = DoclingSkillGenerator()
            
            pdf_dirs = [
                BASE_DIR.parent / "Downloads",
                BASE_DIR / "documents",
                BASE_DIR / "papers",
            ]
            processed = 0
            for pdf_dir in pdf_dirs:
                if pdf_dir.exists():
                    for pdf_file in pdf_dir.glob("*.pdf"):
                        md_file = pdf_file.with_suffix(".md")
                        if not md_file.exists():
                            logger.info(f"Docling processing: {pdf_file.name}")
                            try:
                                extraction = adapter.extract_knowledge(str(pdf_file))
                                if extraction.get("topics") or extraction.get("key_findings"):
                                    generator.generate_from_extraction(extraction, str(pdf_file))
                                    processed += 1
                            except Exception as e:
                                logger.error(f"Docling error on {pdf_file.name}: {e}")
            return processed
        except ImportError:
            # Fallback to legacy behavior if docling not available
            logger.warning("Docling not available, using legacy PDF check")
            pdf_dirs = [
                BASE_DIR.parent / "Downloads",
                BASE_DIR / "documents",
                BASE_DIR / "papers",
            ]
            processed = 0
            for pdf_dir in pdf_dirs:
                if pdf_dir.exists():
                    for pdf_file in pdf_dir.glob("*.pdf"):
                        md_file = pdf_file.with_suffix(".md")
                        if not md_file.exists():
                            logger.info(f"PDF found: {pdf_file.name} - needs processing")
                            processed += 1
            return processed

    def get_status(self) -> dict:
        """Get full ecosystem evolution status."""
        return {
            "feedback_loop": self.fb.get_cycle_summary(),
            "learnings": len(self.fb.learnings),
            "outcomes": len(self.fb.outcomes),
            "healing_recommendations": self.fb.get_healing_recommendations(),
            "skill_candidates": self.fb.get_skill_generation_candidates(),
        }

# ============================================================
# CLI Entry Point
# ============================================================

def main():
    initialize_core()
    import argparse
    parser = argparse.ArgumentParser(description="Evolution Loop v5.0 - Feedback Loop Real")
    parser.add_argument("--run-cycle", action="store_true", help="Run one evolution cycle")
    parser.add_argument("--diagnose", action="store_true", help="Run multi-agent diagnosis only")
    parser.add_argument("--status", action="store_true", help="Show evolution status")
    parser.add_argument("--learnings", action="store_true", help="Extract and show learnings")
    parser.add_argument("--healing", action="store_true", help="Show healing recommendations")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    runner = EvolutionLoopRunner()

    if args.run_cycle:
        cycle = runner.run_cycle()
        if args.json:
            print(json.dumps(cycle.__dict__, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"\n{'='*60}")
            print(f"  EVOLUTION CYCLE: {cycle.cycle_id}")
            print(f"{'='*60}")
            print(f"  Duration: {cycle.duration_ms:.0f}ms")
            print(f"  Health: {cycle.health_before:.1f} -> {cycle.health_after:.1f}")
            print(f"  Phases completed: {cycle.phase}")
            print(f"  Actions: {len(cycle.actions_taken)}")
            for a in cycle.actions_taken:
                print(f"    - {a}")
            print(f"  Learnings: {cycle.learnings_generated}")
            print(f"  Skill candidates: {cycle.skills_generated}")
            print(f"  PDFs pending: {cycle.pdfs_processed}")
            print(f"{'='*60}")

    elif args.diagnose:
        diagnosis = runner.diagnosis.run_diagnosis()
        if args.json:
            print(json.dumps(diagnosis, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"\n{'='*60}")
            print(f"  MULTI-AGENT DIAGNOSIS")
            print(f"{'='*60}")
            for agent, result in diagnosis.get("analyses", {}).items():
                print(f"  [{agent}] {result}")
            print(f"{'='*60}")

    elif args.status:
        status = runner.get_status()
        if args.json:
            print(json.dumps(status, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"\n{'='*60}")
            print(f"  EVOLUTION STATUS")
            print(f"{'='*60}")
            summary = status["feedback_loop"]
            print(f"  Total cycles: {summary.get('total_cycles', 0)}")
            print(f"  Total learnings: {summary.get('total_learnings', 0)}")
            print(f"  Total outcomes: {summary.get('total_outcomes', 0)}")
            print(f"  Healing recommendations: {len(status['healing_recommendations'])}")
            print(f"  Skill candidates: {len(status['skill_candidates'])}")
            print(f"{'='*60}")

    elif args.learnings:
        learnings = runner.fb.extract_learnings()
        if args.json:
            print(json.dumps([l.__dict__ for l in learnings], ensure_ascii=False, indent=2, default=str))
        else:
            print(f"\n{'='*60}")
            print(f"  EXTRACTED LEARNINGS ({len(learnings)} new)")
            print(f"{'='*60}")
            for l in learnings:
                print(f"  [{l.category}] {l.pattern} (confidence: {l.confidence:.2f})")
            print(f"{'='*60}")

    elif args.healing:
        recs = runner.fb.get_healing_recommendations()
        if args.json:
            print(json.dumps(recs, ensure_ascii=False, indent=2, default=str))
        else:
            print(f"\n{'='*60}")
            print(f"  HEALING RECOMMENDATIONS ({len(recs)})")
            print(f"{'='*60}")
            for r in recs:
                print(f"  [{r['type']}] {r['action']} (confidence: {r['confidence']:.2f})")
            print(f"{'='*60}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()


