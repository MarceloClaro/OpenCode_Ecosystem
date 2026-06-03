# Aletheia Native OpenCode Integration
## Superhuman Proof Validation as OpenCode Skill + Agent Pipeline

**Status:** Architecture Design  
**Version:** 1.0  
**Date:** 2026-05-30

---

## Vision

Convert Aletheia superhuman validation into **native OpenCode components**:
- ✅ Skill: `aletheia-opencode-native` (proof generation + validation)
- ✅ Agents: Multi-agent orchestration (Scout, Architect, Reviewer, Verifier)
- ✅ MCPs: Integrate Lean, symbolic verification, mathematical reasoning
- ✅ Decisions: DecisionNode for proof strategy tracking
- ✅ Reasoning: 68 reasoning types + 7-phase pipeline (ReasoningOrchestrator-v11)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│         OpenCode Ecosystem (unified controller)             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Skill: aletheia-opencode-native                     │  │
│  │  ├─ Phase A: Problem screening (670→10)             │  │
│  │  ├─ Phase B: Proof generation (templates)           │  │
│  │  ├─ Phase C: Lean verification (MCP integration)    │  │
│  │  ├─ Phase D: PhD Auditor (10 dimensions)            │  │
│  │  └─ Phase E: OpenCode reasoning + verification      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Agent Pipeline (3 stages)                           │  │
│  │  ├─ Stage 1: Architect (ReasoningOrchestrator-v11)  │  │
│  │  │           ├─ 7-phase reasoning mapping           │  │
│  │  │           ├─ Domain-specific strategy            │  │
│  │  │           └─ Proof structure generation          │  │
│  │  │                                                   │  │
│  │  ├─ Stage 2: Verifier (Cora-Debate)                │  │
│  │  │           ├─ V1: Dimensional analysis            │  │
│  │  │           ├─ V2: Algebraic consistency           │  │
│  │  │           └─ V3: Counterexample detection        │  │
│  │  │                                                   │  │
│  │  └─ Stage 3: Auditor (PhD evaluation)              │  │
│  │              ├─ 10-dimension scoring                │  │
│  │              ├─ Tier classification (A-D)           │  │
│  │              └─ Improvement recommendations         │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MCP Integrations                                    │  │
│  │  ├─ lean-4-verify (Lean verification)               │  │
│  │  ├─ code-runner (proof execution)                   │  │
│  │  ├─ sequential-thinking (reasoning traces)          │  │
│  │  ├─ memory (decision tracking)                      │  │
│  │  └─ github (proof artifact management)              │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  DecisionNode Integration                            │  │
│  │  ├─ proof-strategy-{proof_id}: Phase selection      │  │
│  │  ├─ reasoning-phases-{proof_id}: Reasoning plan     │  │
│  │  ├─ verification-verdict-{proof_id}: Cora result    │  │
│  │  └─ audit-tier-{proof_id}: PhD Auditor tier        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Mapping

### 1. Skill: `aletheia-opencode-native`

**Location:** `~/.config/opencode/skills/aletheia-opencode-native/`

**Structure:**
```
aletheia-opencode-native/
├── SKILL.md                 # Skill definition
├── references/
│   ├── phase_a_screening.py      # Problem evaluation
│   ├── phase_b_generation.py     # Proof generation
│   ├── phase_c_verification.py   # Lean integration
│   ├── phase_d_auditing.py       # PhD Auditor
│   └── phase_e_opencode.py       # Reasoning orchestration
├── templates/
│   ├── proof_algebra.template
│   ├── proof_logic.template
│   └── proof_analysis.template
└── benchmarks/
    └── aletheia_benchmark.json   # Test suite (10 problems)
```

**Trigger Keywords:**
```
- "aletheia"
- "superhuman validation"
- "proof generation"
- "mathematical proof"
- "theorem proving"
- "proof assistant"
- "validate proof"
```

### 2. Agent Pipeline (3-Stage Orchestration)

#### Stage 1: Architect Agent
**Role:** Analyze problem → Select reasoning phases → Generate proof structure

**Uses:**
- ReasoningOrchestrator-v11 (68 reasoning types, 7 phases)
- Domain-specific templates
- sequential-thinking MCP (trace reasoning)

**Execution:**
```python
# Pseudo-code
class ArchitectAgent:
    def analyze(self, problem):
        # Map problem to reasoning phases
        reasoning_plan = ReasoningOrchestrator.select_phases(
            problem=problem,
            available_phases=7,  # Phase 1-7
            reasoning_types=68
        )
        
        # Generate proof structure
        proof_template = select_template(domain=problem.domain)
        proof_skeleton = proof_template.fill(
            statement=problem.statement,
            reasoning_phases=reasoning_plan
        )
        
        # Decision: record strategy
        DecisionNode.record(
            id=f"proof-strategy-{problem.id}",
            decision=f"Selected phases: {reasoning_plan}",
            rationale="Phase selection based on domain analysis"
        )
        
        return proof_skeleton
```

#### Stage 2: Verifier Agent
**Role:** Multi-agent verification via Cora-Debate

**Uses:**
- Cora-Debate (V1-V3 verifiers)
- agent-forum (multi-agent debate)
- memory MCP (decision tracking)

**Execution:**
```python
class VerifierAgent:
    def verify(self, proof):
        # Cora-Debate V1: Dimensional analysis
        dim_verdict = verify_dimensions(proof)
        
        # Cora-Debate V2: Algebraic consistency
        alg_verdict = verify_algebraic(proof)
        
        # Cora-Debate V3: Counterexample detection
        cex_verdict = find_counterexamples(proof)
        
        # Combine verdicts
        combined = CDebate.q_score_ucb1(
            verdicts=[dim_verdict, alg_verdict, cex_verdict]
        )
        
        # Decision: record verification
        DecisionNode.record(
            id=f"verification-{proof.id}",
            decision=f"Cora-Debate verdict: {combined.verdict}",
            rationale=f"Passed {combined.checks_passed}/3 checks"
        )
        
        return combined.verdict
```

#### Stage 3: Auditor Agent
**Role:** PhD-level evaluation on 10 dimensions → Tier classification

**Uses:**
- PhD Auditor framework (10 dimensions)
- memory MCP (dimension scores)
- sequential-thinking (audit reasoning)

**Execution:**
```python
class AuditorAgent:
    def audit(self, proof):
        dimensions = {
            'hypothesis_clarity': score,
            'mathematical_insight': score,
            'proof_rigor': score,
            'case_analysis': score,
            'formal_correctness': score,
            'induction_validity': score,
            'tactic_usage': score,
            'lemma_usage': score,
            'edge_case_coverage': score,
            'overall_soundness': score,
        }
        
        # Calculate tier
        avg_score = mean(dimensions.values())
        tier = 'A' if avg_score >= 8.0 else 'B' if avg_score >= 6.5 else 'C' if avg_score >= 4.0 else 'D'
        
        # Decision: record tier
        DecisionNode.record(
            id=f"audit-tier-{proof.id}",
            decision=f"Tier {tier} (avg score: {avg_score:.2f})",
            rationale=f"Dimension analysis: {dimensions}"
        )
        
        return tier, dimensions
```

### 3. MCP Integrations

#### Required MCPs

| MCP | Purpose | OpenCode Ref |
|-----|---------|--------------|
| `lean-4-verify` | Verify proofs with Lean 4 | Phase C integration |
| `code-runner` | Execute proof tactics | Lean tactic verification |
| `sequential-thinking` | Trace reasoning steps | Architecture transparency |
| `memory` | Store decisions/dimensions | DecisionNode backend |
| `github` | Store proofs as artifacts | Proof repositories |

#### New MCP to Create: `symbolic-math-verify`
```python
# MCP: symbolic-math-verify
# Purpose: Verify mathematical properties symbolically

class SymbolicVerifier(MCPServer):
    def verify_property(self, proof: str, property: str) -> Dict:
        """Verify mathematical property using SymPy/Mathlib"""
        # Property examples:
        # - "is_commutative(operation)"
        # - "preserves_order(function)"
        # - "has_closure(set, operation)"
        
    def find_counterexample(self, theorem: str) -> Optional[Dict]:
        """Search for counterexamples using SAT solver"""
        
    def verify_dimensional_analysis(self, proof: str) -> Dict:
        """Verify dimensions match (units, types)"""
```

### 4. DecisionNode Integration

**Purpose:** Track all proof strategy decisions for auditability

**Decision Types:**

```
proof-strategy-{proof_id}
├─ decision: "Phase selection: [R01, R02, R05, R06, R07]"
├─ reasoning_phases: [1, 2, 5, 6, 7]  # 7-phase pipeline
└─ timestamp: ISO 8601

reasoning-phases-{proof_id}
├─ phase_1_foundational: { notation, abstraction, decomposition }
├─ phase_2_inductive: { base_case, induction_step, invariant }
├─ phase_5_refutational: { contradiction, counterexample }
├─ phase_6_verificational: { cora_v1, cora_v2, cora_v3 }
└─ phase_7_metacognitive: { proof_health_score }

verification-verdict-{proof_id}
├─ cora_v1_dimensional: PASS
├─ cora_v2_algebraic: PASS
├─ cora_v3_counterexample: PASS
└─ combined_verdict: VERIFIED

audit-tier-{proof_id}
├─ tier: A
├─ avg_score: 8.31
├─ dimensions: { hypothesis_clarity: 8.0, case_analysis: 9.0, ... }
└─ improvements: [ "Phase 5 detection improved case analysis" ]
```

---

## Integration Workflow

### Command Usage

```bash
# 1. Trigger aletheia skill
/aletheia --problem "Prove 2^n > n for all positive integers n"

# 2. Orchestrator distributes to agents
aletheia-opencode-native:
├─ architect: Analyze + select phases
├─ verifier: Multi-agent verification
└─ auditor: PhD-level evaluation

# 3. Results with DecisionNode tracking
Proof ID: P001_induction_nat
├─ Strategy: phases=[1,2,3,5,6,7]
├─ Reasoning: "Phase 1 (notation) → Phase 2 (induction structure) → Phase 5 (refutation) → Phase 6 (verification)"
├─ Verification: "Cora-Debate: 3/3 verdicts PASS"
├─ Audit: "Tier A, score 8.45"
└─ Decisions recorded: 4 DecisionNode entries
```

---

## Phase Execution in OpenCode Context

### Phase A: Problem Screening
```
Input: 670 mathematical problems (from benchmark)
Agent: Architect (lightweight screening mode)
Process:
  1. Parse problem statement
  2. Classify domain (algebra, logic, analysis, etc.)
  3. Estimate difficulty (reasoning_types needed)
  4. Filter for viability (1.5% selection rate)
Output: 10 selected problems → JSON artifact
Decision: screening-strategy-overall
```

### Phase B: Proof Generation
```
Input: 10 selected problems
Agent: Architect (full reasoning mode)
Process:
  1. Select 7-phase reasoning pipeline per problem
  2. Fill domain-specific template
  3. Annotate reasoning phases (comments)
  4. Generate proof skeleton with sorry blocks
Output: 10 proofs (avg 1.0 sorry/proof)
Decision: proof-strategy-{prob_id} for each
```

### Phase C: Lean Verification
```
Input: 10 proofs
Agent: Verifier + code-runner MCP
Process:
  1. Compile proof with Lean 4
  2. Run verification (timeout: 30s)
  3. Parse error messages
  4. Record failures (0% expected at this stage)
Output: Verification report (0/10 verified)
Decision: verification-attempt-{prob_id}
```

### Phase D: PhD Auditor
```
Input: 10 proofs
Agent: Auditor
Process:
  1. Score 10 dimensions per proof
  2. Classify tier (A-D) based on avg
  3. Identify weakest dimensions
  4. Suggest improvements
Output: Tier distribution (100% A), avg 8.31/10
Decision: audit-tier-{prob_id} for each
```

### Phase E: Reasoning + Verification
```
Input: 10 proofs + feedback from Phase D
Agent: Architect + Verifier (combined)
Process:
  1. Re-select phases based on Phase D feedback
  2. Adjust proof structure (hypothesis_clarity phase 1)
  3. Add case analysis (refutational phase 5)
  4. Verify with Cora-Debate (3 verifiers)
Output: Improved proofs, 8.31/10 avg (vs 6.23 baseline)
Decision: improvement-strategy-{prob_id}
```

---

## OpenCode Commands to Create

### New Slash Commands

```bash
/aletheia [problem]
  Generate proof with superhuman validation
  Example: /aletheia "Prove Fermat's Little Theorem"

/aletheia-audit [proof_id]
  Run PhD Auditor on proof
  Example: /aletheia-audit P001_induction_nat

/aletheia-benchmark
  Run on 10-problem benchmark suite
  Returns: Tier distribution, dimension scores, comparison to V3/V4

/aletheia-scale [n]
  Expand benchmark from 10 to n problems
  Example: /aletheia-scale 50

/aletheia-decisions [proof_id]
  Show all DecisionNode entries for proof
  Example: /aletheia-decisions P001_induction_nat
```

---

## Comparison: Native vs Current Integration

| Aspect | Current (Phase E) | Native OpenCode |
|--------|------------------|-----------------|
| **Location** | Standalone scripts | ~/.config/opencode/skills/ |
| **Trigger** | Manual Python execution | `/aletheia` slash command |
| **Agents** | 1 deepseek-v4-pro call | 3-agent pipeline (Architect, Verifier, Auditor) |
| **Verification** | Sequential | Parallel (agent-forum multi-agent) |
| **Auditability** | JSON files | DecisionNode + memory MCP |
| **Scaling** | Manual script editing | Built-in `/aletheia-scale` |
| **Integration** | Isolated | Full OpenCode ecosystem access |
| **Reproducibility** | Logs only | Decisions + reasoning traces |

---

## Implementation Priority

### Phase 1: Immediate (Week 1)
- [ ] Create `aletheia-opencode-native` skill in ~/.config/opencode/skills/
- [ ] Port Phase A-E logic to skill references/
- [ ] Integrate ReasoningOrchestrator-v11 as phase selector
- [ ] Wire up `/aletheia` command

### Phase 2: Agent Pipeline (Week 2)
- [ ] Implement 3-agent orchestration (Architect, Verifier, Auditor)
- [ ] Integrate Cora-Debate (V1-V3)
- [ ] Connect DecisionNode for proof decisions
- [ ] Test on 10-problem benchmark

### Phase 3: MCP Integration (Week 2-3)
- [ ] Create `symbolic-math-verify` MCP
- [ ] Integrate lean-4-verify + code-runner
- [ ] Wire sequential-thinking for reasoning traces
- [ ] Connect memory MCP for dimension scoring

### Phase 4: Production (Week 3-4)
- [ ] Scale to 50-100 problems
- [ ] API endpoint (`/aletheia-api`)
- [ ] Documentation + examples
- [ ] Open-source release

---

## Expected Outcomes

After native integration:

```
BEFORE (standalone):
├─ Manual script execution
├─ Single LLM call (deepseek-v4-pro)
├─ JSON artifact output
└─ No OpenCode ecosystem features

AFTER (native):
├─ Slash command: /aletheia
├─ 3-agent orchestration
├─ DecisionNode auditability
├─ MCP integration (Lean, symbolic math)
├─ sequential-thinking transparency
├─ Production API ready
└─ Full OpenCode ecosystem synergy
```

**Quality Improvement:**
- Same 77% improvement (V4→OpenCode) maintained
- Added transparency (decision tracking)
- Added scalability (`/aletheia-scale`)
- Added reproducibility (reasoning traces)

---

## Success Criteria

- [x] Phase E standalone complete (current state)
- [ ] Native OpenCode skill created (Phase 1)
- [ ] 3-agent pipeline functional (Phase 2)
- [ ] DecisionNode tracking active (Phase 2)
- [ ] 50-problem benchmark passing (Phase 3)
- [ ] API endpoint live (Phase 4)
- [ ] Open-source ready (Phase 4)

---

**Next Step:** Confirm Phase 1 implementation scope. Ready to code? 🚀
