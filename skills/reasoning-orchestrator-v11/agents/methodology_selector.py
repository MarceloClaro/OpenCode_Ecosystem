#!/usr/bin/env python
# =====================================================================
# AUTOMATIC METHODOLOGY SELECTOR — Weighted Activation
# SDD <-> TDD <-> REVERSA — Orchestrated by context, not by command
# =====================================================================
import sys, os, json, math, time, re, hashlib
from typing import Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

class Methodology(Enum):
    SDD = "spec_driven_development"
    TDD = "test_driven_development"
    REVERSA = "reverse_engineering"
    SYNTHESIS = "synthesis"

@dataclass
class ContextProfile:
    """What the system knows about the current context."""
    has_existing_code: bool = False
    has_tests: bool = False
    has_specs: bool = False
    is_legacy: bool = False
    is_greenfield: bool = False
    has_errors: bool = False
    complexity: int = 5  # 1-10
    code_size_lines: int = 0
    last_modified_days: int = 0
    
    @property
    def confidence(self) -> float:
        """How confident is the system about this profile?"""
        signals = sum([self.has_existing_code, self.has_tests, self.has_specs,
                      self.is_legacy, self.is_greenfield, self.has_errors])
        return min(0.95, 0.3 + signals * 0.10)

@dataclass 
class MethodologyWeights:
    """Computed weights for each methodology based on context."""
    sdd: float = 0.0
    tdd: float = 0.0
    reversa: float = 0.0
    synthesis: float = 0.0
    
    @property
    def dominant(self) -> Methodology:
        """Which methodology has the highest weight?"""
        weights = {
            Methodology.SDD: self.sdd,
            Methodology.TDD: self.tdd,
            Methodology.REVERSA: self.reversa,
            Methodology.SYNTHESIS: self.synthesis,
        }
        return max(weights, key=weights.get)
    
    @property
    def ordered(self) -> list[tuple[Methodology, float]]:
        """Methodologies ordered by weight."""
        weights = [
            (Methodology.SDD, self.sdd),
            (Methodology.TDD, self.tdd),
            (Methodology.REVERSA, self.reversa),
            (Methodology.SYNTHESIS, self.synthesis),
        ]
        return sorted(weights, key=lambda x: -x[1])
    
    @property
    def should_chain(self) -> bool:
        """Should we chain multiple methodologies?"""
        active = sum(1 for w in [self.sdd, self.tdd, self.reversa] if w > 0.30)
        return active >= 2


class MethodologySelector:
    """
    Automatically selects which methodology (SDD, TDD, Reversa) to activate
    based on context weights — no human intervention needed.
    
    Decision rules:
    
    REVERSA dominates when:
    - Existing code exists AND (no specs OR no tests OR is_legacy)
    - Weight: +0.30 for existing code, +0.25 for legacy, +0.20 for no_specs
    
    SDD dominates when:
    - Greenfield project OR no specs exist
    - Weight: +0.40 for greenfield, +0.25 for no_specs, +0.15 low_complexity
    
    TDD dominates when:
    - Has specs AND has existing code AND no tests
    - Weight: +0.30 for has_specs, +0.25 for no_tests, +0.20 for has_errors
    
    SYNTHESIS activates when:
    - Multiple methodologies have weight > 0.30 (chains them)
    - Weight: proportional to number of active methodologies
    """
    
    def __init__(self):
        self.history = []
    
    def analyze_context(self, profile: ContextProfile) -> tuple[MethodologyWeights, str]:
        """Analyze context and compute methodology weights."""
        weights = MethodologyWeights()
        
        # ================================================================
        # REVERSA — Reverse Engineering
        # ================================================================
        if profile.has_existing_code:
            weights.reversa += 0.30
        if profile.is_legacy:
            weights.reversa += 0.25
        if not profile.has_specs and profile.has_existing_code:
            weights.reversa += 0.20
        if profile.code_size_lines > 1000:
            weights.reversa += 0.10
        if profile.last_modified_days > 180:
            weights.reversa += 0.10
        
        # ================================================================
        # SDD — Spec-Driven Development
        # ================================================================
        if profile.is_greenfield:
            weights.sdd += 0.40
        if not profile.has_specs:
            weights.sdd += 0.25
        if profile.complexity <= 4:
            weights.sdd += 0.15
        if not profile.has_existing_code:
            weights.sdd += 0.15
        
        # ================================================================
        # TDD — Test-Driven Development
        # ================================================================
        if profile.has_specs and profile.has_existing_code:
            weights.tdd += 0.30
        if not profile.has_tests:
            weights.tdd += 0.25
        if profile.has_errors:
            weights.tdd += 0.20
        if profile.complexity >= 6:
            weights.tdd += 0.10
        
        # ================================================================
        # SYNTHESIS — Unification
        # ================================================================
        active_count = sum(1 for w in [weights.sdd, weights.tdd, weights.reversa] if w > 0.30)
        weights.synthesis = min(0.90, active_count * 0.25)
        
        # Normalize to 0-1 range
        total = weights.sdd + weights.tdd + weights.reversa + weights.synthesis
        if total > 0:
            weights.sdd = min(1.0, weights.sdd / total)
            weights.tdd = min(1.0, weights.tdd / total)
            weights.reversa = min(1.0, weights.reversa / total)
            weights.synthesis = min(1.0, weights.synthesis / total)
        
        # Generate explanation
        explanation = self._explain(weights)
        
        # Record
        self.history.append({
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "profile": profile.__dict__,
            "weights": weights.__dict__,
            "dominant": weights.dominant.value,
            "chain": weights.should_chain,
        })
        
        return weights, explanation
    
    def _explain(self, weights: MethodologyWeights) -> str:
        """Generate human-readable explanation of the decision."""
        parts = []
        
        dominant = weights.dominant
        if dominant == Methodology.REVERSA:
            parts.append("REVERSA selecionado: codigo existente sem especificacoes/documentacao. "
                        "Engenharia reversa necessaria antes de qualquer desenvolvimento.")
        elif dominant == Methodology.SDD:
            parts.append("SDD selecionado: projeto greenfield ou sem especificacoes. "
                        "Definir especificacoes antes de implementar.")
        elif dominant == Methodology.TDD:
            parts.append("TDD selecionado: especificacoes existentes, codigo presente, sem testes. "
                        "Ciclo Red-Green-Refactor ativado.")
        
        if weights.should_chain:
            ordered = weights.ordered
            chain = " -> ".join([m.value.split("_")[0].upper() for m, w in ordered[:3] if w > 0.25])
            parts.append(f"Chain automatico: {chain}")
        
        return " | ".join(parts)
    
    def get_recommended_pipeline(self, weights: MethodologyWeights) -> list[str]:
        """Return the recommended pipeline of agent activations."""
        pipeline = []
        
        if weights.reversa > 0.30:
            pipeline.extend(["reversa-scout", "reversa-archaeologist"])
            if weights.reversa > 0.50:
                pipeline.extend(["reversa-architect", "reversa-writer"])
        
        if weights.sdd > 0.30:
            pipeline.extend(["spec-driven-development", "spec-miner"])
            if weights.sdd > 0.50:
                pipeline.append("plan-generator")
        
        if weights.tdd > 0.30:
            pipeline.extend(["test-driven-development", "test-master"])
        
        if weights.synthesis > 0.40:
            pipeline.append("synthesis-agent")
        
        return pipeline


# =====================================================================
# AUTOMATIC ORCHESTRATOR — Integrates methodology selection with reasoning
# =====================================================================

class AutoMethodologyOrchestrator:
    """
    Automatically selects and activates methodologies based on context.
    No human intervention — the system decides based on weights.
    """
    
    def __init__(self):
        self.selector = MethodologySelector()
    
    def solve(self, problem_context: dict) -> dict:
        """
        Automatically determine methodology and activate agents.
        
        Args:
            problem_context: dict with keys:
                - description: str
                - has_existing_code: bool
                - has_tests: bool
                - has_specs: bool
                - is_legacy: bool
                - is_greenfield: bool
                - has_errors: bool
                - complexity: int (1-10)
                - code_size_lines: int
                - last_modified_days: int
        """
        # Build context profile
        profile = ContextProfile(
            has_existing_code=problem_context.get("has_existing_code", False),
            has_tests=problem_context.get("has_tests", False),
            has_specs=problem_context.get("has_specs", False),
            is_legacy=problem_context.get("is_legacy", False),
            is_greenfield=problem_context.get("is_greenfield", False),
            has_errors=problem_context.get("has_errors", False),
            complexity=problem_context.get("complexity", 5),
            code_size_lines=problem_context.get("code_size_lines", 0),
            last_modified_days=problem_context.get("last_modified_days", 0),
        )
        
        # Compute weights
        weights, explanation = self.selector.analyze_context(profile)
        
        # Get recommended pipeline
        pipeline = self.selector.get_recommended_pipeline(weights)
        
        # Build result
        return {
            "context_profile": {
                "confidence": profile.confidence,
                "signals": {
                    "existing_code": profile.has_existing_code,
                    "tests": profile.has_tests,
                    "specs": profile.has_specs,
                    "legacy": profile.is_legacy,
                    "greenfield": profile.is_greenfield,
                }
            },
            "methodology_weights": {
                "sdd": round(weights.sdd, 2),
                "tdd": round(weights.tdd, 2),
                "reversa": round(weights.reversa, 2),
                "synthesis": round(weights.synthesis, 2),
            },
            "dominant_methodology": weights.dominant.value,
            "should_chain": weights.should_chain,
            "chain_order": [m.value for m, w in weights.ordered if w > 0.25],
            "explanation": explanation,
            "activated_agents": pipeline,
        }


# =====================================================================
# DEMO — Test multiple scenarios
# =====================================================================

def demo():
    """Demonstrate automatic methodology selection across scenarios."""
    print("=" * 70)
    print("AUTOMATIC METHODOLOGY SELECTOR — Weighted Activation")
    print("SDD <-> TDD <-> REVERSA — Zero human intervention")
    print("=" * 70)
    
    orch = AutoMethodologyOrchestrator()
    
    scenarios = {
        "Greenfield Project": {
            "is_greenfield": True,
            "complexity": 6,
        },
        "Legacy System (no docs, no tests)": {
            "has_existing_code": True,
            "is_legacy": True,
            "code_size_lines": 5000,
            "last_modified_days": 365,
            "complexity": 8,
        },
        "Active Development (has specs, needs tests)": {
            "has_existing_code": True,
            "has_specs": True,
            "has_errors": True,
            "complexity": 7,
        },
        "Bug Fix (existing code, tests, specs)": {
            "has_existing_code": True,
            "has_tests": True,
            "has_specs": True,
            "has_errors": True,
            "complexity": 4,
        },
        "Code Review (all present)": {
            "has_existing_code": True,
            "has_tests": True,
            "has_specs": True,
            "complexity": 5,
        },
    }
    
    for scenario_name, context in scenarios.items():
        result = orch.solve(context)
        
        print(f"\n{'-'*70}")
        print(f"SCENARIO: {scenario_name}")
        print(f"{'-'*70}")
        print(f"  Context: {result['context_profile']['signals']}")
        print(f"  Confidence: {result['context_profile']['confidence']:.0%}")
        print(f"  Weights: SDD={result['methodology_weights']['sdd']:.2f} | "
              f"TDD={result['methodology_weights']['tdd']:.2f} | "
              f"REVERSA={result['methodology_weights']['reversa']:.2f} | "
              f"SYNTH={result['methodology_weights']['synthesis']:.2f}")
        print(f"  Dominant: {result['dominant_methodology'].upper()}")
        print(f"  Chain: {result['should_chain']} ({' -> '.join(result['chain_order'])})")
        print(f"  Explanation: {result['explanation'][:120]}...")
        print(f"  Agents: {result['activated_agents']}")
    
    print(f"\n{'='*70}")
    print("SUMMARY: Methodology Selection Rules")
    print(f"{'='*70}")
    print("""
  REVERSA activates when:  existing_code + (no_specs OR legacy OR old_code)
  SDD activates when:       greenfield OR no_specs OR low_complexity
  TDD activates when:       has_specs + existing_code + (no_tests OR errors)
  SYNTHESIS chains when:    2+ methodologies have weight > 0.30
  
  The system automatically selects the dominant methodology
  and chains them when multiple are needed.
  ZERO human intervention required.
""")

if __name__ == "__main__":
    demo()

