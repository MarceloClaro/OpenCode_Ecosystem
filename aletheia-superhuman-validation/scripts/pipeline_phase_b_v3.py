"""
pipeline_phase_b_v3.py - Phase B V3: Provas completas via heuristicas + LLM

Repete Phase B mas com ProofGeneratorV3:
  - Tenta completar provas (remove sorry)
  - Usa heuristicas por dominio se LLM nao disponivel
  - Re-verifica com Lean Phase C depois
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys

sys.path.insert(0, str(Path(__file__).parent))
from proof_generator_v3 import ProofGeneratorV3, LLMProvider


# 10 problemas selecionados
SELECTED_PROBLEMS = [
    {'id': 'A0004', 'domain': 'combinatorics', 'statement': 'For any finite set S with n elements, |P(S)| = 2^n'},
    {'id': 'B0014', 'domain': 'number_theory', 'statement': 'Every prime p > 2 is odd'},
    {'id': 'B0017', 'domain': 'analysis', 'statement': 'lim(n->inf) 1/n = 0'},
    {'id': 'E0019', 'domain': 'graph_theory', 'statement': 'A tree with n vertices has n-1 edges'},
    {'id': 'E0020', 'domain': 'geometry', 'statement': 'Sum of angles in a triangle is 180 degrees'},
    {'id': 'E0025', 'domain': 'induction', 'statement': 'sum(i, i=1..n) = n(n+1)/2'},
    {'id': 'E0030', 'domain': 'finite_case', 'statement': 'For finite set, |A ∪ B| <= |A| + |B|'},
    {'id': 'E0035', 'domain': 'algebra', 'statement': 'In a field, a*0 = 0'},
    {'id': 'E0038', 'domain': 'logic', 'statement': 'P ∨ ¬P (law of excluded middle)'},
    {'id': 'E0045', 'domain': 'category_theory', 'statement': 'Composition of functions is associative'},
]


class PhaseBV3Pipeline:
    """Orquestrador Phase B V3: Provas completas"""
    
    def __init__(
        self,
        results_dir: str = "results",
        llm_provider: LLMProvider = LLMProvider.FALLBACK,
        api_key: str = None
    ):
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        self.gen = ProofGeneratorV3(llm_provider=llm_provider, api_key=api_key)
        self.llm_provider = llm_provider
    
    def run(self):
        """Executa Phase B V3"""
        
        print("\n" + "="*80)
        print("PHASE B V3: PROOF GENERATION (with Heuristic Completion)")
        print("="*80)
        print(f"LLM Provider: {self.llm_provider.value}")
        print(f"Problems: {len(SELECTED_PROBLEMS)}")
        print(f"Output: {self.results_dir}\n")
        
        start_time = datetime.utcnow().isoformat()
        print(f"Start: {start_time}\n")
        
        # Gerar provas
        results = []
        generated_count = 0
        failed_count = 0
        
        for i, problem in enumerate(SELECTED_PROBLEMS, 1):
            problem_id = problem['id']
            print(f"[{i}/{len(SELECTED_PROBLEMS)}] Generating proof for {problem_id}...", end="", flush=True)
            
            try:
                candidate = self.gen.generate(
                    problem_id=problem['id'],
                    statement=problem['statement'],
                    domain=problem['domain']
                )
                
                results.append({
                    'problem_id': candidate.problem_id,
                    'domain': candidate.domain,
                    'statement': candidate.statement,
                    'lean_code': candidate.lean_code,
                    'natural_proof': candidate.natural_proof,
                    'confidence': candidate.confidence,
                    'template_used': candidate.template_used,
                    'llm_improved': candidate.llm_improved,
                    'sorry_count': candidate.sorry_count,
                    'source': candidate.source,
                    'timestamp': candidate.timestamp
                })
                
                generated_count += 1
                status = f"OK (sorry: {candidate.sorry_count}, src: {candidate.source[0:3]})"
                print(f" {status}")
            
            except Exception as e:
                failed_count += 1
                print(f" FAILED ({str(e)[:40]})")
                results.append({
                    'problem_id': problem['id'],
                    'domain': problem['domain'],
                    'error': str(e)
                })
        
        # Salvar
        self._save_results(results, start_time)
        self._print_summary(results)
    
    def _save_results(self, results: List[Dict], start_time: str):
        """Salva resultados em JSON"""
        
        end_time = datetime.utcnow().isoformat()
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        duration = (end_dt - start_dt).total_seconds()
        
        # Contar stats
        generated = sum(1 for r in results if 'error' not in r)
        failed = sum(1 for r in results if 'error' in r)
        
        output = {
            'metadata': {
                'phase': 'B_V3',
                'engine': 'ProofGeneratorV3 (Heuristic)',
                'llm_provider': self.llm_provider.value,
                'total_problems': len(SELECTED_PROBLEMS),
                'generated': generated,
                'failed': failed,
                'start_time': start_time,
                'end_time': end_time,
                'duration_sec': round(duration, 1),
            },
            'results': results
        }
        
        output_file = self.results_dir / "pipeline_phase_b_v3_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\nOK Results saved: {output_file}\n")
    
    def _print_summary(self, results: List[Dict]):
        """Imprime sumario"""
        
        valid_results = [r for r in results if 'error' not in r]
        
        print("="*80)
        print("SUMMARY")
        print("="*80)
        
        total = len(SELECTED_PROBLEMS)
        generated = len(valid_results)
        failed = total - generated
        success_rate = 100 * generated / total if total > 0 else 0
        
        print(f"Total:     {total}")
        print(f"Generated: {generated}")
        print(f"Failed:    {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Estatisticas de sorry
        if valid_results:
            sorry_counts = [r['sorry_count'] for r in valid_results if 'sorry_count' in r]
            if sorry_counts:
                total_sorry = sum(sorry_counts)
                avg_sorry = total_sorry / len(sorry_counts)
                zero_sorry = sum(1 for s in sorry_counts if s == 0)
                
                print(f"\nSorry statistics:")
                print(f"  Total sorry: {total_sorry}")
                print(f"  Avg/proof: {avg_sorry:.2f}")
                print(f"  Zero sorry: {zero_sorry}/{len(sorry_counts)}")
            
            # Source distribution
            sources = {}
            for r in valid_results:
                src = r.get('source', 'unknown')
                sources[src] = sources.get(src, 0) + 1
            
            print(f"\nSource distribution:")
            for src, count in sorted(sources.items()):
                pct = 100 * count / len(valid_results)
                print(f"  {src:20s}: {count:2d} ({pct:5.1f}%)")
            
            # Improved count
            improved = sum(1 for r in valid_results if r.get('llm_improved', False))
            print(f"\nLLM improved: {improved}/{len(valid_results)}")
        
        print("\n" + "="*80 + "\n")


def main():
    """Ponto de entrada"""
    pipeline = PhaseBV3Pipeline(
        results_dir="results",
        llm_provider=LLMProvider.FALLBACK
    )
    pipeline.run()


if __name__ == "__main__":
    main()
