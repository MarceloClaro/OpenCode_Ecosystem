#!/usr/bin/env python3
"""
test_n2_n3_upgrades.py — N2+N3 Upgrades TDD Suite

8 Critical Tests:
  N2-UP-001: SelfModel.forecast_confidence() preve tendencia
  N2-UP-002: SelfModel.source_introspection() examina proprio codigo
  N2-UP-003: SelfModel.self_other_boundary() distingue self/other
  N2-UP-004: SelfModel.predict_state() combina forecasting + introspeccao
  N3-UP-005: MetacognitiveMonitor.auto_monitor() loop autonomo
  N3-UP-006: MetacognitiveMonitor.root_cause_analysis() correlaciona anomalias
  N3-UP-007: MetacognitiveMonitor.adaptive_thresholds() ajusta thresholds
  N3-UP-008: MetacognitiveMonitor.correction_learning_report() rankeia correcoes

Uso: python specs/test_n2_n3_upgrades.py
"""

import json, sys
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
SCANNER_DIR = BASE_DIR / "skills" / "system" / "academic-audit"
sys.path.insert(0, str(SCANNER_DIR))

from self_model import SelfModel, AttentionItem
from metacognitive_loop import MetacognitiveMonitor


class CTResult:
    def __init__(self, ct_id, name, passed, detail="", evidence=None):
        self.ct_id = ct_id; self.name = name; self.passed = passed
        self.detail = detail; self.evidence = evidence


# ═══════════════════════════════════════════════════════════════════════════
# CTs — N2 UPGRADES
# ═══════════════════════════════════════════════════════════════════════════

def n2_up_001_forecast() -> CTResult:
    """N2-UP-001: SelfModel.forecast_confidence() preve tendencia."""
    model = SelfModel()

    # Simular queda de confianca
    for conf in [0.8, 0.6, 0.4, 0.3, 0.2]:
        model.update_state(confidence_global=conf, anomalies_active=1)

    fc = model.forecast_confidence()

    if "predicted" not in fc:
        return CTResult("N2-UP-001", "Forecast retorna predicted", False, str(fc))
    if fc["trend"] != "falling":
        return CTResult("N2-UP-001", "Detecta tendencia de queda", False, f"trend={fc['trend']}")
    if fc["predicted"] > 0.3:
        return CTResult("N2-UP-001", "Preve confianca baixa (<0.3)", False, f"pred={fc['predicted']}")

    return CTResult("N2-UP-001", "Forecast preve queda de confianca", True,
                    f"pred={fc['predicted']}, trend={fc['trend']}, interval={fc['confidence_interval']}")


def n2_up_002_source_introspection() -> CTResult:
    """N2-UP-002: SelfModel.source_introspection() examina proprio codigo."""
    model = SelfModel()
    info = model.source_introspection()

    if info["module_count"] == 0:
        return CTResult("N2-UP-002", "Introspeccao encontra modulos", False, "0 modulos")
    if info["total_lines"] == 0:
        return CTResult("N2-UP-002", "Introspeccao conta linhas", False, "0 linhas")
    if "self_model.py" not in info["modules"]:
        return CTResult("N2-UP-002", "Reconhece o proprio arquivo", False,
                        f"modules={list(info['modules'].keys())[:5]}")

    return CTResult("N2-UP-002", "Source introspection funciona", True,
                    f"modules={info['module_count']}, loc={info['total_lines']}")


def n2_up_003_self_other_boundary() -> CTResult:
    """N2-UP-003: SelfModel.self_other_boundary() distingue self/other."""
    model = SelfModel()

    self_check = model.self_other_boundary("SelfModel")
    other_check = model.self_other_boundary("MCP:websearch")
    boundary_check = model.self_other_boundary("unknown_plugin")

    if self_check["classification"] != "self":
        return CTResult("N2-UP-003", "SelfModel reconhecido como self", False, str(self_check))
    if other_check["classification"] != "other":
        return CTResult("N2-UP-003", "MCP externo reconhecido como other", False, str(other_check))

    return CTResult("N2-UP-003", "Self/other boundary funciona", True,
                    f"self={self_check['classification']}, other={other_check['classification']}, boundary={boundary_check['classification']}")


def n2_up_004_predict_state() -> CTResult:
    """N2-UP-004: SelfModel.predict_state() combina forecasting + introspeccao."""
    model = SelfModel()

    for conf in [0.7, 0.65, 0.6, 0.55, 0.5]:
        model.update_state(confidence_global=conf, anomalies_active=1)

    pred = model.predict_state()

    if pred.get("status") == "insufficient_data":
        return CTResult("N2-UP-004", "Predict state com dados suficientes", False, "insufficient_data")
    if "risk_assessment" not in pred:
        return CTResult("N2-UP-004", "Predict inclui risk_assessment", False, str(pred))
    if "recommended_action" not in pred:
        return CTResult("N2-UP-004", "Predict inclui recommended_action", False, str(pred))

    return CTResult("N2-UP-004", "Predict state combina forecast + introspeccao", True,
                    f"risk={pred['risk_assessment']}, action={pred['recommended_action']}")


# ═══════════════════════════════════════════════════════════════════════════
# CTs — N3 UPGRADES
# ═══════════════════════════════════════════════════════════════════════════

def n3_up_005_auto_monitor() -> CTResult:
    """N3-UP-005: MetacognitiveMonitor.auto_monitor() loop autonomo."""
    monitor = MetacognitiveMonitor()

    # Registrar baseline
    for _ in range(3):
        monitor.observe("scanner", {"overall_density": 0.7, "dimensions": {"raciocinio": {"covered": ["Prob"], "density": 0.4, "coverage_pct": 40, "blind_spot_score": 0.2}}})

    # Auto-monitor: o loop deve executar pelo menos 1 iteracao
    scan_data = {"overall_density": 0.2, "dimensions": {"raciocinio": {"covered": [], "density": 0.0, "coverage_pct": 0, "blind_spot_score": 0.1}}}
    result = monitor.auto_monitor(lambda: scan_data, max_iterations=2)

    if result["iterations"] == 0:
        return CTResult("N3-UP-005", "Auto-monitor executa iteracoes", False, f"iterations={result['iterations']}")
    if result["corrections_applied"] == 0:
        return CTResult("N3-UP-005", "Auto-monitor aplica correcoes", False, "0 correcoes")

    return CTResult("N3-UP-005", "Loop autonomo funciona", True,
                    f"iterations={result['iterations']}, corrections={result['corrections_applied']}, stabilized={result['stabilized']}")


def n3_up_006_root_cause() -> CTResult:
    """N3-UP-006: Root cause analysis com inferencia causal (Granger-inspired).

    5 traces: ANOM-001 aparece sozinho (causa), ANOM-002 so depois (efeito).
    Base rate baixo + alta probabilidade condicional = Granger score positivo.
    """
    monitor = MetacognitiveMonitor()

    # T0-T1: limpos
    monitor.observe("s", {"overall_density": 0.7, "dimensions": {"r": {"covered": ["P"], "density": 0.3, "coverage_pct": 30, "blind_spot_score": 0.3}}}).anomaly_flags = []
    monitor.observe("s", {"overall_density": 0.7, "dimensions": {"r": {"covered": ["P"], "density": 0.3, "coverage_pct": 30, "blind_spot_score": 0.3}}}).anomaly_flags = []

    # T2: ANOM-001 (causa)
    monitor.observe("s", {"overall_density": 0.5, "dimensions": {"r": {"covered": ["P"], "density": 0.2, "coverage_pct": 20, "blind_spot_score": 0.3}}}).anomaly_flags = ["ANOM-001"]

    # T3: ANOM-002 (efeito imediato)
    monitor.observe("s", {"overall_density": 0.5, "dimensions": {"r": {"covered": [], "density": 0.0, "coverage_pct": 0, "blind_spot_score": 0.1}}}).anomaly_flags = ["ANOM-002"]

    # T4: limpo
    monitor.observe("s", {"overall_density": 0.7, "dimensions": {"r": {"covered": ["P"], "density": 0.3, "coverage_pct": 30, "blind_spot_score": 0.3}}}).anomaly_flags = []

    # Registrar anomalias
    from metacognitive_loop import AnomalyPattern
    monitor._anomalies = [AnomalyPattern("ANOM-001", "g", (0.3,1), 0.15, "critical", "Q"), AnomalyPattern("ANOM-002", "r", (2,10), 0, "high", "P")]

    rca = monitor.root_cause_analysis()

    if "verdict" not in rca:
        return CTResult("N3-UP-006", "Root cause retorna verdict", False, str(rca))

    has_causal = (
        len(rca.get("causal_edges", [])) > 0 or
        len(rca.get("causal_chains", [])) > 0 or
        len(rca.get("common_causes", [])) > 0
    )

    if not has_causal:
        return CTResult("N3-UP-006", "Inferencia causal detecta relacoes", False,
                       f"edges={len(rca.get('causal_edges',[]))}, chains={len(rca.get('causal_chains',[]))}, verdict={rca['verdict'][:80]}")

    bayesian = rca.get("bayesian", {})
    return CTResult("N3-UP-006", "Root cause com inferencia causal (Granger + Bayes)", True,
                    f"edges={len(rca.get('causal_edges',[]))}, chains={len(rca.get('causal_chains',[]))}, "
                    f"bayes={len(bayesian.get('inferences',[]))}, verdict={rca['verdict'][:80]}")


def n3_up_007_adaptive_thresholds() -> CTResult:
    """N3-UP-007: MetacognitiveMonitor.adaptive_thresholds() ajusta thresholds."""
    monitor = MetacognitiveMonitor()

    # Sem historico suficiente
    thresh = monitor.adaptive_thresholds()
    if thresh["density_drop_threshold"] != 0.30:
        return CTResult("N3-UP-007", "Threshold default = 0.30", False, str(thresh))

    # Com historico (simular correcoes bem-sucedidas)
    for _ in range(6):
        monitor.observe("scanner", {"overall_density": 0.5, "dimensions": {}})
    monitor.correct()

    thresh2 = monitor.adaptive_thresholds()
    if "false_positive_rate" not in thresh2:
        return CTResult("N3-UP-007", "Adaptive thresholds inclui false_positive_rate", False, str(thresh2))

    return CTResult("N3-UP-007", "Adaptive thresholds ajustam com historico", True,
                    f"density_threshold={thresh2['density_drop_threshold']}, fpr={thresh2['false_positive_rate']}")


def n3_up_008_correction_learning() -> CTResult:
    """N3-UP-008: MetacognitiveMonitor.correction_learning_report() rankeia correcoes."""
    monitor = MetacognitiveMonitor()

    # Simular correcoes com diferentes taxas de sucesso
    for _ in range(5):
        monitor.observe("scanner", {"overall_density": 0.2, "dimensions": {}})
    corrections = monitor.correct()

    # Marcar algumas como bem-sucedidas e outras nao
    for i, c in enumerate(corrections):
        c.success = (i % 2 == 0)
        c.delta_improvement = 0.15 if c.success else 0.0
        monitor.corrector._corrections.append(c)

    report = monitor.correction_learning_report()

    if report.get("status") == "no_data":
        return CTResult("N3-UP-008", "Learning report com dados", False, "no_data")
    if "best_action" not in report:
        return CTResult("N3-UP-008", "Learning report identifica best_action", False, str(report))

    return CTResult("N3-UP-008", "Correction learning rankeia por sucesso", True,
                    f"best={report['best_action']}, types_learned={report['correction_types_learned']}")


# ═══════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════

def run_all() -> tuple[list[CTResult], int, int]:
    cts = [
        n2_up_001_forecast(),
        n2_up_002_source_introspection(),
        n2_up_003_self_other_boundary(),
        n2_up_004_predict_state(),
        n3_up_005_auto_monitor(),
        n3_up_006_root_cause(),
        n3_up_007_adaptive_thresholds(),
        n3_up_008_correction_learning(),
    ]
    passed = sum(1 for ct in cts if ct.passed)
    failed = sum(1 for ct in cts if not ct.passed)
    return cts, passed, failed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="N2+N3 Upgrades TDD Suite")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    cts, passed, failed = run_all()

    if args.json:
        print(json.dumps({"suite": "N2+N3-Upgrades", "total": len(cts), "passed": passed, "failed": failed,
                          "results": [{"ct_id": ct.ct_id, "name": ct.name, "passed": ct.passed, "detail": ct.detail} for ct in cts]},
                         indent=2, ensure_ascii=False))
    else:
        print(f"\n{'='*80}")
        print(f"  N2 + N3 Upgrades — TDD Suite")
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
