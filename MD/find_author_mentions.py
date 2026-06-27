import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Let's split at index 136424 to get the body
body = content[:136424]

authors = ["Almeida", "Moran", "Bacich", "Blikstein", "Brasil", "Campos", "Garofalo", "Goya", "Kafai", "Resnick", "Papert", "Valente"]

print("Author mentions in body:")
for a in authors:
    matches = list(re.finditer(re.escape(a), body, re.IGNORECASE))
    print(f"  {a}: {len(matches)} matches")
    for m in matches[:2]:
        idx = m.start()
        context = body[max(0, idx-40):min(len(body), idx+40)]
        safe = context.encode('cp1252', errors='replace').decode('cp1252')
        print(f"    Context: {repr(safe)}")
