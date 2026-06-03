#!/usr/bin/env python3
"""
Phase B Quick Run - Teste rápido com ProofGeneratorV2 em 5 problemas
"""

import json
import logging
from pathlib import Path
from proof_generator_v2 import ProofGeneratorV2
from dataclasses import asdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(message)s'
)
logger = logging.getLogger("phase_b_quick")

# Problemas selecionados (top 5)
PROBLEMS = [
    {
        "id": "A0004",
        "statement": "Let a=(a₁,a₂,a₃), b=(b₁,b₂,b₃). a <₂ b if aᵢ < bᵢ for ≥2 coordinates. How many chains a₁ <₂ a₂ <₂ ... of length k?",
        "domain": "combinatorics"
    },
    {
        "id": "B0014",
        "statement": "Does series ∑(2/3 + 1/3 sin n)ⁿ/n converge?",
        "domain": "analysis"
    },
    {
        "id": "B0017",
        "statement": "For K real number field, for ε>0, ∃ lacunary sequence (tₙ) with |p(tₙ)| < ε for all p∈Z[x], deg(p)≤d.",
        "domain": "number_theory"
    },
    {
        "id": "E0019",
        "statement": "Let dᵢ = |Bᵢ∩Bᵢ₊₁|. Minimize ∑dᵢ over all covering the plane by 3-colorings.",
        "domain": "combinatorics"
    },
    {
        "id": "E0020",
        "statement": "Construct point set in plane with no empty or full triangles of size k.",
        "domain": "geometry"
    }
]

def main():
    generator = ProofGeneratorV2()
    results_dir = Path("results/phase_b_quick")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("\n" + "="*70)
    logger.info("PHASE B QUICK RUN (5 problemas)")
    logger.info("="*70)
    
    candidates = []
    
    for problem in PROBLEMS:
        logger.info(f"\nProcessando: {problem['id']}")
        
        try:
            candidate = generator.generate(
                problem_id=problem['id'],
                statement=problem['statement'],
                domain=problem['domain'],
                max_tokens=1500
            )
            
            if candidate:
                candidates.append(candidate)
                
                # Salvar
                output_file = results_dir / f"{problem['id']}_candidate.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(candidate), f, indent=2, ensure_ascii=False)
                
                logger.info(f"✓ Salvo: {output_file}")
        
        except Exception as e:
            logger.error(f"✗ Erro: {e}")
    
    # Relatório final
    logger.info("\n" + "="*70)
    logger.info(f"SUMMARY: {len(candidates)}/5 provas geradas")
    logger.info("="*70)
    
    for c in candidates:
        logger.info(f"  {c.problem_id}: confiança={c.confidence:.0%}, template={c.template_used}")

if __name__ == "__main__":
    main()
