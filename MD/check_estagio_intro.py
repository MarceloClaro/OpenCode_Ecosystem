import os

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "02-Dissertação_EstagioAtual.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

print(content[3000:].encode('ascii', errors='replace').decode('ascii'))
