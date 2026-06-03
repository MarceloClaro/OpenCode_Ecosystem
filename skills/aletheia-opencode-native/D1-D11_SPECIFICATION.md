# CORA-Eval 11-Dimensional Proof Evaluation Framework
## Complete Specification (D1–D11)

**Version:** 2.0 (Phase 2 Week 2)  
**Status:** Active (D1–D10 Validated, D11 Newly Added)  
**Last Updated:** 2026-05-30

---

## Overview

The CORA-Eval framework measures mathematical proofs across **11 independent dimensions**, each targeting a distinct aspect of proof quality. The framework produces:
- Individual dimensional scores (0–10 scale)
- Aggregate tier classification (A, B, C, D)
- Comparative analysis vs. previous versions
- Improvement recommendations

---

## Dimensional Specifications

### **D1: Hypothesis Clarity** (Weight: 0.10)

**Definition:** Clarity and precision of the main theorem statement.

**Measures:**
- Is the theorem statement unambiguous?
- Are all variables and assumptions clearly defined?
- Is the main result/goal explicitly stated?

**Scoring Guide:**
- **9–10:** Crystal clear theorem, all terms defined in context, no ambiguity
- **7–8:** Clear statement with minor notation issues or implicit assumptions
- **5–6:** Understandable but requires inference or re-reading
- **3–4:** Ambiguous statement, unclear what is being proved
- **0–2:** Severely unclear or misleading statement

**Examples:**
- ✅ Good: "For any set A, prove that A ∪ A = A" (clear, simple)
- ❌ Bad: "Show something about the thing in that context" (vague)

---

### **D2: Mathematical Insight** (Weight: 0.10)

**Definition:** Depth of mathematical understanding and novelty of approach.

**Measures:**
- Does the proof reveal deeper mathematical structure?
- Is the approach novel or insightful vs. mechanical?
- Does it connect to broader mathematical concepts?

**Scoring Guide:**
- **9–10:** Breakthrough insight, novel technique, deep connection to theory
- **7–8:** Solid insight, uses mathematical structure effectively
- **5–6:** Routine approach, but mathematically sound
- **3–4:** Mechanical manipulation, limited insight
- **0–2:** Incorrect or trivial understanding

**Examples:**
- ✅ Good: Proof using symmetry, duality, or unexpected isomorphism
- ❌ Bad: Brute force case enumeration without pattern recognition

---

### **D3: Proof Rigor** (Weight: 0.12)

**Definition:** Formal rigor, precision, and logical soundness of the proof.

**Measures:**
- Are all steps formally justified?
- Are logical connectives used correctly?
- Are inference rules applied validly?

**Scoring Guide:**
- **9–10:** Rigorous formal proof, every step justified, no gaps
- **7–8:** Mostly rigorous, minor informal steps acceptable in context
- **5–6:** Generally sound but with some unjustified leaps
- **3–4:** Multiple gaps in logic or incorrect applications of rules
- **0–2:** Fundamentally flawed reasoning

**Examples:**
- ✅ Good: "By axiom X, we have A. Since B follows from A by theorem Y, the conclusion holds."
- ❌ Bad: "It's clear that... [no justification]"

---

### **D4: Case Analysis** (Weight: 0.12)

**Definition:** Coverage of all cases and subcases required for completeness.

**Measures:**
- Are all necessary cases identified?
- Does each case receive adequate treatment?
- Are boundary conditions considered?

**Scoring Guide:**
- **9–10:** Exhaustive case analysis, no missing cases
- **7–8:** All major cases covered, minor edge cases implicit
- **5–6:** Most cases covered, 1–2 gaps
- **3–4:** Significant case omissions
- **0–2:** Proof only handles special case(s)

**Examples:**
- ✅ Good: "Case 1: x > 0. Case 2: x = 0. Case 3: x < 0." (all covered)
- ❌ Bad: "When x is positive..." (what about x ≤ 0?)

---

### **D5: Formal Correctness** (Weight: 0.12)

**Definition:** Absence of logical errors, type errors, and syntactic mistakes.

**Measures:**
- Are there any contradictions in the proof?
- Are all type/domain constraints satisfied?
- Are there any false statements presented as fact?

**Scoring Guide:**
- **9–10:** No errors, syntactically and semantically correct
- **7–8:** Minor typos or notational inconsistencies, no logical error
- **5–6:** One subtle error that doesn't break the main argument
- **3–4:** Multiple errors, but proof structure salvageable
- **0–2:** Fundamental error(s) invalidate the proof

**Examples:**
- ✅ Good: "Set A ⊆ B and element x ∈ A, therefore x ∈ B" (correct logic)
- ❌ Bad: "A ⊆ B and x ∉ A, therefore x ∉ B" (false; x could be in B)

---

### **D6: Induction Validity** (Weight: 0.10)

**Definition:** Validity of inductive reasoning (if applicable).

**Measures:**
- Is the base case correctly established?
- Is the inductive hypothesis clearly stated?
- Does the inductive step correctly use the hypothesis?

**Scoring Guide (if applicable):**
- **9–10:** Induction rigorous and complete (base + step correct)
- **7–8:** Induction sound with minor gaps
- **5–6:** Induction present but loose in one direction
- **3–4:** Inductive step flawed or incomplete
- **0–2:** Induction fundamentally broken or absent when needed
- **N/A:** Not applicable if proof doesn't use induction

**Examples:**
- ✅ Good: "Base: n=1, [verified]. Inductive step: Assume true for n, prove for n+1 by [method]."
- ❌ Bad: "Assume true for all n < k, prove for k" (weak form of induction without justification)

---

### **D7: Tactic Usage** (Weight: 0.10)

**Definition:** Correct and appropriate use of proof tactics/strategies (Lean tactics, inference rules, etc.).

**Measures:**
- Are tactics applied correctly?
- Are tactics chosen appropriately for the goal?
- Are there more efficient tactic sequences?

**Scoring Guide:**
- **9–10:** Expert tactic usage, efficient and elegant
- **7–8:** Correct tactics, some redundancy
- **5–6:** Mostly correct, minor misapplications
- **3–4:** Frequent inappropriate or incorrect tactic use
- **0–2:** Fundamental misunderstanding of tactics

**Examples (Lean):**
- ✅ Good: Using `simp` to simplify, then `exact` to close
- ❌ Bad: Using `sorry` to skip proof steps

---

### **D8: Lemma Usage** (Weight: 0.08)

**Definition:** Appropriate selection and application of lemmas.

**Measures:**
- Are lemmas correctly applied?
- Is the choice of lemmas justified?
- Are supporting lemmas created when needed?

**Scoring Guide:**
- **9–10:** Optimal lemma selection, each lemma essential and well-applied
- **7–8:** Good lemma choices, appropriate application
- **5–6:** Adequate lemma usage with minor redundancy
- **3–4:** Lemmas misapplied or unnecessary
- **0–2:** Lemma errors or critical lemma missing

**Examples:**
- ✅ Good: Using `list.append_assoc` when proving list properties
- ❌ Bad: Importing a lemma about groups when proving properties of integers

---

### **D9: Edge Case Coverage** (Weight: 0.08)

**Definition:** Coverage of boundary and special cases.

**Measures:**
- Are empty/null cases handled?
- Are maximal/minimal cases tested?
- Are degenerate cases considered?

**Scoring Guide:**
- **9–10:** All edge cases explicitly verified
- **7–8:** Most edge cases covered, one or two implicit
- **5–6:** Edge cases mentioned but some gaps
- **3–4:** Several important edge cases missed
- **0–2:** Edge case failures invalidate proof

**Examples:**
- ✅ Good: "Empty list case: trivial. Single element: verified. Two+ elements: by induction."
- ❌ Bad: Proof assumes non-empty list without checking

---

### **D10: Overall Soundness** (Weight: 0.00)

**Definition:** Overall validity and completeness of proof.

**Measure:** Meta-dimension computed from D1–D9.

**Calculation:**
```
overall_soundness = average(D1, D2, ..., D9)
```

**Notes:**
- Not independently scored; derived from other dimensions
- Used for tiering decisions and comparative analysis
- Provides single summary metric

---

## **D11: Proof Elegance & Pedagogical Clarity** (Weight: 0.08) — NEW

**Definition:** Elegance of presentation, pedagogical structure, and accessibility for learning.

**Measures:**
- Is the proof presented elegantly (minimal steps, clear structure)?
- Would a student learn valuable concepts from this proof?
- Is the proof accessible without unnecessary complexity?

**Scoring Guide:**
- **9–10:** Canonical/elegant proof, teaches mathematical intuition, minimal but complete
- **8:** Elegant presentation with clear pedagogical value
- **6–7:** Adequate structure, but somewhat verbose or lacking pedagogical insight
- **4–5:** Correct but unnecessarily complex or hard to follow
- **2–3:** Dense or convoluted, difficult to extract insights
- **0–1:** Inelegant or misleading presentation

**Pedagogical Value Indicators:**
- Clear lemma progression (lemmas build intuition)
- Explicit statement of key ideas before technical details
- Connection to broader mathematical concepts
- Examples or intuition provided
- Minimal "magic" steps

**Examples:**
- ✅ High (9): Modus Ponens proof — canonical form, teaches logical structure
- ✅ High (8.5): Set union proof with clear case analysis, simple definitions
- ⚠️ Medium (6.5): Ε-δ limit definition — necessarily technical, but can be clearer
- ❌ Low (4): Correct uniqueness proof of prime factorization — dense, lacks intuition
- ❌ Very Low (2): Brute-force proof of simple statement with 20+ cases

**Domain-Specific Guidance:**
- **Set Theory:** Reward simple, definition-based proofs (high D11)
- **Algebra:** Reward structure-revealing proofs (high D11)
- **Analysis:** Lower D11 expected due to inherent complexity
- **Logic:** Reward canonical forms (e.g., natural deduction, sequent calculus)
- **Number Theory:** Reward proofs revealing deeper number-theoretic structure

---

## Dimensional Weights Summary

| Dimension | Name | Weight | Category | D1–D10? |
|-----------|------|--------|----------|---------|
| D1 | Hypothesis Clarity | 0.10 | Statement | ✅ |
| D2 | Mathematical Insight | 0.10 | Understanding | ✅ |
| D3 | Proof Rigor | 0.12 | Formality | ✅ |
| D4 | Case Analysis | 0.12 | Completeness | ✅ |
| D5 | Formal Correctness | 0.12 | Correctness | ✅ |
| D6 | Induction Validity | 0.10 | Technique | ✅ |
| D7 | Tactic Usage | 0.10 | Implementation | ✅ |
| D8 | Lemma Usage | 0.08 | Structure | ✅ |
| D9 | Edge Case Coverage | 0.08 | Completeness | ✅ |
| D10 | Overall Soundness | 0.00 | Meta (computed) | ✅ |
| **D11** | **Proof Elegance & Pedagogy** | **0.08** | **Presentation** | **🆕** |
| — | **TOTAL (excluding D10)** | **1.00** | — | — |

---

## Tier Classification

### Tier A: PhD-Level, Publishable
- **Score Threshold:** ≥ 8.0 (minimum on D3, D4, D5)
- **Characteristics:**
  - Rigorous, complete, correct
  - Suitable for academic publication or formal verification
  - May be elegant (high D11) or technical (low D11)
- **Improvement Suggestions:** Minor refinement only

### Tier B: High Quality, Minor Revisions
- **Score Threshold:** 7.0–7.99
- **Characteristics:**
  - Sound proof, but with small gaps or clarity issues
  - Acceptable for course/textbook with revisions
- **Improvement Suggestions:** Clarify specific dimension(s)

### Tier C: Acceptable, Significant Revision Needed
- **Score Threshold:** 6.0–6.99
- **Characteristics:**
  - Proof mostly correct but with notable gaps
  - Requires rework before publication
- **Improvement Suggestions:** Major revisions in D3–D5

### Tier D: Below Standard, Major Rework Required
- **Score Threshold:** < 6.0
- **Characteristics:**
  - Proof has significant errors or gaps
  - Not suitable for publication without substantial revision
- **Improvement Suggestions:** Fundamental reworking needed

---

## Scoring Examples: 5 Pilot Problems

### Pilot 001: Set Union Property (Set Theory, Easy)
**Theorem:** For any set A, A ∪ A = A

| D | Score | Reasoning |
|---|-------|-----------|
| D1 | 9.0 | Crystal clear statement |
| D2 | 8.0 | Basic set theory, pedagogical |
| D3 | 9.0 | Two-direction inclusion, rigorous |
| D4 | 9.0 | All cases (x ∈ A, x ∉ A) covered |
| D5 | 9.0 | No logical errors |
| D6 | N/A | Not applicable |
| D7 | 8.5 | Simple tactic application |
| D8 | 8.0 | No lemmas needed; structure clear |
| D9 | 9.0 | Handles all set elements |
| D10 | 8.8 | Avg(D1–D9 applicable) |
| **D11** | **8.5** | **Simple, elegant, highly teachable** |
| **AVG** | **8.8** | **Tier A** |

---

### Pilot 003: Modus Ponens (Logic, Intermediate)
**Theorem:** From P and (P → Q), derive Q

| D | Score | Reasoning |
|---|-------|-----------|
| D1 | 9.5 | Canonical logical form |
| D2 | 9.0 | Foundational logical insight |
| D3 | 9.0 | Formally rigorous (axiom or inference rule) |
| D4 | 9.0 | No case analysis needed (universal rule) |
| D5 | 9.5 | No logical errors |
| D6 | N/A | Not inductive |
| D7 | 9.0 | Clean, direct tactic |
| D8 | N/A | No lemmas |
| D9 | N/A | No edge cases |
| D10 | 9.1 | Avg(D1–D7 applicable) |
| **D11** | **9.0** | **Canonical form; teaches logical structure** |
| **AVG** | **9.1** | **Tier A (highest tier)** |

---

### Pilot 004: Ε-δ Limit Definition (Analysis, Graduate)
**Theorem:** Prove lim(x→a) f(x) = L given ε-δ conditions

| D | Score | Reasoning |
|---|-------|-----------|
| D1 | 7.5 | Clear but technical statement |
| D2 | 7.0 | Solid analysis, standard approach |
| D3 | 8.5 | Rigorous but complex |
| D4 | 7.0 | Case analysis over ε, δ ranges |
| D5 | 8.5 | Correct, but subtle details |
| D6 | N/A | Not inductive |
| D7 | 7.5 | Standard analysis tactics |
| D8 | 7.0 | Uses continuity/definition lemmas |
| D9 | 7.5 | Boundary cases (ε→0, δ→0) |
| D10 | 7.5 | Avg(D1–D9) |
| **D11** | **6.5** | **Necessarily technical; harder to make pedagogical** |
| **AVG** | **7.4** | **Tier B** |

---

## Integration with Aletheia Pipeline

### Architect Agent
- Selects reasoning types based on domain (D2 insight)
- Generates proof skeleton with structure guidelines

### Verifier Agent (V1–V3 + V7)
- V1: Dimensional verification
- V2: Algebraic verification
- V3: Counterexample detection
- **V7 (NEW):** D11 elegance & pedagogy assessment

### Auditor Agent
- Scores D1–D11 (10 weighted + 1 meta)
- Assigns tier (A–D)
- Generates improvement suggestions

### Decision Node Integration
- Records D11 assessment decisions (d11_assessment_pilot_NNN)
- Tracks design choices for D11 calibration

---

## Calibration & Validation

### D1–D10 Validation
- ✅ **Aletheia Benchmark:** 10 curated problems, 100% Tier A achieved
- ✅ **V4 Comparison:** 33.5% improvement (6.23 → 8.31 avg score)
- ✅ **DecisionNode:** 30+ decisions recorded, 100% consistency

### D11 Validation (Week 2 Pilot)
- **Pilot Dataset:** 5 hand-crafted problems (set theory, algebra, logic, analysis, number theory)
- **Expected Results:** Elegance scores vary 6.5–9.0 (domain-dependent)
- **Integration:** Full pipeline (Architect → Verifier V7 → Auditor) supporting D11

---

## Future Work (Week 3+)

1. **V7 Verifier Implementation:** Automated D11 assessment via code analysis
2. **REST API:** `/aletheia/evaluate` accepting proof + returning D1–D11 scores
3. **Benchmark Expansion:** Extend to 20 problems with D11 baseline
4. **D12 Research:** Possible future dimension (e.g., "Reusability" or "Generalizability")

---

**End of Specification v2.0**
