"""
IMO Benchmark Adapter
Integrate Aletheia V7 with Google DeepMind's IMO-ProofBench v2

Loads real proof problems from IMO-ProofBench, assesses with V7 Verifier,
and validates scoring against expected difficulty levels.

CSV Format (IMO ProofBench v2):
- Problem ID: PB-{Level}-NNN
- Problem: LaTeX theorem statement
- Solution: Proof text
- Grading guidelines: Evaluation criteria
- Category: {geometry, combinatorics, number_theory, algebra}
- Level: {Basic (1-3), Intermediate (4-5), Advanced (6)}
- Short Answer: Answer (if applicable)
- Source: IMO year/problem

Mapping to Aletheia domains:
- geometry → analysis (geometric proofs are complex)
- combinatorics → algebra (combinatorial logic)
- number_theory → number_theory
- algebra → algebra
- (other) → logic
"""

import csv
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class IMOProblem:
    """Represents a single IMO-ProofBench problem"""
    problem_id: str
    problem_statement: str
    solution: str
    grading_guidelines: str
    category: str
    level: str  # "Basic", "Intermediate", "Advanced"
    short_answer: Optional[str]
    source: str
    
    @property
    def difficulty_level(self) -> int:
        """Convert level string to numeric (1-6)"""
        level_map = {
            "Basic": 1,
            "Intermediate": 4,
            "Advanced": 6
        }
        # Extract base from level
        base = level_map.get(self.level.split()[0] if self.level else "Basic", 1)
        # If level contains number, use it
        if self.level and len(self.level) > 0:
            match = re.search(r'(\d+)', self.level)
            if match:
                return int(match.group(1))
        return base
    
    @property
    def aletheia_domain(self) -> str:
        """Map IMO category to Aletheia domain"""
        domain_map = {
            "geometry": "analysis",
            "combinatorics": "algebra",
            "number_theory": "number_theory",
            "algebra": "algebra",
            "inequality": "algebra",
            "discrete mathematics": "algebra"
        }
        category_lower = self.category.lower() if self.category else ""
        return domain_map.get(category_lower, "logic")
    
    def to_verifier_proof(self) -> Dict:
        """Convert to format for V7 Verifier"""
        return {
            "proof_id": self.problem_id,
            "text": self.solution,
            "domain": self.aletheia_domain,
            "metadata": {
                "imo_category": self.category,
                "imo_level": self.level,
                "difficulty": self.difficulty_level,
                "problem_statement": self.problem_statement,
                "source": self.source
            }
        }


class IMOBenchmarkAdapter:
    """Adapter for loading and validating against IMO-ProofBench"""
    
    def __init__(self):
        """Initialize adapter"""
        self.problems: List[IMOProblem] = []
        self.assessments: Dict[str, Dict] = {}
    
    def load_from_csv(self, csv_path: str) -> int:
        """
        Load problems from IMO-ProofBench CSV file
        
        Args:
            csv_path: Path to proofbench_v2.csv
        
        Returns:
            Number of problems loaded
        """
        self.problems = []
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    problem = IMOProblem(
                        problem_id=row.get('Problem ID', ''),
                        problem_statement=row.get('Problem', ''),
                        solution=row.get('Solution', ''),
                        grading_guidelines=row.get('Grading guidelines', ''),
                        category=row.get('Category', ''),
                        level=row.get('Level', ''),
                        short_answer=row.get('Short Answer'),
                        source=row.get('Source', '')
                    )
                    if problem.problem_id:
                        self.problems.append(problem)
        except FileNotFoundError:
            print(f"CSV file not found: {csv_path}")
            return 0
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return 0
        
        return len(self.problems)
    
    def load_from_url(self, url: str = "https://raw.githubusercontent.com/google-deepmind/superhuman/main/imobench/proofbench_v2.csv") -> int:
        """
        Load problems directly from GitHub URL
        
        Args:
            url: GitHub raw content URL for proofbench_v2.csv
        
        Returns:
            Number of problems loaded
        """
        import urllib.request
        import io
        
        self.problems = []
        
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(content))
                
                for row in reader:
                    problem = IMOProblem(
                        problem_id=row.get('Problem ID', ''),
                        problem_statement=row.get('Problem', ''),
                        solution=row.get('Solution', ''),
                        grading_guidelines=row.get('Grading guidelines', ''),
                        category=row.get('Category', ''),
                        level=row.get('Level', ''),
                        short_answer=row.get('Short Answer'),
                        source=row.get('Source', '')
                    )
                    if problem.problem_id:
                        self.problems.append(problem)
        except Exception as e:
            print(f"Error loading from URL: {e}")
            return 0
        
        return len(self.problems)
    
    def get_problems_by_level(self, level: str) -> List[IMOProblem]:
        """
        Get problems filtered by difficulty level
        
        Args:
            level: "Basic", "Intermediate", or "Advanced"
        
        Returns:
            List of matching problems
        """
        return [p for p in self.problems if p.level == level]
    
    def get_problems_by_category(self, category: str) -> List[IMOProblem]:
        """
        Get problems filtered by category
        
        Args:
            category: "geometry", "algebra", "number_theory", "combinatorics"
        
        Returns:
            List of matching problems
        """
        return [p for p in self.problems if p.category.lower() == category.lower()]
    
    def get_problems_by_domain(self, domain: str) -> List[IMOProblem]:
        """
        Get problems filtered by Aletheia domain
        
        Args:
            domain: "algebra", "logic", "analysis", "number_theory"
        
        Returns:
            List of matching problems
        """
        return [p for p in self.problems if p.aletheia_domain == domain]
    
    def sample_problems(self, n: int = 5, level: Optional[str] = None) -> List[IMOProblem]:
        """
        Sample n problems, optionally filtered by level
        
        Args:
            n: Number of problems to sample
            level: Optional level filter
        
        Returns:
            List of sampled problems
        """
        candidates = self.get_problems_by_level(level) if level else self.problems
        
        if n > len(candidates):
            return candidates
        
        # Simple stratified sampling
        import random
        return random.sample(candidates, min(n, len(candidates)))
    
    def record_assessment(self, proof_id: str, assessment: Dict):
        """
        Record V7 assessment result
        
        Args:
            proof_id: IMO problem ID
            assessment: Assessment dict from V7 Verifier
        """
        self.assessments[proof_id] = assessment
    
    def get_assessment(self, proof_id: str) -> Optional[Dict]:
        """Get recorded assessment for a problem"""
        return self.assessments.get(proof_id)
    
    def get_summary_statistics(self) -> Dict:
        """
        Compute summary statistics from loaded problems
        
        Returns:
            Dict with counts by level, category, domain
        """
        if not self.problems:
            return {}
        
        by_level = {}
        by_category = {}
        by_domain = {}
        
        for p in self.problems:
            by_level[p.level] = by_level.get(p.level, 0) + 1
            by_category[p.category] = by_category.get(p.category, 0) + 1
            by_domain[p.aletheia_domain] = by_domain.get(p.aletheia_domain, 0) + 1
        
        return {
            "total_problems": len(self.problems),
            "by_level": by_level,
            "by_category": by_category,
            "by_domain": by_domain,
            "avg_problem_length": sum(len(p.problem_statement) for p in self.problems) / len(self.problems),
            "avg_solution_length": sum(len(p.solution) for p in self.problems) / len(self.problems)
        }
    
    def get_assessment_stats(self) -> Dict:
        """
        Compute statistics from assessments
        
        Returns:
            Dict with avg scores by level/category
        """
        if not self.assessments:
            return {}
        
        stats_by_level = {}
        stats_by_category = {}
        
        for proof_id, assessment in self.assessments.items():
            # Find matching problem
            problem = next((p for p in self.problems if p.problem_id == proof_id), None)
            if not problem:
                continue
            
            score = assessment.get('overall_d11_score', 0)
            
            # Group by level
            level = problem.level
            if level not in stats_by_level:
                stats_by_level[level] = []
            stats_by_level[level].append(score)
            
            # Group by category
            category = problem.category
            if category not in stats_by_category:
                stats_by_category[category] = []
            stats_by_category[category].append(score)
        
        # Compute averages
        result = {
            "total_assessed": len(self.assessments),
            "by_level": {},
            "by_category": {}
        }
        
        for level, scores in stats_by_level.items():
            result["by_level"][level] = {
                "count": len(scores),
                "avg_score": sum(scores) / len(scores),
                "min_score": min(scores),
                "max_score": max(scores)
            }
        
        for category, scores in stats_by_category.items():
            result["by_category"][category] = {
                "count": len(scores),
                "avg_score": sum(scores) / len(scores),
                "min_score": min(scores),
                "max_score": max(scores)
            }
        
        return result
    
    def export_assessments_to_json(self, output_path: str):
        """Exportar avaliações e estatísticas para JSON"""
        import json
        from enum import Enum
        
        # Converter Enums para strings
        def enum_converter(obj):
            if isinstance(obj, Enum):
                return obj.name
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        export_data = {
            "benchmark": "IMO-ProofBench v2",
            "total_assessed": len(self.assessments),
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "assessments": self.assessments,
            "statistics": self.get_assessment_stats()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=enum_converter)
