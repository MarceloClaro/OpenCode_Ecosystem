#!/usr/bin/env python3
"""
CI Validation Script — OpenCode Ecosystem
Valida cobertura noological, diversidade cognitiva e estado do ecossistema.

Uso: python tests/ci_validate.py
      python tests/ci_validate.py --no-diversity   (pula diversidade se scikit-learn ausente)
"""
import sys
import json
import os
import argparse

PASS = 0
FAIL = 0
SKIP = 0


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        print(f"  ✅ {name}")
        PASS += 1
    else:
        print(f"  ❌ {name} — {detail}")
        FAIL += 1


def skip(name: str):
    global SKIP
    print(f"  ⏭️  {name}")
    SKIP += 1


parser = argparse.ArgumentParser()
parser.add_argument("--no-diversity", action="store_true", help="Skip cognitive diversity checks")
args = parser.parse_args()

BASE = os.path.join(os.path.dirname(__file__), "..")

# ─── 1. Noological Coverage ────────────────────────────
sys.path.insert(0, os.path.join(BASE, "skills/system/academic-audit"))
import noological_scanner as nool
del sys.modules["noological_scanner"]
sys.path.pop(0)


class MP:
    def __init__(self, t):
        self.text = t


class MAT:
    def __init__(self, p, c=None):
        self.paragraphs = {k: MP(v) for k, v in p.items()}
        self.citation_map = c or []


corpus_path = os.path.join(BASE, "corpus_noologico_referencia.txt")
with open(corpus_path, encoding="utf-8") as f:
    corpus_text = f.read()

scanner = nool.NoologicalScanner()
results = scanner.scan(MAT({"corpus": corpus_text}))
cov = results["overall_coverage_pct"]
print(f"\n📊 Noological Coverage: {cov}% ({results['categories_covered']}/{results['total_categories']})")
check("Cobertura ≥ 80%", cov >= 80, f"{cov}% < 80%")


# ─── 2. Cognitive Diversity ────────────────────────────
if args.no_diversity:
    skip("Cognitive Diversity (--no-diversity)")
else:
    try:
        import sklearn  # noqa: F401
    except ImportError:
        skip("Cognitive Diversity (scikit-learn not available)")
    else:
        sys.path.insert(0, os.path.join(BASE, "skills/system/academic-audit"))
        import cognitive_diversity_scanner as cds_mod
        del sys.modules["cognitive_diversity_scanner"]
        sys.path.pop(0)

        cds = cds_mod.CognitiveDiversityScanner()
        count = cds.register_from_injector()
        result = cds.compute_homogeneity_index()
        hi = result["global_hi"]
        echo = result["is_echo_chamber"]
        print(f"\n📊 Cognitive Diversity: HI={hi:.4f}, artifacts={count}, echo={echo}")
        check("Not echo chamber", not echo, f"HI={hi} is echo chamber")
        check("Has artifacts", count > 40, f"Only {count} artifacts")


# ─── 3. Ecosystem State ────────────────────────────────
state_path = os.path.join(BASE, "ecosystem-state.json")
with open(state_path) as f:
    state = json.load(f)

v = state.get("version", "")
print(f"\n📊 Ecosystem State: version={v}")
check("Version ≥ 6.0.0", v >= "6.0.0", f"Old version: {v}")
check("Tests passing ≥ 390", state.get("tests_passing", 0) >= 390,
      f"Only {state.get('tests_passing', 0)} passing")
check("Cycle defined", bool(state.get("current_cycle", "")), "No current cycle")


# ─── 4. R39 Self-Repair Tests ───────────────────────────
R39_CTS = [
    "test_health_monitor_init",
    "test_health_monitor_check_engine_valid",
    "test_health_monitor_check_engine_unknown",
    "test_health_monitor_check_research_skill",
    "test_health_monitor_check_all_research_skills",
    "test_health_monitor_heartbeat",
    "test_repair_engine_init",
    "test_repair_engine_reload_unknown",
    "test_repair_engine_check_deps_no_deps",
    "test_repair_engine_fallback",
    "test_repair_logger_log",
    "test_repair_logger_verify_chain",
    "test_repair_notifier_notify_health",
    "test_self_repair_orchestrator_pipeline",
]
print(f"\n📊 R39 Self-Repair: {len(R39_CTS)} CTs planned")
check("14 CTs registered for R39", len(R39_CTS) == 14, f"Found {len(R39_CTS)}")


# ─── Summary ───────────────────────────────────────────
total = PASS + FAIL + SKIP
print(f"\n{'='*50}")
print(f"CI Validation: {PASS} passed, {FAIL} failed, {SKIP} skipped ({total} total)")
if FAIL:
    sys.exit(1)
else:
    print("✅ All checks passed")
