import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "02-Dissertação_EstagioAtual.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Find any occurrences of 4-digit years starting with 19 or 20
years = re.finditer(r"\b(19\d{2}|20\d{2})\b", content)
year_matches = list(years)
print(f"Total year occurrences in {fname}: {len(year_matches)}")

# Let's print the context for all year matches
for i, m in enumerate(year_matches):
    idx = m.start()
    context = content[max(0, idx-45):min(len(content), idx+45)]
    safe_context = context.encode('ascii', errors='replace').decode('ascii')
    print(f"{i}: Year {m.group(1)} at {idx} -> ... {repr(safe_context)} ...")
