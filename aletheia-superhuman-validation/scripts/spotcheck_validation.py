"""
spotcheck_validation.py — Phase 1.1 Stage 5: Spot-Check Validation
==================================================================
Validates 50 random samples (7.5%) across major domains:
1. Statement extraction accuracy
2. Type classification quality
3. Difficulty reasonableness
4. Proof status correctness
5. Domain assignment

Output: data/spotcheck_validation_report.json + detailed console report
"""

import json
import random
import os
import re
from collections import Counter, defaultdict

RAW_DIR = "raw_data/formal-conjectures"
ENRICHED_JSON = "data/erdos_718_enriched_v1.1.json"
OUTPUT_REPORT = "data/spotcheck_validation_report.json"

random.seed(42)  # Reproducible

# ─── Validation Dimensions ──────────────────────────────────────────────────

def check_statement_accuracy(problem, full_content):
    """
    Check if statement was accurately extracted from Lean doc comment.
    Score: 1.0 = exact match, 0.8 = partial match, 0.5 = different, 0.0 = missing
    """
    extracted = problem.get("statement", "").strip()
    if not extracted:
        return 0.0, "No statement extracted"
    
    # Find doc comments that look like the statement
    doc_comments = re.findall(r'/\-\-(.*?)\-/', full_content, re.DOTALL)
    if not doc_comments:
        return 0.0, "No doc comments found in file"
    
    # Check if extracted statement matches any doc comment
    best_score = 0.0
    best_match = ""
    for dc in doc_comments:
        dc_clean = dc.strip()
        # Simple overlap score
        extracted_words = set(extracted.lower().split())
        dc_words = set(dc_clean.lower().split())
        if len(extracted_words) == 0:
            continue
        overlap = len(extracted_words & dc_words)
        score = overlap / len(extracted_words)
        if score > best_score:
            best_score = score
            best_match = dc_clean[:100]
    
    if best_score >= 0.7:
        return 1.0, f"Good match (score={best_score:.2f})"
    elif best_score >= 0.4:
        return 0.6, f"Partial match (score={best_score:.2f})"
    else:
        return 0.2, f"Poor match (score={best_score:.2f})"


def check_proof_status(problem, full_content):
    """Verify proof status matches @[category ...] tag."""
    enrichment = problem.get("enrichment", {})
    reported_status = enrichment.get("proof_status", "unknown")
    
    # Extract actual categories
    categories = re.findall(r'@\[category\s+([^\]]+)\]', full_content)
    
    actual_statuses = set()
    for cat in categories:
        cat_lower = cat.lower()
        if "research open" in cat_lower:
            actual_statuses.add("research_open")
        elif "research solved" in cat_lower:
            actual_statuses.add("research_solved")
        elif "textbook" in cat_lower:
            actual_statuses.add("textbook")
        elif "test" in cat_lower:
            actual_statuses.add("test")
        elif "api" in cat_lower:
            actual_statuses.add("api")
    
    if not actual_statuses:
        return 0.5, "No status tags found (might be unknown)"
    
    if reported_status in actual_statuses:
        return 1.0, f"Correct ({reported_status})"
    else:
        return 0.0, f"Mismatch: reported={reported_status}, actual={actual_statuses}"


def check_difficulty(problem):
    """Basic sanity check on difficulty scoring."""
    enrichment = problem.get("enrichment", {})
    score = enrichment.get("difficulty_score", 5)
    cat = enrichment.get("difficulty_category", "medium")
    status = enrichment.get("proof_status", "unknown")
    
    issues = []
    
    # research_open should generally be hard+
    if status == "research_open" and score < 5:
        issues.append(f"Open problem but score={score}")
    
    # textbook should generally be easy-medium
    if status == "textbook" and score > 7:
        issues.append(f"Textbook but score={score}")
    
    # API should be easy
    if status == "api" and score > 5:
        issues.append(f"API but score={score}")
    
    if not issues:
        return 1.0, f"Reasonable (score={score}, cat={cat}, status={status})"
    else:
        return 0.5, f"Minor issues: {'; '.join(issues[:2])}"


def check_types(problem):
    """Basic type sanity check."""
    types = problem.get("types", [])
    domain = problem.get("domain", "")
    enrichment = problem.get("enrichment", {})
    
    if not types:
        return 0.3, "No types assigned"
    
    issues = []
    
    # Domain-type consistency
    domain_type_map = {
        "ErdosProblems": ["combinatorics", "graph_theory", "discrete_math", "number_theory"],
        "Wikipedia": ["mathematics", "general", "number_theory"],
        "Millenium": ["analysis", "topology", "algebra", "number_theory"],
        "OEIS": ["sequence", "integer_sequence"],
    }
    
    expected = domain_type_map.get(domain, [])
    if expected:
        has_expected = any(e in types for e in expected)
        if not has_expected:
            issues.append(f"No expected types for {domain} ({expected})")
    
    if not issues:
        return 1.0, f"Types look good ({len(types)} assigned)"
    else:
        return 0.7, f"Minor: {'; '.join(issues)}"


def check_domain(problem):
    """Verify domain assignment is correct based on directory."""
    filepath = problem.get("filepath", "")
    domain = problem.get("domain", "")
    
    if not filepath or not domain:
        return 0.0, "Missing filepath or domain"
    
    # Domain should match the first directory component (or exact match)
    path_parts = filepath.split(os.sep)
    if path_parts[0] == domain:
        return 1.0, f"Correct ({domain})"
    else:
        return 0.0, f"Mismatch: domain={domain}, path starts with={path_parts[0]}"


# ─── Sampling ───────────────────────────────────────────────────────────────

def stratified_sample(problems, sample_size=50):
    """Sample problems stratified by domain to ensure diverse coverage."""
    domain_groups = defaultdict(list)
    for i, p in enumerate(problems):
        domain_groups[p.get("domain", "Unknown")].append(i)
    
    # Compute samples per domain (proportional with min 1)
    samples_per_domain = {}
    remaining = sample_size
    domains = sorted(domain_groups.keys(), key=lambda d: -len(domain_groups[d]))
    
    for d in domains:
        proportion = max(1, round(len(domain_groups[d]) / len(problems) * sample_size))
        samples_per_domain[d] = min(proportion, len(domain_groups[d]))
    
    # Adjust to hit exact sample_size
    total = sum(samples_per_domain.values())
    while total > sample_size:
        # Reduce the largest non-essential sample
        for d in reversed(domains):
            if samples_per_domain[d] > 1:
                samples_per_domain[d] -= 1
                total -= 1
                break
    
    while total < sample_size:
        for d in domains:
            if samples_per_domain[d] < len(domain_groups[d]):
                samples_per_domain[d] += 1
                total += 1
                break
    
    # Sample
    sampled_indices = []
    domain_counts = {}
    for d, n in samples_per_domain.items():
        eligible = domain_groups[d]
        chosen = random.sample(eligible, min(n, len(eligible)))
        sampled_indices.extend(chosen)
        domain_counts[d] = len(chosen)
    
    return sampled_indices, domain_counts


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Phase 1.1 Stage 5: Spot-Check Validation")
    print("=" * 60)
    
    # Load enriched dataset
    print(f"\n[1] Loading enriched dataset: {ENRICHED_JSON}")
    with open(ENRICHED_JSON, encoding='utf-8') as f:
        data = json.load(f)
    problems = data["problems"]
    print(f"    Loaded {len(problems)} problems")
    
    # Stratified sampling
    print(f"\n[2] Stratified sampling (target: 50 samples, ~7.5%)")
    sampled_indices, domain_counts = stratified_sample(problems, 50)
    print(f"    Sampled {len(sampled_indices)} problems across {len(domain_counts)} domains:")
    for d, c in sorted(domain_counts.items(), key=lambda x: -x[1]):
        print(f"      {d:25s}: {c}")
    
    # Validate each sample
    print(f"\n[3] Running validations...")
    
    results = []
    dimension_scores = defaultdict(list)
    dimension_errors = []
    
    for idx, problem_idx in enumerate(sampled_indices):
        problem = problems[problem_idx]
        filepath = problem.get("filepath", "")
        full_path = os.path.join(RAW_DIR, filepath)
        
        # Read full file content
        full_content = ""
        if os.path.exists(full_path):
            with open(full_path, encoding='utf-8') as f:
                full_content = f.read()
        
        # Run checks
        stmt_score, stmt_note = check_statement_accuracy(problem, full_content)
        status_score, status_note = check_proof_status(problem, full_content)
        diff_score, diff_note = check_difficulty(problem)
        type_score, type_note = check_types(problem)
        domain_score, domain_note = check_domain(problem)
        
        scores = {
            "statement_accuracy": stmt_score,
            "proof_status": status_score,
            "difficulty_sanity": diff_score,
            "type_quality": type_score,
            "domain_correctness": domain_score,
        }
        
        notes = {
            "statement_accuracy": stmt_note,
            "proof_status": status_note,
            "difficulty_sanity": diff_note,
            "type_quality": type_note,
            "domain_correctness": domain_note,
        }
        
        overall = sum(scores.values()) / len(scores)
        
        for dim, score in scores.items():
            dimension_scores[dim].append(score)
        
        results.append({
            "index": problem_idx,
            "id": problem.get("id"),
            "domain": problem.get("domain"),
            "filename": problem.get("filename"),
            "scores": scores,
            "notes": notes,
            "overall": overall,
        })
        
        if idx % 10 == 0:
            print(f"    Validated {idx}/{len(sampled_indices)}...")
    
    # Compute aggregate metrics
    print(f"\n[4] Computing aggregate metrics...")
    
    aggregate = {}
    for dim, scores in dimension_scores.items():
        aggregate[dim] = {
            "mean": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores),
            "pass_count": sum(1 for s in scores if s >= 0.7),
            "pass_rate": sum(1 for s in scores if s >= 0.7) / len(scores),
        }
    
    overall_scores = [r["overall"] for r in results]
    aggregate["overall"] = {
        "mean": sum(overall_scores) / len(overall_scores),
        "median": sorted(overall_scores)[len(overall_scores) // 2],
        "min": min(overall_scores),
        "max": max(overall_scores),
        "pass_count": sum(1 for s in overall_scores if s >= 0.7),
        "pass_rate": sum(1 for s in overall_scores if s >= 0.7) / len(overall_scores),
    }
    
    # Domain-level analysis
    domain_metrics = defaultdict(list)
    for r in results:
        domain_metrics[r["domain"]].append(r["overall"])
    
    domain_summary = {}
    for d, scores in sorted(domain_metrics.items(), key=lambda x: -len(x[1])):
        domain_summary[d] = {
            "count": len(scores),
            "mean_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
        }
    
    # Build report
    report = {
        "timestamp": "2026-05-30T19:00:00",
        "total_problems": len(problems),
        "sample_size": len(sampled_indices),
        "sample_fraction": len(sampled_indices) / len(problems),
        "aggregate_scores": aggregate,
        "domain_summary": domain_summary,
        "individual_results": results,
        "flagged_issues": [r for r in results if r["overall"] < 0.6],
    }
    
    # Save report
    print(f"\n[5] Saving validation report: {OUTPUT_REPORT}")
    with open(OUTPUT_REPORT, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # ─── Console Report ─────────────────────────────────────────────────────
    print(f"\n{'=' * 60}")
    print(f"SPOT-CHECK VALIDATION REPORT")
    print(f"{'=' * 60}")
    
    print(f"\n--- Aggregate Scores ---")
    print(f"{'Dimension':<30s} {'Mean':<8s} {'Min':<8s} {'Max':<8s} {'Pass Rate':<10s}")
    print(f"{'-'*30} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")
    for dim in ["statement_accuracy", "proof_status", "difficulty_sanity", "type_quality", "domain_correctness"]:
        a = aggregate[dim]
        print(f"{dim:<30s} {a['mean']:<8.3f} {a['min']:<8.2f} {a['max']:<8.2f} {a['pass_rate']:<10.2%}")
    print(f"{'-'*30} {'-'*8} {'-'*8} {'-'*8} {'-'*10}")
    a = aggregate["overall"]
    print(f"{'OVERALL':<30s} {a['mean']:<8.3f} {a['min']:<8.2f} {a['max']:<8.2f} {a['pass_rate']:<10.2%}")
    
    print(f"\n--- Domain-Level Summary ---")
    for d, ds in sorted(domain_summary.items(), key=lambda x: -x[1]["count"]):
        print(f"  {d:25s}: n={ds['count']:2d}, mean={ds['mean_score']:.3f}, range=[{ds['min_score']:.2f}, {ds['max_score']:.2f}]")
    
    print(f"\n--- Flagged Issues ({len(report['flagged_issues'])}) ---")
    for r in report["flagged_issues"]:
        print(f"  [{r['id']}] ({r['domain']}) overall={r['overall']:.2f}")
        for dim, score in r["scores"].items():
            if score < 0.7:
                print(f"    - {dim}: {score:.2f} ({r['notes'].get(dim, '')})")
    
    print(f"\n--- Recommendations ---")
    flagged_count = len(report["flagged_issues"])
    if aggregate["overall"]["pass_rate"] >= 0.95:
        print(f"  ✓ Dataset quality is HIGH ({aggregate['overall']['pass_rate']:.1%} pass rate)")
        print(f"  ✓ Proceed to Phase 1.2 (Infrastructure)")
    elif aggregate["overall"]["pass_rate"] >= 0.80:
        print(f"  ⚠ Dataset quality is GOOD ({aggregate['overall']['pass_rate']:.1%} pass rate)")
        print(f"  ⚠ {flagged_count} flagged issues - consider fixing before Phase 1.2")
    else:
        print(f"  ✗ Dataset quality needs IMPROVEMENT ({aggregate['overall']['pass_rate']:.1%} pass rate)")
        print(f"  ✗ {flagged_count} flagged issues must be fixed before Phase 1.2")
    
    print(f"\n✓ Validation complete. Report: {OUTPUT_REPORT}")


if __name__ == "__main__":
    main()
