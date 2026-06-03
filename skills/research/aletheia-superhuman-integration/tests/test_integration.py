import pytest
import sys
import os

BASE = os.path.join(os.path.dirname(__file__), '..', 'scripts')
sys.path.insert(0, BASE)
sys.path.insert(0, os.path.join(BASE, '..', '..', 'aletheia-math-research', 'scripts'))


class TestSpec013PromptIntegration:
    def setup_method(self):
        from spec_013_prompt_integration import (
            AletheiaPromptLibrary, PromptSelector,
            AletheiaSessionConfig, PromptCategory, AletheiaPrompt
        )
        self.library = AletheiaPromptLibrary()
        self.AletheiaPromptLibrary = AletheiaPromptLibrary
        self.PromptSelector = PromptSelector
        self.AletheiaSessionConfig = AletheiaSessionConfig
        self.PromptCategory = PromptCategory

    def test_library_loads_builtin_prompts(self):
        self.library.load_builtin_prompts()
        prompts = self.library.list_all_prompts()
        assert isinstance(prompts, list)
        assert len(prompts) == 6
        ids = [p["id"] for p in prompts]
        assert "aletheia_gen_hypothesis_eigenweights" in ids
        assert "aletheia_ver_logical_consistency" in ids

    def test_prompt_by_category(self):
        self.library.load_builtin_prompts()
        from spec_013_prompt_integration import PromptCategory
        gen_prompts = self.library.get_prompts_by_category(
            PromptCategory.GENERATOR_HYPOTHESIS
        )
        assert isinstance(gen_prompts, list)

    def test_prompt_selector(self):
        self.library.load_builtin_prompts()
        selector = self.PromptSelector(self.library)
        gen = selector.select_generator("algebra", attempt=1)
        assert gen is not None
        assert hasattr(gen, 'id')
        ver = selector.select_verifier("number_theory", attempt=1)
        assert ver is not None

    def test_session_config_defaults(self):
        cfg = self.AletheiaSessionConfig()
        assert cfg.max_attempts == 10
        assert cfg.strictness == 0.75
        assert cfg.use_aletheia_prompts is True


class TestSpec014CoraWrapper:
    def setup_method(self):
        from spec_014_cora_wrapper import (
            CoraCheckId, CoraCheckResult, AletheiaVerifierOutput,
            EnrichedVerificationResult
        )
        self.CoraCheckId = CoraCheckId
        self.CoraCheckResult = CoraCheckResult
        self.AletheiaVerifierOutput = AletheiaVerifierOutput
        self.EnrichedVerificationResult = EnrichedVerificationResult

    def test_cora_check_enum(self):
        assert self.CoraCheckId.V1_LOGICAL_CONSISTENCY.value == "V1_LogicalConsistency"
        assert self.CoraCheckId.V7_CLARITY_AND_RIGOR.value == "V7_ClarityAndRigor"

    def test_cora_check_result_dataclass(self):
        result = self.CoraCheckResult(
            check_id=self.CoraCheckId.V1_LOGICAL_CONSISTENCY,
            passed=True, confidence=0.95, details="All steps logically connected",
            severity="minor"
        )
        assert result.passed is True
        assert result.confidence == 0.95

    def test_aletheia_verifier_output_dataclass(self):
        output = self.AletheiaVerifierOutput(
            passed=False, score=0.45,
            reasoning="Missing logical connectors",
            suggested_fixes=["Add 'therefore' between steps"],
            hallucination_detected=False
        )
        assert output.passed is False
        assert len(output.suggested_fixes) == 1


class TestSpec015ErdosEvaluator:
    def setup_method(self):
        from spec_015_erdos_evaluator import (
            ErdosProblem, ErdosProblemDifficulty,
            ErdosGradingLevel, ErdosEvaluator, SEED as ERDOS_SEED
        )
        self.ErdosProblem = ErdosProblem
        self.ErdosProblemDifficulty = ErdosProblemDifficulty
        self.ErdosGradingLevel = ErdosGradingLevel
        self.ErdosEvaluator = ErdosEvaluator
        self.ERDOS_SEED = ERDOS_SEED

    def test_erdos_problem_dataclass(self):
        problem = self.ErdosProblem(
            erdos_id="Erdos-1051",
            statement="Let A be a set of n positive integers...",
            domain="combinatorics",
            difficulty=self.ErdosProblemDifficulty.RESEARCH_OPEN,
            source_year=1973
        )
        assert problem.erdos_id == "Erdos-1051"
        assert problem.difficulty == self.ErdosProblemDifficulty.RESEARCH_OPEN

    def test_erdos_evaluator_initialization(self):
        evaluator = self.ErdosEvaluator()
        assert hasattr(evaluator, 'dataset')
        assert hasattr(evaluator, 'results')
        assert hasattr(evaluator, 'grader')

    def test_seed_reproducibility(self):
        assert self.ERDOS_SEED == 42


class TestSpec016ScalingLaw:
    def setup_method(self):
        from spec_016_scaling_law import (
            ComputeBudget, DifficultyProfile, SEED as SCALING_SEED
        )
        self.ComputeBudget = ComputeBudget
        self.DifficultyProfile = DifficultyProfile
        self.SCALING_SEED = SCALING_SEED

    def test_compute_budget_enum(self):
        assert self.ComputeBudget.MINIMAL.value == 0.1
        assert self.ComputeBudget.EXHAUSTIVE.value == 5.0
        assert self.ComputeBudget.NORMAL.value == 1.0

    def test_difficulty_profile_budget(self):
        profile = self.DifficultyProfile(
            problem_id="test-1", domain="number_theory",
            difficulty_level="olympiad", estimated_depth=7
        )
        assert profile.required_budget() == self.ComputeBudget.DEEP

    def test_seed(self):
        assert self.SCALING_SEED == 42
