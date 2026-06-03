"""Phase C: Lean 4 verification for OpenCode proofs."""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

LEAN_PATH = r"C:\Users\marce\Downloads\lean-4.30.0-windows\lean-4.30.0-windows\bin\lean.exe"

def verify_with_lean(proof_code: str, problem_id: str) -> Dict[str, Any]:
    """Verify proof with Lean 4."""
    
    # Create temp file
    temp_dir = Path('temp_lean_verify')
    temp_dir.mkdir(exist_ok=True)
    
    temp_file = temp_dir / f"{problem_id}_verify.lean"
    
    # Wrap proof in Lean 4 syntax
    lean_code = f"""-- {problem_id}
import Mathlib

namespace AletheiaProof

{proof_code}

end AletheiaProof
"""
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(lean_code)
    
    # Run Lean verification
    try:
        result = subprocess.run(
            [LEAN_PATH, str(temp_file)],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8'
        )
        
        verified = result.returncode == 0
        errors = result.stderr if result.stderr else ""
        
        return {
            'verified': verified,
            'errors': errors[:500] if errors else "",
            'returncode': result.returncode,
            'success': verified
        }
    
    except subprocess.TimeoutExpired:
        return {
            'verified': False,
            'errors': "Lean verification timeout (30s)",
            'returncode': -1,
            'success': False
        }
    
    except Exception as e:
        return {
            'verified': False,
            'errors': str(e)[:500],
            'returncode': -1,
            'success': False
        }

def run_phase_c_opencode():
    """Execute Phase C verification for OpenCode proofs."""
    
    print("="*80)
    print("PHASE C: Lean 4 Verification (OpenCode Proofs)")
    print("="*80)
    
    # Load OpenCode proofs
    with open('results/pipeline_phase_e_opencode_results.json', encoding='utf-8') as f:
        data = json.load(f)
    
    results = []
    verified_count = 0
    
    for i, proof in enumerate(data['results'], 1):
        problem_id = proof.get('problem_id', f'Unknown_{i}')
        proof_code = proof.get('lean_code', '')
        
        print(f"\n[{problem_id}] Verifying with Lean 4...", end=' ')
        
        # Verify
        verification = verify_with_lean(proof_code, problem_id)
        
        if verification['verified']:
            print("✓ VERIFIED")
            verified_count += 1
        else:
            print("✗ FAILED")
        
        # Store result
        results.append({
            'problem_id': problem_id,
            'verified': verification['verified'],
            'errors': verification['errors'],
            'returncode': verification['returncode'],
            'sorry_count': proof.get('sorry_count', -1),
            'reasoning_phases': proof.get('reasoning_phases', 0)
        })
    
    # Print summary
    print("\n" + "="*80)
    print("PHASE C SUMMARY (OpenCode)")
    print("="*80)
    print(f"Total proofs:      {len(results)}")
    print(f"Verified:          {verified_count}/{len(results)} ({100*verified_count//len(results)}%)")
    print(f"Failed:            {len(results)-verified_count}/{len(results)}")
    
    # Breakdown by sorry count
    print("\nVerification by Sorry Count:")
    sorry_groups = {}
    for r in results:
        sorry = r['sorry_count']
        if sorry not in sorry_groups:
            sorry_groups[sorry] = {'verified': 0, 'total': 0}
        sorry_groups[sorry]['total'] += 1
        if r['verified']:
            sorry_groups[sorry]['verified'] += 1
    
    for sorry in sorted(sorry_groups.keys()):
        group = sorry_groups[sorry]
        pct = 100 * group['verified'] // group['total'] if group['total'] > 0 else 0
        print(f"  {sorry} sorry: {group['verified']}/{group['total']} verified ({pct}%)")
    
    # Analyze error patterns
    print("\nCommon Error Patterns:")
    error_patterns = {}
    for r in results:
        if r['errors']:
            # Extract first line of error
            first_error = r['errors'].split('\n')[0][:60]
            if first_error not in error_patterns:
                error_patterns[first_error] = 0
            error_patterns[first_error] += 1
    
    for pattern, count in sorted(error_patterns.items(), key=lambda x: -x[1])[:5]:
        print(f"  {count}x: {pattern}...")
    
    # Save results
    output = {
        'phase': 'C',
        'version': 'OpenCode',
        'timestamp': str(__import__('datetime').datetime.now()),
        'summary': {
            'total': len(results),
            'verified': verified_count,
            'success_rate': verified_count / len(results) if results else 0
        },
        'results': results
    }
    
    output_file = Path('results/pipeline_phase_c_opencode_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}")
    
    return output

if __name__ == '__main__':
    run_phase_c_opencode()
