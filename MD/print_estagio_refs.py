import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "02-Dissertação_EstagioAtual.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

ref_match = re.search(r"(\*\*REFER\?NCIAS\*\*|REFER\?NCIAS\s+BIBLIOGR\?FICAS|REFER\?NCIAS\s+BIBLIOGRAFICAS)", content, re.IGNORECASE)
if ref_match:
    print("Found references in", fname)
    print(content[ref_match.start():].encode('ascii', errors='replace').decode('ascii'))
else:
    # Look for last 3000 chars
    print("Last 3000 characters:")
    print(content[-3000:].encode('ascii', errors='replace').decode('ascii'))
