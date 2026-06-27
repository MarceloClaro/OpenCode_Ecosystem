import os

md_dir = r"C:\Users\marce\Documents\OpenCode_Ecosystem\MD\MD"
fname = "01_Trabalho_Final.md"
fpath = os.path.join(md_dir, fname)

with open(fpath, "r", encoding="utf-8") as f:
    content = f.read()

print("Length:", len(content))
print("Last 4000 characters:")
# Safe print by replacing non-ASCII
print(content[-4000:].encode('ascii', errors='replace').decode('ascii'))
