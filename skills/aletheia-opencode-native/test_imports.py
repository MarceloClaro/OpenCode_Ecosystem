#!/usr/bin/env python3
"""Quick import test for Phase 4"""

import sys
sys.path.insert(0, r'C:\Users\marce\.config\opencode\skills\aletheia-opencode-native\references')

print("Testing imports...")

tests = [
    ("prover_agent", ["ProverAgent", "ProofAttempt"]),
    ("reasoning_orchestrator_v11", ["create_orchestrator"]),
    ("debate_arena", ["DebateArena"]),
    ("mcp_enricher", ["create_mcp_enricher"]),
    ("refinement_agent", ["RefinementAgent"]),
    ("imo_benchmark_adapter", ["IMOBenchmarkAdapter"]),
    ("verifier_v7", ["VerifierV7"]),
]

failed = []
for module_name, items in tests:
    try:
        module = __import__(module_name)
        for item in items:
            if not hasattr(module, item):
                failed.append(f"{module_name}.{item} NOT FOUND")
        print(f"OK: {module_name}")
    except Exception as e:
        failed.append(f"FAIL: {module_name} - {str(e)}")
        print(f"FAIL: {module_name} - {e}")

if failed:
    print(f"\n{len(failed)} failures:")
    for f in failed:
        print(f"  {f}")
    sys.exit(1)
else:
    print("\nAll imports successful!")
    sys.exit(0)
