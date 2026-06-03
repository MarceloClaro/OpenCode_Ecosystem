#!/usr/bin/env python3
"""Ultra-light Phase 4 test: 1 problem, just scoring (no debate/enrichment)"""

import sys
sys.path.insert(0, r'C:\Users\marce\.config\opencode\skills\aletheia-opencode-native\references')

print("Ultra-Light Phase 4 Test (Scoring Only)")
print("=" * 60)

# Step 1: Load 1 problem
print("\n[1] Loading 1 IMO problem...")
from imo_benchmark_adapter import IMOBenchmarkAdapter
adapter = IMOBenchmarkAdapter()
try:
    loaded = adapter.load_from_url()
    print(f"  [OK] Loaded {loaded} problems")
except Exception as e:
    print(f"  [WARN] Could not load from URL: {e}")
    adapter.problems = adapter.sample_problems(n=1)
    loaded = len(adapter.problems)

if not adapter.problems:
    print("  [ERROR] No problems!")
    sys.exit(1)

problem = adapter.problems[0]
print(f"  [OK] Using: {problem.problem_id} ({problem.category})")

# Step 2: Create VerifierV7 and assess original problem (baseline)
print("\n[2] Assessing original problem (baseline)...")
from verifier_v7 import VerifierV7

verifier = VerifierV7()
# Original assessment
original_proof_dict = {
    "proof_id": f"{problem.problem_id}_original",
    "text": "[No proof attempt - baseline]",
    "domain": problem.aletheia_domain
}
original_assess = verifier.assess(original_proof_dict)
original_score = original_assess.overall_d11_score
print(f"  [OK] Original D11 score: {original_score:.2f}")

# Step 3: Create a simple proof and assess it
print("\n[3] Creating simple proof...")
simple_proof = f"PROOF FOR PROBLEM {problem.problem_id}:\n\nBy assumption and basic properties, the result follows. QED"
refined_proof_dict = {
    "proof_id": f"{problem.problem_id}_refined",
    "text": simple_proof,
    "domain": problem.aletheia_domain
}
refined_assess = verifier.assess(refined_proof_dict)
refined_score = refined_assess.overall_d11_score
print(f"  [OK] Simple proof D11 score: {refined_score:.2f}")
improvement = refined_score - original_score
print(f"  [OK] Improvement: {improvement:+.2f}")

# Step 4: Summary
print("\n" + "=" * 60)
print("[SUCCESS] Phase 4 validation pipeline ready!")
print(f"  Problem loaded: {problem.problem_id}")
print(f"  Scoring works: {original_score:.2f} -> {refined_score:.2f}")
print(f"  Can now run full validation with 5-60 problems")
