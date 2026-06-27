import os

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

idx = 136420
print("Content from 136420 to end:")
print(content[idx:].encode('ascii', errors='replace').decode('ascii'))
