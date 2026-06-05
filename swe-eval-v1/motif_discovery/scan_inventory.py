import re, yaml
from pathlib import Path
from collections import Counter

root = Path(r"C:\Users\marce\.config\opencode")
known = set()
unknown_refs = Counter()
classified = Counter()
orphan_agents = []

for d in ["skills", "agents"]:
    p = root / d
    if p.exists():
        for item in p.iterdir():
            if item.is_dir():
                known.add(item.name)
            elif item.suffix == ".md":
                known.add(item.stem)

agents_dir = root / "agents"
if agents_dir.exists():
    for af in agents_dir.glob("*.md"):
        content = af.read_text(encoding="utf-8", errors="ignore")
        try:
            m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if m:
                fm = yaml.safe_load(m.group(1))
                skills = fm.get("skills", []) if isinstance(fm, dict) else []
                if isinstance(skills, str):
                    skills = [s.strip() for s in skills.split(",")]
                elif not isinstance(skills, list):
                    skills = []
                for s in skills:
                    s = str(s).strip().strip('"').strip("'")
                    if s and s not in ("None", "null", ""):
                        if s in known:
                            classified[s] += 1
                        else:
                            unknown_refs[s] += 1
                            if s not in [u[0] for u in orphan_agents]:
                                orphan_agents.append((s, af.stem))
        except Exception:
            pass

print("=== SKILLS REFERENCIADAS E REGISTRADAS ===")
for k, v in classified.most_common(40):
    print(f"  {v:3d}x  {k}")

print()
print("=== SKILLS REFERENCIADAS MAS NAO REGISTRADAS (unknown) ===")
for k, v in unknown_refs.most_common(40):
    agents_using = [a for (s, a) in orphan_agents if s == k]
    print(f"  {v:3d}x  {k}  (agentes: {agents_using[:3]})")

print()
total = sum(classified.values()) + sum(unknown_refs.values())
coverage = sum(classified.values()) / max(1, total) * 100
print(f"Classificadas: {sum(classified.values())} refs, {len(classified)} skills distintas")
print(f"Desconhecidas: {sum(unknown_refs.values())} refs, {len(unknown_refs)} skills distintas")
print(f"Cobertura do Registry: {coverage:.1f}%")
