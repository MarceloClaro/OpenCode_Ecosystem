"""
Aletheia V7 Verifier Agent
Stage 2b: Proof Elegance & Pedagogical Clarity Assessment (D11)

Cora-Debate V7: D11 Verification for proof_elegance dimension
- Structural analysis: lemmas, cases, tactics
- Complexity metrics: lines, nesting, abstraction
- Pedagogical heuristics: teaching value, intuitiveness
- Result: D11 score (0-10) + reasoning

Integrates with Auditor Agent for D11 scoring
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum


class EleganceLevel(Enum):
    """Elegance assessment levels"""
    INELEGANT = 0.0      # 0-2: Dense, convoluted
    POOR = 1.0           # 2-4: Correct but unnecessarily complex
    ADEQUATE = 2.0       # 4-5: Adequate structure, somewhat verbose
    GOOD = 3.0           # 6-7: Clear structure, lacks pedagogical insight
    ELEGANT = 4.0        # 8: Elegant presentation with pedagogical value
    CANONICAL = 5.0      # 9-10: Canonical/elegant, teaches concepts


@dataclass
class ProofStructure:
    """Parsed structure of mathematical proof"""
    total_lines: int
    lemma_count: int
    case_count: int
    tactic_count: int
    nesting_depth: int
    avg_lemma_lines: float
    lemma_names: List[str] = field(default_factory=list)
    case_labels: List[str] = field(default_factory=list)
    tactic_types: List[str] = field(default_factory=list)
    
    def complexity_score(self) -> float:
        """Estimate structural complexity (0-1, lower is more elegant)"""
        if self.total_lines == 0:
            return 0.5
        
        # Factors that increase complexity:
        # - Deep nesting
        # - Many cases
        # - Short lemmas (fragmentation)
        # - Many simple tactics (verbosity)
        
        nesting_penalty = min(self.nesting_depth / 5.0, 1.0)
        fragmentation_penalty = max(0, 1.0 - (self.avg_lemma_lines / 15.0))
        verbosity_penalty = min(self.tactic_count / self.total_lines, 0.5)
        
        complexity = (nesting_penalty * 0.4 + 
                     fragmentation_penalty * 0.3 + 
                     verbosity_penalty * 0.3)
        return min(complexity, 1.0)
    
    def clarity_score(self) -> float:
        """Estimate structural clarity (0-1, higher is clearer)"""
        return 1.0 - self.complexity_score()


@dataclass
class PedagogicalAssessment:
    """Assessment of pedagogical value"""
    has_explicit_goal: bool
    has_key_insight: bool
    uses_standard_techniques: bool
    connects_to_theory: bool
    provides_examples: bool
    has_clear_progression: bool
    teaching_value_indicators: List[str] = field(default_factory=list)
    
    def pedagogical_score(self) -> float:
        """Estimate pedagogical value (0-1)"""
        indicators = sum([
            self.has_explicit_goal,
            self.has_key_insight,
            self.uses_standard_techniques,
            self.connects_to_theory,
            self.provides_examples,
            self.has_clear_progression
        ])
        return indicators / 6.0


@dataclass
class D11Assessment:
    """D11 Dimension Assessment Result"""
    proof_id: str
    domain: str
    structure: ProofStructure
    pedagogical: PedagogicalAssessment
    
    elegance_score: float  # 0-10
    pedagogical_clarity_score: float  # 0-10
    overall_d11_score: float  # 0-10 (weighted average)
    
    reasoning: str
    assessment_level: EleganceLevel
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        result = asdict(self)
        result['assessment_level'] = self.assessment_level.name
        return result


class VerifierV7:
    """V7 Verifier: Proof Elegance & Pedagogical Clarity Assessment"""
    
    def __init__(self):
        """Initialize V7 Verifier"""
        self.assessed_proofs = []
    
    def parse_proof_structure(self, proof_text: str) -> ProofStructure:
        """
        Parse proof text to extract structural metrics
        
        Analyzes:
        - Line count
        - Lemma/helper definitions
        - Case divisions
        - Tactic sequences
        - Nesting depth
        """
        lines = proof_text.split('\n')
        total_lines = len([l for l in lines if l.strip()])
        
        # Extract lemmas (look for "lemma", "theorem", "def" keywords)
        lemma_pattern = r'\b(lemma|theorem|def)\s+(\w+)'
        lemmas = re.findall(lemma_pattern, proof_text, re.IGNORECASE)
        lemma_count = len(lemmas)
        lemma_names = [name for _, name in lemmas]
        
        # Extract cases (look for "case", "·", "| ")
        case_pattern = r'(case|·|\|\s+)'
        cases = re.findall(case_pattern, proof_text)
        case_count = len([c for c in cases if c != ''])
        case_labels = [f"case_{i}" for i in range(case_count)]
        
        # Extract tactics (look for tactic keywords)
        tactic_pattern = r'\b(intro|cases|induction|simp|rw|exact|apply|sorry)\b'
        tactics = re.findall(tactic_pattern, proof_text, re.IGNORECASE)
        tactic_count = len(tactics)
        tactic_types = list(set(tactics))
        
        # Estimate nesting depth
        nesting_depth = self._estimate_nesting_depth(proof_text)
        
        # Average lemma lines
        avg_lemma_lines = total_lines / max(lemma_count, 1)
        
        return ProofStructure(
            total_lines=total_lines,
            lemma_count=lemma_count,
            case_count=case_count,
            tactic_count=tactic_count,
            nesting_depth=nesting_depth,
            avg_lemma_lines=avg_lemma_lines,
            lemma_names=lemma_names,
            case_labels=case_labels,
            tactic_types=tactic_types
        )
    
    def _estimate_nesting_depth(self, text: str) -> int:
        """Estimate nesting depth from indentation and bracket matching"""
        max_depth = 0
        current_depth = 0
        
        for char in text:
            if char in '([{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in ')]}':
                current_depth = max(0, current_depth - 1)
            elif char == '\n':
                # Count indentation level
                pass
        
        return max_depth
    
    def assess_pedagogical_value(self, proof_text: str, domain: str) -> PedagogicalAssessment:
        """
        Assess pedagogical value of proof
        
        Looks for:
        - Explicit statement of goal
        - Key insights or intuition
        - Use of standard techniques
        - Connection to broader theory
        - Examples or instantiations
        - Clear progression of ideas
        """
        
        # Look for explicit goal statements
        has_explicit_goal = bool(re.search(
            r'\b(goal|prove|show|demonstrate|verify)\b', 
            proof_text, 
            re.IGNORECASE
        ))
        
        # Look for insight markers
        has_key_insight = bool(re.search(
            r'\b(key idea|observation|note|remark|insight|intuition)\b', 
            proof_text, 
            re.IGNORECASE
        ))
        
        # Check for standard techniques
        standard_techniques = [
            'induction', 'contradiction', 'contrapositive', 
            'symmetry', 'transitivity', 'distributivity'
        ]
        uses_standard_techniques = any(
            technique in proof_text.lower() 
            for technique in standard_techniques
        )
        
        # Look for theory connections
        theory_keywords = [
            'theorem', 'corollary', 'lemma', 'property',
            'structure', 'axiom', 'definition'
        ]
        connects_to_theory = any(
            keyword in proof_text.lower() 
            for keyword in theory_keywords
        )
        
        # Look for examples
        provides_examples = bool(re.search(
            r'\b(example|instance|e\.g\.|for instance)\b', 
            proof_text, 
            re.IGNORECASE
        ))
        
        # Check progression (multiple lemmas suggest clear progression)
        lemma_count = len(re.findall(r'\blemma\b', proof_text, re.IGNORECASE))
        has_clear_progression = lemma_count >= 2
        
        # Compile teaching value indicators
        indicators = []
        if has_explicit_goal:
            indicators.append("explicit_goal")
        if has_key_insight:
            indicators.append("key_insight")
        if uses_standard_techniques:
            indicators.append("standard_techniques")
        if connects_to_theory:
            indicators.append("theory_connection")
        if provides_examples:
            indicators.append("examples")
        if has_clear_progression:
            indicators.append("clear_progression")
        
        return PedagogicalAssessment(
            has_explicit_goal=has_explicit_goal,
            has_key_insight=has_key_insight,
            uses_standard_techniques=uses_standard_techniques,
            connects_to_theory=connects_to_theory,
            provides_examples=provides_examples,
            has_clear_progression=has_clear_progression,
            teaching_value_indicators=indicators
        )
    
    def compute_elegance_score(self, structure: ProofStructure, domain: str) -> float:
        """
        Compute elegance score from structure metrics
        
        Elegance factors:
        - Simplicity (low complexity, few tactics)
        - Clarity (clear structure, not fragmented)
        - Appropriate abstraction (good lemma organization)
        - Domain-specific expectations
        """
        
        # Base score from clarity
        clarity = structure.clarity_score()  # 0-1
        
        # Efficiency: avoid unnecessary lemmas
        lemma_efficiency = 1.0 if structure.lemma_count == 0 else \
                          min(1.0, structure.avg_lemma_lines / 15.0)
        
        # Tactic conciseness
        if structure.total_lines > 0:
            tactic_ratio = structure.tactic_count / structure.total_lines
            conciseness = 1.0 - min(tactic_ratio, 0.5)
        else:
            conciseness = 0.5
        
        # Domain-specific adjustments
        domain_elegance_expectations = {
            "set_theory": 1.0,      # Simple sets are inherently elegant
            "logic": 1.0,            # Clean logical forms expected
            "algebra": 0.95,         # Algebraic structures can be dense
            "analysis": 0.85,        # Analysis proofs are often complex
            "number_theory": 0.9     # Number theory can be tricky
        }
        domain_factor = domain_elegance_expectations.get(domain, 1.0)
        
        # Combined elegance
        elegance = (clarity * 0.4 + 
                   lemma_efficiency * 0.3 + 
                   conciseness * 0.3) * domain_factor
        
        # Convert to 0-10 scale
        return elegance * 10.0
    
    def compute_pedagogical_score(self, ped_assess: PedagogicalAssessment) -> float:
        """
        Compute pedagogical clarity score from assessment
        
        Scale: 0-10
        """
        base_score = ped_assess.pedagogical_score()  # 0-1
        
        # Bonus for comprehensive teaching indicators
        indicator_count = len(ped_assess.teaching_value_indicators)
        indicator_bonus = min(indicator_count / 6.0, 0.3)
        
        pedagogical_score = (base_score + indicator_bonus) * 10.0
        return min(pedagogical_score, 10.0)
    
    def assess(self, proof: Dict) -> D11Assessment:
        """
        Main assessment method: Evaluate proof for D11 elegance & pedagogy
        
        Args:
            proof: Dict with keys:
                - proof_id: str
                - text: str (proof text)
                - domain: str (set_theory, algebra, logic, analysis, number_theory)
                - (optional) reasoning_types: List[str]
        
        Returns:
            D11Assessment with scores and reasoning
        """
        proof_id = proof.get("proof_id", "unknown")
        proof_text = proof.get("text", "")
        domain = proof.get("domain", "algebra")
        
        # Parse structure
        structure = self.parse_proof_structure(proof_text)
        
        # Assess pedagogy
        pedagogical = self.assess_pedagogical_value(proof_text, domain)
        
        # Compute scores
        elegance_score = self.compute_elegance_score(structure, domain)
        pedagogical_score = self.compute_pedagogical_score(pedagogical)
        
        # Overall D11 score (weighted average)
        overall_d11 = (elegance_score * 0.5 + pedagogical_score * 0.5)
        
        # Determine elegance level
        if overall_d11 >= 9.0:
            level = EleganceLevel.CANONICAL
        elif overall_d11 >= 8.0:
            level = EleganceLevel.ELEGANT
        elif overall_d11 >= 6.0:
            level = EleganceLevel.GOOD
        elif overall_d11 >= 4.0:
            level = EleganceLevel.ADEQUATE
        elif overall_d11 >= 2.0:
            level = EleganceLevel.POOR
        else:
            level = EleganceLevel.INELEGANT
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            structure, pedagogical, elegance_score, 
            pedagogical_score, domain
        )
        
        assessment = D11Assessment(
            proof_id=proof_id,
            domain=domain,
            structure=structure,
            pedagogical=pedagogical,
            elegance_score=elegance_score,
            pedagogical_clarity_score=pedagogical_score,
            overall_d11_score=overall_d11,
            reasoning=reasoning,
            assessment_level=level
        )
        
        self.assessed_proofs.append(assessment)
        return assessment
    
    def _generate_reasoning(
        self,
        structure: ProofStructure,
        ped: PedagogicalAssessment,
        elegance: float,
        pedagogy: float,
        domain: str
    ) -> str:
        """Generate human-readable reasoning for D11 score"""
        
        parts = []
        
        # Structure analysis
        if structure.complexity_score() < 0.3:
            parts.append("Simple, well-structured proof")
        elif structure.complexity_score() > 0.7:
            parts.append("Complex or deeply nested structure")
        else:
            parts.append("Moderate structural complexity")
        
        # Lemma organization
        if structure.lemma_count == 0:
            parts.append("Direct proof, no helper lemmas")
        elif structure.avg_lemma_lines >= 15:
            parts.append("Well-organized lemmas with substantial content")
        else:
            parts.append("Fragmented into many small lemmas")
        
        # Pedagogical indicators
        if len(ped.teaching_value_indicators) >= 5:
            parts.append("Strong pedagogical value")
        elif len(ped.teaching_value_indicators) >= 3:
            parts.append("Moderate pedagogical value")
        else:
            parts.append("Limited pedagogical structure")
        
        # Domain context
        domain_notes = {
            "set_theory": "Set theory proofs favor simplicity",
            "logic": "Logic proofs benefit from canonical forms",
            "algebra": "Algebraic proofs reward structural insight",
            "analysis": "Analysis proofs are inherently complex",
            "number_theory": "Number theory favors revealing structure"
        }
        if domain in domain_notes:
            parts.append(domain_notes[domain])
        
        return "; ".join(parts)
