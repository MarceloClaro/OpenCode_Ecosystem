"""Debug theorem extraction across files."""
import re
import os

RAW_DIR = "raw_data/formal-conjectures"

# Use the exact same pattern from enrich_dataset.py
pattern = re.compile(
    r'/\-\-\n?(.*?)\n?\-\-/\s*'
    r'(?:@\[category\s+([^\]]+)\]\s*)?'
    r'(theorem|lemma|def|abbrev|instance)\s+(\w+(?:\.\w+)*)',
    re.DOTALL
)

# Scan a few files
test_files = [
    "ErdosProblems/1.lean",
    "ErdosProblems/10.lean",
    "ErdosProblems/100.lean",
    "Wikipedia/AgohGiugaConjecture.lean",
    "Wikipedia/ErdosRadoSunflowerConjecture.lean",
    "GreensOpenProblems/1.lean",
    "Millenium/BirchSwinnertonDyer.lean",
]

total = 0
for fp in test_files:
    full = os.path.join(RAW_DIR, fp)
    if not os.path.exists(full):
        print(f"MISSING: {fp}")
        continue
    with open(full, encoding='utf-8') as f:
        content = f.read()
    matches = list(pattern.finditer(content))
    print(f"{fp:50s}: {len(matches)} theorems/defs")
    total += len(matches)

print(f"\nTotal across {len(test_files)} files: {total}")

# Now do a broader scan
print("\n=== BROAD SCAN (first 50 files) ===")
all_lean = []
for root, dirs, files in os.walk(RAW_DIR):
    for f in files:
        if f.endswith('.lean'):
            all_lean.append(os.path.join(root, f))

total_theorems = 0
files_with_multiple = 0
for fp in sorted(all_lean)[:50]:
    with open(fp, encoding='utf-8') as f:
        content = f.read()
    matches = list(pattern.finditer(content))
    n = len(matches)
    total_theorems += n
    if n > 1:
        files_with_multiple += 1
    if n == 0:
        print(f"  ZERO: {fp.replace(RAW_DIR+'/','').replace(RAW_DIR+'\\\\','')}")

print(f"Scanned 50 files: {total_theorems} theorems total, {files_with_multiple} files with >1 theorem")
