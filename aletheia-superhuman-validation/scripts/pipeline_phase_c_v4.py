"""Phase C: Lean 4 Verification for V4 Proofs."""

import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

def verify_lean_proof(problem_id: str, lean_code: str, lean_executable: str = None) -> Tuple[bool, str]:
    """Verify a single Lean proof."""
    
    if lean_executable is None:
        lean_executable = r"C:\Users\marce\Downloads\lean-4.30.0-windows\lean-4.30.0-windows\bin\lean.exe"
    
    # Create temp file
    temp_file = Path("temp") / f"{problem_id}_verify.lean"
    temp_file.parent.mkdir(exist_ok=True)
    
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(lean_code)
        
        # Run Lean
        result = subprocess.run(
            [lean_executable, str(temp_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        success = result.returncode == 0
        output = result.stderr if result.stderr else result.stdout
        
        return success, output[:500]
    
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, f"ERROR: {str(e)}"
    finally:
        if temp_file.exists():
            temp_file.unlink()

def run_phase_c_v4() -> List[Dict]:
    """Run Phase C on V4 proofs."""
    
    # Load V4 results
    with open('results/pipeline_phase_e_v4_results.json', encoding='utf-8') as f:
        v4_data = json.load(f)
    
    results = []
    print("\n" + "="*80)
    print("PHASE C: Lean 4 Verification of V4 Proofs")
    print("="*80 + "\n")
    
    for i, proof in enumerate(v4_data['results'], 1):
        problem_id = proof['problem_id']
        lean_code = proof['lean_code']
        domain = proof['domain']
        
        print(f"[{i}/{len(v4_data['results'])}] {problem_id} ({domain})... ", end='', flush=True)
        
        success, output = verify_lean_proof(problem_id, lean_code)
        
        if success:
            print("✓ VERIFIED")
            verification_status = "verified"
        else:
            print("✗ FAILED")
            verification_status = "failed"
        
        results.append({
            'problem_id': problem_id,
            'domain': domain,
            'verification_status': verification_status,
            'lean_error': output if not success else '',
            'sorry_count': proof['sorry_count'],
            'confidence': proof.get('confidence', 0),
            'timestamp': datetime.now().isoformat()
        })
    
    # Summary
    verified = sum(1 for r in results if r['verification_status'] == 'verified')
    print("\n" + "="*80)
    print("PHASE C SUMMARY")
    print("="*80)
    print(f"Total proofs:      {len(results)}")
    print(f"Verified:          {verified}/{len(results)} ({100*verified/len(results):.0f}%)")
    print(f"Failed:            {len(results)-verified}/{len(results)}")
    
    # Save results
    phase_c_output = {
        'phase': 'C-V4',
        'timestamp': datetime.now().isoformat(),
        'total_proofs': len(results),
        'verified_count': verified,
        'verification_rate': verified / len(results) if results else 0,
        'results': results
    }
    
    output_file = Path('results/pipeline_phase_c_v4_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(phase_c_output, f, indent=2, ensure_ascii=False)
    
    print(f"Results saved to: {output_file}\n")
    
    return results

if __name__ == '__main__':
    run_phase_c_v4()
