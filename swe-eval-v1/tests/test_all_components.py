"""
TDD Suite -- SWE-EVAL v1.0 (Corrigido para Windows: locks SQLite + ajustes de threshold)
"""

import json
import os
import sys
import shutil
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


def safe_tempdir():
    """Fixture manual: cria tempdir e garante limpeza com retry no Windows."""
    tmp = tempfile.mkdtemp()
    yield tmp
    try:
        shutil.rmtree(tmp, ignore_errors=True)
    except Exception:
        pass


# ============================================================
# L2+L7: Registry v2.0 + Supply Chain Security
# ============================================================

class TestRegistryV2:
    def test_create_registry(self):
        from supply_chain.registry_v2 import RegistryV2
        for tmp in safe_tempdir():
            db_path = str(Path(tmp) / "test.db")
            reg = RegistryV2(db_path)
            assert reg is not None
            assert Path(db_path).exists()

    def test_register_and_retrieve_skill(self):
        from supply_chain.registry_v2 import RegistryV2
        for tmp in safe_tempdir():
            skill_dir = Path(tmp) / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Test Skill\n\nDescription here.", encoding="utf-8")

            db_path = str(Path(tmp) / "test.db")
            reg = RegistryV2(db_path)
            manifest = reg.register_skill(str(skill_dir))
            assert manifest is not None
            assert manifest.name == "test-skill"

            retrieved = reg.get_manifest("test-skill")
            assert retrieved is not None
            assert retrieved.name == "test-skill"

    def test_integrity_verification(self):
        from supply_chain.registry_v2 import RegistryV2
        for tmp in safe_tempdir():
            skill_dir = Path(tmp) / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Test Skill", encoding="utf-8")

            db_path = str(Path(tmp) / "test.db")
            reg = RegistryV2(db_path)
            reg.register_skill(str(skill_dir))
            assert reg.verify_integrity("test-skill")

            (skill_dir / "SKILL.md").write_text("# Modified Skill", encoding="utf-8")
            assert not reg.verify_integrity("test-skill")

    def test_list_all_skills(self):
        from supply_chain.registry_v2 import RegistryV2
        for tmp in safe_tempdir():
            for name in ["skill-a", "skill-b", "skill-c"]:
                d = Path(tmp) / name
                d.mkdir()
                (d / "SKILL.md").write_text(f"# {name}", encoding="utf-8")

            db_path = str(Path(tmp) / "test.db")
            reg = RegistryV2(db_path)
            for name in ["skill-a", "skill-b", "skill-c"]:
                reg.register_skill(str(Path(tmp) / name))

            skills = reg.list_all()
            assert len(skills) == 3

    def test_check_updates_detects_changes(self):
        from supply_chain.registry_v2 import RegistryV2
        for tmp in safe_tempdir():
            skill_dir = Path(tmp) / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Original", encoding="utf-8")

            db_path = str(Path(tmp) / "test.db")
            reg = RegistryV2(db_path)
            reg.register_skill(str(skill_dir))

            (skill_dir / "SKILL.md").write_text("# Modified", encoding="utf-8")
            stale = reg.check_updates()
            assert len(stale) == 1
            assert stale[0]["action"] == "requires_resign"

    def test_audit_trail(self):
        from supply_chain.registry_v2 import RegistryV2
        for tmp in safe_tempdir():
            skill_dir = Path(tmp) / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Test", encoding="utf-8")

            db_path = str(Path(tmp) / "test.db")
            reg = RegistryV2(db_path)
            reg.register_skill(str(skill_dir))

            trail = reg.get_audit_trail("test-skill")
            assert len(trail) >= 1
            assert trail[0]["event_type"] == "REGISTER"


class TestSecureLoader:
    def test_load_without_manifest_dev_mode(self):
        from supply_chain.secure_loader import SecureLoader, LoadMode
        from supply_chain.registry_v2 import RegistryV2
        for tmp in safe_tempdir():
            skill_dir = Path(tmp) / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Test", encoding="utf-8")

            db_path = str(Path(tmp) / "test.db")
            reg = RegistryV2(db_path)
            loader = SecureLoader(reg, mode=LoadMode.DEV)

            report = loader.load_skill(str(skill_dir))
            assert not report.blocked

    def test_load_without_manifest_secure_mode_blocks(self):
        from supply_chain.secure_loader import SecureLoader, LoadMode
        from supply_chain.registry_v2 import RegistryV2
        for tmp in safe_tempdir():
            skill_dir = Path(tmp) / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Test", encoding="utf-8")

            db_path = str(Path(tmp) / "test.db")
            reg = RegistryV2(db_path)
            loader = SecureLoader(reg, mode=LoadMode.SECURE)

            report = loader.load_skill(str(skill_dir))
            assert report.blocked

    def test_load_with_manifest_passes(self):
        from supply_chain.secure_loader import SecureLoader, LoadMode
        from supply_chain.registry_v2 import RegistryV2
        for tmp in safe_tempdir():
            skill_dir = Path(tmp) / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Test Skill\n\nDescription.", encoding="utf-8")

            db_path = str(Path(tmp) / "test.db")
            reg = RegistryV2(db_path)
            manifest = reg.register_skill(str(skill_dir))

            loader = SecureLoader(reg, mode=LoadMode.SECURE)
            report = loader.load_skill(str(skill_dir))
            assert not report.blocked
            assert report.result.value == "ok"


# ============================================================
# L6: Permission Tiers + Audit Log
# ============================================================

class TestPermissionGate:
    def test_observer_cannot_execute_destructive(self):
        from permission_tiers.permission_gate import PermissionGate, PermissionTier
        gate = PermissionGate(interactive=False)
        result = gate.check_command("rm -rf /tmp/test", "test-agent", PermissionTier.OBSERVER)
        assert not result["allowed"]

    def test_safe_command_allowed(self):
        from permission_tiers.permission_gate import PermissionGate, PermissionTier
        gate = PermissionGate(interactive=False)
        result = gate.check_command("pytest tests/", "test-agent", PermissionTier.CONTRIBUTOR)
        assert result["allowed"]


class TestAuditLogger:
    def test_log_and_retrieve(self):
        from permission_tiers.permission_gate import AuditLogger
        for tmp in safe_tempdir():
            db_path = str(Path(tmp) / "audit.db")
            logger = AuditLogger(db_path)
            logger.log("test-agent", 2, "rm -rf /tmp",
                      "Remocao recursiva", True, True, "APPROVED",
                      "session-001", human_approved=True)

            stats = logger.get_stats("session-001")
            assert stats["total_commands"] == 1
            assert stats["human_approved"] == 1


# ============================================================
# L3: SpecDriftDetector
# ============================================================

class TestContractExtractor:
    def test_extract_endpoints(self):
        from spec_drift.drift_detector import ContractExtractor
        for tmp in safe_tempdir():
            spec_path = Path(tmp) / "spec.md"
            spec_path.write_text("""
# API Spec
O endpoint GET /users retorna lista de usuarios.
O campo "id" e "name" devem estar presentes.
O endpoint POST /users cria um novo usuario.
""", encoding="utf-8")
            extractor = ContractExtractor()
            contracts = extractor.extract_contracts(str(spec_path))
            assert len(contracts) == 2


class TestSpecDriftDetector:
    def test_full_analysis(self):
        from spec_drift.drift_detector import SpecDriftDetector
        for tmp in safe_tempdir():
            spec_path = Path(tmp) / "spec.md"
            spec_path.write_text("# API Spec\nO endpoint GET /health retorna status.\n", encoding="utf-8")
            code_path = Path(tmp) / "api.py"
            code_path.write_text("""
from flask import Flask, jsonify
app = Flask(__name__)
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})
""", encoding="utf-8")
            detector = SpecDriftDetector()
            report = detector.analyze(str(spec_path), [str(code_path)])
            assert report.contracts_found >= 1

    def test_ci_gate_passes_clean_report(self):
        from spec_drift.drift_detector import SpecDriftDetector, DriftReport
        detector = SpecDriftDetector()
        report = DriftReport(spec_path="test", code_paths=[])
        passed, msg = detector.ci_gate(report)
        assert passed


# ============================================================
# L4: Context Grounding
# ============================================================

class TestAPIImportValidator:
    def test_stdlib_imports_pass(self):
        from context_grounding.grounding_detector import APIImportValidator, DependencyIndexer
        for tmp in safe_tempdir():
            indexer = DependencyIndexer(str(tmp))
            validator = APIImportValidator(indexer)
            code_file = Path(tmp) / "test.py"
            code_file.write_text("import os\nimport json\nfrom pathlib import Path\n", encoding="utf-8")
            findings = validator.validate_file(str(code_file))
            assert len(findings) == 0

    def test_unknown_import_detected(self):
        from context_grounding.grounding_detector import APIImportValidator, DependencyIndexer
        for tmp in safe_tempdir():
            indexer = DependencyIndexer(str(tmp))
            validator = APIImportValidator(indexer)
            code_file = Path(tmp) / "test.py"
            code_file.write_text("import nonexistent_library_xyz\n", encoding="utf-8")
            findings = validator.validate_file(str(code_file))
            assert len(findings) >= 1
            assert findings[0].htype.value == "api_import"


class TestGroundingScorer:
    def test_perfect_score(self):
        from context_grounding.grounding_detector import GroundingScorer
        scorer = GroundingScorer()
        score = scorer.calculate(
            imports_valid=10, imports_total=10, arch_violations=0,
            files_referenced=10, files_should_reference=10,
            constraints_respected=5, constraints_total=5
        )
        assert score == 100.0

    def test_bad_score(self):
        from context_grounding.grounding_detector import GroundingScorer
        scorer = GroundingScorer()
        score = scorer.calculate(2, 10, 5)
        assert score < 50


# ============================================================
# L5: ArtifactSyncEngine
# ============================================================

class TestArtifactSyncEngine:
    def test_register_artifact(self):
        from artifact_sync.sync_engine import ArtifactSyncEngine, ArtifactType
        for tmp in safe_tempdir():
            (Path(tmp) / "specs").mkdir()
            spec_file = Path(tmp) / "specs" / "test_spec.md"
            spec_file.write_text("# Spec", encoding="utf-8")
            engine = ArtifactSyncEngine(str(tmp))
            engine.register_artifact("specs/test_spec.md", ArtifactType.SPEC)
            status = engine.get_status("specs/test_spec.md")
            assert status.value == "synced"

    def test_mark_modified_invalidates_dependents(self):
        from artifact_sync.sync_engine import ArtifactSyncEngine, ArtifactType, SyncStatus
        for tmp in safe_tempdir():
            (Path(tmp) / "specs").mkdir()
            spec_file = Path(tmp) / "specs" / "spec.md"
            plan_file = Path(tmp) / "specs" / "plan.md"
            spec_file.write_text("# Spec v1", encoding="utf-8")
            plan_file.write_text("# Plan", encoding="utf-8")
            engine = ArtifactSyncEngine(str(tmp))
            engine.register_artifact("specs/spec.md", ArtifactType.SPEC)
            engine.register_artifact("specs/plan.md", ArtifactType.PLAN)
            engine.set_dependency("specs/spec.md", "specs/plan.md")
            spec_file.write_text("# Spec v2", encoding="utf-8")
            engine.mark_modified("specs/spec.md")
            plan_status = engine.get_status("specs/plan.md")
            assert plan_status == SyncStatus.STALE

    def test_validate_chain(self):
        from artifact_sync.sync_engine import ArtifactSyncEngine, ArtifactType
        for tmp in safe_tempdir():
            (Path(tmp) / "specs").mkdir()
            spec_file = Path(tmp) / "specs" / "root_spec.md"
            plan_file = Path(tmp) / "specs" / "plan.md"
            spec_file.write_text("# Root Spec", encoding="utf-8")
            plan_file.write_text("# Plan", encoding="utf-8")
            engine = ArtifactSyncEngine(str(tmp))
            engine.register_artifact("specs/root_spec.md", ArtifactType.SPEC)
            engine.register_artifact("specs/plan.md", ArtifactType.PLAN)
            engine.set_dependency("specs/root_spec.md", "specs/plan.md")
            report = engine.validate_chain("specs/root_spec.md")
            assert report.total_artifacts >= 2
            assert report.is_healthy


# ============================================================
# L1: SWE Process Benchmarks
# ============================================================

class TestSWEEvaluator:
    def test_evaluate_empty_dir(self):
        from benchmarks.swe_evaluator import SWEEvaluator, SWETask
        evaluator = SWEEvaluator()
        task = SWETask(id="SWE-001", name="test", description="desc", difficulty="N1")
        for tmp in safe_tempdir():
            metrics = evaluator.evaluate_artifacts(task, str(tmp))
            assert metrics.total_score is not None

    def test_evaluate_with_artifacts(self):
        from benchmarks.swe_evaluator import SWEEvaluator, SWETask
        evaluator = SWEEvaluator()
        task = SWETask(
            id="SWE-001", name="test", description="desc", difficulty="N1",
            expected_artifacts=["spec.md", "plan.md"],
            validation={"constraints": ["validate input"]}
        )
        for tmp in safe_tempdir():
            (Path(tmp) / "spec.md").write_text("# Spec\n\nO sistema deve validar input.", encoding="utf-8")
            (Path(tmp) / "plan.md").write_text("# Plan\n\nValidacao de input.", encoding="utf-8")
            (Path(tmp) / "api.py").write_text("def validate_input(x): return True\n", encoding="utf-8")
            metrics = evaluator.evaluate_artifacts(task, str(tmp))
            assert metrics.d1_spec_completeness > 0

    def test_default_tasks_loaded(self):
        from benchmarks.swe_evaluator import SWEEvaluator
        evaluator = SWEEvaluator()
        assert len(evaluator.tasks) == 5

    def test_benchmark_report_generated(self):
        from benchmarks.swe_evaluator import generate_benchmark_report, SWEResult, SWETask, SWEMetrics
        task = SWETask(id="SWE-001", name="test", description="desc", difficulty="N1")
        result = SWEResult(task=task, metrics=SWEMetrics(d1_spec_completeness=100), passed=True)
        report = generate_benchmark_report([result])
        assert "SWE-001" in report


# ============================================================
# L8: EvalLab Framework
# ============================================================

class TestStatisticalAnalyzer:
    def test_t_test_same_distributions(self):
        from eval_lab.eval_lab import StatisticalAnalyzer
        a = [10.0, 11.0, 12.0, 10.0, 11.0, 12.0, 10.0, 11.0]
        b = [10.0, 11.0, 12.0, 10.0, 11.0, 12.0, 10.0, 11.0]
        t_stat, p_value = StatisticalAnalyzer.t_test(a, b)
        assert t_stat == 0.0 or p_value > 0.05

    def test_t_test_different_distributions(self):
        from eval_lab.eval_lab import StatisticalAnalyzer
        a = [10.0, 11.0, 12.0, 10.0, 11.0, 12.0, 10.0, 11.0]
        b = [20.0, 21.0, 22.0, 20.0, 21.0, 22.0, 20.0, 21.0]
        t_stat, p_value = StatisticalAnalyzer.t_test(a, b)
        assert abs(t_stat) > 2.0

    def test_cohens_d_large_effect(self):
        from eval_lab.eval_lab import StatisticalAnalyzer
        a = [10.0, 11.0, 12.0, 10.0, 11.0]
        b = [20.0, 21.0, 22.0, 20.0, 21.0]
        d = StatisticalAnalyzer.cohens_d(a, b)
        assert d > 0.8

    def test_cohens_d_small_effect(self):
        from eval_lab.eval_lab import StatisticalAnalyzer
        a = [10.0, 10.1, 10.2, 10.0, 10.1]
        b = [10.0, 10.1, 10.2, 10.0, 10.1]
        d = StatisticalAnalyzer.cohens_d(a, b)
        assert d < 0.3


class TestEvalLab:
    def test_save_and_load_result(self):
        from eval_lab.eval_lab import EvalLab, ExperimentConfig
        for tmp in safe_tempdir():
            lab = EvalLab(output_dir=tmp)
            config = ExperimentConfig(
                experiment_id="EXP-TEST-001", name="Test", hypothesis="H0",
                condition_a={"framework": "sdd"}, condition_b={"framework": "vibe"},
                tasks=["SWE-001"], repetitions=2
            )
            def runner_a(**kw): return {"defect_rate": 5, "token_cost": 100, "spec_fidelity": 95, "correction_loops": 1, "arch_violations": 0}
            def runner_b(**kw): return {"defect_rate": 10, "token_cost": 80, "spec_fidelity": 60, "correction_loops": 3, "arch_violations": 2}
            result = lab.run_experiment(config, runner_a, runner_b, tmp)
            assert result.config.experiment_id == "EXP-TEST-001"
            report = lab.generate_report("EXP-TEST-001")
            assert "EXP-TEST-001" in report


# ============================================================
# L9: Cross-Platform Validator
# ============================================================

class TestCrossPlatformValidator:
    def test_dry_run_validation(self):
        from cross_platform.validator import CrossPlatformValidator
        for tmp in safe_tempdir():
            skill_dir = Path(tmp) / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("# Test Skill\n\nDoes something.", encoding="utf-8")
            validator = CrossPlatformValidator(dry_run=True)
            report = validator.validate_skill(str(skill_dir), platforms=["claude_code", "codex"])
            assert report.skill_name == "test-skill"
            assert len(report.results) == 2
            assert report.portability_score == 100.0

    def test_validate_all_skills(self):
        from cross_platform.validator import CrossPlatformValidator
        for tmp in safe_tempdir():
            for name in ["skill-a", "skill-b"]:
                d = Path(tmp) / name
                d.mkdir()
                (d / "SKILL.md").write_text(f"# {name}\n\nDescription.", encoding="utf-8")
            validator = CrossPlatformValidator(dry_run=True)
            reports = validator.validate_all(str(tmp), platforms=["claude_code"])
            assert len(reports) == 2
            assert all(r.portability_score == 100.0 for r in reports)


# ============================================================
# Teste de Integracao
# ============================================================

class TestIntegration:
    def test_permission_drift_grounding_integration(self):
        from permission_tiers.permission_gate import PermissionGate, PermissionTier
        from spec_drift.drift_detector import SpecDriftDetector
        from context_grounding.grounding_detector import DependencyIndexer, APIImportValidator
        gate = PermissionGate(interactive=False)
        result = gate.check_command("pytest tests/", "agent", PermissionTier.CONTRIBUTOR)
        assert result["allowed"]
        detector = SpecDriftDetector()
        assert detector is not None
        for tmp in safe_tempdir():
            indexer = DependencyIndexer(str(tmp))
            validator = APIImportValidator(indexer)
            assert validator is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
