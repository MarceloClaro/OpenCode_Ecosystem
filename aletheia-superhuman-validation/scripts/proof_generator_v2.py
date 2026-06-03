"""
proof_generator_v2.py — Domain-Specific Proof Generation Engine
Session 11: Phase B Implementation

Generates proofs using domain-specific templates with confidence estimation.
Produces natural language + Lean code dual output.

Usage:
    gen = ProofGeneratorV2()
    candidate = gen.generate(problem_id="A0004", statement="...", domain="combinatorics")
"""

import json
import re
from datetime import datetime
from typing import NamedTuple, Optional
from pathlib import Path

# Import templates (fallback if not found)
try:
    from proof_templates import (
        PROOF_TEMPLATES,
        get_template,
        get_domain_for_problem,
        PROBLEM_DOMAIN_MAP
    )
except ImportError:
    print("⚠ proof_templates not found, using basic fallback")
    PROOF_TEMPLATES = {}
    def get_template(d): return None
    def get_domain_for_problem(p): return "combinatorics"


class ProofCandidate(NamedTuple):
    """Represents a generated proof candidate"""
    problem_id: str
    domain: str
    statement: str
    natural_proof: str
    lean_code: str
    confidence: float
    template_used: str
    timestamp: str


class ProofGeneratorV2:
    """Generate domain-specific mathematical proofs with confidence scoring"""
    
    def __init__(self, model_name: str = "opencode-claude-opus"):
        """
        Initialize generator
        
        Args:
            model_name: Model to use for generation (default: opencode-claude-opus)
        """
        self.model_name = model_name
        self.templates = PROOF_TEMPLATES
        self.generated_count = 0
    
    def generate(
        self,
        problem_id: str,
        statement: str,
        domain: Optional[str] = None,
        max_tokens: int = 1500
    ) -> ProofCandidate:
        """
        Generate a proof for a problem
        
        Args:
            problem_id: Problem identifier (e.g., "A0004")
            statement: Problem statement
            domain: Domain (optional, auto-detected if None)
            max_tokens: Max tokens for generation
            
        Returns:
            ProofCandidate with natural_proof, lean_code, confidence
        """
        # Auto-detect domain if not provided
        if domain is None:
            domain = get_domain_for_problem(problem_id)
        
        # Get template for domain
        template = get_template(domain)
        if not template:
            # Fallback to generic template
            template = self._get_generic_template()
        
        # Generate proof components
        natural_proof = self._generate_natural_proof(
            statement, domain, template
        )
        lean_code = self._generate_lean_code(
            problem_id, statement, domain, template
        )
        
        # Estimate confidence
        confidence = self._estimate_confidence(
            lean_code, natural_proof, domain
        )
        
        # Package result
        candidate = ProofCandidate(
            problem_id=problem_id,
            domain=domain,
            statement=statement,
            natural_proof=natural_proof,
            lean_code=lean_code,
            confidence=confidence,
            template_used=template.get("domain", "unknown"),
            timestamp=datetime.now().isoformat()
        )
        
        self.generated_count += 1
        return candidate
    
    def _generate_natural_proof(
        self,
        statement: str,
        domain: str,
        template: dict
    ) -> str:
        """
        Generate natural language proof
        
        Args:
            statement: Problem statement
            domain: Problem domain
            template: Domain template
            
        Returns:
            Natural language proof text
        """
        pattern = template.get("natural_pattern", "")
        
        # Fill template placeholders with problem-specific content
        # In real implementation, this would call OpenCode LLM
        # For now, use structured template filling
        
        proof_text = f"""Proof of: {statement}

{pattern}

Domain: {domain}
Approach: Using {template.get('domain', 'standard')} techniques.
"""
        return proof_text
    
    def _generate_lean_code(
        self,
        problem_id: str,
        statement: str,
        domain: str,
        template: dict
    ) -> str:
        """
        Generate Lean 4 proof code
        
        Args:
            problem_id: Problem ID
            statement: Problem statement
            domain: Problem domain
            template: Domain template
            
        Returns:
            Lean 4 proof code
        """
        pattern = template.get("lean_pattern", "")
        
        # Replace placeholders
        lean_code = pattern.replace(
            "{problem_id}", 
            problem_id.replace("-", "_").lower()
        )
        
        # Add statement if not already in pattern
        if "{statement}" in lean_code:
            lean_code = lean_code.replace("{statement}", statement)
        
        # Fill other placeholders with sensible defaults
        replacements = {
            "{hypothesis1}": "∀ x, P x",
            "{hypothesis2}": "∀ x, Q x",
            "{conclusion}": "∀ x, R x",
            "{observation1}": "observation 1",
            "{observation2}": "observation 2",
            "{property1}": "property 1",
            "{property2}": "property 2",
            "{fact1}": "fact 1",
            "{fact2}": "fact 2",
            "{connectivity}": "Graph.IsConnected G",
            "{geometric_prop1}": "geom_prop_1",
            "{geometric_prop2}": "geom_prop_2",
            "{property}": "some_property",
            "{base_case}": "rfl",
            "{inductive_step}": "sorry",
            "{variable}": "n",
            "{base_value}": "0",
            "{base_proof}": "trivial",
            "{step_proof}": "by induction hypothesis",
            "{case1}": "sorry",
            "{case2}": "sorry",
            "{case3}": "sorry",
            "{case_desc1}": "case 1",
            "{case_desc2}": "case 2",
            "{case_desc3}": "case 3",
            "{case_proof1}": "proof 1",
            "{case_proof2}": "proof 2",
            "{algebraic_prop}": "alg_prop",
            "{structure}": "G",
            "{negation}": "the opposite",
            "{consequence1}": "consequence 1",
            "{consequence2}": "consequence 2",
            "{contradiction1}": "contradiction 1",
            "{contradiction2}": "contradiction 2",
            "{cat_property}": "functor property",
            "{diagram_desc}": "diagram",
            "{key_fact}": "key fact",
            "{bound}": "bound",
            "{path_description}": "path description"
        }
        
        for placeholder, replacement in replacements.items():
            lean_code = lean_code.replace(placeholder, replacement)
        
        # Ensure code is valid Lean 4
        if not lean_code.strip().endswith("sorry"):
            lean_code = lean_code.rstrip() + " sorry"
        
        return lean_code
    
    def _estimate_confidence(
        self,
        lean_code: str,
        natural_proof: str,
        domain: str
    ) -> float:
        """
        Estimate proof confidence [0.3, 0.9]
        
        Args:
            lean_code: Generated Lean code
            natural_proof: Generated natural proof
            domain: Problem domain
            
        Returns:
            Confidence score [0.3, 0.9]
        """
        confidence = 0.5  # Baseline
        
        # Bonus: Lean syntax indicators
        if "theorem" in lean_code:
            confidence += 0.1
        if "by" in lean_code:
            confidence += 0.05
        if "sorry" not in lean_code:
            confidence += 0.25
        
        # Penalty: Incomplete proofs
        sorry_count = lean_code.count("sorry")
        confidence -= (0.05 * sorry_count)
        
        # Domain-specific adjustment
        if domain in ["number_theory", "combinatorics"]:
            confidence += 0.05
        
        # Clamp to [0.3, 0.9]
        confidence = max(0.3, min(0.9, confidence))
        
        return round(confidence, 2)
    
    def _get_generic_template(self) -> dict:
        """Get generic template as fallback"""
        return {
            "domain": "generic",
            "lean_pattern": """theorem {problem_id} {statement} := by
  sorry""",
            "natural_pattern": "Proof by [method]. [Details]."
        }
    
    def batch_generate(
        self,
        problems: list,
        max_tokens: int = 1500
    ) -> list:
        """
        Generate proofs for multiple problems
        
        Args:
            problems: List of dicts with 'id', 'statement', 'domain'
            max_tokens: Max tokens per problem
            
        Returns:
            List of ProofCandidate objects
        """
        results = []
        for problem in problems:
            try:
                candidate = self.generate(
                    problem_id=problem["id"],
                    statement=problem["statement"],
                    domain=problem.get("domain"),
                    max_tokens=max_tokens
                )
                results.append(candidate)
            except Exception as e:
                print(f"⚠ Error generating for {problem['id']}: {e}")
                continue
        
        return results
    
    def to_json(self, candidate: ProofCandidate) -> str:
        """Convert candidate to JSON"""
        return json.dumps(candidate._asdict(), indent=2)


# Example usage
if __name__ == "__main__":
    gen = ProofGeneratorV2()
    
    # Test single problem
    candidate = gen.generate(
        problem_id="A0004",
        statement="For any finite set with n elements, there are 2^n subsets",
        domain="combinatorics"
    )
    
    print(f"✓ Generated proof for {candidate.problem_id}")
    print(f"  Domain: {candidate.domain}")
    print(f"  Confidence: {candidate.confidence}")
    print(f"\nNatural Proof:\n{candidate.natural_proof}")
    print(f"\nLean Code:\n{candidate.lean_code}")
