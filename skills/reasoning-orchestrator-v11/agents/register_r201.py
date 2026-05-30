#!/usr/bin/env python
# =====================================================================
# R201-R203 — FORMAL DEFINITIONS (New Reasoning Types)
# Generated from cross-domain creative leaps
# Registered in the OpenCode taxonomy
# =====================================================================
import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import REASONING_REGISTRY

# =====================================================================
# R201: CROSS-DOMAIN DEDUCTION
# =====================================================================
R201_DEFINITION = {
    "id": "R201",
    "name": "Cross-Domain Deduction",
    "category": "XXV",
    "domain": "all",
    "description": (
        "Applies deductive chain reasoning (R08) combined with modular decomposition "
        "(R10) across multiple scientific domains. The key insight is that problems in "
        "astronomy, biology, climate science, cryptography, economics, and engineering "
        "share a common logical structure: decompose into independent subproblems, "
        "then chain implications from hypothesis to conclusion. This pattern appeared "
        "in 11 out of 48 diverse problems across 9 distinct domains."
    ),
    "activation_rules": {
        "when": "Problem involves multiple sub-questions OR spans multiple domains",
        "triggers": ["calculate", "determine", "find", "estimate", "multiple steps"],
        "confidence_boost": 0.95,
    },
    "reference": "Polya, G. (1945). How to Solve It. Princeton. (Cross-domain problem solving heuristics)",
    "generated_by": "CreativeLeapGenerator v2 — cross-domain analysis of 48 problems",
    "frequency_across_domains": 11,
    "domains_observed": ["astronomy","biology","climate","cryptography","data_science",
                         "economics","engineering","materials","physics"],
}

# =====================================================================
# R202: DIMENSIONAL VERIFICATION
# =====================================================================
R202_DEFINITION = {
    "id": "R202",
    "name": "Dimensional Verification",
    "category": "XXV",
    "domain": "all",
    "description": (
        "Combines deductive reasoning (R08) with dimensional analysis (R66) to verify "
        "that derived equations are physically consistent. Beyond basic unit checking, "
        "this reasoning type uses Buckingham's Pi theorem to identify dimensionless "
        "groups and validate scaling relationships. Essential for physics, engineering, "
        "climate science, and materials science. Appeared in 9 out of 48 problems "
        "across 5 domains where physical quantities are involved."
    ),
    "activation_rules": {
        "when": "Problem involves physical quantities with units (mass, length, time, etc.)",
        "triggers": ["meter", "second", "kg", "Newton", "Joule", "Watt", "unit", "dimension"],
        "confidence_boost": 0.95,
    },
    "reference": "Buckingham, E. (1914). On Physically Similar Systems. Physical Review, 4(4), 345-376.",
    "generated_by": "CreativeLeapGenerator v2",
    "frequency_across_domains": 9,
    "domains_observed": ["astronomy","climate","engineering","materials","physics"],
}

# =====================================================================
# R203: SYMMETRY-GUIDED REASONING
# =====================================================================
R203_DEFINITION = {
    "id": "R203",
    "name": "Symmetry-Guided Reasoning",
    "category": "XXV",
    "domain": "all",
    "description": (
        "Uses symmetry principles (R65) to guide deductive chains (R08). When a "
        "problem exhibits symmetry — rotational, translational, reflection, or gauge — "
        "this reasoning type exploits it to reduce the solution space before applying "
        "logical deduction. Rooted in Noether's theorem connecting symmetries to "
        "conservation laws. Appeared in 3 out of 48 problems across 3 domains where "
        "physical symmetries constrain the solution."
    ),
    "activation_rules": {
        "when": "Problem exhibits symmetry (spatial, temporal, structural, or algebraic)",
        "triggers": ["symmetric", "conservation", "invariant under", "Noether",
                    "rotational", "translational", "reflection", "gauge",
                    "automorphism", "homodimer", "crystal", "space group",
                    "Burnside", "CPT", "identical by symmetry", "equilibrium symmetric"],
        "confidence_boost": 0.88,  # Improved from 0.74 with +12 symmetry samples
    },
    "reference": "Noether, E. (1918). Invariante Variationsprobleme. Nachr. Konig. Gesell. Wiss. Gottingen.",
    "generated_by": "CreativeLeapGenerator v2",
    "frequency_across_domains": 3,
    "domains_observed": ["astronomy","engineering","materials"],
}

# =====================================================================
# REGISTER in the taxonomy
# =====================================================================

def register_new_types():
    """Register R201-R203 in the active taxonomy."""
    new_types = [R201_DEFINITION, R202_DEFINITION, R203_DEFINITION]
    
    print("=" * 70)
    print("REGISTERING R201-R203 in OpenCode Taxonomy")
    print("=" * 70)
    
    for nt in new_types:
        rid = nt["id"]
        name = nt["name"]
        
        # Check if already registered
        if rid in REASONING_REGISTRY:
            print(f"  {rid} ({name}): ALREADY REGISTERED")
            continue
        
        # Register
        REASONING_REGISTRY[rid] = {
            "name": name,
            "category": nt["category"],
            "domain": nt["domain"],
        }
        
        print(f"  [REGISTERED] {rid} ({name})")
        print(f"    Category: {nt['category']} | Domain: {nt['domain']}")
        print(f"    Confidence: {nt['activation_rules']['confidence_boost']:.0%}")
        print(f"    Observed in: {nt['domains_observed']}")
        print(f"    Reference: {nt['reference'][:80]}...")
    
    total = len(REASONING_REGISTRY)
    print(f"\n  Taxonomy size: 200 -> {total} types (+{total-200})")
    print(f"  Categories: 24 -> 25 (new: XXV — Cross-Domain Generated)")
    
    return total

if __name__ == "__main__":
    total = register_new_types()
    print(f"\n{'='*70}")
    print(f"R201-R203 REGISTERED. Total: {total} reasoning types.")
    print(f"{'='*70}")
