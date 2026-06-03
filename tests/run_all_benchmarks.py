# -*- coding: utf-8 -*-
"""
CORA-Eval TDD Benchmark Runner
Executa todas as suites de teste TDD e gera relatorio JSON.
"""
import sys, os, json
from datetime import datetime

# Forca UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(__file__))
from test_d4_quimica import main as run_d4
from test_d5_biologia import main as run_d5
from test_d6_geociencias import main as run_d6
from test_d8_literatura import main as run_d8

def run_all():
    suites = {
        "D4 - Quimica (N1)": run_d4,
        "D5 - Biologia (N1)": run_d5,
        "D6 - Geociencias (N1)": run_d6,
        "D8 - Literatura (N1)": run_d8,
    }
    print("\n" + "=" * 60)
    print("  CORA-Eval: TDD Benchmark Runner - 4 Suites N1")
    print("=" * 60 + "\n")
    results = {}
    all_ok = 0
    for name, runner in suites.items():
        print(f"> {name}")
        print("-" * 60)
        ok = runner()
        results[name] = "PASS" if ok else "FAIL"
        if ok: all_ok += 1
        print()
    print("=" * 60)
    print("  RESUMO FINAL")
    print("=" * 60)
    for name, status in results.items():
        print(f"  [{status}] {name}")
    print("-" * 60)
    print(f"  TOTAL: {all_ok}/{len(suites)} suites passing")
    print("=" * 60)
    report_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_file = os.path.join(report_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump({
            "benchmark": "CORA-Eval", "level": "N1",
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "suites": results, "all_green": all_ok == len(suites),
        }, f, indent=2, ensure_ascii=False)
    print(f"\n  Relatorio: {report_file}")
    return all_ok == len(suites)

if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
