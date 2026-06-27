import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Let's search for anything in parentheses that looks like (Name, Year) or (Name & Name, Year) or similar
# e.g., (A & B, YYYY) or (A et al., YYYY) or (A, B & C, YYYY)
parenthesized_citations = re.findall(r"\(([^)]+,\s*\d{4})\)", content)
print("Parenthesized citations in body:")
print("Count:", len(parenthesized_citations))
for cite in sorted(list(set(parenthesized_citations))):
    print(f"  - {cite}")
