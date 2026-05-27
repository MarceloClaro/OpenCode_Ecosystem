#!/usr/bin/env python3
# =====================================================================
# R205-R208 — GEOMETRIC REASONING PATTERNS (New Reasoning Types)
# Learned from DCA Módulo 1 (Macedo 2026): S² as canonical symplectic manifold
# Category: XXVI — Geometric Reasoning (auto-generated from DCA learning)
# =====================================================================
import sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from framework import REASONING_REGISTRY

# =====================================================================
# R205: LOCAL EXACTNESS (R-EXATA-LOCAL)
# =====================================================================
R205_DEFINITION = {
    "id": "R205",
    "name": "Local-Exactness Probe",
    "category": "XXVI",
    "domain": "geometry",
    "description": (
        "When a closed differential form (dΩ=0) is encountered, systematically search "
        "for a local potential α such that Ω = dα. This reasoning type uses the Poincaré "
        "lemma (every closed form is locally exact) and the Darboux theorem (every "
        "symplectic manifold is locally isomorphic to R^{2n} with canonical form). "
        "Rich in educational context because the S² sphere (simplest 2D example) already "
        "exhibits the full richness: Ω = J sin θ dθ∧dφ = d[J(1−cos θ)dφ] locally, but "
        "∫Ω = 4πJ ≠ 0 proves non-exactness globally. Essential for Hamiltonian dynamics "
        "(local canonical coordinates), gauge theory (local potentials for field strengths), "
        "and de Rham cohomology."
    ),
    "activation_rules": {
        "when": "Problem involves exterior derivative d or closed forms (dω=0)",
        "triggers": ["dΩ", "dω", "closed form", "exact", "potential", "Darboux",
                     "symplectic", "Poincaré lemma", "local coordinates", "canonical"],
        "confidence_boost": 0.92,
    },
    "reference": "Macedo, A.M.S. (2026). Dinâmica Clássica Avançada, Módulo 1, UFC. "
                "Exercício 7: forma simplética como diferencial exata em S².",
    "generated_by": "GeometricReasoningEngine — DCA Módulo 1 Learning Pipeline",
    "frequency_across_domains": 1,
    "domains_observed": ["symplectic_geometry", "differential_geometry", "classical_mechanics"],
    "canonical_example": "S²: Ω = J sin θ dθ∧dφ = d[J(1−cos θ)dφ], ∫Ω=4πJ≠0",
}

# =====================================================================
# R206: TOPOLOGICAL SINGULARITY DETECTOR (R-SINGULARIDADE-TOPOLÓGICA)
# =====================================================================
R206_DEFINITION = {
    "id": "R206",
    "name": "Topological-Singularity Detector",
    "category": "XXVI",
    "domain": "geometry",
    "description": (
        "Singularities in local potentials α (where α is not well-defined) reveal "
        "non-trivial topology of the underlying manifold. When dα = Ω globally but "
        "α has singularities at isolated points, use Stokes' theorem (∫_M Ω = ∮_{∂M} α) "
        "to compute topological invariants. In S², α = J(1−cos θ)dφ is singular at "
        "θ = 0, π (the poles), yet Ω remains regular everywhere. This pattern connects: "
        "(1) de Rham cohomology H²_dR(S²) ≅ R, (2) the Dirac monopole (magnetic charge "
        "from singularity in vector potential), (3) the Hopf fibration S³ → S² with "
        "Chern class c₁ = 1, and (4) the Gauss-Bonnet theorem (∫K dA = 2πχ)."
    ),
    "activation_rules": {
        "when": "Potential α has coordinate singularities OR manifold has non-trivial topology",
        "triggers": ["singularity", "pole", "monopole", "Chern", "Stokes", "cohomology",
                     "Hopf", "Dirac", "magnetic charge", "Gauss-Bonnet", "χ", "Euler"],
        "confidence_boost": 0.90,
    },
    "reference": "Macedo, A.M.S. (2026). DCA Módulo 1, UFC. Exercício 7: singularidades "
                "do potencial simplético em S². + Wu-Yang (1975) Dirac monopole.",
    "generated_by": "GeometricReasoningEngine — DCA Módulo 1 Learning Pipeline",
    "frequency_across_domains": 1,
    "domains_observed": ["symplectic_geometry", "topology", "gauge_theory"],
    "canonical_example": "S²: α singular em θ=0,π → H²_dR(S²)≅R → ∫Ω=4πJ ≠ 0",
}

# =====================================================================
# R207: KÄHLER-IDENTITY REASONING (R-KAHLER-IDENTITY)
# =====================================================================
R207_DEFINITION = {
    "id": "R207",
    "name": "Kähler-Identity Reasoning",
    "category": "XXVI",
    "domain": "geometry",
    "description": (
        "In Kähler manifolds, the symplectic form Ω achieves a triple identity: it is "
        "simultaneously (1) the Kähler form (a real (1,1)-form), (2) the volume form "
        "(up to normalization), and (3) the curvature 2-form of the canonical line bundle. "
        "For CP¹ ≅ S², this means: Ω_Kähler = (i/2)∂∂̄ log(1+|z|²) in complex coords "
        "= J sin θ dθ∧dφ in real coords = curvature of the Hopf bundle connection "
        "α = J(1−cos θ)dφ. The potential K = J(1−cos θ) generates the Fubini-Study "
        "metric via g_{ij} = ∂_i ∂_j K. This reasoning type bridges complex geometry "
        "(∂∂̄-lemma), Riemannian geometry (metric from potential), and symplectic "
        "geometry (closed non-degenerate 2-form)."
    ),
    "activation_rules": {
        "when": "Problem involves complex manifolds, Kähler potentials, or Hopf bundles",
        "triggers": ["Kähler", "Fubini-Study", "CP¹", "∂∂̄", "complex structure",
                     "Hopf bundle", "coherent state", "spin", "Berry curvature",
                     "geometric quantization", "prequantum"],
        "confidence_boost": 0.88,
    },
    "reference": "Macedo, A.M.S. (2026). DCA Módulo 1, UFC. Seção 7: geometria "
                "simplética na esfera S². + Griffiths & Harris (1978) Algebraic Geometry.",
    "generated_by": "GeometricReasoningEngine — DCA Módulo 1 Learning Pipeline",
    "frequency_across_domains": 1,
    "domains_observed": ["symplectic_geometry", "complex_geometry", "quantum_mechanics"],
    "canonical_example": "S²: K = J(1−cos θ) → g_FS → Ω = dα = curvatura Hopf",
}

# =====================================================================
# R208: CANONICAL EXAMPLE STRATEGY (STRATEGY-CANONICAL-EXAMPLE)
# =====================================================================
R208_DEFINITION = {
    "id": "R208",
    "name": "Canonical-Example Strategy",
    "category": "XXVI",
    "domain": "all",
    "description": (
        "Meta-reasoning strategy: when encountering a new geometric concept, first "
        "test and fully understand it on the simplest non-trivial example before "
        "generalizing. The S² sphere (dimension 2) is the canonical example for "
        "symplectic geometry because it already exhibits ALL the richness of the "
        "theory — Darboux local exactness, Kähler structure, non-trivial cohomology "
        "(H² ≠ 0), Hopf bundle curvature, and physical applications (spin precession, "
        "Larmor frequency, coherent states) — in the minimal possible dimension. "
        "This strategy generalizes: for Riemannian geometry use S² (constant curvature), "
        "for Lie groups use SU(2), for fiber bundles use Hopf S³→S². The pedagogical "
        "power comes from the fact that computational complexity is minimal (2D) while "
        "conceptual richness is maximal."
    ),
    "activation_rules": {
        "when": "Introducing new geometric concept OR teaching/explaining abstract math",
        "triggers": ["simplest example", "canonical", "prototype", "dimension 2",
                     "pedagogical", "didactic", "explain", "teach", "conceptual"],
        "confidence_boost": 0.85,
    },
    "reference": "Macedo, A.M.S. (2026). DCA Módulo 1, UFC. Estratégia pedagógica: "
                "usar S² como exemplo canônico que exibe toda a teoria simplética.",
    "generated_by": "GeometricReasoningEngine — DCA Módulo 1 Learning Pipeline",
    "frequency_across_domains": 1,
    "domains_observed": ["education", "symplectic_geometry", "differential_geometry"],
    "canonical_example": "S² as minimal example with maximal conceptual richness",
}

# =====================================================================
# REGISTER in the taxonomy
# =====================================================================

def register_geometric_types():
    """Register R205-R208 in the active taxonomy."""
    new_types = [R205_DEFINITION, R206_DEFINITION, R207_DEFINITION, R208_DEFINITION]
    
    print("=" * 70)
    print("REGISTERING R205-R208 in OpenCode Taxonomy")
    print("Category XXVI — Geometric Reasoning (from DCA Módulo 1)")
    print("=" * 70)
    
    for nt in new_types:
        rid = nt["id"]
        name = nt["name"]
        
        if rid in REASONING_REGISTRY:
            print(f"  {rid} ({name}): ALREADY REGISTERED")
            continue
        
        REASONING_REGISTRY[rid] = {
            "name": name,
            "category": nt["category"],
            "domain": nt["domain"],
        }
        
        print(f"  [REGISTERED] {rid} ({name})")
        print(f"    Category: {nt['category']} | Domain: {nt['domain']}")
        print(f"    Confidence: {nt['activation_rules']['confidence_boost']:.0%}")
        example = nt['canonical_example'][:70]
        # Strip non-ASCII for Windows console
        example = example.encode('ascii', errors='replace').decode('ascii')
        print(f"    Canonical example: {example}...")
        print(f"    Observed in: {nt['domains_observed']}")
    
    total = len(REASONING_REGISTRY)
    print(f"\n  Total reasoning types: {total}")
    print(f"  Categories: 25 → 26 (new: XXVI — Geometric Reasoning)")
    
    return total

if __name__ == "__main__":
    total = register_geometric_types()
    print(f"\n{'='*70}")
    print(f"R205-R208 REGISTERED. Total: {total} reasoning types (204 + 4 new).")
    print(f"{'='*70}")
