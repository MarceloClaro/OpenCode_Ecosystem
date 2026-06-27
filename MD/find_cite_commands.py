import os
import re

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

body = content[:136424]

# Let's search for \cite or cite in the body
matches = list(re.finditer(r"cite", body, re.IGNORECASE))
print(f"Occurrences of 'cite' in body: {len(matches)}")
for m in matches[:10]:
    idx = m.start()
    context = body[max(0, idx-40):min(len(body), idx+40)]
    safe = context.encode('cp1252', errors='replace').decode('cp1252')
    print(f"  Context: {repr(safe)}")
    
# Let's search for backslashes followed by words
backslashes = list(re.finditer(r"\\[a-zA-Z]+", body))
print(f"Occurrences of backslash commands: {len(backslashes)}")
for m in backslashes[:10]:
    idx = m.start()
    context = body[max(0, idx-40):min(len(body), idx+40)]
    safe = context.encode('cp1252', errors='replace').decode('cp1252')
    print(f"  Context: {repr(safe)}")
