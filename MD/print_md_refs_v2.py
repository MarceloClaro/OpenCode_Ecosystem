import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Let's search for the substring "REFER" case insensitively
matches = list(re.finditer(r"refer", content, re.IGNORECASE))
print("Found matches for 'refer':")
for m in matches:
    idx = m.start()
    context = content[idx-10:idx+40]
    safe_context = context.encode('ascii', errors='replace').decode('ascii')
    print(f"  Index {idx}: {repr(safe_context)}")
