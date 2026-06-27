import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Let's search for references section
ref_match = re.search(r"(\*\*6\.\s+REFER\?NCIAS\s+BIBLIOGRAFICAS\*\*|6\.\s+REFER\?NCIAS\s+BIBLIOGRAFICAS|REFER\?NCIAS\s+BIBLIOGRAFICAS)", content, re.IGNORECASE)
if ref_match:
    print("Found References section in", fname)
    refs_text = content[ref_match.start():]
    # Safe print by replacing non-ASCII characters
    print(refs_text.encode('ascii', errors='replace').decode('ascii'))
else:
    print("References section not found in", fname)
