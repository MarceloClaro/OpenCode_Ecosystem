# Aletheia-Superhuman Integration: NEXT STEPS (Immediate Actions)

**Date:** 2026-05-30  
**Status:** ✅ Core implementation COMPLETE (88/88 tests passing)  
**Next:** Execute Option B (Validate on Erdős 700 before publishing)

---

## 🎯 Immediate Priorities (This Week)

### Priority 1: Clone & Analyze Dataset (Est. 2-4 hours)
```bash
# 1. Clone google-deepmind/formal-conjectures
cd ~/projects/validation
git clone https://github.com/google-deepmind/formal-conjectures.git
cd formal-conjectures

# 2. Analyze structure
find FormalConjectures/Erdos -name "*.lean" | wc -l
# Expected: ~387 files (subset of 700)

# 3. Count problem categories
grep -r "theorem erdos" FormalConjectures/Erdos | wc -l
```

**Action Item:** Create script `scripts/analyze_formal_conjectures.py`
```python
#!/usr/bin/env python3
"""Extract Erdős problems from formal-conjectures repo."""

import json
import re
from pathlib import Path

def parse_lean_file(filepath: str) -> dict:
    """Extract problem metadata from Lean file."""
    with open(filepath) as f:
        content = f.read()
    
    # Extract theorem name
    match = re.search(r'theorem\s+(\w+)', content)
    theorem_name = match.group(1) if match else "unknown"
    
    # Extract statement
    match = re.search(r'theorem\s+\w+\s*:\s*(.+?)\s*:=', content, re.DOTALL)
    statement = match.group(1).strip() if match else ""
    
    return {
        "theorem": theorem_name,
        "statement_lean": statement[:500],  # First 500 chars
        "file": str(filepath),
    }

def main():
    repo_root = Path("./formal-conjectures")
    erdos_dir = repo_root / "FormalConjectures" / "Erdos"
    
    problems = []
    for lean_file in erdos_dir.glob("**/*.lean"):
        try:
            problem = parse_lean_file(lean_file)
            problems.append(problem)
        except Exception as e:
            print(f"Error parsing {lean_file}: {e}")
    
    print(f"Found {len(problems)} Erdős problems")
    
    # Save to JSON
    with open("erdos_problems_raw.json", "w") as f:
        json.dump(problems, f, indent=2)
    
    print(f"Saved to erdos_problems_raw.json")

if __name__ == "__main__":
    main()
```

**Deliverable:** `erdos_problems_raw.json` (list of 387-551 problems)

---

### Priority 2: Enrich Dataset with Metadata (Est. 2-3 hours)
Create `scripts/enrich_erdos_dataset.py`:
```python
#!/usr/bin/env python3
"""Enrich Erdős problems with metadata from teorth/erdosproblems."""

import json
import yaml
from pathlib import Path

def load_teorth_metadata(yaml_path: str) -> dict:
    """Load problem metadata from teorth/erdosproblems YAML."""
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    
    metadata = {}
    for problem in data.get("problems", []):
        metadata[problem["id"]] = {
            "title": problem.get("title", ""),
            "domain": problem.get("domain", "unknown"),
            "difficulty": problem.get("difficulty", "unknown"),
            "prize": problem.get("prize", 0),
            "solved": problem.get("solved", False),
        }
    
    return metadata

def enrich_problems(raw_problems: list, metadata: dict) -> list:
    """Combine raw Lean data with YAML metadata."""
    enriched = []
    
    for problem in raw_problems:
        # Try to match by theorem name
        erdos_num = extract_number(problem["theorem"])  # erdos_123 -> 123
        
        enriched_problem = {
            **problem,
            "erdos_number": erdos_num,
            "metadata": metadata.get(str(erdos_num), {}),
        }
        enriched.append(enriched_problem)
    
    return enriched

def extract_number(theorem_name: str) -> int:
    """Extract Erdős number from theorem name."""
    import re
    match = re.search(r'erdos_(\d+)', theorem_name)
    return int(match.group(1)) if match else 0

def main():
    # Load raw problems
    with open("erdos_problems_raw.json") as f:
        raw = json.load(f)
    
    # Load metadata (requires teorth/erdosproblems clone)
    metadata = load_teorth_metadata("./erdosproblems/data/problems.yaml")
    
    # Enrich
    enriched = enrich_problems(raw, metadata)
    
    print(f"Enriched {len(enriched)} problems")
    
    # Save
    with open("erdos_700_enriched.json", "w") as f:
        json.dump(enriched, f, indent=2)
    
    print("Saved to erdos_700_enriched.json")

if __name__ == "__main__":
    main()
```

**Deliverable:** `erdos_700_enriched.json` (problems with domain, difficulty, prize, etc.)

---

### Priority 3: Create Validation Plan Document ✅ DONE
See: `VALIDATION_PLAN.md` (already created)

---

## 📋 Week 1 Checklist

- [ ] **Monday:** Clone formal-conjectures repo, run analysis script
  - Deliverable: `erdos_problems_raw.json` (387-551 problems)
  - Expected time: 2 hours

- [ ] **Tuesday:** Enrich dataset with metadata
  - Deliverable: `erdos_700_enriched.json` (with domain, prize, etc.)
  - Expected time: 2 hours

- [ ] **Wednesday:** Data validation & lake setup
  - Task: Verify all problems compile in Lean 4
  - Task: Set up `lake build` test environment
  - Expected time: 3 hours

- [ ] **Thursday-Friday:** Design batch processor
  - Create `spec_batch_processor.py` (chains SPEC-013 → SPEC-016)
  - Add progress tracking & checkpointing
  - Test on 10-20 problems (not full 700 yet)
  - Expected time: 4 hours

---

## 🚀 Week 2-3 Plan (High-Level)

### Week 2: Lean Enhancement Validation + Full Pipeline
- **PHASE 2.2-2.3:** Test Lean enhancement on 50 sample problems
- **PHASE 3.1-3.2:** Run full pipeline on 700 problems (in batches)
  - Batch size: 100 problems × 7 batches
  - Parallel processing: 8 workers
  - Checkpoint after each batch

### Week 3: Metrics + Publication
- **PHASE 3.3:** Compare results vs Aletheia 6.1% baseline
- **PHASE 4.1-4.3:** Create reports & publish to GitHub

---

## 📊 Success Metrics (Option B)

| Metric | Target | How to Validate |
|--------|--------|-----------------|
| Success Rate | ≥ 8% | Count problems passing SPEC-015 |
| vs Baseline | +1.9pp | Compare: (our_rate - 0.061) |
| Lean Boost | +8% | Compare Cora before/after Lean |
| Ground Truth | 9/9 | All AlphaProof-solved problems should pass |
| Code Quality | 0 errors | All tests pass, no crashes |
| Documentation | Complete | VALIDATION_REPORT.md published |

---

## 🔗 File Dependencies

```
erdos_700_enriched.json (input)
    ↓
spec_batch_processor.py (PHASE 3.1)
    ├─ uses spec_013_prompt_integration.py
    ├─ uses spec_014_cora_wrapper.py
    ├─ uses spec_014_lean_verifier.py
    ├─ uses spec_015_erdos_evaluator.py
    └─ uses spec_016_scaling_law.py
    ↓
erdos_700_pipeline_results.json (output)
    ↓
validation_metrics.py (PHASE 3.2)
    ↓
METRICS_700_PROBLEMS.json
    ↓
VALIDATION_RESULTS_COMPARISON.md (vs 6.1%)
    ↓
VALIDATION_REPORT.md (publish)
```

---

## ⚠️ Critical Blockers

### Blocker 1: Lean 4 environment setup
- **Status:** Unknown (not set up yet)
- **Action:** Test `lake build` on sample problem this week
- **Fallback:** Use pattern matching (v1.0) if lake unavailable

### Blocker 2: Dataset completeness
- **Status:** Assuming 700 problems available
- **Action:** Verify count in formal-conjectures repo
- **Fallback:** Use available subset (maybe 387 instead of 700)

### Blocker 3: Success rate target (8%)
- **Status:** Unknown (depends on real data)
- **Action:** Run PHASE 3 and measure
- **Fallback:** Publish as v1.0-beta if < 8%, document gap

---

## 📞 Decision Points

### Decision 1: Use Real Lean 4 Compilation?
- **Yes (v2.0):** Real lake build, better accuracy but slower
- **No (v1.0):** Pattern matching, fast but less accurate
- **Recommendation:** Start with pattern matching (v1.0), upgrade in v2.0

### Decision 2: Validate All 700 or Sample 100?
- **All 700:** Slower, but full validation
- **Sample 100:** Faster, extrapolate to 700
- **Recommendation:** All 700 (only 3 hours with parallel processing)

### Decision 3: Publish as v1.0 or v1.0-beta?
- **v1.0:** Assumes success rate ≥ 8%
- **v1.0-beta:** If < 8%, clearly mark as work-in-progress
- **Recommendation:** Measure first, decide after PHASE 3

---

## 🎁 Deliverables Checklist

### Input Data
- [x] Dataset source identified (google-deepmind/formal-conjectures)
- [ ] 700 problems extracted to JSON
- [ ] Problems enriched with metadata (domain, prize, difficulty)
- [ ] All problems validate (no compilation errors)

### Processing
- [ ] Batch processor created (chains SPEC-013-016)
- [ ] Parallel execution implemented (8 workers)
- [ ] Progress tracking & checkpointing
- [ ] Error logging for failed problems

### Validation
- [ ] 50-problem Lean enhancement sample
- [ ] Tactic extraction accuracy measured
- [ ] Cora V1-V7 boost percentages validated
- [ ] Full 700-problem results collected

### Reports
- [ ] METRICS_700_PROBLEMS.json (statistics)
- [ ] VALIDATION_RESULTS_COMPARISON.md (vs 6.1%)
- [ ] VALIDATION_REPORT.md (complete findings)
- [ ] v2_ROADMAP.md (future work)

### Publication
- [ ] GitHub repo created
- [ ] v1.0 tag & release
- [ ] README.md updated with real metrics
- [ ] Announcement in agent-forum

---

## 🏁 Expected Outcome (Week 3 End)

```
aletheia-superhuman-integration-v1.0
├─ ✅ Core implementation (88/88 tests)
├─ ✅ Real Erdős 700 validation (700 problems)
├─ ✅ Success rate measurement (target: ≥8%)
├─ ✅ Comprehensive documentation
├─ ✅ GitHub publication
└─ ✅ v2.0 roadmap with next steps

Status: PRODUCTION-READY, VALIDATED, PUBLISHED
```

---

## 📞 Contact / Questions

For questions during validation, refer to:
- **Implementation:** `COMPLETION_REPORT.md`
- **Validation Plan:** `VALIDATION_PLAN.md` (this folder)
- **Architecture:** `SKILL.md` (1500+ lines)
- **Quick Start:** `README.md`

---

**Ready to start PHASE 1.2? Begin with Priority 1 above. 🚀**
