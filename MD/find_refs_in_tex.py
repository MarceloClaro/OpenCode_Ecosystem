import os
import re

latex_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\dissertacao-latex"
fpath = os.path.join(latex_dir, "06_referencias.tex")

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

# Let's find all bibitem keys
bibitems = re.findall(r"\\bibitem\{([^\}]+)\}", content)
print("Total bibitems:", len(bibitems))
print("Bibitem keys:")
for b in sorted(bibitems):
    print(f"  - {b}")
