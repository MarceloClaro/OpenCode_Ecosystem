# SPEC_RES_aletheia — Aletheia Math Research Engine

## API Contract

### Module: `aletheia_engine.py`

```python
class AletheiaEngine:
    def __init__(self, max_attempts: int = 10, strictness: float = 0.7,
                 verbose: bool = False)
    def solve(self, problem: MathProblem) -> AletheiaSession
    def get_metrics(self) -> dict

class Generator:
    def generate(self, problem: MathProblem,
                 previous_feedback: Optional[str] = None,
                 attempt_number: int = 1) -> SolutionAttempt

class Verifier:
    def __init__(self, strictness: float = 0.7, verbose: bool = False)
    def verify(self, problem: MathProblem,
               attempt: SolutionAttempt) -> VerificationResult

class Reviser:
    def revise(self, problem: MathProblem,
               attempt: SolutionAttempt,
               verification: VerificationResult) -> str

@dataclass
class MathProblem:
    id: str; statement: str; domain: str; difficulty: str
    known_answer: Optional[str] = None; source: str = ""

@dataclass
class SolutionAttempt:
    attempt_id: int; phase: Phase; content: str
    reasoning_types_used: list[str]; confidence: float

@dataclass
class VerificationResult:
    solution_id: int; passed: bool; score: float
    flaws: list[str]; hallucination_detected: bool
    cora_checks: dict[str, bool]; suggestion: str = ""
    autonomy_level: AutonomyLevel = ...
```

### Module: `aletheia_enhanced.py`

```python
class EnhancedAletheiaEngine(AletheiaEngine):
    def __init__(self, max_attempts=10, strictness=0.7, verbose=False)
    def solve(self, problem: MathProblem) -> AletheiaSession
    # + self.refiner: RefinementTracker

class EnhancedVerifier(Verifier):
    # 7 base checks (V1-V7) + 5 semantic checks (V8-V12)
    def verify(self, problem, attempt) -> VerificationResult

class EnhancedGenerator(Generator):
    # Domain-specific solution generation (gcd, induction, modular)

def detect_subdomain(problem: MathProblem) -> ProblemSubDomain
```

---

## CT-001: Generator produces SolutionAttempt (Structural)
**Entrada**: `Generator().generate(MathProblem(...), attempt_number=1)`
**Esperado**: `isinstance(SolutionAttempt)`, `len(content) > 50`, `len(reasoning_types_used) > 0`, `0.0 <= confidence <= 1.0`

## CT-002: Verifier runs all 7 Cora checks (Completeness)
**Entrada**: `Verifier(strictness=0.5).verify(problem, attempt)`
**Esperado**: `len(cora_checks) == 7` com chaves V1_LogicalConsistency a V7_ClarityAndRigor, `0.0 <= score <= 1.0`

## CT-003: Pipeline solve cycle (Integration)
**Entrada**: `AletheiaEngine(max_attempts=3, strictness=0.6).solve(problem)`
**Esperado**: `session.status in ("solved", "failed")`, `len(attempts) > 0`, `metrics["solve_rate"]` definido

## CT-004: Enhanced Verifier adds V8-V12 (Extension)
**Entrada**: `EnhancedVerifier(strictness=0.7).verify(problem, attempt)`
**Esperado**: `len(cora_checks) == 12` (V1-V7 + V8-V12), `detect_subdomain(gcd_problem) == GCD_EUCLIDEAN`
