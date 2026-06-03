# Aletheia-Superhuman Integration: Validation Plan (Option B)

**Objective:** Validate pipeline against real Erdős 700 dataset before publishing v1.0  
**Target Success Rate:** 8%+ (vs Aletheia baseline 6.1%, +1.9pp improvement)  
**Timeline:** 2 weeks (concurrent phases)

---

## Dataset Sources Identified

### 1. **Google DeepMind Formal Conjectures** ⭐ PRIMARY
- **URL:** https://github.com/google-deepmind/formal-conjectures
- **Size:** 2,615 total problems
  - 1,318 Erdős problems (formalized)
  - 551 Erdős research open
  - 551 Erdős research solved
- **Format:** Lean 4 (mathlib)
- **Last Updated:** 2026-04-08
- **Status:** Active, maintained by Google DeepMind
- **Access:** Apache 2.0 licensed, public

### 2. **Terence Tao's Erdős Problem Database** (YAML Metadata)
- **URL:** https://github.com/teorth/erdosproblems
- **Size:** 1,183 problems total (387 formalized in Lean)
- **Format:** YAML + structured metadata
- **Includes:** Links to OEIS, prizes, citations
- **Status:** Community-maintained

### 3. **AlphaProof Nexus Results Repository**
- **URL:** https://github.com/google-deepmind/alphaproof-nexus-results
- **Contains:** Proofs discovered by AlphaProof (9/353 Erdős problems)
- **Purpose:** Reference for validated solutions
- **Status:** Public benchmark results

### 4. **Erdős Navigator** (Optional)
- **URL:** https://github.com/0bserver07/erdos-navigator
- **Format:** SQLite database + REST API + Python SDK
- **Size:** 1,179 problems with full metadata
- **Purpose:** High-level problem categorization

---

## PHASE 1: Data Extraction & Preparation

### PHASE 1.1: ✅ COMPLETED
**Research repository landscape**
- Identified: Google DeepMind formal-conjectures (primary)
- Identified: Terence Tao erdosproblems metadata
- Identified: AlphaProof Nexus results (validation reference)

### PHASE 1.2: IN PROGRESS
**Extract 700 Erdős problems in structured format**

#### Task 1.2.1: Clone & parse formal-conjectures repo
```bash
git clone https://github.com/google-deepmind/formal-conjectures.git
# Extract all Erdős problem Lean4 files
# Get 551 research open + 149 additional = ~700
```

**Expected output:** `erdos_700_problems.json`
```json
[
  {
    "id": "erdos_1",
    "title": "Problem #1",
    "statement_lean": "theorem erdos_1 : ...",
    "statement_natural": "...",
    "domain": "combinatorics",
    "difficulty": "open",
    "formalized": true,
    "mathlib_deps": ["Finset", "Nat"],
    "solved_status": "open"
  },
  ...
]
```

#### Task 1.2.2: Enrich with metadata from teorth/erdosproblems
- Add OEIS links
- Add prize amounts
- Add citation counts
- Add community reactions

**Expected output:** `erdos_700_enriched.json` (700 problems × 15+ fields)

#### Task 1.2.3: Map to AlphaProof results
- Identify 9 already-solved problems (from AlphaProof results)
- Mark as "ground_truth": true
- Store expected tactic sequences for validation

**Expected output:** `erdos_700_with_ground_truth.json`

### PHASE 1.3: PENDING
**Validate dataset**
- ✓ 700 unique problems (no duplicates)
- ✓ All have valid Lean4 statements
- ✓ All compile in Lean 4 (lake check)
- ✓ No malformed JSON
- ✓ Representativeness check (domains, difficulty)

**Validation report:** `VALIDATION_PHASE1.md`

---

## PHASE 2: Lean Enhancement Model Validation

### PHASE 2.1: PENDING
**Configure real Lean4 compilation (vs pattern matching)**

#### Task 2.1.1: Set up lake build environment
```bash
# In validation environment
git clone https://github.com/google-deepmind/formal-conjectures.git
cd formal-conjectures
lake build
```

#### Task 2.1.2: Extend spec_014_lean_verifier.py for lake integration
```python
class RealLeanVerifier:
    def verify_with_lake(self, problem_id: str, lean_file: str) -> VerificationResult:
        # Call: lake build && lean --run script.lean
        # Parse compiler output for tactic sequences
        # Extract real v/s simulated tactic patterns
        return VerificationResult(...)
```

#### Task 2.1.3: Benchmark: pattern matching vs real compilation
- Run 50 sample problems both ways
- Compare tactic extraction accuracy
- Measure execution time
- Document divergences

**Output:** `LEAN_COMPILATION_BENCHMARK.md`

### PHASE 2.2: PENDING
**Test enhancement model on 50 real proofs**

#### Task 2.2.1: Select 50 representative problems
- 9 from AlphaProof ground truth (with proofs)
- 41 diverse open problems (varied domains)

#### Task 2.2.2: Extract tactics & apply Cora mapping
```python
for problem in sample_50:
    # Run spec_014_lean_verifier.enhance_cora_score_with_lean_verification()
    # Log: original_cora, lean_tactics, boost_per_v, final_cora
    results.append(VerificationOutput(...))
```

**Output:** `LEAN_VALIDATION_50_PROBLEMS.json`
```json
[
  {
    "problem_id": "erdos_1",
    "original_cora_score": 0.45,
    "lean_tactics_extracted": ["simp", "ring", "nlinarith"],
    "tactic_categories": ["LOGICAL", "ARITHMETIC"],
    "cora_v_boosts": {
      "V1": 0.05,
      "V2": 0.20,
      "V3": 0.10,
      "V4": 0.08,
      "V5": 0.22,
      "V6": 0.15,
      "V7": 0.12
    },
    "enhanced_cora_score": 0.62,
    "boost_magnitude": "+37%",
    "formal_verification": "passed",
    "solved_by_alphaproof": false
  },
  ...
]
```

### PHASE 2.3: PENDING
**Validate boost model accuracy**

#### Task 2.3.1: Analyze tactic extraction accuracy
- Compare extracted tactics vs expected (from AlphaProof)
- Measure precision/recall per category
- Identify systematic biases

#### Task 2.3.2: Validate Cora V1-V7 boost percentages
- Expected from training: V1(+15%), V2(+20%), V3(+17%), ...
- Actual from 50-problem sample: ?
- Statistical test: bootstrap confidence intervals

#### Task 2.3.3: Validate enhancement graceful degradation
- 9 problems with full proofs → enhancement works
- 41 problems with no Lean proofs → graceful fallback (no crash)

**Output:** `LEAN_VALIDATION_METRICS.md`

---

## PHASE 3: Full Pipeline Execution (SPEC-013 → SPEC-016)

### PHASE 3.1: PENDING
**Batch processing 700 problems**

#### Task 3.1.1: Create batch processor
```python
class ErdosBatchProcessor:
    def process_700(self):
        for problem in erdos_700:
            # SPEC-013: Prompt generation
            prompt = PromptLibrary.generate(problem)
            
            # SPEC-014: Cora verification
            cora_result = CoraWrapper.verify(prompt)
            
            # SPEC-014-Lean: Enhancement
            enhanced = LeanVerifier.enhance(problem, cora_result)
            
            # SPEC-015: Evaluation
            eval = ErdosEvaluator.grade(enhanced)
            
            # SPEC-016: Scaling (optional)
            budget = ScalingLaw.allocate_budget(problem)
            
            results.append(EvalResult(...))
        
        return results
```

#### Task 3.1.2: Parallelize processing
- 8 workers (CPU-bound: Cora checks)
- 2 workers (I/O-bound: Lean compilation)
- Progress tracking with tqdm

#### Task 3.1.3: Monitor & checkpoint
- Save checkpoint every 100 problems
- Resume from checkpoint if interrupted
- Log any errors with problem IDs

**Output:** `erdos_700_pipeline_results.json` (700 results)

### PHASE 3.2: PENDING
**Collect comprehensive metrics**

#### Task 3.2.1: Success rate calculation
```python
results = load_results()

success_rate = {
    "all_problems": sum(r.success for r in results) / len(results),
    "by_domain": {
        "combinatorics": ...,
        "number_theory": ...,
        ...
    },
    "by_difficulty": {
        "easy": ...,
        "medium": ...,
        "hard": ...
    },
    "with_lean": sum(r.lean_boost > 0 for r in results) / len(results),
    "without_lean": sum(r.lean_boost == 0 for r in results) / len(results),
}

return success_rate
```

#### Task 3.2.2: Score distributions
- Histogram: Cora scores before/after Lean
- Histogram: Autonomy assignment (NONE/TECH/MEANINGFUL/NOVEL)
- Scatterplot: Budget vs problem difficulty

#### Task 3.2.3: Lean enhancement statistics
- % problems with tactics extracted
- Average boost per category
- Correlation: tactic complexity → Cora improvement
- False positive rate (enhancement decreases score)

**Output:** `METRICS_700_PROBLEMS.json`

### PHASE 3.3: PENDING
**Compare vs baseline**

#### Task 3.3.1: Calculate improvement
```python
baseline_aletheia = 0.061  # 6.1% from arxiv paper
our_success_rate = metrics["success_rate"]["all_problems"]
improvement = our_success_rate - baseline_aletheia

target_met = improvement >= 0.019  # 1.9 pp (+31% relative)
```

#### Task 3.3.2: Validate against reference
- 9 AlphaProof-solved problems → should all succeed
- Novelty of solutions → manual spot-check 20 solutions

#### Task 3.3.3: Statistical confidence
- Bootstrap 95% CI on success rate
- Comparison test (vs 6.1% baseline) with power = 0.90

**Output:** `VALIDATION_RESULTS_COMPARISON.md`

---

## PHASE 4: Publication (v1.0 + v2.0 Roadmap)

### PHASE 4.1: PENDING
**Create VALIDATION_REPORT.md**

```markdown
# Aletheia-Superhuman Integration: Validation Report

## Executive Summary
- ✅ Pipeline validated on Erdős 700 real dataset
- ✅ Success rate: X.X% (target: 8%+, baseline: 6.1%)
- ✅ Improvement: +Y.Y pp (+Z% relative to baseline)
- ✅ Lean enhancement: +A% average boost (target: +8%)

## Dataset
- Source: google-deepmind/formal-conjectures
- Size: 700 Erdős problems (551 research open + 149 other)
- Validation: 100% compile in Lean 4

## Methodology
- SPEC-013: Prompt library (50+ templates)
- SPEC-014: Cora V1-V7 verification
- SPEC-014-Lean: Lean4 tactic extraction + enhancement
- SPEC-015: Autonomy assignment & grading
- SPEC-016: Budget scaling (optional)

## Results
### Main Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Success Rate | X.X% | 8%+ | ✅/❌ |
| vs Baseline | +Y.Y pp | +1.9pp | ✅/❌ |
| Lean Boost | +A% | +8% | ✅/❌ |
| with Lean | B% | N/A | - |
| AlphaProof Ground Truth | 9/9 | 9/9 | ✅ |

### By Domain
| Domain | Problems | Success | Rate |
|--------|----------|---------|------|
| Combinatorics | XXX | XX | X.X% |
| Number Theory | XXX | XX | X.X% |
| ... | ... | ... | ... |

### Lean Tactic Effectiveness
| Category | Extraction Acc | Boost | Problems |
|----------|---------------|----|------------|
| SIMPLIFICATION | X% | +X% | XXX |
| ARITHMETIC | X% | +X% | XXX |
| ... | ... | ... | ... |

## Key Findings
1. (Insight from real data)
2. (Insight from real data)
3. ...

## Known Limitations (v1.0)
- Pattern-based tactic extraction (not real lake build)
- No auto-formalization (human-formalized only)
- Dataset bias toward formalizable problems

## Next Steps (v2.0)
- [ ] Real Lean4 compilation with lake build
- [ ] Auto-formalization pipeline
- [ ] Full Erdős 1,200 dataset
- [ ] Multi-agent debate integration
```

### PHASE 4.2: PENDING
**Document v2.0 roadmap**

```markdown
# Aletheia-Superhuman v2.0 Roadmap

## Enhancements
1. **Real Lean4 Compilation**
   - Replace pattern matching with actual lake build
   - Measure real formal_verification_passed rates
   - Cache compiled proofs

2. **Auto-Formalization**
   - SPEC-017: Natural Language → Lean4 formalization
   - Expand beyond 387 formalized Erdős problems
   - Integrate with Mathlib for new definitions

3. **Full 1,200 Erdős Problems**
   - Extend from 700 to 1,179 problems
   - Handle informal statements gracefully
   - Add human interpretation fallback

4. **Multi-Agent Debate (agent-forum)**
   - Lean verifier as formal reviewer
   - Parallel Aletheia (NL) + Formal verdicts
   - Cora V1-V7 arbitration

5. **Performance Optimization**
   - Distributed batch processing (Ray/Dask)
   - GPU-accelerated Lean4 compilation
   - Streaming results pipeline

## Timeline
- Q2 2026: v1.0 validation complete
- Q3 2026: v2.0 real Lean + auto-formalization
- Q4 2026: Full 1,200 problems + multi-agent
- Q1 2027: Production deployment

## Success Criteria
- v1.0: 8%+ success rate (validated)
- v2.0: 12%+ success rate (with real Lean)
- Production: 15%+ success rate (full stack)
```

### PHASE 4.3: PENDING
**Push to GitHub**

```bash
# Create repository
git init aletheia-superhuman-integration
git remote add origin https://github.com/YOU/aletheia-superhuman-integration.git

# Organize structure
scripts/                           # All .py modules + tests
├── spec_013_prompt_integration.py
├── spec_014_cora_wrapper.py
├── spec_014_lean_verifier.py
├── spec_015_erdos_evaluator.py
├── spec_016_scaling_law.py
└── test_*.py

docs/
├── SKILL.md                       # 1500+ lines skill guide
├── README.md                      # Quick start
├── COMPLETION_REPORT.md           # Design & achievements
├── VALIDATION_PLAN.md             # This document
├── VALIDATION_REPORT.md           # Real results (post-validation)
└── v2_ROADMAP.md                  # Future directions

data/
└── erdos_700_with_ground_truth.json  # Input dataset

results/
├── erdos_700_pipeline_results.json   # Full 700 results
├── METRICS_700_PROBLEMS.json         # Statistics
└── VALIDATION_RESULTS_COMPARISON.md  # vs baseline

# Tag as v1.0
git tag -a v1.0-validated -m "Production-ready v1.0 with Erdős 700 validation"
git push origin main --tags
```

---

## PHASE 5: Agent-Forum Integration (Concurrent - Lower Priority)

### Overview
Run Lean verifier as formal reviewer in multi-agent debate system

**Estimated effort:** 2 weeks (parallel with PHASE 3-4)

**Deliverables:**
- `agent_forum_lean_verifier_skill.py` (MCP wrapper)
- Integration tests
- Usage documentation

**Success criteria:**
- Lean + Aletheia verdicts combine without conflicts
- Cora V1-V7 properly weights formal vs NL evidence
- No performance degradation in debate loop

---

## Timeline & Dependencies

```
Week 1 (May 30 - Jun 6)
├─ PHASE 1.2: Data extraction ─────────────────────────────────┐
├─ PHASE 2.1: Lake environment setup ────────────────────┐    │
└─ PHASE 5: Agent-forum design (parallel)                │    │
                                                          ↓    ↓
Week 2 (Jun 7 - Jun 13)
├─ PHASE 1.3: Data validation ──────────────────────┐   │
├─ PHASE 2.2-2.3: Lean model validation (50 problems)─→  │
├─ PHASE 3.1: Batch processing ────────────────┐        │
└─ PHASE 5: Agent-forum implementation (parallel)       │
                                                ↓         ↓
Week 3 (Jun 14 - Jun 20)
├─ PHASE 3.2-3.3: Metrics & comparison ────────────────┐
├─ PHASE 4: Publish v1.0 + v2.0 roadmap ───────────────┤
├─ PHASE 5: Agent-forum testing ───────────────────────┤
└─ GitHub release + announcement ───────────────────────┘
```

---

## Success Criteria (Option B - Validation Complete)

| Criterion | Target | Achieved | Status |
|-----------|--------|----------|--------|
| Dataset extraction | 700 problems | ? | 🔄 |
| Dataset validation | 100% valid | ? | 🔄 |
| Lean model validation | 50 problems | ? | 🔄 |
| Tactic extraction | > 80% accuracy | ? | 🔄 |
| Pipeline execution | 700 problems | ? | 🔄 |
| Success rate | ≥ 8% | ? | 🔄 |
| vs baseline | ≥ +1.9pp | ? | 🔄 |
| Lean boost | +8% | ? | 🔄 |
| v1.0 publication | GitHub release | ? | 🔄 |
| v2.0 roadmap | Documented | ? | 🔄 |

---

## Risk Mitigation

### Risk 1: Lean 4 compilation too slow
- **Mitigation:** Sample-based validation (50 problems), parallelize
- **Fallback:** Stick with pattern matching for v1.0

### Risk 2: Low success rate (< 8%)
- **Mitigation:** Iteratively improve Cora weights, prompt templates
- **Fallback:** Publish as v1.0-beta, document gap in roadmap

### Risk 3: Dataset incomplete/inconsistent
- **Mitigation:** Validate early (PHASE 1.3), use GitHub CI for checks
- **Fallback:** Create synthetic dataset from archived papers

### Risk 4: AlphaProof ground truth unavailable
- **Mitigation:** Reference arxiv paper results, manual spot-checks
- **Fallback:** Validate model without ground truth (regression analysis)

---

## Conclusion

**Option B (Validation Before Publication) is achievable in 3 weeks with:**
1. Real Erdős 700 dataset (google-deepmind/formal-conjectures)
2. Lean enhancement model validated on 50 problems
3. Full pipeline execution with 700 problems
4. Success rate comparison vs 6.1% baseline
5. v1.0 publication with v2.0 roadmap

**Outcome:** Ship production-ready, validated skill with transparent metrics.

---

**Next Action:** Start PHASE 1.2 (data extraction from formal-conjectures repo)
