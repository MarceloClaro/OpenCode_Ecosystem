# Contributing to Aletheia-Superhuman Validation

Thank you for your interest in contributing! This project aims to advance formal reasoning and scientific validation in the OpenCode ecosystem.

## Code of Conduct

Be respectful, collaborative, and scientifically rigorous.

## Getting Started

### Prerequisites
- Python 3.11+
- Lean 4 (elan 4.2.2)
- Git & GitHub

### Setup Development Environment
```bash
git clone https://github.com/[USER]/aletheia-superhuman-validation.git
cd aletheia-superhuman-validation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Running Tests
```bash
# Verify reproducibility (sample)
cd reproducibility
python verify_reproducibility.py --seed 42 --sample 50

# Full batch (if you have Lean 4 installed)
cd ../scripts
python spec_batch_processor.py --batch "phase2_validation_full" --size "large" --lean-check
```

## How to Contribute

### 1. Report Issues
- **Bug Reports**: Use [GitHub Issues](https://github.com/[USER]/aletheia-superhuman-validation/issues)
- **Include**: Error messages, reproduction steps, environment snapshot
- **Label**: `bug`, `critical` (if blocking), `question`

### 2. Suggest Improvements
- **Discussions**: Use [GitHub Discussions](https://github.com/[USER]/aletheia-superhuman-validation/discussions)
- **Propose**: New reasoning types, optimizations, new problem domains
- **Reference**: Relevant papers, benchmarks, or metrics

### 3. Submit Pull Requests

#### Branch Naming (Conventional Commits v1.0.0)
```
feature/[feature-name]     # New features (SPEC-017, new reasoner, etc)
fix/[bug-name]             # Bug fixes
docs/[doc-name]            # Documentation only
refactor/[component]       # Code refactoring
perf/[optimization]        # Performance improvements
test/[test-coverage]       # Test additions
```

Example: `feature/spec-017-proof-search`, `fix/lean4-windows-path`

#### Commit Message Format
```
type(scope): subject line (50 chars max)

Body paragraph (wrapped at 72 chars):
Explain the *what* and *why*, not *how*.

- Bullet point 1
- Bullet point 2

Closes #123 (if applicable)
```

Example:
```
feat(spec-014): add timeout handling for Lean subprocess

Add 30-second timeout for subprocess calls to Lean.exe.
Prevents hanging on malformed proof states.

- Add timeout parameter to run_spec_014_lean()
- Log timeout events with problem metadata
- Skip failed problems (don't hard-fail)

Closes #42
```

#### Pull Request Checklist
- [ ] Branch is up-to-date with `main`
- [ ] Code follows Python style (PEP 8, type hints)
- [ ] Tests pass: `python verify_reproducibility.py --seed 42 --sample 50`
- [ ] Documentation updated if applicable
- [ ] Commit messages follow Conventional Commits v1.0.0
- [ ] No hardcoded paths (use `os.path.expanduser()`, `Path`)
- [ ] Windows compatibility tested (or noted as known issue)

### 4. Add New SPEC Modules

If proposing SPEC-017, SPEC-018, etc:

1. **Create spec_017.py** in `scripts/`
   ```python
   from spec_base import SpecModuleBase, SpecModuleResult
   
   class Spec017:
       """Brief description of SPEC-017."""
       
       def process(self, problem: dict) -> SpecModuleResult:
           # Implementation
           return SpecModuleResult(
               module_name="spec_017",
               status="COMPLETED",
               success=True,
               output="Result description",
               error=None,
               time_ms=elapsed_time
           )
   ```

2. **Add tests** in `tests/test_spec_017.py`
   ```python
   import unittest
   from spec_017 import Spec017
   
   class TestSpec017(unittest.TestCase):
       def test_basic_functionality(self):
           spec = Spec017()
           result = spec.process({...})
           self.assertTrue(result.success)
   ```

3. **Update `spec_batch_processor.py`** to integrate
   ```python
   from spec_017 import Spec017
   
   # In SpecModule.process():
   spec_017_result = Spec017().process(problem)
   results['spec_017_result'] = spec_017_result.to_dict()
   ```

4. **Document in ADR-007** (new architecture decision)

### 5. Add New Problem Domains

If extending beyond Erdős problems:

1. **Create new dataset** in `data/` (e.g., `data/topology_100.json`)
2. **Add metadata schema** (erdos_number → domain-specific identifier)
3. **Test on sample** (10-20 problems) first
4. **Document domain specifics** in new ADR
5. **Report metrics** in new report file

Example structure:
```json
{
  "problems": [
    {
      "identifier": "topology_001",
      "domain": "topology",
      "statement": "Prove that ...",
      "difficulty": "medium",
      "prize": "$1000"
    }
  ]
}
```

## Development Practices

### Code Style
- Follow **PEP 8** (max line length: 100 chars)
- Use **type hints** (Python 3.10+ feature)
- Add **docstrings** (Google style)

Example:
```python
def process_problem(problem: dict, timeout_sec: int = 30) -> SpecModuleResult:
    """Process a single Lean problem through SPEC pipeline.
    
    Args:
        problem: Problem dict with 'filename', 'statement', 'proof_sketch'
        timeout_sec: Max seconds before subprocess kill
    
    Returns:
        SpecModuleResult with success status and timing info
    
    Raises:
        TimeoutError: If Lean subprocess exceeds timeout_sec
    """
```

### Testing
- Write **unit tests** for new functions
- Test **Windows + Linux paths** (use `Path`)
- Add **determinism tests** (same seed = same result)
- Run full batch before submitting PR

### Reproducibility
- **All randomness must use seed=42** or configurable seed
- **Document hyperparameters** in docstring + config
- **No hardcoded paths** — use `os.path.expanduser()` or `Path`
- **Log every subprocess call** with command + environment

## Review Process

1. **Automated Checks** (GitHub Actions)
   - ✅ Python formatting (black, ruff)
   - ✅ Type checking (mypy)
   - ✅ Unit tests
   - ✅ Reproducibility sample (50 problems)

2. **Code Review** (Maintainers)
   - Scientific soundness
   - Performance impact
   - Documentation completeness
   - Backward compatibility

3. **Approval & Merge**
   - 1 approval required
   - CI/CD green
   - Squash-merge to main with conventional commit

## Release Process

### For Maintainers

1. **Update version** in `setup.py`, `__init__.py`
2. **Write CHANGELOG.md** entry
3. **Create release branch**: `release/v1.1.0`
4. **Merge to main** with PR
5. **Create GitHub Release** with release notes
6. **Tag**: `git tag -a v1.1.0 -m "Release v1.1.0"`
7. **Push**: `git push origin v1.1.0`

## Questions?

- **Bug?** → [Issues](https://github.com/[USER]/aletheia-superhuman-validation/issues)
- **Idea?** → [Discussions](https://github.com/[USER]/aletheia-superhuman-validation/discussions)
- **Question?** → [Discussions > Q&A](https://github.com/[USER]/aletheia-superhuman-validation/discussions)

---

**Thank you for helping advance formal reasoning in OpenCode!** 🎓
