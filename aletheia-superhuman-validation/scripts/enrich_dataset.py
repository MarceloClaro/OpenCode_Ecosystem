"""
enrich_dataset.py — Phase 1.1 Stage 4: NLP Enrichment
====================================================
Enhances erdos_718_enriched.json with:
1. Re-extraction of ALL theorems/lemmas/defs per .lean file
2. @[category ...] parsing (proof status + AMS codes)
3. Refined difficulty scoring (1-10 scale)
4. Domain-specific reasoning types
5. Problem archetype detection
6. Proof status (open/solved/textbook)
7. Formal proof links

Output: data/erdos_718_enriched_v1.1.json
"""

import json
import os
import re
import math
from collections import Counter, defaultdict

# ─── Configuration ───────────────────────────────────────────────────────────

RAW_DIR = "raw_data/formal-conjectures"
EXISTING_JSON = "data/erdos_718_enriched.json"
OUTPUT_JSON = "data/erdos_718_enriched_v1.1.json"

# ─── AMS Classification Mapping ──────────────────────────────────────────────

AMS_FIELDS = {
    "0":  "general",
    "1":  "history_biography",
    "3":  "mathematical_logic_foundations",
    "5":  "combinatorics",
    "6":  "order_lattices",
    "8":  "general_algebra",
    "11": "number_theory",
    "12": "field_theory_polynomials",
    "13": "commutative_rings_algebras",
    "14": "algebraic_geometry",
    "15": "linear_algebra_multilinear",
    "16": "associative_rings_algebras",
    "18": "category_theory_homological",
    "20": "group_theory_generalizations",
    "22": "topological_groups_lie",
    "26": "real_functions",
    "28": "measure_integration",
    "30": "functions_complex_analysis",
    "32": "several_complex_variables",
    "33": "special_functions",
    "34": "ordinary_differential_equations",
    "35": "partial_differential_equations",
    "37": "dynamical_systems_ergodic",
    "40": "sequences_series_summability",
    "41": "approximations_expansions",
    "42": "fourier_analysis",
    "46": "functional_analysis",
    "47": "operator_theory",
    "49": "calculus_of_variations",
    "51": "geometry",
    "52": "convex_discrete_geometry",
    "54": "general_topology",
    "55": "algebraic_topology",
    "57": "manifolds_cell_complexes",
    "58": "global_analysis_analysis_manifolds",
    "60": "probability_theory_stochastic",
    "68": "computer_science",
    "81": "quantum_theory",
    "91": "game_theory_economics",
    "94": "information_communication",
}

REASONING_BY_DOMAIN = {
    "ErdosProblems":      ["combinatorial", "extremal", "additive_combinatorics", "graph_theoretic"],
    "Wikipedia":          ["expository", "survey", "reference"],
    "GreensOpenProblems": ["analytic", "structural", "additive_combinatorics"],
    "WrittenOnTheWallII": ["combinatorial", "graph_theoretic", "existential"],
    "OEIS":               ["computational", "conjectural", "sequence_analysis"],
    "Paper":              ["applied", "specialized", "interdisciplinary"],
    "Arxiv":              ["research", "preprint", "theoretical"],
    "Mathoverflow":       ["community_driven", "cross_disciplinary"],
    "Books":              ["pedagogical", "reference", "classical"],
    "Millenium":          ["deep", "structural", "foundational"],
    "OpenQuantumProblems":["quantum", "information_theoretic", "physical"],
    "HilbertProblems":    ["foundational", "programmatic", "historical"],
    "Subsets":            ["combinatorial", "set_theoretic"],
    "LittProblems":       ["research", "open_ended"],
    "OptimizationConstants":["computational", "analytic"],
    "Other":              ["miscellaneous"],
}

ARCHETYPE_PATTERNS = [
    (r'exists?\s+\w+', 'existence'),
    (r'\bforall\b', 'universal'),
    (r'\bexists\b.*\bstrictly\b', 'existence_inequality'),
    (r'\bleast\b|\bminimal\b|\bminimum\b', 'minimality'),
    (r'\bgreatest\b|\bmaximal\b|\bmaximum\b', 'maximality'),
    (r'\bconjecture\b', 'conjecture'),
    (r'\btheorem\b', 'theorem_statement'),
    (r'\blemma\b', 'lemma'),
    (r'\binequality\b|\bleq\b|\bgeq\b|\b<\b|\b>\b', 'inequality'),
    (r'\bcontains?\b|\bsubseteq\b|\bsubset\b', 'containment'),
    (r'\bequal\b|\b=\b', 'equality'),
    (r'\bcard\b|\bcardinality\b|\b\|.*\|\b', 'cardinality'),
    (r'\binfinite\b|\bfinite\b', 'finiteness'),
    (r'\bprime\b', 'prime_property'),
    (r'\bsum\b|\bproduct\b|\bsum\b', 'sum_product'),
    (r'\bsquare\b|\bcube\b', 'power_property'),
    (r'\bgraph\b|\bedge\b|\bvertex\b', 'graph_property'),
    (r'\bapproximat\b|\basymptotic\b|\blimit\b', 'asymptotic'),
]


def parse_category_tag(content):
    """Extract @[category ...] annotations from Lean file content."""
    annotations = []
    pattern = re.compile(r'@\[category\s+([^\]]+)\]')
    for match in pattern.finditer(content):
        raw = match.group(1)
        # Parse components
        parts = [p.strip() for p in raw.split(',')]
        
        proof_status = "unknown"
        ams_codes = []
        formal_proofs = []
        
        for part in parts:
            part_lower = part.lower()
            if part_lower in ("research open", "open"):
                proof_status = "research_open"
            elif part_lower in ("research solved", "solved"):
                proof_status = "research_solved"
            elif part_lower in ("textbook",):
                proof_status = "textbook"
            elif part_lower in ("test",):
                proof_status = "test"
            elif part_lower in ("api",):
                proof_status = "api"
            elif part.startswith("AMS"):
                codes = part.replace("AMS", "").strip().split()
                ams_codes = [c.strip() for c in codes if c.strip().isdigit()]
            elif part.startswith("formal_proof using"):
                # Extract URL
                url_match = re.search(r'"(https?://[^"]+)"', part)
                if url_match:
                    formal_proofs.append(url_match.group(1))
        
        annotations.append({
            "raw": raw,
            "proof_status": proof_status,
            "ams_codes": ams_codes,
            "ams_fields": [AMS_FIELDS.get(c, f"unknown_ams_{c}") for c in ams_codes],
            "formal_proofs": formal_proofs,
        })
    return annotations


def extract_all_theorems(content, domain, filepath):
    """
    Extract ALL theorems/lemmas/definitions from a .lean file.
    Returns list of theorem dicts.
    """
    theorems = []
    
    # Find all documentation comments that precede a declaration
    # Pattern: /-- ... -/ followed by @[category ...] (optional) followed by theorem/lemma/def
    pattern = re.compile(
        r'/\-\-(.*?)\-/\s*'                   # doc comment (no \n? prefix - breaks DOTALL)
        r'(?:@\[category\s+([^\]]+)\]\s*)?'   # optional category tag
        r'(theorem|lemma|def|abbrev|instance)\s+(\w+(?:\.\w+)*)',  # declaration
        re.DOTALL
    )
    
    for match in pattern.finditer(content):
        doc_text = match.group(1).strip()
        category_raw = match.group(2)
        decl_type = match.group(3)
        decl_name = match.group(4)
        
        # Get the surrounding code (up to := or first line break after signature)
        sig_start = match.end()
        sig_end = content.find(":=", sig_start)
        if sig_end == -1:
            sig_end = content.find("\n", sig_start)
        if sig_end == -1:
            sig_end = sig_start + 100
        signature = content[sig_start:sig_end].strip()
        
        theorems.append({
            "decl_type": decl_type,
            "decl_name": decl_name,
            "doc_text": doc_text,
            "signature": signature[:200],
            "category_raw": category_raw,
        })
    
    return theorems


def compute_difficulty_score(problem, annotations, full_content):
    """
    Compute a refined difficulty score 1-10 and category.
    Uses multiple signals: proof status, code complexity, statement length, etc.
    """
    signals = []
    
    # Signal 1: Proof status
    statuses = [a["proof_status"] for a in annotations]
    if "research_open" in statuses:
        signals.append(8)  # open problems are harder
    if "research_solved" in statuses:
        signals.append(5)  # solved problems, moderate
    if "textbook" in statuses:
        signals.append(3)  # textbook = easier
    if "api" in statuses:
        signals.append(2)  # API defs = easy
    
    # Signal 2: Code complexity
    code = problem.get("raw_lean_code", "")
    lines = code.count("\n")
    if lines > 100:
        signals.append(7)
    elif lines > 50:
        signals.append(5)
    elif lines > 20:
        signals.append(4)
    else:
        signals.append(3)
    
    # Signal 3: Statement length (proxy for complexity)
    stmt = problem.get("statement", "")
    stmt_len = len(stmt)
    if stmt_len > 1000:
        signals.append(7)
    elif stmt_len > 500:
        signals.append(5)
    elif stmt_len > 200:
        signals.append(4)
    else:
        signals.append(3)
    
    # Signal 4: Domain baseline
    domain = problem.get("domain", "")
    domain_difficulty = {
        "Millenium": 9,
        "HilbertProblems": 8,
        "OpenQuantumProblems": 7,
        "GreensOpenProblems": 7,
        "ErdosProblems": 6,
        "LittProblems": 6,
        "Mathoverflow": 5,
        "Paper": 5,
        "Wikipedia": 4,
        "Books": 4,
        "OEIS": 4,
        "Arxiv": 5,
        "WrittenOnTheWallII": 5,
        "Subsets": 4,
        "OptimizationConstants": 5,
        "Other": 5,
    }
    signals.append(domain_difficulty.get(domain, 5))
    
    # Signal 5: AMS field diversity
    ams_fields = set()
    for a in annotations:
        ams_fields.update(a["ams_fields"])
    if len(ams_fields) >= 3:
        signals.append(6)
    elif len(ams_fields) >= 2:
        signals.append(4)
    
    # Compute weighted score
    if not signals:
        return 5, "medium"
    
    score = sum(signals) / len(signals)
    score = max(1, min(10, round(score)))
    
    # Category
    if score <= 3:
        category = "easy"
    elif score <= 5:
        category = "medium"
    elif score <= 7:
        category = "hard"
    else:
        category = "expert"
    
    return score, category


def detect_archetype(statement):
    """Detect problem archetype from statement text."""
    matches = []
    for pattern, archetype in ARCHETYPE_PATTERNS:
        if re.search(pattern, statement, re.IGNORECASE):
            matches.append(archetype)
    return list(set(matches)) if matches else ["general"]


def detect_reasoning_types(domain, statement, annotations):
    """Detect reasoning types based on domain + statement analysis."""
    reasoning = []
    
    # Domain-based reasoning
    domain_reasoning = REASONING_BY_DOMAIN.get(domain, ["general"])
    reasoning.extend(domain_reasoning)
    
    # AMS-based reasoning
    ams_fields = set()
    for a in annotations:
        ams_fields.update(a["ams_fields"])
    
    ams_reasoning = {
        "combinatorics": "combinatorial",
        "number_theory": "number_theoretic",
        "geometry": "geometric",
        "algebraic_geometry": "geometric",
        "general_topology": "topological",
        "probability_theory_stochastic": "probabilistic",
        "mathematical_logic_foundations": "logical",
        "quantum_theory": "quantum",
        "computer_science": "computational",
        "game_theory_economics": "game_theoretic",
        "group_theory_generalizations": "algebraic",
        "dynamical_systems_ergodic": "dynamical",
        "functional_analysis": "analytic",
        "fourier_analysis": "analytic",
        "measure_integration": "analytic",
    }
    
    for field in ams_fields:
        mapped = ams_reasoning.get(field)
        if mapped and mapped not in reasoning:
            reasoning.append(mapped)
    
    # Statement-based reasoning
    stmt_lower = statement.lower()
    if "conjecture" in stmt_lower:
        reasoning.append("conjectural")
    if "proof" in stmt_lower or "prove" in stmt_lower:
        reasoning.append("deductive")
    if "algorithm" in stmt_lower or "compute" in stmt_lower:
        reasoning.append("algorithmic")
    if "exists" in stmt_lower:
        reasoning.append("existential")
    if "forall" in stmt_lower or "all" in stmt_lower.split():
        reasoning.append("universal")
    if "graph" in stmt_lower or "edge" in stmt_lower or "vertex" in stmt_lower:
        reasoning.append("graph_theoretic")
    if "optimal" in stmt_lower or "maximum" in stmt_lower or "minimum" in stmt_lower:
        reasoning.append("optimization")
    if "asymptotic" in stmt_lower or "limit" in stmt_lower:
        reasoning.append("asymptotic")
    if "probabilistic" in stmt_lower or "random" in stmt_lower:
        reasoning.append("probabilistic")
    
    return list(set(reasoning))


def count_tactics(raw_lean_code):
    """Count advanced tactics in code as a complexity proxy."""
    tactics = ["simp", "calc", "induction", "omega", "nlinarith", "positivity",
               "aesop", "interval_cases", "cases", "apply", "refine", "exact",
               "have", "let", "by_cases", "contradiction", "absurd", "omega"]
    counts = {}
    for t in tactics:
        counts[t] = raw_lean_code.count(t)
    return counts


def is_conjecture(statement, filename, theorem_type):
    """Determine if this is likely a conjecture (unsolved)."""
    stmt_lower = statement.lower()
    name_lower = filename.lower()
    
    keywords = ["conjecture", "open problem", "unsolved", "unknown"]
    for kw in keywords:
        if kw in stmt_lower or kw in name_lower:
            return True
    return False


def has_proof_sketch(statement):
    """Check if the statement contains a proof sketch."""
    keywords = ["sketch", "outline", "idea", "brief proof", "summary"]
    stmt_lower = statement.lower()
    return any(kw in stmt_lower for kw in keywords)


def map_theorem_type(theorem_type_raw):
    """Map Lean declaration types to readable categories."""
    mapping = {
        "theorem": "theorem",
        "lemma": "lemma",
        "def": "definition",
        "abbrev": "abbreviation",
        "instance": "instance",
        "inductive": "inductive",
    }
    return mapping.get(theorem_type_raw, theorem_type_raw)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 1.1 Stage 4: NLP Enrichment")
    print("=" * 60)
    
    # Load existing dataset
    print(f"\n[1] Loading existing dataset: {EXISTING_JSON}")
    with open(EXISTING_JSON, encoding='utf-8') as f:
        data = json.load(f)
    
    problems = data["problems"]
    print(f"    Loaded {len(problems)} existing problems")
    
    # Process each problem
    print(f"\n[2] Enriching problems with deep metadata...")
    enrichment_stats = {
        "with_annotations": 0,
        "with_multiple_theorems": 0,
        "proof_status": Counter(),
        "difficulty_distribution": Counter(),
        "total_theorems_found": 0,
        "archetype_distribution": Counter(),
        "reasoning_types_distribution": Counter(),
    }
    
    for idx, problem in enumerate(problems):
        if idx % 100 == 0:
            print(f"    Processing problem {idx}/{len(problems)}...")
        
        filepath = problem.get("filepath", "")
        domain = problem.get("domain", "")
        full_path = os.path.join(RAW_DIR, filepath)
        
        # Read full file content
        full_content = ""
        if os.path.exists(full_path):
            try:
                with open(full_path, encoding='utf-8') as f:
                    full_content = f.read()
            except Exception:
                pass
        
        # Parse @[category ...] annotations
        annotations = parse_category_tag(full_content)
        enrichment_stats["with_annotations"] += (1 if annotations else 0)
        
        # Extract ALL theorems from the file
        all_theorems = extract_all_theorems(full_content, domain, filepath)
        enrichment_stats["total_theorems_found"] += len(all_theorems)
        enrichment_stats["with_multiple_theorems"] += (1 if len(all_theorems) > 1 else 0)
        
        # Refined difficulty
        diff_score, diff_cat = compute_difficulty_score(problem, annotations, full_content)
        enrichment_stats["difficulty_distribution"][diff_cat] += 1
        
        # Archetype
        statement = problem.get("statement", "")
        archetype = detect_archetype(statement)
        for a in archetype:
            enrichment_stats["archetype_distribution"][a] += 1
        
        # Reasoning types
        reasoning = detect_reasoning_types(domain, statement, annotations)
        for r in reasoning:
            enrichment_stats["reasoning_types_distribution"][r] += 1
        
        # Proof status from annotations
        all_statuses = [a["proof_status"] for a in annotations]
        primary_status = all_statuses[0] if all_statuses else "unknown"
        enrichment_stats["proof_status"][primary_status] += 1
        
        # Tactic counts
        tactic_counts = count_tactics(problem.get("raw_lean_code", ""))
        
        # Build enrichment object
        enrichment = {
            "difficulty_score": diff_score,
            "difficulty_category": diff_cat,
            "proof_status": primary_status,
            "proof_statuses_all": all_statuses,
            "ams_codes": list(set(c for a in annotations for c in a["ams_codes"])),
            "ams_fields": list(set(f for a in annotations for f in a["ams_fields"])),
            "formal_proof_links": list(set(l for a in annotations for l in a["formal_proofs"])),
            "reasoning_types": reasoning,
            "archetype": archetype,
            "is_conjecture": is_conjecture(statement, problem.get("filename", ""), problem.get("theorem_type", "")),
            "has_proof_sketch": has_proof_sketch(statement),
            "num_theorems_in_file": len(all_theorems),
            "tactic_counts": tactic_counts,
            "enrichment_version": "1.1.0",
        }
        
        problem["enrichment"] = enrichment
    
    # Update metadata
    data["metadata"]["version"] = "1.1-enriched"
    data["metadata"]["notes"] = "Phase 1.1 Stage 4: Full NLP enrichment with AMS classification, reasoning types, difficulty scoring"
    data["metadata"]["enrichment_timestamp"] = "2026-05-30T18:00:00.000000"
    data["metadata"]["enrichment_stats"] = {
        "total_problems": len(problems),
        "with_category_annotations": enrichment_stats["with_annotations"],
        "total_theorems_found_in_files": enrichment_stats["total_theorems_found"],
        "files_with_multiple_theorems": enrichment_stats["with_multiple_theorems"],
    }
    
    # Save enriched dataset
    print(f"\n[3] Saving enriched dataset to {OUTPUT_JSON}")
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    file_size_mb = os.path.getsize(OUTPUT_JSON) / (1024 * 1024)
    print(f"    Saved: {len(problems)} problems, {file_size_mb:.2f} MB")
    
    # ─── Report ──────────────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"ENRICHMENT REPORT")
    print(f"{'=' * 60}")
    
    print(f"\n--- Proof Status Distribution ---")
    for status, count in enrichment_stats["proof_status"].most_common():
        pct = 100 * count / len(problems)
        print(f"  {status:20s}: {count:4d} ({pct:5.1f}%)")
    
    print(f"\n--- Difficulty Distribution (1-10 scale) ---")
    for cat in ["easy", "medium", "hard", "expert"]:
        count = enrichment_stats["difficulty_distribution"][cat]
        pct = 100 * count / len(problems)
        print(f"  {cat:10s}: {count:4d} ({pct:5.1f}%)")
    
    print(f"\n--- Top 15 Archetypes ---")
    for arch, count in enrichment_stats["archetype_distribution"].most_common(15):
        pct = 100 * count / len(problems)
        print(f"  {arch:25s}: {count:4d} ({pct:5.1f}%)")
    
    print(f"\n--- Top 20 Reasoning Types ---")
    for rt, count in enrichment_stats["reasoning_types_distribution"].most_common(20):
        pct = 100 * count / len(problems)
        print(f"  {rt:30s}: {count:4d} ({pct:5.1f}%)")
    
    print(f"\n--- Statistics ---")
    print(f"  Total problems:              {len(problems)}")
    print(f"  With category annotations:   {enrichment_stats['with_annotations']} ({100*enrichment_stats['with_annotations']/len(problems):.1f}%)")
    print(f"  Total theorems in files:     {enrichment_stats['total_theorems_found']}")
    print(f"  Files with >1 theorem:       {enrichment_stats['with_multiple_theorems']}")
    print(f"  Output file size:            {file_size_mb:.2f} MB")
    
    print(f"\n✓ Enrichment complete. Output: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
