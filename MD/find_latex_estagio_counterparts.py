import os
import re

latex_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex"
tex_files = [f for f in os.listdir(latex_dir) if f.endswith(".tex")]

phrase = "tem demonstrado"

for fname in sorted(tex_files):
    fpath = os.path.join(latex_dir, fname)
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    if phrase in content:
        print(f"File: {fname}")
        for m in re.finditer(re.escape(phrase), content):
            idx = m.start()
            context = content[max(0, idx-100):min(len(content), idx+100)]
            print(f"  Context: {repr(' '.join(context.split()))}")
