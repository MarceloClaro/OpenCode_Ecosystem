# Strategic Pivot: Research-Level Erdős Problem Solving

**Date**: 30 May 2026  
**Context**: Phase 1.1-1.2 complete. Reassessing true objective beyond dataset validation.

---

## 🎯 True Objective Clarified

**NOT**: Validate an enriched dataset of 670 Erdős problems.

**YES**: Build a system that **SOLVES real Erdős problems** and achieves **citation on the Terence Tao wiki** (https://github.com/teorth/erdosproblems/wiki/).

This is the **only metric that matters** for research-level mathematics.

---

## 📊 Current State vs. Needed State

| Aspect | Current (v1.0-v1.2) | Needed (Research 3.0) |
|--------|---------------------|----------------------|
| **Dataset** | 670 enriched Erdős problems | + Lean formal proofs + verification |
| **Pipeline** | SPEC validation + annotation | Lean proof checker integration + iterative refinement |
| **Benchmarking** | Dataset quality (96%) | **Actual problem solving** on wiki problems |
| **Output Format** | JSON enrichment + reports | LaTeX proofs + Lean code + arXiv paper |
| **Target Outcome** | Internal validation | **Citation on Tao's wiki** (green/partial/solution badge) |

---

## 🏗️ Architecture: Aletheia-Inspired Pipeline

Studying Google DeepMind's Aletheia (paper + code from superhuman/aletheia/):

1. **Problem formalization** (LaTeX → Lean 4)
2. **Multi-turn proof generation** with Gemini Deep Think
3. **Lean verification** (proof checker)
4. **Iterative refinement** on failed verification
5. **arXiv publication** + wiki contribution

**Key insight**: Lean proof checker is **not optional** — it's the validation gate.

---

## 🔄 Proposed 4-Phase Approach

### Phase A: Lean Integration (Weeks 1-2)

**Objective**: Enable Lean proof checking in pipeline

**Tasks**:
- [ ] Install Lean 4 + mathlib4
- [ ] Create proof formalization pipeline (problem statement → Lean code)
- [ ] Build Lean verification loop (check ✅ / debug ❌)
- [ ] Test on 10 simple Erdős problems from wiki

**Output**: `scripts/lean_verifier.py` + `scripts/formalize_to_lean.py`

**Success Criteria**: 10 proofs formalized and verified in Lean

---

### Phase B: Wiki Problem Selection & Baseline (Weeks 2-3)

**Objective**: Target real problems from Tao's wiki with feasible complexity

**Tasks**:
- [ ] Analyze wiki contributions (green=full, yellow=partial, red=incorrect)
- [ ] Identify 15-20 problems of Erdős wiki with known solutions (lit OR partial)
- [ ] Classify by difficulty + reasoning type (combinatorial, analytic, etc.)
- [ ] Run baseline model (Claude/GPT-5.5) on each + measure success rate

**Output**: `data/wiki_problems_selected.json` (15-20 problems) + baseline_report.md

**Success Criteria**: ≥30% baseline success (at least some solutions attempted)

---

### Phase C: Iterative Refinement Loop (Weeks 3-4)

**Objective**: Improve success rate through Lean verification + model iteration

**Process** (for each wiki problem):

```
1. Problem formulation (LaTeX)
   ↓
2. Generate candidate proof (Claude/GPT)
   ↓
3. Formalize to Lean
   ↓
4. Verify in Lean
   ├─ ✅ Success → document, prepare for wiki submission
   └─ ❌ Fail → analyze error → generate refined proof (step 2)
```

**Max iterations**: 3-5 per problem (diminishing returns)

**Fallback**: If proof fails verification, generate "partial result" (partial proof or variant)

**Output**: 
- `proofs/` directory with `.lean` files (verified)
- `reports/wiki_solution_report.md` (summary of attempts)

**Success Criteria**: ≥3-5 full solutions (🟢) OR ≥8-10 partial solutions (🟡)

---

### Phase D: Wiki Contribution & Publication (Week 4)

**Objective**: Submit findings to Tao's wiki + prepare arXiv paper

**Tasks**:
- [ ] Create GitHub issue on teorth/erdosproblems with solutions
- [ ] Format submissions per wiki guidelines (Lean code + proof details)
- [ ] Write paper: "AI Contributions to Erdős Problems: [X] Solutions via Iterative Lean Verification"
- [ ] Submit to arXiv (cs.AI or cs.LO)
- [ ] Monitor for wiki acceptance/citation

**Output**: 
- GitHub issue(s) on teorth/erdosproblems
- arXiv paper (v2 or new)
- Press/blog post

**Success Criteria**: ≥1 problem cited on Tao's wiki (even as yellow/partial)

---

## 🔬 Key Technical Components (NEW)

### 1. Lean Proof Verifier (`lean_verifier.py`)

```python
# Pseudo-code
class LeanVerifier:
    def formalize_problem(self, problem_statement: str) -> str:
        """Convert problem statement → Lean 4 theorem definition"""
        # Uses LLM to create well-formed Lean syntax
        return lean_code
    
    def verify_proof(self, proof: str) -> bool:
        """Run `lean --check` on proof"""
        # subprocess: lean proof.lean
        return success
    
    def analyze_error(self, error_msg: str) -> str:
        """Parse Lean error → refinement suggestion"""
        return refinement_prompt
```

### 2. Iterative Solver (`iterative_solver.py`)

```python
class WikiProblemSolver:
    max_iterations = 5
    
    def solve(self, problem: WikiProblem):
        for iteration in range(self.max_iterations):
            proof = self.model.generate_proof(problem, history)
            lean_code = self.verifier.formalize_problem(problem)
            lean_proof = self.model.generate_lean_proof(proof)
            
            if self.verifier.verify_proof(lean_proof):
                return {"status": "success", "proof": lean_proof}
            
            error = self.verifier.get_last_error()
            history.append((proof, error))
        
        return {"status": "partial", "best_attempt": ...}
```

### 3. Wiki Formatter (`wiki_formatter.py`)

```python
# Format output for Tao's wiki
# - Include Lean code block
# - Include proof narrative
# - Cite prior literature
# - Flag as standalone/variant/building-on-literature
```

---

## 📚 Research Motivation

**Why this matters**:
- Dataset enrichment (v1.0-1.2) is **infrastructure**, not the goal
- **Real validation** = solving research-level problems + verification
- **Lean proof checker** ensures no hallucination/gaps (unlike natural language)
- **Wiki citation** is the benchmark (not internal metrics)

**Expected outcomes**:
- 3-5 full 🟢 solutions (novel or new proofs of known results)
- 8-10 partial 🟡 solutions (variants, partial progress)
- 1-2 arXiv papers
- 1+ citations on Tao's wiki

---

## ⚡ Resource Requirements

| Requirement | Status |
|-------------|--------|
| **Lean 4 + mathlib4** | Need to install |
| **Claude/GPT-5.5 API access** | ✅ Already have |
| **Computational resources** | CPU sufficient (Lean verification is fast) |
| **Domain knowledge** | Use wiki + problem statements (no new research needed) |

---

## 🗂️ File Structure (Proposed)

```
aletheia-superhuman-validation/
├── RESEARCH_LEVEL_PIVOT.md (this file)
├── ROADMAP_V1.1.md (previous — archive)
├── scripts/
│   ├── lean_verifier.py (NEW)
│   ├── formalize_to_lean.py (NEW)
│   ├── iterative_solver.py (NEW)
│   ├── wiki_formatter.py (NEW)
│   └── [existing scripts]
├── proofs/ (NEW)
│   ├── wiki_problem_001.lean
│   ├── wiki_problem_002.lean
│   └── ...
├── data/
│   └── wiki_problems_selected.json (NEW)
├── reports/
│   ├── baseline_report.md (NEW)
│   └── wiki_solution_report.md (NEW)
└── ...
```

---

## 🎯 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Wiki problems solved (🟢)** | ≥3 | 0 |
| **Partial solutions (🟡)** | ≥8 | 0 |
| **Lean-verified proofs** | ≥10 | 0 |
| **arXiv papers** | ≥1 | 0 |
| **Wiki citations** | ≥1 | 0 |

---

## 🚀 Immediate Next Steps (48 hours)

1. **Install Lean 4** → Create test .lean file
2. **Select 5 wiki problems** → Formalize into Lean
3. **Prototype `lean_verifier.py`** → Verify toy proofs
4. **Generate baseline solutions** → Run Claude on selected problems
5. **Document process** → Create PHASE_A_REPORT.md

**Milestone**: By 1 June, have working Lean verification loop on 5 test problems.

---

## 📝 Notes

- v1.0-1.2 dataset is **still valuable** — use as training/reference
- Don't abandon enrichment pipeline — it supports proof generation
- **Lean is NOT optional** — this is the core validation gate
- Success ≠ solving all Erdős problems — even 3 novel contributions = major achievement

---

**Status**: 🟡 **PLANNING**  
**Next Review**: 1 June 2026  
**Owner**: AI Research System (autonomous)
