"""
test_v2_simple.py — Simple Unit Test for ProofGeneratorV2
Session 11: Quick Validation

Generates a single proof to verify ProofGeneratorV2 works correctly.

Execution:
    $ python test_v2_simple.py
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from proof_generator_v2 import ProofGeneratorV2
from proof_templates import get_domain_for_problem


def test_single_proof():
    """Test generating a single proof"""
    print("\n" + "="*80)
    print("TEST: ProofGeneratorV2 Single Proof Generation")
    print("="*80 + "\n")
    
    # Create generator
    print("1. Initializing ProofGeneratorV2...", end=" ")
    try:
        gen = ProofGeneratorV2()
        print("✓")
    except Exception as e:
        print(f"✗ {str(e)}")
        return False
    
    # Test problem
    problem_id = "A0004"
    statement = "For any finite set S with n elements, |P(S)| = 2^n"
    domain = get_domain_for_problem(problem_id)
    
    print(f"2. Generating proof for {problem_id}...", end=" ")
    try:
        candidate = gen.generate(
            problem_id=problem_id,
            statement=statement,
            domain=domain,
            max_tokens=1500
        )
        print("✓")
    except Exception as e:
        print(f"✗ {str(e)}")
        return False
    
    # Validate result
    print("3. Validating result...", end=" ")
    
    checks = [
        ("problem_id", candidate.problem_id == problem_id),
        ("domain", candidate.domain == domain),
        ("statement", len(candidate.statement) > 0),
        ("natural_proof", len(candidate.natural_proof) > 0),
        ("lean_code", "theorem" in candidate.lean_code),
        ("confidence", 0.3 <= candidate.confidence <= 0.9),
        ("timestamp", len(candidate.timestamp) > 0)
    ]
    
    all_pass = all(check[1] for check in checks)
    if all_pass:
        print("✓")
    else:
        print("✗")
        for name, result in checks:
            status = "✓" if result else "✗"
            print(f"  {status} {name}")
        return False
    
    # Print result
    print("\n" + "="*80)
    print("RESULT")
    print("="*80)
    print(f"Problem ID: {candidate.problem_id}")
    print(f"Domain:     {candidate.domain}")
    print(f"Confidence: {candidate.confidence}")
    print(f"Template:   {candidate.template_used}")
    print(f"\nNatural Proof ({len(candidate.natural_proof)} chars):")
    print("-" * 80)
    print(candidate.natural_proof[:300] + "...")
    print("\nLean Code ({} chars):".format(len(candidate.lean_code)))
    print("-" * 80)
    print(candidate.lean_code[:300] + "...")
    print()
    
    return True


def test_batch_generation():
    """Test generating multiple proofs"""
    print("\n" + "="*80)
    print("TEST: ProofGeneratorV2 Batch Generation (5 problems)")
    print("="*80 + "\n")
    
    problems = [
        {"id": "A0004", "statement": "For any finite set S with n elements, |P(S)| = 2^n"},
        {"id": "B0014", "statement": "gcd(a, b) divides both a and b"},
        {"id": "B0017", "statement": "If a_n → L and b_n → L, then (a_n + b_n)/2 → L"},
        {"id": "E0019", "statement": "In any connected graph, there exists a path between vertices"},
        {"id": "E0020", "statement": "The sum of angles in any triangle equals π radians"}
    ]
    
    # Create generator
    print(f"Generating {len(problems)} proofs...")
    gen = ProofGeneratorV2()
    
    results = gen.batch_generate(problems)
    
    print(f"\nGenerated: {len(results)}/{len(problems)}")
    
    for result in results:
        status = "✓" if hasattr(result, 'confidence') else "✗"
        confidence = result.confidence if hasattr(result, 'confidence') else "N/A"
        print(f"  {status} {result.problem_id}: {confidence}")
    
    print()
    return len(results) == len(problems)


def main():
    """Run all tests"""
    print("\n[TEST] ProofGeneratorV2 Unit Tests\n")
    
    test1 = test_single_proof()
    print("\n" + "-"*80 + "\n")
    test2 = test_batch_generation()
    
    print("\n" + "="*80)
    if test1 and test2:
        print("✓ ALL TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("="*80 + "\n")
    
    return test1 and test2


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
