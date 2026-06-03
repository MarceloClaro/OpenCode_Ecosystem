#!/usr/bin/env python3
"""
Parse 718 Lean files from formal-conjectures into structured JSON.

Stage 3 of Phase 1.1: Data Preparation

This script:
1. Walks raw_data/formal-conjectures/ directory
2. Extracts metadata from each .lean file:
   - filename
   - domain
   - imports
   - theorem/lemma declarations
3. Generates basic statement from Lean code
4. Outputs: data/erdos_718_enriched.json

Output format compatible with v1.0 SPEC processor.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent))


class LeanParser:
    """Parse Lean files and extract problem metadata."""

    def __init__(self):
        self.problems: List[Dict[str, Any]] = []
        self.domain_counts: Dict[str, int] = {}

    def parse_file(self, filepath: Path, domain: str) -> Optional[Dict[str, Any]]:
        """Parse a single .lean file."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            print(f"  ⚠️  Error reading {filepath}: {e}")
            return None

        # Extract imports
        imports = re.findall(r'^import\s+([\w.]+)', content, re.MULTILINE)

        # Extract theorem/lemma declarations
        theorem_match = re.search(
            r'(theorem|lemma|def)\s+(\w+)\s*[:\(]([^:={]*)',
            content
        )

        if not theorem_match:
            return None

        theorem_type = theorem_match.group(1)
        theorem_name = theorem_match.group(2)
        statement_hint = theorem_match.group(3).strip()

        # Build basic statement from Lean code
        statement = self._extract_statement(content, theorem_name)

        # Infer problem types from imports and content
        problem_types = self._infer_types(domain, imports, content)

        # Infer difficulty from code length and complexity
        difficulty = self._infer_difficulty(content)

        # Create problem object
        problem_id = f"{domain[0].upper()}{len(self.problems) + 1:04d}"

        return {
            "id": problem_id,
            "domain": domain,
            "filename": filepath.name,
            "filepath": str(filepath.relative_to(Path(__file__).parent / "raw_data" / "formal-conjectures")),
            "theorem_type": theorem_type,
            "theorem_name": theorem_name,
            "statement": statement,
            "types": problem_types,
            "difficulty": difficulty,
            "dependencies": imports,
            "enrichment": {
                "parsed": True,
                "statement_extracted": bool(statement),
                "hints": statement_hint[:100] if statement_hint else None,
            },
            "raw_lean_code": content[:500] + "..." if len(content) > 500 else content
        }

    def _extract_statement(self, content: str, theorem_name: str) -> str:
        """Extract natural language statement from Lean code."""
        # Try to find comments that describe the theorem
        comment_match = re.search(
            r'(?:--|/--)(.*?)(?=\n(?:theorem|lemma|def))',
            content,
            re.DOTALL
        )
        if comment_match:
            comment = comment_match.group(1).strip()
            # Clean up comment markers
            comment = re.sub(r'^--\s*', '', comment, flags=re.MULTILINE)
            comment = re.sub(r'^\s*-\s*', '', comment, flags=re.MULTILINE)
            return comment[:300]  # Limit to 300 chars

        # Fallback: use theorem name as statement
        return f"Theorem {theorem_name}: formalization of classical mathematical result"

    def _infer_types(self, domain: str, imports: List[str], content: str) -> List[str]:
        """Infer problem types from domain and imports."""
        types = []

        # Domain-based classification
        domain_map = {
            "ErdosProblems": ["combinatorics", "discrete_math", "graph_theory"],
            "Wikipedia": ["general", "mathematics"],
            "GreensOpenProblems": ["algebra", "number_theory"],
            "WrittenOnTheWallII": ["combinatorics", "algebra"],
            "Paper": ["theoretical", "formal_verification"],
            "OEIS": ["sequence", "integer_sequence"],
            "Mathoverflow": ["general", "research"],
            "Books": ["educational", "exercise"],
            "Other": ["general"],
            "Subsets": ["set_theory", "combinatorics"],
            "Millenium": ["difficult", "open_problem"],
            "OpenQuantumProblems": ["quantum", "physics"],
            "HilbertProblems": ["number_theory", "algebra"],
            "Kourovka": ["group_theory", "algebra"],
            "LittProblems": ["algebra", "ring_theory"],
            "OptimizationConstants": ["optimization", "analysis"],
            "Arxiv": ["research", "preprint"],
        }

        types.extend(domain_map.get(domain, ["general"]))

        # Import-based classification
        import_keywords = {
            "Finset": "combinatorics",
            "Graph": "graph_theory",
            "Nat": "number_theory",
            "Int": "integer_arithmetic",
            "Topology": "topology",
            "GroupTheory": "group_theory",
            "RingTheory": "ring_theory",
            "LinearAlgebra": "linear_algebra",
            "Geometry": "geometry",
            "Analysis": "real_analysis",
            "Probability": "probability",
        }

        for imp in imports:
            for keyword, itype in import_keywords.items():
                if keyword.lower() in imp.lower():
                    if itype not in types:
                        types.append(itype)

        return list(set(types))[:5]  # Return up to 5 distinct types

    def _infer_difficulty(self, content: str) -> str:
        """Infer difficulty from code length and complexity."""
        # Count lines of code
        lines = len(content.split('\n'))

        # Count proof tactics/keywords
        tactics = len(re.findall(r'\b(sorry|have|obtain|let|calc|simp|ring|norm_num)\b', content))

        # Simple heuristic
        if lines < 10 and tactics < 3:
            return "easy"
        elif lines < 30 and tactics < 10:
            return "medium"
        else:
            return "hard"

    def parse_directory(self, base_path: Path) -> None:
        """Recursively parse all .lean files in directory."""
        print(f"Parsing {base_path}...")

        for domain_dir in sorted(base_path.iterdir()):
            if not domain_dir.is_dir():
                continue

            domain = domain_dir.name
            self.domain_counts[domain] = 0

            # Find all .lean files
            lean_files = list(domain_dir.rglob("*.lean"))

            for filepath in sorted(lean_files):
                problem = self.parse_file(filepath, domain)
                if problem:
                    self.problems.append(problem)
                    self.domain_counts[domain] += 1

            if self.domain_counts[domain] > 0:
                print(f"  ✓ {domain}: {self.domain_counts[domain]} problems")

    def save_json(self, output_path: Path) -> None:
        """Save parsed problems to JSON."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "metadata": {
                "source": "google-deepmind/formal-conjectures",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0-enriched",
                "total_problems": len(self.problems),
                "domains": dict(sorted(self.domain_counts.items())),
                "raw_data_size_mb": 2.1,
                "notes": "Phase 1.1 Stage 3: Basic parsing + type inference"
            },
            "problems": self.problems
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved {len(self.problems)} problems to {output_path}")
        print(f"   File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")


def main():
    """Main execution."""
    script_dir = Path(__file__).parent
    raw_data_path = script_dir / "raw_data" / "formal-conjectures"
    output_json = script_dir / "data" / "erdos_718_enriched.json"

    if not raw_data_path.exists():
        print(f"❌ Error: {raw_data_path} not found")
        print("   Did you complete Stage 2 (extract)?")
        sys.exit(1)

    print("=" * 60)
    print("PHASE 1.1 STAGE 3: Parse Lean Files → JSON")
    print("=" * 60)
    print()

    parser = LeanParser()
    parser.parse_directory(raw_data_path)

    print()
    print(f"Summary:")
    print(f"  Total problems parsed: {len(parser.problems)}")
    print(f"  Total domains: {len(parser.domain_counts)}")

    parser.save_json(output_json)

    print()
    print("=" * 60)
    print("✅ Stage 3 Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
