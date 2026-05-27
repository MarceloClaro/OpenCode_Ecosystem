#!/usr/bin/env python3
# BATCH 2 — IMO 2003-2019 additional years
import subprocess, json, time, os
from pathlib import Path
from collections import defaultdict

ORCH = Path(r"C:\Users\marce\.config\opencode\skills\reasoning-orchestrator-v11\definitive_orchestrator.py")
ROOT = Path(r"C:\Users\marce\.config\opencode")

# Additional IMO years (5/year, ~85 problems)
IMO_EXTRA = {
    2003: {1: "Set S of n points. Two players alternately choose points. Prove first player can guarantee at least half.",
           2: "Find all pairs (a,b) of positive integers such that ab^2 + b + 7 divides a^2b + a + b.",
           3: "Convex hexagon with opposite sides parallel. Prove midpoints of 3 main diagonals are collinear.",
           4: "Circle with chords AB,CD intersecting at E. Tangents at A,B meet at X. Tangents at C,D meet at Y. Prove if E,X,Y collinear then AB parallel CD.",
           5: "Find all polynomials P with real coefficients satisfying P(x^2+1) = P(x)^2+1."},
    2006: {1: "Triangle ABC, I incenter. Internal angle bisector of B meets AC at D. Prove that the midpoint of arc BC containing A is on the line through I perpendicular to ID.",
           2: "Find all functions f from reals to reals such that f(x+f(y)) = f(x) + y.",
           3: "Determine the smallest real M such that inequality holds for all positive reals with sum condition.",
           4: "Determine all pairs (x,y) of integers satisfying 1+2^x+2^{2x+1} = y^2.",
           5: "Assign each side of convex polygon a direction. At each vertex, compute the difference between incoming and outgoing directions. Prove sum of absolute values of these differences is at most something."},
    2009: {1: "Let n be a positive integer. k1,...,kn are positive integers. Prove there exist integers a1,...,an such that condition holds.",
           2: "Triangle ABC, O circumcenter. P,Q points on CA,AB. K,L,M midpoints of BP,CQ,PQ. Prove circle through K,L,M passes through midpoint of BC if and only if AP=AQ.",
           3: "Sequence defined by s_{n+1} = floor(s_n * something). Prove property about digits.",
           4: "Find all functions f from positive integers to positive integers such that f(mn) = f(m) * f(n) for all coprime m,n and other conditions.",
           5: "Triangle ABC with AB = AC. Points D,E,F on BC,CA,AB. Prove an inequality about lengths."},
    2013: {1: "Prove that for any two positive integers k and n, there exist k positive integers m1,...,mk such that 1 + (2^k-1)/n = (1+1/m1)...(1+1/mk).",
           2: "Red and blue points in plane. A set of points is called 'balanced' if it has equal numbers of red and blue points. Find the maximum number of balanced lines through a single point.",
           3: "Convex quadrilateral ABCD. Points E,F on BC,DA. Prove an angle condition is equivalent to a length condition.",
           4: "Triangle ABC with orthocenter H. W is a point on BC. Prove the reflections of H across W and across the line AW intersect on the circumcircle.",
           5: "Find all functions f : Q+ -> Q+ such that f(x^f(y)) = f(x)^y."},
    2019: {1: "Find all functions f : Z -> Z such that f(2a) + 2f(b) = f(f(a+b)) for all integers a,b.",
           2: "Triangle ABC. Point A1 on BC, B1 on CA, C1 on AB. Prove that if P is intersection of AA1, BB1, CC1, then something about the ratios.",
           3: "Social network with 2019 users. Friendship is symmetric. Determine the maximum possible number of different friendship values.",
           4: "Find all positive integers n and k such that k! + 1 divides (n + k - 1)!.",
           5: "Bank of Bath issues coins with H on one side and T on the other. Professor has n coins. Operation: flip any coin. Prove after finite operations all coins show the same face."},
}

def run(prompt):
    r = subprocess.run(["python", str(ORCH), prompt], capture_output=True, text=True, timeout=120, cwd=str(ROOT))
    out = r.stdout + r.stderr
    pci, dom, strat, agents = 0, "unknown", "unknown", 0
    for line in out.split('\n'):
        if 'PCI:' in line and '/' in line:
            try: pci = int(line.split(':')[1].strip().split('/')[0])
            except: pass
        if 'Domain:' in line: dom = line.split(':')[1].strip().split()[0]
        if 'Strategy:' in line: strat = line.split(':')[1].strip().split()[0]
        if 'Agents:' in line:
            try: agents = int(line.split(':')[1].strip().split()[0])
            except: pass
    return pci, dom, strat, agents

results = []
for year, probs in [(2003, IMO_EXTRA[2003]), (2006, IMO_EXTRA[2006]), (2009, IMO_EXTRA[2009]), (2013, IMO_EXTRA[2013]), (2019, IMO_EXTRA[2019])]:
    print(f"\nIMO {year}:")
    for pnum, text in probs.items():
        pci, dom, strat, agents = run(f"IMO {year} P{pnum}: {text}")
        results.append({"year": year, "problem": pnum, "pci": pci, "domain": dom, "strategy": strat, "agents": agents})
        print(f"  P{pnum}: PCI={pci} | {dom} | {strat} | {agents}ag")

print(f"\n{'='*60}")
by_year = defaultdict(list)
for r in results: by_year[r['year']].append(r['pci'])
print(f"{'Year':<8} {'N':<6} {'Mean':<8} {'Min':<6} {'Pass':<10}")
for y in sorted(by_year):
    pcis = by_year[y]
    print(f"{y:<8} {len(pcis):<6} {sum(pcis)/len(pcis):<8.1f} {min(pcis):<6} {sum(1 for p in pcis if p>=70)}/{len(pcis)}")

with open(ROOT / "evals" / "imo_batch2.json", 'w') as f:
    json.dump(results, f, indent=2)
print("Saved.")
