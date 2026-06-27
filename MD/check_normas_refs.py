import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "03_01_Normas Projeto Final (PF).md"
fpath = os.path.join(md_dir, fname)

if os.path.exists(fpath):
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    print("Normas file length:", len(content))
    matches = list(re.finditer(r"refer", content, re.IGNORECASE))
    print("Matches for 'refer' in Normas:")
    for m in matches:
        idx = m.start()
        context = content[idx-20:idx+60]
        safe = context.encode('cp1252', errors='replace').decode('cp1252')
        print(f"  {idx}: {repr(safe)}")
else:
    print("Normas file not found.")
