#!/usr/bin/env python3
"""
Manual review of Phase B proof candidates.
Analyzes the 3 generated proofs and identifies improvement areas.
"""

import sys
import io
import json
from pathlib import Path
from typing import Dict, List

# Force UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_candidate(candidate_data: Dict) -> Dict:
    """Analisar um proof candidate."""
    analysis = {
        "problem_id": candidate_data["problem_id"],
        "domain": candidate_data["domain"],
        "confidence": candidate_data["confidence"],
        "statement_length": len(candidate_data["statement"]),
        "natural_proof_length": len(candidate_data["natural_proof"]),
        "lean_code_length": len(candidate_data["lean_code"]),
        "issues": [],
        "suggestions": []
    }
    
    # Check for generic placeholder text
    if "Consideramos os casos principais" in candidate_data["natural_proof"]:
        analysis["issues"].append("Natural proof é genérica (placeholder)")
        analysis["suggestions"].append("Refinar prova natural com análise específica do problema")
    
    # Check for incomplete Lean code
    if "sorry" in candidate_data["lean_code"]:
        analysis["issues"].append("Lean code contém 'sorry' (prova incompleta)")
        analysis["suggestions"].append("Expandir Lean code com tácticas específicas")
    
    if "∀ x, P x" in candidate_data["lean_code"]:
        analysis["issues"].append("Lean code usa placeholders de proposição")
        analysis["suggestions"].append("Substituir P x por proposição real do problema")
    
    # Check confidence level
    if candidate_data["confidence"] < 0.7:
        analysis["issues"].append(f"Confidence baixa ({candidate_data['confidence']*100:.0f}%)")
        analysis["suggestions"].append("Aumentar iterações de refinamento ou melhorar few-shot examples")
    
    return analysis

def main():
    """Main review."""
    candidates_dir = Path("results/proof_candidates")
    
    print("=" * 80)
    print("MANUAL REVIEW OF PHASE B PROOF CANDIDATES")
    print("=" * 80)
    
    analyses = []
    
    for proof_file in sorted(candidates_dir.glob("*_proof.json")):
        with open(proof_file, "r", encoding='utf-8') as f:
            candidate_data = json.load(f)
        
        analysis = analyze_candidate(candidate_data)
        analyses.append(analysis)
        
        print(f"\n\n### PROBLEM: {analysis['problem_id']} ({analysis['domain']})")
        print(f"Confidence: {analysis['confidence']*100:.0f}%")
        print(f"Statement length: {analysis['statement_length']} chars")
        print(f"Natural proof length: {analysis['natural_proof_length']} chars")
        print(f"Lean code length: {analysis['lean_code_length']} chars")
        
        if analysis['issues']:
            print(f"\n⚠️  ISSUES:")
            for issue in analysis['issues']:
                print(f"  - {issue}")
        
        if analysis['suggestions']:
            print(f"\n💡 SUGGESTIONS:")
            for suggestion in analysis['suggestions']:
                print(f"  - {suggestion}")
        
        # Print snippet
        print(f"\n📝 Statement snippet:")
        print(f"  {candidate_data['statement'][:150]}...")
        
        print(f"\n🔍 Natural proof:")
        print(f"  {candidate_data['natural_proof']}")
        
        print(f"\n💻 Lean code:")
        print(f"  {candidate_data['lean_code']}")
    
    # Summary
    print("\n\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total_issues = sum(len(a['issues']) for a in analyses)
    total_suggestions = sum(len(a['suggestions']) for a in analyses)
    
    print(f"Total candidates reviewed: {len(analyses)}")
    print(f"Total issues found: {total_issues}")
    print(f"Total suggestions: {total_suggestions}")
    
    print("\n\nRECOMMENDATIONS FOR IMPROVEMENT:")
    print("1. Aumentar número de few-shot examples no ProofGeneratorOpenCode")
    print("2. Implementar domain-specific proof templates (number theory, analysis, etc)")
    print("3. Adicionar iteração refinement que analisa statement e gera prova mais específica")
    print("4. Usar formalizador para extrair proposições exatas antes de gerar Lean code")
    print("5. Implementar verificação léxica básica (check se Lean code compila sintaticamente)")

if __name__ == "__main__":
    main()
