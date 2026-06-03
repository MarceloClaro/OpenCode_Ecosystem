"""
proof_templates.py — 10 Domain-Specific Proof Templates
Session 11: ProofGeneratorV2 Engine

Each template includes:
- Lean pattern (structured, domain-idiomatic)
- Natural language pattern (for human-readable proof)
- Few-shot examples (real proof excerpts)
- Domain hints (for confidence estimation)
"""

PROOF_TEMPLATES = {
    "combinatorics": {
        "domain": "Combinatorics",
        "lean_pattern": """theorem {problem_id} {statement} := by
  -- Count argument or pigeonhole principle
  have h1 : {hypothesis1} := by sorry
  have h2 : {hypothesis2} := by sorry
  exact {conclusion}""",
        "natural_pattern": """We prove by counting/pigeonhole.
Observation 1: {observation1}
Observation 2: {observation2}
By combining these, we conclude {conclusion}.""",
        "few_shot_example": """-- Pigeonhole Principle
theorem pigeonhole_simple : ∃ x, ∃ y, x ≠ y ∧ f x = f y := by
  by_contra h
  push_neg at h
  -- Build contradiction via cardinality
  sorry""",
        "confidence_keywords": ["count", "pigeonhole", "permutation", "arrange"]
    },
    
    "number_theory": {
        "domain": "Number Theory",
        "lean_pattern": """theorem {problem_id} {statement} := by
  -- Use properties of divisibility, primes, or modular arithmetic
  have h1 : {property1} := by sorry
  have h2 : {property2} := by sorry
  omega""",
        "natural_pattern": """By properties of divisibility and modular arithmetic.
Key fact 1: {fact1}
Key fact 2: {fact2}
Therefore {conclusion}.""",
        "few_shot_example": """-- GCD Property
theorem gcd_divides : gcd a b ∣ a ∧ gcd a b ∣ b := by
  constructor
  · exact gcd_dvd_left a b
  · exact gcd_dvd_right a b""",
        "confidence_keywords": ["gcd", "prime", "divisor", "modular", "congruence"]
    },
    
    "analysis": {
        "domain": "Analysis / Calculus",
        "lean_pattern": """theorem {problem_id} {statement} := by
  -- Limit, continuity, or convergence argument
  rw [Metric.tendsto_atTop]
  intro ε hε
  use N
  intro n hn
  rw [Real.dist_eq]
  sorry""",
        "natural_pattern": """By ε-δ argument or convergence test.
For any ε > 0, we can find N such that for all n ≥ N:
{bound}
This shows {conclusion}.""",
        "few_shot_example": """-- Geometric Series
theorem geom_series_sum : ∑ i in range n, x ^ i = (1 - x ^ n) / (1 - x) := by
  induction n with
  | zero => simp
  | succ n ih => sorry""",
        "confidence_keywords": ["limit", "convergence", "continuous", "epsilon", "delta"]
    },
    
    "graph_theory": {
        "domain": "Graph Theory",
        "lean_pattern": """theorem {problem_id} {statement} := by
  -- Path, cycle, or connectivity argument
  have h_connected : {connectivity} := by sorry
  have h_path : ∃ p, IsPath p u v := by sorry
  exact {conclusion}""",
        "natural_pattern": """By graph connectivity and path properties.
The graph has property {property}.
Consider the path {path_description}.
This implies {conclusion}.""",
        "few_shot_example": """-- Handshaking Lemma
theorem handshake : 2 * edgeCount = ∑ v, degree v := by
  -- Each edge contributes to exactly 2 vertices
  sorry""",
        "confidence_keywords": ["path", "cycle", "vertex", "edge", "connected", "degree"]
    },
    
    "geometry": {
        "domain": "Geometry / Topology",
        "lean_pattern": """theorem {problem_id} {statement} := by
  -- Use angle, distance, or topological properties
  have h1 : {geometric_prop1} := by sorry
  have h2 : {geometric_prop2} := by sorry
  rw [angle_sum]
  exact {conclusion}""",
        "natural_pattern": """By geometric construction or topological argument.
Property 1: {prop1}
Property 2: {prop2}
By combining, we obtain {conclusion}.""",
        "few_shot_example": """-- Angle Sum in Triangle
theorem triangle_angle_sum : angle A + angle B + angle C = 180 := by
  -- Use parallel postulate and alternate interior angles
  sorry""",
        "confidence_keywords": ["angle", "distance", "parallel", "perpendicular", "congruent"]
    },
    
    "induction": {
        "domain": "Mathematical Induction",
        "lean_pattern": """theorem {problem_id} {statement} := by
  induction n with
  | zero => {base_case}
  | succ n ih => {inductive_step}""",
        "natural_pattern": """We prove by induction on {variable}.
Base case ({base_value}): {base_proof}
Inductive step: Assume {hypothesis}. Then {step_proof}
By induction, {conclusion}.""",
        "few_shot_example": """theorem sum_naturals : (∑ i in range n, i) = n * (n - 1) / 2 := by
  induction n with
  | zero => norm_num
  | succ n ih => ring_nf; exact ih""",
        "confidence_keywords": ["induction", "base case", "inductive step", "inductive hypothesis"]
    },
    
    "finite_case": {
        "domain": "Finite Case Analysis",
        "lean_pattern": """theorem {problem_id} {statement} := by
  interval_cases {variable}
  · {case1}
  · {case2}
  · {case3}""",
        "natural_pattern": """By exhaustive case analysis.
Case 1 ({case_desc1}): {case_proof1}
Case 2 ({case_desc2}): {case_proof2}
In all cases, {conclusion}.""",
        "few_shot_example": """theorem bool_prop : ∀ b : Bool, b = false ∨ b = true := by
  intro b
  cases b
  · right; rfl
  · left; rfl""",
        "confidence_keywords": ["cases", "fin", "interval_cases", "by_cases"]
    },
    
    "algebra": {
        "domain": "Abstract Algebra",
        "lean_pattern": """theorem {problem_id} {statement} := by
  -- Ring, group, or module properties
  rw [← map_mul, ← map_add]
  have h : {algebraic_prop} := by sorry
  exact {conclusion}""",
        "natural_pattern": """By algebraic properties of {structure}.
Key property: {property}
Therefore {conclusion}.""",
        "few_shot_example": """theorem group_identity_unique : ∃! e, ∀ g, g * e = g := by
  use 1
  constructor
  · intro g; simp
  · intros e he; sorry""",
        "confidence_keywords": ["group", "ring", "field", "module", "homomorphism"]
    },
    
    "logic": {
        "domain": "Mathematical Logic",
        "lean_pattern": """theorem {problem_id} {statement} := by
  by_contra h
  push_neg at h
  -- Derive contradiction
  have c1 : {contradiction1} := by sorry
  have c2 : {contradiction2} := by sorry
  exact absurd c1 (fun _ => c2)""",
        "natural_pattern": """We prove by contradiction.
Assume {negation}. Then {consequence1}.
But this contradicts {consequence2}.
Therefore {conclusion}.""",
        "few_shot_example": """theorem sqrt_two_irrational : ¬ ∃ p q, q ≠ 0 ∧ sqrt 2 = p / q := by
  by_contra ⟨p, q, hq, h⟩
  -- Use parity argument
  sorry""",
        "confidence_keywords": ["by_contra", "contradiction", "absurd", "push_neg"]
    },
    
    "category_theory": {
        "domain": "Category Theory",
        "lean_pattern": """theorem {problem_id} {statement} := by
  -- Commutative diagram or functor property
  rw [← Functor.map_comp]
  have h : {cat_property} := by sorry
  exact {conclusion}""",
        "natural_pattern": """By categorical reasoning and functorial properties.
Consider the diagram: {diagram_desc}
The key fact is {key_fact}.
Therefore {conclusion}.""",
        "few_shot_example": """theorem functor_preserves_composition : F (f ∘ g) = (F f) ∘ (F g) := by
  rfl""",
        "confidence_keywords": ["functor", "morphism", "composition", "commutative", "diagram"]
    }
}

# Mapping: Problem ID → Domain
PROBLEM_DOMAIN_MAP = {
    "A0004": "combinatorics",    # Pigeonhole-like
    "B0014": "number_theory",     # GCD/divisibility
    "B0017": "analysis",          # Convergence
    "E0019": "graph_theory",      # Graph property
    "E0020": "geometry",          # Geometric proof
    "E0025": "induction",         # Induction
    "E0030": "finite_case",       # Finite analysis
    "E0035": "algebra",           # Algebraic structure
    "E0038": "logic",             # Logical proof
    "E0045": "category_theory"    # Categorical
}

def get_template(domain):
    """Get template by domain name"""
    return PROOF_TEMPLATES.get(domain)

def get_domain_for_problem(problem_id):
    """Get domain for a specific problem"""
    return PROBLEM_DOMAIN_MAP.get(problem_id, "combinatorics")  # default

def list_domains():
    """List all available domains"""
    return list(PROOF_TEMPLATES.keys())
