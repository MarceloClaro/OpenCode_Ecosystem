# SPECIFICATIONS — OpenCode Ecosystem
## SDD (Specification-Driven Development) Contract Document
### Agent: marceloclaro | Version: 2.0.0 | TDD-Aligned

---

> **SDD Philosophy:** Every component must have a formal specification  
> before implementation. Tests are written from specifications.  
> Implementation satisfies tests. Refactor preserves tests.

---

## SPECIFICATION INDEX

| ID | Component | Version | Status |
|----|-----------|---------|--------|
| SPEC-001 | MultiReasoningEngine | 2.0.0 | ✅ Implemented |
| SPEC-002 | OrchestrationEngine | 2.0.0 | ✅ Implemented |
| SPEC-003 | ScientificProductionAgent | 2.0.0 | ✅ Implemented |
| SPEC-004 | SROI Integration Contract | 1.0.0 | ✅ Implemented |
| SPEC-005 | QualityGate System | 1.0.0 | ✅ Implemented |
| SPEC-006 | CitationManager | 1.0.0 | ✅ Implemented |

---

## SPEC-001: MultiReasoningEngine

### Purpose
Implements a multi-modal reasoning system supporting 6 epistemological modes,  
enabling agents to apply context-appropriate cognitive strategies.

### Invariants (always true)
```
INV-MRE-1: confidence ∈ [0.0, 1.0] for all results
INV-MRE-2: mode ∈ {deductive, inductive, abductive, analogical, causal, meta} for all calls
INV-MRE-3: chain_length ≤ config.max_reasoning_chain
INV-MRE-4: metrics.total_invocations monotonically increases
INV-MRE-5: history.length ≤ MAX_HISTORY when log_trace = true
```

### Interface Contract

#### `reason(mode: string, context: object) → ReasoningResult`

**Preconditions:**
- `mode` MUST be a non-empty string ∈ valid modes set
- `context` MUST be a non-null object
- Engine MUST be initialized

**Postconditions:**
- Result MUST contain: `mode`, `confidence`, `trace`, `reasoning_path`
- `result.confidence` ∈ [0.0, 1.0]
- `result.mode` === input `mode` (or fallback mode if error occurred)
- `metrics.total_invocations` increases by exactly 1

**Error Contract:**
- Throws `TypeError` if mode is not a string
- Throws `TypeError` if context is null
- Throws `Error` if mode is not in registered modes set
- On execution failure: activates fallback_mode (no uncaught exceptions)

#### `chainReason(chain: Array<{mode, context}>) → ChainResult`

**Preconditions:**
- `chain` MUST be non-empty array
- `chain.length` ≤ `config.max_reasoning_chain`
- Each step MUST have valid `mode` and `context`

**Postconditions:**
- Result contains `steps` array with `chain.length` entries
- `result.overall_confidence` = mean of step confidences
- Each step's output is injected as context into next step

#### `ensembleReason(modes: string[], context: object, combination: string) → EnsembleResult`

**Preconditions:**
- `modes` is a non-empty array of valid mode strings
- `combination` ∈ {'weighted_avg', 'majority_vote', 'highest_confidence'}

**Postconditions:**
- `result.ensemble_results.length` === `modes.length`
- `result.confidence` is computed per combination strategy
- Failed modes contribute confidence = 0 (no uncaught exceptions)

### Reasoning Mode Specifications

#### DEDUCTIVE (Formal Logic)
```
Input:  premises: string[], rules: Rule[]
        Rule = { name: string, condition: (p: string) → boolean, conclude: (p: string) → string, confidence: number }
Output: conclusions: string[], trace: TraceEntry[]
Logic:  ∀ rule ∈ rules, ∀ premise ∈ premises:
          if rule.condition(premise) then conclusions.push(rule.conclude(premise))
Confidence: mean of matched rule confidence values ∈ [0, 1]
```

#### INDUCTIVE (Pattern Generalization)
```
Input:  observations: Array<{pattern: any}>, min_support: number ∈ [0, 1]
Output: generalizations: Array<{pattern, support, count}>
Logic:  frequency(pattern) = count(pattern) / total_observations
        generalize(pattern) iff frequency(pattern) ≥ min_support
Confidence: mean support across all generalizations
```

#### ABDUCTIVE (Best Explanation)
```
Input:  observation: string, hypotheses: Hypothesis[]
        Hypothesis = { name: string, explanatory_power: [0,1], prior: [0,1], simplicity: [0,1] }
Output: best_explanation: Hypothesis, alternatives: Hypothesis[]
Logic:  score(h) = explanatory_power * 0.5 + prior * 0.3 + simplicity * 0.2
        best_explanation = argmax(score, hypotheses)
Confidence: best_explanation.score
```

#### ANALOGICAL (Structure Mapping)
```
Input:  target: {features: string[]}, cases: Case[]
        Case = { name: string, features: string[], solution: string }
Output: best_analog: Case, ranked_cases: Case[]
Logic:  similarity(A, B) = |A.features ∩ B.features| / |A.features ∪ B.features|  (Jaccard)
        best_analog = argmax(similarity(target, case), cases)
Confidence: best_analog.similarity * domain_overlap
```

#### CAUSAL (Pearl Causality Model)
```
Input:  causal_graph: Edge[], intervention: {variable, value}?
        Edge = { cause: string, effect: string, strength: [0,1], confounders: string[] }
Output: effects: Effect[], intervention_effects: Effect[]
Logic:  adjusted_strength(e) = e.strength - (|e.confounders| * 0.05)
        effect(e) iff e.cause === intervention.variable OR intervention === null
Confidence: mean adjusted_strength across effects
```

#### META (Mode Selection & Self-Monitoring)
```
Input:  query: string, available_data: object
Output: selected_mode: string, mode_scores: object, sub_result: ReasoningResult?
Logic:  score(mode) = |query.lower.includes(trigger) for trigger in mode.triggers| / |mode.triggers|
        selected_mode = argmax(score, all_modes_except_meta)
        If score(selected_mode) > 0: execute selected_mode with context
Confidence: 0.85 (fixed — meta is always confident in its selection)
```

---

## SPEC-002: OrchestrationEngine

### Purpose
Routes, schedules, and manages task execution across 128 specialized agents  
with fault tolerance, load balancing, and multi-reasoning integration.

### Invariants
```
INV-ORCH-1: pool.total_agents = 128 (constant)
INV-ORCH-2: task.skill ∈ SKILL_TAXONOMY (all skill strings)
INV-ORCH-3: metrics.tasks_completed + metrics.tasks_failed ≤ metrics.tasks_dispatched
INV-ORCH-4: parallel executions ≤ config.parallel_limit
INV-ORCH-5: retries per task ≤ config.max_retries
```

### Interface Contract

#### `dispatch(task: Task) → Promise<DispatchResult>`

**Preconditions:**
- `task` MUST be a non-null object
- `task.skill` MUST be a string ∈ SKILL_TAXONOMY
- At least one idle agent MUST have the required skill

**Postconditions:**
- Result contains: `status`, `taskId`, `latency_ms`
- `status` ∈ {'success', 'error'}
- `latency_ms` ≥ 0
- `metrics.tasks_dispatched` increases by exactly 1
- If success: `metrics.tasks_completed` increases by 1
- If error: `metrics.tasks_failed` increases by 1

#### `runPipeline(pipeline: Stage[], options: object) → Promise<PipelineResult>`

**Preconditions:**
- `pipeline` is a non-empty array
- Each stage has a valid `skill`

**Postconditions:**
- Result contains: `pipeline_id`, `total_stages`, `successful_stages`, `stages`, `duration_ms`
- `result.total_stages` === `pipeline.length`
- Stages execute in order (no reordering)
- Critical stage failure aborts pipeline

#### `runParallel(tasks: Task[]) → Promise<ParallelResult>`

**Preconditions:**
- `tasks` is a non-empty array

**Postconditions:**
- `result.total` === `tasks.length`
- `result.successful + result.failed` === `result.total`
- Batch size ≤ `config.parallel_limit`

### AgentPool Specification
```
States: idle → busy (assignTask) → idle (releaseAgent)
         idle → error (on persistent failure)
         error → idle (after circuit breaker reset)

Selection: argmax(score, idle_agents_with_skill) where
  score(a) = primary_skill_match * 0.5 + success_rate * 0.3 + (1/(task_count+1)) * 0.2
```

### CircuitBreaker Specification
```
States: closed → open (after threshold failures)
        open → half-open (after resetAfter ms)
        half-open → closed (on success) | open (on failure)

canCall(agentId): 
  closed → true
  open → false (unless elapsed > resetAfter → half-open)
  half-open → true (allow one test call)

threshold: 5 failures (default)
resetAfter: 30000 ms (default)
```

### Skill Taxonomy
```
scientific:    hypothesis_formation, literature_review, methodology_design,
               data_analysis, statistical_modeling, scientific_writing,
               peer_review, citation_management, meta_analysis,
               sroi_calculation, impact_measurement, systematic_review
reasoning:     deductive_reasoning, inductive_reasoning, abductive_reasoning,
               analogical_reasoning, causal_analysis, meta_cognition,
               chain_of_thought, tree_of_thought, socratic_questioning
data:          data_ingestion, data_cleaning, feature_engineering,
               statistical_analysis, nlp_processing, knowledge_extraction,
               graph_analysis, time_series_analysis, anomaly_detection
orchestration: task_decomposition, agent_routing, load_balancing,
               result_synthesis, error_recovery, priority_scheduling,
               dependency_resolution, parallel_execution
communication: report_generation, visualization, api_integration,
               webhook_dispatch, notification, documentation
```

---

## SPEC-003: ScientificProductionAgent

### Purpose
Orchestrates IMRAD scientific writing pipeline with quality gates,  
SROI data integration, peer review simulation, and citation management.

### Invariants
```
INV-SCI-1: Pipeline stage order is fixed: hypothesis → literature → methodology → data → writing → peer_review
INV-SCI-2: Each stage produces an artifact and quality gate evaluation
INV-SCI-3: quality_score ∈ [0.0, 1.0] for each gate
INV-SCI-4: Citation authors and years must be valid (CitationManager.validate() = true)
INV-SCI-5: strict_gates = true → throws on gate failure (score < 0.7)
```

### Quality Gate Specifications

#### HypothesisGate (threshold: 70%)
```
Rules (weighted):
  - research_question.length > 20  (weight: 3)
  - hypothesis.length > 10          (weight: 3)
  - variables has dependent/independent (weight: 2)
  - is_falsifiable === true          (weight: 2)
  - domain.length > 0               (weight: 1)
Pass condition: weighted_score ≥ 0.70
```

#### LiteratureGate (threshold: 70%)
```
Rules (weighted):
  - references.length ≥ 5           (weight: 3)
  - gap_analysis.length > 20        (weight: 2)
  - keywords.length ≥ 3            (weight: 1)
  - all references have author+year (weight: 2)
  - theoretical_framework exists    (weight: 2)
Pass condition: weighted_score ≥ 0.70
```

#### MethodologyGate (threshold: 70%)
```
Rules (weighted):
  - research_design.length > 5      (weight: 3)
  - data_collection array non-empty (weight: 2)
  - analysis_method array non-empty (weight: 2)
  - validity or reliability defined (weight: 2)
  - ethical_considerations defined  (weight: 1)
Pass condition: weighted_score ≥ 0.70
```

#### ResultsGate (threshold: 70%)
```
Rules (weighted):
  - quantitative_data non-empty     (weight: 3)
  - sroi_data with sroi_ratio       (weight: 3)
  - research_question_addressed === true (weight: 3)
  - confidence_intervals present    (weight: 2)
  - visualizations list present     (weight: 1)
Pass condition: weighted_score ≥ 0.70
```

#### WritingGate (threshold: 70%)
```
Rules (weighted):
  - abstract.length ≥ 150          (weight: 3)
  - sections has all IMRAD parts   (weight: 3)
  - conclusion section exists       (weight: 2)
  - references.length ≥ 5          (weight: 2)
  - keywords.length ≥ 3           (weight: 1)
Pass condition: weighted_score ≥ 0.70
```

#### PeerReviewGate (threshold: 70%)
```
Rules (weighted):
  - originality_score ≥ 0.6        (weight: 3)
  - methodology_soundness ≥ 0.7    (weight: 3)
  - evidence_quality ≥ 0.65        (weight: 3)
  - writing_clarity ≥ 0.7          (weight: 2)
  - no major_revisions              (weight: 2)
Pass condition: weighted_score ≥ 0.70
```

### SROI Integration Contract
```
Input:  impact_data.sroi = { sroi_ratio: number, net_social_value: number,
                               investment: number, rating: { level: string } }
        impact_data.ecosystem = { agents: number, skills: number, mcps: number, health_score: number }

Processing:
  users_reached = ecosystem.agents * 150
  jobs_supported = floor(ecosystem.agents * 0.3)
  collaborations = floor(ecosystem.agents / 5)

Output contract for ResultsGate:
  quantitative_data MUST contain: sroi_ratio, net_social_value_brl, users_reached
  sroi_data MUST contain: sroi_ratio (not undefined)
  research_question_addressed MUST be: true
```

---

## SPEC-004: SROI Integration Contract

### SROI Calculation (Formal)
```
deadweight: type.technology → 0.15 | social_innovation → 0.20 | education → 0.10
attribution: project.attribution ∈ [0.0, 1.0], default = 0.70
displacement: project.displacement ∈ [0.0, 0.10], default = 0.05

gross_social_value = Σ(category_score * category_weight for all categories)
net_social_value = gross_social_value * (1 - deadweight) * attribution * (1 - displacement)
sroi_ratio = net_social_value / investment

Validity constraints:
  sroi_ratio MUST be: > 0 given investment > 0 and gross_social_value > 0
  net_social_value MUST be: < gross_social_value (adjustments always reduce)
  investment MUST be: > 0 (non-zero to avoid division by zero)
```

### SROI Rating Scale
```
sroi_ratio ≥ 5.0 → EXCEPCIONAL (5 stars)
sroi_ratio ≥ 3.0 → ALTO_IMPACTO (4 stars)
sroi_ratio ≥ 2.0 → SIGNIFICATIVO (3 stars)
sroi_ratio ≥ 1.0 → POSITIVO (2 stars)
sroi_ratio < 1.0 → BAIXO_IMPACTO (1 star)
```

---

## SPEC-005: QualityGate System

```
QualityGate(name: string, rules: Rule[])
  Rule = { name: string, weight: number, message: string, check: (artifact) → boolean }

evaluate(artifact) → GateResult
  GateResult = {
    gate: string,
    score: number ∈ [0, 1],
    passed: boolean (score ≥ 0.70),
    results: RuleResult[],
    summary: string
  }

Weighted scoring:
  total_weight = Σ(rule.weight for rule in rules)
  passed_weight = Σ(rule.weight for rule in rules where check(artifact) = true)
  score = passed_weight / total_weight

Invariants:
  score ∈ [0.0, 1.0]
  results.length === rules.length
  passed = (score ≥ 0.70)
  Each rule check error → result.passed = false (no uncaught exceptions)
```

---

## SPEC-006: CitationManager

```
addCitation(cite: Citation) → id: string
  Citation = { id?: string, author: string, authors?: string[],
                title: string, year: number, journal?: string,
                publisher?: string, volume?: string, pages?: string }

getFormatted(id: string, style: 'ABNT'|'APA'|'Vancouver'|'IEEE') → string
getAll(style) → string[] (alphabetically sorted by first author)
validate() → { valid: boolean, issues: string[], total: number }

Validation rules:
  year MUST be: year ≥ 1900 AND year ≤ currentYear + 1
  title MUST be: non-empty string
  author/authors MUST be: defined and non-empty
```

---

## TDD CYCLE DOCUMENTATION

### Red → Green → Refactor Log

| Cycle | Spec | Test | Status |
|-------|------|------|--------|
| 1 | SPEC-001: reason() contract | MRE-01 to MRE-04 | ✅ Green |
| 2 | SPEC-001: 6 modes registered | MRE-15 | ✅ Green |
| 3 | SPEC-001: Chain & Ensemble | MRE-08, MRE-09 | ✅ Green |
| 4 | SPEC-001: SDD preconditions | MRE-10, MRE-11 | ✅ Green |
| 5 | SPEC-002: AgentPool 128 agents | ORCH-01, ORCH-02 | ✅ Green |
| 6 | SPEC-002: Circuit breaker | ORCH-07, ORCH-08 | ✅ Green |
| 7 | SPEC-002: Priority queue | ORCH-06 | ✅ Green |
| 8 | SPEC-002: SDD contracts | ORCH-09, ORCH-10 | ✅ Green |
| 9 | SPEC-003: Quality gates | SCI-08, SCI-09 | ✅ Green |
| 10 | SPEC-003: Full pipeline | SCI-11 | ✅ Green |
| 11 | SPEC-004: SROI integration | SCI-07, INT-02 | ✅ Green |
| 12 | Integration: All components | INT-01 to INT-04 | ✅ Green |

---

## FILE STRUCTURE

```
.opencode/
├── engines/
│   ├── multi_reasoning_engine.js      # SPEC-001 implementation
│   ├── orchestration_engine.js        # SPEC-002 implementation  
│   └── scientific_production_agent.js # SPEC-003 implementation
├── tests/
│   └── run_tests.js                   # TDD test suite (46 tests)
├── specs/
│   ├── orchestration.spec.json        # Machine-readable SPEC-002
│   ├── multi_reasoning.spec.json      # Machine-readable SPEC-001
│   └── scientific_agent.spec.json     # Machine-readable SPEC-003
└── SPECIFICATIONS.md                  # This document (SDD source of truth)

.impact/
├── sroi/
│   ├── sroi_engine.json              # SROI config
│   └── scanner.js                    # SROI scanner
├── research_writer.js                # Research writer
├── run_impact_suite.js               # Suite orchestrator
├── impact_suite.py                   # Python suite
├── reports/latest_impact_report.json # Latest scan results
├── research/
│   ├── latest_research.md            # Academic paper
│   └── latest_policy_brief.md        # Policy brief
└── dashboard/index.html              # Interactive dashboard

.evolve/
├── social-impact-metrics.json        # ← SROI metrics integrated here
├── health-report.json
├── metrics-export.json
└── dashboard-metrics.json
```

---

*SDD Document | OpenCode Ecosystem | Agent: marceloclaro | v2.0.0*
