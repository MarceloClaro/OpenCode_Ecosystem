# Phase 1.1 — Download & Dataset Preparation Plan

**Date**: 30 May 2026  
**Dataset Scope**: 700 problems from 12 domains  
**Status**: FINAL (counts confirmed via GitHub API)

---

## 📊 Final Domain Breakdown

Total confirmed: **700 problems** (1.63x vs v1.0's 430)

| Domain | Files | % | Cumulative |
|--------|-------|---|------------|
| ErdosProblems | 430 | 61.4% | 430 |
| Wikipedia | 124 | 17.7% | 554 |
| GreensOpenProblems | 44 | 6.3% | 598 |
| WrittenOnTheWallII | 26 | 3.7% | 624 |
| Paper | 23 | 3.3% | 647 |
| OEIS | 21 | 3.0% | 668 |
| Mathoverflow | 11 | 1.6% | 679 |
| Books (subdirs) | 3 | 0.4% | 682 |
| Other | 5 | 0.7% | 687 |
| Subsets | 2 | 0.3% | 689 |
| Millenium | 4 | 0.6% | 693 |
| OpenQuantumProblems | 3 | 0.4% | 696 |
| HilbertProblems | 2 | 0.3% | 698 |
| Kourovka | 2 | 0.3% | 700 |
| **TOTAL** | **700** | **100%** | **700** |

---

## 📥 Download Strategy

### Option A: Clone Entire Repo (Recommended)
```bash
git clone --depth 1 https://github.com/google-deepmind/formal-conjectures.git
cd formal-conjectures/FormalConjectures
```

**Pros**:
- All data + history
- Can follow git updates
- Preserve structure

**Cons**:
- Large (~50-100 MB)
- Slower (~5 min)

**Recommendation**: ✅ Use this for Phase 1.1

---

### Option B: Download via GitHub API (Parallel)
Extract URLs from GitHub API, download in parallel with curl.

**Pros**:
- Faster (~2 min)
- Minimal space

**Cons**:
- Need to handle rate limiting (60 req/min unauthenticated)
- Complex parallel logic

---

## 🔄 Implementation Plan

### Stage 1: Clone (5 min)
```bash
git clone --depth 1 https://github.com/google-deepmind/formal-conjectures.git fc_repo
# Output: ~50-100 MB
```

### Stage 2: Extract Structure (10 min)
```bash
cd fc_repo/FormalConjectures

# Copy all .lean files preserving domain structure
mkdir -p ../../aletheia-superhuman-validation/raw_data/formal-conjectures
for domain in ErdosProblems Wikipedia GreensOpenProblems WrittenOnTheWallII Paper OEIS Mathoverflow Books Other Subsets Millenium OpenQuantumProblems HilbertProblems Kourovka; do
    if [ -d "$domain" ]; then
        cp -r "$domain" ../../aletheia-superhuman-validation/raw_data/formal-conjectures/
    fi
done

# Handle Books subdirs separately
if [ -d "Books" ]; then
    mkdir -p ../../aletheia-superhuman-validation/raw_data/formal-conjectures/Books
    cp Books/**/*.lean ../../aletheia-superhuman-validation/raw_data/formal-conjectures/Books/
fi
```

### Stage 3: Parse & Structure (30 min)
Parse all 700 .lean files into `erdos_700_enriched.json`:

```json
{
  "metadata": {
    "source": "google-deepmind/formal-conjectures",
    "date": "2026-05-30",
    "version": "1.0",
    "total_problems": 700,
    "domains": {
      "ErdosProblems": 430,
      "Wikipedia": 124,
      ...
    }
  },
  "problems": [
    {
      "id": "E001",
      "domain": "ErdosProblems",
      "filename": "1.lean",
      "statement": "For any set of n ≥ ...",
      "types": ["combinatorics", "graph_theory"],
      "difficulty": "medium",
      "dependencies": ["Finset", "Card"],
      "raw_lean_code": "theorem ..."
    },
    ...
  ]
}
```

**Size estimate**: 2-3 MB

### Stage 4: NLP Enrichment (1-2 hours)
Extend with NLP analysis:

```python
for problem in problems:
    # Extract statement from Lean code
    statement = extract_statement_from_lean(problem.raw_lean_code)
    
    # Classify problem types (ML)
    types = classify_types(statement)  # ["combinatorics", "discrete_math"]
    
    # Infer difficulty from statement length
    difficulty = infer_difficulty(len(statement), "lean_complexity")
    
    # Extract dependencies from Lean imports
    dependencies = extract_dependencies(problem.raw_lean_code)
    
    # Enrich
    problem.update({
        "statement": statement,
        "types": types,
        "difficulty": difficulty,
        "dependencies": dependencies,
        "enriched": True
    })
```

**Model**: Use v1.0 trained classifier (F1=0.91)

### Stage 5: Validation (30 min)
Spot-check 50 samples (7% of 700):
- 10 per major domain (Erdős, Wikipedia, GreensOpenProblems)
- Random selection from others

**Criteria**:
- Statement extraction: correct
- Type classification: ≥0.85 precision
- Difficulty assignment: reasonable
- Dependencies: complete

---

## 🎯 Success Criteria

| Criterion | Target | v1.0 Baseline | Notes |
|-----------|--------|---------------|-------|
| **Total problems** | 700 | 430 | ✅ +63% |
| **Domains** | 12+ | 1 | ✅ Multi-domain |
| **Parse success** | ≥95% | 100% | Expect slight degradation (non-Erdős) |
| **Type classification F1** | ≥0.88 | 0.91 | Domain shift, acceptable -0.03 |
| **Enrichment time** | <2 hours | N/A | Parallel NLP |
| **Output JSON size** | 2-3 MB | 0.8 MB | Proportional |
| **Spot-check (50 samples)** | ≥90% quality | N/A | Manual review |

---

## ⏱️ Timeline

| Stage | Task | Time | Dependency |
|-------|------|------|------------|
| 1 | Clone repo | 5 min | Network |
| 2 | Extract .lean files | 10 min | Stage 1 |
| 3 | Parse JSON structure | 30 min | Stage 2 |
| 4 | NLP enrichment | 1-2 hours | Stage 3 |
| 5 | Spot-check validation | 30 min | Stage 4 |
| 6 | Save to repo | 5 min | Stage 5 |
| **TOTAL** | **Phase 1.1** | **2.5-3.5 hours** | Sequential |

---

## 📝 Output Artifacts

### After Phase 1.1 Completion:

1. **raw_data/formal-conjectures/** — Directory with all 700 .lean files preserved
   ```
   raw_data/formal-conjectures/
   ├── ErdosProblems/
   │   ├── 1.lean
   │   ├── 10.lean
   │   └── ...
   ├── Wikipedia/
   │   └── ...
   └── ...
   ```

2. **data/erdos_700_enriched.json** — Structured dataset (2-3 MB)
   ```json
   {
     "metadata": { ... },
     "problems": [ ... ]  // 700 items
   }
   ```

3. **ENRICHMENT_REPORT.md** — QA results
   - Parse success rate: X%
   - Type classification F1: X
   - Difficulty distribution
   - Domain breakdown analysis
   - 50 spot-check results

---

## 🚀 Next Phase (1.2)

After Phase 1.1 completion, proceed to **Phase 1.2: Infrastructure Setup**:

- [ ] Detect GPU availability (CUDA, compute capability)
- [ ] Create distributed_spec_processor.py (single-GPU or CPU fallback)
- [ ] Benchmark: 430 → 700 in <30s on target hardware
- [ ] Setup experiment tracking (MLflow, W&B)

---

## 🔍 Decision Gates

### Gate 1: Parse Success (Stage 3)
- If <95% problems parse successfully
- **Action**: Debug most common Lean syntax variations, retry parsing

### Gate 2: Type Classification (Stage 4)
- If F1 <0.85
- **Action**: Retrain classifier on combined domains, or accept degradation with explanation

### Gate 3: Spot-Check (Stage 5)
- If <85% quality in spot-check
- **Action**: Review failure patterns, apply manual corrections to failed samples

---

## 💾 Storage Plan

**Repository structure**:
```
aletheia-superhuman-validation/
├── data/
│   ├── erdos_430_baseline.json     ← v1.0 (existing)
│   ├── erdos_700_enriched.json     ← v1.1 NEW
│   └── distributions/              ← Domain analysis
├── raw_data/
│   └── formal-conjectures/         ← 700 .lean files
├── enrichment/
│   ├── classifier_model.pkl        ← Pre-trained from v1.0
│   └── type_ontology.json          ← 68 → 80+ reasoning types
└── reports/
    └── ENRICHMENT_REPORT.md        ← QA summary
```

**Size budget**:
- raw_data: ~5-10 MB (compressed: 1-2 MB)
- erdos_700_enriched.json: 2-3 MB
- Models/reports: 0.5 MB
- **Total**: ~8-16 MB (well within GitHub LFS)

---

## ✅ Status

- [x] Domain discovery (17 domains explored)
- [x] Final counts confirmed (700 total)
- [x] Download strategy defined
- [ ] Clone repo
- [ ] Extract .lean files
- [ ] Parse JSON structure
- [ ] NLP enrichment
- [ ] Spot-check validation
- [ ] Commit to aletheia-superhuman-validation/data/

---

**Ready to proceed with Stage 1?** ✨

