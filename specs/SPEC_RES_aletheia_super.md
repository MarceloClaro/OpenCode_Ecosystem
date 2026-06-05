# SPEC_RES_aletheia_super — Aletheia Superhuman Integration

## API Contract

### Module: `spec_013_prompt_integration.py`

```python
class AletheiaPromptLibrary:
    def load_builtin_prompts(self)
    def list_all_prompts(self) -> list[dict]
    def get_prompt_by_id(self, prompt_id: str) -> AletheiaPrompt
    def get_prompts_by_category(self, category: PromptCategory) -> list[AletheiaPrompt]
    def export_as_yaml(self) -> str

class PromptSelector:
    def __init__(self, library: AletheiaPromptLibrary)
    def select_generator(self, domain: str, attempt: int) -> AletheiaPrompt
    def select_verifier(self, domain: str, attempt: int) -> AletheiaPrompt

@dataclass
class AletheiaSessionConfig:
    use_aletheia_prompts: bool = True
    max_attempts: int = 10
    strictness: float = 0.75
```

### Module: `spec_014_cora_wrapper.py`

```python
class CoraCheckId(Enum):
    V1_LOGICAL_CONSISTENCY to V7_CLARITY_AND_RIGOR

@dataclass
class CoraCheckResult:
    check_id: CoraCheckId; passed: bool
    confidence: float; details: str; severity: str

@dataclass
class AletheiaVerifierOutput:
    passed: bool; score: float; reasoning: str
    suggested_fixes: list[str]; hallucination_detected: bool
```

### Module: `spec_015_erdos_evaluator.py`

```python
class ErdosProblemDifficulty(Enum):
    OLYMPIAD / PHD_EXERCISE / RESEARCH_OPEN

class ErdosGradingLevel(Enum):
    NO_SOLUTION / TECHNICALLY_INCORRECT / TECHNICALLY_CORRECT
    / MEANINGFULLY_CORRECT / NOVEL_CONTRIBUTION

class ErdosEvaluator:
    def __init__(self)
    # problems: list, results: dict
```

### Module: `spec_016_scaling_law.py`

```python
class ComputeBudget(Enum):
    MINIMAL=0.1, EFFICIENT=0.5, NORMAL=1.0, DEEP=2.0, EXHAUSTIVE=5.0

@dataclass
class DifficultyProfile:
    problem_id: str; domain: str; difficulty_level: str
    estimated_depth: int
    def required_budget(self) -> ComputeBudget
```

---

## CT-001: SPEC-013 — Prompt Library loads 6 prompts (Integration)
**Entrada**: `library.load_builtin_prompts()` → `list_all_prompts()`
**Esperado**: 6 prompts carregados, IDs incluem `aletheia_gen_hypothesis_eigenweights` e `aletheia_ver_logical_consistency`

## CT-002: SPEC-014 — CoraCheckId + AletheiaVerifierOutput (Structural)
**Entrada**: `CoraCheckId.V1_LOGICAL_CONSISTENCY.value`
**Esperado**: `"V1_LogicalConsistency"`; `AletheiaVerifierOutput(passed=False, ...)` com `suggested_fixes` populado

## CT-003: SPEC-015 — ErdosProblem + ErdosEvaluator (Structural)
**Entrada**: `ErdosProblem(erdos_id="Erdos-1051", difficulty=RESEARCH_OPEN)` + `ErdosEvaluator()`
**Esperado**: `.erdos_id` == string; evaluator tem `.problems` e `.results`; `SEED == 42`

## CT-004: SPEC-016 — ComputeBudget + DifficultyProfile (Mapping)
**Entrada**: `DifficultyProfile(estimated_depth=7).required_budget()`
**Esperado**: `ComputeBudget.DEEP`; `ComputeBudget.MINIMAL.value == 0.1`
