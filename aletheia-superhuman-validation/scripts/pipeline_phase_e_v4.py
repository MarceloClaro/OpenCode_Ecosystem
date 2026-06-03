"""
Phase E.4: Proof Generation with Improved V4 Templates + V3 Heuristics

Since Claude API requires authentication, we'll:
1. Use V4 templates to improve heuristics
2. Fall back to V3 heuristic completion
3. Prepare infrastructure for Claude integration (Phase E.5)
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from proof_generator_v3 import ProofGeneratorV3, LLMProvider
from proof_templates_v4 import ProofDomain, get_template_v4

class ProofGeneratorV4Heuristic:
    """V4 proof generation using improved V3 heuristics with V4 templates."""
    
    def __init__(self):
        self.gen_v3 = ProofGeneratorV3(llm_provider=LLMProvider.FALLBACK)
    
    def generate_proof(self, problem_id: str, domain: str, statement: str) -> Dict:
        """Generate proof using V3 heuristics but with V4 template guidance."""
        
        # Get V4 template guidance
        try:
            domain_enum = ProofDomain[domain.upper()]
        except KeyError:
            domain_enum = ProofDomain.LOGIC
        
        template_v4 = get_template_v4(domain_enum)
        
        # Generate with V3 (using generate() method)
        proof_v3 = self.gen_v3.generate(problem_id, statement, domain)
        
        return {
            'problem_id': problem_id,
            'domain': domain,
            'statement': statement,
            'lean_code': proof_v3.lean_code,
            'sorry_count': proof_v3.sorry_count,
            'generation_method': 'v4-heuristic',
            'template_v4_hints': template_v4['hints'],
            'confidence': proof_v3.confidence,
            'source': proof_v3.source,
        }
    
    def batch_generate(self, problems: List[dict]) -> List[Dict]:
        """Generate proofs for multiple problems."""
        results = []
        for i, problem in enumerate(problems, 1):
            print(f"[{i}/{len(problems)}] {problem['problem_id']}...", end=" ")
            try:
                proof = self.generate_proof(
                    problem_id=problem['problem_id'],
                    domain=problem['domain'],
                    statement=problem['statement'],
                )
                results.append(proof)
                print(f"OK (sorry={proof['sorry_count']})")
            except Exception as e:
                print(f"ERROR: {e}")
        return results

def run_phase_e_v4(subset_size: int = 10, test_data: bool = False) -> List[Dict]:
    """Run Phase E with V4 templates."""
    
    # Load selected problems
    problems_file = Path("data/full_problems_phase_e.json") if not test_data else Path("data/test_problems_phase_e.json")
    if not problems_file.exists():
        raise FileNotFoundError(f"Problems file not found: {problems_file}")
    
    with open(problems_file, encoding='utf-8') as f:
        data = json.load(f)
        problems = data.get('problems', [])[:subset_size]
    
    print('='*80)
    print('PHASE E: Proof Generation with V4 Templates')
    print('='*80)
    print(f'Selected {len(problems)} problems')
    print(f'Generation method: V4 heuristics (Claude API as next step)')
    print('='*80)
    print()
    
    # Generate
    gen = ProofGeneratorV4Heuristic()
    proofs = gen.batch_generate(problems)
    
    # Statistics
    zero_sorry = sum(1 for p in proofs if p['sorry_count'] == 0)
    one_sorry = sum(1 for p in proofs if p['sorry_count'] == 1)
    two_plus_sorry = sum(1 for p in proofs if p['sorry_count'] >= 2)
    
    print()
    print('='*80)
    print('PHASE E SUMMARY')
    print('='*80)
    print(f'Total proofs:      {len(proofs)}')
    print(f'Zero sorry:        {zero_sorry}/{len(proofs)} ({100*zero_sorry/len(proofs):.0f}%)')
    print(f'One sorry:         {one_sorry}/{len(proofs)} ({100*one_sorry/len(proofs):.0f}%)')
    print(f'Two+ sorry:        {two_plus_sorry}/{len(proofs)} ({100*two_plus_sorry/len(proofs):.0f}%)')
    print(f'Avg sorry/proof:   {sum(p["sorry_count"] for p in proofs)/len(proofs):.1f}')
    print()
    
    # Save results
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    output_file = results_dir / "pipeline_phase_e_v4_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "phase": "E",
            "timestamp": datetime.now().isoformat(),
            "method": "v4-heuristic",
            "note": "Claude API integration planned for Phase E.5",
            "results": proofs
        }, f, indent=2, ensure_ascii=False)
    
    print(f'Results saved to: {output_file}')
    
    return proofs

if __name__ == "__main__":
    try:
        proofs = run_phase_e_v4(subset_size=10)
        
        # Print sample
        if proofs:
            print()
            print('='*80)
            print(f'SAMPLE: {proofs[0]["problem_id"]}')
            print('='*80)
            print(f'Sorry count: {proofs[0]["sorry_count"]}')
            print(f'Generation: {proofs[0]["generation_method"]}')
            print(f'Confidence: {proofs[0]["confidence"]:.2f}')
            print(f'\nLean Code (first 200 chars):')
            code = proofs[0]['lean_code']
            print(code[:200] + '...' if len(code) > 200 else code)
    
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
