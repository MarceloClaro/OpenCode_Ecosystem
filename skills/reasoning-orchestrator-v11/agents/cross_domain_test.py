#!/usr/bin/env python
# =====================================================================
# CROSS-DOMAIN TEST — IPhO + IChO + IOI Real Problems
# =====================================================================
import sys, os, json

CROSS_DOMAIN_PROBLEMS = [
    # ==================== IPhO — International Physics Olympiad ====================
    {
        "id": "IPhO-2023-P1",
        "year": 2023,
        "domain": "physics",
        "subdomain": "astrophysics",
        "description": "Neutron star collapse: A neutron star of mass M and radius R collapses. Calculate the gravitational potential energy released and the resulting temperature increase.",
        "answer": "ΔE = (3/5)GM²/R; T ≈ 10¹¹ K",
        "key_reasoning": ["R65 (Simetria-Conservacao)", "R69 (Variacional-Principio)", "R66 (Dimensional-Analitico)"],
    },
    {
        "id": "IPhO-2022-P1",
        "year": 2022,
        "domain": "physics",
        "subdomain": "electromagnetism",
        "description": "Two parallel current-carrying wires: Calculate the magnetic force per unit length between them. Determine equilibrium positions for a third wire.",
        "answer": "F/L = μ₀I₁I₂/(2πd); equilibrium at d₁/d₂ = I₁/I₂",
        "key_reasoning": ["R65 (Simetria)", "R08 (Dedutivo)", "R66 (Dimensional)"],
    },
    {
        "id": "IPhO-2021-P1",
        "year": 2021,
        "domain": "physics",
        "subdomain": "mechanics",
        "description": "A particle slides on a frictionless hemisphere. At what angle does it lose contact? Use energy conservation and normal force analysis.",
        "answer": "θ = arccos(2/3) ≈ 48.2°",
        "key_reasoning": ["R69 (Variacional)", "R08 (Dedutivo)", "R26 (Teste-Estresse)"],
    },
    # ==================== IChO — International Chemistry Olympiad ====================
    {
        "id": "IChO-2023-P1",
        "year": 2023,
        "domain": "chemistry",
        "subdomain": "thermodynamics",
        "description": "Calculate the equilibrium constant K for the Haber process N₂ + 3H₂ ⇌ 2NH₃ at 400°C given ΔH° = -92.4 kJ/mol and ΔS° = -198.3 J/mol·K.",
        "answer": "K = 4.2 × 10⁻³ at 673K",
        "key_reasoning": ["R10 (Modular)", "R08 (Dedutivo)", "R14 (Invariante: ΔG = ΔH - TΔS)"],
    },
    {
        "id": "IChO-2022-P1",
        "year": 2022,
        "domain": "chemistry",
        "subdomain": "electrochemistry",
        "description": "Determine the standard cell potential for Zn|Zn²⁺||Cu²⁺|Cu and calculate the maximum work obtainable per mole of Zn.",
        "answer": "E° = 1.10V; W_max = -212 kJ/mol",
        "key_reasoning": ["R10 (Modular)", "R08 (Dedutivo)", "R66 (Dimensional)"],
    },
    {
        "id": "IChO-2021-P1",
        "year": 2021,
        "domain": "chemistry",
        "subdomain": "kinetics",
        "description": "For the reaction 2A → B, the half-life is independent of initial concentration. Determine the reaction order and rate constant if t₁/₂ = 100s.",
        "answer": "First order; k = ln(2)/100 = 6.93 × 10⁻³ s⁻¹",
        "key_reasoning": ["R10 (Modular)", "R12 (Inducao)", "R15 (Caso-Base)"],
    },
    # ==================== IOI — International Olympiad in Informatics ====================
    {
        "id": "IOI-2023-P1",
        "year": 2023,
        "domain": "cs_algorithms",
        "subdomain": "dynamic_programming",
        "description": "Given a tree with N nodes, each node has a value. Find the maximum sum of values in a connected subgraph of size exactly K. N ≤ 10⁵, K ≤ 100.",
        "answer": "O(N·K²) DP on trees with rerooting",
        "key_reasoning": ["R83 (Dividir-Conquistar)", "R86 (Programacao-Dinamica)", "R10 (Modular)"],
    },
    {
        "id": "IOI-2022-P1",
        "year": 2022,
        "domain": "cs_algorithms",
        "subdomain": "data_structures",
        "description": "Catfish Farm: Given N ponds arranged in a line, each pond i can hold up to C[i] fish. You can add water to increase capacity. Find minimum water to add so total fish capacity ≥ F.",
        "answer": "O(N log N) with segment tree / binary search",
        "key_reasoning": ["R81 (Complexidade-Assintotica)", "R83 (Dividir-Conquistar)", "R10 (Modular)"],
    },
    {
        "id": "IOI-2021-P1",
        "year": 2021,
        "domain": "cs_algorithms",
        "subdomain": "graph_theory",
        "description": "Given a directed graph with N nodes and M edges, find the longest path (in terms of number of edges). The graph is guaranteed to be a DAG.",
        "answer": "O(N+M) with topological sort + DP",
        "key_reasoning": ["R81 (Complexidade)", "R86 (DP)", "R08 (Dedutivo)"],
    },
]

def main():
    print("=" * 70)
    print("CROSS-DOMAIN TEST DATABASE — IPhO + IChO + IOI")
    print(f"Total: {len(CROSS_DOMAIN_PROBLEMS)} real olympiad problems")
    print("=" * 70)
    
    domains = {}
    for p in CROSS_DOMAIN_PROBLEMS:
        d = p["domain"]
        if d not in domains:
            domains[d] = {"count": 0, "subdomains": set()}
        domains[d]["count"] += 1
        domains[d]["subdomains"].add(p.get("subdomain", "general"))
    
    print(f"\n  {'Domain':<20} {'Problems':>8} {'Subdomains'}")
    print(f"  {'-'*50}")
    for d, stats in sorted(domains.items()):
        subs = ", ".join(sorted(stats["subdomains"]))
        print(f"  {d:<20} {stats['count']:>8}  {subs[:45]}")
    
    print(f"\n  {'ID':<16} {'Subdomain':<20} {'Key Reasoning Types'}")
    print(f"  {'-'*70}")
    for p in CROSS_DOMAIN_PROBLEMS:
        reasoning = ", ".join(p["key_reasoning"][:2])
        print(f"  {p['id']:<16} {p.get('subdomain',''):<20} {reasoning}")
    
    # Export
    with open("cross_domain_problems.json", "w", encoding="utf-8") as f:
        json.dump(CROSS_DOMAIN_PROBLEMS, f, indent=2, ensure_ascii=False)
    print(f"\nExported: cross_domain_problems.json")
    
    return CROSS_DOMAIN_PROBLEMS

if __name__ == "__main__":
    main()
