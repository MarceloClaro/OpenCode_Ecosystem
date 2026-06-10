#!/usr/bin/env python3
"""
test_behavioral_autonomy.py — SPEC-038: Behavioral Autonomy TDD Suite

8 Critical Tests:
  BA-001: TrustScorer.record_outcome atualiza score com peso recente
  BA-002: TrustScorer shadow mode limita confianca nas primeiras 5 execucoes
  BA-003: TrustScorer rollback detection pune queda brusca de sucesso
  BA-004: BehavioralGate bloqueia acoes abaixo do threshold
  BA-005: BehavioralGate classifica risco (safe/moderate/risky/blocked)
  BA-006: NaturalForgetting promove itens sensory -> short_term -> long_term
  BA-007: NaturalForgetting expira itens sensoriais apos TTL
  BA-008: TrustEngine pipeline completo: gate -> execute -> learn -> recall

Uso: python specs/test_behavioral_autonomy.py
"""

import json, sys, time
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from trust_engine import (
    TrustScorer, BehavioralGate, NaturalForgetting,
    OutcomeTracker, TrustEngine, ActionTrust, GateDecision, MemorySlot,
)


class CTResult:
    def __init__(self, ct_id, name, passed, detail="", evidence=None):
        self.ct_id = ct_id; self.name = name; self.passed = passed
        self.detail = detail; self.evidence = evidence


# ═══════════════════════════════════════════════════════════════════════════
# CTs
# ═══════════════════════════════════════════════════════════════════════════

def ba_001_trust_scorer_updates() -> CTResult:
    """BA-001: TrustScorer atualiza score com peso recente (70/30)."""
    scorer = TrustScorer()

    # Simular acao bem-sucedida
    scorer.record_outcome("scan_raciocinio", True)
    scorer.record_outcome("scan_raciocinio", True)
    scorer.record_outcome("scan_raciocinio", True)
    scorer.record_outcome("scan_raciocinio", True)
    scorer.record_outcome("scan_raciocinio", True)

    trust = scorer.get_trust("scan_raciocinio")
    if trust.trust_score < 0.7:
        return CTResult("BA-001", "Trust sobe com sucessos (>0.7)", False,
                        f"trust={trust.trust_score:.2f}, success={trust.successful}/{trust.total_executions}")

    # Simular falhas
    scorer.record_outcome("scan_raciocinio", False)
    scorer.record_outcome("scan_raciocinio", False)
    scorer.record_outcome("scan_raciocinio", False)

    trust2 = scorer.get_trust("scan_raciocinio")
    if trust2.trust_score > trust.trust_score * 0.5:
        return CTResult("BA-001", "Trust cai com falhas consecutivas", False,
                        f"before={trust.trust_score:.2f}, after={trust2.trust_score:.2f}, penalty={trust2.penalty:.2f}")

    return CTResult("BA-001", "TrustScorer adapta com peso recente 70/30", True,
                    f"success={trust2.trust_score:.2f}, penalty={trust2.penalty:.2f}")


def ba_002_shadow_mode() -> CTResult:
    """BA-002: Shadow mode limita confianca nas primeiras 5 execucoes."""
    scorer = TrustScorer()

    # Executar 3 vezes com sucesso (ainda em shadow mode)
    for _ in range(3):
        scorer.record_outcome("acao_nova", True)

    trust = scorer.get_trust("acao_nova")
    if trust.trust_score > 0.5:
        return CTResult("BA-002", "Shadow mode: trust <= 0.5 nas primeiras 5", False,
                        f"trust={trust.trust_score:.2f}")

    # Executar mais 3 (sai do shadow mode)
    for _ in range(3):
        scorer.record_outcome("acao_nova", True)

    trust2 = scorer.get_trust("acao_nova")
    if trust2.trust_score <= 0.5:
        return CTResult("BA-002", "Pos-shadow: trust > 0.5 apos 6 execucoes", False,
                        f"trust={trust2.trust_score:.2f}")

    return CTResult("BA-002", "Shadow mode funciona (5 execucoes)", True,
                    f"shadow_trust={trust.trust_score:.2f}, post_shadow={trust2.trust_score:.2f}")


def ba_003_rollback_detection() -> CTResult:
    """BA-003: Rollback detection pune queda brusca de sucesso."""
    scorer = TrustScorer()

    # Construir baseline de sucesso
    for _ in range(6):
        scorer.record_outcome("acao_risco", True)
    scorer.update_baseline(0.9)

    # Queda brusca
    for _ in range(5):
        scorer.record_outcome("acao_risco", False)

    trust = scorer.get_trust("acao_risco")
    # Deve ter aplicado rollback (trust caiu significativamente)
    if trust.trust_score > 0.4:
        return CTResult("BA-003", "Rollback: trust cai abaixo de 0.4 apos queda", False,
                        f"trust={trust.trust_score:.2f}")

    return CTResult("BA-003", "Rollback detection pune queda brusca", True,
                    f"trust={trust.trust_score:.2f}, penalty={trust.penalty:.2f}")


def ba_004_gate_blocks() -> CTResult:
    """BA-004: BehavioralGate bloqueia acoes abaixo do threshold."""
    scorer = TrustScorer()
    gate = BehavioralGate(scorer)

    # Acao com confianca alta
    for _ in range(8):
        scorer.record_outcome("scan_confiavel", True)
    dec1 = gate.gate("scan_confiavel")
    if not dec1.allowed:
        return CTResult("BA-004", "Gate permite acao confiavel", False,
                        f"allowed={dec1.allowed}, trust={dec1.trust_score:.2f}")

    # Acao nova (shadow mode, trust baixo)
    gate.set_threshold(0.6)
    dec2 = gate.gate("acao_nova")
    if dec2.allowed:
        return CTResult("BA-004", "Gate bloqueia acao nova com threshold alto", False,
                        f"allowed={dec2.allowed}, trust={dec2.trust_score:.2f}")

    return CTResult("BA-004", "BehavioralGate bloqueia/permite corretamente", True,
                    f"allowed_confiavel={dec1.allowed}, blocked_nova={not dec2.allowed}")


def ba_005_risk_classification() -> CTResult:
    """BA-005: BehavioralGate classifica risco (safe/moderate/risky/blocked)."""
    scorer = TrustScorer()
    gate = BehavioralGate(scorer)

    # Safe: alta confianca
    for _ in range(10):
        scorer.record_outcome("safe_action", True)
    safe_dec = gate.gate("safe_action")
    if safe_dec.risk_level != "safe":
        return CTResult("BA-005", f"safe_action = safe (obtido: {safe_dec.risk_level})", False,
                        str(safe_dec))

    # Moderate: poucas execucoes
    for _ in range(3):
        scorer.record_outcome("moderate_action", True)
    mod_dec = gate.gate("moderate_action")
    if mod_dec.risk_level not in ("moderate", "safe"):
        return CTResult("BA-005", f"moderate_action = moderate/safe (obtido: {mod_dec.risk_level})", False,
                        str(mod_dec))

    return CTResult("BA-005", "Risk classification funciona", True,
                    f"safe={safe_dec.risk_level}, moderate={mod_dec.risk_level}")


def ba_006_natural_forgetting_promotion() -> CTResult:
    """BA-006: NaturalForgetting promove sensory -> short_term -> long_term."""
    memory = NaturalForgetting()

    slot = memory.store("Padrao de falha: queda de densidade precede perda de categorias", importance=0.8)

    if slot.memory_type != "sensory":
        return CTResult("BA-006", "Novo item comeca como sensory", False,
                        f"type={slot.memory_type}")

    # Acessar 3 vezes -> promover para short_term
    for _ in range(3):
        memory.recall("queda de densidade")
    recalled = memory.recall("queda de densidade")
    if recalled and recalled.memory_type != "short_term":
        return CTResult("BA-006", "3 acessos promove para short_term", False,
                        f"type={recalled.memory_type}, accesses={recalled.access_count}")

    # Acessar mais 3 vezes -> promover para long_term
    for _ in range(3):
        memory.recall("queda de densidade")
    recalled2 = memory.recall("queda de densidade")
    if recalled2 and recalled2.memory_type != "long_term":
        return CTResult("BA-006", "6 acessos + alta importance promove para long_term", False,
                        f"type={recalled2.memory_type}, accesses={recalled2.access_count}")

    return CTResult("BA-006", "Natural forgetting promove corretamente", True,
                    f"final_type={recalled2.memory_type}, accesses={recalled2.access_count}")


def ba_007_memory_expiry() -> CTResult:
    """BA-007: NaturalForgetting expira itens sensoriais apos TTL."""
    memory = NaturalForgetting()
    memory.SENSORY_TTL = 1  # 1 segundo para teste

    slot = memory.store("Informacao temporaria", importance=0.2)
    stats_before = memory.memory_stats

    # Esperar TTL expirar
    time.sleep(1.5)

    result = memory.recall("Informacao temporaria")
    stats_after = memory.memory_stats

    if result is not None:
        return CTResult("BA-007", "Item sensorial expira apos TTL", False,
                        f"still_present={result is not None}")

    return CTResult("BA-007", "Natural forgetting expira itens corretamente", True,
                    f"before={stats_before['total']}, after={stats_after['total']}")


def ba_008_full_trust_pipeline() -> CTResult:
    """BA-008: TrustEngine pipeline completo: gate -> execute -> learn -> recall."""
    engine = TrustEngine()

    # 1. Gate: acao nova (deve permitir com threshold baixo)
    engine.gate.gate.set_threshold(0.2)
    dec = engine.execute("scan_metodos")

    if not dec.allowed:
        return CTResult("BA-008", "Gate permite acao nova com threshold baixo", False,
                        f"allowed={dec.allowed}, trust={dec.trust_score:.2f}")

    # 2. Learn: simular execucoes bem-sucedidas
    for i in range(8):
        engine.learn("scan_metodos", success=True, delta=0.1,
                     context=f"Scan de metodos #{i+1} concluido com melhoria")

    # 3. Gate apos aprendizado: deve estar mais confiante
    dec2 = engine.execute("scan_metodos")
    if dec2.trust_score < 0.5:
        return CTResult("BA-008", "Trust sobe apos aprendizado", False,
                        f"trust={dec2.trust_score:.2f}")

    # 4. Recall: verificar memoria
    memories = engine.recall("scan_metodos")
    if len(memories) == 0:
        return CTResult("BA-008", "Memoria armazena contexto de execucao", False,
                        "0 memorias")

    # 5. Status
    status = engine.status
    if status["total_improvement"] <= 0:
        return CTResult("BA-008", "Total improvement > 0", False,
                        f"improvement={status['total_improvement']}")

    return CTResult("BA-008", "TrustEngine pipeline completo", True,
                    f"trust={dec2.trust_score:.2f}, memories={len(memories)}, "
                    f"improvement={status['total_improvement']:.2f}, "
                    f"success_rate={status['recent_success_rate']:.0%}")


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_all() -> tuple[list[CTResult], int, int]:
    cts = [
        ba_001_trust_scorer_updates(),
        ba_002_shadow_mode(),
        ba_003_rollback_detection(),
        ba_004_gate_blocks(),
        ba_005_risk_classification(),
        ba_006_natural_forgetting_promotion(),
        ba_007_memory_expiry(),
        ba_008_full_trust_pipeline(),
    ]
    passed = sum(1 for ct in cts if ct.passed)
    failed = sum(1 for ct in cts if not ct.passed)
    return cts, passed, failed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="SPEC-038 Behavioral Autonomy TDD Suite")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    cts, passed, failed = run_all()

    if args.json:
        print(json.dumps({"spec": "SPEC-038", "total": len(cts), "passed": passed, "failed": failed,
                          "results": [{"ct_id": ct.ct_id, "name": ct.name, "passed": ct.passed, "detail": ct.detail} for ct in cts]},
                         indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*80}")
        print(f"  SPEC-038 Behavioral Autonomy — TDD Suite")
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
