"""
pipeline_phase_c_v3.py - Phase C V3: Verificar provas V3 com Lean

Carrega resultados de Phase B V3 e verifica com Lean 4.
Espera melhor performance que Phase C V1 (0/10).
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, NamedTuple
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).parent))
from lean_verifier import LeanVerifier


class VerificationResult(NamedTuple):
    """Resultado de verificacao"""
    problem_id: str
    status: str  # success, partial, failed
    duration_sec: float
    output: str = ""
    error: str = ""


class PhaseCPipeline:
    """Orquestrador Phase C V3"""
    
    def __init__(
        self,
        results_dir: str = "results",
        lean_path: str = r"C:\Users\marce\Downloads\lean-4.30.0-windows\lean-4.30.0-windows\bin\lean.exe"
    ):
        self.results_dir = Path(results_dir)
        self.verifier = LeanVerifier(lean_path=lean_path)
    
    def load_phase_b_v3_results(self) -> List[Dict]:
        """Carrega resultados de Phase B V3"""
        phase_b_file = self.results_dir / "pipeline_phase_b_v3_results.json"
        
        if not phase_b_file.exists():
            raise FileNotFoundError(f"Phase B V3 results not found: {phase_b_file}")
        
        with open(phase_b_file, encoding='utf-8') as f:
            data = json.load(f)
        
        return data['results']
    
    def run(self):
        """Executa Phase C V3"""
        
        print("\n" + "="*80)
        print("PHASE C V3: LEAN VERIFICATION (V3 Proofs)")
        print("="*80)
        print(f"Lean Timeout: {self.verifier.timeout}s")
        
        start_time = datetime.utcnow().isoformat()
        print(f"Start: {start_time}\n")
        
        # Carregar provas
        proofs_b_v3 = self.load_phase_b_v3_results()
        print(f"Verifying {len(proofs_b_v3)} proofs...\n")
        
        # Verificar cada prova
        results = []
        success_count = 0
        partial_count = 0
        failed_count = 0
        
        for i, proof in enumerate(proofs_b_v3, 1):
            problem_id = proof['problem_id']
            print(f"[{i}/{len(proofs_b_v3)}] {problem_id}...", end="", flush=True)
            
            try:
                result = self.verifier.verify_code(problem_id, proof['lean_code'])
                results.append({
                    'problem_id': problem_id,
                    'status': result.status,
                    'duration_sec': result.duration_sec,
                    'sorry_count': proof.get('sorry_count', -1)
                })
                
                if result.status == 'success':
                    success_count += 1
                    print(f" SUCCESS ({result.duration_sec:.2f}s)")
                elif result.status == 'partial':
                    partial_count += 1
                    print(f" PARTIAL ({result.duration_sec:.2f}s)")
                else:
                    failed_count += 1
                    print(f" FAILED ({result.duration_sec:.2f}s)")
            
            except Exception as e:
                failed_count += 1
                print(f" ERROR ({str(e)[:30]})")
                results.append({
                    'problem_id': problem_id,
                    'status': 'failed',
                    'duration_sec': 0,
                    'error': str(e)
                })
        
        # Salvar e resumir
        self._save_results(results, start_time)
        self._print_summary(results, success_count, partial_count, failed_count)
    
    def _save_results(self, results: List[Dict], start_time: str):
        """Salva resultados em JSON"""
        
        end_time = datetime.utcnow().isoformat()
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        duration = (end_dt - start_dt).total_seconds()
        
        output = {
            'metadata': {
                'phase': 'C_V3',
                'verifier': 'Lean 4',
                'lean_timeout_sec': self.verifier.timeout,
                'total_proofs': len(results),
                'start_time': start_time,
                'end_time': end_time,
                'duration_sec': round(duration, 1)
            },
            'results': results
        }
        
        output_file = self.results_dir / "pipeline_phase_c_v3_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"OK Phase C V3 results saved: {output_file}\n")
    
    def _print_summary(self, results: List[Dict], success, partial, failed):
        """Imprime sumario"""
        
        print("="*80)
        print("PHASE C V3 SUMMARY")
        print("="*80)
        
        total = len(results)
        print(f"\nTotal:      {total}")
        print(f"Success:    {success:2d} ({100*success/total if total > 0 else 0:.1f}%)")
        print(f"Partial:    {partial:2d} ({100*partial/total if total > 0 else 0:.1f}%)")
        print(f"Failed:     {failed:2d} ({100*failed/total if total > 0 else 0:.1f}%)")
        
        # Tempo medio
        durations = [r['duration_sec'] for r in results if r['duration_sec'] > 0]
        if durations:
            avg_duration = sum(durations) / len(durations)
            print(f"Avg Duration: {avg_duration:.2f}s")
        
        # Tabela
        print(f"\nStatus table:")
        print(f"{'Problem':<10} {'Status':<10} {'Duration':<10} {'Sorry':<6}")
        print("-" * 40)
        for r in results:
            sorry = r.get('sorry_count', -1)
            sorry_str = str(sorry) if sorry >= 0 else "N/A"
            print(f"{r['problem_id']:<10} {r['status']:<10} {r['duration_sec']:<10.2f} {sorry_str:<6}")
        
        # Comparacao v1 vs v3
        print(f"\n" + "="*80)
        print("COMPARISON: V1 vs V3")
        print("="*80)
        print(f"\nPhase C V1 Results: 0 success, 0 partial, 10 failed")
        print(f"Phase C V3 Results: {success} success, {partial} partial, {failed} failed")
        print(f"\nImprovement: +{success} successes vs V1")
        
        print("\n" + "="*80 + "\n")


def main():
    """Ponto de entrada"""
    pipeline = PhaseCPipeline(results_dir="results")
    pipeline.run()


if __name__ == "__main__":
    main()
