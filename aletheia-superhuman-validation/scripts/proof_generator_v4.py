"""
Proof Generator V4: LLM-integrated proof generation.

Replaces heuristics with Claude API for semantic understanding.
Uses improved V4 templates based on Phase D audit.
"""

import os
import json
from enum import Enum
from typing import NamedTuple, List, Optional
from pathlib import Path
import anthropic

from proof_templates_v4 import ProofDomain, get_llm_prompt_v4

class LLMProvider(Enum):
    """LLM providers for proof generation."""
    CLAUDE = "claude-3-5-sonnet-20241022"  # Latest Claude model
    CLAUDE_OPUS = "claude-3-opus-20250219"
    FALLBACK = "heuristic"

class ImprovedProofV4(NamedTuple):
    """Improved proof with LLM generation details."""
    problem_id: str
    domain: str
    statement: str
    lean_code: str
    sorry_count: int
    llm_model: str
    llm_tokens_used: int
    generation_method: str  # "claude", "fallback"
    confidence: float
    reasoning: str  # LLM's explanation

class ProofGeneratorV4:
    """Generate proofs using Claude API with V4 templates."""
    
    def __init__(self, model: LLMProvider = LLMProvider.CLAUDE):
        self.model = model
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model_id = model.value
        
    def generate_proof(self, problem_id: str, domain: str, statement: str) -> ImprovedProofV4:
        """Generate a proof using Claude API."""
        
        try:
            # Get domain enum
            try:
                domain_enum = ProofDomain[domain.upper()]
            except KeyError:
                domain_enum = ProofDomain.LOGIC
            
            # Get LLM prompt
            prompt = get_llm_prompt_v4(domain_enum, statement)
            
            # Call Claude API
            print(f"  [LLM] Generating proof for {problem_id}...", end="", flush=True)
            message = self.client.messages.create(
                model=self.model_id,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )
            
            # Extract response
            response_text = message.content[0].text
            usage = message.usage
            
            print(f" OK ({usage.output_tokens} tokens)")
            
            # Parse Lean code from response
            lean_code = self._extract_lean_code(response_text)
            sorry_count = lean_code.count("sorry")
            
            # Extract reasoning (first 200 chars of response)
            reasoning = response_text.split("```")[0].strip()[:200] if "```" in response_text else response_text[:200]
            
            return ImprovedProofV4(
                problem_id=problem_id,
                domain=domain,
                statement=statement,
                lean_code=lean_code,
                sorry_count=sorry_count,
                llm_model=self.model_id,
                llm_tokens_used=usage.output_tokens,
                generation_method="claude",
                confidence=0.85 if sorry_count == 0 else 0.7 if sorry_count == 1 else 0.5,
                reasoning=reasoning,
            )
            
        except Exception as e:
            print(f"  [LLM] Error: {e}")
            # Fall back to V3 heuristic
            from proof_generator_v3 import ProofGeneratorV3
            gen_v3 = ProofGeneratorV3(llm_provider=LLMProvider.FALLBACK)
            proof_v3 = gen_v3.generate_proof(problem_id, domain, statement)
            
            # Wrap V3 result as V4
            return ImprovedProofV4(
                problem_id=proof_v3.problem_id,
                domain=proof_v3.domain,
                statement=proof_v3.statement,
                lean_code=proof_v3.lean_code,
                sorry_count=proof_v3.sorry_count,
                llm_model="fallback-v3",
                llm_tokens_used=0,
                generation_method="fallback",
                confidence=proof_v3.confidence,
                reasoning="Fallback to heuristic (V3)",
            )
    
    def _extract_lean_code(self, response: str) -> str:
        """Extract Lean code from LLM response."""
        # Find code block
        if "```lean" in response:
            start = response.find("```lean") + len("```lean")
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            if end > start:
                return response[start:end].strip()
        
        # No code block found, return response as-is (may contain Lean code)
        return response.strip()
    
    def batch_generate(self, problems: List[dict]) -> List[ImprovedProofV4]:
        """Generate proofs for multiple problems."""
        results = []
        for i, problem in enumerate(problems, 1):
            print(f"[{i}/{len(problems)}] {problem['problem_id']}...", end=" ")
            proof = self.generate_proof(
                problem_id=problem['problem_id'],
                domain=problem['domain'],
                statement=problem['statement'],
            )
            results.append(proof)
        return results

def run_phase_e_v4(problems_file: str = "data/selected_problems_phase_a.json") -> List[dict]:
    """Run Phase E.4 with V4 LLM-based generation."""
    
    # Load problems
    problems_path = Path(problems_file)
    if not problems_path.exists():
        raise FileNotFoundError(f"Problems file not found: {problems_file}")
    
    with open(problems_path, encoding='utf-8') as f:
        data = json.load(f)
        problems = data.get('selected_problems', [])[:3]  # Test with 3 problems first
    
    print(f"\n{'='*80}")
    print("PHASE E.4: Proof Generation with Claude LLM (V4)")
    print(f"{'='*80}")
    print(f"Selected {len(problems)} problems for testing\n")
    
    # Generate proofs
    generator = ProofGeneratorV4(model=LLMProvider.CLAUDE)
    proofs = generator.batch_generate(problems)
    
    # Summarize
    print(f"\n{'='*80}")
    print("PHASE E.4 SUMMARY")
    print(f"{'='*80}")
    print(f"Total:        {len(proofs)}")
    print(f"LLM success:  {sum(1 for p in proofs if p.generation_method == 'claude')}/{ len(proofs)}")
    print(f"Zero-sorry:   {sum(1 for p in proofs if p.sorry_count == 0)}/{len(proofs)}")
    print(f"Avg tokens:   {sum(p.llm_tokens_used for p in proofs) / len(proofs):.0f}")
    
    # Save results
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)
    
    output_file = results_dir / "pipeline_phase_e_v4_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "phase": "E.4",
            "model": LLMProvider.CLAUDE.value,
            "templates": "v4",
            "results": [
                {
                    "problem_id": p.problem_id,
                    "domain": p.domain,
                    "statement": p.statement,
                    "lean_code": p.lean_code,
                    "sorry_count": p.sorry_count,
                    "llm_model": p.llm_model,
                    "llm_tokens_used": p.llm_tokens_used,
                    "generation_method": p.generation_method,
                    "confidence": p.confidence,
                    "reasoning": p.reasoning,
                }
                for p in proofs
            ]
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}")
    
    return proofs

if __name__ == "__main__":
    proofs = run_phase_e_v4()
    
    # Print sample
    if proofs:
        print(f"\n{'='*80}")
        print(f"SAMPLE PROOF: {proofs[0].problem_id}")
        print(f"{'='*80}")
        print(f"Reasoning: {proofs[0].reasoning}")
        print(f"\nLean Code (sorry_count={proofs[0].sorry_count}):")
        print(proofs[0].lean_code[:300] + "..." if len(proofs[0].lean_code) > 300 else proofs[0].lean_code)
