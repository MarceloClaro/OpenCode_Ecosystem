import os
import re

latex_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex"
fname = "02_aspectos_estrategicos.tex"
fpath = os.path.join(latex_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Let's search for \cite in this file
cites = re.finditer(r"\\cite(?:\[[^\]]*\])?\{([^\}]+)\}", content)
print(f"Citations in {fname}:")
for i, m in enumerate(cites):
    keys = m.group(1).split(",")
    keys = [k.strip() for k in keys]
    idx = m.start()
    context = content[max(0, idx-100):min(len(content), idx+100)]
    context_clean = " ".join(context.split())
    print(f"{i}: Keys: {keys} -> Context: ... {repr(context_clean)} ...")
