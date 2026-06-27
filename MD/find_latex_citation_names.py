import os
import re

latex_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex"
tex_files = [f for f in os.listdir(latex_dir) if f.endswith(".tex")]

names = ["almeida", "schmidt", "garcia", "silva", "souza", "ferreira", "mendes"]

for fname in sorted(tex_files):
    fpath = os.path.join(latex_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
        
    for name in names:
        matches = list(re.finditer(re.escape(name), content, re.IGNORECASE))
        if matches:
            print(f"\n==================================================")
            print(f"File: {fname} | Name: '{name}' matches: {len(matches)}")
            print(f"==================================================")
            for m in matches[:5]: # Show first 5
                idx = m.start()
                context = content[max(0, idx-50):min(len(content), idx+50)]
                context_clean = " ".join(context.split())
                print(f"  Context: ... {repr(context_clean)} ...")
