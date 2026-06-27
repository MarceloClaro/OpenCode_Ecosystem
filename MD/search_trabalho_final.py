import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

phrases = ["de Almeida", "Garcia et al", "Silva & Souza", "Ferreira & Mendes", "Schmidt"]

print("Searching in 01_Trabalho_Final.md:")
for p in phrases:
    matches = list(re.finditer(re.escape(p), content, re.IGNORECASE))
    print(f"  Phrase '{p}': {len(matches)} matches")
    for m in matches[:3]:
        idx = m.start()
        context = content[max(0, idx-50):min(len(content), idx+50)]
        print(f"    Context: {repr(context)}")
