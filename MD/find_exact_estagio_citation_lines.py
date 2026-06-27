import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "02-Dissertação_EstagioAtual.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    lines = f.readlines()

targets = ["almeida", "garcia", "silva", "ferreira"]
for i, line in enumerate(lines):
    for t in targets:
        if t in line.lower():
            safe_line = line.encode('cp1252', errors='replace').decode('cp1252')
            print(f"Line {i+1}: {repr(safe_line)}")
            break
