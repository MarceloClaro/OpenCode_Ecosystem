import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Let's search for patterns like (Author, Year) or (Author et al., Year) or [Author, Year]
# Standard format: (Name, 20XX) or (Name & Name, 20XX) etc.
matches_parentheses = re.findall(r"\(([^)]*?\b20\d{2}[a-z]?)\)", content)
matches_brackets = re.findall(r"\[([^]]*?\b20\d{2}[a-z]?)\]", content)

print("Parentheses citations with 20XX:")
print(f"Total found: {len(matches_parentheses)}")
for m in sorted(list(set(matches_parentheses)))[:50]:
    print(f"  {m}")

print("\nBrackets citations with 20XX:")
print(f"Total found: {len(matches_brackets)}")
for m in sorted(list(set(matches_brackets)))[:50]:
    print(f"  {m}")
