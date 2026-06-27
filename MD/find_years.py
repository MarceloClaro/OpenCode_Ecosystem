import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Find any occurrences of 4-digit years starting with 19 or 20 in the body text (before References)
ref_match = re.search(r"(\*\*6\.\s+REFER\?NCIAS\s+BIBLIOGRAFICAS\*\*|REFER\?NCIAS\s+BIBLIOGRAFICAS)", content, re.IGNORECASE)
if ref_match:
    body = content[:ref_match.start()]
else:
    body = content

years = re.finditer(r"\b(19\d{2}|20\d{2})\b", body)
year_matches = list(years)
print(f"Total year occurrences in body: {len(year_matches)}")

# Let's print the context for the first 30 year matches
for i, m in enumerate(year_matches[:40]):
    idx = m.start()
    context = body[max(0, idx-40):min(len(body), idx+40)]
    safe_context = context.encode('ascii', errors='replace').decode('ascii')
    print(f"{i}: Year {m.group(1)} at {idx} -> ... {repr(safe_context)} ...")
