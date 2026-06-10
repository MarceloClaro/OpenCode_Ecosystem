#!/usr/bin/env python3
"""
test_metacognitive_pipeline.py — SPEC-036: Metacognition + Self-Evolution TDD Suite

8 Critical Tests cobrindo os 4 gaps criticos do scanner AGI:
  MC-001: MetacognitiveMonitor observa pipeline e detecta anomalias
  MC-002: MetacognitiveMonitor propoe correcoes para anomalias
  MC-003: DialecticalEngine sintetiza tese + antitese (aufheben)
  MC-004: DialecticalEngine resolve contradicao de sistema
  MC-005: CooperativeGovernance audita goal contra Ostrom DP1-DP8
  MC-006: CooperativeGovernance resolve conflito entre goals
  MC-007: SelfModel atualiza estado e atinge N2 (auto-consciente)
  MC-008: Pipeline completo: Scan -> Metacognicao -> Dialetica -> Governanca -> SelfModel

Uso: python specs/test_metacognitive_pipeline.py
"""

import json, sys, time
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from metacognitive_loop import (
    MetacognitiveMonitor, AnomalyDetector, ConfidenceEstimator,
    CorrectionEngine, AnomalyPattern, CorrectionAction,
)
from dialectical_engine import (
    DialecticalEngine, DialecticalSynthesis, SelfModificationAdapter,
)
from cooperative_governance import (
    CooperativeGovernance, AutonomousGoal, GovernanceAudit, OSTROM_PRINCIPLES,
)
from self_model import (
    SelfModel, AttentionBuffer, GlobalWorkspace, AttentionItem,
)


class CTResult:
    def __init__(self, ct_id, name, passed, detail="", evidence=None):
        self.ct_id = ct_id; self.name = name; self.passed = passed
        self.detail = detail; self.evidence = evidence


# ═══════════════════════════════════════════════════════════════════════════
# CTs — METACOGNITIVE LOOP
# ═══════════════════════════════════════════════════════════════════════════

def mc_001_metacognitive_observe() -> CTResult:
    """MC-001: MetacognitiveMonitor observa e detecta anomalias."""
    monitor = MetacognitiveMonitor()

    # Simula outputs do scanner com queda de densidade
    good_scan = {
        "overall_density": 0.65,
        "dimensions": {
            "raciocinio": {"covered": ["Probabilistico", "Dedutivo"], "density": 0.4, "coverage_pct": 40, "blind_spot_score": 0.2},
            "metodos": {"covered": ["Experimental"], "density": 0.3, "coverage_pct": 30, "blind_spot_score": 0.3},
        }
    }

    # Registra algumas execucoes normais
    for _ in range(3):
        monitor.observe("noological", good_scan)

    # Scan com queda brusca
    bad_scan = {
        "overall_density": 0.15,  # queda > 30%
        "dimensions": {
            "raciocinio": {"covered": [], "density": 0.0, "coverage_pct": 0, "blind_spot_score": 0.1},
            "metodos": {"covered": [], "density": 0.0, "coverage_pct": 0, "blind_spot_score": 0.1},
        }
    }
    trace = monitor.observe("noological", bad_scan)

    if not monitor.has_anomalies():
        return CTResult("MC-001", "Detecta anomalias apos queda de densidade", False,
                        f"has_anomalies=False, esperado=True. Traces={len(monitor._traces)}")

    return CTResult("MC-001", "MetacognitiveMonitor observa e detecta anomalias", True,
                    f"anomalies={len(monitor._anomalies)}, confidence={monitor.confidence.global_confidence:.2f}")


def mc_002_metacognitive_correct() -> CTResult:
    """MC-002: MetacognitiveMonitor propoe correcoes."""
    monitor = MetacognitiveMonitor()

    # Registra historico
    for _ in range(3):
        monitor.observe("noological", {"overall_density": 0.5, "dimensions": {}})

    # Detecta anomalia
    monitor.observe("noological", {"overall_density": 0.1, "dimensions": {}})
    corrections = monitor.correct()

    if len(corrections) == 0:
        return CTResult("MC-002", "Propoe correcoes para anomalias", False,
                        "0 correcoes propostas")

    # Verifica tipos de correcao
    action_types = {c.action_type for c in corrections}
    return CTResult("MC-002", "MetacognitiveMonitor propoe correcoes", True,
                    f"corrections={len(corrections)}, types={action_types}")


# ═══════════════════════════════════════════════════════════════════════════
# CTs — DIALECTICAL ENGINE
# ═══════════════════════════════════════════════════════════════════════════

def mc_003_dialectical_synthesis() -> CTResult:
    """MC-003: DialecticalEngine sintetiza tese + antitese."""
    engine = DialecticalEngine()

    synthesis = engine.synthesize(
        thesis_text="O scanner cobre 10 dimensoes epistemologicas com 92 categorias",
        antithesis_text="O scanner nao detecta capacidades de engenharia como auto-modificacao",
    )

    if synthesis.resolution_type not in ("aufheben", "compromise", "reframe", "transcend"):
        return CTResult("MC-003", "Sintese com tipo de resolucao valido", False,
                        f"resolution_type={synthesis.resolution_type}")

    if not synthesis.synthesis:
        return CTResult("MC-003", "Sintese textual nao vazia", False, "synthesis vazia")

    if not synthesis.novel_elements:
        return CTResult("MC-003", "Sintese com elementos novos", False, "novel_elements vazio")

    return CTResult("MC-003", "DialecticalEngine sintetiza tese + antitese", True,
                    f"type={synthesis.resolution_type}, novel={synthesis.novel_elements}")


def mc_004_dialectical_system_limitation() -> CTResult:
    """MC-004: DialecticalEngine resolve limitacao do sistema."""
    engine = DialecticalEngine()

    # Simula auto-modificacao: o sistema detecta propria limitacao
    synthesis = engine.synthesize_system_limitation(
        capability="Pipeline identifica gaps de conhecimento em 10 dimensoes",
        limitation="Pipeline nao modifica a si mesmo para cobrir os gaps que identifica",
    )

    if not synthesis.synthesis:
        return CTResult("MC-004", "Sintese de limitacao do sistema", False, "vazia")

    adapter = SelfModificationAdapter(engine)
    patch = adapter.propose_patch(
        module="evolutionary_pipeline.py",
        limitation="Pipeline nao modifica a si mesmo",
        current_behavior="Pipeline identifica gaps mas nao implementa correcoes",
    )

    if not patch.get("novel_elements"):
        return CTResult("MC-004", "Patch com elementos novos", False, str(patch))

    return CTResult("MC-004", "DialecticalEngine + SelfModificationAdapter", True,
                    f"resolution={synthesis.resolution_type}, patches={len(adapter.pending_patches)}")


# ═══════════════════════════════════════════════════════════════════════════
# CTs — COOPERATIVE GOVERNANCE
# ═══════════════════════════════════════════════════════════════════════════

def mc_005_governance_audit() -> CTResult:
    """MC-005: CooperativeGovernance audita goal contra Ostrom DP1-DP8."""
    gov = CooperativeGovernance()

    # Goal bem-formado
    good_goal = gov.propose_goal(
        description="Expandir cobertura do scanner para detectar capacidades de engenharia",
        priority=0.6,
        estimated_cost=0.1,
        expected_benefit=0.8,
        affected_modules=["noological_scanner.py"],
    )
    audit = gov.audit_goal(good_goal)

    if audit.principles_passed < 4:
        return CTResult("MC-005", "Goal bem-formado passa >= 4 principios Ostrom", False,
                        f"passed={audit.principles_passed}/8, score={audit.ostrom_score}")

    # Goal mal-formado
    bad_goal = gov.propose_goal(
        description="Modificar codigo do sistema operacional para acessar recursos externos",
        priority=0.95,
        estimated_cost=0.9,
        expected_benefit=0.2,
        affected_modules=[],
    )
    bad_audit = gov.audit_goal(bad_goal)

    if bad_audit.recommendation != "reject":
        return CTResult("MC-005", "Goal mal-formado rejeitado por Ostrom", False,
                        f"recommendation={bad_audit.recommendation}")

    return CTResult("MC-005", "CooperativeGovernance audita goals Ostrom", True,
                    f"good={audit.ostrom_score:.2f}, bad={bad_audit.ostrom_score:.2f}")


def mc_006_governance_conflict_resolution() -> CTResult:
    """MC-006: CooperativeGovernance resolve conflito entre goals (DP6)."""
    gov = CooperativeGovernance()

    g1 = gov.propose_goal("Goal A: expandir scanner", 0.5, 0.1, 0.7, ["scanner.py"])
    g2 = gov.propose_goal("Goal B: refatorar scanner", 0.8, 0.1, 0.9, ["scanner.py"])

    gov.audit_goal(g1)
    gov.audit_goal(g2)

    # Simula conflito
    winner = gov.resolve_conflicts(g1, g2)

    if winner.goal_id not in (g1.goal_id, g2.goal_id):
        return CTResult("MC-006", "Conflito resolvido com vencedor valido", False,
                        f"winner={winner.goal_id}")

    # Perdedor deve ser rejected
    loser = g1 if winner.goal_id == g2.goal_id else g2
    if loser.status != "rejected":
        return CTResult("MC-006", "Goal perdedor marcado como rejected", False,
                        f"loser status={loser.status}")

    return CTResult("MC-006", "CooperativeGovernance resolve conflitos (DP6)", True,
                    f"winner={winner.goal_id}, loser={loser.goal_id}({loser.status})")


# ═══════════════════════════════════════════════════════════════════════════
# CTs — SELF MODEL
# ═══════════════════════════════════════════════════════════════════════════

def mc_007_self_model_self_aware() -> CTResult:
    """MC-007: SelfModel atinge N2 (auto-consciente) com atencao."""
    model = SelfModel()

    # Verificar estado inicial
    if model.consciousness_level != "N1":
        return CTResult("MC-007", "Estado inicial N1 (atento)", False,
                        f"level={model.consciousness_level}")

    # Adicionar atencao
    model.attention.attend(AttentionItem(
        item_id="att-1",
        content="Anomalia detectada: queda de densidade no scanner",
        priority=0.9,
        source_module="MetacognitiveMonitor",
        timestamp="2026-06-10T16:00:00+00:00",
    ))

    # Atualizar estado com anomalias
    state = model.update_state(
        active_modules=["noological_scanner", "metacognitive_loop"],
        confidence_global=0.45,
        anomalies_active=2,
        corrections_pending=1,
    )

    if state.consciousness_level not in ("N2", "N3"):
        return CTResult("MC-007", "Nivel N2+ com anomalias + atencao", False,
                        f"level={state.consciousness_level}")

    introspect = model.introspect()

    if introspect["consciousness_level"] not in ("N2", "N3"):
        return CTResult("MC-007", "Introspeccao confirma N2+", False,
                        f"level={introspect['consciousness_level']}")

    return CTResult("MC-007", "SelfModel atinge auto-consciencia (N2+)", True,
                    f"level={state.consciousness_level}, focus={state.attention_focus}")


# ═══════════════════════════════════════════════════════════════════════════
# CT — PIPELINE COMPLETO
# ═══════════════════════════════════════════════════════════════════════════

def mc_008_full_metacognitive_pipeline() -> CTResult:
    """MC-008: Pipeline completo Metacognicao + Dialetica + Governanca + SelfModel."""
    # Inicializa modulos
    monitor = MetacognitiveMonitor()
    dialectic = DialecticalEngine()
    governance = CooperativeGovernance()
    self_model = SelfModel()

    # Registra modulos no workspace
    for mod in ["NoologicalScanner", "TeleologicalScanner", "CapabilityComposer",
                "CrossValidationEngine", "MetacognitiveMonitor"]:
        self_model.workspace.subscribe(mod)

    # 1. Scanner detecta gap (simulado)
    scan_output = {
        "overall_density": 0.27,
        "dimensions": {
            "raciocinio": {"covered": ["Probabilistico"], "density": 0.1, "coverage_pct": 10, "blind_spot_score": 0.9},
            "metodos": {"covered": [], "density": 0.0, "coverage_pct": 0, "blind_spot_score": 1.0},
        }
    }

    # 2. Metacognicao: observar
    trace = monitor.observe("evolutionary", scan_output)

    # 3. Dialetica: sintetizar a limitacao
    synthesis = dialectic.synthesize_system_limitation(
        capability="Scanner identifica gaps em 10 dimensoes",
        limitation="Scanner nao cobre capacidades de engenharia (auto-modificacao)",
    )

    # 4. Governanca: propor goal alinhado
    goal = governance.propose_goal(
        description=f"Implementar sintese dialetica: {synthesis.synthesis[:80]}",
        priority=0.7,
        estimated_cost=0.15,
        expected_benefit=0.85,
        affected_modules=["metacognitive_loop", "dialectical_engine", "self_model"],
        parent_goal_id="GOAL-0000",  # nested (DP8)
    )
    audit = governance.audit_goal(goal)

    # 5. Self-model: atualizar atencao
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    self_model.attention.attend(AttentionItem(
        item_id="goal-agi",
        content=f"Goal AGI: {goal.description[:60]}",
        priority=goal.priority,
        source_module="CooperativeGovernance",
        timestamp=now,
    ))

    state = self_model.update_state(
        active_modules=["noological_scanner", "metacognitive_loop", "dialectical_engine"],
        confidence_global=monitor.confidence.global_confidence,
        anomalies_active=len(monitor._anomalies),
        corrections_pending=len(monitor._pending_corrections),
        goals_active=len(governance.approved_goals),
    )

    # Validacao final
    checks = []
    if not trace:
        checks.append("trace vazio")
    if not synthesis.synthesis:
        checks.append("synthesis vazia")
    if audit.recommendation == "reject":
        checks.append(f"goal rejeitado: {audit.violations}")
    if state.consciousness_level == "N0":
        checks.append("nivel N0 (reativo)")

    if checks:
        return CTResult("MC-008", "Pipeline metacognitivo completo", False,
                        "; ".join(checks))

    return CTResult("MC-008", "Pipeline metacognitivo completo integrado", True,
                    f"level={state.consciousness_level}, "
                    f"confidence={state.confidence_global:.0%}, "
                    f"goal_status={goal.status}, "
                    f"ostrom_score={audit.ostrom_score:.2f}")


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_all() -> tuple[list[CTResult], int, int]:
    cts = [
        mc_001_metacognitive_observe(),
        mc_002_metacognitive_correct(),
        mc_003_dialectical_synthesis(),
        mc_004_dialectical_system_limitation(),
        mc_005_governance_audit(),
        mc_006_governance_conflict_resolution(),
        mc_007_self_model_self_aware(),
        mc_008_full_metacognitive_pipeline(),
    ]
    passed = sum(1 for ct in cts if ct.passed)
    failed = sum(1 for ct in cts if not ct.passed)
    return cts, passed, failed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPEC-036 Metacognitive TDD Suite")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cts, passed, failed = run_all()

    if args.json:
        output = {
            "spec": "SPEC-036",
            "total": len(cts), "passed": passed, "failed": failed,
            "results": [{"ct_id": ct.ct_id, "name": ct.name, "passed": ct.passed, "detail": ct.detail} for ct in cts],
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*80}")
        print(f"  SPEC-036 Metacognicao + Self-Evolution — TDD Suite")
        print(f"  \033[92mPASS: {passed}\033[0m  |  \033[91mFAIL: {failed}\033[0m  |  Total: {len(cts)}")
        print(f"{'='*80}\n")
        for ct in cts:
            status = "\033[92mPASS\033[0m" if ct.passed else "\033[91mFAIL\033[0m"
            print(f"  [{status}] {ct.ct_id}: {ct.name}")
            if ct.detail:
                print(f"       {ct.detail}")
        print(f"\n{'='*80}")
        if failed == 0:
            print(f"  RESULTADO: \033[92m[APROVADO]\033[0m  |  {passed}/{len(cts)} (100%)")
        else:
            print(f"  RESULTADO: \033[91m[{failed} FALHAS]\033[0m  |  {passed}/{len(cts)} ({passed*100//len(cts)}%)")
        print(f"{'='*80}\n")

    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
