import os

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

print("File length:", len(content))
print("First 4000 characters of the file:")
print(content[:4000])
