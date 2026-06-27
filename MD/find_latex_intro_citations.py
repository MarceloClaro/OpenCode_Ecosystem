import os
import re

latex_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex"
fname = "01_introducao.tex"
fpath = os.path.join(latex_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Let's search for sentences containing "pensamento crítico" or "capacitação docente" or similar
phrases = ["pensamento cr", "capacita", "engajamento", "habilidades de"]
for p in phrases:
    matches = list(re.finditer(p, content, re.IGNORECASE))
    print(f"Phrase '{p}' matches: {len(matches)}")
    for m in matches:
        idx = m.start()
        context = content[max(0, idx-100):min(len(content), idx+100)]
        print(f"  Context: {repr(' '.join(context.split()))}")
