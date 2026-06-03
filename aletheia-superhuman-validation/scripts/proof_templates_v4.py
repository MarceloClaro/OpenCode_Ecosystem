"""
Improved proof templates (V4) with LLM prompts.

Based on Phase D audit weaknesses:
1. hypothesis_clarity (4.11/10) - Add explicit assumptions
2. case_analysis (4.51/10) - Include pattern matching
3. proof_rigor (4.73/10) - Add justification steps
4. mathematical_insight (4.73/10) - Include conceptual explanation
"""

from enum import Enum
from typing import Dict

class ProofDomain(Enum):
    COMBINATORICS = "combinatorics"
    NUMBER_THEORY = "number_theory"
    ANALYSIS = "analysis"
    GRAPH_THEORY = "graph_theory"
    GEOMETRY = "geometry"
    INDUCTION = "induction"
    FINITE_CASE = "finite_case"
    ALGEBRA = "algebra"
    LOGIC = "logic"
    CATEGORY_THEORY = "category_theory"

# ==================== V4 TEMPLATES (with LLM prompts) ====================

PROOF_TEMPLATES_V4 = {
    ProofDomain.COMBINATORICS: {
        "name": "Combinatorics Proof",
        "base_structure": """
-- Assumptions: {assumptions}
-- Concept: {concept}
theorem {theorem_name} : {statement} := by
  -- Case 1: Base case
  {base_case}
  
  -- Case 2: Inductive step
  {inductive_step}
  
  -- Justification
  {justification}
""",
        "llm_prompt": """
Generate a Lean 4 proof for a combinatorics theorem with these requirements:
1. **Explicit Assumptions**: State all assumptions at the beginning (e.g., "assume finite set S")
2. **Case Analysis**: Use pattern matching or induction if applicable
3. **Proof Rigor**: Include `calc` blocks showing all justification steps
4. **Mathematical Insight**: Add comments explaining why each step works

Statement: {statement}

Include:
- Assumptions section in comments
- Case-by-case analysis (induction if applicable)
- Justification for each major step
- Full Lean 4 code (no `sorry` unless unavoidable)
""",
        "hints": [
            "Use `induction` for recursive structures",
            "Use `decide` for finite case analysis",
            "Use `simp` with domain-specific lemmas",
        ],
    },
    
    ProofDomain.NUMBER_THEORY: {
        "name": "Number Theory Proof",
        "base_structure": """
-- Assumptions: {assumptions}
-- Key insight: {insight}
theorem {theorem_name} : {statement} := by
  -- Assertion: Assume the given premise
  {premise_handling}
  
  -- Analysis: Break into cases if needed
  {case_analysis}
  
  -- Conclusion: Derive the result
  {conclusion}
""",
        "llm_prompt": """
Generate a Lean 4 proof for a number theory theorem with these requirements:
1. **Explicit Assumptions**: State what is given (e.g., "let p be a prime")
2. **Case Splitting**: For parity, divisibility, etc., use `omega` or case analysis
3. **Proof Rigor**: Show all algebraic transformations with `calc` blocks
4. **Mathematical Insight**: Explain divisibility or modular arithmetic steps

Statement: {statement}

Include:
- Clear statement of given facts
- Case-by-case proof if applicable
- Algebraic justifications with `calc` or `ring_nf`
- Full Lean 4 code (prefer `omega` over `sorry`)
""",
        "hints": [
            "Use `omega` for linear arithmetic",
            "Use `mod_cast` for integer/natural conversions",
            "Use `decide` for finite checks",
        ],
    },
    
    ProofDomain.ANALYSIS: {
        "name": "Real Analysis Proof",
        "base_structure": """
-- Assumptions: {assumptions}
-- Goal: Prove limit/convergence/continuity
theorem {theorem_name} : {statement} := by
  -- Setup: Introduce epsilon
  {setup}
  
  -- Find witness: Provide delta or N
  {witness}
  
  -- Verify: Show it works
  {verification}
""",
        "llm_prompt": """
Generate a Lean 4 proof for a real analysis theorem with these requirements:
1. **Explicit Assumptions**: State epsilon-delta definitions explicitly
2. **Witness Construction**: Show how to compute/choose delta or N
3. **Proof Rigor**: Include all inequality transformations with `calc`
4. **Mathematical Insight**: Explain why the witness works (conceptually)

Statement: {statement}

Include:
- Epsilon/delta setup (or convergence definition)
- Construction of witness (explicit calculation)
- Inequality chain proving the result
- Full Lean 4 code (use `field_simp`, `norm_num`, `ring` appropriately)
""",
        "hints": [
            "Use `intro` for epsilon-delta",
            "Use `use` for witness construction",
            "Use `calc` for inequality chains",
            "Use `norm_num` for concrete arithmetic",
        ],
    },
    
    ProofDomain.GRAPH_THEORY: {
        "name": "Graph Theory Proof",
        "base_structure": """
-- Assumptions: {assumptions}
-- Proof method: {method}
theorem {theorem_name} : {statement} := by
  -- Structure: Define graph/tree structure
  {structure}
  
  -- Induction: On number of vertices/edges
  {induction_step}
  
  -- Conclusion: Derive property
  {conclusion}
""",
        "llm_prompt": """
Generate a Lean 4 proof for a graph theory theorem with these requirements:
1. **Explicit Assumptions**: Define what "graph" means (edges, vertices)
2. **Case Analysis**: Use induction on vertex/edge count if tree/forest
3. **Proof Rigor**: Show counting arguments with explicit formulas
4. **Mathematical Insight**: Explain why induction base & step are correct

Statement: {statement}

Include:
- Definition of graph structure assumed
- Induction base case (single vertex)
- Inductive step (adding vertex/edge)
- Full Lean 4 code (use `omega` for counting)
""",
        "hints": [
            "Use `induction` on vertex count",
            "Use `omega` for edge counting",
            "Use pattern matching for tree structure",
        ],
    },
    
    ProofDomain.GEOMETRY: {
        "name": "Geometry Proof",
        "base_structure": """
-- Assumptions: {assumptions}
-- Geometric concept: {concept}
theorem {theorem_name} : {statement} := by
  -- Definitions: Set up angle/distance relationships
  {definitions}
  
  -- Properties: Apply geometric laws
  {properties}
  
  -- Calculation: Compute result
  {calculation}
""",
        "llm_prompt": """
Generate a Lean 4 proof for a geometry theorem with these requirements:
1. **Explicit Assumptions**: Define what points/angles/lines are used
2. **Case Analysis**: Handle special cases (right triangle, etc.) if needed
3. **Proof Rigor**: Use `simp` with geometric lemmas to justify steps
4. **Mathematical Insight**: Explain why a property holds (e.g., angle sum)

Statement: {statement}

Include:
- Assumption about geometric objects
- List of geometric properties used
- Step-by-step application of properties
- Full Lean 4 code (use geometric lemmas: sum_angles_triangle, etc.)
""",
        "hints": [
            "Use `simp` with geometry-specific lemmas",
            "Use `norm_num` for angle calculations",
            "Use `rfl` for trivial equalities",
        ],
    },
    
    ProofDomain.INDUCTION: {
        "name": "Induction Proof",
        "base_structure": """
-- Assumptions: {assumptions}
-- Property: {property}
theorem {theorem_name} : {statement} := by
  -- Base case: n = {base_value}
  {base_case}
  
  -- Inductive step: assume P(n), prove P(n+1)
  intro n _
  intro ih
  {inductive_step}
""",
        "llm_prompt": """
Generate a Lean 4 proof using mathematical induction with these requirements:
1. **Explicit Assumptions**: State what we're proving by induction
2. **Base Case**: Prove P(0) or P(1) explicitly
3. **Proof Rigor**: Show inductive step with all algebraic steps in `calc`
4. **Mathematical Insight**: Explain how induction hypothesis is used

Statement: {statement}

Include:
- Clear induction setup (`induction n`)
- Explicit base case proof
- Inductive hypothesis application
- All algebraic transformations in `calc` blocks
- Full Lean 4 code (no `sorry`)
""",
        "hints": [
            "Use `induction` tactic",
            "Use `ring` for polynomial proofs",
            "Use `omega` for arithmetic",
        ],
    },
    
    ProofDomain.FINITE_CASE: {
        "name": "Finite Case Analysis",
        "base_structure": """
-- Assumptions: {assumptions}
theorem {theorem_name} : {statement} := by
  -- Exhaustively check finite cases
  {cases}
  
  -- Each case is verified
  all_goals {closure}
""",
        "llm_prompt": """
Generate a Lean 4 proof using case analysis on finite set with these requirements:
1. **Explicit Assumptions**: Explain why the set is finite (e.g., boolean, {1..n})
2. **Case Enumeration**: List all cases clearly
3. **Proof Rigor**: Prove each case independently and completely
4. **Mathematical Insight**: Explain why exhaustion suffices

Statement: {statement}

Include:
- Finite set declaration/assumption
- `decide` tactic or `omega` for each case
- Explicit case breakdown if not obvious
- Full Lean 4 code (use `decide` where applicable)
""",
        "hints": [
            "Use `decide` for decidable propositions",
            "Use `omega` for numeric bounds",
            "Use `norm_num` for concrete arithmetic",
        ],
    },
    
    ProofDomain.ALGEBRA: {
        "name": "Algebra Proof",
        "base_structure": """
-- Assumptions: {assumptions}
theorem {theorem_name} : {statement} := by
  -- Properties of algebraic structure
  {properties}
  
  -- Algebraic manipulation
  {manipulation}
  
  -- Conclusion
  {conclusion}
""",
        "llm_prompt": """
Generate a Lean 4 proof for an algebra theorem with these requirements:
1. **Explicit Assumptions**: State field/ring properties used
2. **Case Analysis**: Handle special elements (0, 1, etc.) if relevant
3. **Proof Rigor**: Use `ring`, `field_simp`, or `group` lemmas
4. **Mathematical Insight**: Explain which algebraic property is key

Statement: {statement}

Include:
- Assumptions about algebraic structure
- Algebraic identities applied in order
- Use of `ring` or `field_simp` tactics
- Full Lean 4 code (prefer `ring` over manual expansion)
""",
        "hints": [
            "Use `ring` for polynomial identities",
            "Use `field_simp` for field equations",
            "Use group/ring lemmas from mathlib",
        ],
    },
    
    ProofDomain.LOGIC: {
        "name": "Logic Proof",
        "base_structure": """
-- Theorem: {statement}
theorem {theorem_name} : {statement} := by
  -- Logical structure
  {logical_structure}
  
  -- Apply logical rules
  {logical_rules}
  
  -- Conclusion
  {conclusion}
""",
        "llm_prompt": """
Generate a Lean 4 proof for a logic theorem with these requirements:
1. **Explicit Assumptions**: State what propositions are assumed
2. **Case Analysis**: Use proof by cases or contradiction if needed
3. **Proof Rigor**: Show each logical step with justification
4. **Mathematical Insight**: Explain which logical law is applied

Statement: {statement}

Include:
- Logical propositions definition
- Case analysis or direct proof path
- Use of `by_contra`, `cases`, or `decide`
- Full Lean 4 code (use `decide` for tautologies)
""",
        "hints": [
            "Use `decide` for decidable tautologies",
            "Use `by_contra` for proof by contradiction",
            "Use `cases` for disjunctions",
        ],
    },
    
    ProofDomain.CATEGORY_THEORY: {
        "name": "Category Theory Proof",
        "base_structure": """
-- Assumptions: {assumptions}
-- Category-theoretic property: {property}
theorem {theorem_name} : {statement} := by
  -- Morphism/functor definitions
  {definitions}
  
  -- Category laws: associativity, identity
  {laws}
  
  -- Conclusion
  {conclusion}
""",
        "llm_prompt": """
Generate a Lean 4 proof for a category theory theorem with these requirements:
1. **Explicit Assumptions**: State morphism/functor assumptions
2. **Case Analysis**: Consider identity and composition carefully
3. **Proof Rigor**: Apply category laws (associativity, identity) explicitly
4. **Mathematical Insight**: Explain which universal property is key

Statement: {statement}

Include:
- Morphism/functor setup
- Application of category associativity/identity laws
- Function composition verification
- Full Lean 4 code (use category lemmas from mathlib)
""",
        "hints": [
            "Use `simp` with category lemmas",
            "Use `ext` for functor equality",
            "Use composition and identity laws",
        ],
    },
}

def get_template_v4(domain: ProofDomain) -> Dict:
    """Get improved V4 template for domain."""
    return PROOF_TEMPLATES_V4.get(domain, PROOF_TEMPLATES_V4[ProofDomain.LOGIC])

def get_llm_prompt_v4(domain: ProofDomain, statement: str) -> str:
    """Get LLM prompt for generating proof with V4 quality standards."""
    template = get_template_v4(domain)
    prompt = template["llm_prompt"].format(statement=statement)
    
    # Add common quality requirements
    quality_suffix = """

QUALITY REQUIREMENTS (MUST FOLLOW):
- NO `sorry` placeholders unless absolutely necessary
- Explicit comments for assumptions
- Each major step justified in `calc` blocks or tactic explanation
- Code must be syntactically valid Lean 4
- Use tactics: simp, omega, ring, field_simp, decide, norm_num as appropriate
- Prefer semantic completeness over placeholder tactics
"""
    return prompt + quality_suffix

if __name__ == "__main__":
    # Test
    domain = ProofDomain.ANALYSIS
    stmt = "limit (fun n => 1/n) = 0"
    prompt = get_llm_prompt_v4(domain, stmt)
    print(f"Template for {domain.value}:")
    print(prompt[:200] + "...")
