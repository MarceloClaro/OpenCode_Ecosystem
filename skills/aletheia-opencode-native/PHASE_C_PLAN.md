# Phase C: Real MCP Integration Plan

## Overview
Integrate **4 real MCPs** into Phase 4 validation pipeline to replace mocks with production-grade tool usage.

---

## MCP Target List

| MCP | Purpose | Integration Point | Success Criteria |
|-----|---------|------------------|------------------|
| **websearch** | Query academic sources (arXiv, papers) | ReasoningOrchestrator context | ≥2 sources per reasoning type |
| **scihub** | Extract paper PDFs & abstracts | RefinementAgent enrichment | ≥1 PDF per proof |
| **code-runner** | Execute & validate proof code | VerifierV7 assessment | ≥80% proofs executable |
| **sequential-thinking** | Deep reasoning chain | ProverAgent strategy generation | ≥3-step chains per proof |

---

## Stage 1: MCP Wrapper Design (Phase C Layer)

### 1a. websearch_mcp.py
**Input**: Problem statement + domain tags
**Output**: SearchResult(sources: List[str], metadata: Dict)
**Timeout**: 2s per query
**Fallback**: Return empty list if timeout

```python
class WebSearchMCP:
    def search(query: str, limit: int = 5) -> SearchResult
    def extract_metadata(url: str) -> Dict[str, Any]
```

### 1b. scihub_mcp.py
**Input**: DOI or paper title
**Output**: PaperResult(content: str, doi: str, abstract: str)
**Timeout**: 3s per paper
**Fallback**: Return abstract-only if PDF fails

```python
class SciHubMCP:
    def fetch_paper(doi: str) -> PaperResult
    def extract_abstract(pdf_content: str) -> str
```

### 1c. code_runner_mcp.py
**Input**: Proof code (Python/Lean)
**Output**: ExecutionResult(success: bool, output: str, error: str)
**Timeout**: 1s per execution
**Fallback**: Return error message, mark as failed

```python
class CodeRunnerMCP:
    def execute(code: str, language: str = "python") -> ExecutionResult
    def validate_syntax(code: str) -> bool
```

### 1d. sequential_thinking_mcp.py
**Input**: Problem statement + hypothesis
**Output**: ReasoningChain(steps: List[str], confidence: float)
**Timeout**: 3s per chain
**Fallback**: Return single-step reasoning

```python
class SequentialThinkingMCP:
    def reason(problem: str, hypothesis: str) -> ReasoningChain
    def validate_logic(steps: List[str]) -> float
```

---

## Stage 2: Integration Points (Phase 4 Modification)

### 2a. ReasoningOrchestrator Enhancement
**Before**: `select_for_problem()` returns 3 reasoning types
**After**: Each type includes websearch context

```
select_for_problem(problem)
  └─ for each reasoning_type:
       └─ websearch(problem + reasoning_type)
       └─ enrich metadata with sources
```

### 2b. ProverAgent Enhancement
**Before**: Generate 2 proof strategies (mock)
**After**: Generate 2 strategies + sequential_thinking chains

```
generate_proofs(problem)
  └─ for each strategy:
       └─ sequential_thinking.reason(problem, strategy)
       └─ append steps to proof
```

### 2c. MCPEnricher Enhancement
**Before**: Mock enrichment
**After**: Real scihub extraction

```
enrich_proof(proof)
  └─ extract_doi_from_proof()
  └─ scihub.fetch_paper(doi)
  └─ append abstract + insights
```

### 2d. VerifierV7 Enhancement
**Before**: Score based on structure only
**After**: Execute proof code, validate output

```
assess(proof)
  └─ code_runner.execute(proof)
  └─ if success: +1.5 to D11 score
  └─ else: report error
```

---

## Stage 3: Validation Flow (60 problems)

```
Phase 4 (with Phase C MCPs):
  [1/60] PB-Basic-001
    [1/6] Original score: 4.07
    [2/6] WebSearch + ProofGeneration (2 proofs)
    [3/6] ReasoningOrchestrator (+ websearch context)
    [4/6] MCPEnricher (scihub + code_runner validation)
    [5/6] RefinementAgent
    [6/6] Refined score: 6.57 (expected)
    
  Aggregate metrics:
    - Avg D11 improvement
    - % proofs executable (code_runner success rate)
    - Avg sources per reasoning (websearch hit rate)
    - Avg papers retrieved (scihub success rate)
```

---

## Stage 4: Metrics & Success Criteria

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| D11 improvement | ≥60% | Must maintain Phase 4 baseline |
| Code execution rate | ≥75% | Real proofs should be mostly executable |
| WebSearch hit rate | ≥80% | Sources must be retrievable |
| Paper retrieval rate | ≥50% | Not all DOIs have open papers |
| Timing overhead | <100ms/problem | Must stay <0.1s total |

---

## Stage 5: Rollback & Retry

If any MCP fails:
1. Log error with timestamp
2. Fall back to mock (do NOT crash)
3. Rerun Phase 4 with improved MCP error handling
4. Threshold: Max 3 retries per MCP

---

## Implementation Order

1. ✅ **websearch_mcp.py** (lowest risk, highest value)
2. ✅ **sequential_thinking_mcp.py** (reasoning enrichment)
3. ✅ **scihub_mcp.py** (paper sources)
4. ✅ **code_runner_mcp.py** (proof validation)
5. ✅ **Integrate into Phase 4 pipeline**
6. ✅ **Revalidate Phase 4 with Phase C MCPs**

---

## Expected Outcome

**Before Phase C**:
- D11: 4.02 → 6.57 (+63.54%)
- All scores: Mock-based, no external validation

**After Phase C**:
- D11: 4.02 → 6.80–7.10 (est. +69–77%, +5–8% from real validation)
- Scores backed by:
  - Real paper sources
  - Executable proof code
  - Deep reasoning chains
  - Academic citations

---

## Timeline

- **Stage 1 (Wrappers)**: ~10 min
- **Stage 2 (Integration)**: ~5 min
- **Stage 3 (Validation 60p)**: ~1 min
- **Stage 4 (Metrics)**: ~2 min
- **Stage 5 (Rollback plan)**: ~3 min
- **Total**: ~20 min (est.)
