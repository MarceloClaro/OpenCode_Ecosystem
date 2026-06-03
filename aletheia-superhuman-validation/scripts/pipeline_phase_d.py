"""
pipeline_phase_d.py - Phase D: Validacao Cientifica com PhD Auditor

Carrega 10 provas de Phase B e executa auditoria cientifica
com 7 verificadores em 10 dimensoes independentes.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys

# Importar PhD Auditor
sys.path.insert(0, str(Path(__file__).parent))
from phd_auditor import PhDAuditor, ProofAuditResult


class PhaseDPipeline:
    """Orquestrador de Phase D: Validacao Cientifica"""
    
    def __init__(self, results_dir: str = "results"):
        self.results_dir = Path(results_dir)
        self.auditor = PhDAuditor()
        self.results_dir.mkdir(exist_ok=True)
    
    def load_phase_b_results(self) -> List[Dict]:
        """Carrega resultados de Phase B"""
        phase_b_file = self.results_dir / "pipeline_phase_b_results.json"
        
        if not phase_b_file.exists():
            raise FileNotFoundError(f"Phase B results not found: {phase_b_file}")
        
        with open(phase_b_file) as f:
            data = json.load(f)
        
        return data['results']
    
    def run(self):
        """Executa Phase D completa"""
        
        print("\n" + "="*80)
        print("PHASE D: VALIDACAO CIENTIFICA (PhD Auditor)")
        print("="*80)
        
        start_time = datetime.utcnow().isoformat()
        print(f"\nStart: {start_time}\n")
        
        # Carregar provas de Phase B
        proofs_b = self.load_phase_b_results()
        print(f"Loaded {len(proofs_b)} proofs from Phase B\n")
        
        # Executar auditoria em cada prova
        audit_results = []
        
        for i, proof in enumerate(proofs_b, 1):
            problem_id = proof['problem_id']
            print(f"[{i}/{len(proofs_b)}] Auditing {problem_id}...", end="", flush=True)
            
            try:
                audit = self.auditor.audit_proof(
                    problem_id=proof['problem_id'],
                    domain=proof['domain'],
                    statement=proof['statement'],
                    lean_code=proof['lean_code'],
                    natural_proof=proof['natural_proof']
                )
                
                audit_results.append(audit)
                print(f" OK (score: {audit.overall_score:.1f}, tier: {audit.proof_quality_tier})")
            
            except Exception as e:
                print(f" FAILED ({str(e)[:50]})")
                audit_results.append(None)
        
        # Salvar resultados
        self._save_results(audit_results, start_time)
        
        # Mostrar sumario
        self._print_summary(audit_results)
    
    def _save_results(self, audits: List, start_time: str):
        """Salva resultados de auditoria em JSON"""
        
        end_time = datetime.utcnow().isoformat()
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
        duration = (end_dt - start_dt).total_seconds()
        
        # Preparar resultados para JSON
        audit_dicts = []
        for audit in audits:
            if audit is None:
                continue
            
            # Converter DimensionScore para dict
            dim_scores = {}
            for dim_name, dim_score in audit.dimension_scores.items():
                dim_scores[dim_name] = {
                    'avg_score': dim_score.avg_score,
                    'min_score': dim_score.min_score,
                    'max_score': dim_score.max_score,
                    'num_verifiers': dim_score.num_verifiers
                }
            
            audit_dict = {
                'problem_id': audit.problem_id,
                'domain': audit.domain,
                'statement': audit.statement,
                'overall_score': audit.overall_score,
                'tier': audit.proof_quality_tier,
                'confidence': audit.confidence,
                'dimension_scores': dim_scores,
                'strengths': audit.strengths,
                'weaknesses': audit.weaknesses,
                'recommendations': audit.recommendations,
                'timestamp': audit.timestamp
            }
            audit_dicts.append(audit_dict)
        
        # Salvar
        output = {
            'metadata': {
                'phase': 'D',
                'engine': 'PhD Auditor',
                'total_proofs': len([a for a in audits if a is not None]),
                'audited': len(audit_dicts),
                'failed': len([a for a in audits if a is None]),
                'start_time': start_time,
                'end_time': end_time,
                'duration_sec': round(duration, 1),
                'verifiers': 7,
                'dimensions': 10
            },
            'results': audit_dicts
        }
        
        output_file = Path(self.results_dir) / "pipeline_phase_d_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\nOK Results saved: {output_file}\n")
    
    def _print_summary(self, audits: List):
        """Imprime sumario dos resultados"""
        
        valid_audits = [a for a in audits if a is not None]
        
        if not valid_audits:
            print("No valid audits to summarize")
            return
        
        print("="*80)
        print("SUMMARY")
        print("="*80)
        
        # Estatisticas gerais
        scores = [a.overall_score for a in valid_audits]
        avg_score = sum(scores) / len(scores)
        
        tier_counts = {}
        for audit in valid_audits:
            tier = audit.proof_quality_tier
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        print(f"\nTotal audited:        {len(valid_audits)}")
        print(f"Average score:        {avg_score:.1f}/100")
        print(f"Min score:            {min(scores):.1f}")
        print(f"Max score:            {max(scores):.1f}")
        
        print(f"\nTier distribution:")
        for tier in ['A', 'B', 'C', 'D']:
            count = tier_counts.get(tier, 0)
            pct = 100 * count / len(valid_audits) if valid_audits else 0
            print(f"  {tier}: {count:2d} ({pct:5.1f}%)")
        
        # Dimensoes
        print(f"\nDimension scores (agregado):")
        
        dim_averages = {}
        for audit in valid_audits:
            for dim_name, dim_score in audit.dimension_scores.items():
                if dim_name not in dim_averages:
                    dim_averages[dim_name] = []
                dim_averages[dim_name].append(dim_score.avg_score)
        
        for dim_name in sorted(dim_averages.keys()):
            scores = dim_averages[dim_name]
            avg = sum(scores) / len(scores)
            print(f"  {dim_name:30s}: {avg:5.2f}/10")
        
        # Top 3 e Bottom 3
        print(f"\nTop 3 proofs:")
        sorted_audits = sorted(valid_audits, key=lambda a: a.overall_score, reverse=True)
        for audit in sorted_audits[:3]:
            print(f"  {audit.problem_id} ({audit.domain:15s}): {audit.overall_score:.1f} [{audit.proof_quality_tier}]")
        
        print(f"\nWeakest proofs:")
        for audit in sorted_audits[-3:]:
            print(f"  {audit.problem_id} ({audit.domain:15s}): {audit.overall_score:.1f} [{audit.proof_quality_tier}]")
        
        print("\n" + "="*80 + "\n")


def main():
    """Ponto de entrada"""
    pipeline = PhaseDPipeline(results_dir="results")
    pipeline.run()


if __name__ == "__main__":
    main()
